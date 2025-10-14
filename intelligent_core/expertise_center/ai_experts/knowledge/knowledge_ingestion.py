"""
Knowledge Ingestion Pipeline

Loads ISO 22301, BCI Guidelines, and other knowledge sources into RAG pipeline
for use by AI Experts.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

from .iso_loader import ISO22301Loader, ISO22301Clause

logger = logging.getLogger(__name__)


class KnowledgeDocument:
    """Unified knowledge document for RAG ingestion"""

    def __init__(
        self,
        document_id: str,
        title: str,
        content: str,
        source: str,
        source_type: str,
        metadata: Dict[str, Any] = None
    ):
        self.document_id = document_id
        self.title = title
        self.content = content
        self.source = source
        self.source_type = source_type  # iso_standard, bci_guidelines, case_study, etc.
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for RAG storage"""
        return {
            'id': self.document_id,
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'source_type': self.source_type,
            'metadata': self.metadata,
            'created_at': self.created_at
        }


class KnowledgeIngestionPipeline:
    """
    Ingest knowledge from ISO_22301_Library into RAG pipeline

    Sources:
    - ISO 22301:2019 clauses (structured)
    - BCI Professional Practices Guidelines
    - ISO/BCI/Platform mapping
    - Healthcare-specific guidance (WHO framework)
    - Implementation guides (BSI, NQA)
    """

    def __init__(
        self,
        library_path: str = "/Users/MD/AI-Platform-ISO/ISO-22301-Library",
        rag_pipeline = None
    ):
        self.library_path = Path(library_path)
        self.rag_pipeline = rag_pipeline
        self.iso_loader = ISO22301Loader(library_path)

    async def ingest_all_knowledge(self) -> Dict[str, int]:
        """
        Ingest all knowledge sources

        Returns:
            Statistics about ingestion
        """

        stats = {
            'iso_clauses': 0,
            'bci_practices': 0,
            'platform_mappings': 0,
            'healthcare_guides': 0,
            'total_documents': 0
        }

        logger.info("🚀 Starting knowledge ingestion...")

        # 1. ISO 22301 clauses
        logger.info("Loading ISO 22301:2019 clauses...")
        iso_docs = await self.ingest_iso_clauses()
        stats['iso_clauses'] = len(iso_docs)
        logger.info(f"✅ Loaded {stats['iso_clauses']} ISO clauses")

        # 2. BCI Professional Practices
        logger.info("Loading BCI Professional Practices...")
        bci_docs = await self.ingest_bci_practices()
        stats['bci_practices'] = len(bci_docs)
        logger.info(f"✅ Loaded {stats['bci_practices']} BCI practices")

        # 3. ISO/BCI/Platform mapping
        logger.info("Loading platform mapping...")
        mapping_docs = await self.ingest_platform_mapping()
        stats['platform_mappings'] = len(mapping_docs)
        logger.info(f"✅ Loaded {stats['platform_mappings']} mapping documents")

        # 4. Healthcare-specific guides
        logger.info("Loading healthcare guidance...")
        health_docs = await self.ingest_healthcare_guides()
        stats['healthcare_guides'] = len(health_docs)
        logger.info(f"✅ Loaded {stats['healthcare_guides']} healthcare guides")

        stats['total_documents'] = sum(stats.values())

        logger.info(f"🎉 Knowledge ingestion complete! Total: {stats['total_documents']} documents")

        return stats

    async def ingest_iso_clauses(self) -> List[KnowledgeDocument]:
        """Ingest ISO 22301:2019 clauses"""

        clauses = self.iso_loader.load_all_clauses()
        documents = []

        for clause in clauses:
            # Create document for full clause
            doc = KnowledgeDocument(
                document_id=f"iso-22301-{clause.clause_number}",
                title=f"ISO 22301:2019 Clause {clause.clause_number}: {clause.clause_title}",
                content=clause._generate_full_text(),
                source="ISO 22301:2019",
                source_type="iso_standard",
                metadata={
                    'clause_number': clause.clause_number,
                    'clause_category': self._get_clause_category(clause.clause_number),
                    'requirements_count': len(clause.requirements),
                    'evidence_count': len(clause.evidence_needed),
                    'audit_questions_count': len(clause.audit_questions)
                }
            )

            documents.append(doc)

            # If RAG pipeline available, ingest
            if self.rag_pipeline:
                await self.rag_pipeline.ingest_document(doc.to_dict())

        return documents

    async def ingest_bci_practices(self) -> List[KnowledgeDocument]:
        """Ingest BCI Professional Practices Guidelines"""

        documents = []

        # BCI has 6 Professional Practices
        bci_practices = [
            {
                'id': 'PP1',
                'title': 'Establishing BCMS',
                'description': 'Policy, governance, scope, context, stakeholder management',
                'iso_clauses': ['4.1', '4.2', '4.3', '4.4', '5.1', '5.2', '5.3', '6.1', '6.2']
            },
            {
                'id': 'PP2',
                'title': 'Embracing BC',
                'description': 'Training, awareness, communication, culture',
                'iso_clauses': ['7.1', '7.2', '7.3', '7.4']
            },
            {
                'id': 'PP3',
                'title': 'Analysis',
                'description': 'Business Impact Analysis (BIA) and Risk Assessment',
                'iso_clauses': ['8.2.2', '8.2.3']
            },
            {
                'id': 'PP4',
                'title': 'Design',
                'description': 'Business continuity strategies and solutions',
                'iso_clauses': ['8.3']
            },
            {
                'id': 'PP5',
                'title': 'Implementation',
                'description': 'BC plans, incident response structure, procedures',
                'iso_clauses': ['8.4.2', '8.4.4']
            },
            {
                'id': 'PP6',
                'title': 'Validation',
                'description': 'Exercising, testing, auditing, management review',
                'iso_clauses': ['8.5', '9.1', '9.2', '9.3']
            }
        ]

        for practice in bci_practices:
            doc = KnowledgeDocument(
                document_id=f"bci-{practice['id'].lower()}",
                title=f"BCI Professional Practice {practice['id']}: {practice['title']}",
                content=f"""BCI Professional Practice {practice['id']}: {practice['title']}

Description:
{practice['description']}

This practice aligns with ISO 22301:2019 clauses: {', '.join(practice['iso_clauses'])}

Best Practices:
- Follow systematic approach
- Document all activities
- Involve relevant stakeholders
- Ensure top management support
- Regular review and update

The BCI Good Practice Guidelines provide detailed guidance for implementing this practice,
including templates, checklists, and industry examples.
""",
                source="BCI Good Practice Guidelines",
                source_type="bci_guidelines",
                metadata={
                    'practice_id': practice['id'],
                    'iso_clauses': practice['iso_clauses']
                }
            )

            documents.append(doc)

            if self.rag_pipeline:
                await self.rag_pipeline.ingest_document(doc.to_dict())

        return documents

    async def ingest_platform_mapping(self) -> List[KnowledgeDocument]:
        """Ingest ISO/BCI/Platform mapping"""

        mapping_file = self.library_path / "iso_bci_platform_mapping.md"

        if not mapping_file.exists():
            logger.warning(f"Mapping file not found: {mapping_file}")
            return []

        with open(mapping_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Create document for entire mapping
        doc = KnowledgeDocument(
            document_id="platform-mapping",
            title="ISO 22301 ↔ BCI ↔ Platform Services Mapping",
            content=content,
            source="Platform Documentation",
            source_type="platform_mapping",
            metadata={
                'purpose': 'Map ISO requirements to platform services',
                'version': '1.0'
            }
        )

        if self.rag_pipeline:
            await self.rag_pipeline.ingest_document(doc.to_dict())

        return [doc]

    async def ingest_healthcare_guides(self) -> List[KnowledgeDocument]:
        """Ingest healthcare-specific BCM guidance"""

        healthcare_file = self.library_path / "standards" / "health_emergency_bcm.md"

        documents = []

        if healthcare_file.exists():
            with open(healthcare_file, 'r', encoding='utf-8') as f:
                content = f.read()

            doc = KnowledgeDocument(
                document_id="healthcare-bcm-guide",
                title="Healthcare Emergency and BCM Guidance",
                content=content,
                source="WHO/Healthcare BCM Framework",
                source_type="healthcare_guidance",
                metadata={
                    'industry': 'healthcare',
                    'topics': ['patient_safety', 'essential_services', 'emergency_response']
                }
            )

            documents.append(doc)

            if self.rag_pipeline:
                await self.rag_pipeline.ingest_document(doc.to_dict())

        # Add WHO Essential Services framework
        who_doc = KnowledgeDocument(
            document_id="who-essential-services",
            title="WHO Essential Health Services Framework for BCM",
            content="""WHO Essential Health Services Framework

For healthcare organizations implementing Business Continuity Management,
the WHO Essential Health Services framework provides a structured approach
to identifying and prioritizing critical clinical services.

Essential Service Categories (Tier 1 - Highest Priority):
1. Emergency Department operations
2. Intensive Care Unit (ICU)
3. Operating Rooms / Surgical Services
4. Labor & Delivery / Obstetrics
5. Emergency Radiology
6. Emergency Laboratory Services
7. Pharmacy (emergency medications)
8. Blood Bank

Critical Services (Tier 2):
1. Inpatient medical/surgical units
2. Dialysis
3. Oncology/Chemotherapy
4. Cardiac Catheterization
5. Radiology (scheduled)
6. Laboratory (routine)

Important Services (Tier 3):
1. Outpatient clinics
2. Elective surgery
3. Physical therapy
4. Diagnostic imaging (non-emergency)

Supportive Services (Tier 4):
1. Administrative functions
2. Scheduled appointments
3. Medical records (routine)
4. Billing

BIA Process for Healthcare:
1. Start with Tier 1 services (cannot be interrupted)
2. Define RTOs based on patient safety impact
3. Consider regulatory requirements (CMS, Joint Commission, state regulations)
4. Map dependencies (utilities, IT, staffing, supplies)
5. Identify single points of failure

Recovery Time Objectives for Healthcare:
- Tier 1 Essential: RTO = 0-2 hours (immediate alternative required)
- Tier 2 Critical: RTO = 2-24 hours
- Tier 3 Important: RTO = 1-3 days
- Tier 4 Supportive: RTO = 3-7 days

Compliance Considerations:
- HIPAA Security Rule (backup and disaster recovery)
- CMS Emergency Preparedness Rule
- Joint Commission Emergency Management Standards
- State health department regulations
""",
            source="WHO Essential Services Framework",
            source_type="healthcare_guidance",
            metadata={
                'industry': 'healthcare',
                'framework': 'WHO',
                'service_tiers': 4
            }
        )

        documents.append(who_doc)

        if self.rag_pipeline:
            await self.rag_pipeline.ingest_document(who_doc.to_dict())

        return documents

    def _get_clause_category(self, clause_number: str) -> str:
        """Get category for clause number"""

        if clause_number.startswith('4.'):
            return 'context'
        elif clause_number.startswith('5.'):
            return 'leadership'
        elif clause_number.startswith('6.'):
            return 'planning'
        elif clause_number.startswith('7.'):
            return 'support'
        elif clause_number.startswith('8.'):
            return 'operation'
        elif clause_number.startswith('9.'):
            return 'performance'
        elif clause_number.startswith('10.'):
            return 'improvement'
        else:
            return 'other'

    async def search_knowledge(
        self,
        query: str,
        source_types: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base

        Args:
            query: Search query
            source_types: Filter by source type (iso_standard, bci_guidelines, etc.)
            top_k: Number of results to return

        Returns:
            List of matching documents
        """

        if not self.rag_pipeline:
            logger.warning("RAG pipeline not available for search")
            return []

        # Search using RAG pipeline
        results = await self.rag_pipeline.retrieve(
            query=query,
            filters={'source_type': source_types} if source_types else None,
            top_k=top_k
        )

        return results


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        # Initialize pipeline (without RAG for testing)
        pipeline = KnowledgeIngestionPipeline()

        # Ingest all knowledge
        stats = await pipeline.ingest_all_knowledge()

        print(f"\n📊 Ingestion Statistics:")
        print(f"  ISO Clauses: {stats['iso_clauses']}")
        print(f"  BCI Practices: {stats['bci_practices']}")
        print(f"  Platform Mappings: {stats['platform_mappings']}")
        print(f"  Healthcare Guides: {stats['healthcare_guides']}")
        print(f"  Total Documents: {stats['total_documents']}")

    asyncio.run(main())
