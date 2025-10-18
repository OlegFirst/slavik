"""
Example Saga Definitions
========================

Real-world saga definitions for BCM platform operations.
These examples demonstrate common distributed transaction patterns.
"""

from .saga_definition import (
    SagaDefinition,
    SagaStepDefinition,
    SagaExecutionPolicy,
    CompensationStrategy
)


def create_bcm_program_saga() -> SagaDefinition:
    """
    Complete BCM Program Creation Saga

    Creates a full BCM program including:
    - Business Impact Analysis (BIA)
    - BCM Plans (BCM, DR, Incident Response)
    - ISO 22301 Compliance tracking
    - Monitoring and alerting setup

    This is a sequential saga where each step depends on the previous.
    """
    saga = SagaDefinition(
        name="create_bcm_program",
        description="Create complete BCM program with all components",
        execution_policy=SagaExecutionPolicy.SEQUENTIAL,
        compensation_strategy=CompensationStrategy.BACKWARD_RECOVERY,
        total_timeout_seconds=600,  # 10 minutes total
        version="1.0"
    )

    # Step 1: Create Organization Profile
    saga.add_step(
        SagaStepDefinition(
            name="create_organization_profile",
            description="Create organization profile for BCM program",
            forward_action="organization_service.create_bcm_profile",
            forward_params={
                "profile_type": "bcm_program",
                "include_assessment": True
            },
            compensation_action="organization_service.delete_bcm_profile",
            timeout_seconds=60,
            max_retries=3,
            critical=True,
            idempotency_key_field="organization_id"
        )
    )

    # Step 2: Create BIA
    saga.add_step(
        SagaStepDefinition(
            name="create_bia",
            description="Create comprehensive Business Impact Analysis",
            forward_action="bia_service.create_assessment",
            forward_params={
                "assessment_type": "comprehensive",
                "scope": "organization",
                "include_supply_chain": True
            },
            compensation_action="bia_service.delete_assessment",
            timeout_seconds=120,
            max_retries=3,
            critical=True,
            metadata={
                "service": "bia_service",
                "operation": "create"
            }
        )
    )

    # Step 3: Analyze BIA Results
    saga.add_step(
        SagaStepDefinition(
            name="analyze_bia_results",
            description="Analyze BIA to identify critical processes and RTOs",
            forward_action="bia_service.analyze_impact",
            forward_params={
                "analysis_depth": "detailed",
                "include_recommendations": True
            },
            compensation_action="bia_service.clear_analysis",
            timeout_seconds=90,
            max_retries=2,
            critical=True
        )
    )

    # Step 4: Create BCM Plans
    saga.add_step(
        SagaStepDefinition(
            name="create_bcm_plans",
            description="Create BCM, DR, and Incident Response plans",
            forward_action="plans_service.create_plan_suite",
            forward_params={
                "plan_types": ["bcm", "dr", "incident_response"],
                "based_on_bia": True,
                "auto_generate": True
            },
            compensation_action="plans_service.delete_plan_suite",
            timeout_seconds=120,
            max_retries=3,
            critical=True
        )
    )

    # Step 5: Initialize ISO 22301 Compliance
    saga.add_step(
        SagaStepDefinition(
            name="init_iso22301_compliance",
            description="Initialize ISO 22301 compliance tracking",
            forward_action="compliance_service.initialize_program",
            forward_params={
                "standard": "ISO_22301",
                "scope": "bcm_program",
                "create_requirements": True,
                "auto_map": True
            },
            compensation_action="compliance_service.remove_program",
            timeout_seconds=60,
            max_retries=2,
            critical=True
        )
    )

    # Step 6: Create Initial Risk Register
    saga.add_step(
        SagaStepDefinition(
            name="create_risk_register",
            description="Create risk register from BIA findings",
            forward_action="risk_service.create_register_from_bia",
            forward_params={
                "include_inherent_risks": True,
                "include_residual_risks": True
            },
            compensation_action="risk_service.delete_register",
            timeout_seconds=60,
            max_retries=2,
            critical=True
        )
    )

    # Step 7: Setup Monitoring (Non-critical)
    saga.add_step(
        SagaStepDefinition(
            name="setup_monitoring",
            description="Setup program monitoring, metrics, and alerts",
            forward_action="monitoring_service.setup_program_monitoring",
            forward_params={
                "metrics": [
                    "plan_coverage",
                    "compliance_score",
                    "exercise_completion",
                    "risk_score"
                ],
                "alert_thresholds": {
                    "compliance_score": 0.8,
                    "plan_coverage": 0.9
                }
            },
            compensation_action="monitoring_service.remove_monitoring",
            timeout_seconds=30,
            max_retries=1,
            critical=False  # Monitoring is nice-to-have
        )
    )

    # Step 8: Send Notifications (Non-critical)
    saga.add_step(
        SagaStepDefinition(
            name="send_notifications",
            description="Notify stakeholders of program creation",
            forward_action="notification_service.notify_program_created",
            forward_params={
                "recipients": "stakeholders",
                "include_summary": True
            },
            compensation_action=None,  # No compensation needed
            timeout_seconds=20,
            max_retries=1,
            critical=False
        )
    )

    # Lifecycle hooks
    saga.on_start = "audit_service.log_program_creation_start"
    saga.on_complete = "audit_service.log_program_creation_complete"
    saga.on_failure = "audit_service.log_program_creation_failed"
    saga.on_compensated = "audit_service.log_program_creation_rollback"

    return saga


