from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any


class FrameworkDetector:

    @staticmethod
    def detect(file_paths: list[str], languages: dict[str, int] | None = None) -> str | None:
        paths = [p.lower() for p in file_paths]

        checks = [
            ("Next.js", ["pages/_app.tsx", "app/layout.tsx", "next.config.js", "next.config.ts"]),
            ("Nuxt.js", ["nuxt.config.js", "nuxt.config.ts", "pages/index.vue"]),
            ("React", ["package.json"]),
            ("Vue", ["vue.config.js", "vite.config.js"]),
            ("Svelte", ["svelte.config.js", "vite.config.js"]),
            ("Django", ["manage.py", "settings.py"]),
            ("FastAPI", ["main.py"]),
            ("Flask", ["app.py", "flask"]),
            ("Express.js", ["app.js", "index.js"]),
            ("Spring Boot", ["application.properties", "application.yml", "pom.xml"]),
            ("Rails", ["Gemfile", "config/routes.rb"]),
            ("Laravel", ["artisan", "composer.json"]),
            ("Gin", ["go.mod"]),
            ("Actix", ["Cargo.toml"]),
            ("Rocket", ["Cargo.toml"]),
            ("Phoenix", ["mix.exs"]),
        ]
        for framework, signals in checks:
            if any(signal in p for p in paths for signal in signals):
                return framework
        return None

    @staticmethod
    def detect_architecture(framework: str | None, file_paths: list[str]) -> str | None:
        if not framework:
            return "Monolith"
        layered = ["controllers", "services", "repositories", "models"]
        if sum(1 for seg in layered for p in file_paths if f"/{seg}/" in p or f"\\{seg}\\" in p) >= 2:
            return framework in ("Django", "FastAPI", "Flask", "Express.js", "Spring Boot") and "Layered Architecture" or "Modular Monolith"
        return "Monolith"

    @staticmethod
    def estimate_complexity(file_count: int, dep_count: int, dir_count: int) -> str:
        score = file_count / 1000 + dep_count / 50 + dir_count / 10
        if score < 2:
            return "Low"
        if score < 10:
            return "Medium"
        return "High"

    @staticmethod
    def derive_module_name(path: str, repo_root: str = "") -> str:
        rel = path
        if repo_root and rel.startswith(repo_root):
            rel = rel[len(repo_root):].lstrip("/\\")
        parts = PurePosixPath(rel).parts
        for skip in ("src", "lib", "app", "internal", "pkg", "core"):
            if parts and parts[0] == skip:
                parts = parts[1:]
                break
        if len(parts) >= 2:
            return parts[0] + "/" + parts[1]
        return parts[0] if parts else "root"
