"""
Qdrant Vector Database Client

Provides high-level interface for vector operations.
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

from qdrant_client import QdrantClient as QdrantSDKClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
    CollectionInfo,
    ScoredPoint
)

from .config import qdrant_config, COLLECTIONS_CONFIG

logger = logging.getLogger(__name__)


class QdrantVectorDB:
    """
    Qdrant Vector Database Client

    High-level interface for vector operations with collections.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        api_key: Optional[str] = None,
        collection: Optional[str] = None
    ):
        """
        Initialize Qdrant client

        Args:
            host: Qdrant host (default from config)
            port: Qdrant port (default from config)
            api_key: API key for authentication (optional)
            collection: Default collection name
        """
        self.url = qdrant_config.url
        self.api_key = api_key or qdrant_config.api_key
        self.default_collection = collection

        # Initialize SDK client (Qdrant Cloud)
        self.client = QdrantSDKClient(
            url=self.url,
            api_key=self.api_key,
            timeout=qdrant_config.timeout
        )

        logger.info(f"Initialized Qdrant Cloud client: {self.url}")

    async def create_collection(
        self,
        collection_name: str,
        recreate: bool = False
    ) -> bool:
        """
        Create collection if not exists

        Args:
            collection_name: Collection name
            recreate: If True, delete and recreate collection

        Returns:
            True if created, False if already exists
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)

            if exists and recreate:
                logger.info(f"Deleting existing collection: {collection_name}")
                self.client.delete_collection(collection_name=collection_name)
                exists = False

            if not exists:
                # Get config
                config = COLLECTIONS_CONFIG.get(collection_name, {})
                vector_size = config.get("vector_size", qdrant_config.embedding_dimension)
                distance = config.get("distance", qdrant_config.distance_metric)

                # Map distance string to enum
                distance_map = {
                    "Cosine": Distance.COSINE,
                    "Euclid": Distance.EUCLID,
                    "Dot": Distance.DOT
                }
                distance_enum = distance_map.get(distance, Distance.COSINE)

                # Create collection
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=distance_enum
                    )
                )

                logger.info(f"Created collection: {collection_name} (size={vector_size}, distance={distance})")
                return True
            else:
                logger.info(f"Collection already exists: {collection_name}")
                return False

        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            raise

    def upsert(
        self,
        collection_name: Optional[str] = None,
        points: List[Dict[str, Any]] = None,
        vectors: Optional[List[List[float]]] = None,
        payloads: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        Upsert vectors into collection

        Args:
            collection_name: Collection name (uses default if None)
            points: List of points with id, vector, payload
            vectors: List of vectors (if not using points)
            payloads: List of payloads (if not using points)
            ids: List of IDs (if not using points)

        Returns:
            True if successful
        """
        collection = collection_name or self.default_collection
        if not collection:
            raise ValueError("Collection name not specified")

        try:
            # Build points
            if points:
                point_structs = [
                    PointStruct(
                        id=p.get("id") or str(uuid4()),
                        vector=p["vector"],
                        payload=p.get("payload", {})
                    )
                    for p in points
                ]
            elif vectors and payloads:
                if ids and len(ids) != len(vectors):
                    raise ValueError("IDs length must match vectors length")

                point_structs = [
                    PointStruct(
                        id=ids[i] if ids else str(uuid4()),
                        vector=vectors[i],
                        payload=payloads[i] if i < len(payloads) else {}
                    )
                    for i in range(len(vectors))
                ]
            else:
                raise ValueError("Must provide either points or (vectors + payloads)")

            # Upsert
            self.client.upsert(
                collection_name=collection,
                points=point_structs
            )

            logger.info(f"Upserted {len(point_structs)} points to {collection}")
            return True

        except Exception as e:
            logger.error(f"Error upserting to {collection}: {e}")
            raise

    def search(
        self,
        query_vector: List[float],
        collection_name: Optional[str] = None,
        limit: int = None,
        filters: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = None,
        with_payload: bool = True,
        with_vectors: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors

        Args:
            query_vector: Query embedding vector
            collection_name: Collection name (uses default if None)
            limit: Max results to return
            filters: Metadata filters (e.g., {"category": "standard"})
            min_score: Minimum similarity score
            with_payload: Include payload in results
            with_vectors: Include vectors in results

        Returns:
            List of search results with id, score, payload
        """
        collection = collection_name or self.default_collection
        if not collection:
            raise ValueError("Collection name not specified")

        limit = limit or qdrant_config.default_limit
        min_score = min_score or qdrant_config.min_score

        try:
            # Build filters
            query_filter = None
            if filters:
                must_conditions = []
                for key, value in filters.items():
                    must_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                query_filter = Filter(must=must_conditions)

            # Search
            results = self.client.search(
                collection_name=collection,
                query_vector=query_vector,
                limit=limit,
                query_filter=query_filter,
                with_payload=with_payload,
                with_vectors=with_vectors,
                score_threshold=min_score
            )

            # Format results
            formatted_results = [
                {
                    "id": str(hit.id),
                    "score": hit.score,
                    "payload": hit.payload if with_payload else None,
                    "vector": hit.vector if with_vectors else None
                }
                for hit in results
            ]

            logger.info(f"Search in {collection}: found {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching {collection}: {e}")
            raise

    def delete(
        self,
        ids: List[str],
        collection_name: Optional[str] = None
    ) -> bool:
        """
        Delete points by IDs

        Args:
            ids: List of point IDs to delete
            collection_name: Collection name (uses default if None)

        Returns:
            True if successful
        """
        collection = collection_name or self.default_collection
        if not collection:
            raise ValueError("Collection name not specified")

        try:
            self.client.delete(
                collection_name=collection,
                points_selector=ids
            )

            logger.info(f"Deleted {len(ids)} points from {collection}")
            return True

        except Exception as e:
            logger.error(f"Error deleting from {collection}: {e}")
            raise

    def get_collection_info(
        self,
        collection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get collection information

        Args:
            collection_name: Collection name (uses default if None)

        Returns:
            Collection info dict
        """
        collection = collection_name or self.default_collection
        if not collection:
            raise ValueError("Collection name not specified")

        try:
            info = self.client.get_collection(collection_name=collection)

            return {
                "name": collection,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "status": info.status.value,
                "optimizer_status": info.optimizer_status.status.value if info.optimizer_status else None,
                "config": {
                    "vector_size": info.config.params.vectors.size,
                    "distance": info.config.params.vectors.distance.value
                }
            }

        except Exception as e:
            logger.error(f"Error getting info for {collection}: {e}")
            raise

    def scroll(
        self,
        collection_name: Optional[str] = None,
        limit: int = 100,
        offset: Optional[str] = None,
        with_payload: bool = True,
        with_vectors: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Scroll through collection points

        Args:
            collection_name: Collection name
            limit: Max results per page
            offset: Offset ID from previous scroll
            with_payload: Include payload
            with_vectors: Include vectors
            filters: Metadata filters

        Returns:
            (points, next_offset)
        """
        collection = collection_name or self.default_collection
        if not collection:
            raise ValueError("Collection name not specified")

        try:
            # Build filters
            query_filter = None
            if filters:
                must_conditions = []
                for key, value in filters.items():
                    must_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                query_filter = Filter(must=must_conditions)

            # Scroll
            result, next_offset = self.client.scroll(
                collection_name=collection,
                limit=limit,
                offset=offset,
                with_payload=with_payload,
                with_vectors=with_vectors,
                scroll_filter=query_filter
            )

            # Format points
            points = [
                {
                    "id": str(point.id),
                    "payload": point.payload if with_payload else None,
                    "vector": point.vector if with_vectors else None
                }
                for point in result
            ]

            return points, next_offset

        except Exception as e:
            logger.error(f"Error scrolling {collection}: {e}")
            raise

    def health_check(self) -> bool:
        """
        Check if Qdrant is healthy

        Returns:
            True if healthy
        """
        try:
            collections = self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
