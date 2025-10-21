#!/usr/bin/env python3
"""
Load test data into Qdrant collections
Populates bcm_knowledge, workflow_cases, and ai_memory with sample vectors
"""

import os
import sys
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
import logging
import random

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Qdrant connection
QDRANT_URL = os.getenv(
    'QDRANT_URL',
    'https://fa9f6acd-aef9-4ebe-a3f5-f89c62bce378.eu-west-1-0.aws.cloud.qdrant.io:6333'
)
QDRANT_API_KEY = os.getenv(
    'QDRANT_API_KEY',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwiZXhwIjoxNzYwNjU1NDMyfQ.efuzaW9KZeAZbujOWbX33wzgtCGblTANCIgJXyNcjfw'
)

# Sample BCM knowledge data
BCM_KNOWLEDGE_SAMPLES = [
    {
        "id": 1,
        "text": "ISO 22301:2019 Clause 4.1 - Understanding the organization and its context",
        "category": "iso_standard",
        "clause": "4.1"
    },
    {
        "id": 2,
        "text": "Business Impact Analysis (BIA) identifies critical business functions and their recovery priorities",
        "category": "bcm_practice",
        "clause": "8.2.2"
    },
    {
        "id": 3,
        "text": "Recovery Time Objective (RTO) is the maximum acceptable time to restore a business function",
        "category": "bcm_concept",
        "clause": "8.2.2"
    },
    {
        "id": 4,
        "text": "ISO 22301 Clause 5.3 - Organizational roles, responsibilities and authorities for BCMS",
        "category": "iso_standard",
        "clause": "5.3"
    },
    {
        "id": 5,
        "text": "Business Continuity Plan (BCP) documents procedures for maintaining operations during disruptions",
        "category": "bcm_practice",
        "clause": "8.4"
    },
    {
        "id": 6,
        "text": "Testing and exercising BCM plans validates their effectiveness and identifies improvements",
        "category": "bcm_practice",
        "clause": "8.5"
    },
    {
        "id": 7,
        "text": "ISO 22301 Clause 7.2 - Competence requirements for BCM personnel",
        "category": "iso_standard",
        "clause": "7.2"
    },
    {
        "id": 8,
        "text": "Communication strategy ensures stakeholders receive timely information during incidents",
        "category": "bcm_practice",
        "clause": "7.4"
    },
    {
        "id": 9,
        "text": "Risk Assessment identifies threats and vulnerabilities that could disrupt operations",
        "category": "bcm_practice",
        "clause": "8.2.3"
    },
    {
        "id": 10,
        "text": "ISO 22301 Clause 9.1 - Monitoring, measurement, analysis and evaluation of BCMS",
        "category": "iso_standard",
        "clause": "9.1"
    }
]

# Sample workflow cases
WORKFLOW_CASES = [
    {
        "id": 1,
        "text": "Case Study: Financial institution recovered critical trading systems in 2 hours using hot site",
        "industry": "finance",
        "scenario": "technology_failure"
    },
    {
        "id": 2,
        "text": "Healthcare provider maintained patient care during ransomware attack using offline procedures",
        "industry": "healthcare",
        "scenario": "cyber_attack"
    },
    {
        "id": 3,
        "text": "Manufacturing company activated BCP during supply chain disruption caused by natural disaster",
        "industry": "manufacturing",
        "scenario": "supply_chain"
    },
    {
        "id": 4,
        "text": "Retail chain successfully relocated operations to backup facility during building evacuation",
        "industry": "retail",
        "scenario": "facilities"
    },
    {
        "id": 5,
        "text": "Telecommunications provider maintained 99.9% uptime during pandemic using remote workforce",
        "industry": "telecom",
        "scenario": "pandemic"
    }
]

# Sample AI memory (conversation history, learnings)
AI_MEMORY_SAMPLES = [
    {
        "id": 1,
        "text": "User preference: Prefers detailed technical explanations with ISO clause references",
        "memory_type": "user_preference",
        "domain": "bcm"
    },
    {
        "id": 2,
        "text": "Learned pattern: Organizations in finance sector prioritize RTO < 4 hours for trading systems",
        "memory_type": "pattern",
        "domain": "bia"
    },
    {
        "id": 3,
        "text": "Context: Organization has 500 employees, operates in healthcare, ISO 27001 certified",
        "memory_type": "context",
        "domain": "organization"
    },
    {
        "id": 4,
        "text": "Previous recommendation: Implement tabletop exercise before full-scale simulation",
        "memory_type": "recommendation",
        "domain": "validation"
    },
    {
        "id": 5,
        "text": "Successful resolution: User resolved BCP documentation gaps using Living Docs templates",
        "memory_type": "resolution",
        "domain": "documents"
    }
]


