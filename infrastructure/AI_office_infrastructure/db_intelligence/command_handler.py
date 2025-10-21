"""
Command Handler for Orchestrator Commands

Handles commands sent directly from AI Orchestrator
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import text

from orchestrator_integration import OrchestratorCommand, CommandResult

logger = logging.getLogger(__name__)


class CommandHandler:
    """
    Handles commands from AI Orchestrator

    Commands:
    - optimize_query: Apply optimization (create index, rewrite query)
    - kill_query: Terminate long-running query
    - vacuum_table: Run VACUUM on table
    - analyze_table: Run ANALYZE on table
    - create_index: Create database index
    - reindex_table: Rebuild indexes
    """

    def __init__(self, db_intelligence_service):
        self.service = db_intelligence_service

    async def handle_command(self, command: OrchestratorCommand) -> CommandResult:
        """
        Route command to appropriate handler

        Returns result for reporting back to Orchestrator
        """
        start_time = datetime.now()

        try:
            if command.command_type == "optimize_query":
                result = await self._handle_optimize_query(command)

            elif command.command_type == "kill_query":
                result = await self._handle_kill_query(command)

            elif command.command_type == "vacuum_table":
                result = await self._handle_vacuum_table(command)

            elif command.command_type == "analyze_table":
                result = await self._handle_analyze_table(command)

            elif command.command_type == "create_index":
                result = await self._handle_create_index(command)

            elif command.command_type == "reindex_table":
                result = await self._handle_reindex_table(command)

            else:
                return CommandResult(
                    command_id=command.command_id,
                    status="failed",
                    error=f"Unknown command type: {command.command_type}"
                )

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return CommandResult(
                command_id=command.command_id,
                status="success",
                result=result,
                execution_time_ms=execution_time
            )

        except Exception as e:
            logger.error(f"Command execution failed: {e}")

            return CommandResult(
                command_id=command.command_id,
                status="failed",
                error=str(e)
            )

    # =========================================================================
    # COMMAND HANDLERS
    # =========================================================================

    async def _handle_optimize_query(self, command: OrchestratorCommand) -> Dict[str, Any]:
        """
        Apply query optimization

        Parameters:
        - query_hash: str
        - optimization_type: "create_index" | "rewrite_query"
        - details: Dict with specifics
        """
        from infrastructure.database import get_db_session

        query_hash = command.parameters.get("query_hash")
        optimization_type = command.parameters.get("optimization_type")
        details = command.parameters.get("details", {})

        if optimization_type == "create_index":
            # Create index
            table = details.get("table")
            column = details.get("column")
            index_name = details.get("index_name", f"idx_{table}_{column}")

            async with get_db_session() as session:
                await session.execute(text(f"""
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name}
                    ON {table}({column})
                """))

            logger.info(f" Created index: {index_name} on {table}({column})")

            return {
                "optimization_applied": "create_index",
                "index_name": index_name,
                "table": table,
                "column": column
            }

        elif optimization_type == "rewrite_query":
            # Query rewrite would be more complex
            # For now, just log
            logger.info(f"Query rewrite requested for {query_hash}")

            return {
                "optimization_applied": "rewrite_query",
                "status": "logged_for_manual_review"
            }

        else:
            raise ValueError(f"Unknown optimization type: {optimization_type}")

    async def _handle_kill_query(self, command: OrchestratorCommand) -> Dict[str, Any]:
        """
        Kill long-running or problematic query

        Parameters:
        - pid: int - Process ID to kill
        - reason: str
        """
        from infrastructure.database import get_db_session

        pid = command.parameters.get("pid")
        reason = command.parameters.get("reason", "Unknown")

        async with get_db_session() as session:
            # Terminate backend process
            result = await session.execute(text(f"""
                SELECT pg_terminate_backend({pid})
            """))

            terminated = result.scalar()

        logger.info(f" Killed query PID {pid}: {reason}")

        return {
            "killed": terminated,
            "pid": pid,
            "reason": reason
        }

    async def _handle_vacuum_table(self, command: OrchestratorCommand) -> Dict[str, Any]:
        """
        Run VACUUM on table

        Parameters:
        - schema: str
        - table: str
        - full: bool (default False)
        - analyze: bool (default True)
        """
        from infrastructure.database import get_db_session

        schema = command.parameters.get("schema", "public")
        table = command.parameters.get("table")
        full = command.parameters.get("full", False)
        analyze = command.parameters.get("analyze", True)

        if not table:
            raise ValueError("table parameter required")

        vacuum_cmd = "VACUUM FULL" if full else "VACUUM"
        if analyze:
            vacuum_cmd += " ANALYZE"

        async with get_db_session() as session:
            await session.execute(text(f"""
                {vacuum_cmd} {schema}.{table}
            """))

        logger.info(f" {vacuum_cmd} {schema}.{table}")

        return {
            "vacuum_type": "full" if full else "standard",
            "analyzed": analyze,
            "schema": schema,
            "table": table
        }

    async def _handle_analyze_table(self, command: OrchestratorCommand) -> Dict[str, Any]:
        """
        Run ANALYZE on table to update statistics

        Parameters:
        - schema: str
        - table: str
        """
        from infrastructure.database import get_db_session

        schema = command.parameters.get("schema", "public")
        table = command.parameters.get("table")

        if not table:
            raise ValueError("table parameter required")

        async with get_db_session() as session:
            await session.execute(text(f"""
                ANALYZE {schema}.{table}
            """))

        logger.info(f" ANALYZE {schema}.{table}")

        return {
            "schema": schema,
            "table": table,
            "statistics_updated": True
        }

    async def _handle_create_index(self, command: OrchestratorCommand) -> Dict[str, Any]:
        """
        Create database index

        Parameters:
        - schema: str
        - table: str
        - column: str or List[str]
        - index_name: str (optional)
        - index_type: str (btree, gin, gist, etc.)
        - concurrent: bool (default True)
        """
        from infrastructure.database import get_db_session

        schema = command.parameters.get("schema", "public")
        table = command.parameters.get("table")
        column = command.parameters.get("column")
        index_name = command.parameters.get("index_name")
        index_type = command.parameters.get("index_type", "btree")
        concurrent = command.parameters.get("concurrent", True)

        if not table or not column:
            raise ValueError("table and column parameters required")

        # Generate index name if not provided
        if not index_name:
            col_str = column if isinstance(column, str) else "_".join(column)
            index_name = f"idx_{table}_{col_str}"

        # Build column list
        if isinstance(column, list):
            columns_str = ", ".join(column)
        else:
            columns_str = column

        # Build CREATE INDEX command
        cmd = "CREATE INDEX"
        if concurrent:
            cmd += " CONCURRENTLY"
        cmd += f" IF NOT EXISTS {index_name}"
        cmd += f" ON {schema}.{table}"
        cmd += f" USING {index_type}"
        cmd += f" ({columns_str})"

        async with get_db_session() as session:
            await session.execute(text(cmd))

        logger.info(f" Created index: {index_name}")

        return {
            "index_name": index_name,
            "schema": schema,
            "table": table,
            "columns": column,
            "index_type": index_type,
            "concurrent": concurrent
        }

    async def _handle_reindex_table(self, command: OrchestratorCommand) -> Dict[str, Any]:
        """
        Rebuild all indexes on table

        Parameters:
        - schema: str
        - table: str
        - concurrent: bool (default True)
        """
        from infrastructure.database import get_db_session

        schema = command.parameters.get("schema", "public")
        table = command.parameters.get("table")
        concurrent = command.parameters.get("concurrent", True)

        if not table:
            raise ValueError("table parameter required")

        cmd = "REINDEX"
        if concurrent:
            cmd += " (CONCURRENTLY)"
        cmd += f" TABLE {schema}.{table}"

        async with get_db_session() as session:
            await session.execute(text(cmd))

        logger.info(f" REINDEX {schema}.{table}")

        return {
            "schema": schema,
            "table": table,
            "concurrent": concurrent,
            "reindexed": True
        }
