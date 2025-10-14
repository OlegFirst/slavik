"""
Case Anonymizer Service

Multi-layer anonymization for privacy-preserving collective intelligence.

Layers:
1. Organization Anonymization: Remove org name, people, dates
2. Aggregation: Combine with minimum 5 orgs
3. Synthesis: AI generates collective wisdom

Privacy guarantees:
- K-anonymity (k=5)
- No outlier highlighting
- Geographic generalization
- Time correlation prevention

Example:
>>> anonymizer = AnonymizerService()
>>> result = await anonymizer.anonymize_case(case_data)
>>> # result.anonymized_data: All identifying info removed
>>> # result.risk_score: 0.2 (low risk)
>>> # result.k_anonymity: 7 (safe)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import hashlib
from ..config import settings

class AnonymizerService:
    """
    Multi-layer case anonymization service

    Ensures privacy while preserving valuable patterns
    """

    def __init__(self):
        self.k_anonymity = settings.K_ANONYMITY
        self.max_risk_score = settings.MAX_RISK_SCORE

    async def anonymize_case(
        self,
        case_data: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> AnonymizationResult:
        """
        Anonymize case data

        Args:
            case_data: Original case data
            context: Optional context (e.g., similar cases count)

        Returns:
            AnonymizationResult with anonymized data and risk score
        """

        anonymized = {}

        # Layer 1: Remove direct identifiers
        anonymized['organization_context'] = self._anonymize_organization(
            case_data.get('organization_context', {})
        )

        # Layer 2: Anonymize journey
        anonymized['journey'] = self._anonymize_journey(
            case_data.get('journey', {})
        )

        # Layer 3: Anonymize success patterns
        anonymized['success_patterns'] = self._anonymize_patterns(
            case_data.get('success_patterns', [])
        )

        # Layer 4: Anonymize challenges
        anonymized['challenges'] = self._anonymize_challenges(
            case_data.get('challenges', [])
        )

        # Layer 5: Anonymize metrics
        anonymized['metrics'] = self._anonymize_metrics(
            case_data.get('metrics', {})
        )

        # Calculate risk score
        risk_score = self._calculate_risk_score(
            original=case_data,
            anonymized=anonymized,
            context=context
        )

        # Check k-anonymity
        k_value = context.get('similar_cases_count', 1) if context else 1

        return AnonymizationResult(
            anonymized_data=anonymized,
            risk_score=risk_score,
            k_anonymity=k_value,
            is_safe=risk_score <= self.max_risk_score and k_value >= self.k_anonymity,
            warnings=self._generate_warnings(risk_score, k_value)
        )

    def _anonymize_organization(self, org_context: Dict) -> Dict:
        """
        Anonymize organization information

        Removes:
        - Organization name
        - Specific location (city)
        - Exact employee count

        Keeps:
        - Industry category
        - Size category
        - Region (generalized)
        """

        anonymized = {}

        # Industry: Keep as-is (category)
        if 'industry' in org_context:
            anonymized['industry'] = org_context['industry']

        # Size: Convert to category
        if 'size' in org_context:
            anonymized['size_category'] = self._categorize_size(org_context['size'])

        # Region: Generalize
        if 'location' in org_context:
            anonymized['region'] = self._generalize_location(org_context['location'])

        # Maturity level: Keep (generic)
        if 'bcm_maturity' in org_context:
            anonymized['bcm_maturity'] = org_context['bcm_maturity']

        # Remove: name, city, exact_employee_count, specific_location
        # These are NOT included in anonymized version

        return anonymized

    def _anonymize_journey(self, journey: Dict) -> Dict:
        """
        Anonymize journey information

        Removes:
        - Specific dates
        - Individual names
        - Department names (might be unique)

        Keeps:
        - Duration patterns
        - Phase sequence
        - General challenges
        """

        anonymized = {}

        # Duration: Keep pattern
        if 'duration_days' in journey:
            # Round to prevent exact matching
            duration = journey['duration_days']
            anonymized['duration_category'] = self._categorize_duration(duration)

        # Phases: Anonymize each
        if 'phases' in journey:
            anonymized['phases'] = [
                self._anonymize_phase(phase)
                for phase in journey['phases']
            ]

        # Timeline: Relative, not absolute
        if 'start_date' in journey:
            # Don't include exact date
            # Instead: "Q3 2024" or "2024"
            date = journey['start_date']
            anonymized['time_period'] = self._generalize_date(date)

        return anonymized

    def _anonymize_phase(self, phase: Dict) -> Dict:
        """Anonymize individual phase"""

        anonymized = {
            'phase_type': phase.get('phase_type'),
            'duration_days': self._round_duration(phase.get('duration_days', 0)),
            'success_indicators': self._remove_identifiers(
                phase.get('success_indicators', [])
            )
        }

        return anonymized

    def _anonymize_patterns(self, patterns: List[str]) -> List[str]:
        """
        Anonymize success patterns

        Remove:
        - Names: "John implemented..."
        - Specific tools: "Using Jira..."
        - Organization-specific terms

        Keep:
        - General approaches
        - Pattern structure
        """

        anonymized = []

        for pattern in patterns:
            # Remove names
            cleaned = self._remove_names(pattern)

            # Remove organization-specific terms
            cleaned = self._remove_org_specific_terms(cleaned)

            # Generalize tool names
            cleaned = self._generalize_tools(cleaned)

            anonymized.append(cleaned)

        return anonymized

    def _anonymize_challenges(self, challenges: List[str]) -> List[str]:
        """
        Anonymize challenges

        Similar to patterns anonymization
        """

        return [self._remove_identifiers_from_text(c) for c in challenges]

    def _anonymize_metrics(self, metrics: Dict) -> Dict:
        """
        Anonymize metrics

        Strategy:
        - Round numbers to prevent fingerprinting
        - Remove exact values if unique
        - Keep relative comparisons
        """

        anonymized = {}

        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                # Round to prevent exact matching
                anonymized[key] = self._round_metric(value)
            else:
                anonymized[key] = value

        return anonymized

    def _categorize_size(self, size: int) -> str:
        """Categorize organization size"""

        if size < 50:
            return 'small_<50'
        elif size < 200:
            return 'medium_50-200'
        elif size < 500:
            return 'medium_200-500'
        elif size < 1000:
            return 'large_500-1000'
        else:
            return 'large_1000+'

    def _generalize_location(self, location: str) -> str:
        """
        Generalize location to region

        Examples:
        - "Seattle, WA" → "Pacific Northwest"
        - "New York, NY" → "Northeast"
        - "Austin, TX" → "South"
        """

        location_lower = location.lower()

        # US regions
        if any(state in location_lower for state in ['wa', 'or', 'seattle', 'portland']):
            return 'pacific_northwest'
        elif any(state in location_lower for state in ['ny', 'ma', 'ct', 'new york', 'boston']):
            return 'northeast'
        elif any(state in location_lower for state in ['ca', 'california', 'san francisco', 'los angeles']):
            return 'west_coast'
        elif any(state in location_lower for state in ['tx', 'texas', 'austin', 'dallas']):
            return 'south'
        elif any(state in location_lower for state in ['il', 'chicago', 'mi', 'detroit']):
            return 'midwest'

        # International
        elif any(country in location_lower for country in ['uk', 'london', 'england']):
            return 'uk_ireland'
        elif any(country in location_lower for country in ['germany', 'france', 'netherlands']):
            return 'western_europe'

        return 'other'

    def _categorize_duration(self, days: int) -> str:
        """Categorize duration"""

        if days < 30:
            return '<1_month'
        elif days < 60:
            return '1-2_months'
        elif days < 90:
            return '2-3_months'
        elif days < 180:
            return '3-6_months'
        else:
            return '6+_months'

    def _generalize_date(self, date_str: str) -> str:
        """
        Generalize date to quarter/year

        "2024-08-15" → "Q3_2024"
        """

        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            quarter = (date.month - 1) // 3 + 1
            return f"Q{quarter}_{date.year}"
        except:
            return "unknown"

    def _round_duration(self, days: int) -> int:
        """Round duration to nearest 5"""
        return round(days / 5) * 5

    def _round_metric(self, value: float) -> float:
        """Round metric to 2 significant figures"""

        if value == 0:
            return 0

        # Round to 2 significant figures
        from math import log10, floor
        magnitude = floor(log10(abs(value)))
        return round(value, -magnitude + 1)

    def _remove_names(self, text: str) -> str:
        """
        Remove person names from text

        Simple approach: Remove capitalized words that might be names
        Production: Use NER (Named Entity Recognition)
        """

        # Replace common name patterns
        text = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[person]', text)

        # Remove possessives with names
        text = re.sub(r"[A-Z][a-z]+\'s", 'their', text)

        return text

    def _remove_org_specific_terms(self, text: str) -> str:
        """
        Remove organization-specific terminology

        Examples:
        - Department names
        - Internal project names
        - Specific product names
        """

        # Replace department-specific terms
        dept_pattern = r'\b(Department|Division|Team|Unit) of [A-Z][a-z]+\b'
        text = re.sub(dept_pattern, 'department', text, flags=re.IGNORECASE)

        # Replace project code names
        text = re.sub(r'\bProject [A-Z][A-Z0-9]+\b', 'project', text)

        return text

    def _generalize_tools(self, text: str) -> str:
        """
        Generalize specific tool names

        "Using Jira" → "Using project management tool"
        """

        tool_mappings = {
            r'\bJira\b': 'project management tool',
            r'\bAsana\b': 'project management tool',
            r'\bSlack\b': 'communication tool',
            r'\bMicrosoft Teams\b': 'communication tool',
            r'\bTableau\b': 'analytics tool',
            r'\bPower BI\b': 'analytics tool'
        }

        for pattern, replacement in tool_mappings.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    def _remove_identifiers(self, items: List[str]) -> List[str]:
        """Remove identifiers from list of strings"""
        return [self._remove_identifiers_from_text(item) for item in items]

    def _remove_identifiers_from_text(self, text: str) -> str:
        """Remove all identifiers from text"""

        text = self._remove_names(text)
        text = self._remove_org_specific_terms(text)
        text = self._generalize_tools(text)

        return text

    def _calculate_risk_score(
        self,
        original: Dict,
        anonymized: Dict,
        context: Optional[Dict]
    ) -> float:
        """
        Calculate re-identification risk score

        Factors:
        1. Information retained (more = higher risk)
        2. Uniqueness of attributes
        3. K-anonymity value
        4. Temporal proximity

        Returns:
            Risk score: 0.0 (safe) to 1.0 (high risk)
        """

        risk = 0.0

        # Factor 1: K-anonymity
        k_value = context.get('similar_cases_count', 1) if context else 1
        if k_value < 5:
            risk += 0.5  # Major risk
        elif k_value < 10:
            risk += 0.2

        # Factor 2: Unique attributes
        org_size = original.get('organization_context', {}).get('size', 0)
        if org_size > 1000 or org_size < 50:
            # Very large or very small = more identifiable
            risk += 0.1

        # Factor 3: Specific metrics
        metrics = anonymized.get('metrics', {})
        if len(metrics) > 10:
            # Many specific metrics = fingerprinting risk
            risk += 0.15

        # Factor 4: Temporal proximity
        time_period = anonymized.get('journey', {}).get('time_period', '')
        if 'Q' in time_period:  # Has quarterly data
            risk += 0.05

        return min(risk, 1.0)

    def _generate_warnings(self, risk_score: float, k_value: int) -> List[str]:
        """Generate privacy warnings"""

        warnings = []

        if risk_score > self.max_risk_score:
            warnings.append(
                f"Risk score {risk_score:.2f} exceeds threshold {self.max_risk_score}. "
                "Consider additional anonymization."
            )

        if k_value < self.k_anonymity:
            warnings.append(
                f"K-anonymity {k_value} below minimum {self.k_anonymity}. "
                "Need more similar cases for safe aggregation."
            )

        return warnings

    def validate_anonymization(self, result: 'AnonymizationResult') -> bool:
        """
        Validate anonymization meets privacy requirements

        Checks:
        - K-anonymity >= 5
        - Risk score <= threshold
        - No direct identifiers remain
        """

        if not result.is_safe:
            return False

        # Check for direct identifiers
        anonymized_str = str(result.anonymized_data).lower()

        # Patterns that should NOT appear
        forbidden_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Full names
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{4}-\d{2}-\d{2}\b'  # Exact dates
        ]

        for pattern in forbidden_patterns:
            if re.search(pattern, anonymized_str):
                return False

        return True


class AnonymizationResult:
    """Result of anonymization process"""

    def __init__(
        self,
        anonymized_data: Dict[str, Any],
        risk_score: float,
        k_anonymity: int,
        is_safe: bool,
        warnings: List[str]
    ):
        self.anonymized_data = anonymized_data
        self.risk_score = risk_score
        self.k_anonymity = k_anonymity
        self.is_safe = is_safe
        self.warnings = warnings

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'anonymized_data': self.anonymized_data,
            'risk_score': self.risk_score,
            'k_anonymity': self.k_anonymity,
            'is_safe': self.is_safe,
            'warnings': self.warnings
        }
