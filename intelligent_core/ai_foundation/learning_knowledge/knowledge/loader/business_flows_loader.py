"""
Business Flows Loader - Load 320+ BCM business flows into Qdrant

Loads all business flows from:
- WHO Healthcare BCM
- ISO Implementation Guides
- NIST IT Contingency
- Case Library Patterns
- Platform Services
- Best Practices

Into Qdrant collections for RAG/semantic search.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import re
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


class BusinessFlowsLoader:
    """
    Load BCM business flows into vector database

    Features:
    - Parses markdown flow documents
    - Extracts individual flows with metadata
    - Chunks long flows for optimal retrieval
    - Indexes into Qdrant for semantic search
    """

    def __init__(
        self,
        knowledge_path: Optional[Path] = None,
        collection_name: str = "bcm_business_flows"
    ):
        """
        Initialize Business Flows Loader

        Args:
            knowledge_path: Path to business_flows directory
            collection_name: Qdrant collection name
        """
        if knowledge_path is None:
            # Default: intelligent-core/ai-foundation/learning-knowledge/knowledge/business_flows/
            knowledge_path = Path(__file__).parent.parent / "business_flows"

        self.knowledge_path = Path(knowledge_path)
        self.collection_name = collection_name

        # Source documents
        self.sources = {
            "who_healthcare": {
                "file": "WHO_HEALTHCARE_BCM_FLOWS.md",
                "priority": 0.95,
                "domain": "healthcare",
                "type": "domain_specific"
            },
            "iso_implementation": {
                "file": "ISO_IMPLEMENTATION_FLOWS.md",
                "priority": 1.0,
                "domain": "general",
                "type": "implementation_guide"
            },
            "nist_contingency": {
                "file": "NIST_CONTINGENCY_PLANNING_FLOWS.md",
                "priority": 0.9,
                "domain": "it_tech",
                "type": "technical_standard"
            },
            "case_library": {
                "file": "CASE_LIBRARY_PRACTICAL_FLOWS.md",
                "priority": 0.85,
                "domain": "general",
                "type": "practical_patterns"
            }
        }

    async def load_all_flows(self) -> List[Dict[str, Any]]:
        """
        Load all business flows from all sources

        Returns:
            List of flow documents with metadata
        """
        all_flows = []

        for source_id, source_config in self.sources.items():
            file_path = self.knowledge_path / source_config["file"]

            if not file_path.exists():
                logger.warning(f"️ Source not found: {file_path}")
                continue

            logger.info(f" Loading flows from: {source_config['file']}")

            flows = await self._parse_flow_document(
                file_path=file_path,
                source_id=source_id,
                source_config=source_config
            )

            all_flows.extend(flows)
            logger.info(f" Loaded {len(flows)} flows from {source_id}")

        logger.info(f" Total flows loaded: {len(all_flows)}")
        return all_flows

    async def _parse_flow_document(
        self,
        file_path: Path,
        source_id: str,
        source_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Parse markdown document to extract individual flows

        Args:
            file_path: Path to markdown file
            source_id: Source identifier
            source_config: Source configuration

        Returns:
            List of flow documents
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        flows = []

        # Parse by ### Flow headers
        flow_pattern = r'###\s+Flow\s+(\d+):\s+(.+?)\n(.*?)(?=###\s+Flow\s+\d+:|###\s+[A-Z]|$)'
        matches = re.finditer(flow_pattern, content, re.DOTALL)

        for match in matches:
            flow_number = match.group(1)
            flow_name = match.group(2).strip()
            flow_content = match.group(3).strip()

            # Extract metadata from content
            metadata = self._extract_flow_metadata(flow_content)

            # Create flow document
            flow_doc = {
                "flow_id": f"{source_id}_flow_{flow_number}",
                "flow_name": flow_name,
                "flow_number": int(flow_number),
                "content": flow_content,
                "source": source_id,
                "source_file": source_config["file"],
                "priority": source_config["priority"],
                "domain": source_config["domain"],
                "type": source_config["type"],
                "iso_clause": metadata.get("iso_clause"),
                "complexity": metadata.get("complexity", "medium"),
                "estimated_duration": metadata.get("duration"),
                "tags": metadata.get("tags", []),
                "loaded_at": datetime.utcnow().isoformat()
            }

            # Chunk if too long (>2000 tokens ~8000 chars)
            if len(flow_content) > 8000:
                chunks = self._chunk_flow(flow_content, flow_doc)
                flows.extend(chunks)
            else:
                flows.append(flow_doc)

        # Also parse major sections (for documents without numbered flows)
        if len(flows) == 0:
            section_flows = self._parse_by_sections(content, source_id, source_config)
            flows.extend(section_flows)

        return flows

    def _extract_flow_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from flow content

        Args:
            content: Flow content text

        Returns:
            Metadata dictionary
        """
        metadata = {}

        # Extract ISO clause (pattern: 8.2.2, 9.3, etc.)
        iso_match = re.search(r'ISO\s+\d+:\s*(\d+\.\d+\.\d+|\d+\.\d+)', content, re.IGNORECASE)
        if iso_match:
            metadata["iso_clause"] = iso_match.group(1)

        # Extract duration/timeline
        duration_patterns = [
            r'(\d+)\s+weeks?',
            r'(\d+)\s+months?',
            r'(\d+)\s+days?',
            r'(\d+-\d+)\s+hours?'
        ]
        for pattern in duration_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                metadata["duration"] = match.group(0)
                break

        # Extract complexity indicators
        if any(word in content.lower() for word in ['complex', 'advanced', 'sophisticated']):
            metadata["complexity"] = "high"
        elif any(word in content.lower() for word in ['simple', 'basic', 'straightforward']):
            metadata["complexity"] = "low"
        else:
            metadata["complexity"] = "medium"

        # Extract tags
        tags = []
        if 'healthcare' in content.lower() or 'patient' in content.lower():
            tags.append("healthcare")
        if 'it' in content.lower() or 'cyber' in content.lower() or 'technical' in content.lower():
            tags.append("it_tech")
        if 'certification' in content.lower() or 'audit' in content.lower():
            tags.append("certification")
        if 'bia' in content.lower():
            tags.append("bia")
        if 'risk' in content.lower():
            tags.append("risk")
        if 'exercise' in content.lower() or 'test' in content.lower():
            tags.append("testing")

        metadata["tags"] = tags

        return metadata

    def _chunk_flow(self, content: str, base_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk long flow into smaller pieces

        Args:
            content: Flow content
            base_doc: Base flow document

        Returns:
            List of chunked flow documents
        """
        chunks = []

        # Split by major sections (Phase, Step, etc.)
        sections = re.split(r'\n(#{2,4}\s+)', content)

        current_chunk = ""
        chunk_num = 1

        for i, section in enumerate(sections):
            if section.startswith('#'):
                # This is a header
                if len(current_chunk) > 6000:  # ~1500 tokens
                    # Save current chunk
                    chunk_doc = base_doc.copy()
                    chunk_doc["flow_id"] = f"{base_doc['flow_id']}_chunk_{chunk_num}"
                    chunk_doc["content"] = current_chunk.strip()
                    chunk_doc["chunk_number"] = chunk_num
                    chunk_doc["is_chunk"] = True
                    chunks.append(chunk_doc)

                    chunk_num += 1
                    current_chunk = section
                else:
                    current_chunk += section
            else:
                current_chunk += section

        # Add last chunk
        if current_chunk.strip():
            chunk_doc = base_doc.copy()
            chunk_doc["flow_id"] = f"{base_doc['flow_id']}_chunk_{chunk_num}"
            chunk_doc["content"] = current_chunk.strip()
            chunk_doc["chunk_number"] = chunk_num
            chunk_doc["is_chunk"] = True
            chunks.append(chunk_doc)

        return chunks

    def _parse_by_sections(
        self,
        content: str,
        source_id: str,
        source_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Parse document by major sections (when no numbered flows)

        Args:
            content: Document content
            source_id: Source identifier
            source_config: Source configuration

        Returns:
            List of section documents
        """
        flows = []

        # Split by ## headers
        sections = re.split(r'\n##\s+(.+?)\n', content)

        for i in range(1, len(sections), 2):
            if i + 1 >= len(sections):
                break

            section_name = sections[i].strip()
            section_content = sections[i + 1].strip()

            # Skip metadata sections
            if any(skip in section_name.lower() for skip in ['overview', 'summary', 'contents', 'index']):
                continue

            flow_doc = {
                "flow_id": f"{source_id}_section_{i // 2}",
                "flow_name": section_name,
                "content": section_content,
                "source": source_id,
                "source_file": source_config["file"],
                "priority": source_config["priority"],
                "domain": source_config["domain"],
                "type": source_config["type"],
                "is_section": True,
                "loaded_at": datetime.utcnow().isoformat()
            }

            flows.append(flow_doc)

        return flows

    async def index_flows(
        self,
        flows: List[Dict[str, Any]],
        vector_indexer
    ) -> int:
        """
        Index flows into Qdrant vector database

        Args:
            flows: List of flow documents
            vector_indexer: VectorIndexer instance

        Returns:
            Number of flows indexed
        """
        logger.info(f" Indexing {len(flows)} flows into Qdrant...")

        indexed_count = 0

        for flow in flows:
            try:
                # Index flow
                await vector_indexer.index_document(
                    collection_name=self.collection_name,
                    document_id=flow["flow_id"],
                    text=f"{flow['flow_name']}\n\n{flow['content']}",
                    metadata=flow
                )

                indexed_count += 1

                if indexed_count % 10 == 0:
                    logger.info(f" Indexed {indexed_count}/{len(flows)} flows...")

            except Exception as e:
                logger.error(f" Failed to index {flow['flow_id']}: {e}")

        logger.info(f" Indexing complete: {indexed_count}/{len(flows)} flows indexed")

        return indexed_count


async def main():
    """
    Main function to load and index business flows

    Usage:
        python business_flows_loader.py
    """
    from ..indexer.vector_indexer import VectorIndexer

    # Initialize loader
    loader = BusinessFlowsLoader()

    # Load all flows
    logger.info(" Loading business flows...")
    flows = await loader.load_all_flows()

    # Initialize vector indexer
    indexer = VectorIndexer(
        collection_name="bcm_business_flows",
        embedding_provider="auto"  # Will try OpenAI, then local, then TF-IDF
    )

    # Create collection
    await indexer.create_collection_if_not_exists()

    # Index flows
    indexed_count = await loader.index_flows(flows, indexer)

    logger.info(f"""
     Business Flows Loading Complete!

    Flows Loaded: {len(flows)}
    Flows Indexed: {indexed_count}
    Collection: bcm_business_flows

    Now you can query flows with RAG:

    from intelligent_core.ai_foundation.rag.pipeline import RAGPipeline

    rag = RAGPipeline()
    results = rag.query("How to conduct BIA in healthcare?")
    """)


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
