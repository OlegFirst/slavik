"""
Database Collector

Collects data from databases via SQL queries
"""

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from collectors.base import DatabaseCollector as BaseDBCollector

logger = logging.getLogger(__name__)


class DatabaseCollector(BaseDBCollector):
    """
    Database Data Collector

    Collects data from SQL databases (PostgreSQL, MySQL, etc.)
    """

    def __init__(
        self,
        credentials: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Database collector

        Required credentials:
            - connection_string: SQLAlchemy connection string
              Examples:
                - postgresql+asyncpg://user:pass@localhost/dbname
                - mysql+aiomysql://user:pass@localhost/dbname
                - sqlite+aiosqlite:///path/to/database.db

        Required config:
            - queries: Dict mapping entity types to SQL queries
              Example: {
                  'companies': 'SELECT * FROM companies',
                  'contacts': 'SELECT * FROM contacts WHERE active = true'
              }

        Optional config:
            - id_column: Name of ID column (default: 'id')
            - created_column: Name of created timestamp column
            - updated_column: Name of updated timestamp column
        """
        super().__init__(credentials, config)

        # SQL queries for each entity type
        self._queries = self.config.get('queries', {})

        # Column name mapping
        self._id_column = self.config.get('id_column', 'id')
        self._created_column = self.config.get('created_column', 'created_at')
        self._updated_column = self.config.get('updated_column', 'updated_at')

        # SQLAlchemy components
        self._engine = None
        self._session_maker = None

    @property
    def source_name(self) -> str:
        return "Database"

    @property
    def supported_entities(self) -> List[str]:
        return list(self._queries.keys())

    async def connect(self) -> bool:
        """
        Connect to database

        Returns:
            True if connection successful
        """
        logger.info("Connecting to database")

        try:
            if not self._connection_string:
                raise ValueError("connection_string not provided")

            # Create async engine
            self._engine = create_async_engine(
                self._connection_string,
                echo=False,
                pool_pre_ping=True
            )

            # Create session maker
            self._session_maker = sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            # Test connection
            async with self._session_maker() as session:
                await session.execute(text("SELECT 1"))

            self._db_connection = self._engine
            self._initialized = True

            logger.info("Connected to database")

            return True

        except Exception as e:
            logger.error(f"Database connection failed: {e}", exc_info=True)
            raise ConnectionError(f"Failed to connect to database: {e}")

    async def disconnect(self) -> None:
        """Close database connection"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None

        self._session_maker = None
        self._db_connection = None
        self._initialized = False

        logger.info("Disconnected from database")

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test database connection

        Returns:
            Test results
        """
        try:
            async with self._session_maker() as session:
                result = await session.execute(text("SELECT 1 as test"))
                row = result.fetchone()

            return {
                'status': 'success',
                'test_query': 'SELECT 1',
                'result': row[0] if row else None
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
        Collect data from database

        Args:
            entity_type: Entity type to collect
            filters: SQL WHERE conditions (applied after base query)
            limit: Maximum records
            offset: Starting offset

        Returns:
            List of collected records
        """
        await self.ensure_connected()

        if not self.is_entity_supported(entity_type):
            raise ValueError(f"Entity type not supported: {entity_type}")

        base_query = self._queries[entity_type]

        logger.info(f"Collecting {entity_type} from database")

        try:
            # Build complete query
            query = self._build_query(base_query, filters, limit, offset)

            logger.info(f"Executing query: {query}")

            # Execute query
            records = await self.execute_query(query)

            logger.info(f"Collected {len(records)} {entity_type} records from database")

            # Normalize records
            normalized = [
                self.normalize_record(record, entity_type)
                for record in records
            ]

            return normalized

        except Exception as e:
            logger.error(f"Error collecting {entity_type} from database: {e}", exc_info=True)
            raise

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
            Query results as list of dicts
        """
        await self.ensure_connected()

        try:
            async with self._session_maker() as session:
                if params:
                    result = await session.execute(text(query), params)
                else:
                    result = await session.execute(text(query))

                # Convert rows to dicts
                records = []
                for row in result:
                    # Get column names
                    columns = result.keys()
                    # Create dict from row
                    record = dict(zip(columns, row))
                    records.append(record)

                return records

        except Exception as e:
            logger.error(f"Query execution failed: {e}", exc_info=True)
            raise

    async def get_metadata(self, entity_type: str) -> Dict[str, Any]:
        """
        Get database table metadata

        Args:
            entity_type: Entity type

        Returns:
            Metadata dictionary
        """
        await self.ensure_connected()

        if not self.is_entity_supported(entity_type):
            raise ValueError(f"Entity type not supported: {entity_type}")

        base_query = self._queries[entity_type]

        try:
            # Extract table name from query (simple heuristic)
            table_name = self._extract_table_name(base_query)

            return {
                'entity_type': entity_type,
                'table': table_name,
                'base_query': base_query,
                'id_column': self._id_column,
                'created_column': self._created_column,
                'updated_column': self._updated_column
            }

        except Exception as e:
            logger.error(f"Error getting metadata for {entity_type}: {e}", exc_info=True)
            return {}

    def _build_query(
        self,
        base_query: str,
        filters: Optional[Dict[str, Any]],
        limit: Optional[int],
        offset: Optional[int]
    ) -> str:
        """
        Build complete SQL query with filters, limit, and offset

        Args:
            base_query: Base SELECT query
            filters: Filter conditions
            limit: Record limit
            offset: Record offset

        Returns:
            Complete SQL query
        """
        query = base_query.strip()

        # Add WHERE clause for filters
        if filters:
            where_clause = self._build_where_clause(filters)

            if where_clause:
                # Check if query already has WHERE
                if 'WHERE' in query.upper():
                    query += f" AND {where_clause}"
                else:
                    query += f" WHERE {where_clause}"

        # Add ORDER BY if not present (needed for consistent pagination)
        if 'ORDER BY' not in query.upper():
            query += f" ORDER BY {self._id_column}"

        # Add LIMIT and OFFSET
        if limit:
            query += f" LIMIT {limit}"

        if offset:
            query += f" OFFSET {offset}"

        return query

    def _build_where_clause(self, filters: Dict[str, Any]) -> str:
        """
        Build WHERE clause from filters

        Args:
            filters: Filter dictionary

        Returns:
            WHERE clause (without WHERE keyword)
        """
        conditions = []

        for key, value in filters.items():
            if isinstance(value, str):
                # String value - use quotes
                conditions.append(f"{key} = '{value}'")
            elif isinstance(value, bool):
                # Boolean value
                conditions.append(f"{key} = {value}")
            elif isinstance(value, (int, float)):
                # Numeric value
                conditions.append(f"{key} = {value}")
            elif value is None:
                # NULL value
                conditions.append(f"{key} IS NULL")
            elif isinstance(value, dict):
                # Operator-based filter: {'field': {'>': 100}}
                for op, val in value.items():
                    if isinstance(val, str):
                        conditions.append(f"{key} {op} '{val}'")
                    else:
                        conditions.append(f"{key} {op} {val}")

        return ' AND '.join(conditions)

    def _extract_table_name(self, query: str) -> Optional[str]:
        """
        Extract table name from SELECT query

        Args:
            query: SQL query

        Returns:
            Table name or None
        """
        # Simple extraction: find word after FROM
        query_upper = query.upper()
        from_index = query_upper.find('FROM')

        if from_index == -1:
            return None

        # Get text after FROM
        after_from = query[from_index + 4:].strip()

        # Get first word (table name)
        table_name = after_from.split()[0]

        # Remove trailing characters like comma, parenthesis, etc.
        table_name = table_name.split(',')[0].split('(')[0].split(')')[0]

        return table_name.strip()

    def normalize_record(
        self,
        raw_record: Dict[str, Any],
        entity_type: str
    ) -> Dict[str, Any]:
        """
        Normalize database record to standard format

        Args:
            raw_record: Raw database row as dict
            entity_type: Entity type

        Returns:
            Normalized record
        """
        # Extract standard fields
        record_id = raw_record.get(self._id_column)
        created_at = raw_record.get(self._created_column)
        updated_at = raw_record.get(self._updated_column)

        normalized = {
            'source': self.source_name,
            'source_id': str(record_id) if record_id else None,
            'entity_type': entity_type,
        }

        if created_at:
            normalized['created_at'] = str(created_at)

        if updated_at:
            normalized['updated_at'] = str(updated_at)

        # Keep all raw data
        normalized['raw_data'] = raw_record

        # Extract common fields if present
        for field in ['name', 'email', 'phone', 'website', 'address']:
            if field in raw_record:
                normalized[field] = raw_record[field]

        return normalized
