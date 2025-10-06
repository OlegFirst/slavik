"""
Documents Module Core Processors Package

Exports all document processing components:
- Extractor: Multi-format text extraction
- Classifier: Document type and standards classification
- Analyzer: NLP and AI analysis
- Comparator: Version comparison and diff
"""

from .extractor import (
    DocumentExtractor,
    clean_extracted_text,
    extract_document_sections,
)

from .classifier import (
    DocumentClassifier,
    DocumentTypePattern,
    ISO_22301_CLAUSE_PATTERNS,
    BCI_GPG_PATTERNS,
    batch_classify_documents,
)

from .analyzer import (
    DocumentAnalyzer,
    analyze_iso_compliance,
)

from .comparator import (
    DocumentComparator,
    quick_similarity,
)

__all__ = [
    # Extractor
    'DocumentExtractor',
    'clean_extracted_text',
    'extract_document_sections',

    # Classifier
    'DocumentClassifier',
    'DocumentTypePattern',
    'ISO_22301_CLAUSE_PATTERNS',
    'BCI_GPG_PATTERNS',
    'batch_classify_documents',

    # Analyzer
    'DocumentAnalyzer',
    'analyze_iso_compliance',

    # Comparator
    'DocumentComparator',
    'quick_similarity',
]
