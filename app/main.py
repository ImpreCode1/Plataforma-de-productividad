from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.modules.users.router import router as users_router
from app.modules.evaluation_periods.router import router as evaluation_periods_router
from app.modules.evaluation_results.router import router as evaluation_results_router

from app.db.session import get_db

app = FastAPI(
    title="Plataforma de Evaluación de Productividad",
    version="1.0.0"
)

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(evaluation_periods_router, prefix="/evaluation_period", tags=["Evaluation_periods"])
app.include_router(evaluation_results_router, prefix="/evaluation_results", tags=["Evaluation_results"])

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