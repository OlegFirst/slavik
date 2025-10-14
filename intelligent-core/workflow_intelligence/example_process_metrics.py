"""
Example: Using Prometheus Metrics with Process Framework

This example demonstrates how to integrate Prometheus metrics
into your Process Framework workflows.

Run this file to see metrics in action:
    python3 example_process_metrics.py

Then view metrics at:
    http://localhost:9001/metrics
"""

import asyncio
import time
from pathlib import Path
from process_framework import (
    ProcessDefinition,
    ProcessStep,
    StepType,
    FormField,
    FieldValidation,
    ValidationRule,
    get_process_framework
)
from metrics import (
    process_metrics,
    track_process_execution,
    track_step_execution,
    track_validation
)


# ============================================================================
# Example 1: Manual Metrics Tracking
# ============================================================================

def example_manual_tracking():
    """Example of manually tracking metrics"""
    print("\n" + "=" * 70)
    print("Example 1: Manual Metrics Tracking")
    print("=" * 70)

    # Start a process
    print("\n1. Starting BIA process manually...")
    process_metrics.track_process_start("bia_process")
    process_metrics.increment_active_instances("bia_process")

    start_time = time.time()

    # Execute steps
    print("2. Executing steps...")

    # Step 1: Data collection
    step_start = time.time()
    # ... step logic here ...
    time.sleep(0.1)  # Simulate work
    process_metrics.track_step_execution(
        process_id="bia_process",
        step_id="collect_data",
        duration_seconds=time.time() - step_start,
        result="success"
    )
    print("   ✓ Data collection step completed")

    # Track validation errors (if any)
    process_metrics.track_validation_error(
        process_id="bia_process",
        step_id="collect_data",
        field_name="rto_value"
    )
    print("   ✓ Validation error tracked")

    # Step 2: Analysis
    step_start = time.time()
    # ... analysis logic ...
    time.sleep(0.05)
    process_metrics.track_step_execution(
        process_id="bia_process",
        step_id="analysis",
        duration_seconds=time.time() - step_start,
        result="success"
    )
    print("   ✓ Analysis step completed")

    # Generate document
    print("3. Generating report...")
    process_metrics.track_document_generation(
        template_id="bia_report",
        format="pdf"
    )
    print("   ✓ PDF report generated")

    # Complete process
    print("4. Completing process...")
    total_duration = time.time() - start_time
    process_metrics.track_process_completion(
        process_id="bia_process",
        status="completed",
        duration_seconds=total_duration
    )
    process_metrics.decrement_active_instances("bia_process")
    print(f"   ✓ Process completed in {total_duration:.2f}s")


# ============================================================================
# Example 2: Using Decorators
# ============================================================================

@track_process_execution(process_id="risk_assessment")
async def execute_risk_assessment_process():
    """Example process with decorator-based tracking"""
    print("\n   Executing risk assessment process...")

    # Step 1
    await execute_risk_identification()

    # Step 2
    await execute_risk_analysis()

    # Step 3
    await execute_mitigation_planning()

    print("   ✓ Risk assessment process completed")


@track_step_execution(process_id="risk_assessment", step_id="risk_identification")
async def execute_risk_identification():
    """Step 1: Risk identification"""
    await asyncio.sleep(0.05)  # Simulate work
    print("      → Risk identification completed")


@track_step_execution(process_id="risk_assessment", step_id="risk_analysis")
async def execute_risk_analysis():
    """Step 2: Risk analysis"""
    await asyncio.sleep(0.03)  # Simulate work
    print("      → Risk analysis completed")


@track_step_execution(process_id="risk_assessment", step_id="mitigation_planning")
async def execute_mitigation_planning():
    """Step 3: Mitigation planning"""
    await asyncio.sleep(0.02)  # Simulate work

    # Generate report
    process_metrics.track_document_generation(
        template_id="risk_assessment_report",
        format="docx"
    )
    print("      → Mitigation planning completed")


