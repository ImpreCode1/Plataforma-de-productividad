from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.security.dependencies import DBSession, CurrentUser, require_roles
from app.modules.notifications import service
from app.modules.notifications.schemas import (
    NotificationSendRequest,
    NotificationSendResponse,
    UserInfo
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get("/users", dependencies=[Depends(require_roles("ADMIN"))])
def get_users(
    role: Optional[str] = Query(None, description="Filter by role: LEADER, EMPLOYEE"),
    db: DBSession = DBSession,
    current_user: CurrentUser = CurrentUser
):
    """Get list of users filtered by role"""
    
    if role == "LEADER":
        users = service.get_users_by_type(db, "all_leaders")
    elif role == "EMPLOYEE":
        users = service.get_users_by_type(db, "all_employees")
    else:
        from app.models.user import User
        users = db.query(User).filter(User.is_active == True).all()
    
    from app.models.role import UserRole, Role
    
    result = []
    for user in users:
        user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        role_names = []
        for ur in user_roles:
            r = db.query(Role).filter(Role.id == ur.role_id).first()
            if r:
                role_names.append(r.name)
        
        result.append(UserInfo(
            id=str(user.id),
            name=user.name or user.email,
            email=user.email,
            role=", ".join(role_names) if role_names else "Sin rol",
            area=user.area
        ))
    
    return {"users": result}


@router.post("/send", response_model=NotificationSendResponse, dependencies=[Depends(require_roles("ADMIN"))])
def send_notifications(
    request: NotificationSendRequest,
    db: DBSession = DBSession,
    current_user: CurrentUser = CurrentUser
):
    """Send email notifications to selected users"""
    
    result = service.send_notifications(
        db=db,
        recipient_type=request.recipient_type,
        recipient_ids=request.recipient_ids or [],
        filter_area=request.filter_area,
        template=request.template,
        month=request.month,
        year=request.year,
        sent_by=str(current_user.id)
    )
    
    return NotificationSendResponse(**result)