"""
KPI Auto-Collection Tasks
Celery tasks for automatic KPI data collection from BCM modules
"""

from celery import shared_task
from datetime import datetime, timedelta
import logging
from typing import Dict, Optional
import asyncio

from integrations.bcm_client import get_bcm_client
from database import get_db, KPIMeasurement, KPIDefinition

logger = logging.getLogger(__name__)


# ===== HELPER FUNCTIONS =====

async def record_kpi_measurement(
    tenant_id: str,
    kpi_code: str,
    value: float,
    collection_method: str = "automated",
    data_quality: str = "high",
    metadata: Optional[Dict] = None
):
    """
    Record KPI measurement to database

    Args:
        tenant_id: Tenant ID
        kpi_code: KPI code (e.g., "PLAN_CURRENCY")
        value: Measured value
        collection_method: How data was collected
        data_quality: Data quality level
        metadata: Additional metadata
    """
    try:
        db = next(get_db())

        # Find KPI definition
        kpi_def = db.query(KPIDefinition).filter(
            KPIDefinition.tenant_id == tenant_id,
            KPIDefinition.kpi_code == kpi_code
        ).first()

        if not kpi_def:
            logger.warning(f"KPI definition not found: {kpi_code} for tenant {tenant_id}")
            return

        # Create measurement
        measurement = KPIMeasurement(
            tenant_id=tenant_id,
            kpi_id=kpi_def.id,
            measurement_date=datetime.utcnow(),
            value=value,
            collection_method=collection_method,
            data_quality=data_quality,
            notes=f"Auto-collected at {datetime.utcnow().isoformat()}",
            collected_by="system_auto_collector",
            metadata=metadata or {}
        )

        db.add(measurement)
        db.commit()

        logger.info(f"✅ Recorded KPI {kpi_code} = {value} for tenant {tenant_id}")

    except Exception as e:
        logger.error(f"❌ Failed to record KPI {kpi_code}: {e}")
        db.rollback()


# ===== KPI COLLECTION TASKS =====

@shared_task(name='tasks.kpi_collector.collect_plan_currency_rate')
def collect_plan_currency_rate(tenant_id: str):
    """
    Collect Plan Currency Rate KPI
    Measures % of BC plans that are current (reviewed within period)
    """
    logger.info(f"📊 Collecting Plan Currency Rate for tenant {tenant_id}")

    async def _collect():
        client = get_bcm_client()
        stats = await client.get_plans_currency_stats(tenant_id)

        if stats and "currency_rate" in stats:
            await record_kpi_measurement(
                tenant_id=tenant_id,
                kpi_code="PLAN_CURRENCY",
                value=stats["currency_rate"],
                metadata={
                    "current_plans": stats.get("current_plans", 0),
                    "total_plans": stats.get("total_plans", 0)
                }
            )
        else:
            logger.warning(f"No plan currency data for tenant {tenant_id}")

    asyncio.run(_collect())


@shared_task(name='tasks.kpi_collector.collect_rto_achievement_rate')
def collect_rto_achievement_rate(tenant_id: str):
    """
    Collect RTO Achievement Rate KPI
    Measures % of incidents recovered within RTO
    """
    logger.info(f"📊 Collecting RTO Achievement Rate for tenant {tenant_id}")

    async def _collect():
        client = get_bcm_client()
        stats = await client.get_rto_achievement_stats(tenant_id)

        if stats and "achievement_rate" in stats:
            await record_kpi_measurement(
                tenant_id=tenant_id,
                kpi_code="RTO_ACHIEVEMENT",
                value=stats["achievement_rate"],
                metadata={
                    "within_rto": stats.get("within_rto", 0),
                    "total_incidents": stats.get("total", 0)
                }
            )
        else:
            logger.warning(f"No RTO achievement data for tenant {tenant_id}")

    asyncio.run(_collect())


@shared_task(name='tasks.kpi_collector.collect_exercise_completion_rate')
def collect_exercise_completion_rate(tenant_id: str):
    """
    Collect Exercise Completion Rate KPI
    Measures % of planned exercises completed
    """
    logger.info(f"📊 Collecting Exercise Completion Rate for tenant {tenant_id}")

    async def _collect():
        client = get_bcm_client()

        # Get exercises from last 12 months
        since_date = (datetime.utcnow() - timedelta(days=365)).isoformat()
        stats = await client.get_exercise_summary(tenant_id, since_date)

        if stats:
            planned = stats.get("total_planned", 0)
            completed = stats.get("completed", 0)
            completion_rate = (completed / planned * 100) if planned > 0 else 0

            await record_kpi_measurement(
                tenant_id=tenant_id,
                kpi_code="EXERCISE_COMPLETION",
                value=completion_rate,
                metadata={
                    "planned": planned,
                    "completed": completed,
                    "period": "12_months"
                }
            )
        else:
            logger.warning(f"No exercise data for tenant {tenant_id}")

    asyncio.run(_collect())


@shared_task(name='tasks.kpi_collector.collect_training_completion_rate')
def collect_training_completion_rate(tenant_id: str):
    """
    Collect Training Completion Rate KPI
    Measures % of assigned trainings completed
    """
    logger.info(f"📊 Collecting Training Completion Rate for tenant {tenant_id}")

    async def _collect():
        client = get_bcm_client()
        stats = await client.get_training_completion_stats(tenant_id)

        if stats and "completion_rate" in stats:
            await record_kpi_measurement(
                tenant_id=tenant_id,
                kpi_code="TRAINING_COMPLETION",
                value=stats["completion_rate"],
                metadata={
                    "completed": stats.get("completed", 0),
                    "assigned": stats.get("assigned", 0)
                }
            )
        else:
            logger.warning(f"No training completion data for tenant {tenant_id}")

    asyncio.run(_collect())


