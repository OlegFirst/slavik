"""
Initialize Knowledge Base for Intelligence Layer

Loads ISO 22301, BCI Guidelines, and other knowledge sources
into RAG pipeline and Knowledge Graph for use by AI Experts.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

from .iso_loader import ISO22301Loader
from .knowledge_ingestion import KnowledgeIngestionPipeline
from .knowledge_graph import KnowledgeGraphBuilder

logger = logging.getLogger(__name__)


class KnowledgeInitializer:
    """
    Initialize complete knowledge base for Intelligence Layer

    Steps:
    1. Load ISO 22301 clauses (structured)
    2. Build Knowledge Graph (relationships)
    3. Ingest into RAG pipeline (searchable)
    4. Verify knowledge availability
    """

    def __init__(
        self,
        library_path: str = "/Users/MD/AI-Platform-ISO/ISO-22301-Library",
        rag_pipeline = None
    ):
        self.library_path = library_path
        self.rag_pipeline = rag_pipeline

        # Components
        self.iso_loader = ISO22301Loader(library_path)
        self.ingestion_pipeline = KnowledgeIngestionPipeline(library_path, rag_pipeline)
        self.graph_builder = KnowledgeGraphBuilder()

        # Results
        self.knowledge_graph = None
        self.ingestion_stats = None

    async def initialize_all(self) -> Dict[str, Any]:
        """
        Initialize complete knowledge base

        Returns:
            Initialization statistics
        """

        logger.info("=" * 70)
        logger.info(" INITIALIZING INTELLIGENCE LAYER KNOWLEDGE BASE")
        logger.info("=" * 70)

        stats = {
            'iso_clauses_loaded': 0,
            'knowledge_graph_nodes': 0,
            'knowledge_graph_edges': 0,
            'rag_documents_ingested': 0,
            'status': 'not_started'
        }

        try:
            # Step 1: Load ISO 22301 clauses
            logger.info("\n Step 1: Loading ISO 22301:2019 clauses...")
            clauses = self.iso_loader.load_all_clauses()
            stats['iso_clauses_loaded'] = len(clauses)
            logger.info(f" Loaded {stats['iso_clauses_loaded']} ISO clauses")

            # Step 2: Build Knowledge Graph
            logger.info("\n️  Step 2: Building Knowledge Graph...")
            self.knowledge_graph = self.graph_builder.build_from_iso_clauses(clauses)
            graph_stats = self.knowledge_graph.get_statistics()
            stats['knowledge_graph_nodes'] = graph_stats['total_nodes']
            stats['knowledge_graph_edges'] = graph_stats['total_edges']
            logger.info(
                f" Knowledge Graph built: "
                f"{stats['knowledge_graph_nodes']} nodes, "
                f"{stats['knowledge_graph_edges']} edges"
            )

            # Print graph breakdown
            logger.info("\n  Nodes by type:")
            for node_type, count in graph_stats['nodes_by_type'].items():
                logger.info(f"    - {node_type}: {count}")

            # Step 3: Ingest into RAG pipeline
            logger.info("\n Step 3: Ingesting knowledge into RAG pipeline...")
            self.ingestion_stats = await self.ingestion_pipeline.ingest_all_knowledge()
            stats['rag_documents_ingested'] = self.ingestion_stats['total_documents']
            logger.info(f" Ingested {stats['rag_documents_ingested']} documents into RAG")

            # Print ingestion breakdown
            logger.info("\n  Documents by source:")
            logger.info(f"    - ISO Clauses: {self.ingestion_stats['iso_clauses']}")
            logger.info(f"    - BCI Practices: {self.ingestion_stats['bci_practices']}")
            logger.info(f"    - Platform Mappings: {self.ingestion_stats['platform_mappings']}")
            logger.info(f"    - Healthcare Guides: {self.ingestion_stats['healthcare_guides']}")

            # Step 4: Verify knowledge availability
            logger.info("\n Step 4: Verifying knowledge availability...")
            verification = await self._verify_knowledge()
            stats['verification'] = verification

            if verification['all_passed']:
                stats['status'] = 'success'
                logger.info(" All verification checks passed!")
            else:
                stats['status'] = 'partial'
                logger.warning("️  Some verification checks failed")

            # Summary
            logger.info("\n" + "=" * 70)
            logger.info(" KNOWLEDGE BASE INITIALIZATION COMPLETE")
            logger.info("=" * 70)
            logger.info(f"\n  Status: {stats['status']}")
            logger.info(f"  ISO Clauses: {stats['iso_clauses_loaded']}")
            logger.info(f"  Knowledge Graph: {stats['knowledge_graph_nodes']} nodes, {stats['knowledge_graph_edges']} edges")
            logger.info(f"  RAG Documents: {stats['rag_documents_ingested']}")
            logger.info("\n" + "=" * 70)

            return stats

        except Exception as e:
            logger.error(f" Knowledge base initialization failed: {e}", exc_info=True)
            stats['status'] = 'failed'
            stats['error'] = str(e)
            return stats

    async def _verify_knowledge(self) -> Dict[str, Any]:
        """Verify knowledge is available"""

        verification = {
            'all_passed': True,
            'checks': []
        }

        # Check 1: ISO clause 8.2.2 (BIA) exists in graph
        check1 = {
            'name': 'ISO Clause 8.2.2 (BIA) in Knowledge Graph',
            'passed': False
        }

        bia_clause = self.knowledge_graph.get_node('iso-8.2.2')
        if bia_clause:
            check1['passed'] = True
            logger.info("   ISO Clause 8.2.2 (BIA) found in Knowledge Graph")
        else:
            check1['passed'] = False
            logger.error("   ISO Clause 8.2.2 (BIA) NOT found in Knowledge Graph")
            verification['all_passed'] = False

        verification['checks'].append(check1)

        # Check 2: BIA clause has evidence requirements
        check2 = {
            'name': 'BIA clause has evidence requirements',
            'passed': False
        }

        evidence = self.knowledge_graph.get_iso_clause_evidence('8.2.2')
        if len(evidence) > 0:
            check2['passed'] = True
            check2['count'] = len(evidence)
            logger.info(f"   BIA clause has {len(evidence)} evidence requirements")
        else:
            check2['passed'] = False
            logger.error("   BIA clause has NO evidence requirements")
            verification['all_passed'] = False

        verification['checks'].append(check2)

        # Check 3: BCI practices mapped
        check3 = {
            'name': 'BCI Professional Practices in graph',
            'passed': False
        }

        bci_nodes = self.knowledge_graph.query(node_type=self.graph_builder.graph.nodes[list(self.graph_builder.graph.nodes.keys())[0]].type.__class__.BCI_PRACTICE)
        if len(bci_nodes) >= 6:
            check3['passed'] = True
            check3['count'] = len(bci_nodes)
            logger.info(f"   {len(bci_nodes)} BCI Professional Practices in graph")
        else:
            check3['passed'] = False
            logger.error(f"   Only {len(bci_nodes)} BCI practices (expected 6)")
            verification['all_passed'] = False

        verification['checks'].append(check3)

        # Check 4: RAG ingestion (if pipeline available)
        if self.rag_pipeline:
            check4 = {
                'name': 'RAG documents searchable',
                'passed': False
            }

            # Try searching for BIA
            try:
                results = await self.ingestion_pipeline.search_knowledge(
                    query="Business Impact Analysis",
                    top_k=1
                )
                if len(results) > 0:
                    check4['passed'] = True
                    logger.info("   RAG search working (found BIA documents)")
                else:
                    check4['passed'] = False
                    logger.error("   RAG search returned no results")
                    verification['all_passed'] = False
            except Exception as e:
                check4['passed'] = False
                check4['error'] = str(e)
                logger.error(f"   RAG search failed: {e}")
                verification['all_passed'] = False

            verification['checks'].append(check4)

        return verification

    def get_knowledge_graph(self):
        """Get initialized knowledge graph"""
        return self.knowledge_graph

    def get_ingestion_stats(self):
        """Get ingestion statistics"""
        return self.ingestion_stats


async def initialize_intelligence_layer_knowledge(
    library_path: str = "/Users/MD/AI-Platform-ISO/ISO-22301-Library",
    rag_pipeline = None
) -> KnowledgeInitializer:
    """
    Convenience function to initialize knowledge base

    Args:
        library_path: Path to ISO-22301-Library
        rag_pipeline: RAG pipeline instance (optional)

    Returns:
        Initialized KnowledgeInitializer
    """

    initializer = KnowledgeInitializer(library_path, rag_pipeline)
    await initializer.initialize_all()
    return initializer


# Example usage
if __name__ == "__main__":
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    async def main():
        # Initialize knowledge base (without RAG for testing)
        initializer = await initialize_intelligence_layer_knowledge()

        # Access knowledge graph
        kg = initializer.get_knowledge_graph()

        # Example: Query BIA evidence
        print("\n\n Example: BIA Evidence Requirements")
        evidence = kg.get_iso_clause_evidence('8.2.2')
        for i, ev in enumerate(evidence, 1):
            print(f"  {i}. {ev}")

        # Example: Get BCI practice for clause
        practice = kg.get_bci_practice_for_clause('8.2.2')
        print(f"\n BIA maps to BCI Practice: {practice}")

        # Example: Get all operation clauses
        from .knowledge_graph import NodeType
        operation_clauses = kg.query(
            node_type=NodeType.ISO_CLAUSE,
            filters={'category': 'operation'}
        )
        print(f"\n Operation Clauses ({len(operation_clauses)}):")
        for clause in operation_clauses[:3]:
            print(f"  - {clause.properties['clause_number']}: {clause.properties['title']}")

    asyncio.run(main())
