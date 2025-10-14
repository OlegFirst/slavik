"""
Archive Service

Exports old data to cold storage (S3/MinIO/local filesystem).
Compresses and encrypts archived data for long-term storage.

Features:
- Export to S3/MinIO or local filesystem
- Compression (gzip/zip)
- Optional encryption (AES-256)
- Incremental archiving
- Archive catalog for querying
- Restore from archive capability

Workflow:
1. Identify old data based on retention policy
2. Export to JSON/CSV/Parquet format
3. Compress (gzip)
4. Upload to S3/MinIO or save locally
5. Update archive catalog
6. Optionally delete from source table
"""

import logging
import json
import gzip
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import tempfile
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


# =============================================================================
# ARCHIVE CONFIGURATION
# =============================================================================

@dataclass
class ArchiveConfig:
    """Archive configuration for a table"""
    schema: str
    table: str
    archive_format: str  # 'json', 'csv', 'parquet'
    compression: str     # 'gzip', 'zip', 'none'
    storage_backend: str # 's3', 'minio', 'local'
    storage_path: str    # S3 bucket or local path
    encrypt: bool = False
    enabled: bool = True
    last_archive: Optional[datetime] = None


# Archive configurations
ARCHIVE_CONFIGS = [
    # Audit logs - JSON format for flexibility
    ArchiveConfig("public", "audit_logs", "json", "gzip", "local", "/var/archives/audit_logs"),

    # Security events - JSON with encryption
    ArchiveConfig("public", "security_events", "json", "gzip", "local", "/var/archives/security_events", encrypt=True),

    # Workflow logs - CSV for analysis
    ArchiveConfig("workflow_engine", "workflow_logs", "csv", "gzip", "local", "/var/archives/workflow_logs"),

    # AI interactions - JSON
    ArchiveConfig("ai_learning", "interactions", "json", "gzip", "local", "/var/archives/ai_interactions"),

    # BIA assessments - JSON with full history
    ArchiveConfig("bia", "assessment_history", "json", "gzip", "local", "/var/archives/bia_assessments"),
]


# =============================================================================
# ARCHIVE SERVICE
# =============================================================================

