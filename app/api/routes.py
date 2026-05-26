from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Enterprise RAG System Running"}