from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Any

from app.services.neo4j_service import neo4j_service
from app.api.routes.analyze import _analysis_store, _graph_cache

import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class GraphSearchQuery(BaseModel):
    query: str = Field(..., description="Natural-language or path fragment to search for")
    hops: int = Field(default=2, ge=1, le=4, description="Max traversal depth")
    limit: int = Field(default=20, ge=1, le=100)


class NodeQuery(BaseModel):
    node_id: str
    hops: int = Field(default=2, ge=1, le=4)
    limit: int = Field(default=30, ge=1, le=200)


class PathQuery(BaseModel):
    source_id: str
    target_id: str


def _require_completed(analysis_id: str) -> dict[str, Any] | None:
    if analysis_id not in _analysis_store:
        return None
    store = _analysis_store[analysis_id]
    if store.get("status") != "completed":
        return None
    return store


@router.post("/neo4j/sync/{analysis_id}")
async def sync_graph(analysis_id: str) -> dict[str, Any]:
    store = _require_completed(analysis_id)
    if store is None:
        return {"detail": "Analysis not found or not completed", "status": "error"}
    graph_data = _graph_cache.get(analysis_id)
    if graph_data is None:
        return {"detail": "Graph data not found", "status": "error"}
    try:
        from app.graph.models import RepositoryGraph
        graph = RepositoryGraph()
        graph.graph.add_nodes_from([(n["id"], n) for n in graph_data["nodes"]])
        graph.graph.add_edges_from([(e["source"], e["target"], e) for e in graph_data["edges"]])
        await neo4j_service.upsert_repo(analysis_id, store["repo_data"], graph)
        return {"status": "ok", "analysis_id": analysis_id, "nodes": len(graph_data["nodes"]), "edges": len(graph_data["edges"])}
    except Exception as exc:
        logger.exception("Failed to sync to Neo4j: %s", exc)
        return {"detail": str(exc), "status": "error"}


@router.get("/neo4j/graph/{analysis_id}")
async def get_neo4j_graph(analysis_id: str) -> dict[str, Any]:
    try:
        return await neo4j_service.get_graph(analysis_id)
    except Exception as exc:
        logger.exception("Failed to fetch Neo4j graph: %s", exc)
        return {"detail": str(exc), "nodes": [], "edges": []}


@router.get("/neo4j/entry-points/{analysis_id}")
async def get_entry_points(analysis_id: str, limit: int = 20) -> dict[str, Any]:
    try:
        return await neo4j_service.get_entry_points(analysis_id, limit=limit)
    except Exception as exc:
        logger.exception("Failed to fetch entry points: %s", exc)
        return {"entry_points": [], "detail": str(exc)}


@router.get("/neo4j/related/{analysis_id}/{node_id}")
async def get_related(analysis_id: str, node_id: str, hops: int = 2, limit: int = 30) -> dict[str, Any]:
    try:
        return await neo4j_service.find_related(analysis_id, node_id, hops=min(hops, 4), limit=limit)
    except Exception as exc:
        logger.exception("Failed to find related: %s", exc)
        return {"paths": [], "detail": str(exc)}


@router.get("/neo4j/path/{analysis_id}")
async def shortest_path(analysis_id: str, source: str, target: str) -> dict[str, Any]:
    try:
        result = await neo4j_service.shortest_path(analysis_id, source, target)
        if result is None:
            return {"detail": "No path found", "source": source, "target": target}
        return result
    except Exception as exc:
        logger.exception("Failed shortest path: %s", exc)
        return {"detail": str(exc)}


@router.post("/neo4j/search/{analysis_id}")
async def search_graph(analysis_id: str, body: GraphSearchQuery) -> dict[str, Any]:
    store = _require_completed(analysis_id)
    if store is None:
        return {"detail": "Analysis not found or not completed", "results": []}
    try:
        return await neo4j_service.search(analysis_id, body.query, hops=body.hops, limit=body.limit)
    except Exception as exc:
        logger.exception("Graph search failed: %s", exc)
        return {"query": body.query, "results": [], "detail": str(exc)}
