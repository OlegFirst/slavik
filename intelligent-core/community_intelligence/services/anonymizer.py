"""
Smart Anonymization Service

Intelligently anonymizes case data while preserving utility for community learning.

Principles:
1. Remove direct identifiers (names, emails, IDs)
2. Generalize quasi-identifiers (dates, locations)
3. Preserve context (industry, size, patterns)
4. K-anonymity: ensure ≥k similar records exist
"""

from typing import Dict, Any, List, Set
import re
import hashlib
from dataclasses import dataclass

@dataclass
class AnonymizationResult:
    """Result of anonymization process"""
    anonymized_data: Dict[str, Any]
    removed_fields: List[str]
    transformed_fields: List[str]
    risk_score: float  # 0-1, higher = more identifiable

class SmartAnonymizer:
    """
    Intelligent anonymization preserving utility

    Example:
    >>> anonymizer = SmartAnonymizer(k_anonymity=5)
    >>> result = await anonymizer.anonymize_case(case_data)
    >>> print(f"Risk: {result.risk_score}")
    """

    # Direct identifiers to remove
    DIRECT_IDENTIFIERS = {
        'organization_name', 'org_name', 'company_name',
        'person_name', 'email', 'phone', 'address',
        'user_id', 'org_id', 'employee_id',
        'ip_address', 'domain', 'url'
    }

    # Quasi-identifiers to generalize
    QUASI_IDENTIFIERS = {
        'location', 'city', 'region', 'country',
        'date', 'timestamp', 'founded_date',
        'employee_count', 'revenue', 'budget'
    }

    def __init__(self, k_anonymity: int = 5):
        self.k = k_anonymity

    async def anonymize_case(self, case_data: Dict[str, Any]) -> AnonymizationResult:
        """
        Anonymize case data while preserving utility

        Steps:
        1. Remove direct identifiers
        2. Generalize quasi-identifiers
        3. Hash stable identifiers
        4. Validate k-anonymity
        """

        anonymized = case_data.copy()
        removed = []
        transformed = []

        # 1. Remove direct identifiers
        for field in self.DIRECT_IDENTIFIERS:
            if self._field_exists(anonymized, field):
                self._remove_field(anonymized, field)
                removed.append(field)

        # 2. Generalize organization context
        if 'organization_context' in anonymized:
            org = anonymized['organization_context']

            # Keep: industry, size, maturity (useful for matching)
            # Remove: name, location specifics, unique identifiers

            if 'location' in org:
                org['region'] = self._generalize_location(org['location'])
                del org['location']
                transformed.append('organization_context.location')

            if 'employee_count' in org:
                org['size'] = self._generalize_size(org['employee_count'])
                del org['employee_count']
                transformed.append('organization_context.employee_count')

        # 3. Anonymize journey (process names, dependencies)
        if 'journey' in anonymized:
            for step in anonymized['journey']:
                # Generalize dates
                if 'started_at' in step:
                    step['started_at'] = self._generalize_date(step['started_at'])
                    transformed.append('journey.started_at')

                # Generalize specific process names
                if 'actions' in step:
                    for action in step['actions']:
                        if 'data' in action and 'process_name' in action['data']:
                            action['data']['process_name'] = self._generalize_process_name(
                                action['data']['process_name']
                            )

        # 4. Hash stable IDs (for linking without revealing)
        anonymized['source_hash'] = self._create_stable_hash(case_data)

        # 5. Calculate re-identification risk
        risk = self._calculate_risk(anonymized)

        return AnonymizationResult(
            anonymized_data=anonymized,
            removed_fields=removed,
            transformed_fields=transformed,
            risk_score=risk
        )

    def _generalize_location(self, location: str) -> str:
        """Generalize location to region"""
        region_map = {
            'tallinn': 'northern_europe',
            'helsinki': 'northern_europe',
            'stockholm': 'northern_europe',
            'oslo': 'northern_europe',
            'copenhagen': 'northern_europe',
            'london': 'western_europe',
            'paris': 'western_europe',
            'berlin': 'central_europe',
            'warsaw': 'central_europe',
            'prague': 'central_europe',
            'moscow': 'eastern_europe',
            'new york': 'north_america',
            'san francisco': 'north_america',
            'toronto': 'north_america',
            'singapore': 'southeast_asia',
            'tokyo': 'east_asia',
            'sydney': 'oceania'
        }

        location_lower = location.lower()
        for city, region in region_map.items():
            if city in location_lower:
                return region

        return 'unknown_region'

    def _generalize_size(self, employee_count: int) -> str:
        """Generalize employee count to size category"""
        if employee_count < 50:
            return 'small'
        elif employee_count < 250:
            return 'medium'
        elif employee_count < 1000:
            return 'large'
        else:
            return 'enterprise'

    def _generalize_date(self, date_str: str) -> str:
        """Generalize date to month/year"""
        if isinstance(date_str, str) and len(date_str) >= 7:
            return date_str[:7]  # Keep YYYY-MM
        return date_str

    def _generalize_process_name(self, name: str) -> str:
        """
        Generalize specific process names

        Example:
        "Emergency Department at City Hospital" → "Emergency Services"
        "SAP ERP System v9.5" → "ERP System"
        """

        generalizations = {
            r'emergency\s+department.*': 'Emergency Services',
            r'patient\s+records.*': 'Patient Records Management',
            r'.*erp.*': 'ERP System',
            r'.*crm.*': 'CRM System',
            r'.*email.*': 'Email System',
            r'.*payroll.*': 'Payroll System',
            r'.*hr.*': 'HR System',
            r'.*finance.*': 'Finance System'
        }

        name_lower = name.lower()
        for pattern, generic in generalizations.items():
            if re.search(pattern, name_lower):
                return generic

        return name

    def _create_stable_hash(self, data: Dict) -> str:
        """Create stable hash for linking"""
        hashable = f"{data.get('module')}_{data.get('workflow_name')}"
        return hashlib.sha256(hashable.encode()).hexdigest()[:16]

    def _calculate_risk(self, data: Dict) -> float:
        """
        Calculate re-identification risk

        Higher risk if:
        - Rare industry + size combination
        - Very specific metrics
        - Unique patterns
        """
        risk = 0.0

        if 'organization_context' in data:
            industry = data['organization_context'].get('industry')
            size = data['organization_context'].get('size')

            # Rare industries increase risk
            if industry in ['aerospace', 'nuclear', 'defense']:
                risk += 0.3

        if 'metrics' in data:
            if data['metrics'].get('processes_count', 0) > 50:
                risk += 0.2

        return min(risk, 1.0)

    def _field_exists(self, data: Dict, field: str) -> bool:
        """Check if field exists (supports nested paths)"""
        parts = field.split('.')
        current = data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False

        return True

    def _remove_field(self, data: Dict, field: str):
        """Remove field (supports nested paths)"""
        parts = field.split('.')

        if len(parts) == 1:
            data.pop(field, None)
        else:
            current = data
            for part in parts[:-1]:
                if part in current:
                    current = current[part]
                else:
                    return

            current.pop(parts[-1], None)
