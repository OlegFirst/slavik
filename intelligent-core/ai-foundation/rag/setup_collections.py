"""
Qdrant Collections Setup

Creates and configures Qdrant collections for BCM platform
"""

import os
import logging
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

logger = logging.getLogger(__name__)


class QdrantCollectionSetup:
    """Setup and manage Qdrant collections"""

    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize Qdrant setup

        Args:
            url: Qdrant URL (defaults to QDRANT_URL env var)
            api_key: Qdrant API key (defaults to QDRANT_API_KEY env var)
        """
        self.url = url or os.getenv("QDRANT_URL")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")

        if not self.url or not self.api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set")

        self.client = QdrantClient(url=self.url, api_key=self.api_key)

    def create_bcm_knowledge_collection(self, vector_size: int = 1536):
        """
        Create BCM knowledge collection

        Args:
            vector_size: Size of embedding vectors (1536 for text-embedding-3-large)
        """

        collection_name = "bcm_knowledge"

        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            if any(c.name == collection_name for c in collections):
                logger.info(f"Collection {collection_name} already exists")
                return

            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )

            # Create payload index for filtering
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="source_type",
                field_schema="keyword"
            )

            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="industry",
                field_schema="keyword"
            )

            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="module",
                field_schema="keyword"
            )

            logger.info(f"Created collection: {collection_name}")

        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            raise

    def create_workflow_cases_collection(self, vector_size: int = 1536):
        """
        Create workflow cases collection

        Args:
            vector_size: Size of embedding vectors
        """

        collection_name = "workflow_cases"

        try:
            collections = self.client.get_collections().collections
            if any(c.name == collection_name for c in collections):
                logger.info(f"Collection {collection_name} already exists")
                return

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )

            # Indexes for workflow filtering
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="workflow_type",
                field_schema="keyword"
            )

            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="success",
                field_schema="bool"
            )

            logger.info(f"Created collection: {collection_name}")

        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            raise

    def create_documents_collection(self, vector_size: int = 1536):
        """
        Create documents collection

        Args:
            vector_size: Size of embedding vectors
        """

        collection_name = "documents"

        try:
            collections = self.client.get_collections().collections
            if any(c.name == collection_name for c in collections):
                logger.info(f"Collection {collection_name} already exists")
                return

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )

            # Indexes for document metadata
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="document_type",
                field_schema="keyword"
            )

            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="tenant_id",
                field_schema="keyword"
            )

            logger.info(f"Created collection: {collection_name}")

        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            raise

    def setup_all_collections(self, vector_size: int = 1536):
        """
        Setup all Qdrant collections

        Args:
            vector_size: Size of embedding vectors (1536 for OpenAI text-embedding-3-large)
        """

        logger.info("Setting up Qdrant collections...")

        self.create_bcm_knowledge_collection(vector_size)
        self.create_workflow_cases_collection(vector_size)
        self.create_documents_collection(vector_size)

        logger.info("All collections setup complete!")

    def get_collection_info(self):
        """Get information about all collections"""

        collections = self.client.get_collections().collections

        info = {}
        for collection in collections:
            collection_info = self.client.get_collection(collection.name)
            info[collection.name] = {
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "status": collection_info.status
            }

        return info


def main():
    """Main setup script"""

    logging.basicConfig(level=logging.INFO)

    try:
        setup = QdrantCollectionSetup()
        setup.setup_all_collections()

        # Print collection info
        info = setup.get_collection_info()
        logger.info("Collection status:")
        for name, data in info.items():
            logger.info(f"  {name}: {data['points_count']} points, status={data['status']}")

    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise


if __name__ == "__main__":
    main()
