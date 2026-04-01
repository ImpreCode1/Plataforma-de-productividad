from typing import Annotated
from fastapi import Depends, HTTPException, status, Request, Cookie, Header
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import UserRole
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
    x_access_token: str | None = Header(default=None, alias="X-Access-Token"),
    x_access_token_lower: str | None = Header(default=None, alias="x-access-token"),
) -> User:
    
    token = hydra_access or x_access_token or x_access_token_lower
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    payload = validate_jwt(token)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    payload = validate_jwt(token)
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
        name = payload.get("name")
        
        user = User(
            external_auth_id=external_auth_id,
            name=name or "Usuario",
            email=email,
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

        user_roles = [ur.role.name for ur in current_user.user_roles] if hasattr(current_user, 'user_roles') else []

        if not any(role in allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos suficientes",
            )

        return current_user

    return role_checker