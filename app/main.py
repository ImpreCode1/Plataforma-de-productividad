from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.modules.users.router import router as users_router
from app.db.session import get_db

app = FastAPI(
    title="Plataforma de Evaluación de Productividad",
    version="1.0.0"
)

app.include_router(users_router, prefix="/users", tags=["Users"])


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