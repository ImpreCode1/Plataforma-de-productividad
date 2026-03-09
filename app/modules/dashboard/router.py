from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.modules.dashboard.service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/user")
def user_dashboard(
    user_id: UUID,
    month: int,
    db: Session = Depends(get_db)
):

    return DashboardService.user_dashboard(
        db,
        user_id,
        month
    )
    
@router.get("/leader")
def leader_dashboard(
    leader_id: UUID,
    month: int,
    db: Session = Depends(get_db)
):

    return DashboardService.leader_dashboard(
        db,
        leader_id,
        month
    )
    
@router.get("/organization")
def organization_dashboard(
    month: int,
    db: Session = Depends(get_db)
):

    return DashboardService.organization_dashboard(
        db,
        month
    )