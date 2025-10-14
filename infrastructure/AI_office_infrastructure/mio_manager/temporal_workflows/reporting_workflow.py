"""
Reporting Workflow - Comprehensive Platform Reporting
======================================================

Temporal wrapper for generating and publishing reports.

Pattern: "Temporal as Wrapper"
- Lightweight orchestration only
- Real work done by reporting components
- Simple retry policies
- Scheduled or on-demand execution

Integration:
- AutomationToolkitManager (metrics collection)
- ReportingEngine (report generation)
- workflow_intelligence_client (brain communication)
- NotificationService (stakeholder alerts)
"""

import logging
from datetime import timedelta
from typing import Dict, Any, List

from temporalio import workflow, activity
from temporalio.common import RetryPolicy

logger = logging.getLogger(__name__)

# Global instances (injected by worker)
_toolkit_manager = None
_reporting_engine = None


def inject_dependencies(toolkit_manager, reporting_engine):
    """Inject dependencies (called by Temporal worker)."""
    global _toolkit_manager, _reporting_engine
    _toolkit_manager = toolkit_manager
    _reporting_engine = reporting_engine
    logger.info("✅ Dependencies injected into Reporting workflow")


# ============================================================================
# ACTIVITIES - Wrappers around real reporting components
# ============================================================================

@activity.defn
async def collect_platform_metrics() -> Dict[str, Any]:
    """
    Collect comprehensive platform metrics.

    Wrapper around AutomationToolkitManager + Prometheus.
    """
    logger.info("📊 Collecting platform metrics for report")

    try:
        # Service discovery
        discovery = await _toolkit_manager.discover_services()

        # Security scan summary
        security = await _toolkit_manager.run_security_scan()

        # Dependency analysis
        dependencies = await _toolkit_manager.analyze_dependencies()

        # Complexity metrics
        complexity = await _toolkit_manager.analyze_complexity()

        return {
            "status": "success",
            "data": {
                "services": discovery,
                "security": security,
                "dependencies": dependencies,
                "complexity": complexity
            }
        }

    except Exception as e:
        logger.error(f"❌ Metrics collection failed: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@activity.defn
async def generate_report(metrics: Dict[str, Any], report_type: str) -> Dict[str, Any]:
    """
    Generate report from metrics.

    Wrapper around ReportingEngine.
    """
    logger.info(f"📝 Generating {report_type} report")

    try:
        # TODO: Real ReportingEngine implementation
        # report = _reporting_engine.generate_report(metrics, report_type)

        # Placeholder
        report = {
            "report_id": f"RPT-{report_type}-001",
            "type": report_type,
            "generated_at": "2025-10-07T12:00:00Z",
            "summary": {
                "total_services": metrics.get('data', {}).get('services', {}).get('total_services', 0),
                "coverage_pct": metrics.get('data', {}).get('services', {}).get('coverage', {}).get('percentage', 0),
                "security_issues": 0
            },
            "url": f"/reports/{report_type}/001.pdf"
        }

        return {
            "status": "success",
            "report": report
        }

    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@activity.defn
async def publish_report_to_brain(report: Dict[str, Any]) -> bool:
    """
    Publish report to workflow_intelligence (brain).

    Wrapper around workflow_intelligence_client.
    """
    logger.info(f"🧠 Publishing report to brain: {report.get('report_id')}")

    try:
        # TODO: Real workflow_intelligence_client implementation
        # await workflow_intelligence_client.publish_report(report)

        return True

    except Exception as e:
        logger.error(f"❌ Publishing to brain failed: {e}")
        return False


@activity.defn
async def notify_stakeholders(report: Dict[str, Any], stakeholders: List[str]) -> int:
    """
    Notify stakeholders about new report.

    Wrapper around NotificationService.
    """
    logger.info(f"📧 Notifying {len(stakeholders)} stakeholders")

    try:
        # TODO: Real NotificationService implementation
        # for stakeholder in stakeholders:
        #     await notification_service.send(stakeholder, report)

        return len(stakeholders)

    except Exception as e:
        logger.error(f"❌ Stakeholder notification failed: {e}")
        return 0


# ============================================================================
# WORKFLOW - Lightweight orchestration wrapper
# ============================================================================

@workflow.defn
class ReportingWorkflow:
    """
    Reporting Workflow - Comprehensive reporting wrapper.

    Simple orchestration:
    1. Collect metrics
    2. Generate report
    3. Publish to brain
    4. Notify stakeholders

    Can be:
    - Scheduled (daily/weekly/monthly)
    - On-demand (triggered by API)
    - Event-driven (after incident resolution)

    Temporal provides: durability, scheduling, retry.
    """

    @workflow.run
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute reporting workflow.

        Args:
            config: {
                'report_type': 'daily' | 'weekly' | 'monthly' | 'incident',
                'stakeholders': ['team@example.com'],
                'publish_to_brain': True
            }
        """
        report_type = config.get('report_type', 'daily')
        workflow.logger.info(f"🚀 Starting Reporting Workflow: {report_type}")

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=30),
            maximum_attempts=3
        )

        try:
            # 1. Collect platform metrics
            metrics = await workflow.execute_activity(
                collect_platform_metrics,
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy
            )

            if metrics['status'] != 'success':
                workflow.logger.error(f"Metrics collection failed: {metrics}")
                return {
                    "status": "failed",
                    "stage": "metrics_collection",
                    "error": metrics.get('error')
                }

            # 2. Generate report
            report_result = await workflow.execute_activity(
                generate_report,
                args=[metrics, report_type],
                start_to_close_timeout=timedelta(minutes=3),
                retry_policy=retry_policy
            )

            if report_result['status'] != 'success':
                workflow.logger.error(f"Report generation failed: {report_result}")
                return {
                    "status": "failed",
                    "stage": "report_generation",
                    "error": report_result.get('error')
                }

            report = report_result['report']
            workflow.logger.info(f"✅ Report generated: {report.get('report_id')}")

            # 3. Publish to brain (if requested)
            if config.get('publish_to_brain', True):
                published = await workflow.execute_activity(
                    publish_report_to_brain,
                    args=[report],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=retry_policy
                )

                if published:
                    workflow.logger.info("✅ Published to brain")
                else:
                    workflow.logger.warning("⚠️ Failed to publish to brain")

            # 4. Notify stakeholders
            stakeholders = config.get('stakeholders', [])
            if stakeholders:
                notified = await workflow.execute_activity(
                    notify_stakeholders,
                    args=[report, stakeholders],
                    start_to_close_timeout=timedelta(minutes=1),
                    retry_policy=retry_policy
                )

                workflow.logger.info(f"✅ Notified {notified} stakeholders")

            return {
                "status": "success",
                "report_id": report.get('report_id'),
                "report_url": report.get('url'),
                "stakeholders_notified": len(stakeholders)
            }

        except Exception as e:
            workflow.logger.error(f"❌ Reporting workflow failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }


# Export for worker registration
reporting_activities = [
    collect_platform_metrics,
    generate_report,
    publish_report_to_brain,
    notify_stakeholders
]
