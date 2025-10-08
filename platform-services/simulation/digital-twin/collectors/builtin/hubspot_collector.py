"""
HubSpot Collector

Collects data from HubSpot CRM via REST API
"""

import logging
from typing import Dict, List, Optional, Any
from hubspot import HubSpot
from hubspot.crm.companies import ApiException as CompaniesApiException
from hubspot.crm.contacts import ApiException as ContactsApiException

from collectors.base import RESTCollector

logger = logging.getLogger(__name__)


class HubSpotCollector(RESTCollector):
    """
    HubSpot Data Collector

    Collects data from HubSpot CRM using hubspot-api-client
    """

    def __init__(
        self,
        credentials: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize HubSpot collector

        Required credentials:
            - api_key: HubSpot API key or access token
        """
        super().__init__(credentials, config)

        self._api_key = self.credentials.get('api_key')
        self._client = None

        # Entity type mapping
        self._entity_mapping = {
            'companies': 'companies',
            'contacts': 'contacts',
            'deals': 'deals',
            'products': 'products',
            'tickets': 'tickets',
        }

    @property
    def source_name(self) -> str:
        return "HubSpot"

    @property
    def supported_entities(self) -> List[str]:
        return list(self._entity_mapping.keys())

    async def connect(self) -> bool:
        """
        Connect to HubSpot

        Returns:
            True if connection successful
        """
        logger.info("Connecting to HubSpot")

        try:
            self._client = HubSpot(access_token=self._api_key)

            self._initialized = True

            logger.info("Connected to HubSpot")

            return True

        except Exception as e:
            logger.error(f"HubSpot connection failed: {e}", exc_info=True)
            raise ConnectionError(f"Failed to connect to HubSpot: {e}")

    async def disconnect(self) -> None:
        """Close HubSpot connection"""
        self._client = None
        self._initialized = False

        logger.info("Disconnected from HubSpot")

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test HubSpot connection

        Returns:
            Test results
        """
        try:
            # Try to get account details
            account_info = self._client.crm.owners.get_page()

            return {
                'status': 'success',
                'owners_count': len(account_info.results) if account_info.results else 0
            }

        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    async def collect(
        self,
        entity_type: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = 100,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect data from HubSpot

        Args:
            entity_type: Entity type to collect
            filters: Filter parameters
            limit: Maximum records
            offset: Starting offset (after token)

        Returns:
            List of collected records
        """
        await self.ensure_connected()

        if not self.is_entity_supported(entity_type):
            raise ValueError(f"Entity type not supported: {entity_type}")

        logger.info(f"Collecting {entity_type} from HubSpot")

        try:
            if entity_type == 'companies':
                records = await self._collect_companies(limit, offset)
            elif entity_type == 'contacts':
                records = await self._collect_contacts(limit, offset)
            elif entity_type == 'deals':
                records = await self._collect_deals(limit, offset)
            elif entity_type == 'products':
                records = await self._collect_products(limit, offset)
            elif entity_type == 'tickets':
                records = await self._collect_tickets(limit, offset)
            else:
                records = []

            logger.info(f"Collected {len(records)} {entity_type} records from HubSpot")

            # Normalize records
            normalized = [
                self.normalize_record(record, entity_type)
                for record in records
            ]

            return normalized

        except Exception as e:
            logger.error(f"Error collecting {entity_type} from HubSpot: {e}", exc_info=True)
            raise

    async def _collect_companies(
        self,
        limit: int = 100,
        after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Collect companies from HubSpot"""
        try:
            properties = [
                'name', 'domain', 'industry', 'annualrevenue', 'numberofemployees',
                'city', 'state', 'country', 'phone', 'website', 'description',
                'createdate', 'hs_lastmodifieddate'
            ]

            response = self._client.crm.companies.basic_api.get_page(
                limit=limit,
                after=after,
                properties=properties,
                archived=False
            )

            return [self._hubspot_obj_to_dict(company) for company in response.results]

        except CompaniesApiException as e:
            logger.error(f"Error collecting companies: {e}", exc_info=True)
            return []

    async def _collect_contacts(
        self,
        limit: int = 100,
        after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Collect contacts from HubSpot"""
        try:
            properties = [
                'firstname', 'lastname', 'email', 'phone', 'mobilephone',
                'jobtitle', 'company', 'city', 'state', 'country',
                'createdate', 'lastmodifieddate'
            ]

            response = self._client.crm.contacts.basic_api.get_page(
                limit=limit,
                after=after,
                properties=properties,
                archived=False
            )

            return [self._hubspot_obj_to_dict(contact) for contact in response.results]

        except ContactsApiException as e:
            logger.error(f"Error collecting contacts: {e}", exc_info=True)
            return []

    async def _collect_deals(
        self,
        limit: int = 100,
        after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Collect deals from HubSpot"""
        try:
            properties = [
                'dealname', 'amount', 'dealstage', 'pipeline', 'closedate',
                'createdate', 'hs_lastmodifieddate', 'hubspot_owner_id'
            ]

            response = self._client.crm.deals.basic_api.get_page(
                limit=limit,
                after=after,
                properties=properties,
                archived=False
            )

            return [self._hubspot_obj_to_dict(deal) for deal in response.results]

        except Exception as e:
            logger.error(f"Error collecting deals: {e}", exc_info=True)
            return []

    async def _collect_products(
        self,
        limit: int = 100,
        after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Collect products from HubSpot"""
        try:
            properties = [
                'name', 'description', 'price', 'hs_sku',
                'createdate', 'hs_lastmodifieddate'
            ]

            response = self._client.crm.products.basic_api.get_page(
                limit=limit,
                after=after,
                properties=properties,
                archived=False
            )

            return [self._hubspot_obj_to_dict(product) for product in response.results]

        except Exception as e:
            logger.error(f"Error collecting products: {e}", exc_info=True)
            return []

    async def _collect_tickets(
        self,
        limit: int = 100,
        after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Collect tickets from HubSpot"""
        try:
            properties = [
                'subject', 'content', 'hs_pipeline_stage', 'hs_ticket_priority',
                'createdate', 'hs_lastmodifieddate'
            ]

            response = self._client.crm.tickets.basic_api.get_page(
                limit=limit,
                after=after,
                properties=properties,
                archived=False
            )

            return [self._hubspot_obj_to_dict(ticket) for ticket in response.results]

        except Exception as e:
            logger.error(f"Error collecting tickets: {e}", exc_info=True)
            return []

    async def get_metadata(self, entity_type: str) -> Dict[str, Any]:
        """
        Get HubSpot object metadata

        Args:
            entity_type: Entity type

        Returns:
            Object metadata
        """
        await self.ensure_connected()

        if not self.is_entity_supported(entity_type):
            raise ValueError(f"Entity type not supported: {entity_type}")

        try:
            # Get object schema
            if entity_type == 'companies':
                schema = self._client.crm.companies.get_all()
            elif entity_type == 'contacts':
                schema = self._client.crm.contacts.get_all()
            elif entity_type == 'deals':
                schema = self._client.crm.deals.get_all()
            else:
                return {'entity_type': entity_type, 'fields': []}

            return {
                'entity_type': entity_type,
                'object_type': self._entity_mapping[entity_type]
            }

        except Exception as e:
            logger.error(f"Error getting metadata for {entity_type}: {e}", exc_info=True)
            return {}

    def _hubspot_obj_to_dict(self, obj: Any) -> Dict[str, Any]:
        """Convert HubSpot object to dictionary"""
        return {
            'id': obj.id,
            'properties': obj.properties,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
            'archived': obj.archived if hasattr(obj, 'archived') else False
        }

    def normalize_record(
        self,
        raw_record: Dict[str, Any],
        entity_type: str
    ) -> Dict[str, Any]:
        """
        Normalize HubSpot record to standard format

        Args:
            raw_record: Raw HubSpot record
            entity_type: Entity type

        Returns:
            Normalized record
        """
        # Extract properties
        props = raw_record.get('properties', {})
        record_id = raw_record.get('id')

        # Extract common fields
        normalized = {
            'source': self.source_name,
            'source_id': record_id,
            'entity_type': entity_type,
            'created_at': raw_record.get('created_at') or props.get('createdate'),
            'updated_at': raw_record.get('updated_at') or props.get('hs_lastmodifieddate'),
        }

        # Entity-specific normalization
        if entity_type == 'companies':
            normalized.update({
                'name': props.get('name'),
                'domain': props.get('domain'),
                'industry': props.get('industry'),
                'annual_revenue': self._parse_number(props.get('annualrevenue')),
                'employee_count': self._parse_number(props.get('numberofemployees')),
                'phone': props.get('phone'),
                'website': props.get('website'),
                'address': {
                    'city': props.get('city'),
                    'state': props.get('state'),
                    'country': props.get('country'),
                }
            })

        elif entity_type == 'contacts':
            normalized.update({
                'first_name': props.get('firstname'),
                'last_name': props.get('lastname'),
                'name': f"{props.get('firstname', '')} {props.get('lastname', '')}".strip(),
                'email': props.get('email'),
                'phone': props.get('phone'),
                'mobile': props.get('mobilephone'),
                'title': props.get('jobtitle'),
                'company': props.get('company'),
            })

        elif entity_type == 'deals':
            normalized.update({
                'name': props.get('dealname'),
                'amount': self._parse_number(props.get('amount')),
                'stage': props.get('dealstage'),
                'pipeline': props.get('pipeline'),
                'close_date': props.get('closedate'),
            })

        elif entity_type == 'products':
            normalized.update({
                'name': props.get('name'),
                'description': props.get('description'),
                'price': self._parse_number(props.get('price')),
                'sku': props.get('hs_sku'),
            })

        # Keep raw data for reference
        normalized['raw_data'] = raw_record

        return normalized

    def _parse_number(self, value: Any) -> Optional[float]:
        """Parse number from string or return None"""
        if value is None:
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            return None
