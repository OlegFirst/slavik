"""
Data Retention Manager

Manages data lifecycle, retention policies, and archiving for all database schemas.
Ensures compliance with data retention requirements while maintaining database performance.

Retention Policies:
- audit_logs: 365 days retention, archive after 90 days
- bia_data: 7 years retention, archive after 2 years
- workflow_logs: 180 days retention, archive after 30 days
- temp_data: 7 days retention, no archive
- ai_interactions: 90 days retention, archive after 30 days
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


# =============================================================================
# RETENTION POLICIES
# =============================================================================

@dataclass
class RetentionPolicy:
    """Retention policy for a table"""
    schema: str
    table: str
    retention_days: int  # Total retention before deletion
    archive_days: int    # Days before moving to archive (0 = no archive)
    enabled: bool = True
    last_cleanup: Optional[datetime] = None
    last_archive: Optional[datetime] = None


# Predefined retention policies
RETENTION_POLICIES = [
    # Audit & Compliance
    RetentionPolicy("public", "audit_logs", 365, 90),
    RetentionPolicy("public", "security_events", 730, 180),
    RetentionPolicy("governance", "compliance_reports", 2555, 730),  # 7 years

    # BIA & Risk
    RetentionPolicy("bia", "assessments", 2555, 730),  # 7 years
    RetentionPolicy("bia", "scenarios", 2555, 730),
    RetentionPolicy("risk", "assessments", 2555, 730),

    # Workflow & Processes
    RetentionPolicy("workflow_engine", "workflow_logs", 180, 30),
    RetentionPolicy("workflow_engine", "task_executions", 180, 30),
    RetentionPolicy("validation", "validation_logs", 180, 30),

    # AI & Learning
    RetentionPolicy("ai_learning", "interactions", 90, 30),
    RetentionPolicy("ai_learning", "training_data", 365, 90),
    RetentionPolicy("ai_learning", "model_runs", 90, 30),

    # Temporary & Cache
    RetentionPolicy("public", "temp_sessions", 7, 0),
    RetentionPolicy("public", "cache_entries", 1, 0),
    RetentionPolicy("public", "webhook_logs", 30, 0),
]


# =============================================================================
# DATA RETENTION MANAGER
# =============================================================================

class DataRetentionManager:
    """Manages data retention, archiving, and lifecycle"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.policies = {f"{p.schema}.{p.table}": p for p in RETENTION_POLICIES}
        logger.info(f"📋 Data Retention Manager initialized with {len(self.policies)} policies")

    async def check_retention_status(self) -> Dict[str, Any]:
        """
        Check retention status for all tables

        Returns:
            Status report with tables needing cleanup/archive
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "tables_needing_archive": [],
            "tables_needing_cleanup": [],
            "policies_count": len(self.policies),
            "total_old_records": 0
        }

        for policy_key, policy in self.policies.items():
            if not policy.enabled:
                continue

            # Check archive threshold
            if policy.archive_days > 0:
                archive_threshold = datetime.now() - timedelta(days=policy.archive_days)
                count = await self._count_old_records(
                    policy.schema,
                    policy.table,
                    archive_threshold
                )

                if count > 0:
                    report["tables_needing_archive"].append({
                        "table": f"{policy.schema}.{policy.table}",
                        "old_records": count,
                        "archive_threshold_days": policy.archive_days,
                        "threshold_date": archive_threshold.isoformat()
                    })
                    report["total_old_records"] += count

            # Check cleanup threshold
            cleanup_threshold = datetime.now() - timedelta(days=policy.retention_days)
            count = await self._count_old_records(
                policy.schema,
                policy.table,
                cleanup_threshold
            )

            if count > 0:
                report["tables_needing_cleanup"].append({
                    "table": f"{policy.schema}.{policy.table}",
                    "old_records": count,
                    "retention_days": policy.retention_days,
                    "threshold_date": cleanup_threshold.isoformat()
                })

        return report

    async def _count_old_records(self, schema: str, table: str, threshold: datetime) -> int:
        """Count records older than threshold"""
        try:
            # Try common timestamp column names
            timestamp_columns = ['created_at', 'timestamp', 'date_created', 'updated_at']

            for col in timestamp_columns:
                try:
                    query = text(f"""
                        SELECT COUNT(*) FROM {schema}.{table}
                        WHERE {col} < :threshold
                    """)
                    result = await self.db.execute(query, {"threshold": threshold})
                    count = result.scalar()
                    return count or 0
                except Exception:
                    continue

            # No timestamp column found
            logger.debug(f"No timestamp column found in {schema}.{table}")
            return 0

        except Exception as e:
            logger.error(f"Error counting old records in {schema}.{table}: {e}")
            return 0

    async def archive_old_data(
        self,
        schema: str,
        table: str,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Archive old data from table to archive schema

        Args:
            schema: Source schema
            table: Source table
            dry_run: If True, only simulate (don't actually archive)

        Returns:
            Archive operation report
        """
        policy_key = f"{schema}.{table}"
        policy = self.policies.get(policy_key)

        if not policy:
            raise ValueError(f"No retention policy found for {policy_key}")

        if policy.archive_days == 0:
            raise ValueError(f"Table {policy_key} has no archive policy")

        archive_threshold = datetime.now() - timedelta(days=policy.archive_days)

        report = {
            "table": policy_key,
            "archive_threshold": archive_threshold.isoformat(),
            "dry_run": dry_run,
            "records_archived": 0,
            "success": False
        }

        try:
            # Create archive schema if not exists
            await self.db.execute(text("CREATE SCHEMA IF NOT EXISTS archive"))

            # Create archive table if not exists (copy structure)
            await self.db.execute(text(f"""
                CREATE TABLE IF NOT EXISTS archive.{table}
                (LIKE {schema}.{table} INCLUDING ALL)
            """))

            # Count records to archive
            timestamp_col = await self._find_timestamp_column(schema, table)
            if not timestamp_col:
                raise ValueError(f"No timestamp column found in {schema}.{table}")

            count_query = text(f"""
                SELECT COUNT(*) FROM {schema}.{table}
                WHERE {timestamp_col} < :threshold
            """)
            result = await self.db.execute(count_query, {"threshold": archive_threshold})
            records_count = result.scalar()

            report["records_to_archive"] = records_count

            if records_count == 0:
                report["success"] = True
                report["message"] = "No records to archive"
                return report

            if not dry_run:
                # Move data to archive
                move_query = text(f"""
                    INSERT INTO archive.{table}
                    SELECT * FROM {schema}.{table}
                    WHERE {timestamp_col} < :threshold
                """)
                await self.db.execute(move_query, {"threshold": archive_threshold})

                # Delete from source
                delete_query = text(f"""
                    DELETE FROM {schema}.{table}
                    WHERE {timestamp_col} < :threshold
                """)
                result = await self.db.execute(delete_query, {"threshold": archive_threshold})

                await self.db.commit()

                report["records_archived"] = records_count
                report["success"] = True
                report["message"] = f"Archived {records_count} records"

                logger.info(f"✅ Archived {records_count} records from {policy_key}")
            else:
                report["success"] = True
                report["message"] = f"DRY RUN: Would archive {records_count} records"
                logger.info(f"🔍 DRY RUN: Would archive {records_count} records from {policy_key}")

        except Exception as e:
            report["success"] = False
            report["error"] = str(e)
            logger.error(f"❌ Failed to archive data from {policy_key}: {e}")

        return report

    async def cleanup_old_data(
        self,
        schema: str,
        table: str,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Delete old data that exceeded retention period

        Args:
            schema: Table schema
            table: Table name
            dry_run: If True, only simulate (don't actually delete)

        Returns:
            Cleanup operation report
        """
        policy_key = f"{schema}.{table}"
        policy = self.policies.get(policy_key)

        if not policy:
            raise ValueError(f"No retention policy found for {policy_key}")

        retention_threshold = datetime.now() - timedelta(days=policy.retention_days)

        report = {
            "table": policy_key,
            "retention_threshold": retention_threshold.isoformat(),
            "dry_run": dry_run,
            "records_deleted": 0,
            "success": False
        }

        try:
            timestamp_col = await self._find_timestamp_column(schema, table)
            if not timestamp_col:
                raise ValueError(f"No timestamp column found in {schema}.{table}")

            # Count records to delete
            count_query = text(f"""
                SELECT COUNT(*) FROM {schema}.{table}
                WHERE {timestamp_col} < :threshold
            """)
            result = await self.db.execute(count_query, {"threshold": retention_threshold})
            records_count = result.scalar()

            report["records_to_delete"] = records_count

            if records_count == 0:
                report["success"] = True
                report["message"] = "No records to delete"
                return report

            if not dry_run:
                # Delete old records
                delete_query = text(f"""
                    DELETE FROM {schema}.{table}
                    WHERE {timestamp_col} < :threshold
                """)
                await self.db.execute(delete_query, {"threshold": retention_threshold})
                await self.db.commit()

                report["records_deleted"] = records_count
                report["success"] = True
                report["message"] = f"Deleted {records_count} records"

                logger.warning(f"🗑️  Deleted {records_count} old records from {policy_key}")
            else:
                report["success"] = True
                report["message"] = f"DRY RUN: Would delete {records_count} records"
                logger.info(f"🔍 DRY RUN: Would delete {records_count} records from {policy_key}")

        except Exception as e:
            report["success"] = False
            report["error"] = str(e)
            logger.error(f"❌ Failed to cleanup data from {policy_key}: {e}")

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

    async def get_retention_policies(self) -> List[Dict[str, Any]]:
        """Get all retention policies"""
        return [
            {
                **asdict(policy),
                "table_full_name": f"{policy.schema}.{policy.table}"
            }
            for policy in self.policies.values()
        ]

    async def update_policy(
        self,
        schema: str,
        table: str,
        retention_days: Optional[int] = None,
        archive_days: Optional[int] = None,
        enabled: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update retention policy for a table"""
        policy_key = f"{schema}.{table}"
        policy = self.policies.get(policy_key)

        if not policy:
            raise ValueError(f"No retention policy found for {policy_key}")

        if retention_days is not None:
            policy.retention_days = retention_days

        if archive_days is not None:
            policy.archive_days = archive_days

        if enabled is not None:
            policy.enabled = enabled

        logger.info(f"✅ Updated retention policy for {policy_key}")

        return {
            "table": policy_key,
            "policy": asdict(policy)
        }
