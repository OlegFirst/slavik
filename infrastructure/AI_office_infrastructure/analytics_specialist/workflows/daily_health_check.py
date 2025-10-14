"""
Daily Health Check Workflow
============================

Automated daily platform health analysis and reporting to MIO Manager.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from core import AnalyticsCore
from models import SeverityLevel, MIOTaskDelegation

logger = logging.getLogger(__name__)


async def daily_health_check() -> Dict[str, Any]:
    """
    Daily platform health check workflow

    Workflow:
    1. Analytics Specialist analyzes platform health
    2. Generates insights and recommendations
    3. Reports to MIO Manager
    4. If critical issues → Requests task delegation

    Returns:
        Workflow execution result

    Example:
        ```python
        # Scheduled execution (cron)
        @scheduled(cron="0 9 * * *")  # Every day at 09:00
        async def run_daily_health_check():
            result = await daily_health_check()
            print(f"Health score: {result['health_score']}")
        ```
    """
    logger.info("=" * 60)
    logger.info("🏥 DAILY HEALTH CHECK WORKFLOW START")
    logger.info("=" * 60)

    start_time = datetime.now()

    try:
        # Initialize Analytics Core
        core = AnalyticsCore()
        await core.initialize()

        logger.info("📊 Analyzing platform health...")

        # Perform comprehensive analysis
        report = await core.analyze_platform_health()

        logger.info(
            f"✅ Analysis complete: "
            f"health_score={report.overall_health_score:.1f}/100, "
            f"insights={len(report.insights)}, "
            f"critical={len(report.critical_insights)}"
        )

        # Report to MIO Manager
        logger.info("📤 Reporting insights to MIO Manager...")
        mio_response = await core.report_to_mio(report)

        logger.info(f"✅ MIO Manager response: {mio_response.get('status')}")

        # If critical issues → Request task delegation
        if len(report.critical_insights) > 0:
            logger.warning(
                f"⚠️  Found {len(report.critical_insights)} CRITICAL issues! "
                f"Requesting task delegation..."
            )

            # Prepare actions
            actions = [
                {
                    "type": "investigate",
                    "target": insight.affected_components[0] if insight.affected_components else "platform",
                    "details": {
                        "insight_id": insight.id,
                        "category": insight.category.value,
                        "title": insight.title
                    }
                }
                for insight in report.critical_insights[:3]  # Top 3 critical
            ]

            # Request delegation
            task = MIOTaskDelegation(
                title=f"Fix {len(report.critical_insights)} critical platform issues",
                priority="high",
                actions=actions,
                metadata={
                    "report_id": report.id,
                    "health_score": report.overall_health_score,
                    "workflow": "daily_health_check"
                }
            )

            delegation_response = await core.mio_client.delegate_task(task)
            logger.info(f"✅ Task delegated: {delegation_response.get('status')}")

        # Calculate execution time
        duration = (datetime.now() - start_time).total_seconds()

        result = {
            "status": "success",
            "workflow": "daily_health_check",
            "executed_at": start_time.isoformat(),
            "duration_seconds": duration,
            "health_score": report.overall_health_score,
            "total_insights": len(report.insights),
            "critical_insights": len(report.critical_insights),
            "high_severity_insights": len(report.high_severity_insights),
            "recommendations_generated": len(report.recommendations),
            "reported_to_mio": mio_response.get("status") == "success",
            "task_delegated": len(report.critical_insights) > 0,
            "report_id": report.id
        }

        logger.info("=" * 60)
        logger.info(f"✅ DAILY HEALTH CHECK COMPLETE (duration: {duration:.1f}s)")
        logger.info(f"   Health Score: {report.overall_health_score:.1f}/100")
        logger.info(f"   Insights: {len(report.insights)} (Critical: {len(report.critical_insights)})")
        logger.info(f"   Recommendations: {len(report.recommendations)}")
        logger.info("=" * 60)

        return result

    except Exception as e:
        logger.error(f"❌ Daily health check failed: {e}", exc_info=True)

        return {
            "status": "error",
            "workflow": "daily_health_check",
            "executed_at": start_time.isoformat(),
            "error": str(e),
            "duration_seconds": (datetime.now() - start_time).total_seconds()
        }


async def continuous_improvement_scan() -> Dict[str, Any]:
    """
    Continuous improvement workflow (runs hourly)

    Scans for improvement opportunities without generating alerts.
    Lower priority than daily health check.

    Returns:
        Workflow execution result

    Example:
        ```python
        @scheduled(interval="hourly")
        async def run_continuous_improvement():
            result = await continuous_improvement_scan()
        ```
    """
    logger.info("🔍 Continuous improvement scan...")

    try:
        core = AnalyticsCore()
        await core.initialize()

        # Analyze platform health
        report = await core.analyze_platform_health()

        # Filter to improvement opportunities only
        improvements = [
            insight
            for insight in report.insights
            if insight.severity in [SeverityLevel.LOW, SeverityLevel.MEDIUM]
        ]

        logger.info(f"Found {len(improvements)} improvement opportunities")

        # Only report if there are actionable improvements
        if len(improvements) > 5:  # Threshold
            # Report to MIO (low priority)
            await core.report_to_mio(report)

        return {
            "status": "success",
            "workflow": "continuous_improvement",
            "improvements_found": len(improvements),
            "health_score": report.overall_health_score
        }

    except Exception as e:
        logger.error(f"Continuous improvement scan failed: {e}")
        return {
            "status": "error",
            "workflow": "continuous_improvement",
            "error": str(e)
        }
