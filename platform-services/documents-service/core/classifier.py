"""
Document Classification and Categorization
Uses rule-based and ML methods to classify documents

Classifications:
- Document type (policy, procedure, plan, etc.)
- ISO 22301 clause mapping
- BCI GPG practice mapping
- Security classification
- Department/process area

Based on:
- BCM_1/document_processor/document_processor.py (lines 513-620)
- BCM_1/document-processor/services/classifier.py (lines 23-156)
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


# ============================================================================
# CLASSIFICATION PATTERNS
# ============================================================================

class DocumentTypePattern:
    """Patterns for document type classification"""

    POLICY = {
        'keywords': [
            'policy', 'policies', 'strategic direction', 'governance',
            'commitment', 'business continuity policy', 'bc policy'
        ],
        'title_patterns': [
            r'.*policy.*',
            r'.*governance.*framework',
        ],
        'structural_markers': [
            'policy statement', 'policy scope', 'policy objectives',
            'roles and responsibilities', 'policy review'
        ],
    }

    PROCEDURE = {
        'keywords': [
            'procedure', 'procedures', 'process', 'workflow',
            'standard operating procedure', 'sop', 'how to',
            'step-by-step', 'instructions'
        ],
        'title_patterns': [
            r'.*procedure.*',
            r'.*sop.*',
            r'.*process.*',
        ],
        'structural_markers': [
            'purpose', 'scope', 'procedure steps', 'responsibilities',
            'step 1', 'step 2', 'step 3'
        ],
    }

    PLAN = {
        'keywords': [
            'plan', 'business continuity plan', 'bcp', 'disaster recovery',
            'incident response plan', 'crisis management plan',
            'recovery strategy', 'activation', 'response procedures'
        ],
        'title_patterns': [
            r'.*plan.*',
            r'.*bcp.*',
            r'.*recovery.*',
            r'.*response.*',
        ],
        'structural_markers': [
            'activation criteria', 'response team', 'recovery procedures',
            'contact list', 'escalation', 'notification'
        ],
    }

    RISK_ASSESSMENT = {
        'keywords': [
            'risk assessment', 'risk analysis', 'risk evaluation',
            'risk register', 'threat assessment', 'vulnerability',
            'likelihood', 'impact', 'risk matrix'
        ],
        'title_patterns': [
            r'.*risk.*assessment.*',
            r'.*risk.*analysis.*',
            r'.*risk.*register.*',
        ],
        'structural_markers': [
            'risk identification', 'risk analysis', 'risk evaluation',
            'risk treatment', 'likelihood', 'consequence'
        ],
    }

    BIA = {
        'keywords': [
            'business impact analysis', 'bia', 'impact assessment',
            'rto', 'rpo', 'mtpd', 'critical activities',
            'recovery time objective', 'recovery point objective'
        ],
        'title_patterns': [
            r'.*bia.*',
            r'.*business.*impact.*analysis.*',
            r'.*impact.*assessment.*',
        ],
        'structural_markers': [
            'critical activities', 'dependencies', 'rto', 'rpo',
            'financial impact', 'operational impact'
        ],
    }

    AUDIT_REPORT = {
        'keywords': [
            'audit', 'audit report', 'internal audit', 'compliance audit',
            'audit findings', 'non-conformities', 'corrective actions',
            'audit scope', 'audit criteria'
        ],
        'title_patterns': [
            r'.*audit.*report.*',
            r'.*audit.*',
        ],
        'structural_markers': [
            'audit scope', 'audit findings', 'observations',
            'non-conformities', 'recommendations', 'corrective actions'
        ],
    }

    EXERCISE_REPORT = {
        'keywords': [
            'exercise', 'drill', 'test', 'tabletop exercise',
            'exercise report', 'lessons learned', 'exercise objectives',
            'exercise scenario', 'exercise evaluation'
        ],
        'title_patterns': [
            r'.*exercise.*report.*',
            r'.*drill.*report.*',
            r'.*test.*report.*',
        ],
        'structural_markers': [
            'exercise objectives', 'scenario', 'participants',
            'observations', 'lessons learned', 'action items'
        ],
    }


# ============================================================================
# ISO 22301 CLAUSE MAPPING
# ============================================================================

ISO_22301_CLAUSE_PATTERNS = {
    # Context of the organization
    '4.1': ['context', 'organization', 'external issues', 'internal issues', 'environment'],
    '4.2': ['stakeholder', 'interested parties', 'requirements', 'needs and expectations'],
    '4.3': ['scope', 'bcms scope', 'boundaries', 'applicability'],
    '4.4': ['bcms', 'business continuity management system', 'processes', 'interactions'],

    # Leadership
    '5.1': ['leadership', 'commitment', 'top management', 'demonstrate commitment'],
    '5.2': ['policy', 'bc policy', 'business continuity policy', 'establish policy'],
    '5.3': ['roles', 'responsibilities', 'authorities', 'organizational roles'],

    # Planning
    '6.1': ['risk', 'opportunities', 'address risks', 'actions to address'],
    '6.2': ['objectives', 'business continuity objectives', 'bc objectives', 'plan to achieve'],
    '6.3': ['changes', 'planning changes', 'planned changes'],

    # Support
    '7.1': ['resources', 'determine resources', 'provide resources'],
    '7.2': ['competence', 'competent', 'training', 'skills', 'knowledge'],
    '7.3': ['awareness', 'aware', 'importance', 'contribution'],
    '7.4': ['communication', 'internal communication', 'external communication'],
    '7.5': ['documented information', 'document control', 'records', 'documentation'],

    # Operation
    '8.1': ['operational planning', 'control', 'criteria', 'implement'],
    '8.2': ['bia', 'business impact analysis', 'impact assessment', 'risk assessment'],
    '8.3': ['strategy', 'business continuity strategy', 'recovery strategy', 'response strategy'],
    '8.4': ['plans', 'procedures', 'business continuity plans', 'incident response'],
    '8.5': ['exercise', 'testing', 'drill', 'validate', 'test plans'],

    # Performance evaluation
    '9.1': ['monitoring', 'measurement', 'analysis', 'evaluation', 'performance'],
    '9.2': ['internal audit', 'audit', 'audit programme', 'conduct audits'],
    '9.3': ['management review', 'review', 'review inputs', 'review outputs'],

    # Improvement
    '10.1': ['nonconformity', 'corrective action', 'non-conformance', 'corrective actions'],
    '10.2': ['continual improvement', 'continuous improvement', 'improve'],
}


# ============================================================================
# BCI GPG PRACTICE MAPPING
# ============================================================================

BCI_GPG_PATTERNS = {
    'PP1': ['policy', 'governance', 'programme management', 'bcm policy', 'organizational resilience'],
    'PP2': ['embedding', 'culture', 'awareness', 'training', 'competence', 'understanding'],
    'PP3': ['analysis', 'bia', 'risk assessment', 'impact analysis', 'dependencies'],
    'PP4': ['design', 'strategy', 'response', 'recovery', 'resilience options'],
    'PP5': ['response', 'plans', 'procedures', 'incident response', 'crisis management'],
    'PP6': ['validation', 'exercising', 'testing', 'review', 'continuous improvement'],
}


# ============================================================================
# CLASSIFIER CLASS
# ============================================================================

class DocumentClassifier:
    """
    Classify documents using rule-based and pattern matching.

    Classifications:
    - Document type
    - ISO 22301 clauses
    - BCI GPG practices
    - Department/process area
    """

    def __init__(self):
        """Initialize classifier with patterns."""
        self.type_patterns = {
            'policy': DocumentTypePattern.POLICY,
            'procedure': DocumentTypePattern.PROCEDURE,
            'plan': DocumentTypePattern.PLAN,
            'risk_assessment': DocumentTypePattern.RISK_ASSESSMENT,
            'bia': DocumentTypePattern.BIA,
            'audit_report': DocumentTypePattern.AUDIT_REPORT,
            'exercise_report': DocumentTypePattern.EXERCISE_REPORT,
        }

    def classify(
        self,
        text: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Classify document based on content.

        Args:
            text: Document text content
            title: Document title (optional)
            metadata: Document metadata (optional)

        Returns:
            Classification results dictionary
        """
        text_lower = text.lower()
        title_lower = title.lower() if title else ''

        # Classify document type
        doc_type, type_confidence = self._classify_type(text_lower, title_lower)

        # Map to ISO 22301 clauses
        iso_clauses = self._map_iso_clauses(text_lower)

        # Map to BCI GPG practices
        bci_practices = self._map_bci_practices(text_lower)

        # Detect department/process area
        department = self._detect_department(text_lower)
        process_area = self._detect_process_area(text_lower)

        # Suggest security classification
        classification = self._suggest_classification(doc_type, iso_clauses, text_lower)

        return {
            'document_type': doc_type,
            'type_confidence': type_confidence,
            'iso_clauses': iso_clauses,
            'bci_practices': bci_practices,
            'department': department,
            'process_area': process_area,
            'suggested_classification': classification,
            'is_controlled': doc_type in ['policy', 'procedure', 'plan'],
            'requires_approval': doc_type in ['policy', 'procedure', 'plan', 'risk_assessment', 'bia'],
        }

    def _classify_type(
        self,
        text: str,
        title: str
    ) -> Tuple[str, float]:
        """
        Classify document type with confidence score.

        Based on: BCM_1/document_processor/document_processor.py lines 546-589

        Args:
            text: Lowercase document text
            title: Lowercase document title

        Returns:
            Tuple of (document_type, confidence_score)
        """
        type_scores = {}

        for doc_type, patterns in self.type_patterns.items():
            score = 0.0

            # Check title patterns (highest weight)
            for pattern in patterns['title_patterns']:
                if re.search(pattern, title):
                    score += 40

            # Check keywords in title (high weight)
            for keyword in patterns['keywords']:
                if keyword in title:
                    score += 30

            # Check keywords in text (medium weight)
            keyword_count = sum(1 for kw in patterns['keywords'] if kw in text)
            score += min(keyword_count * 5, 20)  # Max 20 points

            # Check structural markers (medium weight)
            marker_count = sum(1 for marker in patterns['structural_markers'] if marker in text)
            score += min(marker_count * 3, 15)  # Max 15 points

            type_scores[doc_type] = min(score, 100)  # Cap at 100

        # Get highest scoring type
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            confidence = type_scores[best_type] / 100.0

            # If confidence too low, classify as "other"
            if confidence < 0.3:
                return 'other', confidence

            return best_type, confidence

        return 'other', 0.0

    def _map_iso_clauses(self, text: str) -> List[str]:
        """
        Map document to ISO 22301 clauses.

        Based on: BCM_1/document_processor/document_processor.py lines 591-607

        Args:
            text: Lowercase document text

        Returns:
            List of matched ISO clause numbers
        """
        matched_clauses = []

        for clause, keywords in ISO_22301_CLAUSE_PATTERNS.items():
            # Check if any keywords present
            if any(keyword in text for keyword in keywords):
                matched_clauses.append(clause)

        # Sort clauses
        matched_clauses.sort()

        return matched_clauses

    def _map_bci_practices(self, text: str) -> List[str]:
        """
        Map document to BCI GPG Professional Practices.

        Args:
            text: Lowercase document text

        Returns:
            List of matched BCI practice codes (PP1-PP6)
        """
        matched_practices = []

        for practice, keywords in BCI_GPG_PATTERNS.items():
            # Check if any keywords present
            keyword_matches = sum(1 for keyword in keywords if keyword in text)

            # Need at least 2 keyword matches for confidence
            if keyword_matches >= 2:
                matched_practices.append(practice)

        # Sort practices
        matched_practices.sort()

        return matched_practices

    def _detect_department(self, text: str) -> Optional[str]:
        """
        Detect department from document text.

        Args:
            text: Lowercase document text

        Returns:
            Department name or None
        """
        department_patterns = {
            'IT': ['information technology', 'it department', 'technology', 'infrastructure'],
            'Operations': ['operations', 'operational', 'production'],
            'HR': ['human resources', 'hr department', 'personnel', 'people'],
            'Finance': ['finance', 'financial', 'accounting', 'treasury'],
            'Security': ['security', 'information security', 'cyber security'],
            'Risk': ['risk management', 'risk department', 'enterprise risk'],
            'Compliance': ['compliance', 'regulatory', 'audit'],
            'Facilities': ['facilities', 'building management', 'physical security'],
        }

        for dept, keywords in department_patterns.items():
            if any(keyword in text for keyword in keywords):
                return dept

        return None

    def _detect_process_area(self, text: str) -> Optional[str]:
        """
        Detect business process area from document text.

        Args:
            text: Lowercase document text

        Returns:
            Process area name or None
        """
        process_patterns = {
            'Customer Service': ['customer service', 'customer support', 'help desk'],
            'Supply Chain': ['supply chain', 'procurement', 'logistics', 'vendor'],
            'Manufacturing': ['manufacturing', 'production', 'assembly'],
            'Sales': ['sales', 'business development', 'account management'],
            'Marketing': ['marketing', 'communications', 'public relations'],
            'Product Development': ['product development', 'research', 'development', 'r&d'],
        }

        for process, keywords in process_patterns.items():
            if any(keyword in text for keyword in keywords):
                return process

        return None

    def _suggest_classification(
        self,
        doc_type: str,
        iso_clauses: List[str],
        text: str
    ) -> str:
        """
        Suggest security classification based on document attributes.

        Based on: BCM_1/document-processor/services/classifier.py lines 134-156

        Args:
            doc_type: Classified document type
            iso_clauses: Mapped ISO clauses
            text: Document text

        Returns:
            Suggested classification level
        """
        # Critical documents get higher classification
        critical_types = ['policy', 'risk_assessment', 'bia', 'audit_report']

        if doc_type in critical_types:
            return 'confidential'

        # Documents with sensitive keywords
        sensitive_keywords = [
            'confidential', 'restricted', 'sensitive', 'proprietary',
            'trade secret', 'personal data', 'pii', 'financial',
            'salary', 'compensation', 'security vulnerability'
        ]

        if any(keyword in text for keyword in sensitive_keywords):
            return 'confidential'

        # Plans and procedures typically internal
        if doc_type in ['plan', 'procedure']:
            return 'internal'

        # Check if ISO 22301 core clauses (more sensitive)
        core_clauses = ['4.3', '6.1', '8.2', '8.3', '8.4']
        if any(clause in iso_clauses for clause in core_clauses):
            return 'internal'

        # Default to internal for BCM documents
        return 'internal'


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def batch_classify_documents(
    documents: List[Dict[str, Any]],
    classifier: Optional[DocumentClassifier] = None
) -> List[Dict[str, Any]]:
    """
    Classify multiple documents in batch.

    Args:
        documents: List of document dictionaries with 'text' and optionally 'title'
        classifier: Classifier instance (will create if None)

    Returns:
        List of classification results
    """
    if classifier is None:
        classifier = DocumentClassifier()

    results = []

    for doc in documents:
        result = classifier.classify(
            text=doc.get('text', ''),
            title=doc.get('title'),
            metadata=doc.get('metadata')
        )

        results.append({
            **doc,
            'classification': result
        })

    return results
