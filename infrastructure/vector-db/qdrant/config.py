"""
Qdrant Vector Database Configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional


class QdrantConfig(BaseSettings):
    """Qdrant connection and collection configuration"""

    # Connection (Qdrant Cloud)
    url: str = "https://fa9f6acd-aef9-4ebe-a3f5-f89c62bce378.eu-west-1-0.aws.cloud.qdrant.io"
    api_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.XalkCWKEVbNd9P5Bj3f7Y4pPEySIZD3RyCc8EAG5EIE"

    # Legacy local config (for backward compatibility)
    host: str = "localhost"
    port: int = 6333
    grpc_port: int = 6334
    https: bool = True
    timeout: float = 30.0

    # Collections
    knowledge_collection: str = "knowledge_base"
    cases_collection: str = "workflow_cases"
    memory_collection: str = "ai_memory"

    # Embedding configuration
    embedding_dimension: int = 1536  # OpenAI ada-002
    distance_metric: str = "Cosine"  # Cosine, Euclid, Dot

    # Search configuration
    default_limit: int = 10
    max_limit: int = 100
    min_score: float = 0.7  # Minimum similarity score

    # Performance
    batch_size: int = 100
    parallel_requests: int = 4
    prefetch_limit: int = 1000

    # Indexing
    hnsw_ef_construct: int = 128  # HNSW index building parameter
    hnsw_m: int = 16  # HNSW index building parameter

    class Config:
        env_prefix = "QDRANT_"
        env_file = ".env"
        case_sensitive = False


# Global config instance
qdrant_config = QdrantConfig()


# Collection configurations
COLLECTIONS_CONFIG = {
    "knowledge_base": {
        "description": "RAG knowledge base - documents, standards, best practices",
        "vector_size": qdrant_config.embedding_dimension,
        "distance": qdrant_config.distance_metric,
        "hnsw_config": {
            "m": qdrant_config.hnsw_m,
            "ef_construct": qdrant_config.hnsw_ef_construct,
        },
        "payload_schema": {
            "text": {"type": "text", "index": True},
            "source": {"type": "keyword"},
            "category": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "created_at": {"type": "datetime"},
        }
    },
    "workflow_cases": {
        "description": "Case Library - successful workflow cases",
        "vector_size": qdrant_config.embedding_dimension,
        "distance": qdrant_config.distance_metric,
        "hnsw_config": {
            "m": qdrant_config.hnsw_m,
            "ef_construct": qdrant_config.hnsw_ef_construct,
        },
        "payload_schema": {
            "case_id": {"type": "keyword"},
            "module": {"type": "keyword"},
            "industry": {"type": "keyword"},
            "org_size": {"type": "keyword"},
            "maturity_level": {"type": "keyword"},
            "success_patterns": {"type": "text"},
            "lessons_learned": {"type": "text"},
            "created_at": {"type": "datetime"},
        }
    },
    "ai_memory": {
        "description": "Long-term memory for AI agents",
        "vector_size": qdrant_config.embedding_dimension,
        "distance": qdrant_config.distance_metric,
        "hnsw_config": {
            "m": qdrant_config.hnsw_m,
            "ef_construct": qdrant_config.hnsw_ef_construct,
        },
        "payload_schema": {
            "agent_id": {"type": "keyword"},
            "conversation_id": {"type": "keyword"},
            "context": {"type": "text"},
            "timestamp": {"type": "datetime"},
        }
    }
}
