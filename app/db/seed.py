from sqlalchemy.orm import Session
from app.models.role import Role, UserRole
from app.models.user import User

ADMIN_EMAIL = "sebastian.ortiz@impresistem.com"

def seed_roles(db: Session):

    roles = ["ADMIN", "LEADER", "EMPLOYEE"]

    role_map = {}

    for role_name in roles:
        role = db.query(Role).filter(Role.name == role_name).first()

        if not role:
            role = Role(name=role_name)
            db.add(role)
            db.flush()

        role_map[role_name] = role

    db.commit()

    return role_map


def seed_admin_user(db: Session, role_map):

    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()

    if not admin:
        print("⚠️ Admin no existe aún (se creará cuando importes Excel)")
        return

    # Verificar si ya tiene rol ADMIN
    existing = db.query(UserRole).filter(
        UserRole.user_id == admin.id,
        UserRole.role_id == role_map["ADMIN"].id
    ).first()

    if not existing:
        db.add(UserRole(
            user_id=admin.id,
            role_id=role_map["ADMIN"].id
        ))
        db.commit()
        print("✅ Admin asignado correctamente")


def run_seed(db: Session):

    role_map = seed_roles(db)
    seed_admin_user(db, role_map)