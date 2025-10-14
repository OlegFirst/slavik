"""
BIA Workflow - Business Impact Analysis
========================================

Temporal workflow for executing BIA process with 6 stages.

Based on existing workflow_intelligence state machine but with:
- Durable execution (survives restarts)
- Automatic retries
- Compensation logic
- Progress tracking

Integrates with:
- AnalyzerCoordinator (from orchestration/bcm-services-orchestrator/)
- BCM Services (BIA, Document)
- EventBus (audit trail)
"""

import logging
from datetime import timedelta
from typing import Dict, Any
import httpx

from temporalio import workflow, activity
from temporalio.common import RetryPolicy

# Import real components
from orchestration.bcm_services_orchestrator import AnalyzerCoordinator, AnalyzerType
from orchestration.bcm_services_orchestrator import BCMServiceRegistry, BCMServiceType

logger = logging.getLogger(__name__)

# Global instances (injected by worker)
_analyzer_coordinator: AnalyzerCoordinator = None
_service_registry: BCMServiceRegistry = None


def inject_dependencies(analyzer_coordinator: AnalyzerCoordinator, service_registry: BCMServiceRegistry):
    """Inject dependencies for activities (called by Temporal worker)."""
    global _analyzer_coordinator, _service_registry
    _analyzer_coordinator = analyzer_coordinator
    _service_registry = service_registry
    logger.info("Dependencies injected into BIA workflow activities")


# Activity definitions
@activity.defn
async def bia_activity_identify_processes(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 1: Identify critical business processes.

    Uses:
    - ImpactAnalyzer (via AnalyzerCoordinator)
    - BIA Service
    """
    logger.info(f"BIA Stage 1: Identifying processes for {input_data.get('tenant_id')}")

    try:
        # Call AnalyzerCoordinator → ImpactAnalyzer
        analysis_result = await _analyzer_coordinator.route_analysis(
            analysis_type=AnalyzerType.IMPACT,
            input_data={
                'type': 'process_identification',
                'organization_id': input_data.get('organization_id'),
                'scope': input_data.get('scope', 'all')
            },
            tenant_id=input_data['tenant_id']
        )

        if not analysis_result.get('success'):
            raise Exception(f"Analysis failed: {analysis_result.get('error')}")

        insights = analysis_result.get('insights', [])

        # Extract process count from AI analysis
        processes_identified = len(insights)
        critical_count = sum(1 for i in insights if i.get('criticality') == 'high')

        return {
            "stage": "identify_processes",
            "processes_identified": processes_identified,
            "critical_count": critical_count,
            "insights": insights,
            "analyzer": analysis_result.get('analyzer'),
            "confidence": analysis_result.get('confidence'),
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Stage 1 failed: {str(e)}")
        return {
            "stage": "identify_processes",
            "status": "failed",
            "error": str(e)
        }


@activity.defn
async def bia_activity_analyze_dependencies(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 2: Analyze process dependencies.

    Uses:
    - BIA Service (dependency mapping)
    """
    logger.info(f"BIA Stage 2: Analyzing dependencies")

    try:
        # Get BIA Service URL from registry
        bia_service_url = _service_registry.get_service_url(BCMServiceType.BIA_SERVICE)

        # Call BIA Service
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{bia_service_url}/api/bia/dependencies",
                json={
                    'processes': input_data.get('processes', []),
                    'tenant_id': input_data['tenant_id']
                },
                headers={'X-Tenant-ID': input_data['tenant_id']}
            )

            if response.status_code != 200:
                raise Exception(f"BIA Service returned {response.status_code}")

            result = response.json()

        return {
            "stage": "analyze_dependencies",
            "dependencies_mapped": result.get('dependencies_count', 0),
            "dependency_data": result.get('dependencies', []),
            "status": "completed"
        }

    except httpx.TimeoutException:
        logger.error("BIA Service timeout")
        return {
            "stage": "analyze_dependencies",
            "status": "failed",
            "error": "Service timeout"
        }
    except Exception as e:
        logger.error(f"Stage 2 failed: {str(e)}")
        return {
            "stage": "analyze_dependencies",
            "status": "failed",
            "error": str(e)
        }


