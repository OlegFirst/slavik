#!/usr/bin/env python3
"""
Load Business Flows into Qdrant

Simple script to load 320+ BCM business flows into vector database for RAG.

Usage:
    python load_business_flows.py

Requirements:
    - Qdrant running (docker-compose up qdrant)
    - QDRANT_URL and QDRANT_API_KEY in environment

What it does:
    1. Loads flows from business_flows/ directory
    2. Parses WHO, ISO, NIST, Case Library documents
    3. Extracts individual flows with metadata
    4. Creates embeddings (OpenAI, local, or TF-IDF fallback)
    5. Indexes into Qdrant collection: bcm_business_flows

After loading:
    - Query flows with RAGPipeline
    - Semantic search across 320+ flows
    - Context-aware BCM guidance
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add intelligent-core to path
intelligent_core_path = Path(__file__).parents[4]
sys.path.insert(0, str(intelligent_core_path))

from intelligent_core.ai_foundation.learning_knowledge.knowledge.loader.business_flows_loader import BusinessFlowsLoader
from intelligent_core.ai_foundation.learning_knowledge.knowledge.indexer.vector_indexer import VectorIndexer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function"""

    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  BCM Business Flows Loader                               ║
    ║  Loading 320+ flows into Qdrant for RAG                  ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # Check Qdrant connection
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    logger.info(f"🔗 Connecting to Qdrant: {qdrant_url}")

    if not qdrant_api_key:
        logger.warning("⚠️  QDRANT_API_KEY not set - using local Qdrant without auth")

    # Initialize loader
    logger.info("📚 Initializing Business Flows Loader...")
    loader = BusinessFlowsLoader()

    # Check if knowledge files exist
    knowledge_path = loader.knowledge_path
    if not knowledge_path.exists():
        logger.error(f"❌ Knowledge path not found: {knowledge_path}")
        logger.error("Make sure business flows are in:")
        logger.error("  intelligent-core/ai-foundation/learning-knowledge/knowledge/business_flows/")
        sys.exit(1)

    logger.info(f"✅ Knowledge path found: {knowledge_path}")

    # List available sources
    available_sources = []
    for source_id, source_config in loader.sources.items():
        file_path = knowledge_path / source_config["file"]
        if file_path.exists():
            file_size = file_path.stat().st_size / 1024  # KB
            available_sources.append(f"{source_config['file']} ({file_size:.1f} KB)")
            logger.info(f"  ✅ {source_config['file']} ({file_size:.1f} KB)")
        else:
            logger.warning(f"  ⚠️  {source_config['file']} - NOT FOUND")

    if not available_sources:
        logger.error("❌ No source files found!")
        sys.exit(1)

    # Load all flows
    logger.info("\n📖 Loading flows from all sources...")
    flows = await loader.load_all_flows()

    if not flows:
        logger.error("❌ No flows loaded!")
        sys.exit(1)

    logger.info(f"✅ Loaded {len(flows)} total flow documents")

    # Show breakdown by source
    source_counts = {}
    for flow in flows:
        source = flow.get("source", "unknown")
        source_counts[source] = source_counts.get(source, 0) + 1

    logger.info("\n📊 Flows by source:")
    for source, count in sorted(source_counts.items()):
        logger.info(f"  {source}: {count} flows")

    # Initialize vector indexer
    logger.info("\n🔍 Initializing Vector Indexer...")

    try:
        indexer = VectorIndexer(
            collection_name="bcm_business_flows",
            embedding_provider="auto",  # Will try OpenAI, then local, then TF-IDF
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key
        )

        logger.info(f"✅ Using {indexer.embedding_provider.provider} embeddings")
        logger.info(f"✅ Embedding dimension: {indexer.embedding_provider.embedding_dim}")

    except Exception as e:
        logger.error(f"❌ Failed to initialize indexer: {e}")
        logger.error("Make sure Qdrant is running: docker-compose up qdrant")
        sys.exit(1)

    # Create collection
    logger.info("\n📦 Creating Qdrant collection...")
    try:
        await indexer.create_collection_if_not_exists()
        logger.info("✅ Collection ready: bcm_business_flows")
    except Exception as e:
        logger.error(f"❌ Failed to create collection: {e}")
        sys.exit(1)

    # Index flows
    logger.info("\n💾 Indexing flows into Qdrant...")
    logger.info("This may take a few minutes depending on embedding provider...")

    try:
        indexed_count = await loader.index_flows(flows, indexer)
        logger.info(f"✅ Successfully indexed {indexed_count}/{len(flows)} flows")

    except Exception as e:
        logger.error(f"❌ Indexing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Show summary
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║  ✅ Business Flows Loading Complete!                     ║
    ╠══════════════════════════════════════════════════════════╣
    ║  Flows Loaded:     {len(flows):>4}                                   ║
    ║  Flows Indexed:    {indexed_count:>4}                                   ║
    ║  Collection:       bcm_business_flows                    ║
    ║  Embedding:        {indexer.embedding_provider.provider:<15}                 ║
    ╚══════════════════════════════════════════════════════════╝

    🚀 Now you can query flows with RAG:

    from intelligent_core.ai_foundation.rag.pipeline import RAGPipeline

    rag = RAGPipeline()
    results = rag.query("How to conduct BIA in healthcare?")

    Or test the search:

    from intelligent_core.ai_foundation.learning_knowledge.knowledge.indexer.vector_indexer import VectorIndexer

    indexer = VectorIndexer(collection_name="bcm_business_flows")
    results = await indexer.search("healthcare BIA", top_k=5)

    ✅ Ready for production use!
    """)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Loading interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
