"""
Initialize Qdrant Collections

Creates all required collections for BCM platform:
- knowledge_base: RAG knowledge (standards, best practices)
- workflow_cases: Case Library (successful workflow cases)
- ai_memory: Long-term memory for AI agents
"""

import asyncio
import logging
from client import QdrantVectorDB
from config import COLLECTIONS_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_collections():
    """Initialize all Qdrant collections"""

    logger.info(" Starting Qdrant collections initialization...")

    # Initialize client
    client = QdrantVectorDB()

    # Check health
    if not client.health_check():
        logger.error(" Qdrant is not healthy!")
        return False

    logger.info(" Qdrant is healthy")

    # Create each collection
    for collection_name, config in COLLECTIONS_CONFIG.items():
        logger.info(f"\n Creating collection: {collection_name}")
        logger.info(f"   Description: {config['description']}")

        try:
            created = await client.create_collection(
                collection_name=collection_name,
                recreate=False  # Don't recreate if exists
            )

            if created:
                logger.info(f"    Created: {collection_name}")

                # Get collection info
                info = client.get_collection_info(collection_name)
                logger.info(f"    Vector size: {info['config']['vector_size']}")
                logger.info(f"    Distance: {info['config']['distance']}")
                logger.info(f"    Status: {info['status']}")
            else:
                logger.info(f"   ℹ️  Already exists: {collection_name}")

        except Exception as e:
            logger.error(f"    Error creating {collection_name}: {e}")
            return False

    logger.info("\n All collections initialized successfully!")

    # Print summary
    logger.info("\n Collections Summary:")
    for collection_name in COLLECTIONS_CONFIG.keys():
        info = client.get_collection_info(collection_name)
        logger.info(f"   • {collection_name}: {info['points_count']} points")

    return True


async def delete_all_collections():
    """Delete all collections (use with caution!)"""

    logger.warning("️  DELETING ALL COLLECTIONS...")

    client = QdrantVectorDB()

    for collection_name in COLLECTIONS_CONFIG.keys():
        try:
            client.client.delete_collection(collection_name=collection_name)
            logger.info(f"   ️  Deleted: {collection_name}")
        except Exception as e:
            logger.warning(f"   ️  Could not delete {collection_name}: {e}")


async def reset_collections():
    """Reset all collections (delete and recreate)"""

    logger.warning("️  RESETTING ALL COLLECTIONS...")

    await delete_all_collections()
    await init_collections()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "reset":
            asyncio.run(reset_collections())
        elif command == "delete":
            asyncio.run(delete_all_collections())
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Usage: python init_collections.py [init|reset|delete]")
    else:
        # Default: init
        asyncio.run(init_collections())
