"""
Partitioning Manager

Manages table partitioning for large tables to improve query performance.
Automatically creates and manages time-based partitions (monthly/yearly).

Benefits:
- Faster queries on large tables (query only relevant partitions)
- Easier data archiving (drop old partitions)
- Better vacuum performance (smaller chunks)
- Improved index maintenance

Partitioning Strategy:
- Large tables (>1M rows): Monthly partitions
- Audit/log tables: Monthly partitions
- Historical data: Yearly partitions
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from dateutil.relativedelta import relativedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


# =============================================================================
# PARTITIONING CONFIGURATION
# =============================================================================

@dataclass
class PartitioningConfig:
    """Partitioning configuration for a table"""
    schema: str
    table: str
    partition_type: str  # 'monthly', 'yearly', 'daily'
    partition_key: str   # Column to partition by (e.g., 'created_at')
    retention_partitions: int  # Number of partitions to keep
    enabled: bool = True
    last_partition_check: Optional[datetime] = None


# Tables that should be partitioned
PARTITIONING_CONFIGS = [
    # Audit & Security Logs (high volume)
    PartitioningConfig("public", "audit_logs", "monthly", "created_at", 12),  # 1 year
    PartitioningConfig("public", "security_events", "monthly", "created_at", 24),  # 2 years

    # Workflow & Task Executions (high volume)
    PartitioningConfig("workflow_engine", "workflow_logs", "monthly", "created_at", 6),  # 6 months
    PartitioningConfig("workflow_engine", "task_executions", "monthly", "executed_at", 6),

    # AI Interactions (high volume)
    PartitioningConfig("ai_learning", "interactions", "monthly", "created_at", 3),  # 3 months
    PartitioningConfig("ai_learning", "model_runs", "monthly", "started_at", 3),

    # Validation & Monitoring
    PartitioningConfig("validation", "validation_logs", "monthly", "created_at", 6),

    # Historical BIA data (yearly partitions for long-term storage)
    PartitioningConfig("bia", "assessment_history", "yearly", "created_at", 7),  # 7 years
]


# =============================================================================
# PARTITIONING MANAGER
# =============================================================================

class PartitioningManager:
    """Manages table partitioning for performance optimization"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.configs = {f"{c.schema}.{c.table}": c for c in PARTITIONING_CONFIGS}
        logger.info(f" Partitioning Manager initialized with {len(self.configs)} tables")

    async def check_partitioning_status(self) -> Dict[str, Any]:
        """
        Check partitioning status for all configured tables

        Returns:
            Status report with tables needing new partitions
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "tables_needing_partitions": [],
            "partitioned_tables": [],
            "non_partitioned_tables": [],
            "total_partitions": 0
        }

        for config_key, config in self.configs.items():
            if not config.enabled:
                continue

            is_partitioned = await self._is_table_partitioned(config.schema, config.table)

            if is_partitioned:
                partitions = await self._list_partitions(config.schema, config.table)
                report["partitioned_tables"].append({
                    "table": config_key,
                    "partition_type": config.partition_type,
                    "partition_count": len(partitions),
                    "latest_partition": partitions[0] if partitions else None,
                    "oldest_partition": partitions[-1] if partitions else None
                })
                report["total_partitions"] += len(partitions)

                # Check if we need new partitions
                if await self._needs_new_partition(config):
                    report["tables_needing_partitions"].append({
                        "table": config_key,
                        "partition_type": config.partition_type,
                        "action": "create_future_partitions"
                    })
            else:
                report["non_partitioned_tables"].append({
                    "table": config_key,
                    "partition_type": config.partition_type,
                    "action": "convert_to_partitioned"
                })

        return report

    async def _is_table_partitioned(self, schema: str, table: str) -> bool:
        """Check if table is partitioned"""
        try:
            query = text("""
                SELECT COUNT(*) FROM pg_partitioned_table pt
                JOIN pg_class c ON pt.partrelid = c.oid
                JOIN pg_namespace n ON c.relnamespace = n.oid
                WHERE n.nspname = :schema AND c.relname = :table
            """)
            result = await self.db.execute(query, {"schema": schema, "table": table})
            count = result.scalar()
            return count > 0
        except Exception as e:
            logger.error(f"Error checking if {schema}.{table} is partitioned: {e}")
            return False

    async def _list_partitions(self, schema: str, table: str) -> List[str]:
        """List all partitions for a table"""
        try:
            query = text("""
                SELECT c.relname as partition_name
                FROM pg_inherits i
                JOIN pg_class c ON i.inhrelid = c.oid
                JOIN pg_class p ON i.inhparent = p.oid
                JOIN pg_namespace n ON p.relnamespace = n.oid
                WHERE n.nspname = :schema AND p.relname = :table
                ORDER BY c.relname DESC
            """)
            result = await self.db.execute(query, {"schema": schema, "table": table})
            return [row[0] for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error listing partitions for {schema}.{table}: {e}")
            return []

    async def _needs_new_partition(self, config: PartitioningConfig) -> bool:
        """Check if table needs new partitions created"""
        partitions = await self._list_partitions(config.schema, config.table)

        if not partitions:
            return True  # No partitions yet

        # Parse latest partition name to get date
        latest_partition = partitions[0]

        # Extract date from partition name (e.g., table_name_2025_10 -> 2025-10)
        try:
            if config.partition_type == "monthly":
                # Check if we need next 2 months
                now = datetime.now()
                next_month = now + relativedelta(months=1)
                expected_partition = f"{config.table}_{next_month.year}_{next_month.month:02d}"
                return expected_partition not in partitions
            elif config.partition_type == "yearly":
                now = datetime.now()
                next_year = now + relativedelta(years=1)
                expected_partition = f"{config.table}_{next_year.year}"
                return expected_partition not in partitions
            elif config.partition_type == "daily":
                now = datetime.now()
                tomorrow = now + timedelta(days=1)
                expected_partition = f"{config.table}_{tomorrow.year}_{tomorrow.month:02d}_{tomorrow.day:02d}"
                return expected_partition not in partitions
        except Exception as e:
            logger.error(f"Error checking partition needs: {e}")
            return False

        return False

    async def convert_to_partitioned(
        self,
        schema: str,
        table: str,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Convert existing table to partitioned table

        WARNING: This is a complex operation that requires downtime!

        Steps:
        1. Rename original table
        2. Create new partitioned table with same structure
        3. Create partitions for existing data
        4. Copy data to partitions
        5. Drop original table

        Args:
            schema: Table schema
            table: Table name
            dry_run: If True, only show what would be done

        Returns:
            Operation report
        """
        config_key = f"{schema}.{table}"
        config = self.configs.get(config_key)

        if not config:
            raise ValueError(f"No partitioning config found for {config_key}")

        report = {
            "table": config_key,
            "partition_type": config.partition_type,
            "dry_run": dry_run,
            "steps": [],
            "success": False
        }

        try:
            # Check if already partitioned
            if await self._is_table_partitioned(schema, table):
                report["success"] = True
                report["message"] = "Table is already partitioned"
                return report

            # Step 1: Get table structure
            report["steps"].append("Analyzing table structure...")

            # Get row count
            count_query = text(f"SELECT COUNT(*) FROM {schema}.{table}")
            result = await self.db.execute(count_query)
            row_count = result.scalar()
            report["row_count"] = row_count

            if dry_run:
                report["steps"].append(f"DRY RUN: Would partition {row_count} rows")
                report["steps"].append(f"1. Rename {table} to {table}_old")
                report["steps"].append(f"2. Create partitioned table {table}")
                report["steps"].append(f"3. Create {config.partition_type} partitions based on {config.partition_key}")
                report["steps"].append(f"4. Copy data to partitions")
                report["steps"].append(f"5. Drop {table}_old")
                report["success"] = True
                report["message"] = f"DRY RUN: Would convert {config_key} to partitioned table"
                return report

            # Actual conversion (not implemented for safety - requires careful planning)
            report["success"] = False
            report["message"] = "Actual conversion requires manual planning and downtime"
            report["recommendation"] = "Contact DBA to plan partitioning conversion"

        except Exception as e:
            report["success"] = False
            report["error"] = str(e)
            logger.error(f" Failed to convert {config_key} to partitioned: {e}")

        return report

    async def create_partitions(
        self,
        schema: str,
        table: str,
        months_ahead: int = 3,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Create future partitions for a partitioned table

        Args:
            schema: Table schema
            table: Table name
            months_ahead: Number of months/years to create ahead
            dry_run: If True, only show what would be created

        Returns:
            Operation report
        """
        config_key = f"{schema}.{table}"
        config = self.configs.get(config_key)

        if not config:
            raise ValueError(f"No partitioning config found for {config_key}")

        report = {
            "table": config_key,
            "partition_type": config.partition_type,
            "dry_run": dry_run,
            "partitions_created": [],
            "success": False
        }

        try:
            # Check if table is partitioned
            if not await self._is_table_partitioned(schema, table):
                raise ValueError(f"Table {config_key} is not partitioned yet")

            # Get existing partitions
            existing_partitions = await self._list_partitions(schema, table)

            # Generate partition names and ranges
            now = datetime.now()
            partitions_to_create = []

            for i in range(months_ahead):
                if config.partition_type == "monthly":
                    target_date = now + relativedelta(months=i+1)
                    partition_name = f"{table}_{target_date.year}_{target_date.month:02d}"
                    start_date = target_date.replace(day=1)
                    end_date = start_date + relativedelta(months=1)
                elif config.partition_type == "yearly":
                    target_date = now + relativedelta(years=i+1)
                    partition_name = f"{table}_{target_date.year}"
                    start_date = target_date.replace(month=1, day=1)
                    end_date = start_date + relativedelta(years=1)
                elif config.partition_type == "daily":
                    target_date = now + timedelta(days=i+1)
                    partition_name = f"{table}_{target_date.year}_{target_date.month:02d}_{target_date.day:02d}"
                    start_date = target_date.replace(hour=0, minute=0, second=0)
                    end_date = start_date + timedelta(days=1)
                else:
                    continue

                # Skip if partition already exists
                if partition_name in existing_partitions:
                    continue

                partitions_to_create.append({
                    "name": partition_name,
                    "start": start_date,
                    "end": end_date
                })

            report["partitions_to_create"] = len(partitions_to_create)

            if not dry_run and partitions_to_create:
                # Create partitions
                for partition in partitions_to_create:
                    create_query = text(f"""
                        CREATE TABLE IF NOT EXISTS {schema}.{partition['name']}
                        PARTITION OF {schema}.{table}
                        FOR VALUES FROM ('{partition['start']}') TO ('{partition['end']}')
                    """)
                    await self.db.execute(create_query)
                    report["partitions_created"].append(partition['name'])
                    logger.info(f" Created partition {schema}.{partition['name']}")

                await self.db.commit()
                report["success"] = True
                report["message"] = f"Created {len(partitions_to_create)} partitions"
            else:
                report["success"] = True
                report["message"] = f"DRY RUN: Would create {len(partitions_to_create)} partitions"
                report["partitions_preview"] = [p['name'] for p in partitions_to_create]

        except Exception as e:
            report["success"] = False
            report["error"] = str(e)
            logger.error(f" Failed to create partitions for {config_key}: {e}")

        return report

    async def drop_old_partitions(
        self,
        schema: str,
        table: str,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Drop old partitions that exceed retention period

        Args:
            schema: Table schema
            table: Table name
            dry_run: If True, only show what would be dropped

        Returns:
            Operation report
        """
        config_key = f"{schema}.{table}"
        config = self.configs.get(config_key)

        if not config:
            raise ValueError(f"No partitioning config found for {config_key}")

        report = {
            "table": config_key,
            "dry_run": dry_run,
            "partitions_dropped": [],
            "success": False
        }

        try:
            # Get all partitions
            partitions = await self._list_partitions(schema, table)

            # Sort and keep only retention_partitions newest
            partitions_to_drop = []
            if len(partitions) > config.retention_partitions:
                partitions_to_drop = partitions[config.retention_partitions:]

            report["partitions_to_drop"] = len(partitions_to_drop)

            if not dry_run and partitions_to_drop:
                for partition_name in partitions_to_drop:
                    drop_query = text(f"DROP TABLE IF EXISTS {schema}.{partition_name}")
                    await self.db.execute(drop_query)
                    report["partitions_dropped"].append(partition_name)
                    logger.warning(f"️  Dropped old partition {schema}.{partition_name}")

                await self.db.commit()
                report["success"] = True
                report["message"] = f"Dropped {len(partitions_to_drop)} old partitions"
            else:
                report["success"] = True
                report["message"] = f"DRY RUN: Would drop {len(partitions_to_drop)} partitions"
                report["partitions_preview"] = partitions_to_drop

        except Exception as e:
            report["success"] = False
            report["error"] = str(e)
            logger.error(f" Failed to drop old partitions for {config_key}: {e}")

        return report

    async def get_partition_stats(self, schema: str, table: str) -> Dict[str, Any]:
        """Get statistics for all partitions of a table"""
        try:
            partitions = await self._list_partitions(schema, table)

            stats = []
            total_rows = 0
            total_size = 0

            for partition_name in partitions:
                # Get partition size and row count
                query = text(f"""
                    SELECT
                        pg_total_relation_size('{schema}.{partition_name}') as size_bytes,
                        (SELECT COUNT(*) FROM {schema}.{partition_name}) as row_count
                """)
                result = await self.db.execute(query)
                row = result.fetchone()

                size_bytes = row[0] or 0
                row_count = row[1] or 0

                stats.append({
                    "partition": partition_name,
                    "size_bytes": size_bytes,
                    "size_mb": round(size_bytes / 1024 / 1024, 2),
                    "row_count": row_count
                })

                total_rows += row_count
                total_size += size_bytes

            return {
                "table": f"{schema}.{table}",
                "partition_count": len(partitions),
                "total_rows": total_rows,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "partitions": stats
            }
        except Exception as e:
            logger.error(f"Error getting partition stats for {schema}.{table}: {e}")
            return {
                "table": f"{schema}.{table}",
                "error": str(e)
            }

    async def get_partitioning_configs(self) -> List[Dict[str, Any]]:
        """Get all partitioning configurations"""
        return [
            {
                **asdict(config),
                "table_full_name": f"{config.schema}.{config.table}"
            }
            for config in self.configs.values()
        ]
