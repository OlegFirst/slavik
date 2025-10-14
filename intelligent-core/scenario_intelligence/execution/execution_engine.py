"""
Execution Engine - Main orchestrator for scenario execution

Coordinates:
- ScenarioExecutor: Executes scenarios
- ExecutionValidator: Validates results
- ExecutionReporter: Generates reports
- PostgresScenarioStorage: Saves execution history
- Temporal: Workflow orchestration (optional)

This is the main entry point for executing scenarios.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from .executor import ScenarioExecutor, ExecutionResult
from .validator import ExecutionValidator, ValidationReport
from .reporter import ExecutionReporter, ExecutionReport

# Import storage - handle case where it's not available
try:
    from ..storage.postgres_storage import PostgresScenarioStorage
except ImportError:
    PostgresScenarioStorage = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExecutionEngine:
    """
    Main Execution Engine - Orchestrates scenario execution

    Features:
    - Single scenario execution
    - Batch execution
    - Workflow execution (L4)
    - Result validation
    - Report generation
    - Database persistence
    - Metrics collection
    """

    def __init__(
        self,
        storage: Optional[Any] = None,
        temporal_client: Optional[Any] = None,
        save_to_db: bool = True,
        validate_results: bool = True
    ):
        """
        Initialize Execution Engine

        Args:
            storage: PostgresScenarioStorage instance
            temporal_client: Temporal client (optional)
            save_to_db: Save execution history to database
            validate_results: Validate execution results
        """
        self.storage = storage
        self.temporal_client = temporal_client
        self.save_to_db = save_to_db and storage is not None
        self.validate_results = validate_results

        self.executor = ScenarioExecutor()
        self.validator = ExecutionValidator()
        self.reporter = ExecutionReporter()

        logger.info("🚀 Execution Engine initialized")
        logger.info(f"   Storage: {'✅' if self.storage else '❌'}")
        logger.info(f"   Temporal: {'✅' if self.temporal_client else '❌'}")

    async def execute_scenario(
        self,
        scenario_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionReport:
        """
        Execute a single scenario by ID

        Args:
            scenario_id: Scenario ID to execute
            context: Execution context

        Returns:
            ExecutionReport
        """
        logger.info(f"🎯 Executing scenario: {scenario_id}")

        # Load scenario from storage
        if not self.storage:
            raise Exception("Storage not configured - cannot load scenario")

        scenario = await self.storage.get_scenario_by_id(scenario_id)
        if not scenario:
            raise Exception(f"Scenario not found: {scenario_id}")

        # Execute
        result = await self.execute_scenario_direct(scenario, context)

        return result

    async def execute_scenario_direct(
        self,
        scenario: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionReport:
        """
        Execute a scenario directly (without loading from storage)

        Args:
            scenario: Scenario definition
            context: Execution context

        Returns:
            ExecutionReport
        """
        # Execute scenario
        async with ScenarioExecutor() as executor:
            result = await executor.execute(scenario, context)

        # Validate result
        validation = None
        if self.validate_results:
            validation = self.validator.validate_result(result, scenario)

        # Generate report
        report = self.reporter.generate_report(
            results=[result],
            validations=[validation] if validation else None,
            report_type='single',
            metadata={'scenario_id': result.scenario_id}
        )

        # Save to database
        if self.save_to_db:
            await self._save_execution_history(result, validation)

        return report

    async def execute_batch(
        self,
        scenario_ids: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionReport:
        """
        Execute multiple scenarios

        Args:
            scenario_ids: List of scenario IDs
            context: Shared execution context

        Returns:
            ExecutionReport with all results
        """
        logger.info(f"📦 Executing batch: {len(scenario_ids)} scenarios")

        if not self.storage:
            raise Exception("Storage not configured - cannot load scenarios")

        results = []
        validations = []

        for scenario_id in scenario_ids:
            try:
                # Load scenario
                scenario = await self.storage.get_scenario_by_id(scenario_id)
                if not scenario:
                    logger.error(f"  ❌ Scenario not found: {scenario_id}")
                    continue

                # Execute
                async with ScenarioExecutor() as executor:
                    result = await executor.execute(scenario, context)
                    results.append(result)

                # Validate
                if self.validate_results:
                    validation = self.validator.validate_result(result, scenario)
                    validations.append(validation)

                # Save to database
                if self.save_to_db:
                    await self._save_execution_history(result, validation if self.validate_results else None)

            except Exception as e:
                logger.error(f"  ❌ Failed to execute {scenario_id}: {e}")

        # Generate combined report
        report = self.reporter.generate_report(
            results=results,
            validations=validations if validations else None,
            report_type='batch',
            metadata={'scenario_count': len(scenario_ids)}
        )

        return report

    async def execute_workflow(
        self,
        workflow_scenario: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionReport:
        """
        Execute L4 workflow scenario (combines multiple scenarios)

        Args:
            workflow_scenario: L4 workflow definition
            context: Execution context

        Returns:
            ExecutionReport
        """
        logger.info(f"🔄 Executing workflow: {workflow_scenario.get('meta', {}).get('id', 'unknown')}")

        # Handle both formats
        if 'scenario' in workflow_scenario:
            workflow_scenario = workflow_scenario['scenario']

        # Extract sub-scenarios
        workflow_config = workflow_scenario.get('workflow', {})
        sub_scenarios = workflow_config.get('scenarios', [])

        if not sub_scenarios:
            logger.warning("  ⚠️  No sub-scenarios defined in workflow")
            sub_scenarios = []

        results = []
        validations = []
        local_context = context or {}

        # Execute each sub-scenario in sequence
        for i, sub_scenario_ref in enumerate(sub_scenarios):
            sub_scenario_id = sub_scenario_ref.get('scenario_id')
            if not sub_scenario_id:
                logger.warning(f"  ⚠️  Sub-scenario {i} has no ID")
                continue

            logger.info(f"  📍 Executing sub-scenario {i+1}/{len(sub_scenarios)}: {sub_scenario_id}")

            try:
                # Load sub-scenario
                if self.storage:
                    sub_scenario = await self.storage.get_scenario_by_id(sub_scenario_id)
                else:
                    logger.warning(f"    ⚠️  Storage not available, skipping {sub_scenario_id}")
                    continue

                if not sub_scenario:
                    logger.error(f"    ❌ Sub-scenario not found: {sub_scenario_id}")
                    continue

                # Execute with shared context
                async with ScenarioExecutor() as executor:
                    result = await executor.execute(sub_scenario, local_context)
                    results.append(result)

                # Update context with result
                local_context[f"workflow.{sub_scenario_id}"] = result.to_dict()

                # Validate
                if self.validate_results:
                    validation = self.validator.validate_result(result, sub_scenario)
                    validations.append(validation)

                # Check if we should stop on failure
                stop_on_failure = sub_scenario_ref.get('stop_on_failure', True)
                if result.status == 'failed' and stop_on_failure:
                    logger.error(f"    ❌ Sub-scenario failed, stopping workflow")
                    break

            except Exception as e:
                logger.error(f"    ❌ Failed to execute sub-scenario {sub_scenario_id}: {e}")
                if sub_scenario_ref.get('stop_on_failure', True):
                    break

        # Generate workflow report
        report = self.reporter.generate_report(
            results=results,
            validations=validations if validations else None,
            report_type='workflow',
            metadata={
                'workflow_id': workflow_scenario.get('meta', {}).get('id'),
                'total_sub_scenarios': len(sub_scenarios),
                'executed_sub_scenarios': len(results)
            }
        )

        return report

    async def _save_execution_history(
        self,
        result: ExecutionResult,
        validation: Optional[ValidationReport] = None
    ):
        """Save execution history to database"""
        if not self.storage:
            return

        try:
            # Get connection pool from storage
            pool = self.storage.pool
            if not pool:
                logger.warning("  ⚠️  Database pool not available")
                return

            async with pool.acquire() as conn:
                # Prepare result data
                result_data = result.to_dict()

                # Add validation if available
                if validation:
                    result_data['validation'] = validation.to_dict()

                # Convert status to match DB enum
                status_map = {
                    'success': 'success',
                    'failed': 'failed',
                    'partial': 'failed'  # Map partial to failed for now
                }
                db_status = status_map.get(result.status, 'failed')

                # Insert execution record
                query = """
                    INSERT INTO scenario_intelligence.scenario_executions (
                        scenario_id,
                        started_at,
                        completed_at,
                        status,
                        result,
                        error_message
                    )
                    VALUES ($1, $2, $3, $4, $5::jsonb, $6)
                    RETURNING id
                """

                import json
                execution_id = await conn.fetchval(
                    query,
                    result.scenario_id,
                    result.started_at,
                    result.completed_at,
                    db_status,
                    json.dumps(result_data),
                    result.error
                )

                logger.info(f"  💾 Saved execution history: {execution_id}")

        except Exception as e:
            logger.error(f"  ❌ Failed to save execution history: {e}")

    async def get_execution_history(
        self,
        scenario_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get execution history for a scenario

        Args:
            scenario_id: Scenario ID
            limit: Maximum results

        Returns:
            List of execution records
        """
        if not self.storage or not self.storage.pool:
            return []

        try:
            async with self.storage.pool.acquire() as conn:
                query = """
                    SELECT
                        id,
                        scenario_id,
                        started_at,
                        completed_at,
                        status,
                        result,
                        error_message
                    FROM scenario_intelligence.scenario_executions
                    WHERE scenario_id = $1
                    ORDER BY started_at DESC
                    LIMIT $2
                """

                rows = await conn.fetch(query, scenario_id, limit)

                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get execution history: {e}")
            return []

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get execution statistics

        Returns:
            Statistics dict
        """
        if not self.storage or not self.storage.pool:
            return {}

        try:
            async with self.storage.pool.acquire() as conn:
                query = """
                    SELECT
                        COUNT(*) as total_executions,
                        COUNT(*) FILTER (WHERE status = 'success') as successful,
                        COUNT(*) FILTER (WHERE status = 'failed') as failed,
                        AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration,
                        MIN(started_at) as first_execution,
                        MAX(started_at) as last_execution
                    FROM scenario_intelligence.scenario_executions
                """

                row = await conn.fetchrow(query)

                return dict(row) if row else {}

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}


# Test
async def main():
    """Test Execution Engine"""
    import os

    # Create test scenario
    test_scenario = {
        'meta': {
            'id': 'test-execution-engine',
            'level': 1,
            'type': 'functional',
            'version': '1.0.0'
        },
        'description': {
            'title': 'Test Execution Engine',
            'summary': 'Testing complete execution flow'
        },
        'execution': {
            'steps': [
                {
                    'id': 'step1',
                    'action': 'mock_action',
                    'params': {'message': 'Hello'},
                    'expect': {'status': 200}
                },
                {
                    'id': 'step2',
                    'action': 'mock_action',
                    'params': {'message': 'World'},
                    'expect': {'status': 200}
                }
            ]
        }
    }

    # Initialize engine (without storage for simple test)
    engine = ExecutionEngine(storage=None, save_to_db=False)

    # Execute
    report = await engine.execute_scenario_direct(test_scenario)

    # Print report
    print("\n" + "="*60)
    print("EXECUTION ENGINE TEST REPORT:")
    print("="*60)
    print(f"Report ID: {report.report_id}")
    print(f"Type: {report.report_type}")
    print(f"Status: {report.summary['overall_status']}")
    print(f"Executions: {report.summary['total_executions']}")
    print(f"Success Rate: {report.summary['success_rate']:.1%}")
    print(f"Avg Duration: {report.summary['timing']['avg_duration']:.2f}s")
    print("\nValidation:")
    if report.validations:
        val = report.validations[0]
        print(f"  Status: {val['validation_status']}")
        print(f"  Issues: {val['summary']['total_issues']}")

    # Test with database (if available)
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL and PostgresScenarioStorage:
        print("\n" + "="*60)
        print("TESTING WITH DATABASE:")
        print("="*60)

        storage = PostgresScenarioStorage(connection_string=DATABASE_URL)
        await storage.initialize()

        engine_with_db = ExecutionEngine(storage=storage, save_to_db=True)

        # Save test scenario
        await storage.register(test_scenario)

        # Execute by ID
        report2 = await engine_with_db.execute_scenario('test-execution-engine')

        print(f"✅ Executed scenario from database")
        print(f"   Status: {report2.summary['overall_status']}")

        # Get history
        history = await engine_with_db.get_execution_history('test-execution-engine')
        print(f"✅ Retrieved {len(history)} execution history records")

        await storage.close()


if __name__ == "__main__":
    asyncio.run(main())