def incident_response_saga() -> SagaDefinition:
    """
    Incident Response Saga

    Coordinates multi-service incident response workflow:
    - Log incident
    - Activate response team
    - Execute response plan
    - Communicate with stakeholders
    - Document lessons learned
    """
    saga = SagaDefinition(
        name="incident_response",
        description="Coordinate incident response across services",
        execution_policy=SagaExecutionPolicy.SEQUENTIAL,
        compensation_strategy=CompensationStrategy.FORWARD_RECOVERY,  # Try to complete
        total_timeout_seconds=3600,  # 1 hour for incident response
        version="1.0"
    )

    saga.add_step(
        SagaStepDefinition(
            name="log_incident",
            description="Log incident in incident management system",
            forward_action="incident_service.create_incident",
            forward_params={
                "auto_classify": True,
                "auto_assign": True
            },
            compensation_action="incident_service.close_incident",
            timeout_seconds=30,
            max_retries=3,
            critical=True,
            idempotency_key_field="incident_id"
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="activate_response_team",
            description="Activate incident response team",
            forward_action="response_service.activate_team",
            forward_params={
                "notification_method": "multi_channel",
                "urgency": "high"
            },
            compensation_action="response_service.deactivate_team",
            timeout_seconds=60,
            max_retries=5,  # Keep trying to notify
            critical=True
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="execute_response_plan",
            description="Execute automated response plan steps",
            forward_action="response_service.execute_plan",
            forward_params={
                "plan_type": "incident_response",
                "auto_execute": True
            },
            compensation_action=None,  # Forward recovery - no rollback
            timeout_seconds=1800,  # 30 minutes
            max_retries=1,
            critical=True
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="notify_stakeholders",
            description="Send incident notifications to stakeholders",
            forward_action="notification_service.send_incident_alerts",
            forward_params={
                "alert_type": "incident",
                "include_status_page": True
            },
            compensation_action=None,
            timeout_seconds=30,
            max_retries=3,
            critical=False
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="document_response",
            description="Document incident response actions",
            forward_action="documentation_service.create_incident_log",
            forward_params={
                "include_timeline": True,
                "include_actions": True
            },
            compensation_action=None,
            timeout_seconds=60,
            max_retries=2,
            critical=False
        )
    )

    return saga


