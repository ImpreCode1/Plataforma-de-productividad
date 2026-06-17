"""
app/modules/position_groups/router.py

Endpoint para exponer el arbol jerarquico de la organizacion
(Vicepresidencia -> Direccion) con conteo de personas.

Nota: get_current_user se aplica a nivel de include_router en main.py,
igual que el resto de los modulos (action_plan, dashboard, etc.), no aqui.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.position_groups.service import get_position_groups_tree


router = APIRouter(prefix="/position-groups", tags=["position-groups"])


@router.get("/tree")
def read_position_groups_tree(db: Session = Depends(get_db)):
    """
    Devuelve el arbol completo: vicepresidencias con sus direcciones anidadas
    y el conteo de personas (directo y acumulado) por nodo.
    """
    return get_position_groups_tree(db)