"""
Scenario Executor - Executes individual scenarios and steps

Responsibilities:
- Execute scenario steps sequentially
- Measure timing for each step
- Capture outputs and errors
- Support different action types (API calls, commands, etc.)
"""

import asyncio
import logging
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import copy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class StepResult:
    """Result of a single step execution"""
    step_id: str
    action: str
    status: str  # 'success', 'failed', 'skipped'
    started_at: str
    completed_at: str
    duration_seconds: float
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionResult:
    """Result of complete scenario execution"""
    scenario_id: str
    status: str  # 'success', 'failed', 'partial'
    started_at: str
    completed_at: str
    duration_seconds: float
    steps: List[StepResult]
    context: Dict[str, Any]
    summary: Dict[str, Any]
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'scenario_id': self.scenario_id,
            'status': self.status,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'duration_seconds': self.duration_seconds,
            'steps': [step.to_dict() for step in self.steps],
            'context': self.context,
            'summary': self.summary,
            'error': self.error
        }


class ScenarioExecutor:
    """
    Executes individual scenarios

    Supports:
    - Sequential step execution
    - Action resolution (API calls, HTTP requests, mock actions)
    - Context variable substitution
    - Error handling and retries
    - Timing measurements
    """

    def __init__(self, http_timeout: int = 30):
        self.http_timeout = http_timeout
        self.http_client = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.http_client = httpx.AsyncClient(timeout=self.http_timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.http_client:
            await self.http_client.aclose()

    async def execute(self, scenario: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """
        Execute a complete scenario

        Args:
            scenario: Scenario definition
            context: Initial execution context

        Returns:
            ExecutionResult with all step results
        """
        # Handle both formats: {"scenario": {...}} and direct {...}
        if 'scenario' in scenario:
            scenario = scenario['scenario']

        start_time = datetime.utcnow()
        context = context or {}

        # Extract metadata
        meta = scenario.get('meta', {})
        scenario_id = meta.get('id', 'unknown')

        logger.info(f" Starting execution: {scenario_id}")

        try:
            # Get execution steps
            execution_config = scenario.get('execution', {})
            steps = execution_config.get('steps', [])

            # If no execution steps, look in test_scenarios
            if not steps:
                test_scenarios = scenario.get('test_scenarios', [])
                if test_scenarios:
                    # Use first test scenario for MVP
                    first_test = test_scenarios[0]
                    steps = first_test.get('steps', [])

            if not steps:
                logger.warning(f"  ️  No execution steps found in scenario")
                steps = []

            # Execute all steps
            step_results = []
            local_context = copy.deepcopy(context)

            for step in steps:
                step_result = await self.execute_step(step, local_context)
                step_results.append(step_result)

                # Update context with step result
                local_context[f"steps.{step_result.step_id}"] = step_result.output

                # Stop on error if configured
                if step_result.status == 'failed' and step.get('stop_on_error', True):
                    logger.error(f"   Step {step_result.step_id} failed, stopping execution")
                    break

            # Calculate overall status
            failed_steps = [s for s in step_results if s.status == 'failed']
            success_steps = [s for s in step_results if s.status == 'success']

            if not step_results:
                overall_status = 'success'  # No steps = success (scenario validation only)
            elif failed_steps:
                overall_status = 'partial' if success_steps else 'failed'
            else:
                overall_status = 'success'

            # Calculate duration
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            # Create summary
            summary = {
                'total_steps': len(step_results),
                'successful_steps': len(success_steps),
                'failed_steps': len(failed_steps),
                'skipped_steps': len([s for s in step_results if s.status == 'skipped'])
            }

            logger.info(f" Execution completed: {scenario_id} ({overall_status})")
            logger.info(f"   Duration: {duration:.2f}s, Steps: {len(success_steps)}/{len(step_results)} passed")

            return ExecutionResult(
                scenario_id=scenario_id,
                status=overall_status,
                started_at=start_time.isoformat(),
                completed_at=end_time.isoformat(),
                duration_seconds=duration,
                steps=step_results,
                context=local_context,
                summary=summary
            )

        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            logger.error(f" Execution failed: {scenario_id} - {e}")

            return ExecutionResult(
                scenario_id=scenario_id,
                status='failed',
                started_at=start_time.isoformat(),
                completed_at=end_time.isoformat(),
                duration_seconds=duration,
                steps=[],
                context=context,
                summary={'error': 'Execution crashed'},
                error=str(e)
            )

    async def execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> StepResult:
        """
        Execute a single step

        Args:
            step: Step definition
            context: Current execution context

        Returns:
            StepResult with execution details
        """
        step_id = step.get('id', 'unknown')
        action = step.get('action', 'unknown')

        start_time = datetime.utcnow()

        logger.info(f"  ️  Executing step: {step_id} (action: {action})")

        try:
            # Resolve parameters
            params = self._resolve_params(step.get('params', {}), context)

            # Execute action based on type
            output = await self._execute_action(action, params, step, context)

            # Check expectations if defined
            expectations = step.get('expect', step.get('expected', {}))
            if expectations:
                self._validate_expectations(expectations, output)

            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            logger.info(f"     Step completed: {step_id} ({duration:.2f}s)")

            return StepResult(
                step_id=step_id,
                action=action,
                status='success',
                started_at=start_time.isoformat(),
                completed_at=end_time.isoformat(),
                duration_seconds=duration,
                output=output
            )

        except Exception as e:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            logger.error(f"     Step failed: {step_id} - {e}")

            return StepResult(
                step_id=step_id,
                action=action,
                status='failed',
                started_at=start_time.isoformat(),
                completed_at=end_time.isoformat(),
                duration_seconds=duration,
                error=str(e)
            )

    async def _execute_action(
        self,
        action: str,
        params: Dict[str, Any],
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute specific action type

        Supports:
        - HTTP requests (GET, POST, PUT, DELETE)
        - Health checks
        - Mock/simulated actions
        """
        # HTTP request actions
        if action in ['http_request', 'api_call', 'check_availability', 'check_health_endpoint']:
            return await self._execute_http_request(step, params)

        # Method-specific shortcuts
        method = step.get('method', '').upper()
        if method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            return await self._execute_http_request(step, params)

        # Mock actions for testing
        return await self._execute_mock_action(action, params)

    async def _execute_http_request(self, step: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP request"""
        method = step.get('method', 'GET').upper()

        # Get endpoint from step or params
        endpoint = step.get('endpoint') or step.get('url') or params.get('endpoint') or params.get('url')

        if not endpoint:
            raise ValueError("No endpoint/url specified for HTTP request")

        # Prepare request
        headers = params.get('headers', {})
        payload = params.get('payload', params.get('body'))

        logger.debug(f"      HTTP {method} {endpoint}")

        if not self.http_client:
            self.http_client = httpx.AsyncClient(timeout=self.http_timeout)

        try:
            # Execute request
            response = await self.http_client.request(
                method=method,
                url=endpoint,
                headers=headers,
                json=payload if payload else None,
                follow_redirects=True
            )

            # Parse response
            try:
                response_data = response.json()
            except:
                response_data = {'text': response.text}

            return {
                'status': response.status_code,
                'status_code': response.status_code,
                'http_status': response.status_code,
                'headers': dict(response.headers),
                'data': response_data,
                'response': response_data,
                'response_time': response.elapsed.total_seconds(),
                'success': 200 <= response.status_code < 300
            }

        except httpx.TimeoutException:
            raise Exception(f"Request timeout after {self.http_timeout}s")
        except Exception as e:
            raise Exception(f"HTTP request failed: {e}")

    async def _execute_mock_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mock action for testing"""
        logger.debug(f"      Mock action: {action}")

        # Simulate some processing time
        await asyncio.sleep(0.1)

        return {
            'action': action,
            'params': params,
            'status': 200,
            'success': True,
            'simulated': True,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _resolve_params(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve variables in parameters from context

        Supports {{variable}} syntax
        """
        if not params:
            return {}

        resolved = {}

        for key, value in params.items():
            if isinstance(value, str) and '{{' in value and '}}' in value:
                # Variable substitution
                var_path = value.replace('{{', '').replace('}}', '').strip()
                resolved_value = self._get_from_context(var_path, context)
                resolved[key] = resolved_value if resolved_value is not None else value
            elif isinstance(value, dict):
                resolved[key] = self._resolve_params(value, context)
            elif isinstance(value, list):
                resolved[key] = [
                    self._resolve_params(item, context) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                resolved[key] = value

        return resolved

    def _get_from_context(self, path: str, context: Dict[str, Any]) -> Any:
        """Get value from context using dot notation"""
        parts = path.split('.')
        value = context

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return None
            else:
                return None

        return value

    def _validate_expectations(self, expectations: Dict[str, Any], output: Dict[str, Any]):
        """
        Validate output against expectations

        Raises exception if validation fails
        """
        # Check status/status_code
        for status_key in ['status', 'status_code', 'http_status']:
            if status_key in expectations:
                expected = expectations[status_key]
                actual = output.get(status_key) or output.get('status')
                if actual != expected:
                    raise Exception(f"Expected {status_key}={expected}, got {actual}")

        # Check response fields
        if 'response_contains' in expectations:
            response_data = output.get('data', output.get('response', {}))
            for field in expectations['response_contains']:
                if field not in str(response_data):
                    raise Exception(f"Expected field '{field}' not in response")

        # Check response time
        if 'response_time_max' in expectations:
            max_time_str = expectations['response_time_max']
            max_time = self._parse_duration(max_time_str)
            actual_time = output.get('response_time', 0)
            if actual_time > max_time:
                raise Exception(f"Response time {actual_time}s exceeds max {max_time}s")

    def _parse_duration(self, duration_str: str) -> float:
        """Parse duration string like '2s', '500ms' to seconds"""
        duration_str = str(duration_str).lower().strip()

        if duration_str.endswith('ms'):
            return float(duration_str[:-2]) / 1000
        elif duration_str.endswith('s'):
            return float(duration_str[:-1])
        elif duration_str.endswith('m'):
            return float(duration_str[:-1]) * 60
        else:
            # Assume seconds
            return float(duration_str)


# Test
async def main():
    """Test ScenarioExecutor"""

    # Simple test scenario
    test_scenario = {
        'meta': {
            'id': 'test-executor',
            'level': 1,
            'type': 'functional'
        },
        'execution': {
            'steps': [
                {
                    'id': 'step1',
                    'action': 'mock_action',
                    'params': {
                        'message': 'Hello World'
                    },
                    'expect': {
                        'status': 200
                    }
                },
                {
                    'id': 'step2',
                    'action': 'mock_action',
                    'params': {
                        'previous': '{{steps.step1.message}}'
                    }
                }
            ]
        }
    }

    async with ScenarioExecutor() as executor:
        result = await executor.execute(test_scenario)

        print("\n" + "="*60)
        print("EXECUTION RESULT:")
        print("="*60)
        print(f"Status: {result.status}")
        print(f"Duration: {result.duration_seconds:.2f}s")
        print(f"Steps: {result.summary['successful_steps']}/{result.summary['total_steps']} passed")
        print("\nStep Results:")
        for step in result.steps:
            print(f"  - {step.step_id}: {step.status} ({step.duration_seconds:.2f}s)")


if __name__ == "__main__":
    asyncio.run(main())
