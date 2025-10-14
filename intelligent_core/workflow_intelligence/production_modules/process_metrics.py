"""
Prometheus Metrics for Process Framework

Comprehensive metrics tracking for business process execution, monitoring,
and analysis. Provides insights into process performance, validation quality,
and operational health.

Metrics Categories:
- Process Execution: Start, completion, duration tracking
- Step Execution: Individual step performance and results
- Validation: Field validation errors and patterns
- Document Generation: Template usage and format distribution
- Active Processes: Real-time process instance monitoring
- Approvals: Pending approval tracking

Usage:
    from intelligent_core.workflow_intelligence.metrics import (
        process_metrics,
        track_process_execution,
        track_step_execution
    )

    # Use decorators
    @track_process_execution(process_id="bia_process")
    async def execute_process():
        ...

    # Or track manually
    process_metrics.track_process_start("bia_process")
    process_metrics.track_step_execution("bia_process", "risk_assessment", 1.5, "success")
"""

from prometheus_client import Counter, Histogram, Gauge
from functools import wraps
import time
from typing import Optional, Literal
import asyncio


# ============================================================================
# COUNTERS - Monotonically increasing values
# ============================================================================

process_framework_process_started_total = Counter(
    'process_framework_process_started_total',
    'Total number of process instances started',
    ['process_id'],
    unit='processes'
)
"""
Counter: Total process instances started

Labels:
- process_id: Unique identifier of the process definition (e.g., 'bia_process', 'risk_assessment')

Example values:
- process_framework_process_started_total{process_id="bia_process"} 142
- process_framework_process_started_total{process_id="risk_assessment"} 87
"""

process_framework_process_completed_total = Counter(
    'process_framework_process_completed_total',
    'Total number of process instances completed',
    ['process_id', 'status'],
    unit='processes'
)
"""
Counter: Total process instances completed

Labels:
- process_id: Unique identifier of the process definition
- status: Completion status (completed, cancelled, suspended, failed)

Example values:
- process_framework_process_completed_total{process_id="bia_process",status="completed"} 128
- process_framework_process_completed_total{process_id="bia_process",status="cancelled"} 8
- process_framework_process_completed_total{process_id="risk_assessment",status="completed"} 79
"""

process_framework_step_executed_total = Counter(
    'process_framework_step_executed_total',
    'Total number of process steps executed',
    ['process_id', 'step_id', 'result'],
    unit='steps'
)
"""
Counter: Total process steps executed

Labels:
- process_id: Process definition identifier
- step_id: Step identifier within the process (e.g., 'collect_data', 'approval', 'analysis')
- result: Execution result (success, error, skipped, validation_failed)

Example values:
- process_framework_step_executed_total{process_id="bia_process",step_id="collect_data",result="success"} 142
- process_framework_step_executed_total{process_id="bia_process",step_id="approval",result="error"} 3
"""

process_framework_validation_errors_total = Counter(
    'process_framework_validation_errors_total',
    'Total number of validation errors by field',
    ['process_id', 'step_id', 'field_name'],
    unit='errors'
)
"""
Counter: Total validation errors encountered

Labels:
- process_id: Process definition identifier
- step_id: Step where validation occurred
- field_name: Name of the field that failed validation

Example values:
- process_framework_validation_errors_total{process_id="bia_process",step_id="collect_data",field_name="rto_value"} 12
- process_framework_validation_errors_total{process_id="bia_process",step_id="collect_data",field_name="impact_score"} 8

Use this to identify problematic fields that frequently cause validation issues.
"""

process_framework_documents_generated_total = Counter(
    'process_framework_documents_generated_total',
    'Total number of documents generated from templates',
    ['template_id', 'format'],
    unit='documents'
)
"""
Counter: Total documents generated

Labels:
- template_id: Document template identifier (e.g., 'bia_report', 'risk_assessment_report')
- format: Output format (pdf, docx, html, json)

Example values:
- process_framework_documents_generated_total{template_id="bia_report",format="pdf"} 95
- process_framework_documents_generated_total{template_id="bia_report",format="docx"} 47
- process_framework_documents_generated_total{template_id="risk_assessment_report",format="pdf"} 68

Helps track document generation patterns and format preferences.
"""


