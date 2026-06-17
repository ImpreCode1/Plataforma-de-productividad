from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.staticfiles import StaticFiles

from app.core.security.dependencies import get_current_user
from app.db.session import get_db, SessionLocal
from app.db.seed import run_seed

from app.modules.users.router import router as users_router
from app.modules.indicator_assignments.router import router as indicators_router
from app.modules.indicator_tracking.router import router as indicator_tracking_router
from app.modules.evidence.router import router as evidence_router
from app.modules.action_plan.router import router as action_plan_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.roles.router import router as roles_router
from app.modules.team.router import router as team_router
from app.modules.notifications.router import router as notifications_router
from app.modules.approval.router import router as approval_router
from app.modules.special_mode.router import router as special_mode_router
from app.modules.position_groups.router import router as position_groups_router


app = FastAPI(
    title="Plataforma de Evaluación de Productividad",
    version="1.0.0"
)

app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")


@app.on_event("startup")
def startup_seed():
    db = SessionLocal()
    try:
        run_seed(db)
        print("✅ Seed completo ejecutado")
    finally:
        db.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "https://www.impresistem.com",
        "https://impresistem.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, dependencies=[Depends(get_current_user)])
app.include_router(indicators_router, dependencies=[Depends(get_current_user)])
app.include_router(indicator_tracking_router, dependencies=[Depends(get_current_user)])
app.include_router(evidence_router, dependencies=[Depends(get_current_user)])
app.include_router(action_plan_router, dependencies=[Depends(get_current_user)])
app.include_router(dashboard_router, dependencies=[Depends(get_current_user)])
app.include_router(team_router, dependencies=[Depends(get_current_user)])
app.include_router(roles_router)
app.include_router(notifications_router, dependencies=[Depends(get_current_user)])
app.include_router(approval_router, dependencies=[Depends(get_current_user)])
app.include_router(special_mode_router, dependencies=[Depends(get_current_user)])
app.include_router(position_groups_router, dependencies=[Depends(get_current_user)])


@app.get("/")
def HelloWorld():
    return {"message": "API de Plataforma de Productividad Impresistem funcionando correctamente"}


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