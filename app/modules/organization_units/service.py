from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.organization import OrganizationUnit
from app.modules.organization_units.schemas import (
    OrganizationUnitCreate,
    OrganizationUnitUpdate
)


def list_units(db: Session):

    return db.query(OrganizationUnit).all()


def get_unit(db: Session, unit_id: UUID):

    unit = db.query(OrganizationUnit).filter(
        OrganizationUnit.id == unit_id
    ).first()

    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization unit not found"
        )

    return unit


def create_unit(db: Session, unit_in: OrganizationUnitCreate):

    unit = OrganizationUnit(**unit_in.model_dump())

    db.add(unit)
    db.commit()
    db.refresh(unit)

    return unit


def update_unit(
    db: Session,
    unit_id: UUID,
    unit_in: OrganizationUnitUpdate
):

    unit = get_unit(db, unit_id)

    for field, value in unit_in.model_dump(exclude_unset=True).items():
        setattr(unit, field, value)

    db.commit()
    db.refresh(unit)

    return unit


def delete_unit(db: Session, unit_id: UUID):

    unit = get_unit(db, unit_id)

    db.delete(unit)
    db.commit()

    return unit