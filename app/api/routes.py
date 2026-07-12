import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import tempfile
import os

from app.ingestion.ingestor import ingest_file
from app.retrieval.retriever import retrieve
from app.retrieval.validator import validate, ValidationError
from app.generation.generator import generate_answer
from app.cost_tracker import CostTracker
from app.auth.rbac import check_access, get_user_role, get_allowed_departments
from app.auth.api_key_auth import validate_api_key

logger = logging.getLogger(__name__)
router = APIRouter()

# --- API Key Security ---
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def require_api_key(api_key: str = Security(api_key_header)) -> dict:
    if not api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header missing")
    key_data = validate_api_key(api_key)
    if not key_data:
        raise HTTPException(status_code=403, detail="Invalid or inactive API key")
    return key_data


class QueryRequest(BaseModel):
    query: str
    department: str = "general"
    user_id: str = "anonymous"
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    sources: list
    chunks_used: int
    model: str
    cost: dict


class IngestResponse(BaseModel):
    document_id: str
    filename: str
    chunks_created: int
    status: str


@router.get("/")
def root():
    return {"message": "Enterprise RAG System Running"}


@router.get("/health")
def health_check():
    return {"status": "healthy"}


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    file: UploadFile = File(...),
    department: str = Form(default="general"),
    uploaded_by: str = Form(default="anonymous"),
    key_data: dict = Depends(require_api_key)
):
    try:
        print(f"[DEBUG] file.filename = {file.filename!r}", flush=True)
        suffix = os.path.splitext(file.filename)[-1] or ".txt"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = ingest_file(file_path=tmp_path, department=department, original_filename=file.filename)
        os.unlink(tmp_path)

        return IngestResponse(
            document_id=result["document_id"],
            filename=file.filename,
            chunks_created=result["chunks_created"],
            status="success"
        )
    except Exception as e:
        logger.error(f"Ingest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
def query(
    request: QueryRequest,
    key_data: dict = Depends(require_api_key)
):
    try:
        # RBAC check
        allowed, role = check_access(request.user_id, request.department)
        if not allowed:
            allowed_depts = get_allowed_departments(role)
            return QueryResponse(
                answer=f"Access denied. Your role '{role}' does not have permission to query the '{request.department}' department. Allowed departments: {', '.join(allowed_depts)}.",
                sources=[],
                chunks_used=0,
                model="none",
                cost={"total_cost_usd": 0.0, "total_tokens": 0}
            )

        tracker = CostTracker(session_id=f"{request.user_id}_{request.query[:20]}")

        chunks = retrieve(
            query=request.query,
            department=request.department,
            top_k=request.top_k
        )

        try:
            validated = validate(query=request.query, chunks=chunks)
        except ValidationError as e:
            return QueryResponse(
                answer=str(e),
                sources=[],
                chunks_used=0,
                model="none",
                cost={"total_cost_usd": 0.0, "total_tokens": 0}
            )

        result = generate_answer(query=request.query, validated_chunks=validated)

        if "usage" in result:
            cost_event = tracker.track(
                provider="groq",
                model=result["model"],
                prompt_tokens=result["usage"]["prompt_tokens"],
                completion_tokens=result["usage"]["completion_tokens"]
            )
        else:
            cost_event = {"total_cost_usd": 0.0, "total_tokens": 0}

        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            chunks_used=result["chunks_used"],
            model=result.get("model", "unknown"),
            cost=cost_event
        )

    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))