async def example_decorator_tracking():
    """Example of using decorators for automatic tracking"""
    print("\n" + "=" * 70)
    print("Example 2: Decorator-Based Tracking")
    print("=" * 70)

    print("\n1. Starting risk assessment with decorators...")
    await execute_risk_assessment_process()


# ============================================================================
# Example 3: Integration with Process Framework
# ============================================================================

def example_framework_integration():
    """Example of integrating metrics with Process Framework"""
    print("\n" + "=" * 70)
    print("Example 3: Process Framework Integration")
    print("=" * 70)

    # Create a simple process definition
    print("\n1. Creating process definition...")
    process = ProcessDefinition(
        id="simple_approval",
        name="Simple Approval Process",
        version="1.0",
        description="A simple approval process with metrics"
    )

    # Add steps
    step1 = ProcessStep(
        id="submit_request",
        name="Submit Request",
        step_type=StepType.FORM_INPUT,
        description="Submit approval request",
        form_fields=[
            FormField(
                name="request_title",
                label="Request Title",
                field_type="text",
                required=True,
                validations=[
                    FieldValidation(
                        rule=ValidationRule.REQUIRED,
                        value=True,
                        error_message="Title is required"
                    ),
                    FieldValidation(
                        rule=ValidationRule.MIN_LENGTH,
                        value=5,
                        error_message="Title must be at least 5 characters"
                    )
                ]
            )
        ],
        next_steps=["approval"]
    )

    step2 = ProcessStep(
        id="approval",
        name="Manager Approval",
        step_type=StepType.APPROVAL,
        description="Manager reviews and approves",
        next_steps=["complete"]
    )

    process.add_step(step1)
    process.add_step(step2)
    process.start_step_id = "submit_request"
    process.end_step_ids = ["complete"]

    print("   ✓ Process definition created")

    # Initialize framework
    print("\n2. Starting process instance...")
    framework = get_process_framework(Path(__file__).parent / "test_processes")
    framework.register_process(process)

    # Track process start
    process_metrics.track_process_start(process.id)
    process_metrics.increment_active_instances(process.id)

    # Start instance
    instance = framework.start_process(
        process_id=process.id,
        started_by="user@example.com",
        initial_data={}
    )
    print(f"   ✓ Process instance started: {instance.id}")

    # Execute step 1
    print("\n3. Executing step 1 (submit_request)...")
    step_start = time.time()

    # Simulate validation error
    step_data = {
        "request_title": "Hi"  # Too short - will fail validation
    }

    success, error, next_step = framework.execute_step(
        instance_id=instance.id,
        step_data=step_data,
        executed_by="user@example.com"
    )

    step_duration = time.time() - step_start

    if not success:
        # Track validation error
        process_metrics.track_validation_error(
            process_id=process.id,
            step_id="submit_request",
            field_name="request_title"
        )
        print(f"   ✗ Validation failed: {error}")

        # Track step with validation_failed result
        process_metrics.track_step_execution(
            process_id=process.id,
            step_id="submit_request",
            duration_seconds=step_duration,
            result="validation_failed"
        )

    # Retry with valid data
    print("\n4. Retrying with valid data...")
    step_start = time.time()
    step_data = {
        "request_title": "My Important Request"
    }

    success, error, next_step = framework.execute_step(
        instance_id=instance.id,
        step_data=step_data,
        executed_by="user@example.com"
    )

    step_duration = time.time() - step_start

    if success:
        process_metrics.track_step_execution(
            process_id=process.id,
            step_id="submit_request",
            duration_seconds=step_duration,
            result="success"
        )
        print(f"   ✓ Step completed successfully")
        print(f"   ✓ Next step: {next_step}")

    # Track pending approval
    print("\n5. Tracking pending approval...")
    process_metrics.increment_pending_approvals(process.id, "approval")
    print("   ✓ Pending approval incremented")

    # Complete approval
    print("\n6. Completing approval...")
    step_start = time.time()
    time.sleep(0.05)  # Simulate approval delay

    process_metrics.track_step_execution(
        process_id=process.id,
        step_id="approval",
        duration_seconds=time.time() - step_start,
        result="success"
    )
    process_metrics.decrement_pending_approvals(process.id, "approval")
    print("   ✓ Approval completed")

    # Complete process
    print("\n7. Completing process...")
    total_duration = time.time() - step_start
    process_metrics.track_process_completion(
        process_id=process.id,
        status="completed",
        duration_seconds=total_duration
    )
    process_metrics.decrement_active_instances(process.id)
    print("   ✓ Process completed")


