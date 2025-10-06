"""
Abstract Base Collector

Defines interface for all data collectors
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================
# ENUMS
# ============================================

class CollectionStatus(str, Enum):
    """Collection operation status"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class EntityType(str, Enum):
    """Standard entity types across all sources"""
    ORGANIZATION = "organization"
    CONTACT = "contact"
    LEAD = "lead"
    OPPORTUNITY = "opportunity"
    ACCOUNT = "account"
    PROJECT = "project"
    TASK = "task"
    INVOICE = "invoice"
    PAYMENT = "payment"
    PRODUCT = "product"
    CUSTOM = "custom"


# ============================================
# COLLECTION RESULT
# ============================================

class CollectionResult:
    """Result of a collection operation"""

    def __init__(
        self,
        entity_type: str,
        status: CollectionStatus,
        records: List[Dict[str, Any]],
        total_count: Optional[int] = None,
        errors: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.entity_type = entity_type
        self.status = status
        self.records = records
        self.total_count = total_count or len(records)
        self.errors = errors or []
        self.metadata = metadata or {}
        self.collected_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'entity_type': self.entity_type,
            'status': self.status.value,
            'records': self.records,
            'total_count': self.total_count,
            'collected_count': len(self.records),
            'errors': self.errors,
            'metadata': self.metadata,
            'collected_at': self.collected_at.isoformat()
        }


# ============================================
# ABSTRACT BASE COLLECTOR
# ============================================

