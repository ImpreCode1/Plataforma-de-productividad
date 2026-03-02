from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_users():
    return {"message": "Users endpoint working"}