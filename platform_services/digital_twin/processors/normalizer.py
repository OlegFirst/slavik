"""
Data Normalizer

Normalizes data from different sources to canonical schema
Based on organization-data-collector.js quality scoring and validation logic
"""

import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum

from core.models.base import Organization, DataSourceType

logger = logging.getLogger(__name__)


# ============================================
# CANONICAL SCHEMAS
# ============================================

class EntityType(str, Enum):
    """Canonical entity types"""
    ORGANIZATION = "organization"
    PERSON = "person"
    CONTACT = "contact"
    TRANSACTION = "transaction"
    EVENT = "event"
    METRIC = "metric"
    DOCUMENT = "document"


class DataQuality(str, Enum):
    """Data quality levels (from organization_data_collector.js)"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    INCOMPLETE = "incomplete"


# ============================================
# CANONICAL FIELD MAPPINGS
# ============================================

class CanonicalFieldMapping:
    """
    Canonical field mappings for different sources

    Based on existing digital-twin-platform normalization logic
    """

    # Organization fields mapping
    ORGANIZATION_FIELDS = {
        'id': ['id', '_id', 'org_id', 'organization_id', 'company_id'],
        'name': ['name', 'company_name', 'organization_name', 'legal_name'],
        'email': ['email', 'contact_email', 'primary_email', 'email_address'],
        'phone': ['phone', 'telephone', 'phone_number', 'contact_phone'],
        'website': ['website', 'url', 'web', 'domain', 'homepage'],
        'industry': ['industry', 'sector', 'vertical', 'industry_code'],
        'employee_count': ['employees', 'employee_count', 'staff_count', 'numberofemployees'],
        'annual_revenue': ['revenue', 'annual_revenue', 'annualrevenue', 'yearly_revenue'],
        'address': ['address', 'street', 'location'],
        'city': ['city', 'town', 'locality'],
        'state': ['state', 'province', 'region'],
        'country': ['country', 'country_code'],
        'postal_code': ['postal_code', 'zip', 'zipcode', 'postcode'],
    }

    # Person/Contact fields mapping
    PERSON_FIELDS = {
        'id': ['id', '_id', 'contact_id', 'person_id'],
        'first_name': ['first_name', 'firstname', 'given_name', 'fname'],
        'last_name': ['last_name', 'lastname', 'surname', 'family_name', 'lname'],
        'full_name': ['name', 'full_name', 'fullname', 'display_name'],
        'email': ['email', 'email_address', 'primary_email'],
        'phone': ['phone', 'telephone', 'mobile', 'phone_number'],
        'title': ['title', 'job_title', 'position', 'role', 'jobtitle'],
        'company': ['company', 'organization', 'company_name'],
        'department': ['department', 'dept', 'division'],
    }

    # Transaction fields mapping
    TRANSACTION_FIELDS = {
        'id': ['id', '_id', 'transaction_id', 'invoice_id'],
        'amount': ['amount', 'total', 'value', 'sum'],
        'currency': ['currency', 'currency_code'],
        'date': ['date', 'transaction_date', 'created_date', 'invoice_date'],
        'type': ['type', 'transaction_type', 'category'],
        'status': ['status', 'state', 'payment_status'],
        'description': ['description', 'memo', 'notes'],
    }


# ============================================
# DATA NORMALIZER
# ============================================

class DataNormalizer:
    """
    Data Normalizer

    Normalizes raw data from various sources to canonical schema
    Implements quality scoring from organization_data_collector.js
    """

    def __init__(self):
        """Initialize normalizer"""
        self.field_mappings = {
            EntityType.ORGANIZATION: CanonicalFieldMapping.ORGANIZATION_FIELDS,
            EntityType.PERSON: CanonicalFieldMapping.PERSON_FIELDS,
            EntityType.CONTACT: CanonicalFieldMapping.PERSON_FIELDS,
            EntityType.TRANSACTION: CanonicalFieldMapping.TRANSACTION_FIELDS,
        }

        # Source-specific transformers
        self.source_transformers: Dict[DataSourceType, Any] = {}

        logger.info("Data Normalizer initialized")

    async def normalize(
        self,
        raw_data: Dict[str, Any],
        source_type: DataSourceType,
        entity_type: EntityType
    ) -> Dict[str, Any]:
        """
        Normalize raw data to canonical schema

        Args:
            raw_data: Raw data from source
            source_type: Data source type
            entity_type: Entity type

        Returns:
            Normalized data dictionary
        """
        logger.info(f"Normalizing {entity_type.value} from {source_type.value}")

        try:
            # Get field mapping for entity type
            field_mapping = self.field_mappings.get(entity_type, {})

            # Extract and map fields
            normalized = {}

            for canonical_field, source_fields in field_mapping.items():
                value = self._extract_field(raw_data, source_fields)
                if value is not None:
                    # Apply type conversion
                    normalized[canonical_field] = self._convert_type(
                        canonical_field,
                        value,
                        entity_type
                    )

            # Add metadata
            normalized['_metadata'] = {
                'source': source_type.value,
                'entity_type': entity_type.value,
                'normalized_at': datetime.utcnow().isoformat(),
                'quality': self._assess_quality(normalized, entity_type).value
            }

            # Keep original data for reference
            normalized['_raw'] = raw_data

            logger.info(f"Normalized {entity_type.value}: quality={normalized['_metadata']['quality']}")

            return normalized

        except Exception as e:
            logger.error(f"Normalization failed: {e}", exc_info=True)
            raise

    async def normalize_batch(
        self,
        records: List[Dict[str, Any]],
        source_type: DataSourceType,
        entity_type: EntityType
    ) -> List[Dict[str, Any]]:
        """
        Normalize batch of records

        Args:
            records: List of raw records
            source_type: Data source type
            entity_type: Entity type

        Returns:
            List of normalized records
        """
        logger.info(f"Normalizing batch of {len(records)} {entity_type.value} records")

        normalized_records = []

        for record in records:
            try:
                normalized = await self.normalize(record, source_type, entity_type)
                normalized_records.append(normalized)
            except Exception as e:
                logger.error(f"Failed to normalize record: {e}")
                # Continue with other records
                continue

        logger.info(f"Successfully normalized {len(normalized_records)}/{len(records)} records")

        return normalized_records

    def _extract_field(
        self,
        data: Dict[str, Any],
        possible_fields: List[str]
    ) -> Optional[Any]:
        """
        Extract field value from data using multiple possible field names

        Args:
            data: Source data
            possible_fields: List of possible field names

        Returns:
            Field value or None
        """
        for field_name in possible_fields:
            # Try direct access
            if field_name in data:
                return data[field_name]

            # Try case-insensitive access
            for key in data.keys():
                if key.lower() == field_name.lower():
                    return data[key]

        return None

    def _convert_type(
        self,
        field_name: str,
        value: Any,
        entity_type: EntityType
    ) -> Any:
        """
        Convert field value to appropriate type

        Args:
            field_name: Field name
            value: Raw value
            entity_type: Entity type

        Returns:
            Converted value
        """
        # Skip empty values
        if value is None or value == '' or value == 'null':
            return None

        # Numeric fields
        if field_name in ['employee_count', 'annual_revenue', 'amount']:
            try:
                # Remove currency symbols and commas
                if isinstance(value, str):
                    value = value.replace('$', '').replace(',', '').strip()
                return float(value)
            except (ValueError, TypeError):
                return None

        # Boolean fields
        if field_name in ['is_company', 'active', 'verified']:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ['true', '1', 'yes', 'y']
            return bool(value)

        # Date fields
        if field_name in ['date', 'created_at', 'updated_at']:
            if isinstance(value, datetime):
                return value.isoformat()
            if isinstance(value, str):
                return value  # Keep as string, will be parsed later
            return None

        # String fields (default)
        return str(value).strip() if value else None

    def _assess_quality(
        self,
        normalized: Dict[str, Any],
        entity_type: EntityType
    ) -> DataQuality:
        """
        Assess data quality (based on organization-data-collector.js)

        Args:
            normalized: Normalized data
            entity_type: Entity type

        Returns:
            Quality level
        """
        # Required fields by entity type
        required_fields = {
            EntityType.ORGANIZATION: ['name'],
            EntityType.PERSON: ['full_name', 'email'],
            EntityType.CONTACT: ['full_name', 'email'],
            EntityType.TRANSACTION: ['amount', 'date'],
        }

        # Recommended fields by entity type
        recommended_fields = {
            EntityType.ORGANIZATION: ['email', 'phone', 'address', 'city', 'country'],
            EntityType.PERSON: ['phone', 'company', 'title'],
            EntityType.CONTACT: ['phone', 'company', 'title'],
            EntityType.TRANSACTION: ['type', 'status', 'description'],
        }

        entity_required = required_fields.get(entity_type, [])
        entity_recommended = recommended_fields.get(entity_type, [])

        # Check required fields
        missing_required = sum(1 for f in entity_required if f not in normalized or not normalized[f])
        if missing_required > 0:
            return DataQuality.INCOMPLETE

        # Calculate completeness
        present_recommended = sum(1 for f in entity_recommended if f in normalized and normalized[f])
        total_recommended = len(entity_recommended)

        if total_recommended == 0:
            completeness = 1.0
        else:
            completeness = present_recommended / total_recommended

        # Determine quality level
        if completeness >= 0.9:
            return DataQuality.EXCELLENT
        elif completeness >= 0.7:
            return DataQuality.GOOD
        elif completeness >= 0.5:
            return DataQuality.ACCEPTABLE
        else:
            return DataQuality.POOR

    def register_source_transformer(
        self,
        source_type: DataSourceType,
        transformer: Any
    ) -> None:
        """
        Register custom transformer for specific source

        Args:
            source_type: Data source type
            transformer: Transformer function or class
        """
        self.source_transformers[source_type] = transformer
        logger.info(f"Registered transformer for {source_type.value}")

    def get_field_mapping(
        self,
        entity_type: EntityType
    ) -> Dict[str, List[str]]:
        """
        Get field mapping for entity type

        Args:
            entity_type: Entity type

        Returns:
            Field mapping dictionary
        """
        return self.field_mappings.get(entity_type, {})

    def add_field_mapping(
        self,
        entity_type: EntityType,
        canonical_field: str,
        source_fields: List[str]
    ) -> None:
        """
        Add custom field mapping

        Args:
            entity_type: Entity type
            canonical_field: Canonical field name
            source_fields: List of source field names
        """
        if entity_type not in self.field_mappings:
            self.field_mappings[entity_type] = {}

        self.field_mappings[entity_type][canonical_field] = source_fields
        logger.info(f"Added field mapping: {canonical_field} for {entity_type.value}")

    async def validate_normalized(
        self,
        normalized: Dict[str, Any],
        entity_type: EntityType
    ) -> Dict[str, Any]:
        """
        Validate normalized data

        Args:
            normalized: Normalized data
            entity_type: Entity type

        Returns:
            Validation result with errors if any
        """
        errors = []
        warnings = []

        # Check required fields
        if entity_type == EntityType.ORGANIZATION:
            if not normalized.get('name'):
                errors.append("Missing required field: name")

        elif entity_type in [EntityType.PERSON, EntityType.CONTACT]:
            if not normalized.get('full_name') and not (normalized.get('first_name') and normalized.get('last_name')):
                errors.append("Missing required field: name")
            if not normalized.get('email'):
                warnings.append("Missing recommended field: email")

        # Check data types
        if 'employee_count' in normalized:
            if not isinstance(normalized['employee_count'], (int, float)):
                errors.append("Invalid type for employee_count")

        if 'annual_revenue' in normalized:
            if not isinstance(normalized['annual_revenue'], (int, float)):
                errors.append("Invalid type for annual_revenue")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'quality': normalized.get('_metadata', {}).get('quality', 'unknown')
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get normalizer statistics

        Returns:
            Statistics dictionary
        """
        return {
            'registered_entity_types': len(self.field_mappings),
            'registered_transformers': len(self.source_transformers),
            'entity_types': [et.value for et in self.field_mappings.keys()]
        }
