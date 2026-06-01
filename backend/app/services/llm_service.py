from __future__ import annotations

import re
from typing import Any

from app.core.config import settings


class LLMService:
    def __init__(self, provider: str | None = None, model: str | None = None) -> None:
        self.provider = provider or settings.llm_provider
        self.model = model or settings.llm_model
        self._client: Any = None

    def _get_python_client(self) -> Any:
        if self.provider == "openai":
            from openai import AsyncOpenAI
            return AsyncOpenAI(api_key=settings.openai_api_key)
        if self.provider == "anthropic":
            from anthropic import AsyncAnthropic
            return AsyncAnthropic(api_key=settings.anthropic_api_key)
        if self.provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=settings.google_api_key)
            return genai.GenerativeModel(self.model)
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        if not settings.has_llm_key:
            return "[LLM key not configured]"
        try:
            client = self._get_python_client()
            if self.provider == "openai":
                msgs = []
                if system_prompt:
                    msgs.append({"role": "system", "content": system_prompt})
                msgs.append({"role": "user", "content": prompt})
                resp = await client.chat.completions.create(
                    model=self.model, messages=msgs, max_tokens=4096, temperature=0.3
                )
                return resp.choices[0].message.content or ""
            if self.provider == "anthropic":
                resp = await client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=0.3,
                    system=system_prompt or "",
                    messages=[{"role": "user", "content": prompt}],
                )
                return resp.content[0].text
            if self.provider == "google":
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                resp = client.generate_content(full_prompt)
                return resp.text
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as exc:
            return f"[LLM Error: {type(exc).__name__}: {exc}]"

    async def generate_architecture_summary(
        self,
        repo_name: str,
        language: str | None,
        framework: str | None,
        file_count: int,
        structure_summary: str,
        key_modules: list[dict[str, Any]],
    ) -> dict[str, Any]:
        system = """You are an expert software architect.
Analyze the repository structure and provide an architecture assessment.
Respond with a JSON object with keys: architecture_type, key_modules (list of {name, description}),
complexity (one of: Low, Medium, High), summary (one paragraph)."""

        prompt = f"""Repository: {repo_name}
Language: {language or 'Unknown'}
Framework: {framework or 'Unknown'}
File count: {file_count}
Structure:
{structure_summary}

Key modules detected:
{chr(10).join(f'- {m.get("name","")}: {m.get("path","")}' for m in key_modules[:20])}
"""
        response = await self.generate(prompt, system)
        try:
            import json
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        return {
            "architecture_type": "Unknown",
            "key_modules": [],
            "complexity": "Medium",
            "summary": response[:500],
        }

    async def answer_question(
        self,
        question: str,
        repo_name: str,
        file_contexts: list[dict[str, Any]],
        architecture_summary: str,
    ) -> str:
        system = f"""You are Atlas, an AI software architect assistant for the repository '{repo_name}'.
Use ONLY the provided file contexts to answer. If information is not available, say so clearly.
Cite file paths when referencing specific code."""

        files_text = "\n\n".join(
            f"--- {f.get('path','')} ---\n{f.get('content_preview','') or ''}"
            for f in file_contexts[:10]
        )

        prompt = f"""Architecture Summary:
{architecture_summary}

File Contexts:
{files_text}

User Question: {question}"""
        return await self.generate(prompt, system)

    async def generate_onboarding(
        self,
        repo_name: str,
        entry_point: str | None,
        key_modules: list[dict[str, Any]],
        architecture_type: str | None,
    ) -> dict[str, Any]:
        system = """You are a senior engineer creating an onboarding plan.
Return JSON with: steps (list of {{title, description, files, estimated_minutes}}),
total_estimated_minutes, prerequisites."""

        prompt = f"""Repository: {repo_name}
Architecture: {architecture_type or 'Unknown'}
Entry point: {entry_point or 'Unknown'}
Key modules:
{chr(10).join(f'- {m.get("name","")}: {m.get("path","")}' for m in key_modules[:15])}
"""
        response = await self.generate(prompt, system)
        try:
            import json
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        return {
            "steps": [
                {"title": "Explore entry point", "description": "Start with the main application file", "files": [entry_point] if entry_point else [], "estimated_minutes": 10},
                {"title": "Understand architecture", "description": f"Review the {architecture_type or 'project'} structure", "files": [], "estimated_minutes": 15},
                {"title": "Study key modules", "description": "Explore the core business logic modules", "files": [m.get("path","") for m in key_modules[:5]], "estimated_minutes": 20},
            ],
            "total_estimated_minutes": 45,
            "prerequisites": ["Basic familiarity with the language used"],
        }
