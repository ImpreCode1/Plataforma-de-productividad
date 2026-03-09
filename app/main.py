from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.security.dependencies import get_current_user

from app.modules.users.router import router as users_router
from app.modules.positions.router import router as positions_router
from app.modules.organization_units.router import router as organizations_router
from app.modules.indicators.router import router as indicators_router
from app.modules.position_indicators.router import router as position_indicators_router

from app.db.session import get_db

app = FastAPI(
    title="Plataforma de Evaluación de Productividad",
    version="1.0.0"
)

app.include_router(users_router, dependencies=[Depends(get_current_user)])
app.include_router(positions_router, dependencies=[Depends(get_current_user)])
app.include_router(organizations_router, dependencies=[Depends(get_current_user)])
app.include_router(indicators_router, dependencies=[Depends(get_current_user)])
app.include_router(position_indicators_router, dependencies=[Depends(get_current_user)])


@app.get("/")
def HelloWorld():
    try:
        return{"API de Plataforma de Productividad Impresistem Funcionando Correctamente"}
    except Exception:
        return{"API de Plataforma de Productividad Impresistem NO esta funcionando :()"}
        
@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(e)
        }
        