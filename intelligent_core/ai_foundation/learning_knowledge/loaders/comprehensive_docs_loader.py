#!/usr/bin/env python3
"""
Comprehensive Platform Documentation Loader
Loads 7 key platform documents into Qdrant for RAG integration

Documents:
1. AI_FOUNDATION_CAPABILITIES.md (45 KB)
2. AI_ORCHESTRATION_CAPABILITIES.md (38 KB)
3. DOMAIN_EXPERTISE_CAPABILITIES.md (42 KB)
4. PREDICTIVE_INTELLIGENCE_CAPABILITIES.md (35 KB)
5. INFRASTRUCTURE_ORCHESTRATION_COMPLETE.md (52 KB)
6. BUSINESS_PROCESS_SCENARIOS_COMPLETE.md (78 KB)
7. ALL_USAGE_SCENARIOS_CATALOG.md (112 KB)

Total: ~352 KB, ~1500 chunks expected

Usage:
    python comprehensive_docs_loader.py --mode=full
    python comprehensive_docs_loader.py --mode=test --limit=100
"""

import os
import re
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib
from datetime import datetime

# Try importing dependencies
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("️  sentence-transformers not installed. Install with: pip install sentence-transformers")

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("️  qdrant-client not installed. Install with: pip install qdrant-client")


