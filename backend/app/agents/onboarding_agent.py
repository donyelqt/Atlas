from __future__ import annotations

from typing import Any

from app.services.llm_service import LLMService
from app.graph.models import RepositoryGraph


class OnboardingAgent:
    def __init__(self, llm: LLMService | None = None) -> None:
        self.llm = llm or LLMService()

    async def run(
        self, repo_data: dict[str, Any], graph: RepositoryGraph | None = None
    ) -> dict[str, Any]:
        entry_point = self._detect_entry_point(repo_data)
        modules = repo_data.get("modules", [])
        arch_summary = repo_data.get("architecture_type", "Unknown")
        return await self.llm.generate_onboarding(
            repo_name=repo_data.get("full_name", repo_data.get("name", "")),
            entry_point=entry_point,
            key_modules=modules,
            architecture_type=arch_summary,
        )

    def _detect_entry_point(self, repo_data: dict[str, Any]) -> str | None:
        candidates = [
            "main.py",
            "app.py",
            "index.js",
            "index.ts",
            "main.ts",
            "server.js",
        ]
        for mod in repo_data.get("modules", []):
            for f in mod.get("files", []):
                if f.split("/")[-1] in candidates:
                    return f
        return None
