from neo4j import AsyncGraphDatabase
from src.config.settings import settings

class Neo4jConnector:
    def __init__(self):
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI, 
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    async def close(self):
        await self.driver.close()

    async def get_dependencies(self, file_path: str, repo_id: str):
        """Finds what a file imports and what imports it (1-hop)."""
        cypher_query = """
        MATCH (f:File {path: $file_path, repository_id: $repo_id})
        OPTIONAL MATCH (f)-[:IMPORTS]->(imported:File)
        OPTIONAL MATCH (importer:File)-[:IMPORTS]->(f)
        RETURN 
            collect(DISTINCT imported.path) as imports,
            collect(DISTINCT importer.path) as imported_by
        """
        async with self.driver.session() as session:
            try:
                result = await session.run(cypher_query, file_path=file_path, repo_id=repo_id)
                record = await result.single()
                if record:
                    return {
                        "imports": record["imports"],
                        "imported_by": record["imported_by"]
                    }
                return {"imports": [], "imported_by": []}
            except Exception as e:
                print(f"Neo4j Query Error: {e}")
                return {"imports": [], "imported_by": []}

neo4j_db = Neo4jConnector()
