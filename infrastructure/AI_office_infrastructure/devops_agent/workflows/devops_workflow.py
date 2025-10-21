#!/usr/bin/env python3
"""
DevOps Agent Temporal Workflow

Orchestrates DevOps Agent operations through Temporal
"""

from datetime import timedelta
from typing import Dict
from temporalio import workflow, activity
import logging

logger = logging.getLogger(__name__)


@activity.defn
async def scan_infrastructure(config: Dict) -> Dict:
    """Scan infrastructure - Activity"""
    from tools.devops_agent.agent import DevOpsAgent

    agent = DevOpsAgent(config.get("project_root", "/Users/MD/AI-Platform-ISO"))
    await agent.initialize()

    scan_type = config.get("scan_type", "full")
    results = await agent.scan_infrastructure(scan_type)

    return results


@activity.defn
async def ai_analysis(scan_results: Dict) -> Dict:
    """AI analysis of scan results - Activity"""
    from tools.devops_agent.agent import DevOpsAgent

    agent = DevOpsAgent("/Users/MD/AI-Platform-ISO")
    await agent.initialize()

    analysis = await agent.ai_analysis(scan_results)
    return analysis


@activity.defn
async def apply_fixes(recommendations: List[Dict]) -> Dict:
    """Apply auto-remediation - Activity"""
    from tools.devops_agent.agent import DevOpsAgent

    agent = DevOpsAgent("/Users/MD/AI-Platform-ISO")
    await agent.initialize()

    results = await agent.apply_fixes(recommendations)
    return results


@activity.defn
async def report_to_brain(analysis: Dict) -> Dict:
    """Report to Workflow Intelligence - Activity"""
    from tools.devops_agent.agent import DevOpsAgent

    agent = DevOpsAgent("/Users/MD/AI-Platform-ISO")
    await agent.initialize()

    await agent.report_to_brain(analysis)
    return {"status": "reported"}


@workflow.defn
class DevOpsAgentWorkflow:
    """
    DevOps Agent Workflow

    Orchestrates:
    1. Infrastructure scanning
    2. AI analysis
    3. Auto-remediation (if approved)
    4. Reporting to мозг
    """

    @workflow.run
    async def run(self, config: Dict) -> Dict:
        """
        Main workflow execution

        Args:
            config: Workflow configuration
                - scan_type: 'full', 'events', 'containers', 'deployments'
                - auto_fix: bool - apply fixes automatically
                - report_to_brain: bool - send report to мозг

        Returns:
            Workflow results
        """
        workflow.logger.info(f" DevOps Agent Workflow started: {config}")

        # Step 1: Scan infrastructure
        workflow.logger.info("Step 1: Scanning infrastructure...")
        scan_results = await workflow.execute_activity(
            scan_infrastructure,
            config,
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=workflow.RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1)
            )
        )

        workflow.logger.info(f" Scan complete: {scan_results.get('total_issues', 0)} issues")

        # Step 2: AI Analysis
        workflow.logger.info("Step 2: AI analysis...")
        analysis = await workflow.execute_activity(
            ai_analysis,
            scan_results,
            start_to_close_timeout=timedelta(minutes=5)
        )

        workflow.logger.info(f" AI analysis: {len(analysis.get('ai_recommendations', []))} recommendations")

        # Step 3: Auto-fix (if approved)
        fix_results = {}
        if config.get("auto_fix") and analysis.get("auto_fix_approved"):
            workflow.logger.info("Step 3: Applying fixes...")
            fix_results = await workflow.execute_activity(
                apply_fixes,
                analysis["ai_recommendations"],
                start_to_close_timeout=timedelta(minutes=15)
            )

            workflow.logger.info(f" Fixes: {fix_results.get('fixes_successful', 0)} successful")

        # Step 4: Report to мозг
        if config.get("report_to_brain", True):
            workflow.logger.info("Step 4: Reporting to мозг...")
            await workflow.execute_activity(
                report_to_brain,
                {
                    "scan_results": scan_results,
                    "analysis": analysis,
                    "fix_results": fix_results
                },
                start_to_close_timeout=timedelta(minutes=2)
            )

            workflow.logger.info(" Report sent to Workflow Intelligence")

        # Return final results
        return {
            "status": "completed",
            "scan_results": scan_results,
            "analysis": analysis,
            "fix_results": fix_results
        }


@workflow.defn
class DevOpsWeeklyDeepScan:
    """
    Weekly Deep Scan Workflow

    Runs every Monday at 03:00
    - Full infrastructure scan
    - Dockerfile generation
    - Port conflict detection
    - Deployment health check
    - Comprehensive report
    """

    @workflow.run
    async def run(self) -> Dict:
        """Weekly deep scan execution"""
        workflow.logger.info("️  Weekly Deep Scan started (Monday 03:00)")

        config = {
            "scan_type": "full",
            "auto_fix": False,  # Manual review required
            "report_to_brain": True
        }

        # Use main DevOps Agent workflow
        result = await workflow.execute_child_workflow(
            DevOpsAgentWorkflow.run,
            config,
            id=f"devops-weekly-scan-{workflow.now().isoformat()}"
        )

        workflow.logger.info(" Weekly Deep Scan completed")
        return result