@dataclass
class DocumentChunk:
    """Represents a chunk of documentation"""
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class ComprehensiveDocsLoader:
    """Loader for comprehensive platform documentation"""

    def __init__(
        self,
        docs_path: str = None,
        qdrant_url: str = "localhost",
        qdrant_port: int = 6333,
        embedding_model: str = "sentence-transformers/all-mpnet-base-v2"
    ):
        """Initialize loader

        Args:
            docs_path: Path to comprehensive-platform-docs folder
            qdrant_url: Qdrant server URL
            qdrant_port: Qdrant server port
            embedding_model: Sentence transformer model name
        """
        # Set default path if not provided
        if docs_path is None:
            current_dir = Path(__file__).parent.parent
            docs_path = current_dir.parent.parent.parent / "doc-project" / "comprehensive-platform-docs"

        self.docs_path = Path(docs_path)
        self.qdrant_url = qdrant_url
        self.qdrant_port = qdrant_port
        self.embedding_model_name = embedding_model

        # Document definitions
        self.documents = {
            "ai_foundation": {
                "file": "AI_FOUNDATION_CAPABILITIES.md",
                "collection": "platform_capabilities",
                "category": "AI Capabilities",
                "priority": "high",
                "keywords": ["LLM", "RAG", "ML", "predictions", "self-learning", "Claude", "OpenAI"]
            },
            "ai_orchestration": {
                "file": "AI_ORCHESTRATION_CAPABILITIES.md",
                "collection": "platform_capabilities",
                "category": "Orchestration",
                "priority": "high",
                "keywords": ["cognitive loop", "memory", "orchestrator", "decision making", "safety"]
            },
            "domain_expertise": {
                "file": "DOMAIN_EXPERTISE_CAPABILITIES.md",
                "collection": "platform_capabilities",
                "category": "Domain Expertise",
                "priority": "high",
                "keywords": ["specialists", "collective intelligence", "k-anonymity", "case library", "stuck detection"]
            },
            "predictive": {
                "file": "PREDICTIVE_INTELLIGENCE_CAPABILITIES.md",
                "collection": "platform_capabilities",
                "category": "Predictive Analytics",
                "priority": "high",
                "keywords": ["predictions", "forecasting", "timeline", "certification", "event intelligence"]
            },
            "infrastructure": {
                "file": "INFRASTRUCTURE_ORCHESTRATION_COMPLETE.md",
                "collection": "platform_patterns",
                "category": "Infrastructure Patterns",
                "priority": "high",
                "keywords": ["event bus", "saga", "circuit breaker", "deployment", "scaling", "patterns"]
            },
            "scenarios": {
                "file": "BUSINESS_PROCESS_SCENARIOS_COMPLETE.md",
                "collection": "platform_scenarios",
                "category": "Business Scenarios",
                "priority": "maximum",
                "keywords": ["ISO certification", "incident response", "BIA", "exercise", "examples", "end-to-end"]
            },
            "usage_scenarios": {
                "file": "ALL_USAGE_SCENARIOS_CATALOG.md",
                "collection": "platform_scenarios",
                "category": "Usage Scenarios",
                "priority": "maximum",
                "keywords": ["scenarios", "use cases", "how to", "examples", "all scenarios", "570 scenarios"]
            }
        }

        # Chunking parameters
        self.chunk_size = 1000  # tokens (approximate)
        self.chunk_overlap = 200  # tokens

        # Initialize components
        self.embedding_model = None
        self.qdrant_client = None

        print(f" Documents path: {self.docs_path}")
        print(f" Qdrant: {qdrant_url}:{qdrant_port}")
        print(f" Embedding model: {embedding_model}")

    def _init_embedding_model(self):
        """Initialize sentence transformer model"""
        if not EMBEDDINGS_AVAILABLE:
            raise RuntimeError("sentence-transformers not installed")

        if self.embedding_model is None:
            print(f"⏳ Loading embedding model: {self.embedding_model_name}...")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            print(f" Embedding model loaded (dimension: {self.embedding_model.get_sentence_embedding_dimension()})")

    def _init_qdrant_client(self):
        """Initialize Qdrant client"""
        if not QDRANT_AVAILABLE:
            raise RuntimeError("qdrant-client not installed")

        if self.qdrant_client is None:
            print(f"⏳ Connecting to Qdrant at {self.qdrant_url}:{self.qdrant_port}...")
            self.qdrant_client = QdrantClient(host=self.qdrant_url, port=self.qdrant_port)
            print(" Connected to Qdrant")

    def _create_collections(self):
        """Create Qdrant collections if they don't exist"""
        collections = {
            "platform_capabilities": "AI capabilities, orchestration, specialists, predictive analytics",
            "platform_patterns": "Infrastructure patterns (event bus, deployment, scaling)",
            "platform_scenarios": "Business scenarios and usage examples (570+ scenarios)"
        }

        embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        for collection_name, description in collections.items():
            # Check if collection exists
            try:
                self.qdrant_client.get_collection(collection_name)
                print(f" Collection '{collection_name}' already exists")
            except Exception:
                # Create collection
                print(f"⏳ Creating collection '{collection_name}' ({description})...")
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                print(f" Collection '{collection_name}' created")

    def _chunk_document(self, content: str, doc_info: Dict[str, Any]) -> List[DocumentChunk]:
        """Chunk document by logical sections

        Args:
            content: Document markdown content
            doc_info: Document metadata

        Returns:
            List of DocumentChunk objects
        """
        chunks = []

        # Split by major headers (##)
        sections = re.split(r'\n## ', content)

        for i, section in enumerate(sections):
            if not section.strip():
                continue

            # Extract section title
            lines = section.split('\n')
            section_title = lines[0].strip('#').strip() if lines else "Unknown"
            section_content = '\n'.join(lines[1:]) if len(lines) > 1 else section

            # Further split by subsections (###) if section is too large
            if len(section_content) > self.chunk_size * 4:  # ~4000 chars
                subsections = re.split(r'\n### ', section_content)

                for j, subsection in enumerate(subsections):
                    if not subsection.strip():
                        continue

                    subsection_lines = subsection.split('\n')
                    subsection_title = subsection_lines[0].strip('#').strip() if subsection_lines else "Unknown"
                    subsection_content = '\n'.join(subsection_lines[1:]) if len(subsection_lines) > 1 else subsection

                    # Create chunk
                    chunk_id = self._generate_chunk_id(
                        doc_info["file"],
                        section_title,
                        subsection_title
                    )

                    chunk = DocumentChunk(
                        id=chunk_id,
                        text=f"# {section_title}\n## {subsection_title}\n\n{subsection_content}",
                        metadata={
                            "source_document": doc_info["file"],
                            "section": section_title,
                            "subsection": subsection_title,
                            "category": doc_info["category"],
                            "collection": doc_info["collection"],
                            "priority": doc_info["priority"],
                            "keywords": doc_info["keywords"],
                            "chunk_index": len(chunks),
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    chunks.append(chunk)
            else:
                # Create single chunk for section
                chunk_id = self._generate_chunk_id(doc_info["file"], section_title)

                chunk = DocumentChunk(
                    id=chunk_id,
                    text=f"# {section_title}\n\n{section_content}",
                    metadata={
                        "source_document": doc_info["file"],
                        "section": section_title,
                        "subsection": None,
                        "category": doc_info["category"],
                        "collection": doc_info["collection"],
                        "priority": doc_info["priority"],
                        "keywords": doc_info["keywords"],
                        "chunk_index": len(chunks),
                        "timestamp": datetime.now().isoformat()
                    }
                )
                chunks.append(chunk)

        return chunks

    def _generate_chunk_id(self, filename: str, section: str, subsection: str = None) -> str:
        """Generate unique chunk ID"""
        parts = [filename, section]
        if subsection:
            parts.append(subsection)

        id_string = "::".join(parts)
        return hashlib.md5(id_string.encode()).hexdigest()

    def _create_embeddings(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Create embeddings for chunks

        Args:
            chunks: List of DocumentChunk objects

        Returns:
            Chunks with embeddings added
        """
        print(f"⏳ Creating embeddings for {len(chunks)} chunks...")

        # Extract texts
        texts = [chunk.text for chunk in chunks]

        # Create embeddings in batch
        embeddings = self.embedding_model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding.tolist()

        print(f" Embeddings created ({len(chunks)} chunks)")
        return chunks

    def _index_chunks(self, chunks: List[DocumentChunk]) -> int:
        """Index chunks into Qdrant

        Args:
            chunks: List of DocumentChunk objects with embeddings

        Returns:
            Number of indexed chunks
        """
        # Group chunks by collection
        chunks_by_collection = {}
        for chunk in chunks:
            collection = chunk.metadata["collection"]
            if collection not in chunks_by_collection:
                chunks_by_collection[collection] = []
            chunks_by_collection[collection].append(chunk)

        total_indexed = 0

        for collection_name, collection_chunks in chunks_by_collection.items():
            print(f"⏳ Indexing {len(collection_chunks)} chunks into '{collection_name}'...")

            # Create points
            points = [
                PointStruct(
                    id=chunk.id,
                    vector=chunk.embedding,
                    payload=chunk.metadata
                )
                for chunk in collection_chunks
            ]

            # Upsert to Qdrant (batch)
            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=points
            )

            total_indexed += len(collection_chunks)
            print(f" Indexed {len(collection_chunks)} chunks into '{collection_name}'")

        return total_indexed

    async def load_all_documents(self, mode: str = "full", limit: Optional[int] = None) -> Dict[str, Any]:
        """Load all documents into Qdrant

        Args:
            mode: "full" or "test"
            limit: Limit number of chunks (for testing)

        Returns:
            Statistics dictionary
        """
        print("=" * 60)
        print(" Comprehensive Platform Documentation Loader")
        print("=" * 60)

        # Initialize components
        self._init_embedding_model()
        self._init_qdrant_client()
        self._create_collections()

        all_chunks = []
        stats = {
            "documents_processed": 0,
            "total_chunks": 0,
            "chunks_by_collection": {},
            "start_time": datetime.now().isoformat()
        }

        # Process each document
        for doc_key, doc_info in self.documents.items():
            doc_path = self.docs_path / doc_info["file"]

            if not doc_path.exists():
                print(f"️  Document not found: {doc_path}")
                continue

            print(f"\n Processing: {doc_info['file']}...")

            # Read document
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Chunk document
            chunks = self._chunk_document(content, doc_info)
            print(f"    Created {len(chunks)} chunks")

            all_chunks.extend(chunks)
            stats["documents_processed"] += 1

            # Update stats
            collection = doc_info["collection"]
            if collection not in stats["chunks_by_collection"]:
                stats["chunks_by_collection"][collection] = 0
            stats["chunks_by_collection"][collection] += len(chunks)

        # Apply limit if in test mode
        if mode == "test" and limit:
            print(f"\n️  TEST MODE: Limiting to {limit} chunks")
            all_chunks = all_chunks[:limit]

        stats["total_chunks"] = len(all_chunks)

        # Create embeddings
        all_chunks = self._create_embeddings(all_chunks)

        # Index into Qdrant
        indexed_count = self._index_chunks(all_chunks)
        stats["indexed_chunks"] = indexed_count
        stats["end_time"] = datetime.now().isoformat()

        # Print summary
        print("\n" + "=" * 60)
        print(" LOADING COMPLETE")
        print("=" * 60)
        print(f" Statistics:")
        print(f"   Documents processed: {stats['documents_processed']}")
        print(f"   Total chunks: {stats['total_chunks']}")
        print(f"   Indexed chunks: {stats['indexed_chunks']}")
        print(f"\n Chunks by collection:")
        for collection, count in stats["chunks_by_collection"].items():
            print(f"   {collection}: {count} chunks")
        print("=" * 60)

        return stats

    async def test_search(self, query: str, collection: str = "platform_scenarios", limit: int = 5):
        """Test search functionality

        Args:
            query: Search query
            collection: Collection name
            limit: Number of results
        """
        print(f"\n Testing search: '{query}'")
        print(f"   Collection: {collection}")

        # Create query embedding
        query_embedding = self.embedding_model.encode(query).tolist()

        # Search Qdrant
        results = self.qdrant_client.search(
            collection_name=collection,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True
        )

        print(f"\n Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n   {i}. Score: {result.score:.3f}")
            print(f"      Document: {result.payload['source_document']}")
            print(f"      Section: {result.payload['section']}")
            if result.payload.get('subsection'):
                print(f"      Subsection: {result.payload['subsection']}")
            print(f"      Category: {result.payload['category']}")


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Load comprehensive platform documentation into Qdrant")
    parser.add_argument("--mode", choices=["full", "test"], default="full", help="Loading mode")
    parser.add_argument("--limit", type=int, help="Limit number of chunks (test mode)")
    parser.add_argument("--docs-path", help="Path to comprehensive-platform-docs folder")
    parser.add_argument("--qdrant-url", default="localhost", help="Qdrant server URL")
    parser.add_argument("--qdrant-port", type=int, default=6333, help="Qdrant server port")
    parser.add_argument("--test-query", help="Test search query after loading")

    args = parser.parse_args()

    # Create loader
    loader = ComprehensiveDocsLoader(
        docs_path=args.docs_path,
        qdrant_url=args.qdrant_url,
        qdrant_port=args.qdrant_port
    )

    # Load documents
    stats = await loader.load_all_documents(mode=args.mode, limit=args.limit)

    # Test search if requested
    if args.test_query:
        await loader.test_search(args.test_query)


if __name__ == "__main__":
    asyncio.run(main())
