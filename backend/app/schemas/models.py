from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RepoUrlRequest(BaseModel):
    repo_url: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"repo_url": "https://github.com/vercel/next.js"}]
        }
    }


class ChatRequest(BaseModel):
    analysis_id: str
    question: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"analysis_id": "abc-123", "question": "How does authentication work?"}]
        }
    }


class AnalysisSummary(BaseModel):
    id: str
    status: AnalysisStatus
    repo_url: str
    framework: str | None = None
    language: str | None = None
    file_count: int = 0
    directory_count: int = 0
    architecture_type: str | None = None
    complexity: str | None = None
    error: str | None = None
    created_at: str
    completed_at: str | None = None


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    path: str
    language: str | None = None
    size: int = 0
    children: list[str] | None = None


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str
    label: str | None = None


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] | None = None


class FileInfo(BaseModel):
    path: str
    name: str
    type: str
    language: str | None = None
    size: int
    content_preview: str | None = None
    imports: list[str] | None = None
    exports: list[str] | None = None
    functions: list[str] | None = None
    classes: list[str] | None = None


class ModuleInfo(BaseModel):
    name: str
    path: str
    files: list[FileInfo]
    dependencies: list[str]
    description: str | None = None