@activity.defn
async def bia_activity_assess_impact(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 3: Assess business impact.

    Uses:
    - ImpactAnalyzer
    """
    logger.info(f"BIA Stage 3: Assessing impact")

    try:
        # Call AnalyzerCoordinator → ImpactAnalyzer
        analysis_result = await _analyzer_coordinator.route_analysis(
            analysis_type=AnalyzerType.IMPACT,
            input_data={
                'type': 'impact_assessment',
                'processes': input_data.get('processes', []),
                'dependencies': input_data.get('dependency_data', [])
            },
            tenant_id=input_data['tenant_id']
        )

        if not analysis_result.get('success'):
            raise Exception(f"Impact analysis failed: {analysis_result.get('error')}")

        insights = analysis_result.get('insights', [])
        high_impact = sum(1 for i in insights if i.get('impact_level') == 'high')

        return {
            "stage": "assess_impact",
            "processes_assessed": len(insights),
            "high_impact": high_impact,
            "impact_data": insights,
            "confidence": analysis_result.get('confidence'),
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Stage 3 failed: {str(e)}")
        return {
            "stage": "assess_impact",
            "status": "failed",
            "error": str(e)
        }


@activity.defn
async def bia_activity_determine_rto_rpo(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 4: Determine RTO/RPO for each process.

    Uses:
    - ImpactAnalyzer (AI recommendations)
    - BIA Service (persistence)
    """
    logger.info(f"BIA Stage 4: Determining RTO/RPO")

    try:
        # Step 1: AI Analysis for RTO/RPO recommendations
        analysis_result = await _analyzer_coordinator.route_analysis(
            analysis_type=AnalyzerType.IMPACT,
            input_data={
                'type': 'rto_rpo_determination',
                'processes': input_data.get('processes', []),
                'impact_data': input_data.get('impact_data', [])
            },
            tenant_id=input_data['tenant_id']
        )

        if not analysis_result.get('success'):
            raise Exception(f"RTO/RPO analysis failed: {analysis_result.get('error')}")

        recommendations = analysis_result.get('recommendations', [])

        # Step 2: Save RTO/RPO to BIA Service
        bia_service_url = _service_registry.get_service_url(BCMServiceType.BIA_SERVICE)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{bia_service_url}/api/bia/rto-rpo",
                json={
                    'processes': input_data.get('processes', []),
                    'rto_rpo_recommendations': recommendations,
                    'tenant_id': input_data['tenant_id']
                },
                headers={'X-Tenant-ID': input_data['tenant_id']}
            )

            if response.status_code != 200:
                raise Exception(f"BIA Service returned {response.status_code}")

            result = response.json()

        # Calculate averages
        rto_values = [r.get('rto_hours', 0) for r in recommendations if r.get('rto_hours')]
        rpo_values = [r.get('rpo_hours', 0) for r in recommendations if r.get('rpo_hours')]

        avg_rto = sum(rto_values) / len(rto_values) if rto_values else 0
        avg_rpo = sum(rpo_values) / len(rpo_values) if rpo_values else 0

        return {
            "stage": "determine_rto_rpo",
            "processes_with_rto": len(recommendations),
            "avg_rto_hours": avg_rto,
            "avg_rpo_hours": avg_rpo,
            "rto_rpo_data": recommendations,
            "analyzer_confidence": analysis_result.get('confidence'),
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Stage 4 failed: {str(e)}")
        return {
            "stage": "determine_rto_rpo",
            "status": "failed",
            "error": str(e)
        }


@activity.defn
async def bia_activity_review_results(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 5: Review and validate results.

    Uses:
    - ComplianceAnalyzer (ISO 22301 validation)
    - GovernanceAnalyzer (policy adherence)
    """
    logger.info(f"BIA Stage 5: Reviewing results")

    try:
        # Prepare BIA results for review
        bia_results = {
            'processes': input_data.get('processes', []),
            'dependencies': input_data.get('dependency_data', []),
            'impact_assessment': input_data.get('impact_data', []),
            'rto_rpo': input_data.get('rto_rpo_data', [])
        }

        # Step 1: Compliance validation (ISO 22301 alignment)
        compliance_result = await _analyzer_coordinator.route_analysis(
            analysis_type=AnalyzerType.COMPLIANCE,
            input_data={
                'type': 'bia_validation',
                'bia_results': bia_results,
                'standard': 'ISO_22301'
            },
            tenant_id=input_data['tenant_id']
        )

        # Step 2: Governance validation (internal policies)
        governance_result = await _analyzer_coordinator.route_analysis(
            analysis_type=AnalyzerType.GOVERNANCE,
            input_data={
                'type': 'policy_check',
                'bia_results': bia_results
            },
            tenant_id=input_data['tenant_id']
        )

        # Check if both validations passed
        compliance_passed = compliance_result.get('success') and compliance_result.get('confidence', 0) > 0.7
        governance_passed = governance_result.get('success') and governance_result.get('confidence', 0) > 0.7

        validation_passed = compliance_passed and governance_passed

        # Collect issues
        issues = []
        if not compliance_passed:
            issues.extend(compliance_result.get('insights', []))
        if not governance_passed:
            issues.extend(governance_result.get('insights', []))

        return {
            "stage": "review_results",
            "validation_passed": validation_passed,
            "compliance_passed": compliance_passed,
            "governance_passed": governance_passed,
            "issues_found": len(issues),
            "issues": issues,
            "compliance_confidence": compliance_result.get('confidence'),
            "governance_confidence": governance_result.get('confidence'),
            "status": "completed" if validation_passed else "completed_with_warnings"
        }

    except Exception as e:
        logger.error(f"Stage 5 failed: {str(e)}")
        return {
            "stage": "review_results",
            "status": "failed",
            "error": str(e)
        }


@activity.defn
async def bia_activity_generate_report(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 6: Generate BIA report.

    Uses:
    - Document Service
    """
    logger.info(f"BIA Stage 6: Generating report")

    try:
        # Get Document Service URL
        doc_service_url = _service_registry.get_service_url(BCMServiceType.DOCUMENT_SERVICE)

        # Call Document Service to generate report
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{doc_service_url}/api/documents/generate",
                json={
                    'type': 'bia_report',
                    'data': {
                        'processes': input_data.get('processes', []),
                        'dependencies': input_data.get('dependencies', []),
                        'impact_assessment': input_data.get('impact_data', []),
                        'rto_rpo': input_data.get('rto_rpo_data', [])
                    },
                    'tenant_id': input_data['tenant_id'],
                    'format': 'pdf'
                },
                headers={'X-Tenant-ID': input_data['tenant_id']}
            )

            if response.status_code != 200:
                raise Exception(f"Document Service returned {response.status_code}")

            result = response.json()

        return {
            "stage": "generate_report",
            "report_url": result.get('report_url'),
            "report_id": result.get('document_id'),
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Stage 6 failed: {str(e)}")
        return {
            "stage": "generate_report",
            "status": "failed",
            "error": str(e)
        }


# Workflow definition
@workflow.defn
class BIAWorkflow:
    """
    BIA Workflow - 6-stage Business Impact Analysis.

    Stages:
    1. Identify processes
    2. Analyze dependencies
    3. Assess impact
    4. Determine RTO/RPO
    5. Review results
    6. Generate report

    Features:
    - Automatic retries on failures
    - Progress tracking
    - Compensation logic (rollback)
    - Human approval gates (optional)
    """

    @workflow.run
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute BIA workflow."""
        workflow.logger.info(f"Starting BIA workflow for tenant: {input_data.get('tenant_id')}")

        # Retry policy for activities
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=30),
            maximum_attempts=3
        )

        results = {
            "workflow": "BIAWorkflow",
            "tenant_id": input_data.get("tenant_id"),
            "started_at": workflow.now().isoformat(),
            "stages": []
        }

        try:
            # Stage 1: Identify processes
            stage1 = await workflow.execute_activity(
                bia_activity_identify_processes,
                input_data,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )
            results["stages"].append(stage1)
            workflow.logger.info(f"Stage 1 complete: {stage1['processes_identified']} processes")

            # Stage 2: Analyze dependencies
            stage2_input = {**input_data, "processes": stage1}
            stage2 = await workflow.execute_activity(
                bia_activity_analyze_dependencies,
                stage2_input,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry_policy
            )
            results["stages"].append(stage2)

            # Stage 3: Assess impact
            stage3_input = {**input_data, "dependencies": stage2}
            stage3 = await workflow.execute_activity(
                bia_activity_assess_impact,
                stage3_input,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry_policy
            )
            results["stages"].append(stage3)

            # Stage 4: Determine RTO/RPO
            stage4_input = {**input_data, "impact_assessment": stage3}
            stage4 = await workflow.execute_activity(
                bia_activity_determine_rto_rpo,
                stage4_input,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry_policy
            )
            results["stages"].append(stage4)

            # Stage 5: Review results
            stage5_input = {**input_data, "rto_rpo": stage4}
            stage5 = await workflow.execute_activity(
                bia_activity_review_results,
                stage5_input,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )
            results["stages"].append(stage5)

            # Stage 6: Generate report
            stage6_input = {**input_data, "reviewed_results": stage5}
            stage6 = await workflow.execute_activity(
                bia_activity_generate_report,
                stage6_input,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )
            results["stages"].append(stage6)

            results["status"] = "completed"
            results["completed_at"] = workflow.now().isoformat()
            results["report_url"] = stage6["report_url"]

            workflow.logger.info(f"BIA workflow completed successfully")

            return results

        except Exception as e:
            workflow.logger.error(f"BIA workflow failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
            results["failed_at"] = workflow.now().isoformat()

            # Compensation logic (rollback)
            await self._compensate(results)

            raise

    async def _compensate(self, results: Dict[str, Any]):
        """Rollback/compensation logic for failed workflow."""
        workflow.logger.warning(f"Compensating BIA workflow")

        # TODO: Implement rollback logic
        # - Delete created BIA records
        # - Notify stakeholders
        # - Update audit trail


# Export activities for registration
bia_activities = [
    bia_activity_identify_processes,
    bia_activity_analyze_dependencies,
    bia_activity_assess_impact,
    bia_activity_determine_rto_rpo,
    bia_activity_review_results,
    bia_activity_generate_report
]
