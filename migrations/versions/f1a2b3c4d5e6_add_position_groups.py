"""add position_groups table and seed Financial Officer hierarchy

Revision ID: xxxxxxxxxxxx
Revises: <PON_AQUI_EL_HEAD_ACTUAL>
Create Date: 2026-06-17

Contexto: jerarquia organizacional confirmada por Diana Diaz (PMO Leader) el
17/06/2026. Solo la vicepresidencia Financial Officer fue validada palabra
por palabra en la llamada -- el resto de vicepresidencias se cargara en una
migracion posterior una vez Diana las confirme. Por eso is_validated=True
solo para Financial Officer.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = "f1a2b3c4d5e6"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Crear tabla position_groups
    op.create_table(
        "position_groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("level", sa.String(), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("position_groups.id"), nullable=True),
        sa.Column("is_validated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("level IN ('vicepresidencia', 'direccion')", name="ck_position_groups_level"),
    )

    # 2. Agregar FK en users (nullable: no todos los usuarios estaran clasificados de inmediato)
    op.add_column(
        "users",
        sa.Column("position_group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("position_groups.id"), nullable=True),
    )

    # 3. Seed: Financial Officer (unica vicepresidencia confirmada por Diana el 17/06/2026)
    position_groups = sa.table(
        "position_groups",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("level", sa.String),
        sa.column("parent_id", postgresql.UUID(as_uuid=True)),
        sa.column("is_validated", sa.Boolean),
    )

    vp_id = uuid.uuid4()
    direcciones = {
        "Direccion Financiera (Mayreth Galvis)": uuid.uuid4(),
        "Direccion Contabilidad e Impuestos (Beatriz Manrique)": uuid.uuid4(),
        "Direccion Activos Operativos (Paola Alvarez)": uuid.uuid4(),
        "Direccion de Operaciones (Sergio Pascagaza)": uuid.uuid4(),
        "Coordinacion Planeacion Financiera (Yeraldin Velasco)": uuid.uuid4(),
    }

    rows = [
        {"id": vp_id, "name": "Financial Officer", "level": "vicepresidencia", "parent_id": None, "is_validated": True},
    ]
    for nombre, dir_id in direcciones.items():
        rows.append({"id": dir_id, "name": nombre, "level": "direccion", "parent_id": vp_id, "is_validated": True})

    op.bulk_insert(position_groups, rows)

    # Guardamos los IDs de direcciones como comentario de referencia para el mapeo subarea->direccion
    # que se hara en el servicio de import, no en esta migracion:
    # Treasury, Financial - Credit, Financial - Collections, Foreign payments, Financial
    #   -> Direccion Financiera (Mayreth Galvis)
    # Accounting, Accounting - Tax
    #   -> Direccion Contabilidad e Impuestos (Beatriz Manrique)
    # Operating Assets, Manufacturer account
    #   -> Direccion Activos Operativos (Paola Alvarez)
    # Operations, Operations - Imports, Operations - Logistics, Operations - Procurement
    #   -> Direccion de Operaciones (Sergio Pascagaza)
    # Financial Planning
    #   -> Coordinacion Planeacion Financiera (Yeraldin Velasco)
    # Legal -> SIN CLASIFICAR, queda sin asignar a proposito


def downgrade() -> None:
    op.drop_column("users", "position_group_id")
    op.drop_table("position_groups")