# ============================================================================
# HISTOGRAMS - Distribution of observed values
# ============================================================================

process_framework_step_execution_duration_seconds = Histogram(
    'process_framework_step_execution_duration_seconds',
    'Step execution duration in seconds',
    ['process_id', 'step_id'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 300.0]
)
"""
Histogram: Step execution duration distribution

Labels:
- process_id: Process definition identifier
- step_id: Step identifier

Buckets: [1ms, 5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s, 10s, 30s, 1min, 5min]

Provides:
- process_framework_step_execution_duration_seconds_bucket{le="0.1"}: Count of steps completed in <= 100ms
- process_framework_step_execution_duration_seconds_sum: Total time spent in step execution
- process_framework_step_execution_duration_seconds_count: Total number of step executions

Example queries:
- Average step duration: rate(process_framework_step_execution_duration_seconds_sum[5m]) /
                        rate(process_framework_step_execution_duration_seconds_count[5m])
- 95th percentile: histogram_quantile(0.95, process_framework_step_execution_duration_seconds_bucket)
"""

process_framework_process_duration_seconds = Histogram(
    'process_framework_process_duration_seconds',
    'Complete process execution duration in seconds',
    ['process_id'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0, 1800.0, 3600.0, 7200.0, 14400.0, 86400.0]
)
"""
Histogram: Complete process duration distribution

Labels:
- process_id: Process definition identifier

Buckets: [1s, 5s, 10s, 30s, 1min, 5min, 10min, 30min, 1h, 2h, 4h, 24h]

Provides:
- process_framework_process_duration_seconds_bucket{le="300"}: Count of processes completed in <= 5 minutes
- process_framework_process_duration_seconds_sum: Total time spent in process execution
- process_framework_process_duration_seconds_count: Total number of completed processes

Example queries:
- Average process duration: rate(process_framework_process_duration_seconds_sum[1h]) /
                           rate(process_framework_process_duration_seconds_count[1h])
- 99th percentile: histogram_quantile(0.99, process_framework_process_duration_seconds_bucket)
"""


# ============================================================================
# GAUGES - Current state values that can go up or down
# ============================================================================

process_framework_active_instances = Gauge(
    'process_framework_active_instances',
    'Number of currently active process instances',
    ['process_id']
)
"""
Gauge: Currently active process instances

Labels:
- process_id: Process definition identifier

Example values:
- process_framework_active_instances{process_id="bia_process"} 14
- process_framework_active_instances{process_id="risk_assessment"} 8

Use this to monitor:
- Process execution load
- Stuck or long-running processes
- Capacity planning

Alert example:
- Alert if process_framework_active_instances{process_id="bia_process"} > 50
"""

process_framework_pending_approvals = Gauge(
    'process_framework_pending_approvals',
    'Number of process steps waiting for approval',
    ['process_id', 'step_id']
)
"""
Gauge: Pending approval count

Labels:
- process_id: Process definition identifier
- step_id: Approval step identifier

Example values:
- process_framework_pending_approvals{process_id="bia_process",step_id="manager_approval"} 5
- process_framework_pending_approvals{process_id="risk_assessment",step_id="final_approval"} 3

Use this to monitor:
- Approval bottlenecks
- SLA compliance
- Workload distribution

Alert example:
- Alert if process_framework_pending_approvals > 10 for 15 minutes
"""


# ============================================================================
# PROCESS METRICS CLASS
# ============================================================================

