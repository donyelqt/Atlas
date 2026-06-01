from __future__ import annotations

import re
import os
from typing import Any
from urllib.parse import urlparse

import httpx

from app.core.config import settings


class GitHubService:
    BASE_URL = "https://api.github.com"

    def __init__(self) -> None:
        self._headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "Atlas/0.1.0",
        }
        if settings.github_token:
            self._headers["Authorization"] = f"Bearer {settings.github_token}"

    @staticmethod
    def parse_repo_url(repo_url: str) -> tuple[str, str]:
        parsed = urlparse(repo_url)
        parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
        owner, repo = parts[0], parts[1]
        repo = repo.replace(".git", "")
        return owner, repo

    async def _get(self, url: str, params: dict[str, Any] | None = None) -> Any:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=self._headers, params=params)
            resp.raise_for_status()
            return resp.json()

    async def get_repo_info(self, owner: str, repo: str) -> dict[str, Any]:
        return await self._get(f"{self.BASE_URL}/repos/{owner}/{repo}")

    async def get_repo_tree(
        self, owner: str, repo: str, recursive: bool = True
    ) -> list[dict[str, Any]]:
        branch = "main"
        tree_data = await self._get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/git/trees/{branch}",
            params={"recursive": "1" if recursive else "0"},
        )
        if tree_data.get("truncated"):
            pass
        return tree_data.get("tree", [])

    async def get_file_content(self, owner: str, repo: str, path: str, ref: str = "main") -> str | None:
        try:
            data = await self._get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}",
                params={"ref": ref},
            )
            if data.get("encoding") == "base64":
                import base64
                return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return data.get("content", "")
        except httpx.HTTPStatusError:
            return None

    async def get_languages(self, owner: str, repo: str) -> dict[str, int]:
        return await self._get(f"{self.BASE_URL}/repos/{owner}/{repo}/languages")

    LANG_EXT = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
        ".jsx": "JavaScript", ".java": "Java", ".go": "Go", ".rs": "Rust",
        ".rb": "Ruby", ".php": "PHP", ".cs": "C#", ".cpp": "C++", ".c": "C",
        ".swift": "Swift", ".kt": "Kotlin", ".scala": "Scala", ".r": "R",
        ".ex": "Elixir", ".exs": "Elixir", ".hs": "Haskell", ".ml": "OCaml",
        ".lua": "Lua", ".dart": "Dart", ".vue": "Vue", ".svelte": "Svelte",
    }

    FRAMEWORK_SIGNALS = {
        "next.js": ["next.config", "pages/_app", "app/layout"],
        "react": ["react", "package.json"],
        "vue": ["vue.config", "nuxt.config"],
        "django": ["settings.py", "manage.py", "wsgi.py"],
        "flask": ["app.py", "flask"],
        "fastapi": ["fastapi", "main.py"],
        "express": ["express", "app.js"],
        "spring": ["application.properties", "application.yml"],
        "rails": ["Gemfile", "config/routes.rb"],
        "laravel": ["artisan", "composer.json"],
        "gin": ["go.mod"],
        "actix": ["Cargo.toml"],
    }

    @classmethod
    def detect_language(cls, path: str, languages: dict[str, int] | None = None) -> str | None:
        _, ext = os.path.splitext(path)
        return cls.LANG_EXT.get(ext.lower())

    @classmethod
    def detect_framework(cls, file_paths: list[str], languages: dict[str, int] | None = None) -> str | None:
        paths_lower = [p.lower() for p in file_paths]
        for framework, signals in cls.FRAMEWORK_SIGNALS.items():
            for signal in signals:
                if any(signal.lower() in p for p in paths_lower):
                    return framework
        if languages:
            top_lang = max(languages, key=languages.get) if languages else None
            if top_lang == "Python":
                return "FastAPI" if any("fastapi" in p for p in paths_lower) else "Django"
            if top_lang == "JavaScript":
                return "Next.js" if any("next" in p for p in paths_lower) else "Express"
            if top_lang == "TypeScript":
                return "Next.js" if any("next" in p for p in paths_lower) else "Express"
            if top_lang == "Go":
                return "Gin"
            if top_lang == "Rust":
                return "Actix"
        return None
