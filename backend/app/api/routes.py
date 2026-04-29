from fastapi import APIRouter, Request
from app.api.schemas import ChatRequest, SQLRequest
from app.core.security import require_scope
from app.services.orchestrator import answer_question
from app.services.document_service import retriever
from app.tools.sql_tool import run_sql, run_named_query, SAFE_QUERY_LIBRARY

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/chat")
def chat(payload: ChatRequest, request: Request):
    require_scope(request, "analytics")
    return answer_question(payload.question)

@router.get("/analytics/top-titles")
def top_titles(request: Request):
    require_scope(request, "analytics")
    return {"rows": run_named_query("top_titles_2025")}

@router.get("/analytics/city-engagement")
def city_engagement(request: Request):
    require_scope(request, "analytics")
    return {"rows": run_named_query("city_engagement_last_month")}

@router.get("/analytics/queries")
def query_catalog(request: Request):
    require_scope(request, "analytics")
    return {"queries": list(SAFE_QUERY_LIBRARY.keys())}

@router.post("/sql/read-only")
def read_only_sql(payload: SQLRequest, request: Request):
    require_scope(request, "analytics")
    return {"rows": run_sql(payload.sql)}

@router.get("/documents/search")
def search_docs(q: str, request: Request):
    require_scope(request, "documents")
    return {"rows": retriever.search(q)}
