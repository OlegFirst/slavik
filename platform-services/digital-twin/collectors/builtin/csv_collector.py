"""
CSV Collector

Collects data from CSV files
"""

import logging
import csv
import aiofiles
from typing import Dict, List, Optional, Any
from pathlib import Path

from collectors.base import FileCollector

logger = logging.getLogger(__name__)


class CSVCollector(FileCollector):
    """
    CSV File Data Collector

    Collects data from CSV files
    """

    def __init__(
        self,
        credentials: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize CSV collector

        Required config:
            - file_path: Path to CSV file or directory with CSV files
            - entity_type: Entity type for the data (e.g., 'companies', 'contacts')

        Optional config:
            - delimiter: CSV delimiter (default: ',')
            - encoding: File encoding (default: 'utf-8')
            - has_header: Whether CSV has header row (default: True)
            - column_mapping: Dict mapping CSV columns to standard fields
              Example: {'Company Name': 'name', 'Email': 'email'}
        """
        super().__init__(credentials, config)

        self._file_path = Path(self.config.get('file_path', ''))
        self._entity_type = self.config.get('entity_type', 'custom')
        self._delimiter = self.config.get('delimiter', ',')
        self._encoding = self.config.get('encoding', 'utf-8')
        self._has_header = self.config.get('has_header', True)
        self._column_mapping = self.config.get('column_mapping', {})

        self._files: List[Path] = []

    @property
    def source_name(self) -> str:
        return "CSV File"

    @property
    def supported_entities(self) -> List[str]:
        return [self._entity_type]

    async def connect(self) -> bool:
        """
        Validate file path

        Returns:
            True if file(s) exist
        """
        logger.info(f"Validating CSV path: {self._file_path}")

        try:
            if not self._file_path.exists():
                raise FileNotFoundError(f"Path not found: {self._file_path}")

            # If directory, find all CSV files
            if self._file_path.is_dir():
                self._files = list(self._file_path.glob('*.csv'))
                if not self._files:
                    raise FileNotFoundError(f"No CSV files found in: {self._file_path}")
                logger.info(f"Found {len(self._files)} CSV files")
            else:
                # Single file
                if not self._file_path.suffix.lower() == '.csv':
                    raise ValueError(f"Not a CSV file: {self._file_path}")
                self._files = [self._file_path]

            self._initialized = True

            logger.info(f"CSV collector initialized with {len(self._files)} file(s)")

            return True

        except Exception as e:
            logger.error(f"CSV validation failed: {e}", exc_info=True)
            raise ConnectionError(f"Failed to validate CSV: {e}")

    async def disconnect(self) -> None:
        """Close collector"""
        self._files = []
        self._initialized = False

        logger.info("CSV collector closed")

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test CSV access

        Returns:
            Test results
        """
        try:
            return {
                'status': 'success',
                'files': [str(f) for f in self._files],
                'file_count': len(self._files)
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
        Collect data from CSV file(s)

        Args:
            entity_type: Entity type to collect
            filters: Row filters (applied after loading)
            limit: Maximum records
            offset: Starting offset

        Returns:
            List of collected records
        """
        await self.ensure_connected()

        if entity_type != self._entity_type:
            raise ValueError(f"Entity type {entity_type} not supported, expected {self._entity_type}")

        logger.info(f"Collecting {entity_type} from {len(self._files)} CSV file(s)")

        try:
            all_records = []

            # Read all CSV files
            for file_path in self._files:
                records = await self._read_csv_file(file_path)
                all_records.extend(records)

            # Apply filters
            if filters:
                all_records = self._apply_filters(all_records, filters)

            # Apply offset and limit
            if offset:
                all_records = all_records[offset:]

            if limit:
                all_records = all_records[:limit]

            logger.info(f"Collected {len(all_records)} {entity_type} records from CSV")

            # Normalize records
            normalized = [
                self.normalize_record(record, entity_type)
                for record in all_records
            ]

            return normalized

        except Exception as e:
            logger.error(f"Error collecting {entity_type} from CSV: {e}", exc_info=True)
            raise

    async def _read_csv_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Read single CSV file

        Args:
            file_path: Path to CSV file

        Returns:
            List of records
        """
        logger.info(f"Reading CSV file: {file_path}")

        records = []

        try:
            # Read file asynchronously
            async with aiofiles.open(file_path, mode='r', encoding=self._encoding) as f:
                content = await f.read()

            # Parse CSV
            csv_reader = csv.reader(content.splitlines(), delimiter=self._delimiter)

            # Get headers
            if self._has_header:
                headers = next(csv_reader)
            else:
                # Use column numbers as keys
                first_row = next(csv_reader)
                headers = [f'column_{i}' for i in range(len(first_row))]
                # Re-add first row to records
                records.append(dict(zip(headers, first_row)))

            # Read rows
            for row in csv_reader:
                if not row:  # Skip empty rows
                    continue

                record = dict(zip(headers, row))
                records.append(record)

            logger.info(f"Read {len(records)} records from {file_path.name}")

            return records

        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}", exc_info=True)
            return []

    async def get_metadata(self, entity_type: str) -> Dict[str, Any]:
        """
        Get CSV metadata

        Args:
            entity_type: Entity type

        Returns:
            Metadata dictionary
        """
        await self.ensure_connected()

        # Read first file to get column names
        if self._files:
            try:
                async with aiofiles.open(self._files[0], mode='r', encoding=self._encoding) as f:
                    first_line = await f.readline()

                csv_reader = csv.reader([first_line], delimiter=self._delimiter)
                headers = next(csv_reader)

                return {
                    'entity_type': entity_type,
                    'files': [str(f) for f in self._files],
                    'columns': headers,
                    'column_count': len(headers),
                    'has_header': self._has_header,
                    'delimiter': self._delimiter,
                    'encoding': self._encoding
                }

            except Exception as e:
                logger.error(f"Error reading metadata: {e}", exc_info=True)

        return {
            'entity_type': entity_type,
            'files': []
        }

    def _apply_filters(
        self,
        records: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply filters to records

        Args:
            records: List of records
            filters: Filter dictionary

        Returns:
            Filtered records
        """
        filtered = []

        for record in records:
            match = True

            for key, value in filters.items():
                if key not in record:
                    match = False
                    break

                # Simple equality check
                if str(record[key]).lower() != str(value).lower():
                    match = False
                    break

            if match:
                filtered.append(record)

        return filtered

    def normalize_record(
        self,
        raw_record: Dict[str, Any],
        entity_type: str
    ) -> Dict[str, Any]:
        """
        Normalize CSV record to standard format

        Args:
            raw_record: Raw CSV row as dict
            entity_type: Entity type

        Returns:
            Normalized record
        """
        # Apply column mapping if configured
        mapped_record = {}

        if self._column_mapping:
            for csv_col, std_field in self._column_mapping.items():
                if csv_col in raw_record:
                    mapped_record[std_field] = raw_record[csv_col]

            # Keep unmapped columns
            for key, value in raw_record.items():
                if key not in self._column_mapping:
                    mapped_record[key] = value
        else:
            mapped_record = raw_record.copy()

        # Build normalized record
        normalized = {
            'source': self.source_name,
            'source_id': mapped_record.get('id') or raw_record.get('id'),
            'entity_type': entity_type,
            'raw_data': raw_record,
            'mapped_data': mapped_record
        }

        # Extract common fields if present
        for field in ['name', 'email', 'phone', 'website', 'address']:
            if field in mapped_record:
                normalized[field] = mapped_record[field]

        return normalized

    async def read_file(self) -> List[Dict[str, Any]]:
        """
        Read all CSV files

        Returns:
            All records from all files
        """
        await self.ensure_connected()

        all_records = []

        for file_path in self._files:
            records = await self._read_csv_file(file_path)
            all_records.extend(records)

        return all_records
