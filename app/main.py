from fastapi import FastAPI
from app.api.v1 import users

app = FastAPI(
    title="Performance Evaluation Platform",
    version="1.0.0"
)

app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])

@app.get("/health")
def health():
    return {"status": "ok"}