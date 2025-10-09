#!/usr/bin/env python3
"""
Simple script to load comprehensive platform documentation into Qdrant

Usage:
    # Full load (all 7 documents, ~1500 chunks, 5-10 minutes)
    python load_comprehensive_docs.py

    # Test load (first 100 chunks, ~1 minute)
    python load_comprehensive_docs.py --test

    # Test search after loading
    python load_comprehensive_docs.py --test-query "How do I start a BIA?"
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loaders.comprehensive_docs_loader import ComprehensiveDocsLoader


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Load comprehensive platform docs")
    parser.add_argument("--test", action="store_true", help="Test mode (load only 100 chunks)")
    parser.add_argument("--test-query", help="Test search query after loading")
    args = parser.parse_args()

    # Create loader
    print("🚀 Starting comprehensive documentation loader...")
    loader = ComprehensiveDocsLoader()

    # Load documents
    mode = "test" if args.test else "full"
    limit = 100 if args.test else None

    stats = await loader.load_all_documents(mode=mode, limit=limit)

    # Test search if requested
    if args.test_query:
        print("\n" + "=" * 60)
        await loader.test_search(args.test_query)
        print("=" * 60)

    print("\n✅ Done! Documentation loaded into Qdrant.")
    print("\n💡 You can now query using RAG pipeline:")
    print("   - Collection: platform_capabilities (AI, orchestration, specialists)")
    print("   - Collection: platform_patterns (infrastructure patterns)")
    print("   - Collection: platform_scenarios (570+ usage scenarios)")

    print("\n💡 Test queries:")
    print('   python load_comprehensive_docs.py --test-query "How do I start a BIA?"')
    print('   python load_comprehensive_docs.py --test-query "What can AI do?"')
    print('   python load_comprehensive_docs.py --test-query "Show me incident response flow"')


if __name__ == "__main__":
    asyncio.run(main())
