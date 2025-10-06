"""
Salesforce Collector

Collects data from Salesforce CRM via REST API
"""

import logging
from typing import Dict, List, Optional, Any
from simple_salesforce import Salesforce

from collectors.base import DataCollector

logger = logging.getLogger(__name__)


class SalesforceCollector(DataCollector):
    """
    Salesforce Data Collector

    Collects data from Salesforce CRM using simple-salesforce library
    """

    def __init__(
        self,
        credentials: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Salesforce collector

        Required credentials:
            - username: Salesforce username
            - password: Salesforce password
            - security_token: Salesforce security token
            - domain: Optional domain (default: 'login')
        """
        super().__init__(credentials, config)

        self._username = self.credentials.get('username')
        self._password = self.credentials.get('password')
        self._security_token = self.credentials.get('security_token')
        self._domain = self.credentials.get('domain', 'login')

        self._sf = None

        # Entity type to Salesforce object mapping
        self._object_mapping = {
            'accounts': 'Account',
            'contacts': 'Contact',
            'leads': 'Lead',
            'opportunities': 'Opportunity',
            'cases': 'Case',
            'campaigns': 'Campaign',
            'products': 'Product2',
            'tasks': 'Task',
            'events': 'Event',
        }

    @property
    def source_name(self) -> str:
        return "Salesforce"

    @property
    def supported_entities(self) -> List[str]:
        return list(self._object_mapping.keys())

    async def connect(self) -> bool:
        """
        Connect to Salesforce

        Returns:
            True if connection successful
        """
        logger.info("Connecting to Salesforce")

        try:
            self._sf = Salesforce(
                username=self._username,
                password=self._password,
                security_token=self._security_token,
                domain=self._domain
            )

            self._initialized = True

            logger.info(f"Connected to Salesforce (instance: {self._sf.sf_instance})")

            return True

        except Exception as e:
            logger.error(f"Salesforce connection failed: {e}", exc_info=True)
            raise ConnectionError(f"Failed to connect to Salesforce: {e}")

    async def disconnect(self) -> None:
        """Close Salesforce connection"""
        self._sf = None
        self._initialized = False

        logger.info("Disconnected from Salesforce")

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test Salesforce connection

        Returns:
            Test results
        """
        try:
            # Try to query user info
            user_info = self._sf.query("SELECT Id, Name, Username FROM User WHERE Id = '%s'" % self._sf.sf_instance)

            return {
                'status': 'success',
                'instance': self._sf.sf_instance,
                'api_version': self._sf.sf_version,
                'user_id': user_info['records'][0]['Id'] if user_info['records'] else None
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
        Collect data from Salesforce

        Args:
            entity_type: Entity type to collect
            filters: SOQL WHERE conditions
            limit: Maximum records
            offset: Starting offset

        Returns:
            List of collected records
        """
        await self.ensure_connected()

        if not self.is_entity_supported(entity_type):
            raise ValueError(f"Entity type not supported: {entity_type}")

        # Get Salesforce object name
        sf_object = self._object_mapping[entity_type]

        logger.info(f"Collecting {entity_type} ({sf_object}) from Salesforce")

        try:
            # Build SOQL query
            fields = self._get_fields_for_entity(entity_type)
            field_list = ', '.join(fields)

            soql = f"SELECT {field_list} FROM {sf_object}"

            # Add filters
            if filters:
                where_clause = self._build_where_clause(filters)
                if where_clause:
                    soql += f" WHERE {where_clause}"

            # Add limit and offset
            if limit:
                soql += f" LIMIT {limit}"
            if offset:
                soql += f" OFFSET {offset}"

            logger.info(f"SOQL: {soql}")

            # Execute query
            result = self._sf.query_all(soql)

            records = result['records']

            logger.info(f"Collected {len(records)} {entity_type} records from Salesforce")

            # Normalize records
            normalized = [
                self.normalize_record(record, entity_type)
                for record in records
            ]

            return normalized

        except Exception as e:
            logger.error(f"Error collecting {entity_type} from Salesforce: {e}", exc_info=True)
            raise

    async def get_metadata(self, entity_type: str) -> Dict[str, Any]:
        """
        Get Salesforce object metadata

        Args:
            entity_type: Entity type

        Returns:
            Object metadata
        """
        await self.ensure_connected()

        if not self.is_entity_supported(entity_type):
            raise ValueError(f"Entity type not supported: {entity_type}")

        sf_object = self._object_mapping[entity_type]

        try:
            # Get object description
            metadata = getattr(self._sf, sf_object).describe()

            return {
                'object': sf_object,
                'entity_type': entity_type,
                'label': metadata.get('label'),
                'fields': [
                    {
                        'name': field['name'],
                        'label': field['label'],
                        'type': field['type'],
                        'required': not field['nillable']
                    }
                    for field in metadata.get('fields', [])
                ]
            }

        except Exception as e:
            logger.error(f"Error getting metadata for {entity_type}: {e}", exc_info=True)
            return {}

    def _build_where_clause(self, filters: Dict[str, Any]) -> str:
        """
        Build SOQL WHERE clause from filters

        Args:
            filters: Filter dictionary

        Returns:
            WHERE clause string
        """
        conditions = []

        for key, value in filters.items():
            if isinstance(value, str):
                # String value
                conditions.append(f"{key} = '{value}'")
            elif isinstance(value, bool):
                # Boolean value
                conditions.append(f"{key} = {str(value).lower()}")
            elif isinstance(value, (int, float)):
                # Numeric value
                conditions.append(f"{key} = {value}")
            elif isinstance(value, dict):
                # Operator-based filter: {'field': {'>': 100}}
                for op, val in value.items():
                    if isinstance(val, str):
                        conditions.append(f"{key} {op} '{val}'")
                    else:
                        conditions.append(f"{key} {op} {val}")

        return ' AND '.join(conditions)

    def _get_fields_for_entity(self, entity_type: str) -> List[str]:
        """
        Get fields to retrieve for entity type

        Args:
            entity_type: Entity type

        Returns:
            List of field names
        """
        # Common fields
        common_fields = ['Id', 'CreatedDate', 'LastModifiedDate', 'IsDeleted']

        # Entity-specific fields
        entity_fields = {
            'accounts': [
                'Name', 'Type', 'Industry', 'AnnualRevenue', 'NumberOfEmployees',
                'Website', 'Phone', 'BillingStreet', 'BillingCity', 'BillingState',
                'BillingPostalCode', 'BillingCountry', 'Description', 'OwnerId'
            ],
            'contacts': [
                'FirstName', 'LastName', 'Name', 'Email', 'Phone', 'MobilePhone',
                'Title', 'Department', 'AccountId', 'OwnerId', 'MailingStreet',
                'MailingCity', 'MailingState', 'MailingPostalCode', 'MailingCountry'
            ],
            'leads': [
                'FirstName', 'LastName', 'Name', 'Company', 'Email', 'Phone',
                'Status', 'LeadSource', 'Industry', 'AnnualRevenue', 'NumberOfEmployees',
                'Rating', 'OwnerId', 'ConvertedAccountId', 'ConvertedContactId',
                'ConvertedOpportunityId', 'IsConverted'
            ],
            'opportunities': [
                'Name', 'AccountId', 'StageName', 'Amount', 'CloseDate',
                'Probability', 'Type', 'LeadSource', 'IsClosed', 'IsWon',
                'Description', 'OwnerId', 'ForecastCategory'
            ],
            'cases': [
                'CaseNumber', 'Subject', 'Status', 'Priority', 'Origin',
                'AccountId', 'ContactId', 'Description', 'IsClosed',
                'ClosedDate', 'OwnerId'
            ],
            'campaigns': [
                'Name', 'Type', 'Status', 'StartDate', 'EndDate',
                'ExpectedRevenue', 'BudgetedCost', 'ActualCost', 'NumberSent',
                'NumberOfLeads', 'NumberOfConvertedLeads', 'OwnerId'
            ],
            'products': [
                'Name', 'ProductCode', 'Description', 'IsActive', 'Family'
            ],
            'tasks': [
                'Subject', 'Status', 'Priority', 'ActivityDate', 'WhoId',
                'WhatId', 'Description', 'OwnerId', 'IsClosed'
            ],
            'events': [
                'Subject', 'StartDateTime', 'EndDateTime', 'WhoId', 'WhatId',
                'Description', 'Location', 'OwnerId'
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
        Normalize Salesforce record to standard format

        Args:
            raw_record: Raw Salesforce record
            entity_type: Entity type

        Returns:
            Normalized record
        """
        # Remove attributes metadata
        clean_record = {k: v for k, v in raw_record.items() if k != 'attributes'}

        # Extract ID
        record_id = clean_record.get('Id')

        # Extract common fields
        normalized = {
            'source': self.source_name,
            'source_id': record_id,
            'entity_type': entity_type,
            'created_at': clean_record.get('CreatedDate'),
            'updated_at': clean_record.get('LastModifiedDate'),
            'is_deleted': clean_record.get('IsDeleted', False)
        }

        # Entity-specific normalization
        if entity_type == 'accounts':
            normalized.update({
                'name': clean_record.get('Name'),
                'type': clean_record.get('Type'),
                'industry': clean_record.get('Industry'),
                'annual_revenue': clean_record.get('AnnualRevenue'),
                'employee_count': clean_record.get('NumberOfEmployees'),
                'website': clean_record.get('Website'),
                'phone': clean_record.get('Phone'),
                'address': {
                    'street': clean_record.get('BillingStreet'),
                    'city': clean_record.get('BillingCity'),
                    'state': clean_record.get('BillingState'),
                    'postal_code': clean_record.get('BillingPostalCode'),
                    'country': clean_record.get('BillingCountry'),
                }
            })

        elif entity_type == 'contacts':
            normalized.update({
                'name': clean_record.get('Name'),
                'first_name': clean_record.get('FirstName'),
                'last_name': clean_record.get('LastName'),
                'email': clean_record.get('Email'),
                'phone': clean_record.get('Phone'),
                'mobile': clean_record.get('MobilePhone'),
                'title': clean_record.get('Title'),
                'department': clean_record.get('Department'),
                'account_id': clean_record.get('AccountId'),
            })

        elif entity_type == 'leads':
            normalized.update({
                'name': clean_record.get('Name'),
                'company': clean_record.get('Company'),
                'email': clean_record.get('Email'),
                'phone': clean_record.get('Phone'),
                'status': clean_record.get('Status'),
                'source': clean_record.get('LeadSource'),
                'is_converted': clean_record.get('IsConverted', False),
            })

        elif entity_type == 'opportunities':
            normalized.update({
                'name': clean_record.get('Name'),
                'account_id': clean_record.get('AccountId'),
                'stage': clean_record.get('StageName'),
                'amount': clean_record.get('Amount'),
                'close_date': clean_record.get('CloseDate'),
                'probability': clean_record.get('Probability'),
                'is_won': clean_record.get('IsWon', False),
                'is_closed': clean_record.get('IsClosed', False),
            })

        # Keep raw data for reference
        normalized['raw_data'] = clean_record

        return normalized
