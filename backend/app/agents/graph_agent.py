from __future__ import annotations

from app.services.github_service import GitHubService
from app.services.llm_service import LLMService
from app.graph.builder import GraphBuilder


class GraphAgent:
    def __init__(
        self, github_service: GitHubService | None = None, llm: LLMService | None = None
    ) -> None:
        self.github = github_service or GitHubService()

    async def run(self, repo_url: str, max_files: int = 500) -> Any:
        builder = GraphBuilder(self.github)
        return await builder.build_from_repo_url(repo_url, max_files=max_files)
