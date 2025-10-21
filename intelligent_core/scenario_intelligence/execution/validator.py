"""
Execution Validator - Validates execution results against expected outcomes

Responsibilities:
- Validate step results
- Validate overall scenario success
- Check compliance with expectations
- Generate validation reports
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from .executor import ExecutionResult, StepResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Single validation issue"""
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'step', 'timing', 'output', 'compliance'
    message: str
    step_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationReport:
    """Complete validation report"""
    scenario_id: str
    is_valid: bool
    validation_status: str  # 'passed', 'failed', 'warning'
    issues: List[ValidationIssue]
    summary: Dict[str, Any]
    validated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'scenario_id': self.scenario_id,
            'is_valid': self.is_valid,
            'validation_status': self.validation_status,
            'issues': [issue.to_dict() for issue in self.issues],
            'summary': self.summary,
            'validated_at': self.validated_at
        }


class ExecutionValidator:
    """
    Validates execution results

    Checks:
    - Step execution success
    - Timing requirements
    - Output validation
    - Compliance with scenario expectations
    """

    def __init__(self):
        self.validation_rules = {}

    def validate_result(self, result: ExecutionResult, scenario: Dict[str, Any]) -> ValidationReport:
        """
        Validate complete execution result

        Args:
            result: Execution result
            scenario: Original scenario definition

        Returns:
            ValidationReport with all issues
        """
        from datetime import datetime

        logger.info(f" Validating execution: {result.scenario_id}")

        # Handle both formats
        if 'scenario' in scenario:
            scenario = scenario['scenario']

        issues = []

        # 1. Validate overall status
        if result.status == 'failed':
            issues.append(ValidationIssue(
                severity='error',
                category='execution',
                message='Scenario execution failed',
                details={'error': result.error}
            ))
        elif result.status == 'partial':
            issues.append(ValidationIssue(
                severity='warning',
                category='execution',
                message='Scenario execution partially failed',
                details={'summary': result.summary}
            ))

        # 2. Validate each step
        step_issues = self._validate_steps(result.steps, scenario)
        issues.extend(step_issues)

        # 3. Validate timing requirements
        timing_issues = self._validate_timing(result, scenario)
        issues.extend(timing_issues)

        # 4. Validate compliance (if defined)
        compliance_issues = self._validate_compliance(result, scenario)
        issues.extend(compliance_issues)

        # Determine overall validation status
        errors = [i for i in issues if i.severity == 'error']
        warnings = [i for i in issues if i.severity == 'warning']

        if errors:
            validation_status = 'failed'
            is_valid = False
        elif warnings:
            validation_status = 'warning'
            is_valid = True
        else:
            validation_status = 'passed'
            is_valid = True

        # Create summary
        summary = {
            'total_issues': len(issues),
            'errors': len(errors),
            'warnings': len(warnings),
            'info': len([i for i in issues if i.severity == 'info']),
            'steps_validated': len(result.steps),
            'duration_seconds': result.duration_seconds
        }

        logger.info(f"  {'' if is_valid else ''} Validation: {validation_status} "
                   f"({len(errors)} errors, {len(warnings)} warnings)")

        return ValidationReport(
            scenario_id=result.scenario_id,
            is_valid=is_valid,
            validation_status=validation_status,
            issues=issues,
            summary=summary,
            validated_at=datetime.utcnow().isoformat()
        )

    def _validate_steps(self, steps: List[StepResult], scenario: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate individual step results"""
        issues = []

        for step_result in steps:
            # Check for failed steps
            if step_result.status == 'failed':
                issues.append(ValidationIssue(
                    severity='error',
                    category='step',
                    message=f"Step {step_result.step_id} failed",
                    step_id=step_result.step_id,
                    details={'error': step_result.error}
                ))

            # Check step timing if defined
            step_def = self._find_step_definition(step_result.step_id, scenario)
            if step_def:
                max_duration = step_def.get('max_duration')
                if max_duration:
                    max_seconds = self._parse_duration(max_duration)
                    if step_result.duration_seconds > max_seconds:
                        issues.append(ValidationIssue(
                            severity='warning',
                            category='timing',
                            message=f"Step {step_result.step_id} exceeded max duration",
                            step_id=step_result.step_id,
                            details={
                                'actual': step_result.duration_seconds,
                                'max': max_seconds
                            }
                        ))

        return issues

    def _validate_timing(self, result: ExecutionResult, scenario: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate timing requirements"""
        issues = []

        # Check overall execution time
        execution_config = scenario.get('execution', {})
        max_execution_time = execution_config.get('max_execution_time')

        if max_execution_time:
            max_seconds = self._parse_duration(max_execution_time)
            if result.duration_seconds > max_seconds:
                issues.append(ValidationIssue(
                    severity='warning',
                    category='timing',
                    message='Scenario exceeded max execution time',
                    details={
                        'actual': result.duration_seconds,
                        'max': max_seconds
                    }
                ))

        # Check for slow steps (arbitrary threshold)
        slow_threshold = 10.0  # seconds
        for step in result.steps:
            if step.duration_seconds > slow_threshold:
                issues.append(ValidationIssue(
                    severity='info',
                    category='timing',
                    message=f"Step {step.step_id} took longer than expected",
                    step_id=step.step_id,
                    details={'duration': step.duration_seconds}
                ))

        return issues

    def _validate_compliance(self, result: ExecutionResult, scenario: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate compliance requirements"""
        issues = []

        compliance_config = scenario.get('compliance', {})

        # Check required steps completed
        required_steps = compliance_config.get('required_steps', [])
        completed_step_ids = {s.step_id for s in result.steps if s.status == 'success'}

        for required_step in required_steps:
            if required_step not in completed_step_ids:
                issues.append(ValidationIssue(
                    severity='error',
                    category='compliance',
                    message=f"Required step '{required_step}' not completed",
                    details={'required_step': required_step}
                ))

        # Check minimum success rate
        min_success_rate = compliance_config.get('min_success_rate')
        if min_success_rate:
            total_steps = len(result.steps)
            if total_steps > 0:
                success_steps = len([s for s in result.steps if s.status == 'success'])
                success_rate = success_steps / total_steps

                if success_rate < min_success_rate:
                    issues.append(ValidationIssue(
                        severity='error',
                        category='compliance',
                        message='Success rate below minimum',
                        details={
                            'actual': success_rate,
                            'required': min_success_rate
                        }
                    ))

        return issues

    def validate_step(self, step_result: StepResult, expected: Dict[str, Any]) -> bool:
        """
        Validate individual step result

        Args:
            step_result: Step execution result
            expected: Expected outcomes

        Returns:
            True if valid
        """
        if step_result.status != 'success':
            return False

        # Check status code
        if 'status' in expected or 'status_code' in expected:
            expected_status = expected.get('status') or expected.get('status_code')
            actual_status = None

            if step_result.output:
                actual_status = (step_result.output.get('status') or
                               step_result.output.get('status_code'))

            if actual_status != expected_status:
                return False

        # Check response contains
        if 'response_contains' in expected and step_result.output:
            response_str = str(step_result.output)
            for field in expected['response_contains']:
                if field not in response_str:
                    return False

        return True

    def _find_step_definition(self, step_id: str, scenario: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find step definition in scenario"""
        # Check execution steps
        execution_steps = scenario.get('execution', {}).get('steps', [])
        for step in execution_steps:
            if step.get('id') == step_id:
                return step

        # Check test scenarios
        test_scenarios = scenario.get('test_scenarios', [])
        for test_scenario in test_scenarios:
            for step in test_scenario.get('steps', []):
                if step.get('id') == step_id:
                    return step

        return None

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
            return float(duration_str)


# Test
if __name__ == "__main__":
    from datetime import datetime

    # Mock execution result
    mock_result = ExecutionResult(
        scenario_id='test-scenario',
        status='success',
        started_at=datetime.utcnow().isoformat(),
        completed_at=datetime.utcnow().isoformat(),
        duration_seconds=1.5,
        steps=[
            StepResult(
                step_id='step1',
                action='mock',
                status='success',
                started_at=datetime.utcnow().isoformat(),
                completed_at=datetime.utcnow().isoformat(),
                duration_seconds=0.5,
                output={'status': 200}
            )
        ],
        context={},
        summary={'total_steps': 1, 'successful_steps': 1, 'failed_steps': 0}
    )

    mock_scenario = {
        'meta': {'id': 'test-scenario'},
        'execution': {
            'steps': [
                {'id': 'step1', 'action': 'mock'}
            ]
        }
    }

    validator = ExecutionValidator()
    report = validator.validate_result(mock_result, mock_scenario)

    print("\n" + "="*60)
    print("VALIDATION REPORT:")
    print("="*60)
    print(f"Status: {report.validation_status}")
    print(f"Valid: {report.is_valid}")
    print(f"Issues: {len(report.issues)}")
    print(f"Summary: {report.summary}")
