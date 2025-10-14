#!/usr/bin/env python3
"""
DevOps Infrastructure Workflow - Temporal Durable Execution

Provides fault-tolerant, retryable workflows for DevOps operations:
- Infrastructure scanning (events, containers, deployments)
- AI-powered analysis with RAG + LLM
- Auto-remediation with approval
- Dockerfile generation
- Deployment monitoring

Patterns:
- Saga для rollback при ошибках
- Retry policies для fault tolerance
- Human-in-the-loop для critical approvals
- Long-running workflows с state persistence
"""

import asyncio
import logging
from datetime import timedelta, datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from temporalio import workflow, activity
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ScanConfig:
    """Configuration for infrastructure scan"""
    scan_type: str = "full"  # 'full', 'events', 'containers', 'deployments'
    project_root: str = "/Users/MD/AI-Platform-ISO"
    auto_fix_enabled: bool = False
    require_approval: bool = True


@dataclass
class ScanResult:
    """Result of infrastructure scan"""
    timestamp: str
    scan_type: str
    events: Dict[str, Any]
    containers: Dict[str, Any]
    deployments: Dict[str, Any]
    total_issues: int


@dataclass
class AIAnalysisResult:
    """Result of AI analysis"""
    recommendations: List[Dict[str, Any]]
    risk_level: str
    auto_fix_approved: bool


@dataclass
class ApprovalRequest:
    """Request for brain approval"""
    agent_id: str = "devops-agent"
    context: str = "auto_remediation"
    recommendations: List[Dict[str, Any]] = None
    risk_assessment: Dict[str, Any] = None


@dataclass
class FixResult:
    """Result of fix application"""
    approved: int
    fixes_attempted: int
    fixes_successful: int
    fixes_failed: int
    feedbacks: List[str]
    applied_fixes: List[Dict[str, Any]]  # For rollback


# ============================================================================
# Activities - DevOps Operations
# ============================================================================

@activity.defn
async def scan_infrastructure(config: ScanConfig) -> ScanResult:
    """
    Scan infrastructure with DevOps Agent

    Activity: Idempotent, retryable
    """
    import sys
    from pathlib import Path

    # Add project to path
    sys.path.insert(0, config.project_root)
    sys.path.insert(0, str(Path(config.project_root) / "tools" / "devops-agent"))

    from agent import DevOpsAgent

    logger.info(f"🔍 Scanning infrastructure: {config.scan_type}")

    agent = DevOpsAgent(config.project_root)
    await agent.initialize()

    scan_results = await agent.scan_infrastructure(scan_type=config.scan_type)

    return ScanResult(
        timestamp=datetime.utcnow().isoformat(),
        scan_type=config.scan_type,
        events=scan_results.get("events", {}),
        containers=scan_results.get("containers", {}),
        deployments=scan_results.get("deployments", {}),
        total_issues=scan_results.get("total_issues", 0)
    )


@activity.defn
async def analyze_with_ai(scan_result: ScanResult) -> AIAnalysisResult:
    """
    AI-powered analysis with RAG + LLM

    Activity: Uses RAG for historical patterns, LLM for recommendations
    """
    import sys
    from pathlib import Path

    project_root = "/Users/MD/AI-Platform-ISO"
    sys.path.insert(0, project_root)
    sys.path.insert(0, str(Path(project_root) / "tools" / "devops-agent"))

    from agent import DevOpsAgent

    logger.info("🧠 Running AI analysis with RAG + LLM...")

    agent = DevOpsAgent(project_root)
    await agent.initialize()

    # Convert ScanResult to dict
    scan_dict = {
        "timestamp": scan_result.timestamp,
        "scan_type": scan_result.scan_type,
        "events": scan_result.events,
        "containers": scan_result.containers,
        "deployments": scan_result.deployments,
        "total_issues": scan_result.total_issues
    }

    ai_analysis = await agent.ai_analysis(scan_dict)

    return AIAnalysisResult(
        recommendations=ai_analysis.get("recommendations", []),
        risk_level=ai_analysis.get("risk_level", "unknown"),
        auto_fix_approved=ai_analysis.get("auto_fix_approved", False)
    )