def multi_tenant_data_import_saga() -> SagaDefinition:
    """
    Multi-Tenant Data Import Saga

    Parallel import of data for new tenant:
    - Import users
    - Import assets
    - Import locations
    - Setup permissions (depends on users)
    - Initialize tenant configuration
    """
    saga = SagaDefinition(
        name="multi_tenant_data_import",
        description="Import data for new tenant with parallel processing",
        execution_policy=SagaExecutionPolicy.PARALLEL,
        compensation_strategy=CompensationStrategy.BACKWARD_RECOVERY,
        total_timeout_seconds=600,
        version="1.0"
    )

    # These can run in parallel (no dependencies)
    saga.add_step(
        SagaStepDefinition(
            name="import_users",
            description="Import user data",
            forward_action="import_service.import_users",
            forward_params={
                "source": "csv",
                "validate": True
            },
            compensation_action="import_service.rollback_users",
            timeout_seconds=120,
            max_retries=2,
            critical=True
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="import_assets",
            description="Import asset data",
            forward_action="import_service.import_assets",
            forward_params={
                "source": "csv",
                "validate": True,
                "include_dependencies": True
            },
            compensation_action="import_service.rollback_assets",
            timeout_seconds=120,
            max_retries=2,
            critical=True
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="import_locations",
            description="Import location data",
            forward_action="import_service.import_locations",
            forward_params={
                "source": "csv",
                "validate": True
            },
            compensation_action="import_service.rollback_locations",
            timeout_seconds=90,
            max_retries=2,
            critical=True
        )
    )

    # This depends on users being imported
    saga.add_step(
        SagaStepDefinition(
            name="setup_permissions",
            description="Setup user permissions and roles",
            forward_action="permission_service.setup_tenant_permissions",
            forward_params={
                "auto_assign_roles": True,
                "default_role": "user"
            },
            compensation_action="permission_service.remove_tenant_permissions",
            timeout_seconds=60,
            max_retries=2,
            critical=True,
            depends_on=["import_users"]  # Wait for users to be imported
        )
    )

    # This depends on all imports completing
    saga.add_step(
        SagaStepDefinition(
            name="initialize_tenant_config",
            description="Initialize tenant configuration",
            forward_action="tenant_service.initialize_configuration",
            forward_params={
                "create_defaults": True,
                "enable_features": ["bia", "plans", "compliance"]
            },
            compensation_action="tenant_service.remove_configuration",
            timeout_seconds=60,
            max_retries=2,
            critical=True,
            depends_on=["import_users", "import_assets", "import_locations"]
        )
    )

    return saga


def drill_execution_pipeline_saga() -> SagaDefinition:
    """
    Drill Execution Pipeline Saga

    Pipeline for executing BCM drill/exercise:
    - Schedule drill
    - Prepare environment
    - Execute drill
    - Collect results
    - Generate report
    - Update training records

    Each step's output flows to the next step.
    """
    saga = SagaDefinition(
        name="drill_execution_pipeline",
        description="Execute BCM drill with pipeline processing",
        execution_policy=SagaExecutionPolicy.PIPELINE,
        compensation_strategy=CompensationStrategy.PARTIAL_COMPENSATION,
        total_timeout_seconds=7200,  # 2 hours
        version="1.0"
    )

    saga.add_step(
        SagaStepDefinition(
            name="schedule_drill",
            description="Schedule drill and notify participants",
            forward_action="drill_service.schedule",
            forward_params={
                "drill_type": "tabletop",
                "notify_participants": True
            },
            compensation_action="drill_service.cancel_drill",
            timeout_seconds=60,
            critical=True,
            # Output: drill_id, participant_list, schedule_info
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="prepare_environment",
            description="Prepare drill environment and materials",
            forward_action="drill_service.prepare_environment",
            # Receives: drill_id, participant_list from previous step
            compensation_action="drill_service.cleanup_environment",
            timeout_seconds=300,
            critical=True,
            # Output: environment_id, materials_list
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="execute_drill",
            description="Execute the drill scenario",
            forward_action="drill_service.execute",
            # Receives: drill_id, environment_id, participant_list, materials_list
            compensation_action=None,  # Can't undo execution
            timeout_seconds=3600,  # 1 hour
            critical=False,
            # Output: execution_results, participant_responses, timeline
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="collect_results",
            description="Collect and analyze drill results",
            forward_action="drill_service.collect_results",
            # Receives: execution_results, participant_responses
            compensation_action=None,
            timeout_seconds=600,
            critical=False,
            # Output: analysis, metrics, findings
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="generate_report",
            description="Generate drill report",
            forward_action="reporting_service.generate_drill_report",
            # Receives: all previous outputs
            compensation_action="reporting_service.delete_report",
            timeout_seconds=300,
            critical=False,
            # Output: report_id, report_url
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="update_training_records",
            description="Update participant training records",
            forward_action="training_service.update_records",
            # Receives: participant_list, execution_results
            compensation_action="training_service.revert_records",
            timeout_seconds=120,
            critical=False
        )
    )

    return saga


