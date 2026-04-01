from typing import Annotated
from fastapi import Depends, HTTPException, status, Request, Cookie
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.models.company_employee import CompanyEmployee
from app.core.security.jwt_validation import validate_jwt


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DBSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    request: Request,
    db: DBSession,
    hydra_access: str | None = Cookie(default=None),
) -> User:
    
    if not hydra_access:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    payload = validate_jwt(hydra_access)

    external_auth_id = payload.get("sub")

    if not external_auth_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin identificador válido",
        )

    user = (
        db.query(User)
        .filter(User.external_auth_id == external_auth_id)
        .first()
    )

    if not user:
        email = payload.get("email")
        
        employee = (
            db.query(CompanyEmployee)
            .filter(CompanyEmployee.email == email)
            .first()
        )
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a la plataforma. Contacta al administrador.",
            )
        
        if not employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tu cuenta está desactivada. Contacta al administrador.",
            )
        
        user = User(
            external_auth_id=external_auth_id,
            name=payload.get("name", employee.name),
            email=email,
            position_id=employee.position_id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    request.state.user = user
    request.state.jwt_payload = payload

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*allowed_roles: str):

    def role_checker(
        current_user: CurrentUser,
    ) -> User:

        user_roles = [role.name for role in current_user.roles]

        if not any(role in allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos suficientes",
            )

        return current_user

    return role_checker
