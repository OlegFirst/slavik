"""
Generic REST Collector

Collects data from any REST API with configurable endpoints
"""

import logging
import httpx
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

from collectors.base import RESTCollector

logger = logging.getLogger(__name__)


class GenericRESTCollector(RESTCollector):
    """
    Generic REST API Data Collector

    Flexible collector that can work with any REST API
    """

    def __init__(
        self,
        credentials: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Generic REST collector

        Required credentials:
            - base_url: Base URL of the API

        Optional credentials:
            - api_key: API key
            - api_key_header: Header name for API key (default: 'Authorization')
            - auth_type: 'bearer', 'basic', 'api_key', or 'none'
            - username: For basic auth
            - password: For basic auth

        Required config:
            - endpoints: Dict mapping entity types to endpoint paths
              Example: {'companies': '/api/companies', 'contacts': '/api/contacts'}

        Optional config:
            - pagination_type: 'offset', 'page', or 'cursor'
            - pagination_param: Parameter name for pagination (default: 'offset' or 'page')
            - limit_param: Parameter name for limit (default: 'limit')
            - response_data_path: JSON path to data array (default: root)
              Example: 'data.results' for response like {'data': {'results': [...]}}
        """
        super().__init__(credentials, config)

        # Parse configuration
        self._auth_type = self.credentials.get('auth_type', 'bearer')
        self._api_key = self.credentials.get('api_key')
        self._api_key_header = self.credentials.get('api_key_header', 'Authorization')
        self._username = self.credentials.get('username')
        self._password = self.credentials.get('password')

        # Endpoint configuration
        self._endpoints = self.config.get('endpoints', {})

        # Pagination configuration
        self._pagination_type = self.config.get('pagination_type', 'offset')
        self._pagination_param = self.config.get('pagination_param')
        if not self._pagination_param:
            self._pagination_param = 'page' if self._pagination_type == 'page' else 'offset'

        self._limit_param = self.config.get('limit_param', 'limit')
        self._response_data_path = self.config.get('response_data_path')

        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def source_name(self) -> str:
        return self.config.get('source_name', 'Generic REST API')

    @property
    def supported_entities(self) -> List[str]:
        return list(self._endpoints.keys())

    async def connect(self) -> bool:
        """
        Initialize HTTP client

        Returns:
            True if successful
        """
        logger.info(f"Initializing HTTP client for {self.source_name}")

        try:
            # Build headers
            headers = self._build_auth_headers()

            # Create HTTP client
            self._http_client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=headers,
                timeout=30.0
            )

            self._initialized = True

            logger.info(f"HTTP client initialized for {self.source_name}")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize HTTP client: {e}", exc_info=True)
            raise ConnectionError(f"Failed to initialize: {e}")

    async def disconnect(self) -> None:
        """Close HTTP client"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

        self._initialized = False

        logger.info("HTTP client closed")

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test API connection

        Returns:
            Test results
        """
        try:
            # Try to make a simple request to first endpoint
            if not self._endpoints:
                return {
                    'status': 'failed',
                    'error': 'No endpoints configured'
                }

            first_entity = list(self._endpoints.keys())[0]
            endpoint = self._endpoints[first_entity]

            response = await self._http_client.get(endpoint, params={'limit': 1})
            response.raise_for_status()

            return {
                'status': 'success',
                'status_code': response.status_code,
                'base_url': self._base_url
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
        Collect data from REST API

        Args:
            entity_type: Entity type to collect
            filters: Query parameters
            limit: Maximum records
            offset: Starting offset

        Returns:
            List of collected records
        """
        await self.ensure_connected()

        if not self.is_entity_supported(entity_type):
            raise ValueError(f"Entity type not supported: {entity_type}")

        endpoint = self._endpoints[entity_type]

        logger.info(f"Collecting {entity_type} from {endpoint}")

        try:
            # Build query parameters
            params = {}

            if filters:
                params.update(filters)

            if limit:
                params[self._limit_param] = limit

            if offset is not None:
                params[self._pagination_param] = offset

            # Make request
            response = await self._http_client.get(endpoint, params=params)
            response.raise_for_status()

            # Parse response
            data = response.json()

            # Extract records from response
            records = self._extract_records(data)

            logger.info(f"Collected {len(records)} {entity_type} records")

            # Normalize records
            normalized = [
                self.normalize_record(record, entity_type)
                for record in records
            ]

            return normalized

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error collecting {entity_type}: {e.response.status_code} - {e.response.text}",
                exc_info=True
            )
            raise

        except Exception as e:
            logger.error(f"Error collecting {entity_type}: {e}", exc_info=True)
            raise

    async def get_metadata(self, entity_type: str) -> Dict[str, Any]:
        """
        Get metadata for entity type

        Args:
            entity_type: Entity type

        Returns:
            Metadata dictionary
        """
        return {
            'entity_type': entity_type,
            'endpoint': self._endpoints.get(entity_type),
            'source': self.source_name
        }

    def _build_auth_headers(self) -> Dict[str, str]:
        """Build authentication headers"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if self._auth_type == 'bearer' and self._api_key:
            headers[self._api_key_header] = f'Bearer {self._api_key}'

        elif self._auth_type == 'api_key' and self._api_key:
            headers[self._api_key_header] = self._api_key

        elif self._auth_type == 'basic' and self._username and self._password:
            import base64
            credentials = base64.b64encode(
                f'{self._username}:{self._password}'.encode()
            ).decode()
            headers['Authorization'] = f'Basic {credentials}'

        return headers

    def _extract_records(self, data: Any) -> List[Dict[str, Any]]:
        """
        Extract records from API response

        Args:
            data: Response data

        Returns:
            List of records
        """
        # If no data path specified, assume data is the array
        if not self._response_data_path:
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Try common paths
                for key in ['data', 'results', 'items', 'records']:
                    if key in data:
                        value = data[key]
                        if isinstance(value, list):
                            return value
                # If no common key, return as single record
                return [data]
            else:
                return []

        # Navigate nested path (e.g., 'data.results')
        parts = self._response_data_path.split('.')
        current = data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                logger.warning(f"Could not navigate to {self._response_data_path}")
                return []

        if isinstance(current, list):
            return current
        else:
            return [current]

    def normalize_record(
        self,
        raw_record: Dict[str, Any],
        entity_type: str
    ) -> Dict[str, Any]:
        """
        Normalize record to standard format

        Args:
            raw_record: Raw record from API
            entity_type: Entity type

        Returns:
            Normalized record
        """
        # Try to extract common fields
        record_id = raw_record.get('id') or raw_record.get('_id') or raw_record.get('uuid')

        normalized = {
            'source': self.source_name,
            'source_id': str(record_id) if record_id else None,
            'entity_type': entity_type,
        }

        # Try to extract timestamps
        for created_field in ['created_at', 'createdAt', 'created', 'date_created']:
            if created_field in raw_record:
                normalized['created_at'] = raw_record[created_field]
                break

        for updated_field in ['updated_at', 'updatedAt', 'modified', 'last_modified']:
            if updated_field in raw_record:
                normalized['updated_at'] = raw_record[updated_field]
                break

        # Keep full raw data
        normalized['raw_data'] = raw_record

        return normalized