def generate_embedding(text: str, dimension: int = 384) -> list:
    """
    Generate dummy embedding vector for testing
    In production, this would use actual embedding model (e.g., sentence-transformers)
    """
    # Use text hash to generate deterministic random vector
    random.seed(hash(text))
    return [random.uniform(-1, 1) for _ in range(dimension)]


def recreate_collections(client: QdrantClient):
    """Recreate all collections with proper configuration"""

    collections_config = {
        "bcm_knowledge": {
            "vector_size": 384,  # sentence-transformers/all-MiniLM-L6-v2 dimension
            "distance": Distance.COSINE,
            "description": "BCM domain knowledge, ISO standards, best practices"
        },
        "workflow_cases": {
            "vector_size": 384,
            "distance": Distance.COSINE,
            "description": "Historical BCM cases and workflow examples"
        },
        "ai_memory": {
            "vector_size": 384,
            "distance": Distance.COSINE,
            "description": "AI agent memory and learned patterns"
        }
    }

    for collection_name, config in collections_config.items():
        try:
            # Check if collection exists
            existing = client.get_collections()
            exists = any(c.name == collection_name for c in existing.collections)

            if exists:
                logger.info(f" Collection '{collection_name}' already exists, recreating...")
                client.delete_collection(collection_name)

            # Create collection
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=config["vector_size"],
                    distance=config["distance"]
                )
            )
            logger.info(f" Created collection: {collection_name}")

        except Exception as e:
            logger.error(f" Failed to create {collection_name}: {e}")
            raise


def load_bcm_knowledge(client: QdrantClient):
    """Load BCM knowledge vectors"""
    logger.info(" Loading BCM knowledge data...")

    points = []
    for sample in BCM_KNOWLEDGE_SAMPLES:
        vector = generate_embedding(sample["text"])
        point = PointStruct(
            id=sample["id"],
            vector=vector,
            payload={
                "text": sample["text"],
                "category": sample["category"],
                "iso_clause": sample["clause"],
                "source": "test_data"
            }
        )
        points.append(point)

    client.upsert(
        collection_name="bcm_knowledge",
        points=points
    )
    logger.info(f" Loaded {len(points)} BCM knowledge vectors")


def load_workflow_cases(client: QdrantClient):
    """Load workflow case vectors"""
    logger.info(" Loading workflow cases data...")

    points = []
    for sample in WORKFLOW_CASES:
        vector = generate_embedding(sample["text"])
        point = PointStruct(
            id=sample["id"],
            vector=vector,
            payload={
                "text": sample["text"],
                "industry": sample["industry"],
                "scenario": sample["scenario"],
                "source": "test_data"
            }
        )
        points.append(point)

    client.upsert(
        collection_name="workflow_cases",
        points=points
    )
    logger.info(f" Loaded {len(points)} workflow case vectors")


def load_ai_memory(client: QdrantClient):
    """Load AI memory vectors"""
    logger.info(" Loading AI memory data...")

    points = []
    for sample in AI_MEMORY_SAMPLES:
        vector = generate_embedding(sample["text"])
        point = PointStruct(
            id=sample["id"],
            vector=vector,
            payload={
                "text": sample["text"],
                "memory_type": sample["memory_type"],
                "domain": sample["domain"],
                "source": "test_data"
            }
        )
        points.append(point)

    client.upsert(
        collection_name="ai_memory",
        points=points
    )
    logger.info(f" Loaded {len(points)} AI memory vectors")


def verify_data(client: QdrantClient):
    """Verify loaded data"""
    logger.info("\n Verification:")

    collections = client.get_collections()
    for collection in collections.collections:
        info = client.get_collection(collection.name)
        logger.info(f"  - {collection.name}: {info.points_count} vectors")

        # Test search
        if info.points_count > 0:
            # Get first point to use as query
            first_point = client.scroll(
                collection_name=collection.name,
                limit=1
            )[0][0]

            # Search similar vectors
            results = client.search(
                collection_name=collection.name,
                query_vector=first_point.vector,
                limit=3
            )
            logger.info(f"    Search test: Found {len(results)} similar vectors")


def main():
    """Main execution"""
    logger.info(" Starting Qdrant test data loader")

    try:
        # Connect to Qdrant
        logger.info(f" Connecting to Qdrant: {QDRANT_URL}")
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            timeout=30
        )
        logger.info(" Connected to Qdrant")

        # Recreate collections
        recreate_collections(client)

        # Load data
        load_bcm_knowledge(client)
        load_workflow_cases(client)
        load_ai_memory(client)

        # Verify
        verify_data(client)

        logger.info("\n Test data loaded successfully!")
        return 0

    except Exception as e:
        logger.error(f" Failed to load test data: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
