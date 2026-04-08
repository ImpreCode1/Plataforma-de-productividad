from typing import Annotated
from fastapi import Depends, HTTPException, status, Request, Cookie, Header
from sqlalchemy.orm import Session, selectinload

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
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> User:

    token = hydra_access or authorization

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    if token.startswith("Bearer "):
        token = token[7:]

    payload = validate_jwt(token)

    email = payload.get("email")
    external_auth_id = payload.get("sub")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin email",
        )

    # 🔥 Buscar por EMAIL (clave del sistema)
    user = (
        db.query(User)
        .options(selectinload(User.roles).selectinload(UserRole.role))
        .filter(User.email == email)
        .first()
    )

    # ❌ NO crear usuario → debe venir del Excel
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no registrado en la plataforma",
        )

    # 🔥 Opcional: vincular external_auth_id si no existe
    if external_auth_id and not user.external_auth_id:
        user.external_auth_id = external_auth_id
        db.commit()

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

    def role_checker(current_user: CurrentUser) -> User:

        user_roles = [
            ur.role.name for ur in current_user.roles if ur.role
        ]

        if not any(role in allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos suficientes",
            )

        return current_user

    return role_checker