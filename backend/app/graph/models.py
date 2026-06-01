from __future__ import annotations

import networkx as nx
from typing import Any


NodeData = dict[str, Any]
EdgeData = dict[str, Any]


class RepositoryGraph:
    def __init__(self) -> None:
        self.graph = nx.DiGraph()

    def add_node(self, node_id: str, **attrs: Any) -> None:
        self.graph.add_node(node_id, **attrs)

    def add_edge(self, source: str, target: str, **attrs: Any) -> None:
        self.graph.add_edge(source, target, **attrs)

    def to_dict(self) -> dict[str, Any]:
        node_lookup = {}
        for node_id, data in self.graph.nodes(data=True):
            node_lookup[node_id] = {
                "id": node_id,
                "label": data.get("label", node_id),
                "type": data.get("type", "unknown"),
                "path": data.get("path", node_id),
                "language": data.get("language"),
                "size": data.get("size", 0),
                "children": data.get("children"),
            }
        edge_list = []
        for source, target, data in self.graph.edges(data=True):
            edge_list.append({
                "source": source,
                "target": target,
                "type": data.get("type", "unknown"),
                "label": data.get("label"),
            })
        return {"nodes": list(node_lookup.values()), "edges": edge_list}

    def build_from_modules(self, modules: list[dict[str, Any]], edges: list[dict[str, Any]] | None = None) -> None:
        dir_nodes: dict[str, dict[str, Any]] = {}
        file_nodes: dict[str, dict[str, Any]] = {}
        module_map: dict[str, str] = {}

        for module in modules:
            mod_name = module.get("name", "root")
            mod_path = module.get("path", "")
            module_map[mod_name] = mod_path
            dir_label = mod_name.split("/")[-1] if "/" in mod_name else mod_name
            self.add_node(
                mod_path,
                label=dir_label,
                type="module",
                path=mod_path,
                language=module.get("language"),
                children=[],
            )
            dir_nodes[mod_path] = {"name": mod_name, "path": mod_path}
            for file_info in module.get("files", []):
                fpath = file_info.get("path", "")
                fname = file_info.get("name", "")
                self.add_node(
                    fpath,
                    label=fname,
                    type="file",
                    path=fpath,
                    language=file_info.get("language"),
                    size=file_info.get("size", 0),
                )
                file_nodes[fpath] = file_info
                self.add_edge(mod_path, fpath, type="contains")
                imports = file_info.get("imports") or []
                for imp in imports:
                    imp_path = self._resolve_import(imp, fpath, file_nodes)
                    if imp_path and imp_path in file_nodes:
                        self.add_edge(fpath, imp_path, type="imports", label=imp)

        if edges:
            for edge in edges:
                self.add_edge(edge.get("source", ""), edge.get("target", ""), type=edge.get("type", "unknown"))

    @staticmethod
    def _resolve_import(imp: str, from_path: str, known_files: dict[str, Any]) -> str | None:
        if imp.startswith("."):
            from_dir = "/".join(from_path.split("/")[:-1])
            resolved = from_dir + "/" + imp.lstrip(".")
            for k in known_files:
                if k.endswith(resolved) or resolved in k:
                    return k
        for k in known_files:
            if k.endswith("/" + imp.replace(".", "/") + ".py") or k.endswith("/" + imp + ".py"):
                return k
        return None
