from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Enterprise RAG System Running"}

@router.get("/health")
def health_check():
    return {"status": "healthy"}