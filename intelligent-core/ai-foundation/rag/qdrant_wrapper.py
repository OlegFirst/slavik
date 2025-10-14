"""
Qdrant Client for RAG
=====================

Vector database client for knowledge storage and retrieval.
"""

import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import structlog

logger = structlog.get_logger(__name__)


class QdrantVectorStore:
    """
    Qdrant vector database client for RAG.

    Collections:
    - bcm_knowledge: ISO 22301, BCI guidelines, best practices
    - workflow_cases: Successful workflow execution cases
    - documents: Organization documents
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection_name: str = "bcm_knowledge"
    ):
        """
        Initialize Qdrant client.

        Args:
            url: Qdrant Cloud URL (from env QDRANT_URL)
            api_key: Qdrant API key (from env QDRANT_API_KEY)
            collection_name: Default collection to use
        """
        self.url = url or os.getenv("QDRANT_URL")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.collection_name = collection_name

        if not self.url or not self.api_key:
            raise ValueError(
                "Qdrant credentials not found. Set QDRANT_URL and QDRANT_API_KEY"
            )

        # Initialize Qdrant client
        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key,
            timeout=30
        )

        logger.info(
            "qdrant_initialized",
            collection=collection_name,
            url=self.url[:50] + "..."
        )

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int = 1536,  # OpenAI ada-002 embedding size
        distance: Distance = Distance.COSINE
    ) -> bool:
        """
        Create a new collection.

        Args:
            collection_name: Name of collection
            vector_size: Dimension of vectors (1536 for OpenAI, 768 for sentence-transformers)
            distance: Distance metric (COSINE, EUCLID, DOT)

        Returns:
            True if created successfully
        """
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance
                )
            )
            logger.info("collection_created", collection=collection_name)
            return True
        except Exception as e:
            logger.error("collection_create_failed", collection=collection_name, error=str(e))
            return False

    async def upsert(
        self,
        collection_name: str,
        points: List[PointStruct]
    ) -> bool:
        """
        Insert or update points in collection.

        Args:
            collection_name: Collection name
            points: List of PointStruct objects

        Returns:
            True if successful
        """
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info("points_upserted", collection=collection_name, count=len(points))
            return True
        except Exception as e:
            logger.error("upsert_failed", collection=collection_name, error=str(e))
            return False

    async def search(
        self,
        query_vector: List[float],
        collection_name: Optional[str] = None,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query embedding vector
            collection_name: Collection to search (default: self.collection_name)
            limit: Max number of results
            score_threshold: Minimum similarity score

        Returns:
            List of search results with score and payload
        """
        collection = collection_name or self.collection_name

        try:
            results = self.client.search(
                collection_name=collection,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )

            formatted_results = [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                }
                for hit in results
            ]

            logger.info(
                "search_completed",
                collection=collection,
                results_count=len(formatted_results)
            )

            return formatted_results

        except Exception as e:
            logger.error("search_failed", collection=collection, error=str(e))
            return []

    async def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get collection information."""
        try:
            info = self.client.get_collection(collection_name=collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            logger.error("get_collection_info_failed", collection=collection_name, error=str(e))
            return None

    async def close(self):
        """Close Qdrant client connection."""
        if self.client:
            self.client.close()
            logger.info("qdrant_connection_closed")
