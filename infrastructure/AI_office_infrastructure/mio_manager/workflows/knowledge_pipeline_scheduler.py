"""
Knowledge Pipeline Scheduler
============================

Integrates Automated Knowledge Pipeline into mio-manager's scheduled automation.

**Schedule:**
- Daily full pipeline (02:00 UTC)
- Hourly analysis (00:00 every hour)

**Integration:**
- Calls analytics-specialist pipeline API
- Monitors execution
- Sends notifications
- Records metrics

**Configuration:**
See: infrastructure/AI-office-infrastructure/analytics-specialist/config/pipeline_config.yaml
"""

import asyncio
import httpx
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class KnowledgePipelineScheduler:
    """
    Scheduler for Automated Knowledge Pipeline

    Integrates with:
    - analytics-specialist API (pipeline execution)
    - notification-service (alerts)
    - monitoring service (metrics)
    """

    def __init__(
        self,
        analytics_specialist_url: str = "http://localhost:8007",
        notification_url: str = "http://localhost:8005",
        monitoring_url: str = "http://localhost:8009"
    ):
        self.analytics_url = analytics_specialist_url
        self.notification_url = notification_url
        self.monitoring_url = monitoring_url

        self.client = httpx.AsyncClient(timeout=600.0)  # 10 min timeout

        logger.info(f"KnowledgePipelineScheduler initialized")
        logger.info(f"  Analytics Specialist: {self.analytics_url}")

    async def schedule_daily_full_pipeline(self):
        """
        Daily full pipeline (runs at 02:00 UTC)

        Executes all stages:
        - System analysis
        - Pattern extraction
        - Documentation generation
        - Rules generation
        - RAG integration
        - Event catalog
        """
        logger.info("🚀 Starting daily full pipeline")

        try:
            # Trigger pipeline
            response = await self.client.post(
                f"{self.analytics_url}/api/v1/pipeline/trigger",
                json={
                    "mode": "full",
                    "async_execution": True
                }
            )

            if response.status_code == 200:
                result = response.json()
                run_id = result["run_id"]

                logger.info(f"✅ Pipeline triggered: {run_id}")

                # Monitor execution
                await self._monitor_pipeline_execution(run_id)

                # Send success notification
                await self._send_notification(
                    level="info",
                    title="✅ Daily Knowledge Pipeline Complete",
                    message=f"Full pipeline completed successfully. Run ID: {run_id}"
                )

                # Record metrics
                await self._record_metrics("pipeline.daily.success", 1)

            else:
                raise Exception(f"Pipeline trigger failed: {response.status_code} {response.text}")

        except Exception as e:
            logger.error(f"❌ Daily pipeline failed: {e}")

            # Send failure notification
            await self._send_notification(
                level="error",
                title="🚨 Daily Knowledge Pipeline Failed",
                message=f"Error: {str(e)}"
            )

            # Record failure metric
            await self._record_metrics("pipeline.daily.failure", 1)

    async def schedule_hourly_analysis(self):
        """
        Hourly analysis (runs at :00 every hour)

        Executes:
        - System analysis
        - Pattern extraction
        """
        logger.info("🔍 Starting hourly analysis")

        try:
            # Trigger analysis
            response = await self.client.post(
                f"{self.analytics_url}/api/v1/pipeline/trigger",
                json={
                    "mode": "analyze",
                    "async_execution": True
                }
            )

            if response.status_code == 200:
                result = response.json()
                run_id = result["run_id"]

                logger.info(f"✅ Analysis triggered: {run_id}")

                # Monitor execution (but don't block)
                asyncio.create_task(self._monitor_pipeline_execution(run_id))

                # Record metrics
                await self._record_metrics("pipeline.hourly.triggered", 1)

            else:
                raise Exception(f"Analysis trigger failed: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Hourly analysis failed: {e}")
            await self._record_metrics("pipeline.hourly.failure", 1)

    async def trigger_on_demand(
        self,
        mode: str = "full",
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Trigger pipeline on demand

        **Args:**
        - mode: "full", "analyze", "docs", "index"
        - reason: Why this was triggered (for logging)

        **Returns:**
        - Pipeline run details
        """
        logger.info(f"🎯 On-demand pipeline trigger: mode={mode}, reason={reason}")

        try:
            response = await self.client.post(
                f"{self.analytics_url}/api/v1/pipeline/trigger",
                json={
                    "mode": mode,
                    "async_execution": False  # Synchronous for on-demand
                }
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ On-demand pipeline complete: {result['run_id']}")

                # Record metrics
                await self._record_metrics(f"pipeline.on_demand.{mode}", 1)

                return result

            else:
                raise Exception(f"Pipeline failed: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ On-demand pipeline failed: {e}")
            await self._record_metrics(f"pipeline.on_demand.{mode}.failure", 1)
            raise

    async def check_pipeline_health(self) -> Dict[str, Any]:
        """Check if pipeline service is healthy"""
        try:
            response = await self.client.get(
                f"{self.analytics_url}/api/v1/pipeline/health"
            )

            if response.status_code == 200:
                health = response.json()
                logger.info(f"Pipeline health: {health['status']}")
                return health
            else:
                logger.warning(f"Pipeline health check failed: {response.status_code}")
                return {"status": "error", "code": response.status_code}

        except Exception as e:
            logger.error(f"Pipeline health check error: {e}")
            return {"status": "error", "message": str(e)}

    # === Private Helper Methods ===

    async def _monitor_pipeline_execution(self, run_id: str, poll_interval: int = 30):
        """Monitor pipeline execution until complete"""
        logger.info(f"👀 Monitoring pipeline: {run_id}")

        max_attempts = 60  # 30 min max
        attempts = 0

        while attempts < max_attempts:
            try:
                # Check status
                response = await self.client.get(
                    f"{self.analytics_url}/api/v1/pipeline/status/{run_id}"
                )

                if response.status_code == 200:
                    status = response.json()

                    if status["status"] == "completed":
                        logger.info(f"✅ Pipeline {run_id} completed")
                        logger.info(f"   Stages: {len(status['stages_completed'])}")
                        logger.info(f"   Duration: {status['duration_seconds']:.2f}s")
                        return status

                    elif status["status"] == "failed":
                        logger.error(f"❌ Pipeline {run_id} failed")
                        logger.error(f"   Errors: {status['errors']}")
                        return status

                    elif status["status"] == "running":
                        logger.info(f"⏳ Pipeline {run_id} running... ({attempts * poll_interval}s)")

                # Wait before next poll
                await asyncio.sleep(poll_interval)
                attempts += 1

            except Exception as e:
                logger.error(f"Error monitoring pipeline: {e}")
                await asyncio.sleep(poll_interval)
                attempts += 1

        logger.warning(f"⚠️  Pipeline {run_id} monitoring timeout after {max_attempts * poll_interval}s")

    async def _send_notification(
        self,
        level: str,
        title: str,
        message: str
    ):
        """Send notification via notification-service"""
        try:
            await self.client.post(
                f"{self.notification_url}/api/v1/notifications/send",
                json={
                    "level": level,
                    "title": title,
                    "message": message,
                    "channels": ["slack", "email"],
                    "source": "knowledge_pipeline_scheduler"
                }
            )
            logger.info(f"📧 Notification sent: {title}")

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    async def _record_metrics(self, metric_name: str, value: float):
        """Record metrics to monitoring service"""
        try:
            await self.client.post(
                f"{self.monitoring_url}/api/v1/metrics",
                json={
                    "metric": metric_name,
                    "value": value,
                    "timestamp": datetime.now().isoformat(),
                    "labels": {
                        "source": "knowledge_pipeline_scheduler",
                        "component": "automation"
                    }
                }
            )

        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# === Integration with mio-manager scheduler ===

async def setup_pipeline_schedules():
    """
    Set up scheduled jobs for knowledge pipeline

    Call this from mio-manager main.py startup
    """
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    scheduler = AsyncIOScheduler()
    pipeline_scheduler = KnowledgePipelineScheduler()

    # Daily full pipeline at 02:00 UTC
    scheduler.add_job(
        pipeline_scheduler.schedule_daily_full_pipeline,
        trigger="cron",
        hour=2,
        minute=0,
        id="daily_full_pipeline",
        name="Daily Full Knowledge Pipeline"
    )

    # Hourly analysis
    scheduler.add_job(
        pipeline_scheduler.schedule_hourly_analysis,
        trigger="cron",
        minute=0,
        id="hourly_analysis",
        name="Hourly System Analysis"
    )

    scheduler.start()
    logger.info("✅ Knowledge Pipeline schedules configured")

    return scheduler, pipeline_scheduler


# === Example usage ===

async def main():
    """Test scheduler"""
    scheduler = KnowledgePipelineScheduler()

    # Check health
    health = await scheduler.check_pipeline_health()
    print(f"Pipeline health: {health}")

    # Trigger on-demand
    # result = await scheduler.trigger_on_demand(mode="analyze", reason="testing")
    # print(f"On-demand result: {result}")

    await scheduler.close()


if __name__ == "__main__":
    asyncio.run(main())
