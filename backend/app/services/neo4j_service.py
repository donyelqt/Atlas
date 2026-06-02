from __future__ import annotations

import logging
from typing import Any

from neo4j import AsyncGraphDatabase

from app.core.config import settings

logger = logging.getLogger(__name__)


class Neo4jService:
    def __init__(self) -> None:
        self._driver: AsyncGraphDatabase.driver | None = None

    async def connect(self) -> None:
        if self._driver is not None:
            return
        self._driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        try:
            await self._driver.verify_connectivity()
            logger.info("Connected to Neo4j")
        except Exception:
            logger.exception("Failed to connect to Neo4j")
            raise

    async def close(self) -> None:
        if self._driver is not None:
            await self._driver.close()
            self._driver = None

    async def upsert_repo(self, analysis_id: str, repo_data: dict[str, Any], graph: Any) -> None:
        await self.connect()
        assert self._driver is not None
        async with self._driver.session(database=settings.neo4j_database) as session:
            tx = await session.begin_transaction()
            try:
                await tx.run(
                    """
                    MERGE (r:Repository {id: $id})
                    SET r.name = $name,
                        r.url = $url,
                        r.framework = $framework,
                        r.language = $language,
                        r.file_count = $file_count,
                        r.architecture_type = $architecture,
                        r.complexity = $complexity,
                        r.updated_at = timestamp()
                    """,
                    id=analysis_id,
                    name=repo_data.get("full_name") or repo_data.get("name"),
                    url=repo_data.get("repo_url"),
                    framework=repo_data.get("framework"),
                    language=repo_data.get("language"),
                    file_count=repo_data.get("file_count", 0),
                    architecture=repo_data.get("architecture_type"),
                    complexity=repo_data.get("complexity"),
                )

                data = graph.to_dict()
                for node in data.get("nodes", []):
                    await tx.run(
                        """
                        MERGE (n:Node {id: $id})
                        SET n.label = $label,
                            n.type = $type,
                            n.path = $path,
                            n.language = $language,
                            n.size = $size
                        WITH n
                        MATCH (r:Repository {id: $repo_id})
                        MERGE (r)-[:HAS_NODE]->(n)
                        """,
                        id=node["id"],
                        label=node.get("label"),
                        type=node.get("type"),
                        path=node.get("path"),
                        language=node.get("language"),
                        size=node.get("size", 0),
                        repo_id=analysis_id,
                    )

                for edge in data.get("edges", []):
                    await tx.run(
                        """
                        MATCH (s:Node {id: $source})
                        MATCH (t:Node {id: $target})
                        MERGE (s)-[e:EDGE {type: $type}]->(t)
                        SET e.label = $label
                        """,
                        source=edge["source"],
                        target=edge["target"],
                        type=edge.get("type", "unknown"),
                        label=edge.get("label"),
                    )

                await tx.commit()
            except Exception:
                await tx.rollback()
                raise

    async def get_graph(self, analysis_id: str) -> dict[str, Any]:
        await self.connect()
        assert self._driver is not None
        async with self._driver.session(database=settings.neo4j_database) as session:
            nodes_result = await session.run(
                """
                MATCH (r:Repository {id: $repo_id})-[:HAS_NODE]->(n)
                RETURN n.id AS id, n.label AS label, n.type AS type, n.path AS path,
                       n.language AS language, n.size AS size
                ORDER BY n.type, n.label
                """,
                repo_id=analysis_id,
            )
            nodes = [dict(record) async for record in nodes_result]

            edges_result = await session.run(
                """
                MATCH (s:Node)-[e:EDGE]->(t:Node)
                WHERE EXISTS {
                    MATCH (r:Repository {id: $repo_id})-[:HAS_NODE]->(s)
                }
                RETURN s.id AS source, t.id AS target, e.type AS type, e.label AS label
                """,
                repo_id=analysis_id,
            )
            edges = [dict(record) async for record in edges_result]

            return {"nodes": nodes, "edges": edges}

    async def find_related(self, analysis_id: str, node_id: str, hops: int = 2) -> list[dict[str, Any]]:
        await self.connect()
        assert self._driver is not None
        async with self._driver.session(database=settings.neo4j_database) as session:
            result = await session.run(
                """
                MATCH (start:Node {id: $node_id})
                CALL apoc.path.expand(start, null, null, 0, $hops) YIELD path
                RETURN [n in nodes(path) | n.id] AS node_path,
                       [r in relationships(path) | type(r)] AS edge_types
                LIMIT 50
                """,
                node_id=node_id,
                hops=hops,
            )
            return [dict(record) async for record in result]

    async def get_entry_points(self, analysis_id: str) -> list[dict[str, Any]]:
        await self.connect()
        assert self._driver is not None
        async with self._driver.session(database=settings.neo4j_database) as session:
            result = await session.run(
                """
                MATCH (r:Repository {id: $repo_id})-[:HAS_NODE]->(n:Node)
                WHERE n.type IN ['file', 'module'] AND
                      (n.label STARTS WITH 'main' OR n.label STARTS WITH 'index' OR
                       n.label STARTS WITH 'app' OR n.label STARTS WITH 'server')
                RETURN n.id AS id, n.label AS label, n.type AS type, n.path AS path
                LIMIT 20
                """,
                repo_id=analysis_id,
            )
            return [dict(record) async for record in result]

    async def run_query(self, cypher: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Run a raw Cypher query (used by the chat agent for graph-backed reasoning)."""
        await self.connect()
        assert self._driver is not None
        async with self._driver.session(database=settings.neo4j_database) as session:
            result = await session.run(cypher, parameters or {})
            return [dict(record) async for record in result]