class ProcessMetrics:
    """
    Centralized metrics tracking for Process Framework

    Provides high-level methods to track process and step execution,
    validation errors, and document generation.

    Example usage:
        process_metrics.track_process_start("bia_process")
        process_metrics.track_step_execution("bia_process", "collect_data", 1.5, "success")
        process_metrics.track_validation_error("bia_process", "collect_data", "rto_value")
    """

    @staticmethod
    def track_process_start(process_id: str):
        """
        Track process instance start

        Args:
            process_id: Unique identifier of the process definition
        """
        process_framework_process_started_total.labels(process_id=process_id).inc()

    @staticmethod
    def track_process_completion(
        process_id: str,
        status: Literal["completed", "cancelled", "suspended", "failed"],
        duration_seconds: float
    ):
        """
        Track process instance completion

        Args:
            process_id: Process definition identifier
            status: Completion status
            duration_seconds: Total process execution time
        """
        process_framework_process_completed_total.labels(
            process_id=process_id,
            status=status
        ).inc()

        process_framework_process_duration_seconds.labels(
            process_id=process_id
        ).observe(duration_seconds)

    @staticmethod
    def track_step_execution(
        process_id: str,
        step_id: str,
        duration_seconds: float,
        result: Literal["success", "error", "skipped", "validation_failed"]
    ):
        """
        Track step execution

        Args:
            process_id: Process definition identifier
            step_id: Step identifier
            duration_seconds: Step execution time
            result: Execution result
        """
        process_framework_step_executed_total.labels(
            process_id=process_id,
            step_id=step_id,
            result=result
        ).inc()

        process_framework_step_execution_duration_seconds.labels(
            process_id=process_id,
            step_id=step_id
        ).observe(duration_seconds)

    @staticmethod
    def track_validation_error(process_id: str, step_id: str, field_name: str):
        """
        Track validation error

        Args:
            process_id: Process definition identifier
            step_id: Step where validation occurred
            field_name: Field that failed validation
        """
        process_framework_validation_errors_total.labels(
            process_id=process_id,
            step_id=step_id,
            field_name=field_name
        ).inc()

    @staticmethod
    def track_document_generation(template_id: str, format: str):
        """
        Track document generation

        Args:
            template_id: Document template identifier
            format: Output format (pdf, docx, html, json)
        """
        process_framework_documents_generated_total.labels(
            template_id=template_id,
            format=format
        ).inc()

    @staticmethod
    def update_active_instances(process_id: str, count: int):
        """
        Update active instance count

        Args:
            process_id: Process definition identifier
            count: Current number of active instances
        """
        process_framework_active_instances.labels(process_id=process_id).set(count)

    @staticmethod
    def increment_active_instances(process_id: str):
        """
        Increment active instance count

        Args:
            process_id: Process definition identifier
        """
        process_framework_active_instances.labels(process_id=process_id).inc()

    @staticmethod
    def decrement_active_instances(process_id: str):
        """
        Decrement active instance count

        Args:
            process_id: Process definition identifier
        """
        process_framework_active_instances.labels(process_id=process_id).dec()

    @staticmethod
    def update_pending_approvals(process_id: str, step_id: str, count: int):
        """
        Update pending approval count

        Args:
            process_id: Process definition identifier
            step_id: Approval step identifier
            count: Current number of pending approvals
        """
        process_framework_pending_approvals.labels(
            process_id=process_id,
            step_id=step_id
        ).set(count)

    @staticmethod
    def increment_pending_approvals(process_id: str, step_id: str):
        """
        Increment pending approval count

        Args:
            process_id: Process definition identifier
            step_id: Approval step identifier
        """
        process_framework_pending_approvals.labels(
            process_id=process_id,
            step_id=step_id
        ).inc()

    @staticmethod
    def decrement_pending_approvals(process_id: str, step_id: str):
        """
        Decrement pending approval count

        Args:
            process_id: Process definition identifier
            step_id: Approval step identifier
        """
        process_framework_pending_approvals.labels(
            process_id=process_id,
            step_id=step_id
        ).dec()


# Global instance
process_metrics = ProcessMetrics()


# ============================================================================
# DECORATORS
# ============================================================================