# ============================================================================
# Example 4: Monitoring Active Processes
# ============================================================================

def example_active_monitoring():
    """Example of monitoring active processes"""
    print("\n" + "=" * 70)
    print("Example 4: Active Process Monitoring")
    print("=" * 70)

    print("\n1. Starting multiple process instances...")

    # Start multiple processes
    for i in range(3):
        process_metrics.track_process_start("bia_process")
        process_metrics.increment_active_instances("bia_process")
        print(f"   ✓ Started BIA process instance {i+1}")

    for i in range(2):
        process_metrics.track_process_start("risk_assessment")
        process_metrics.increment_active_instances("risk_assessment")
        print(f"   ✓ Started Risk Assessment instance {i+1}")

    print("\n2. Adding pending approvals...")
    process_metrics.increment_pending_approvals("bia_process", "manager_approval")
    process_metrics.increment_pending_approvals("bia_process", "manager_approval")
    process_metrics.increment_pending_approvals("risk_assessment", "final_approval")
    print("   ✓ Added 2 pending approvals for BIA")
    print("   ✓ Added 1 pending approval for Risk Assessment")

    print("\n3. Current state:")
    print("   - Active BIA processes: 3")
    print("   - Active Risk Assessment processes: 2")
    print("   - Pending BIA approvals: 2")
    print("   - Pending Risk Assessment approvals: 1")

    # Complete some processes
    print("\n4. Completing processes...")
    process_metrics.track_process_completion("bia_process", "completed", 120.0)
    process_metrics.decrement_active_instances("bia_process")
    process_metrics.decrement_pending_approvals("bia_process", "manager_approval")
    print("   ✓ Completed 1 BIA process")

    process_metrics.track_process_completion("risk_assessment", "completed", 180.0)
    process_metrics.decrement_active_instances("risk_assessment")
    process_metrics.decrement_pending_approvals("risk_assessment", "final_approval")
    print("   ✓ Completed 1 Risk Assessment")

    print("\n5. Updated state:")
    print("   - Active BIA processes: 2")
    print("   - Active Risk Assessment processes: 1")
    print("   - Pending BIA approvals: 1")
    print("   - Pending Risk Assessment approvals: 0")


# ============================================================================
# Main
# ============================================================================

def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("Process Framework Metrics Examples")
    print("=" * 70)
    print("\nThese examples demonstrate how to use Prometheus metrics")
    print("with the Process Framework.")
    print("\nMetrics will be available at: http://localhost:9001/metrics")
    print("(Start the metrics exporter with: python3 -m")
    print(" intelligent_core.workflow_intelligence.metrics_exporter)")

    # Run examples
    example_manual_tracking()

    asyncio.run(example_decorator_tracking())

    example_framework_integration()

    example_active_monitoring()

    print("\n" + "=" * 70)
    print("All Examples Complete!")
    print("=" * 70)
    print("\nView metrics at: http://localhost:9001/metrics")
    print("Search for metrics starting with: process_framework_")
    print("\nAvailable metrics:")
    print("  • process_framework_process_started_total")
    print("  • process_framework_process_completed_total")
    print("  • process_framework_step_executed_total")
    print("  • process_framework_validation_errors_total")
    print("  • process_framework_documents_generated_total")
    print("  • process_framework_step_execution_duration_seconds")
    print("  • process_framework_process_duration_seconds")
    print("  • process_framework_active_instances")
    print("  • process_framework_pending_approvals")


if __name__ == "__main__":
    main()
