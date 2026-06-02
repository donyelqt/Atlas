from __future__ import annotations

import logging
from typing import Any

from app.services.neo4j_service import neo4j_service

logger = logging.getLogger(__name__)


class GraphSearchService:
    """Repository-scoped natural-language and Cypher search over the Neo4j graph."""

    async def _get_driver(self):
        svc = neo4j_service
        await svc.connect()
        return svc._driver

    async def search(
        self,
        analysis_id: str,
        query: str,
        *,
        hops: int = 2,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Run a natural-language graph search across all levels."""
        driver = await self._get_driver()
        db = neo4j_service
        cypher = f"""
            MATCH (r:Repository {{id: $repo_id}})-[:HAS_NODE]->(start:Node)
            WHERE toLower(start.label) CONTAINS toLower($query)
               OR toLower(start.path)  CONTAINS toLower($query)
            WITH start
            CALL apoc.path.expand(start, null, null, 0, $hops) YIELD path
            WITH path, nodes(path) AS ns, relationships(path) AS rs
            WHERE ALL(n IN ns WHERE (n:Node) AND EXISTS {{ MATCH (r:Repository {{id:$repo_id}})-[:HAS_NODE]->(n) }})
            RETURN
              [n IN ns | {{id:n.id, label:n.label, type:n.type, path:n.path}}] AS node_path,
              [r IN rs | type(r)]                                AS edge_types
            LIMIT $limit
        """
        async with driver.session(database=db.neo4j_database) as session:
            result = await session.run(
                cypher, repo_id=analysis_id, query=query, hops=hops, limit=limit
            )
            rows = [dict(record) async for record in result]
        return {"query": query, "hops": hops, "results": rows}

    async def related_nodes(
        self,
        analysis_id: str,
        node_id: str,
        *,
        hops: int = 2,
        limit: int = 30,
    ) -> dict[str, Any]:
        """Get nodes connected to the given node within `hops` hops."""
        driver = await self._get_driver()
        db = neo4j_service
        cypher = """
            MATCH (start:Node {id:$node_id})
            CALL apoc.path.expand(start, null, null, 0, $hops) YIELD path
            WITH path, nodes(path) AS ns, relationships(path) AS rs
            WHERE ALL(n IN ns WHERE (n:Node) AND EXISTS {
                    MATCH (r:Repository {id:$repo_id})-[:HAS_NODE]->(n)
            })
            RETURN
              [n IN ns | {id:n.id, label:n.label, type:n.type, path:n.path}] AS node_path,
              [r IN rs | type(r)]                                         AS edge_types
            LIMIT $limit
        """
        async with driver.session(database=db.neo4j_database) as session:
            result = await session.run(
                cypher, repo_id=analysis_id, node_id=node_id, hops=hops, limit=limit
            )
            rows = [dict(record) async for record in result]
        return {"node_id": node_id, "hops": hops, "paths": rows}

    async def entry_points(self, analysis_id: str, limit: int = 20) -> dict[str, Any]:
        """Return candidate entry-point files/modules for the repo."""
        driver = await self._get_driver()
        db = neo4j_service
        cypher = """
            MATCH (r:Repository {id:$repo_id})-[:HAS_NODE]->(n:Node)
            WHERE n.type IN ['file','module']
              AND (
                    toLower(n.label) STARTS WITH 'main'
                 OR toLower(n.label) STARTS WITH 'index'
                 OR toLower(n.label) STARTS WITH 'app'
                 OR toLower(n.label) STARTS WITH 'server'
                 OR toLower(n.label) STARTS WITH 'wsgi'
              )
            RETURN n.id AS id, n.label AS label, n.type AS type, n.path AS path
            ORDER BY n.type, n.label
            LIMIT $limit
        """
        async with driver.session(database=db.neo4j_database) as session:
            result = await session.run(cypher, repo_id=analysis_id, limit=limit)
            rows = [dict(record) async for record in result]
        return {"entry_points": rows}

    async def shortest_path(
        self, analysis_id: str, source_id: str, target_id: str
    ) -> dict[str, Any] | None:
        driver = await self._get_driver()
        db = neo4j_service
        cypher = """
            MATCH (r:Repository {id:$repo_id})
            MATCH (s:Node {id:$source_id}), (t:Node {id:$target_id})
            MATCH p = shortestPath((s)-[*]-(t))
            WHERE ALL(n IN nodes(p) WHERE (n:Node) AND EXISTS {
                    MATCH (r:Repository {id:$repo_id}})-[:HAS_NODE]->(n)
            })
            RETURN [n IN nodes(p) | {id:n.id, label:n.label, type:n.type, path:n.path}] AS nodes,
                   [r IN relationships(p) | type(r)]                               AS edge_types,
                   length(p)                                                       AS hops
        """
        async with driver.session(database=db.neo4j_database) as session:
            result = await session.run(
                cypher, repo_id=analysis_id, source_id=source_id, target_id=target_id
            )
            record = await result.single()
            if record is None:
                return None
            return {
                "source": source_id,
                "target": target_id,
                "hops": record["hops"],
                "nodes": record["nodes"],
                "edge_types": record["edge_types"],
            }

    async def node_degree(self, analysis_id: str, node_id: str) -> dict[str, Any]:
        driver = await self._get_driver()
        db = neo4j_service
        cypher = """
            MATCH (r:Repository {id:$repo_id}})
            MATCH (n:Node {id:$node_id})
            OPTIONAL MATCH (n)-[out:EDGE]->()
            OPTIONAL MATCH (n)<-[inc:EDGE]-()
            RETURN n.id AS id,
                   n.label AS label,
                   n.type AS type,
                   count(DISTINCT out) AS outgoing,
                   count(DISTINCT inc) AS incoming,
                   count(DISTINCT out) + count(DISTINCT inc) AS total
        """
        async with driver.session(database=db.neo4j_database) as session:
            record = await session.run(
                cypher, repo_id=analysis_id, node_id=node_id
            ).single()
        if record is None:
            return {"node_id": node_id, "found": False}
        return {
            "node_id": record["id"],
            "label": record["label"],
            "type": record["type"],
            "outgoing": record["outgoing"],
            "incoming": record["incoming"],
            "total": record["total"],
        }


graph_search = GraphSearchService()
