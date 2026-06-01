from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from tree_sitter import Language, Parser
import tree_sitter_languages

from app.parsers import framework_detector


_lang_cache: dict[str, Language] = {}


def get_language(lang_name: str) -> Language | None:
    if lang_name not in _lang_cache:
        try:
            langs = tree_sitter_languages.get_language(lang_name)
            _lang_cache[lang_name] = langs
        except Exception:
            return None
    return _lang_cache.get(lang_name)


LANG_MAP: dict[str, str] = {
    ".py": "python", ".js": "javascript", ".ts": "typescript", ".tsx": "tsx",
    ".jsx": "javascript", ".java": "java", ".go": "go", ".rs": "rust",
    ".rb": "ruby", ".php": "php", ".cs": "c_sharp", ".cpp": "cpp", ".c": "c",
    ".swift": "swift", ".kt": "kotlin", ".scala": "scala", ".r": "r",
    ".ex": "elixir", ".exs": "elixir", ".hs": "haskell", ".lua": "lua",
    ".dart": "dart", ".vue": "vue", ".svelte": "svelte",
}

import typing as _typing
if _typing.TYPE_CHECKING:
    import tree_sitter


def detect_language_from_path(path: str) -> str | None:
    _, ext = Path(path).suffix.lower()
    return LANG_MAP.get(ext)


IMPORT_QUERIES: dict[str, str] = {
    "python": """
    (import_statement name: (dotted_name (name) @import) (#match? @import "^([a-zA-Z_][a-zA-Z0-9_]*)"))
    (import_from_statement module_name: (dotted_name (name) @import))
    """,
    "javascript": """
    (import_statement source: (string) @import)
    (call_expression
      function: (identifier) @func
      (#eq? @func "require")
      arguments: (arguments (string) @import)
    )
    """,
    "typescript": """
    (import_statement source: (string) @import)
    """,
    "tsx": """
    (import_statement source: (string) @import)
    """,
    "go": """
    (import_spec path: (interpreted_string_literal) @import)
    """,
    "rust": """
    (use_declaration argument: (scoped_identifier path: (identifier) @import))
    """,
}

FUNCTION_QUERIES: dict[str, str] = {
    "python": "(function_definition name: (identifier) @function)",
    "javascript": "(function_declaration name: (identifier) @function) (variable_declarator name: (identifier) @function value: (arrow_function))",
    "typescript": "(function_declaration name: (identifier) @function) (method_definition name: (property_identifier) @function)",
    "go": "(function_declaration name: (identifier) @function)",
    "rust": "(function_item name: (identifier) @function)",
}

CLASS_QUERIES: dict[str, str] = {
    "python": "(class_definition name: (identifier) @class)",
    "javascript": "(class_declaration name: (identifier) @class)",
    "typescript": "(class_declaration name: (type_identifier) @class) (interface_declaration name: (type_identifier) @class)",
    "go": "(type_spec name: (type_identifier) @class)",
    "rust": "(struct_item name: (field_identifier) @class)",
}


async def parse_file(path: str, content: str, language: str | None = None) -> dict[str, Any]:
    lang_name = language or detect_language_from_path(path)
    if not lang_name:
        return _basic_parse(content, path)
    lang = get_language(lang_name)
    if lang is None:
        return _basic_parse(content, path)

    try:
        parser = Parser()
        parser.set_language(lang)
        tree = parser.parse(bytes(content, "utf-8"))
        root = tree.root_node

        imports = _query_nodes(root, lang, IMPORT_QUERIES.get(lang_name, ""))
        functions = _query_nodes(root, lang, FUNCTION_QUERIES.get(lang_name, ""))
        classes = _query_nodes(root, lang, CLASS_QUERIES.get(lang_name, ""))

        return {
            "imports": imports,
            "functions": functions,
            "classes": classes,
            "size": len(content),
            "lines": content.count("\n") + 1,
            "content_preview": content[:2000],
        }
    except Exception:
        return _basic_parse(content, path)


def _query_nodes(root: Any, lang: Language, query_str: str) -> list[str]:
    if not query_str:
        return []
    try:
        query = lang.query(query_str)
        captures = query.captures(root)
        results: list[str] = []
        for node, _name in captures:
            results.append(node.text.decode("utf-8", errors="replace"))
        return list(dict.fromkeys(results))
    except Exception:
        return []


def _basic_parse(content: str, path: str) -> dict[str, Any]:
    return {
        "imports": [],
        "functions": [],
        "classes": [],
        "size": len(content),
        "lines": content.count("\n") + 1,
        "content_preview": content[:2000],
    }