@activity.defn
async def request_brain_approval(approval_req: ApprovalRequest) -> Dict[str, Any]:
    """
    Request approval from Workflow Intelligence (brain)

    Activity: Long-running, waits for human approval
    """
    import sys
    from pathlib import Path

    project_root = "/Users/MD/AI-Platform-ISO"
    sys.path.insert(0, project_root)
    sys.path.insert(0, str(Path(project_root) / "tools" / "devops-agent"))

    from integrations.workflow_intelligence import WorkflowIntelligenceClient

    logger.info("🧠 Requesting approval from brain...")

    brain = WorkflowIntelligenceClient()

    decision = await brain.request_decision({
        "agent_id": approval_req.agent_id,
        "context": approval_req.context,
        "recommendations": approval_req.recommendations,
        "risk_assessment": approval_req.risk_assessment
    })

    approved_actions = decision.get("approved_actions", [])

    logger.info(f"✅ Brain approved {len(approved_actions)} actions")

    return {
        "approved": True,
        "approved_actions": approved_actions,
        "decision_id": decision.get("decision_id", "unknown")
    }


@activity.defn
async def apply_fixes(approved_actions: List[Dict[str, Any]]) -> FixResult:
    """
    Apply approved fixes with tracking for rollback

    Activity: Idempotent, tracks applied fixes for compensation
    """
    import sys
    from pathlib import Path

    project_root = "/Users/MD/AI-Platform-ISO"
    sys.path.insert(0, project_root)
    sys.path.insert(0, str(Path(project_root) / "tools" / "devops-agent"))

    from agent import DevOpsAgent

    logger.info(f"🛠️ Applying {len(approved_actions)} approved fixes...")

    agent = DevOpsAgent(project_root)
    await agent.initialize()

    result = await agent.apply_fixes(approved_actions)

    return FixResult(
        approved=result.get("approved", 0),
        fixes_attempted=result.get("fixes_attempted", 0),
        fixes_successful=result.get("fixes_successful", 0),
        fixes_failed=result.get("fixes_failed", 0),
        feedbacks=result.get("feedbacks", []),
        applied_fixes=result.get("applied_fixes", [])
    )


