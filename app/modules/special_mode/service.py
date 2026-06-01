from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from datetime import datetime
from typing import Optional, List

from app.models.approval_config import ApprovalConfig
from app.models.user import User


def create_config(db: Session, config_type: str, config_value: str, load_mode: str, created_by: UUID) -> ApprovalConfig:
    valid_types = ["area", "position", "team", "user"]
    valid_modes = ["employee", "leader", "admin"]

    if config_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Tipo inválido. Debe ser: {', '.join(valid_types)}")
    if load_mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Modo inválido. Debe ser: {', '.join(valid_modes)}")

    existing = db.query(ApprovalConfig).filter(
        ApprovalConfig.config_type == config_type,
        ApprovalConfig.config_value == config_value,
        ApprovalConfig.is_active == True,
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una configuración activa para este valor")

    config = ApprovalConfig(
        config_type=config_type,
        config_value=config_value,
        load_mode=load_mode,
        is_active=True,
        created_by=created_by,
        created_at=datetime.utcnow(),
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


def list_configs(db: Session, config_type: Optional[str] = None) -> List[ApprovalConfig]:
    query = db.query(ApprovalConfig).filter(ApprovalConfig.is_active == True)
    if config_type:
        query = query.filter(ApprovalConfig.config_type == config_type)
    return query.order_by(ApprovalConfig.created_at.desc()).all()


def update_config(db: Session, config_id: UUID, load_mode: str) -> ApprovalConfig:
    config = db.query(ApprovalConfig).filter(ApprovalConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")

    valid_modes = ["employee", "leader", "admin"]
    if load_mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Modo inválido. Debe ser: {', '.join(valid_modes)}")

    config.load_mode = load_mode
    db.commit()
    db.refresh(config)
    return config


def delete_config(db: Session, config_id: UUID):
    config = db.query(ApprovalConfig).filter(ApprovalConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    config.is_active = False
    db.commit()


def get_load_mode(db: Session, user_id: UUID) -> str:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return "employee"

    configs = db.query(ApprovalConfig).filter(ApprovalConfig.is_active == True).order_by(
        ApprovalConfig.config_type
    ).all()

    specific_configs = {
        "user": None,
        "team": None,
        "position": None,
        "area": None,
    }

    for config in configs:
        if config.config_type == "user" and config.config_value == str(user_id):
            specific_configs["user"] = config
        elif config.config_type == "team" and user.leader_id and config.config_value == str(user.leader_id):
            specific_configs["team"] = config
        elif config.config_type == "position" and user.position_name and config.config_value.lower() == user.position_name.lower():
            specific_configs["position"] = config
        elif config.config_type == "area" and user.area and config.config_value.lower() == user.area.lower():
            specific_configs["area"] = config

    for priority in ["user", "team", "position", "area"]:
        if specific_configs[priority]:
            return specific_configs[priority].load_mode

    return "employee"