def track_process_execution(process_id: str):
    """
    Decorator to automatically track process execution

    Tracks:
    - Process start
    - Process completion (success/failure)
    - Total duration
    - Active instance count

    Args:
        process_id: Process definition identifier

    Example:
        @track_process_execution(process_id="bia_process")
        async def execute_bia_process(instance_id: str):
            # Process execution logic
            pass
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            process_metrics.track_process_start(process_id)
            process_metrics.increment_active_instances(process_id)

            status = "failed"
            try:
                result = await func(*args, **kwargs)
                status = "completed"
                return result
            except Exception as e:
                status = "failed"
                raise
            finally:
                duration = time.time() - start_time
                process_metrics.track_process_completion(process_id, status, duration)
                process_metrics.decrement_active_instances(process_id)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            process_metrics.track_process_start(process_id)
            process_metrics.increment_active_instances(process_id)

            status = "failed"
            try:
                result = func(*args, **kwargs)
                status = "completed"
                return result
            except Exception as e:
                status = "failed"
                raise
            finally:
                duration = time.time() - start_time
                process_metrics.track_process_completion(process_id, status, duration)
                process_metrics.decrement_active_instances(process_id)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def track_step_execution(process_id: str, step_id: str):
    """
    Decorator to automatically track step execution

    Tracks:
    - Step execution count
    - Step duration
    - Execution result (success/error)

    Args:
        process_id: Process definition identifier
        step_id: Step identifier

    Example:
        @track_step_execution(process_id="bia_process", step_id="collect_data")
        async def collect_data_step(data: dict):
            # Step logic
            pass
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            result_status = "success"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                result_status = "error"
                raise
            finally:
                duration = time.time() - start_time
                process_metrics.track_step_execution(
                    process_id,
                    step_id,
                    duration,
                    result_status
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            result_status = "success"

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                result_status = "error"
                raise
            finally:
                duration = time.time() - start_time
                process_metrics.track_step_execution(
                    process_id,
                    step_id,
                    duration,
                    result_status
                )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def track_validation(process_id: str, step_id: str):
    """
    Decorator to automatically track validation errors

    Expects the decorated function to raise ValidationError with field information,
    or return a dict with validation results.

    Args:
        process_id: Process definition identifier
        step_id: Step identifier

    Example:
        @track_validation(process_id="bia_process", step_id="collect_data")
        async def validate_data(data: dict):
            errors = {}
            if not data.get('rto_value'):
                errors['rto_value'] = ['RTO value is required']

            if errors:
                for field_name in errors:
                    # Validation errors will be tracked
                    pass

            return errors
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)

                # If result is a dict with validation errors
                if isinstance(result, dict) and result:
                    for field_name, errors in result.items():
                        if errors:  # Field has validation errors
                            process_metrics.track_validation_error(
                                process_id,
                                step_id,
                                field_name
                            )

                return result
            except Exception as e:
                # Track exception-based validation errors
                if hasattr(e, 'field_name'):
                    process_metrics.track_validation_error(
                        process_id,
                        step_id,
                        e.field_name
                    )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                # If result is a dict with validation errors
                if isinstance(result, dict) and result:
                    for field_name, errors in result.items():
                        if errors:  # Field has validation errors
                            process_metrics.track_validation_error(
                                process_id,
                                step_id,
                                field_name
                            )

                return result
            except Exception as e:
                # Track exception-based validation errors
                if hasattr(e, 'field_name'):
                    process_metrics.track_validation_error(
                        process_id,
                        step_id,
                        e.field_name
                    )
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of Process Framework metrics
    """

    # Manual tracking
    print("Starting BIA process...")
    process_metrics.track_process_start("bia_process")
    process_metrics.increment_active_instances("bia_process")

    print("Executing data collection step...")
    process_metrics.track_step_execution(
        process_id="bia_process",
        step_id="collect_data",
        duration_seconds=1.5,
        result="success"
    )

    print("Tracking validation error...")
    process_metrics.track_validation_error(
        process_id="bia_process",
        step_id="collect_data",
        field_name="rto_value"
    )

    print("Generating BIA report...")
    process_metrics.track_document_generation(
        template_id="bia_report",
        format="pdf"
    )

    print("Completing process...")
    process_metrics.track_process_completion(
        process_id="bia_process",
        status="completed",
        duration_seconds=125.5
    )
    process_metrics.decrement_active_instances("bia_process")

    print("\nMetrics tracking complete!")
    print("View metrics at http://localhost:9001/metrics")