class DataCollector(ABC):
    """
    Abstract Base Class for Data Collectors

    All collectors must implement this interface
    """

    def __init__(
        self,
        credentials: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize collector

        Args:
            credentials: Authentication credentials
            config: Additional configuration
        """
        self.credentials = credentials or {}
        self.config = config or {}
        self._initialized = False
        self._connection = None

        logger.info(f"Initializing {self.__class__.__name__}")

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return source system name"""
        pass

    @property
    @abstractmethod
    def supported_entities(self) -> List[str]:
        """Return list of supported entity types"""
        pass

    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to data source

        Returns:
            True if connection successful

        Raises:
            ConnectionError: If connection fails
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to data source"""
        pass

    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to data source

        Returns:
            Dictionary with connection test results
        """
        pass

    @abstractmethod
    async def collect(
        self,
        entity_type: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect data from source

        Args:
            entity_type: Type of entity to collect
            filters: Optional filters
            limit: Maximum number of records
            offset: Starting offset for pagination

        Returns:
            List of collected records

        Raises:
            ValueError: If entity_type not supported
            Exception: If collection fails
        """
        pass

    @abstractmethod
    async def get_metadata(
        self,
        entity_type: str
    ) -> Dict[str, Any]:
        """
        Get metadata about entity type

        Args:
            entity_type: Entity type

        Returns:
            Metadata dictionary with schema information
        """
        pass

    # ============================================
    # COMMON HELPER METHODS
    # ============================================

    async def ensure_connected(self) -> None:
        """Ensure connection is established"""
        if not self._initialized:
            await self.connect()
            self._initialized = True

    def is_entity_supported(self, entity_type: str) -> bool:
        """Check if entity type is supported"""
        return entity_type in self.supported_entities

    async def collect_all(
        self,
        entity_types: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, CollectionResult]:
        """
        Collect data for multiple entity types

        Args:
            entity_types: List of entity types (default: all supported)
            filters: Optional filters

        Returns:
            Dictionary of collection results by entity type
        """
        logger.info(f"Collecting from {self.source_name}")

        # Use all supported entities if not specified
        if entity_types is None:
            entity_types = self.supported_entities

        results = {}

        for entity_type in entity_types:
            if not self.is_entity_supported(entity_type):
                logger.warning(
                    f"Entity type {entity_type} not supported by {self.source_name}"
                )
                results[entity_type] = CollectionResult(
                    entity_type=entity_type,
                    status=CollectionStatus.FAILED,
                    records=[],
                    errors=[f"Entity type not supported: {entity_type}"]
                )
                continue

            try:
                logger.info(f"Collecting {entity_type} from {self.source_name}")

                records = await self.collect(entity_type, filters=filters)

                results[entity_type] = CollectionResult(
                    entity_type=entity_type,
                    status=CollectionStatus.SUCCESS,
                    records=records,
                    total_count=len(records)
                )

                logger.info(f"Collected {len(records)} {entity_type} records")

            except Exception as e:
                logger.error(
                    f"Error collecting {entity_type} from {self.source_name}: {e}",
                    exc_info=True
                )

                results[entity_type] = CollectionResult(
                    entity_type=entity_type,
                    status=CollectionStatus.FAILED,
                    records=[],
                    errors=[str(e)]
                )

        return results

    async def collect_with_pagination(
        self,
        entity_type: str,
        filters: Optional[Dict[str, Any]] = None,
        page_size: int = 100,
        max_pages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect data with pagination

        Args:
            entity_type: Entity type to collect
            filters: Optional filters
            page_size: Records per page
            max_pages: Maximum pages to fetch

        Returns:
            All collected records
        """
        logger.info(f"Collecting {entity_type} with pagination (page_size={page_size})")

        all_records = []
        page = 0
        offset = 0

        while True:
            # Check max_pages limit
            if max_pages and page >= max_pages:
                logger.info(f"Reached max_pages limit: {max_pages}")
                break

            # Collect page
            records = await self.collect(
                entity_type,
                filters=filters,
                limit=page_size,
                offset=offset
            )

            if not records:
                logger.info(f"No more records, collected {len(all_records)} total")
                break

            all_records.extend(records)
            page += 1
            offset += page_size

            logger.info(f"Page {page}: collected {len(records)} records")

            # If we got fewer records than page_size, we're done
            if len(records) < page_size:
                logger.info(f"Last page reached, collected {len(all_records)} total")
                break

        return all_records

    def normalize_record(
        self,
        raw_record: Dict[str, Any],
        entity_type: str
    ) -> Dict[str, Any]:
        """
        Normalize raw record to standard format

        Can be overridden by subclasses for custom normalization

        Args:
            raw_record: Raw record from source
            entity_type: Entity type

        Returns:
            Normalized record
        """
        # Default: return as-is with metadata
        return {
            'source': self.source_name,
            'entity_type': entity_type,
            'raw_data': raw_record,
            'collected_at': datetime.utcnow().isoformat()
        }

    def get_info(self) -> Dict[str, Any]:
        """
        Get collector information

        Returns:
            Collector information dictionary
        """
        return {
            'name': self.__class__.__name__,
            'source': self.source_name,
            'supported_entities': self.supported_entities,
            'initialized': self._initialized,
            'has_credentials': bool(self.credentials)
        }

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


# ============================================
# BASE IMPLEMENTATIONS
# ============================================

class RESTCollector(DataCollector):
    """
    Base class for REST API collectors

    Provides common REST functionality
    """

    def __init__(
        self,
        credentials: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(credentials, config)

        # HTTP client (to be initialized)
        self._http_client = None
        self._base_url = credentials.get('base_url') if credentials else None
        self._headers = {}

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        if not self._base_url:
            raise ValueError("base_url not configured")

        base = self._base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')

        return f"{base}/{endpoint}"

    def _build_headers(
        self,
        additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Build request headers"""
        headers = self._headers.copy()

        if additional_headers:
            headers.update(additional_headers)

        return headers


class DatabaseCollector(DataCollector):
    """
    Base class for database collectors

    Provides common database functionality
    """

    def __init__(
        self,
        credentials: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(credentials, config)

        # Database connection
        self._db_connection = None
        self._connection_string = credentials.get('connection_string') if credentials else None

    async def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute database query

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Query results
        """
        await self.ensure_connected()

        if not self._db_connection:
            raise ConnectionError("Database not connected")

        # Implementation depends on database type
        # Subclasses should override
        raise NotImplementedError("execute_query must be implemented by subclass")


class FileCollector(DataCollector):
    """
    Base class for file-based collectors

    Provides common file functionality
    """

    def __init__(
        self,
        credentials: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(credentials, config)

        self._file_path = config.get('file_path') if config else None

    async def read_file(self) -> Any:
        """
        Read file content

        Returns:
            File content
        """
        if not self._file_path:
            raise ValueError("file_path not configured")

        # Implementation depends on file type
        # Subclasses should override
        raise NotImplementedError("read_file must be implemented by subclass")
