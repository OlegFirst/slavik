"""
Risk Assessment Workflow
========================

Temporal workflow for risk analysis with 5 stages.

Integrates with:
- RiskAnalyzer (FAIR-based quantification)
- Risk Service (persistence)
- Document Service (reporting)
"""

import logging
from datetime import timedelta
from typing import Dict, Any
import httpx

from temporalio import workflow, activity
from temporalio.common import RetryPolicy

from orchestration.bcm_services_orchestrator import AnalyzerCoordinator, AnalyzerType
from orchestration.bcm_services_orchestrator import BCMServiceRegistry, BCMServiceType

logger = logging.getLogger(__name__)

# Global instances (injected by worker)
_analyzer_coordinator: AnalyzerCoordinator = None
_service_registry: BCMServiceRegistry = None


def inject_dependencies(analyzer_coordinator: AnalyzerCoordinator, service_registry: BCMServiceRegistry):
    """Inject dependencies for activities."""
    global _analyzer_coordinator, _service_registry
    _analyzer_coordinator = analyzer_coordinator
    _service_registry = service_registry
    logger.info("Dependencies injected into Risk workflow activities")


@activity.defn
async def risk_activity_identify_threats(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 1: Identify threats.

    Uses:
    - RiskAnalyzer (threat identification via AI)
    """
    logger.info(f"Risk Stage 1: Identifying threats")

    try:
        # Call RiskAnalyzer
        analysis_result = await _analyzer_coordinator.route_analysis(
            analysis_type=AnalyzerType.RISK,
            input_data={
                'type': 'threat_identification',
                'organization_id': input_data.get('organization_id'),
                'scope': input_data.get('scope', 'all'),
                'industry': input_data.get('industry')
            },
            tenant_id=input_data['tenant_id']
        )

        if not analysis_result.get('success'):
            raise Exception(f"Threat identification failed: {analysis_result.get('error')}")

        threats = analysis_result.get('insights', [])

        return {
            "stage": "identify_threats",
            "threats_found": len(threats),
            "critical_threats": sum(1 for t in threats if t.get('severity') == 'critical'),
            "threats_data": threats,
            "analyzer_confidence": analysis_result.get('confidence'),
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Stage 1 failed: {str(e)}")
        return {"stage": "identify_threats", "status": "failed", "error": str(e)}


@activity.defn
async def risk_activity_assess_vulnerabilities(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 2: Assess vulnerabilities.

    Uses:
    - RiskAnalyzer (vulnerability assessment)
    - Risk Service (CVE database integration)
    """
    logger.info(f"Risk Stage 2: Assessing vulnerabilities")

    try:
        # Call RiskAnalyzer
        analysis_result = await _analyzer_coordinator.route_analysis(
            analysis_type=AnalyzerType.RISK,
            input_data={
                'type': 'vulnerability_assessment',
                'threats': input_data.get('threats_data', []),
                'assets': input_data.get('assets', [])
            },
            tenant_id=input_data['tenant_id']
        )

        if not analysis_result.get('success'):
            raise Exception(f"Vulnerability assessment failed: {analysis_result.get('error')}")

        vulnerabilities = analysis_result.get('insights', [])

        # Save to Risk Service
        risk_service_url = _service_registry.get_service_url(BCMServiceType.RISK_SERVICE)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{risk_service_url}/api/risk/vulnerabilities",
                json={
                    'vulnerabilities': vulnerabilities,
                    'tenant_id': input_data['tenant_id']
                },
                headers={'X-Tenant-ID': input_data['tenant_id']}
            )

            if response.status_code != 200:
                raise Exception(f"Risk Service returned {response.status_code}")

        return {
            "stage": "assess_vulnerabilities",
            "vulnerabilities": len(vulnerabilities),
            "high_severity": sum(1 for v in vulnerabilities if v.get('severity') == 'high'),
            "vulnerabilities_data": vulnerabilities,
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Stage 2 failed: {str(e)}")
        return {"stage": "assess_vulnerabilities", "status": "failed", "error": str(e)}


@activity.defn
async def risk_activity_calculate_fair(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 3: Calculate FAIR risk scores.

    Uses:
    - RiskAnalyzer (FAIR quantification)
    - Risk Service (LEF/ALE calculations)
    """
    logger.info(f"Risk Stage 3: Calculating FAIR scores")

    try:
        # Call RiskAnalyzer for FAIR analysis
        analysis_result = await _analyzer_coordinator.route_analysis(
            analysis_type=AnalyzerType.RISK,
            input_data={
                'type': 'fair_analysis',
                'threats': input_data.get('threats_data', []),
                'vulnerabilities': input_data.get('vulnerabilities_data', [])
            },
            tenant_id=input_data['tenant_id']
        )

        if not analysis_result.get('success'):
            raise Exception(f"FAIR calculation failed: {analysis_result.get('error')}")

        fair_results = analysis_result.get('recommendations', [])

        # Calculate ALE (Annual Loss Expectancy)
        ale_values = [f.get('ale', 0) for f in fair_results if f.get('ale')]
        avg_ale = sum(ale_values) / len(ale_values) if ale_values else 0
        total_ale = sum(ale_values)

        # Save to Risk Service
        risk_service_url = _service_registry.get_service_url(BCMServiceType.RISK_SERVICE)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{risk_service_url}/api/risk/fair",
                json={
                    'fair_results': fair_results,
                    'total_ale': total_ale,
                    'tenant_id': input_data['tenant_id']
                },
                headers={'X-Tenant-ID': input_data['tenant_id']}
            )

            if response.status_code != 200:
                raise Exception(f"Risk Service returned {response.status_code}")

        return {
            "stage": "calculate_fair",
            "risks_quantified": len(fair_results),
            "avg_ale": avg_ale,
            "total_ale": total_ale,
            "fair_data": fair_results,
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Stage 3 failed: {str(e)}")
        return {"stage": "calculate_fair", "status": "failed", "error": str(e)}


@activity.defn
async def risk_activity_recommend_treatments(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 4: Recommend risk treatments.

    Uses:
    - RiskAnalyzer (treatment recommendations)
    """
    logger.info(f"Risk Stage 4: Recommending treatments")

    try:
        # Call RiskAnalyzer for treatment recommendations
        analysis_result = await _analyzer_coordinator.route_analysis(
            analysis_type=AnalyzerType.RISK,
            input_data={
                'type': 'treatment_planning',
                'fair_results': input_data.get('fair_data', []),
                'risk_appetite': input_data.get('risk_appetite', 'moderate')
            },
            tenant_id=input_data['tenant_id']
        )

        if not analysis_result.get('success'):
            raise Exception(f"Treatment recommendation failed: {analysis_result.get('error')}")

        treatments = analysis_result.get('recommendations', [])

        # Categorize treatments
        treatment_types = {}
        for t in treatments:
            ttype = t.get('treatment_type', 'mitigate')
            treatment_types[ttype] = treatment_types.get(ttype, 0) + 1

        return {
            "stage": "recommend_treatments",
            "treatments": len(treatments),
            "treatment_types": treatment_types,
            "treatments_data": treatments,
            "estimated_cost": sum(t.get('cost', 0) for t in treatments),
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Stage 4 failed: {str(e)}")
        return {"stage": "recommend_treatments", "status": "failed", "error": str(e)}


@activity.defn
async def risk_activity_generate_report(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage 5: Generate risk report.

    Uses:
    - Document Service
    """
    logger.info(f"Risk Stage 5: Generating report")

    try:
        # Get Document Service URL
        doc_service_url = _service_registry.get_service_url(BCMServiceType.DOCUMENT_SERVICE)

        # Call Document Service
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{doc_service_url}/api/documents/generate",
                json={
                    'type': 'risk_assessment_report',
                    'data': {
                        'threats': input_data.get('threats_data', []),
                        'vulnerabilities': input_data.get('vulnerabilities_data', []),
                        'fair_analysis': input_data.get('fair_data', []),
                        'treatments': input_data.get('treatments_data', []),
                        'total_ale': input_data.get('total_ale', 0)
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
        logger.error(f"Stage 5 failed: {str(e)}")
        return {"stage": "generate_report", "status": "failed", "error": str(e)}


@workflow.defn
class RiskAssessmentWorkflow:
    """Risk Assessment Workflow - 5 stages with full integration."""

    @workflow.run
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute risk assessment workflow."""
        workflow.logger.info(f"Starting Risk workflow for tenant: {input_data.get('tenant_id')}")

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=30),
            maximum_attempts=3
        )

        results = {
            "workflow": "RiskAssessmentWorkflow",
            "tenant_id": input_data.get("tenant_id"),
            "started_at": workflow.now().isoformat(),
            "stages": []
        }

        try:
            # Stage 1: Identify threats
            stage1 = await workflow.execute_activity(
                risk_activity_identify_threats,
                input_data,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )
            results["stages"].append(stage1)

            # Stage 2: Assess vulnerabilities
            stage2_input = {**input_data, **stage1}
            stage2 = await workflow.execute_activity(
                risk_activity_assess_vulnerabilities,
                stage2_input,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry_policy
            )
            results["stages"].append(stage2)

            # Stage 3: Calculate FAIR
            stage3_input = {**input_data, **stage1, **stage2}
            stage3 = await workflow.execute_activity(
                risk_activity_calculate_fair,
                stage3_input,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry_policy
            )
            results["stages"].append(stage3)

            # Stage 4: Recommend treatments
            stage4_input = {**input_data, **stage3}
            stage4 = await workflow.execute_activity(
                risk_activity_recommend_treatments,
                stage4_input,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )
            results["stages"].append(stage4)

            # Stage 5: Generate report
            stage5_input = {**input_data, **stage1, **stage2, **stage3, **stage4}
            stage5 = await workflow.execute_activity(
                risk_activity_generate_report,
                stage5_input,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )
            results["stages"].append(stage5)

            results["status"] = "completed"
            results["completed_at"] = workflow.now().isoformat()
            results["report_url"] = stage5["report_url"]

            return results

        except Exception as e:
            workflow.logger.error(f"Risk workflow failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
            raise


risk_activities = [
    risk_activity_identify_threats,
    risk_activity_assess_vulnerabilities,
    risk_activity_calculate_fair,
    risk_activity_recommend_treatments,
    risk_activity_generate_report
]
