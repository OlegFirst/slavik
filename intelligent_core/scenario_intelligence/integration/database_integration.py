"""
Database Integration for Scenario Intelligence

Использует СУЩЕСТВУЮЩИЙ DatabaseManager из infrastructure/database
"""

import logging
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add infrastructure to path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

from infrastructure.database.managers.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ScenarioDatabaseManager(DatabaseManager):
    """
    Database Manager для Scenario Intelligence

    Расширяет СУЩЕСТВУЮЩИЙ DatabaseManager для работы со схемой scenario_intelligence
    """

    def __init__(self):
        super().__init__(name="ScenarioIntelligence")
        self.schema = "scenario_intelligence"

    # =====================================================================
    # SCENARIOS
    # =====================================================================

    def save_scenario(self, scenario: Dict[str, Any]) -> bool:
        """
        Save scenario to database

        Args:
            scenario: Full scenario dict

        Returns:
            Success boolean
        """
        meta = scenario.get('meta', {})

        query = f"""
            INSERT INTO {self.schema}.scenarios (
                id, version, level, type, pillar, module, subsystem,
                content, status, iso_clauses
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id, version) DO UPDATE SET
                content = EXCLUDED.content,
                updated_at = NOW()
            RETURNING id
        """

        params = (
            meta.get('id'),
            meta.get('version', '1.0.0'),
            meta.get('level'),
            meta.get('type'),
            meta.get('pillar'),
            meta.get('module'),
            meta.get('subsystem'),
            json.dumps(scenario),
            'active',
            scenario.get('compliance', {}).get('iso_22301', {}).get('clauses', [])
        )

        try:
            result = self.execute(query, params, commit=True)
            if result:
                logger.info(f" Scenario saved: {result[0][0]}")
                return True
            return False

        except Exception as e:
            logger.error(f" Error saving scenario: {e}")
            return False

    def get_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Get scenario by ID

        Args:
            scenario_id: Scenario ID

        Returns:
            Scenario dict or None
        """
        query = f"""
            SELECT content
            FROM {self.schema}.scenarios
            WHERE id = %s AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 1
        """

        try:
            result = self.execute(query, (scenario_id,), commit=False)
            if result and len(result) > 0:
                return result[0][0]  # JSONB column
            return None

        except Exception as e:
            logger.error(f" Error getting scenario: {e}")
            return None

    def find_scenarios(
        self,
        level: Optional[int] = None,
        type: Optional[str] = None,
        module: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find scenarios by filters

        Args:
            level: Filter by level (1-4)
            type: Filter by type
            module: Filter by module

        Returns:
            List of scenarios
        """
        # Build dynamic query
        conditions = ["status = 'active'"]
        params = []

        if level is not None:
            conditions.append(f"level = %s")
            params.append(level)

        if type is not None:
            conditions.append(f"type = %s")
            params.append(type)

        if module is not None:
            conditions.append(f"module = %s")
            params.append(module)

        query = f"""
            SELECT content
            FROM {self.schema}.scenarios
            WHERE {' AND '.join(conditions)}
            ORDER BY created_at DESC
        """

        try:
            results = self.execute(query, tuple(params), commit=False)
            return [row[0] for row in results] if results else []

        except Exception as e:
            logger.error(f" Error finding scenarios: {e}")
            return []

    # =====================================================================
    # EXECUTIONS
    # =====================================================================

    def save_execution(
        self,
        scenario_id: str,
        scenario_version: str,
        result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Save execution record

        Args:
            scenario_id: Scenario ID
            scenario_version: Scenario version
            result: Execution result
            context: Execution context

        Returns:
            Execution ID (UUID) or None
        """
        query = f"""
            INSERT INTO {self.schema}.executions (
                scenario_id, scenario_version, context, status, result,
                error_message, duration_ms, steps_executed, steps_total,
                chaos_result, compliance_result, evidence_generated,
                called_scenarios, emitted_events
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """

        params = (
            scenario_id,
            scenario_version,
            json.dumps(context),
            result.get('status'),
            json.dumps(result),
            result.get('error'),
            result.get('duration', 0),
            result.get('steps_executed', 0),
            result.get('steps_total', 0),
            json.dumps(result.get('chaos_result')) if result.get('chaos_result') else None,
            json.dumps(result.get('compliance_result')) if result.get('compliance_result') else None,
            json.dumps(result.get('evidence_generated')) if result.get('evidence_generated') else None,
            result.get('called_scenarios', []),
            result.get('emitted_events', [])
        )

        try:
            exec_result = self.execute(query, params, commit=True)
            if exec_result and len(exec_result) > 0:
                execution_id = str(exec_result[0][0])
                logger.info(f" Execution saved: {execution_id}")
                return execution_id
            return None

        except Exception as e:
            logger.error(f" Error saving execution: {e}")
            return None

    def get_executions(
        self,
        scenario_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get execution history

        Args:
            scenario_id: Filter by scenario ID (optional)
            limit: Max results

        Returns:
            List of execution records
        """
        if scenario_id:
            query = f"""
                SELECT id, scenario_id, executed_at, status, result, duration_ms
                FROM {self.schema}.executions
                WHERE scenario_id = %s
                ORDER BY executed_at DESC
                LIMIT %s
            """
            params = (scenario_id, limit)
        else:
            query = f"""
                SELECT id, scenario_id, executed_at, status, result, duration_ms
                FROM {self.schema}.executions
                ORDER BY executed_at DESC
                LIMIT %s
            """
            params = (limit,)

        try:
            results = self.execute(query, params, commit=False)
            if not results:
                return []

            executions = []
            for row in results:
                executions.append({
                    'id': str(row[0]),
                    'scenario_id': row[1],
                    'executed_at': row[2].isoformat() if row[2] else None,
                    'status': row[3],
                    'result': row[4],
                    'duration_ms': row[5]
                })
            return executions

        except Exception as e:
            logger.error(f" Error getting executions: {e}")
            return []

    # =====================================================================
    # STATISTICS
    # =====================================================================

    def get_statistics(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for scenario

        Note: Statistics are auto-updated via trigger

        Args:
            scenario_id: Scenario ID

        Returns:
            Statistics dict or None
        """
        query = f"""
            SELECT
                total_executions,
                successful_executions,
                failed_executions,
                success_rate,
                avg_duration_ms,
                min_duration_ms,
                max_duration_ms,
                last_executed_at,
                last_status
            FROM {self.schema}.statistics
            WHERE scenario_id = %s
        """

        try:
            result = self.execute(query, (scenario_id,), commit=False)
            if result and len(result) > 0:
                row = result[0]
                return {
                    'total_executions': row[0],
                    'successful_executions': row[1],
                    'failed_executions': row[2],
                    'success_rate': float(row[3]) if row[3] else 0.0,
                    'avg_duration_ms': float(row[4]) if row[4] else 0.0,
                    'min_duration_ms': row[5],
                    'max_duration_ms': row[6],
                    'last_executed_at': row[7].isoformat() if row[7] else None,
                    'last_status': row[8]
                }
            return None

        except Exception as e:
            logger.error(f" Error getting statistics: {e}")
            return None

    def get_all_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for all scenarios

        Returns:
            Dict of scenario_id -> statistics
        """
        query = f"""
            SELECT scenario_id, total_executions, successful_executions,
                   failed_executions, success_rate, avg_duration_ms
            FROM {self.schema}.statistics
            ORDER BY total_executions DESC
        """

        try:
            results = self.execute(query, commit=False)
            if not results:
                return {}

            stats_dict = {}
            for row in results:
                stats_dict[row[0]] = {
                    'total_executions': row[1],
                    'successful_executions': row[2],
                    'failed_executions': row[3],
                    'success_rate': float(row[4]) if row[4] else 0.0,
                    'avg_duration_ms': float(row[5]) if row[5] else 0.0
                }
            return stats_dict

        except Exception as e:
            logger.error(f" Error getting all statistics: {e}")
            return {}


# Global instance
scenario_db_manager = ScenarioDatabaseManager()


# =====================================================================
# Helper functions
# =====================================================================

def initialize_db():
    """Initialize database connection"""
    scenario_db_manager.connect(min_conn=2, max_conn=10)
    logger.info(" Scenario Database Manager initialized")


def close_db():
    """Close database connection"""
    scenario_db_manager.disconnect()
    logger.info(" Scenario Database Manager closed")
