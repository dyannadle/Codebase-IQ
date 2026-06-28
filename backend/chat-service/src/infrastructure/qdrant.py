from qdrant_client import AsyncQdrantClient
from src.config.settings import settings

class QdrantConnector:
    def __init__(self):
        self.client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None
        )
        self.collection_name = "codebase_chunks"

    async def search(self, query_vector: list[float], org_id: str, repo_ids: list[str], limit: int = 5):
        """Performs a semantic search with payload filtering for RBAC."""
        try:
            from qdrant_client.http import models
            
            # Filter by Organization and specific Repositories
            filter_conditions = models.Filter(
                must=[
                    models.FieldCondition(
                        key="organization_id",
                        match=models.MatchValue(value=org_id)
                    ),
                    models.FieldCondition(
                        key="repository_id",
                        match=models.MatchAny(any=repo_ids)
                    )
                ]
            )

            results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=filter_conditions,
                limit=limit
            )
            return results
        except Exception as e:
            print(f"Qdrant Search Error: {e}")
            return []

qdrant_db = QdrantConnector()