def compliance_assessment_saga() -> SagaDefinition:
    """
    Compliance Assessment Saga

    End-to-end compliance assessment workflow:
    - Create assessment
    - Collect evidence
    - Run automated checks
    - Generate gap analysis
    - Create improvement plan
    - Schedule follow-up
    """
    saga = SagaDefinition(
        name="compliance_assessment",
        description="Execute full compliance assessment workflow",
        execution_policy=SagaExecutionPolicy.SEQUENTIAL,
        compensation_strategy=CompensationStrategy.BACKWARD_RECOVERY,
        total_timeout_seconds=1800,  # 30 minutes
        version="1.0"
    )

    saga.add_step(
        SagaStepDefinition(
            name="create_assessment",
            description="Create compliance assessment record",
            forward_action="compliance_service.create_assessment",
            forward_params={
                "standard": "ISO_22301",
                "scope": "full",
                "include_annexes": True
            },
            compensation_action="compliance_service.delete_assessment",
            timeout_seconds=60,
            critical=True,
            idempotency_key_field="assessment_id"
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="collect_evidence",
            description="Collect evidence from all services",
            forward_action="compliance_service.collect_evidence",
            forward_params={
                "sources": [
                    "bia_service",
                    "plans_service",
                    "risk_service",
                    "training_service"
                ],
                "auto_validate": True
            },
            compensation_action="compliance_service.clear_evidence",
            timeout_seconds=300,
            critical=True
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="run_automated_checks",
            description="Run automated compliance checks",
            forward_action="compliance_service.run_checks",
            forward_params={
                "check_types": ["mandatory", "recommended"],
                "include_metrics": True
            },
            compensation_action="compliance_service.clear_checks",
            timeout_seconds=180,
            critical=True
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="generate_gap_analysis",
            description="Generate gap analysis report",
            forward_action="compliance_service.generate_gap_analysis",
            forward_params={
                "include_recommendations": True,
                "prioritize_gaps": True
            },
            compensation_action="compliance_service.delete_gap_analysis",
            timeout_seconds=120,
            critical=True
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="create_improvement_plan",
            description="Create improvement plan from gaps",
            forward_action="planning_service.create_improvement_plan",
            forward_params={
                "auto_prioritize": True,
                "assign_owners": True,
                "set_deadlines": True
            },
            compensation_action="planning_service.delete_plan",
            timeout_seconds=90,
            critical=False
        )
    )

    saga.add_step(
        SagaStepDefinition(
            name="schedule_follow_up",
            description="Schedule follow-up assessment",
            forward_action="scheduling_service.schedule_assessment",
            forward_params={
                "frequency": "quarterly",
                "notify_stakeholders": True
            },
            compensation_action="scheduling_service.cancel_schedule",
            timeout_seconds=30,
            critical=False
        )
    )

    return saga


def get_all_example_sagas() -> list[SagaDefinition]:
    """Get all example saga definitions"""
    return [
        create_bcm_program_saga(),
        incident_response_saga(),
        multi_tenant_data_import_saga(),
        drill_execution_pipeline_saga(),
        compliance_assessment_saga()
    ]


def register_all_example_sagas(orchestrator) -> None:
    """
    Register all example sagas with an orchestrator.

    Usage:
        from saga_engine import SagaOrchestrator
        from saga_engine.example_sagas import register_all_example_sagas

        orchestrator = SagaOrchestrator(...)
        register_all_example_sagas(orchestrator)
    """
    for saga in get_all_example_sagas():
        orchestrator.register_saga(saga)
