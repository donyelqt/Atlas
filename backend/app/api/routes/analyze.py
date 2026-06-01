from fastapi import APIRouter

from app.schemas.models import RepoUrlRequest, AnalysisSummary, ChatRequest, ChatResponse, GraphResponse
from app.agents import RepositoryAgent, ArchitectureAgent, GraphAgent, OnboardingAgent
from app.services.llm_service import LLMService
from app.core.config import settings

import logging
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
router = APIRouter()


_analysis_store: dict[str, dict[str, Any]] = {}
_graph_cache: dict[str, dict[str, Any]] = {}


@router.post("/analyze", response_model=AnalysisSummary)
async def analyze_repo(request: RepoUrlRequest) -> AnalysisSummary:
    analysis_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    summary = AnalysisSummary(
        id=analysis_id,
        status="processing",
        repo_url=request.repo_url,
        created_at=now,
    )
    _analysis_store[analysis_id] = {
        "id": analysis_id,
        "repo_url": request.repo_url,
        "status": "processing",
        "created_at": now,
        "repo_data": None,
        "graph_data": None,
        "architecture": None,
        "onboarding": None,
    }
    try:
        repo_agent = RepositoryAgent()
        repo_data = await repo_agent.run(request.repo_url)
        graph_agent = GraphAgent()
        graph = await graph_agent.run(request.repo_url)
        llm = LLMService()
        arch_agent = ArchitectureAgent(llm)
        architecture = await arch_agent.run(repo_data)
        onboard_agent = OnboardingAgent(llm)
        onboarding = await onboard_agent.run(repo_data, graph)
        _analysis_store[analysis_id].update({
            "status": "completed",
            "repo_data": repo_data,
            "graph_data": graph.to_dict(),
            "architecture": architecture,
            "onboarding": onboarding,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "framework": repo_data.get("framework"),
            "language": repo_data.get("language"),
            "file_count": repo_data.get("file_count", 0),
            "directory_count": repo_data.get("directory_count", 0),
            "architecture_type": architecture.get("architecture_type"),
            "complexity": architecture.get("complexity"),
        })
        _graph_cache[analysis_id] = graph.to_dict()
        summary.status = "completed"
        summary.framework = repo_data.get("framework")
        summary.language = repo_data.get("language")
        summary.file_count = repo_data.get("file_count", 0)
        summary.directory_count = repo_data.get("directory_count", 0)
        summary.architecture_type = architecture.get("architecture_type")
        summary.complexity = architecture.get("complexity")
        summary.completed_at = _analysis_store[analysis_id]["completed_at"]
    except Exception as exc:
        logger.exception("Analysis failed for %s", request.repo_url)
        _analysis_store[analysis_id]["status"] = "failed"
        _analysis_store[analysis_id]["error"] = str(exc)
        summary.status = "failed"
        summary.error = str(exc)
    return summary


@router.get("/graph/{analysis_id}", response_model=GraphResponse)
async def get_graph(analysis_id: str) -> GraphResponse:
    if analysis_id not in _graph_cache:
        raise ValueError(f"Analysis {analysis_id} not found")
    data = _graph_cache[analysis_id]
    return GraphResponse(nodes=data["nodes"], edges=data["edges"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    llm = LLMService()
    if request.analysis_id not in _analysis_store:
        return ChatResponse(answer="Analysis not found. Please run analysis first.", sources=[])
    store = _analysis_store[request.analysis_id]
    if store.get("status") != "completed":
        return ChatResponse(answer="Analysis not yet completed.", sources=[])
    repo_data = store.get("repo_data", {})
    arch_summary = store.get("architecture", {}).get("summary", "")
    modules = repo_data.get("modules", [])
    file_contexts: list[dict[str, Any]] = []
    for mod in modules[:3]:
        for f in mod.get("files", [])[:5]:
            file_contexts.append({
                "path": f.get("path", ""),
                "content_preview": f.get("content_preview"),
                "imports": f.get("imports"),
                "functions": f.get("functions"),
                "classes": f.get("classes"),
            })
    answer = await llm.answer_question(
        question=request.question,
        repo_name=repo_data.get("full_name", repo_data.get("name", "")),
        file_contexts=file_contexts,
        architecture_summary=arch_summary,
    )
    sources = [f.get("path", "") for f in file_contexts[:5] if f.get("content_preview")]
    return ChatResponse(answer=answer, sources=sources)


@router.get("/summary/{analysis_id}")
async def get_summary(analysis_id: str) -> dict[str, Any]:
    if analysis_id not in _analysis_store:
        raise ValueError(f"Analysis {analysis_id} not found")
    store = _analysis_store[analysis_id]
    return {
        "id": store["id"],
        "status": store["status"],
        "repo_url": store["repo_url"],
        "framework": store.get("framework"),
        "language": store.get("language"),
        "file_count": store.get("file_count", 0),
        "directory_count": store.get("directory_count", 0),
        "architecture_type": store.get("architecture_type"),
        "complexity": store.get("complexity"),
        "architecture": store.get("architecture"),
        "onboarding": store.get("onboarding"),
        "created_at": store["created_at"],
        "completed_at": store.get("completed_at"),
        "error": store.get("error"),
    }
