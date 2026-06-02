from __future__ import annotations

import logging
from typing import Any

from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class ArchitectureAgent:
    def __init__(self, llm: LLMService | None = None) -> None:
        self.llm = llm or LLMService()

    async def run(self, repo_data: dict[str, Any]) -> dict[str, Any]:
        structure_summary = "\n".join(
            f"{m['name']}: {len(m['files'])} files"
            for m in repo_data.get("modules", [])[:20]
        )
        return await self.llm.generate_architecture_summary(
            repo_name=repo_data.get("full_name", repo_data.get("name", "")),
            language=repo_data.get("language"),
            framework=repo_data.get("framework"),
            file_count=repo_data.get("file_count", 0),
            structure_summary=structure_summary,
            key_modules=repo_data.get("modules", []),
        )