@shared_task(name='tasks.kpi_collector.collect_audit_finding_closure_rate')
def collect_audit_finding_closure_rate(tenant_id: str):
    """
    Collect Audit Finding Closure Rate KPI
    Measures % of audit findings closed
    """
    logger.info(f"📊 Collecting Audit Finding Closure Rate for tenant {tenant_id}")

    async def _collect():
        client = get_bcm_client()
        stats = await client.get_audit_finding_closure_stats(tenant_id)

        if stats and "closure_rate" in stats:
            await record_kpi_measurement(
                tenant_id=tenant_id,
                kpi_code="FINDING_CLOSURE",
                value=stats["closure_rate"],
                metadata={
                    "closed": stats.get("closed", 0),
                    "total": stats.get("total", 0)
                }
            )
        else:
            logger.warning(f"No audit finding data for tenant {tenant_id}")

    asyncio.run(_collect())


@shared_task(name='tasks.kpi_collector.collect_capa_effectiveness_rate')
def collect_capa_effectiveness_rate(tenant_id: str):
    """
    Collect CAPA Effectiveness Rate KPI
    Measures % of CAPAs that are effective
    """
    logger.info(f"📊 Collecting CAPA Effectiveness Rate for tenant {tenant_id}")

    async def _collect():
        client = get_bcm_client()
        stats = await client.get_capa_effectiveness_stats(tenant_id)

        if stats and "effectiveness_rate" in stats:
            await record_kpi_measurement(
                tenant_id=tenant_id,
                kpi_code="CAPA_EFFECTIVENESS",
                value=stats["effectiveness_rate"],
                metadata={
                    "effective": stats.get("effective", 0),
                    "total": stats.get("total", 0)
                }
            )
        else:
            logger.warning(f"No CAPA effectiveness data for tenant {tenant_id}")

    asyncio.run(_collect())


@shared_task(name='tasks.kpi_collector.collect_incident_response_time')
def collect_incident_response_time(tenant_id: str):
    """
    Collect Average Incident Response Time KPI
    Measures average time to respond to incidents (minutes)
    """
    logger.info(f"📊 Collecting Incident Response Time for tenant {tenant_id}")

    async def _collect():
        client = get_bcm_client()
        stats = await client.get_incident_response_time_stats(tenant_id)

        if stats and "avg_response_time" in stats:
            await record_kpi_measurement(
                tenant_id=tenant_id,
                kpi_code="INCIDENT_RESPONSE_TIME",
                value=stats["avg_response_time"],
                metadata={
                    "total_incidents": stats.get("total_incidents", 0),
                    "unit": "minutes"
                }
            )
        else:
            logger.warning(f"No incident response time data for tenant {tenant_id}")

    asyncio.run(_collect())


# ===== MASTER COLLECTION TASK =====

@shared_task(name='tasks.kpi_collector.collect_all_kpis')
def collect_all_kpis():
    """
    Master task: Collect all KPIs for all active tenants
    Runs daily via Celery Beat
    """
    logger.info("🚀 Starting daily KPI collection for all tenants")

    try:
        db = next(get_db())

        # Get all active tenants
        # Assuming we have a tenants table or we extract unique tenant_ids from KPI definitions
        tenants = db.query(KPIDefinition.tenant_id).distinct().all()

        for (tenant_id,) in tenants:
            logger.info(f"📊 Collecting KPIs for tenant: {tenant_id}")

            # Trigger individual KPI collection tasks
            collect_plan_currency_rate.delay(tenant_id)
            collect_rto_achievement_rate.delay(tenant_id)
            collect_exercise_completion_rate.delay(tenant_id)
            collect_training_completion_rate.delay(tenant_id)
            collect_audit_finding_closure_rate.delay(tenant_id)
            collect_capa_effectiveness_rate.delay(tenant_id)
            collect_incident_response_time.delay(tenant_id)

        logger.info(f"✅ KPI collection triggered for {len(tenants)} tenants")

    except Exception as e:
        logger.error(f"❌ Master KPI collection failed: {e}")


# ===== ON-DEMAND COLLECTION =====

@shared_task(name='tasks.kpi_collector.collect_kpis_for_tenant')
def collect_kpis_for_tenant(tenant_id: str):
    """
    On-demand: Collect all KPIs for specific tenant
    Can be triggered via API
    """
    logger.info(f"📊 On-demand KPI collection for tenant {tenant_id}")

    # Trigger all individual tasks
    tasks = [
        collect_plan_currency_rate.delay(tenant_id),
        collect_rto_achievement_rate.delay(tenant_id),
        collect_exercise_completion_rate.delay(tenant_id),
        collect_training_completion_rate.delay(tenant_id),
        collect_audit_finding_closure_rate.delay(tenant_id),
        collect_capa_effectiveness_rate.delay(tenant_id),
        collect_incident_response_time.delay(tenant_id)
    ]

    logger.info(f"✅ Triggered {len(tasks)} KPI collection tasks for tenant {tenant_id}")
    return {"tenant_id": tenant_id, "tasks_triggered": len(tasks)}