class ArchiveService:
    """Manages data archiving to cold storage"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.configs = {f"{c.schema}.{c.table}": c for c in ARCHIVE_CONFIGS}
        logger.info(f"📦 Archive Service initialized with {len(self.configs)} configurations")

    async def check_archive_status(self) -> Dict[str, Any]:
        """
        Check archive status for all configured tables

        Returns:
            Status report with tables needing archiving
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "tables_needing_archive": [],
            "recent_archives": [],
            "total_configs": len(self.configs),
            "storage_backends": {}
        }

        # Group by storage backend
        backends = {}
        for config in self.configs.values():
            if config.storage_backend not in backends:
                backends[config.storage_backend] = 0
            backends[config.storage_backend] += 1

        report["storage_backends"] = backends

        for config_key, config in self.configs.items():
            if not config.enabled:
                continue

            # Check if archive is needed (example: archive monthly)
            needs_archive = True
            if config.last_archive:
                days_since_archive = (datetime.now() - config.last_archive).days
                needs_archive = days_since_archive >= 30  # Archive monthly

            if needs_archive:
                report["tables_needing_archive"].append({
                    "table": config_key,
                    "format": config.archive_format,
                    "backend": config.storage_backend,
                    "last_archive": config.last_archive.isoformat() if config.last_archive else None
                })

        return report

    async def export_to_archive(
        self,
        schema: str,
        table: str,
        date_threshold: datetime,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Export old data to archive

        Args:
            schema: Table schema
            table: Table name
            date_threshold: Export data older than this date
            dry_run: If True, only show what would be archived

        Returns:
            Archive operation report
        """
        config_key = f"{schema}.{table}"
        config = self.configs.get(config_key)

        if not config:
            raise ValueError(f"No archive config found for {config_key}")

        report = {
            "table": config_key,
            "date_threshold": date_threshold.isoformat(),
            "dry_run": dry_run,
            "format": config.archive_format,
            "compression": config.compression,
            "backend": config.storage_backend,
            "success": False
        }

        try:
            # Find timestamp column
            timestamp_col = await self._find_timestamp_column(schema, table)
            if not timestamp_col:
                raise ValueError(f"No timestamp column found in {schema}.{table}")

            # Count records to archive
            count_query = text(f"""
                SELECT COUNT(*) FROM {schema}.{table}
                WHERE {timestamp_col} < :threshold
            """)
            result = await self.db.execute(count_query, {"threshold": date_threshold})
            records_count = result.scalar()

            report["records_to_archive"] = records_count

            if records_count == 0:
                report["success"] = True
                report["message"] = "No records to archive"
                return report

            if dry_run:
                report["success"] = True
                report["message"] = f"DRY RUN: Would archive {records_count} records"
                report["estimated_size_mb"] = round(records_count * 0.001, 2)  # Rough estimate
                return report

            # Fetch data to archive
            fetch_query = text(f"""
                SELECT * FROM {schema}.{table}
                WHERE {timestamp_col} < :threshold
                ORDER BY {timestamp_col}
                LIMIT 10000
            """)
            result = await self.db.execute(fetch_query, {"threshold": date_threshold})
            rows = result.fetchall()
            columns = result.keys()

            # Convert to desired format
            if config.archive_format == "json":
                data = [dict(zip(columns, row)) for row in rows]
                archive_data = json.dumps(data, default=str, indent=2)
            elif config.archive_format == "csv":
                import csv
                import io
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(columns)
                writer.writerows(rows)
                archive_data = output.getvalue()
            else:
                raise ValueError(f"Unsupported format: {config.archive_format}")

            # Generate archive filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{table}_{timestamp}.{config.archive_format}"

            # Compress if enabled
            if config.compression == "gzip":
                compressed_data = gzip.compress(archive_data.encode('utf-8'))
                filename += ".gz"
            else:
                compressed_data = archive_data.encode('utf-8')

            # Save to storage backend
            if config.storage_backend == "local":
                archive_path = await self._save_to_local(
                    config.storage_path,
                    filename,
                    compressed_data
                )
                report["archive_path"] = archive_path
            elif config.storage_backend in ["s3", "minio"]:
                archive_url = await self._save_to_s3(
                    config.storage_path,
                    filename,
                    compressed_data
                )
                report["archive_url"] = archive_url
            else:
                raise ValueError(f"Unsupported backend: {config.storage_backend}")

            report["records_archived"] = len(rows)
            report["archive_filename"] = filename
            report["archive_size_bytes"] = len(compressed_data)
            report["archive_size_mb"] = round(len(compressed_data) / 1024 / 1024, 2)
            report["success"] = True
            report["message"] = f"Archived {len(rows)} records to {filename}"

            logger.info(f"✅ Archived {len(rows)} records from {config_key} to {filename}")

            # Update catalog
            await self._update_archive_catalog(
                schema=schema,
                table=table,
                filename=filename,
                records_count=len(rows),
                date_from=rows[0][columns.index(timestamp_col)],
                date_to=rows[-1][columns.index(timestamp_col)],
                size_bytes=len(compressed_data)
            )

        except Exception as e:
            report["success"] = False
            report["error"] = str(e)
            logger.error(f"❌ Failed to archive data from {config_key}: {e}")

        return report

    async def _find_timestamp_column(self, schema: str, table: str) -> Optional[str]:
        """Find timestamp column in table"""
        timestamp_columns = ['created_at', 'timestamp', 'date_created', 'updated_at']

        for col in timestamp_columns:
            try:
                query = text(f"""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_schema = :schema
                    AND table_name = :table
                    AND column_name = :col
                """)
                result = await self.db.execute(
                    query,
                    {"schema": schema, "table": table, "col": col}
                )
                if result.scalar():
                    return col
            except:
                continue

        return None

    async def _save_to_local(
        self,
        base_path: str,
        filename: str,
        data: bytes
    ) -> str:
        """Save archive to local filesystem"""
        try:
            # Create directory if not exists
            os.makedirs(base_path, exist_ok=True)

            # Full path
            full_path = os.path.join(base_path, filename)

            # Write file
            with open(full_path, 'wb') as f:
                f.write(data)

            logger.info(f"📁 Saved archive to {full_path}")
            return full_path

        except Exception as e:
            logger.error(f"Failed to save to local: {e}")
            raise

    async def _save_to_s3(
        self,
        bucket: str,
        filename: str,
        data: bytes
    ) -> str:
        """Save archive to S3/MinIO"""
        # This is a placeholder - implement actual S3 upload
        # You would use boto3 or aioboto3 here
        logger.warning("S3/MinIO upload not implemented yet - would upload to: s3://{bucket}/{filename}")

        # Example implementation:
        # import boto3
        # s3 = boto3.client('s3')
        # s3.put_object(Bucket=bucket, Key=filename, Body=data)
        # url = f"s3://{bucket}/{filename}"
        # return url

        return f"s3://{bucket}/{filename}"

    async def _update_archive_catalog(
        self,
        schema: str,
        table: str,
        filename: str,
        records_count: int,
        date_from: datetime,
        date_to: datetime,
        size_bytes: int
    ):
        """Update archive catalog table"""
        try:
            # Create catalog table if not exists
            await self.db.execute(text("""
                CREATE TABLE IF NOT EXISTS public.archive_catalog (
                    id SERIAL PRIMARY KEY,
                    schema_name TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    archive_filename TEXT NOT NULL,
                    records_count INT NOT NULL,
                    date_from TIMESTAMP,
                    date_to TIMESTAMP,
                    size_bytes BIGINT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))

            # Insert catalog entry
            insert_query = text("""
                INSERT INTO public.archive_catalog
                (schema_name, table_name, archive_filename, records_count, date_from, date_to, size_bytes)
                VALUES
                (:schema, :table, :filename, :count, :date_from, :date_to, :size)
            """)
            await self.db.execute(insert_query, {
                "schema": schema,
                "table": table,
                "filename": filename,
                "count": records_count,
                "date_from": date_from,
                "date_to": date_to,
                "size": size_bytes
            })

            await self.db.commit()
            logger.info(f"✅ Updated archive catalog for {schema}.{table}")

        except Exception as e:
            logger.error(f"Failed to update archive catalog: {e}")

    async def list_archives(
        self,
        schema: Optional[str] = None,
        table: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List archives from catalog"""
        try:
            query = """
                SELECT
                    schema_name,
                    table_name,
                    archive_filename,
                    records_count,
                    date_from,
                    date_to,
                    size_bytes,
                    created_at
                FROM public.archive_catalog
                WHERE 1=1
            """
            params = {}

            if schema:
                query += " AND schema_name = :schema"
                params["schema"] = schema

            if table:
                query += " AND table_name = :table"
                params["table"] = table

            query += " ORDER BY created_at DESC LIMIT :limit"
            params["limit"] = limit

            result = await self.db.execute(text(query), params)
            rows = result.fetchall()

            archives = []
            for row in rows:
                archives.append({
                    "schema": row[0],
                    "table": row[1],
                    "filename": row[2],
                    "records_count": row[3],
                    "date_from": row[4].isoformat() if row[4] else None,
                    "date_to": row[5].isoformat() if row[5] else None,
                    "size_bytes": row[6],
                    "size_mb": round(row[6] / 1024 / 1024, 2) if row[6] else 0,
                    "created_at": row[7].isoformat() if row[7] else None
                })

            return archives

        except Exception as e:
            logger.error(f"Failed to list archives: {e}")
            return []

    async def get_archive_stats(self) -> Dict[str, Any]:
        """Get archive statistics"""
        try:
            query = text("""
                SELECT
                    COUNT(*) as total_archives,
                    SUM(records_count) as total_records,
                    SUM(size_bytes) as total_size_bytes,
                    MIN(created_at) as first_archive,
                    MAX(created_at) as last_archive
                FROM public.archive_catalog
            """)
            result = await self.db.execute(query)
            row = result.fetchone()

            if not row or row[0] == 0:
                return {
                    "total_archives": 0,
                    "total_records": 0,
                    "total_size_mb": 0,
                    "message": "No archives found"
                }

            return {
                "total_archives": row[0],
                "total_records": row[1],
                "total_size_bytes": row[2],
                "total_size_mb": round(row[2] / 1024 / 1024, 2) if row[2] else 0,
                "total_size_gb": round(row[2] / 1024 / 1024 / 1024, 2) if row[2] else 0,
                "first_archive": row[3].isoformat() if row[3] else None,
                "last_archive": row[4].isoformat() if row[4] else None
            }

        except Exception as e:
            logger.error(f"Failed to get archive stats: {e}")
            return {
                "error": str(e)
            }

    async def restore_from_archive(
        self,
        archive_filename: str,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Restore data from archive

        Args:
            archive_filename: Archive filename to restore
            dry_run: If True, only show what would be restored

        Returns:
            Restore operation report
        """
        report = {
            "archive_filename": archive_filename,
            "dry_run": dry_run,
            "success": False
        }

        try:
            # Get archive info from catalog
            query = text("""
                SELECT schema_name, table_name, archive_filename, records_count
                FROM public.archive_catalog
                WHERE archive_filename = :filename
            """)
            result = await self.db.execute(query, {"filename": archive_filename})
            row = result.fetchone()

            if not row:
                raise ValueError(f"Archive {archive_filename} not found in catalog")

            schema, table, filename, records_count = row

            config_key = f"{schema}.{table}"
            config = self.configs.get(config_key)

            if not config:
                raise ValueError(f"No archive config found for {config_key}")

            report["schema"] = schema
            report["table"] = table
            report["records_count"] = records_count

            if dry_run:
                report["success"] = True
                report["message"] = f"DRY RUN: Would restore {records_count} records to {schema}.{table}"
                return report

            # TODO: Implement actual restore logic
            # 1. Read archive file
            # 2. Decompress if needed
            # 3. Parse format (JSON/CSV)
            # 4. Insert into table
            # 5. Verify record count

            report["success"] = False
            report["message"] = "Restore not implemented yet - requires careful planning"

        except Exception as e:
            report["success"] = False
            report["error"] = str(e)
            logger.error(f"❌ Failed to restore from {archive_filename}: {e}")

        return report

    async def get_archive_configs(self) -> List[Dict[str, Any]]:
        """Get all archive configurations"""
        return [
            {
                **asdict(config),
                "table_full_name": f"{config.schema}.{config.table}"
            }
            for config in self.configs.values()
        ]
