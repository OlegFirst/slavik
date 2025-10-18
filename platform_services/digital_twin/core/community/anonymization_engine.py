"""
Anonymization Engine

Ensures privacy by anonymizing sensitive data before sharing in community.

Features:
- Text anonymization (remove PII, organizations, emails, etc.)
- Data generalization (revenue → category, location → region, etc.)
- Configurable anonymization levels
- NER-based entity detection and replacement
"""

import logging
import re
from typing import Dict, List, Optional, Any, Set
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================
# ANONYMIZATION RULES
# ============================================

class AnonymizationLevel(str, Enum):
    """Level of anonymization to apply"""
    MINIMAL = "minimal"     # Remove only obvious PII
    STANDARD = "standard"   # Remove PII + organization names
    FULL = "full"          # Aggressive anonymization


# Common patterns to anonymize
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_PATTERN = r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
URL_PATTERN = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
CREDIT_CARD_PATTERN = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'

# Common person name indicators (simple heuristic)
# TODO: enhance with NER model
PERSON_TITLES = [
    'Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'CEO', 'CTO', 'CFO',
    'Director', 'Manager', 'President', 'VP'
]


# ============================================
# ANONYMIZATION ENGINE
# ============================================

class AnonymizationEngine:
    """
    Engine for anonymizing sensitive data
    """

    def __init__(
        self,
        default_level: AnonymizationLevel = AnonymizationLevel.STANDARD
    ):
        """
        Initialize Anonymization Engine

        Args:
            default_level: Default anonymization level
        """
        self.default_level = default_level

        # Replacement templates
        self.replacements = {
            'email': '[email]',
            'phone': '[phone]',
            'url': '[url]',
            'person': '[Person Name]',
            'organization': '[Organization Name]',
            'location': '[Location]',
            'ssn': '[SSN]',
            'credit_card': '[XXXX]',
            'number': '[Number]',
        }

        # Cache for detected entities (per session)
        self._entity_cache: Dict[str, Set[str]] = {
            'persons': set(),
            'organizations': set(),
            'locations': set(),
        }

        logger.info(f"Anonymization Engine initialized (level: {default_level.value})")

    # ============================================
    # PUBLIC API - TEXT ANONYMIZATION
    # ============================================

    async def anonymize_text(
        self,
        text: str,
        level: Optional[AnonymizationLevel] = None
    ) -> str:
        """
        Anonymize text content

        Args:
            text: Text to anonymize
            level: Anonymization level (default: engine default)

        Returns:
            Anonymized text
        """
        if not text:
            return text

        level = level or self.default_level
        anonymized = text

        # Level 1: Remove obvious PII (all levels)
        anonymized = self._remove_pii(anonymized)

        # Level 2: Remove organization references (standard+)
        if level in [AnonymizationLevel.STANDARD, AnonymizationLevel.FULL]:
            anonymized = await self._remove_organizations(anonymized)

        # Level 3: Aggressive anonymization (full only)
        if level == AnonymizationLevel.FULL:
            anonymized = await self._aggressive_anonymization(anonymized)

        return anonymized

    async def anonymize_data(
        self,
        data: Dict[str, Any],
        level: Optional[AnonymizationLevel] = None
    ) -> Dict[str, Any]:
        """
        Anonymize dictionary data

        Args:
            data: Dictionary to anonymize
            level: Anonymization level

        Returns:
            Anonymized dictionary
        """
        level = level or self.default_level
        anonymized = {}

        for key, value in data.items():
            if isinstance(value, str):
                anonymized[key] = await self.anonymize_text(value, level)
            elif isinstance(value, dict):
                anonymized[key] = await self.anonymize_data(value, level)
            elif isinstance(value, list):
                anonymized[key] = [
                    await self.anonymize_text(item, level) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                anonymized[key] = value

        return anonymized

    # ============================================
    # PUBLIC API - DATA GENERALIZATION
    # ============================================

    def generalize_revenue(self, revenue: float) -> str:
        """
        Generalize revenue to category

        Examples:
            $500,000 → "$100K-$1M"
            $5,000,000 → "$1M-$10M"
        """
        if revenue < 100_000:
            return "$0-$100K"
        elif revenue < 1_000_000:
            return "$100K-$1M"
        elif revenue < 10_000_000:
            return "$1M-$10M"
        elif revenue < 100_000_000:
            return "$10M-$100M"
        else:
            return "$100M+"

    def generalize_size(self, employee_count: int) -> str:
        """
        Generalize employee count to size category

        Examples:
            25 → "11-50"
            156 → "51-200"
        """
        if employee_count <= 10:
            return "1-10"
        elif employee_count <= 50:
            return "11-50"
        elif employee_count <= 200:
            return "51-200"
        elif employee_count <= 1000:
            return "201-1000"
        else:
            return "1000+"

    def generalize_location(self, location: str) -> str:
        """
        Generalize location (remove specific address)

        Examples:
            "123 Main St, Boston, MA, USA" → "Boston, USA"
            "456 Oak Ave, London, UK" → "London, UK"
        """
        if not location:
            return "[Location]"

        # Remove specific street addresses
        # Keep city and country
        parts = [p.strip() for p in location.split(',')]

        if len(parts) >= 3:
            # Assume format: [street], [city], [state/region], [country]
            city = parts[-3] if len(parts) >= 3 else parts[0]
            country = parts[-1]
            return f"{city}, {country}"
        elif len(parts) == 2:
            return f"{parts[0]}, {parts[1]}"
        else:
            return parts[0]

    def generalize_date(self, date_str: str) -> str:
        """
        Generalize date to month/year

        Examples:
            "2024-03-15" → "March 2024"
            "2024-03-15 14:30:00" → "March 2024"
        """
        try:
            # Simple parsing - just extract year and month
            # Format: YYYY-MM-DD or similar
            parts = date_str.split('-')
            if len(parts) >= 2:
                year = parts[0]
                month = int(parts[1])
                month_names = [
                    'January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'
                ]
                if 1 <= month <= 12:
                    return f"{month_names[month-1]} {year}"
        except Exception:
            pass

        return "[Date]"

    # ============================================
    # PRIVATE METHODS - ANONYMIZATION
    # ============================================

    def _remove_pii(self, text: str) -> str:
        """Remove obvious PII (emails, phones, URLs, SSN, credit cards)"""

        # Email addresses
        text = re.sub(EMAIL_PATTERN, self.replacements['email'], text)

        # Phone numbers
        text = re.sub(PHONE_PATTERN, self.replacements['phone'], text)

        # URLs
        text = re.sub(URL_PATTERN, self.replacements['url'], text)

        # SSN
        text = re.sub(SSN_PATTERN, self.replacements['ssn'], text)

        # Credit cards
        text = re.sub(CREDIT_CARD_PATTERN, self.replacements['credit_card'], text)

        return text

    async def _remove_organizations(self, text: str) -> str:
        """
        Remove organization names

        TODO: Enhance with NER model for better detection
        Currently uses simple heuristics
        """
        # Simple heuristic: replace common suffixes
        suffixes = [
            ' Inc.', ' LLC', ' Corp.', ' Corporation', ' Ltd.',
            ' Limited', ' Company', ' Co.', ' LLP', ' Plc'
        ]

        for suffix in suffixes:
            # Find words before suffix
            pattern = r'\b([A-Z][A-Za-z&\s]+)' + re.escape(suffix) + r'\b'
            text = re.sub(pattern, self.replacements['organization'], text)

        return text

    async def _aggressive_anonymization(self, text: str) -> str:
        """
        Aggressive anonymization (remove person names, locations, numbers)

        TODO: Implement proper NER with spaCy or transformers
        """
        # Remove person titles + names (simple heuristic)
        for title in PERSON_TITLES:
            # Pattern: Title Name (e.g., "Dr. Smith", "CEO John")
            pattern = r'\b' + re.escape(title) + r'\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'
            text = re.sub(pattern, self.replacements['person'], text)

        # Remove standalone capitalized names (potential person/org names)
        # Be conservative to avoid false positives
        # Only replace sequences of 2+ capitalized words
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'

        def replace_if_name(match):
            name = match.group(1)
            # Don't replace if it's common non-name capitalized phrase
            common_phrases = [
                'Business Continuity', 'Disaster Recovery', 'Risk Management',
                'United States', 'European Union', 'New York', 'Los Angeles'
            ]
            if name in common_phrases:
                return name
            return self.replacements['person']

        text = re.sub(pattern, replace_if_name, text)

        # Remove specific numbers (potential sensitive data)
        # Keep percentages and common numbers
        # Replace 5+ digit numbers
        text = re.sub(r'\b\d{5,}\b', self.replacements['number'], text)

        return text

    # ============================================
    # ENTITY DETECTION (FOR NER)
    # ============================================

    async def detect_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Detect entities in text

        TODO: Implement with spaCy NER or transformers

        Returns:
            Dictionary of entity types to lists of detected entities
        """
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'emails': [],
            'phones': [],
            'urls': [],
        }

        # Email detection
        entities['emails'] = re.findall(EMAIL_PATTERN, text)

        # Phone detection
        entities['phones'] = re.findall(PHONE_PATTERN, text)

        # URL detection
        entities['urls'] = re.findall(URL_PATTERN, text)

        # TODO: Add NER for persons, organizations, locations
        # Example with spaCy:
        # import spacy
        # nlp = spacy.load("en_core_web_sm")
        # doc = nlp(text)
        # for ent in doc.ents:
        #     if ent.label_ == "PERSON":
        #         entities['persons'].append(ent.text)
        #     elif ent.label_ == "ORG":
        #         entities['organizations'].append(ent.text)
        #     elif ent.label_ in ["GPE", "LOC"]:
        #         entities['locations'].append(ent.text)

        return entities

    # ============================================
    # VALIDATION
    # ============================================

    def validate_anonymization(self, text: str) -> Dict[str, Any]:
        """
        Validate that text is properly anonymized

        Returns:
            Validation results with any remaining PII found
        """
        issues = []

        # Check for emails
        if re.search(EMAIL_PATTERN, text):
            issues.append("Email addresses detected")

        # Check for phone numbers
        if re.search(PHONE_PATTERN, text):
            issues.append("Phone numbers detected")

        # Check for URLs
        if re.search(URL_PATTERN, text):
            issues.append("URLs detected")

        # Check for SSN
        if re.search(SSN_PATTERN, text):
            issues.append("SSN detected")

        # Check for credit cards
        if re.search(CREDIT_CARD_PATTERN, text):
            issues.append("Credit card numbers detected")

        is_valid = len(issues) == 0

        return {
            'is_valid': is_valid,
            'issues': issues,
            'text_length': len(text),
        }

    # ============================================
    # STATISTICS
    # ============================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get anonymization engine statistics"""
        return {
            'default_level': self.default_level.value,
            'cached_entities': {
                'persons': len(self._entity_cache['persons']),
                'organizations': len(self._entity_cache['organizations']),
                'locations': len(self._entity_cache['locations']),
            },
        }

    def clear_cache(self) -> None:
        """Clear entity cache"""
        for key in self._entity_cache:
            self._entity_cache[key].clear()
        logger.info("Anonymization cache cleared")
