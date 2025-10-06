"""
Odoo Collector

Collects data from Odoo ERP system via XML-RPC API
"""

import logging
import xmlrpc.client
from typing import Dict, List, Optional, Any

from collectors.base import DataCollector

logger = logging.getLogger(__name__)


class OdooCollector(DataCollector):
    """
    Odoo Data Collector

    Collects data from Odoo ERP using XML-RPC API
    """

    def __init__(
        self,
        credentials: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Odoo collector

        Required credentials:
            - url: Odoo server URL
            - db: Database name
            - username: Username
            - password: Password or API key
        """
        super().__init__(credentials, config)

        self._url = self.credentials.get('url')
        self._db = self.credentials.get('db')
        self._username = self.credentials.get('username')
        self._password = self.credentials.get('password')

        self._uid = None
        self._common_proxy = None
        self._object_proxy = None

        # Entity type to Odoo model mapping
        self._model_mapping = {
            'companies': 'res.partner',
            'contacts': 'res.partner',
            'projects': 'project.project',
            'tasks': 'project.task',
            'invoices': 'account.move',
            'products': 'product.product',
            'users': 'res.users',
            'leads': 'crm.lead',
            'opportunities': 'crm.lead',
        }

    @property
    def source_name(self) -> str:
        return "Odoo"

    @property
    def supported_entities(self) -> List[str]:
        return list(self._model_mapping.keys())

    async def connect(self) -> bool:
        """
        Connect to Odoo server

        Returns:
            True if connection successful
        """
        logger.info(f"Connecting to Odoo: {self._url}")

        try:
            # Create proxy objects
            self._common_proxy = xmlrpc.client.ServerProxy(
                f'{self._url}/xmlrpc/2/common'
            )

            # Authenticate
            self._uid = self._common_proxy.authenticate(
                self._db,
                self._username,
                self._password,
                {}
            )

            if not self._uid:
                raise ConnectionError("Authentication failed")

            # Create object proxy
            self._object_proxy = xmlrpc.client.ServerProxy(
                f'{self._url}/xmlrpc/2/object'
            )

            self._initialized = True

            logger.info(f"Connected to Odoo as user ID: {self._uid}")

            return True

        except Exception as e:
            logger.error(f"Odoo connection failed: {e}", exc_info=True)
            raise ConnectionError(f"Failed to connect to Odoo: {e}")

    async def disconnect(self) -> None:
        """Close Odoo connection"""
        # XML-RPC connections are stateless, nothing to close
        self._uid = None
        self._common_proxy = None
        self._object_proxy = None
        self._initialized = False

        logger.info("Disconnected from Odoo")

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test Odoo connection

        Returns:
            Test results
        """
        try:
            # Get server version
            version = self._common_proxy.version()

            return {
                'status': 'success',
                'server_version': version.get('server_version'),
                'protocol_version': version.get('protocol_version'),
                'database': self._db,
                'user_id': self._uid
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
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect data from Odoo

        Args:
            entity_type: Entity type to collect
            filters: Odoo domain filters
            limit: Maximum records
            offset: Starting offset

        Returns:
            List of collected records
        """
        await self.ensure_connected()

        if not self.is_entity_supported(entity_type):
            raise ValueError(f"Entity type not supported: {entity_type}")

        # Get Odoo model name
        model = self._model_mapping[entity_type]

        logger.info(f"Collecting {entity_type} ({model}) from Odoo")

        try:
            # Build domain (Odoo filters)
            domain = self._build_domain(entity_type, filters)

            # Get record IDs
            kwargs = {}
            if limit:
                kwargs['limit'] = limit
            if offset:
                kwargs['offset'] = offset

            record_ids = self._object_proxy.execute_kw(
                self._db,
                self._uid,
                self._password,
                model,
                'search',
                [domain],
                kwargs
            )

            if not record_ids:
                logger.info(f"No {entity_type} records found")
                return []

            # Get fields to read
            fields = self._get_fields_for_entity(entity_type)

            # Read records
            records = self._object_proxy.execute_kw(
                self._db,
                self._uid,
                self._password,
                model,
                'read',
                [record_ids],
                {'fields': fields}
            )

            logger.info(f"Collected {len(records)} {entity_type} records from Odoo")

            # Normalize records
            normalized = [
                self.normalize_record(record, entity_type)
                for record in records
            ]

            return normalized

        except Exception as e:
            logger.error(f"Error collecting {entity_type} from Odoo: {e}", exc_info=True)
            raise

    async def get_metadata(self, entity_type: str) -> Dict[str, Any]:
        """
        Get Odoo model metadata

        Args:
            entity_type: Entity type

        Returns:
            Model metadata
        """
        await self.ensure_connected()

        if not self.is_entity_supported(entity_type):
            raise ValueError(f"Entity type not supported: {entity_type}")

        model = self._model_mapping[entity_type]

        try:
            # Get model fields
            fields = self._object_proxy.execute_kw(
                self._db,
                self._uid,
                self._password,
                model,
                'fields_get',
                [],
                {'attributes': ['string', 'type', 'help', 'required']}
            )

            return {
                'model': model,
                'entity_type': entity_type,
                'fields': fields
            }

        except Exception as e:
            logger.error(f"Error getting metadata for {entity_type}: {e}", exc_info=True)
            return {}

    def _build_domain(
        self,
        entity_type: str,
        filters: Optional[Dict[str, Any]]
    ) -> List[Any]:
        """
        Build Odoo domain from filters

        Args:
            entity_type: Entity type
            filters: Filter dictionary

        Returns:
            Odoo domain list
        """
        domain = []

        # Add entity-specific filters
        if entity_type == 'companies':
            # Companies are partners that are not individuals
            domain.append(('is_company', '=', True))
        elif entity_type == 'contacts':
            # Contacts are individuals
            domain.append(('is_company', '=', False))
        elif entity_type == 'opportunities':
            # Opportunities are leads with type 'opportunity'
            domain.append(('type', '=', 'opportunity'))
        elif entity_type == 'leads':
            # Leads have type 'lead'
            domain.append(('type', '=', 'lead'))

        # Add custom filters
        if filters:
            for key, value in filters.items():
                if isinstance(value, dict):
                    # Handle operators: {'field': {'>=': 100}}
                    for op, val in value.items():
                        domain.append((key, op, val))
                else:
                    # Simple equality
                    domain.append((key, '=', value))

        return domain

    def _get_fields_for_entity(self, entity_type: str) -> List[str]:
        """
        Get fields to retrieve for entity type

        Args:
            entity_type: Entity type

        Returns:
            List of field names
        """
        # Common fields for all entities
        common_fields = ['id', 'create_date', 'write_date', 'create_uid', 'write_uid']

        # Entity-specific fields
        entity_fields = {
            'companies': [
                'name', 'email', 'phone', 'website', 'street', 'city', 'zip',
                'country_id', 'state_id', 'vat', 'company_type', 'industry_id'
            ],
            'contacts': [
                'name', 'email', 'phone', 'mobile', 'function', 'title',
                'parent_id', 'company_id'
            ],
            'projects': [
                'name', 'user_id', 'partner_id', 'date_start', 'date',
                'task_count', 'task_ids'
            ],
            'tasks': [
                'name', 'project_id', 'user_id', 'partner_id', 'date_deadline',
                'stage_id', 'priority', 'description'
            ],
            'invoices': [
                'name', 'partner_id', 'invoice_date', 'invoice_date_due',
                'amount_total', 'amount_untaxed', 'amount_tax', 'state',
                'move_type', 'payment_state'
            ],
            'products': [
                'name', 'default_code', 'list_price', 'standard_price',
                'type', 'categ_id', 'uom_id', 'active'
            ],
            'leads': [
                'name', 'partner_id', 'contact_name', 'email_from', 'phone',
                'stage_id', 'user_id', 'expected_revenue', 'probability', 'type'
            ],
            'opportunities': [
                'name', 'partner_id', 'contact_name', 'email_from', 'phone',
                'stage_id', 'user_id', 'expected_revenue', 'probability',
                'date_closed', 'type'
            ],
        }

        fields = common_fields.copy()
        fields.extend(entity_fields.get(entity_type, []))

        return fields

    def normalize_record(
        self,
        raw_record: Dict[str, Any],
        entity_type: str
    ) -> Dict[str, Any]:
        """
        Normalize Odoo record to standard format

        Args:
            raw_record: Raw Odoo record
            entity_type: Entity type

        Returns:
            Normalized record
        """
        # Extract ID
        record_id = raw_record.get('id')

        # Extract common fields
        normalized = {
            'source': self.source_name,
            'source_id': str(record_id),
            'entity_type': entity_type,
            'created_at': raw_record.get('create_date'),
            'updated_at': raw_record.get('write_date'),
        }

        # Entity-specific normalization
        if entity_type in ['companies', 'contacts']:
            normalized.update({
                'name': raw_record.get('name'),
                'email': raw_record.get('email'),
                'phone': raw_record.get('phone'),
                'address': {
                    'street': raw_record.get('street'),
                    'city': raw_record.get('city'),
                    'zip': raw_record.get('zip'),
                    'country': self._extract_many2one(raw_record.get('country_id')),
                    'state': self._extract_many2one(raw_record.get('state_id')),
                }
            })

            if entity_type == 'companies':
                normalized['is_company'] = True
                normalized['website'] = raw_record.get('website')
                normalized['vat'] = raw_record.get('vat')
                normalized['industry'] = self._extract_many2one(raw_record.get('industry_id'))

        elif entity_type == 'projects':
            normalized.update({
                'name': raw_record.get('name'),
                'partner': self._extract_many2one(raw_record.get('partner_id')),
                'start_date': raw_record.get('date_start'),
                'end_date': raw_record.get('date'),
                'task_count': raw_record.get('task_count', 0)
            })

        elif entity_type == 'invoices':
            normalized.update({
                'number': raw_record.get('name'),
                'partner': self._extract_many2one(raw_record.get('partner_id')),
                'date': raw_record.get('invoice_date'),
                'due_date': raw_record.get('invoice_date_due'),
                'amount_total': raw_record.get('amount_total'),
                'amount_tax': raw_record.get('amount_tax'),
                'state': raw_record.get('state'),
                'type': raw_record.get('move_type'),
            })

        # Keep raw data for reference
        normalized['raw_data'] = raw_record

        return normalized

    def _extract_many2one(self, value: Any) -> Optional[str]:
        """
        Extract name from Odoo many2one field

        Args:
            value: Many2one value (False, or [id, 'name'])

        Returns:
            Name string or None
        """
        if not value or value is False:
            return None

        if isinstance(value, (list, tuple)) and len(value) >= 2:
            return value[1]  # Return name

        return str(value)
