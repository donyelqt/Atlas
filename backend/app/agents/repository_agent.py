from __future__ import annotations

import logging
from typing import Any

from app.parsers.framework_detector import FrameworkDetector
from app.services.github_service import GitHubService

logger = logging.getLogger(__name__)


class RepositoryAgent:
    def __init__(self) -> None:
        self.github = GitHubService()

    async def run(self, repo_url: str, max_files: int = 500) -> dict[str, Any]:
        owner, repo = self.github.parse_repo_url(repo_url)
        repo_info = await self.github.get_repo_info(owner, repo)
        tree = await self.github.get_repo_tree(owner, repo, recursive=True)
        languages = await self.github.get_languages(owner, repo)

        blob_entries = [e for e in tree if e.get("type") == "blob"]
        tree_entries = [e for e in tree if e.get("type") == "tree"]
        file_paths = [e["path"] for e in blob_entries]
        if len(file_paths) > max_files:
            file_paths = file_paths[:max_files]

        framework = self.github.detect_framework(file_paths, languages)
        lang_top = max(languages, key=languages.get) if languages else None
        arch = FrameworkDetector.detect_architecture(framework, file_paths)
        complexity = FrameworkDetector.estimate_complexity(
            len(blob_entries), len(tree_entries), len(tree_entries)
        )

        modules = self._build_modules(file_paths)

        return {
            "repo_url": repo_url,
            "name": repo,
            "full_name": f"{owner}/{repo}",
            "description": repo_info.get("description"),
            "framework": framework,
            "language": lang_top,
            "languages": dict(list(languages.items())[:10]),
            "file_count": len(blob_entries),
            "directory_count": len(tree_entries),
            "architecture_type": arch,
            "complexity": complexity,
            "modules": modules,
            "stars": repo_info.get("stargazers_count", 0),
            "license": (repo_info.get("license") or {}).get("name"),
        }

    def _build_modules(self, file_paths: list[str]) -> list[dict[str, Any]]:
        grouped: dict[str, list[str]] = {}
        for path in file_paths:
            mod = FrameworkDetector.derive_module_name(path)
            grouped.setdefault(mod, []).append(path)
        return [{"name": k, "path": k, "files": v} for k, v in grouped.items()]
