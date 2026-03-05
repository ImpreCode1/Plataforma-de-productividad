from typing import Annotated
from fastapi import Depends, HTTPException, status, Request, Cookie
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security.jwt_validation import validate_jwt


# ---------------------------------------------------------
# Database Dependency
# ---------------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DBSession = Annotated[Session, Depends(get_db)]


# ---------------------------------------------------------
# Current Authenticated User
# ---------------------------------------------------------

def get_current_user(
    request: Request,
    hydra_access: str | None = Cookie(default=None),
    db: DBSession = Depends(),
) -> User:
    
    # 1️⃣ Verificar existencia del token
    if not hydra_access:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    # 2️⃣ Validar JWT emitido por Hydra
    payload = validate_jwt(hydra_access)

    # 3️⃣ Extraer identificador externo
    external_auth_id = payload.get("sub")

    if not external_auth_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin identificador válido",
        )

    # 4️⃣ Buscar usuario interno
    user = (
        db.query(User)
        .filter(User.external_auth_id == external_auth_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no registrado en la plataforma",
        )

    # 5️⃣ Validar usuario activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    # 6️⃣ Guardar información en request state (útil para auditoría)
    request.state.user = user
    request.state.jwt_payload = payload

    return user


# Alias tipado para usar en endpoints
CurrentUser = Annotated[User, Depends(get_current_user)]


# ---------------------------------------------------------
# RBAC - Role Based Access Control
# ---------------------------------------------------------

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