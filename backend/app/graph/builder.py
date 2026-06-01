from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.graph.models import RepositoryGraph
from app.services.github_service import GitHubService
from app.parsers.tree_sitter_parser import parse_file
from app.parsers.framework_detector import FrameworkDetector


class GraphBuilder:
    def __init__(self, github_service: GitHubService | None = None) -> None:
        self.github = github_service or GitHubService()

    async def build_from_repo_url(self, repo_url: str, max_files: int = 500) -> RepositoryGraph:
        owner, repo = self.github.parse_repo_url(repo_url)
        repo_info = await self.github.get_repo_info(owner, repo)
        tree = await self.github.get_repo_tree(owner, repo, recursive=True)
        languages = await self.github.get_languages(owner, repo)

        file_entries = [e for e in tree if e.get("type") == "blob"]
        if len(file_entries) > max_files:
            file_entries = file_entries[:max_files]

        file_paths = [e["path"] for e in tree if e.get("type") == "blob"]
        framework = self.github.detect_framework(file_paths, languages)

        modules: dict[str, dict[str, Any]] = defaultdict(lambda: {
            "name": "",
            "path": "",
            "files": [],
            "dependencies": [],
            "language": None,
        })

        for entry in file_entries:
            path = entry["path"]
            lang = self.github.detect_language(path)
            mod_name = FrameworkDetector.derive_module_name(path, f"{owner}/{repo}")

            if not modules[mod_name]["name"]:
                modules[mod_name]["name"] = mod_name
                modules[mod_name]["path"] = mod_name
                modules[mod_name]["language"] = lang

            content = await self.github.get_file_content(owner, repo, path)
            parsed = parse_file(path, content or "", lang)
            file_info = {
                "path": path,
                "name": path.split("/")[-1],
                "type": "file",
                "language": lang,
                "size": entry.get("size", 0) or len(content or ""),
                "imports": parsed.get("imports", []),
                "exports": parsed.get("exports", []),
                "functions": parsed.get("functions", []),
                "classes": parsed.get("classes", []),
                "content_preview": parsed.get("content_preview"),
            }
            modules[mod_name]["files"].append(file_info)

            for imp in parsed.get("imports", []):
                if imp not in modules[mod_name]["dependencies"]:
                    modules[mod_name]["dependencies"].append(imp)

        repo_graph = RepositoryGraph()
        edges: list[dict[str, Any]] = []
        for mod_name, mod_data in modules.items():
            deps = [d for d in mod_data["dependencies"] if d in modules]
            if deps:
                for dep in deps[:5]:
                    edges.append({"source": mod_name, "target": dep, "type": "depends_on"})

        repo_graph.build_from_modules(list(modules.values()), edges)
        return repo_graph