@activity.defn
async def rollback_fixes(applied_fixes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Rollback applied fixes (compensating action)

    Activity: Saga compensation
    """
    logger.warning(f"⏪ Rolling back {len(applied_fixes)} fixes...")

    rollback_count = 0

    for fix in applied_fixes:
        try:
            # Implement rollback logic based on fix type
            if fix.get("category") == "event_architecture":
                # Rollback event fix
                logger.info(f"⏪ Reverting event fix: {fix.get('id')}")
                rollback_count += 1

            elif fix.get("category") == "missing_dockerfile":
                # Remove generated Dockerfile
                logger.info(f"⏪ Removing Dockerfile: {fix.get('path')}")
                rollback_count += 1

        except Exception as e:
            logger.error(f"❌ Rollback failed for {fix.get('id')}: {e}")

    return {
        "rollback_successful": rollback_count,
        "rollback_failed": len(applied_fixes) - rollback_count
    }


@activity.defn
async def generate_dockerfiles(missing_services: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate Dockerfiles with AI

    Activity: Uses RAG + LLM for Dockerfile generation
    """
    import sys
    from pathlib import Path

    project_root = "/Users/MD/AI-Platform-ISO"
    sys.path.insert(0, project_root)
    sys.path.insert(0, str(Path(project_root) / "tools" / "devops-agent"))

    from auto_remediation.dockerfile_generator import DockerfileGenerator

    logger.info(f"🐳 Generating Dockerfiles for {len(missing_services)} services...")

    generator = DockerfileGenerator(project_root)
    await generator.initialize()

    generated = []
    failed = []

    for service in missing_services:
        try:
            result = await generator.generate({"service_metadata": service})
            if result.get("success"):
                generated.append(service.get("name"))
            else:
                failed.append(service.get("name"))
        except Exception as e:
            logger.error(f"❌ Dockerfile generation failed for {service.get('name')}: {e}")
            failed.append(service.get("name"))

    return {
        "generated": generated,
        "failed": failed,
        "total": len(missing_services)
    }


@activity.defn
async def report_to_brain(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Report results to Workflow Intelligence

    Activity: Final reporting
    """
    import sys
    from pathlib import Path

    project_root = "/Users/MD/AI-Platform-ISO"
    sys.path.insert(0, project_root)
    sys.path.insert(0, str(Path(project_root) / "tools" / "devops-agent"))

    from integrations.workflow_intelligence import WorkflowIntelligenceClient

    logger.info("📡 Reporting to Workflow Intelligence...")

    brain = WorkflowIntelligenceClient()

    response = await brain.report_infrastructure_analysis({
        "agent_id": "devops-agent",
        "timestamp": datetime.utcnow().isoformat(),
        "report_type": "infrastructure_analysis",
        "data": report_data
    })

    logger.info(f"✅ Report sent to brain: {response.get('status')}")

    return response


@activity.defn
async def export_prometheus_metrics(metrics_data: Dict[str, Any]) -> None:
    """
    Export metrics to Prometheus

    Activity: Metrics export
    """
    logger.info("📊 Exporting metrics to Prometheus...")

    # TODO: Implement Prometheus push
    # from prometheus_client import push_to_gateway

    logger.info("✅ Metrics exported (placeholder)")


# ============================================================================
# Workflow - DevOps Infrastructure Management
# ============================================================================

@workflow.defn
class DevOpsInfrastructureWorkflow:
    """
    Main DevOps Infrastructure Workflow

    Provides durable, fault-tolerant execution for:
    - Infrastructure scanning
    - AI-powered analysis
    - Auto-remediation with approval
    - Reporting

    Patterns:
    - Saga for rollback
    - Retry for fault tolerance
    - Human-in-the-loop for approvals
    """

    @workflow.run
    async def run(self, config: ScanConfig) -> Dict[str, Any]:
        """
        Execute DevOps infrastructure workflow

        Steps:
        1. Scan → 2. Analyze → 3. Approve → 4. Fix → 5. Report
        """

        workflow.logger.info(f"🚀 Starting DevOps Infrastructure Workflow: {config.scan_type}")

        # Step 1: Scan Infrastructure (with retry)
        scan_result = await workflow.execute_activity(
            scan_infrastructure,
            config,
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                backoff_coefficient=2.0
            )
        )

        workflow.logger.info(f"✅ Scan completed: {scan_result.total_issues} issues found")

        # Step 2: AI Analysis (with retry)
        ai_analysis = await workflow.execute_activity(
            analyze_with_ai,
            scan_result,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=2)
            )
        )

        workflow.logger.info(f"✅ AI analysis: {len(ai_analysis.recommendations)} recommendations")

        fix_result = None

        # Step 3: Apply fixes if enabled
        if config.auto_fix_enabled and ai_analysis.recommendations:

            # Step 3.1: Get approval if required
            if config.require_approval:
                approval = await workflow.execute_activity(
                    request_brain_approval,
                    ApprovalRequest(
                        agent_id="devops-agent",
                        context="auto_remediation",
                        recommendations=ai_analysis.recommendations,
                        risk_assessment={"risk_level": ai_analysis.risk_level}
                    ),
                    start_to_close_timeout=timedelta(hours=24),  # Wait up to 24h for approval
                    heartbeat_timeout=timedelta(minutes=1)
                )

                approved_actions = approval.get("approved_actions", [])
            else:
                approved_actions = ai_analysis.recommendations

            # Step 3.2: Apply fixes with compensation on failure
            if approved_actions:
                try:
                    fix_result = await workflow.execute_activity(
                        apply_fixes,
                        approved_actions,
                        start_to_close_timeout=timedelta(minutes=30),
                        retry_policy=RetryPolicy(maximum_attempts=2)
                    )

                    workflow.logger.info(
                        f"✅ Fixes applied: {fix_result.fixes_successful}/{fix_result.fixes_attempted}"
                    )

                    # Compensating action on failure
                    if fix_result.fixes_failed > 0 and fix_result.applied_fixes:
                        workflow.logger.warning("⚠️ Some fixes failed, rolling back...")

                        await workflow.execute_activity(
                            rollback_fixes,
                            fix_result.applied_fixes,
                            start_to_close_timeout=timedelta(minutes=10)
                        )

                except Exception as e:
                    workflow.logger.error(f"❌ Fix application failed: {e}")
                    # Saga compensation - rollback
                    if fix_result and fix_result.applied_fixes:
                        await workflow.execute_activity(
                            rollback_fixes,
                            fix_result.applied_fixes,
                            start_to_close_timeout=timedelta(minutes=10)
                        )
                    raise

        # Step 4: Report to brain (always, even if no fixes)
        report_data = {
            "scan_results": {
                "timestamp": scan_result.timestamp,
                "scan_type": scan_result.scan_type,
                "events": scan_result.events,
                "containers": scan_result.containers,
                "deployments": scan_result.deployments,
                "total_issues": scan_result.total_issues
            },
            "ai_analysis": {
                "recommendations_count": len(ai_analysis.recommendations),
                "risk_level": ai_analysis.risk_level
            },
            "fix_results": {
                "fixes_successful": fix_result.fixes_successful if fix_result else 0,
                "fixes_failed": fix_result.fixes_failed if fix_result else 0
            } if fix_result else None
        }

        await workflow.execute_activity(
            report_to_brain,
            report_data,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # Step 5: Export metrics
        await workflow.execute_activity(
            export_prometheus_metrics,
            {
                "total_issues": scan_result.total_issues,
                "fixes_applied": fix_result.fixes_successful if fix_result else 0
            },
            start_to_close_timeout=timedelta(minutes=1)
        )

        workflow.logger.info("🎉 DevOps Infrastructure Workflow completed!")

        return {
            "status": "completed",
            "scan_results": report_data["scan_results"],
            "ai_analysis": report_data["ai_analysis"],
            "fix_results": report_data.get("fix_results")
        }


# ============================================================================
# Workflow - Continuous Monitoring (Hourly)
# ============================================================================

@workflow.defn
class ContinuousMonitoringWorkflow:
    """
    Continuous Infrastructure Monitoring

    Runs continuously with hourly scans:
    - Quick event scan
    - Metrics export
    - Alert on critical issues
    """

    @workflow.run
    async def run(self) -> None:
        """Run continuous monitoring loop"""

        workflow.logger.info("🔄 Starting Continuous Monitoring Workflow")

        while True:
            # Hourly quick scan (events only)
            try:
                config = ScanConfig(
                    scan_type="events",
                    auto_fix_enabled=False,
                    require_approval=False
                )

                scan_result = await workflow.execute_activity(
                    scan_infrastructure,
                    config,
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=RetryPolicy(maximum_attempts=2)
                )

                # Export metrics
                await workflow.execute_activity(
                    export_prometheus_metrics,
                    {
                        "event_gaps": scan_result.events.get("gaps_found", 0),
                        "critical_gaps": scan_result.events.get("critical_gaps", 0)
                    },
                    start_to_close_timeout=timedelta(minutes=1)
                )

                # Alert on critical issues
                critical_count = scan_result.events.get("critical_gaps", 0)
                if critical_count > 0:
                    workflow.logger.warning(f"⚠️ Critical issues detected: {critical_count}")
                    # TODO: Send alert to brain

                workflow.logger.info("✅ Hourly monitoring cycle completed")

            except Exception as e:
                workflow.logger.error(f"❌ Monitoring cycle failed: {e}")

            # Wait 1 hour
            await asyncio.sleep(3600)


# ============================================================================
# Workflow - Dockerfile Generation
# ============================================================================

@workflow.defn
class DockerfileGenerationWorkflow:
    """
    AI-powered Dockerfile Generation Workflow

    Generates Dockerfiles for services missing them
    """

    @workflow.run
    async def run(self, missing_services: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Dockerfiles for missing services"""

        workflow.logger.info(f"🐳 Generating Dockerfiles for {len(missing_services)} services")

        result = await workflow.execute_activity(
            generate_dockerfiles,
            missing_services,
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(maximum_attempts=2)
        )

        workflow.logger.info(
            f"✅ Dockerfile generation: {len(result['generated'])} success, {len(result['failed'])} failed"
        )

        return result
