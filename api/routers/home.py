from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def home():
    return {"message": "Model API is running successfully 🚀"}