"""
API Routes
All validation service endpoints

NOTE: Due to migration from monolithic main.py, many endpoints are preserved here.
Business logic should be gradually extracted to service layer.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

# Import from new structure
import sys
from pathlib import Path

# Add parent directory to path for shared library
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))

from shared.database import get_db
from models.database import (
    Exercise as ExerciseDB,
    ExerciseScenario as ExerciseScenarioDB,
    ExerciseObservation as ExerciseObservationDB,
    ExerciseAction as ExerciseActionDB,
    KPI as KPIDB,
    KPIMeasurement as KPIMeasurementDB,
    AuditPlan as AuditPlanDB,
    AuditFinding as AuditFindingDB,
    CAPA as CAPADB,
    ManagementReview as ManagementReviewDB,
)
from models.domain import (
    ExerciseType, ExerciseStatus, ObservationType, ObservationSeverity,
    PerformanceDirection, MeasurementFrequency, PerformanceStatus,
    DataQuality, CollectionMethod,
    AuditType, AuditStatus, FindingType, FindingSeverity,
    CAPAType, CAPAStatus, CAPASource,
)
from workflows import (
    can_start_exercise, can_complete_exercise, can_review_exercise,
    can_start_audit, can_complete_fieldwork, can_issue_report,
    can_implement_capa, can_verify_capa, can_close_capa,
    calculate_kpi_status, calculate_kpi_trend, get_kpi_summary,
)
from api.schemas import (
    ExerciseCreate, ExerciseUpdate, ExerciseResponse,
    ObservationCreate, ScenarioCreate,
    KPICreate, KPIUpdate, KPIResponse, MeasurementCreate,
    AuditCreate, AuditUpdate, AuditResponse, FindingCreate,
    CAPACreate, CAPAUpdate, CAPAResponse,
    ManagementReviewCreate, ManagementReviewResponse,
)

import logging

# Import services for dependency injection
from services.kpi_service import KPIService
from services.audit_service import AuditService
from services.exercise_service import ExerciseService
from services.scenario_service import ScenarioService
from services.capa_service import CAPAService
from repositories.repository import ValidationRepository

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/validation", tags=["validation"])


# ==================== DEPENDENCY INJECTION ====================

def get_validation_repository(db: AsyncSession = Depends(get_db)) -> ValidationRepository:
    """Get validation repository instance"""
    return ValidationRepository(db)


def get_kpi_service(repo: ValidationRepository = Depends(get_validation_repository)) -> KPIService:
    """Get KPI service instance"""
    return KPIService(repo)


def get_audit_service(repo: ValidationRepository = Depends(get_validation_repository)) -> AuditService:
    """Get audit service instance"""
    return AuditService(repo)


def get_exercise_service(repo: ValidationRepository = Depends(get_validation_repository)) -> ExerciseService:
    """Get exercise service instance"""
    return ExerciseService(repo)


def get_scenario_service(repo: ValidationRepository = Depends(get_validation_repository)) -> ScenarioService:
    """Get scenario service instance"""
    return ScenarioService(repo)


def get_capa_service(repo: ValidationRepository = Depends(get_validation_repository)) -> CAPAService:
    """Get CAPA service instance"""
    return CAPAService(repo)


# ==================== EXERCISE ENDPOINTS ====================

@router.post("/exercises", response_model=ExerciseResponse, status_code=201)
async def create_exercise(exercise: ExerciseCreate, exercise_service: ExerciseService = Depends(get_exercise_service)):
    """Create new exercise"""
    try:
        exercise_data = {
            "tenant_id": exercise.tenant_id,
            "exercise_code": exercise.exercise_code,
            "exercise_name": exercise.exercise_name,
            "description": exercise.description,
            "exercise_type": exercise.exercise_type,
            "scenario_id": exercise.scenario_id,
            "complexity_level": exercise.complexity_level,
            "objectives": exercise.objectives,
            "success_criteria": exercise.success_criteria,
            "planned_date": exercise.planned_date,
            "planned_duration_hours": exercise.planned_duration_hours,
            "facilitator": exercise.facilitator,
            "participants": exercise.participants,
        }

        result = await exercise_service.create_exercise(exercise_data)
        logger.info(f"Exercise created: {result.id} - {result.exercise_name}")
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Exercise creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exercises", response_model=List[ExerciseResponse])
async def list_exercises(
    tenant_id: str,
    status: Optional[ExerciseStatus] = None,
    exercise_type: Optional[ExerciseType] = None,
    exercise_service: ExerciseService = Depends(get_exercise_service)
):
    """List exercises with filters"""
    try:
        result = await exercise_service.list_exercises(tenant_id, status, exercise_type)
        logger.info(f"Listed {len(result)} exercises for tenant {tenant_id}")
        return result

    except Exception as e:
        logger.error(f"List exercises failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(exercise_id: int, exercise_service: ExerciseService = Depends(get_exercise_service)):
    """Get exercise by ID"""
    try:
        result = await exercise_service.get_exercise(exercise_id)
        logger.info(f"Retrieved exercise {exercise_id}")
        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Get exercise failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exercises/{exercise_id}/start")
async def start_exercise(exercise_id: int, exercise_service: ExerciseService = Depends(get_exercise_service)):
    """Start exercise"""
    try:
        result = await exercise_service.start_exercise(exercise_id)
        logger.info(f"Exercise started: {exercise_id}")
        return result

    except ValueError as e:
        # ValueError can be "not found" or validation error - check message
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Start exercise failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exercises/{exercise_id}/complete")
async def complete_exercise(exercise_id: int, exercise_service: ExerciseService = Depends(get_exercise_service)):
    """Complete exercise (transition in_progress → completed)"""
    try:
        result = await exercise_service.complete_exercise(exercise_id)
        logger.info(f"Exercise completed: {exercise_id}")
        return result

    except ValueError as e:
        # ValueError can be "not found" or validation error - check message
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Complete exercise failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exercises/{exercise_id}/observations", status_code=201)
async def add_observation(exercise_id: int, observation: ObservationCreate, exercise_service: ExerciseService = Depends(get_exercise_service)):
    """Add observation to exercise"""
    try:
        observation_data = {
            "tenant_id": observation.tenant_id,
            "observation_type": observation.observation_type,
            "severity": observation.severity,
            "title": observation.title,
            "description": observation.description,
            "evidence": observation.evidence,
            "timestamp": observation.timestamp,
            "process_area": observation.process_area,
            "recommendation": observation.recommendation,
        }

        result = await exercise_service.add_observation(exercise_id, observation_data)
        logger.info(f"Observation added to exercise {exercise_id}")
        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Add observation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/exercises/{exercise_id}/report")
async def get_exercise_report(exercise_id: int, exercise_service: ExerciseService = Depends(get_exercise_service)):
    """Generate exercise report"""
    try:
        result = await exercise_service.generate_report(exercise_id)
        logger.info(f"Generated report for exercise {exercise_id}")
        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Generate report failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SCENARIO ENDPOINTS ====================

@router.post("/scenarios", status_code=201)
async def create_scenario(scenario: ScenarioCreate, scenario_service: ScenarioService = Depends(get_scenario_service)):
    """Create exercise scenario using service layer"""
    try:
        scenario_data = {
            "tenant_id": scenario.tenant_id,
            "scenario_code": scenario.scenario_code,
            "scenario_name": scenario.scenario_name,
            "description": scenario.description,
            "scenario_type": scenario.scenario_type,
            "category": scenario.category,
            "complexity_level": scenario.complexity_level,
            "full_scenario": scenario.full_scenario,
            "injects": scenario.injects,
            "recommended_exercise_type": scenario.recommended_exercise_type,
            "estimated_duration_hours": scenario.estimated_duration_hours,
        }

        db_scenario = await scenario_service.create_scenario(scenario_data)
        logger.info(f"Scenario created: {db_scenario.id} - {db_scenario.scenario_name}")
        return db_scenario

    except ValueError as e:
        logger.error(f"Scenario creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Scenario creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scenarios")
async def list_scenarios(
    tenant_id: str,
    scenario_type: Optional[str] = None,
    category: Optional[str] = None,
    scenario_service: ScenarioService = Depends(get_scenario_service)
):
    """List exercise scenarios using service layer"""
    try:
        scenarios = await scenario_service.list_scenarios(tenant_id, scenario_type, category)
        logger.info(f"Listed {len(scenarios)} scenarios for tenant {tenant_id}")
        return scenarios

    except Exception as e:
        logger.error(f"List scenarios failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== KPI ENDPOINTS ====================

@router.post("/kpis", response_model=KPIResponse, status_code=201)
async def create_kpi(kpi: KPICreate, kpi_service: KPIService = Depends(get_kpi_service)):
    """Create new KPI using service layer"""
    try:
        kpi_data = {
            "tenant_id": kpi.tenant_id,
            "kpi_code": kpi.kpi_code,
            "kpi_name": kpi.kpi_name,
            "category_id": kpi.category_id,
            "description": kpi.description,
            "objective": kpi.objective,
            "measurement_unit": kpi.measurement_unit,
            "calculation_method": kpi.calculation_method,
            "data_source": kpi.data_source,
            "target_value": kpi.target_value,
            "warning_threshold": kpi.warning_threshold,
            "critical_threshold": kpi.critical_threshold,
            "performance_direction": kpi.performance_direction,
            "measurement_frequency": kpi.measurement_frequency,
            "owner_id": kpi.owner_id,
            "owner_name": kpi.owner_name,
            "iso_clause": kpi.iso_clause,
        }

        db_kpi = await kpi_service.create_kpi(kpi_data)
        logger.info(f"KPI created: {db_kpi.id} - {db_kpi.kpi_name}")
        return db_kpi

    except ValueError as e:
        logger.error(f"KPI creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"KPI creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis", response_model=List[KPIResponse])
async def list_kpis(
    tenant_id: str,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    kpi_service: KPIService = Depends(get_kpi_service)
):
    """List KPIs with filters using service layer"""
    try:
        kpis = await kpi_service.list_kpis(tenant_id, category_id, status)
        logger.info(f"Retrieved {len(kpis)} KPIs for tenant {tenant_id}")
        return kpis
    except Exception as e:
        logger.error(f"List KPIs failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis/{kpi_id}", response_model=KPIResponse)
async def get_kpi(kpi_id: int, kpi_service: KPIService = Depends(get_kpi_service)):
    """Get KPI by ID using service layer"""
    try:
        kpi = await kpi_service.get_kpi(kpi_id)
        if not kpi:
            raise HTTPException(status_code=404, detail="KPI not found")

        logger.info(f"Retrieved KPI {kpi_id}")
        return kpi
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get KPI failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/kpis/{kpi_id}")
async def update_kpi(
    kpi_id: int,
    updates: KPIUpdate,
    kpi_service: KPIService = Depends(get_kpi_service)
):
    """Update KPI using service layer"""
    try:
        update_dict = updates.dict(exclude_unset=True)
        kpi = await kpi_service.update_kpi(kpi_id, update_dict)
        logger.info(f"KPI updated: {kpi_id}")
        return kpi
    except ValueError as e:
        logger.error(f"Update KPI failed: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Update KPI failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kpis/{kpi_id}/measure", status_code=201)
async def record_measurement(
    kpi_id: int,
    measurement: MeasurementCreate,
    kpi_service: KPIService = Depends(get_kpi_service)
):
    """Record KPI measurement using service layer"""
    try:
        db_measurement = await kpi_service.record_measurement(
            kpi_id=kpi_id,
            value=measurement.value,
            measured_by=measurement.collected_by,
            measurement_date=measurement.measurement_date,
            notes=measurement.notes,
            data_quality=measurement.data_quality,
            collection_method=measurement.collection_method
        )

        logger.info(f"Measurement recorded for KPI {kpi_id}: {measurement.value}")
        return db_measurement

    except ValueError as e:
        logger.error(f"Record measurement failed: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Record measurement failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis/{kpi_id}/trend")
async def get_kpi_trend(
    kpi_id: int,
    days: int = 90,
    kpi_service: KPIService = Depends(get_kpi_service)
):
    """Get KPI trend analysis using service layer"""
    try:
        trend_data = await kpi_service.get_kpi_trend(kpi_id=kpi_id, period_days=days)
        logger.info(f"Retrieved trend for KPI {kpi_id} ({days} days)")
        return trend_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Get trend failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpis/dashboard")
async def get_kpi_dashboard(
    tenant_id: str,
    kpi_service: KPIService = Depends(get_kpi_service)
):
    """Get KPI dashboard summary using service layer"""
    try:
        dashboard_data = await kpi_service.get_dashboard(tenant_id)
        logger.info(f"Retrieved KPI dashboard for tenant {tenant_id}")
        return dashboard_data
    except Exception as e:
        logger.error(f"KPI dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kpi/collect-now")
async def trigger_kpi_collection(
    tenant_id: str,
    kpi_service: KPIService = Depends(get_kpi_service)
):
    """Trigger on-demand KPI collection for tenant using service layer"""
    try:
        result = await kpi_service.trigger_collection(tenant_id)
        logger.info(f"KPI collection triggered for tenant {tenant_id}")
        return result
    except Exception as e:
        logger.error(f"Failed to trigger KPI collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kpi/alerts")
async def get_active_kpi_alerts(
    tenant_id: str,
    severity: Optional[str] = None,
    kpi_service: KPIService = Depends(get_kpi_service)
):
    """Get active KPI alerts using service layer"""
    try:
        alerts_data = await kpi_service.get_active_alerts(tenant_id, severity)
        logger.info(f"Retrieved {alerts_data['total_alerts']} active alerts for tenant {tenant_id}")
        return alerts_data
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kpi/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    notes: Optional[str] = None,
    kpi_service: KPIService = Depends(get_kpi_service)
):
    """Acknowledge KPI alert using service layer"""
    try:
        # For now, use a default user_id. In production, this should come from authentication
        user_id = "system"
        alert = await kpi_service.acknowledge_alert(alert_id, user_id, notes)
        logger.info(f"Alert {alert_id} acknowledged by {user_id}")
        return {
            "message": "Alert acknowledged",
            "alert_id": alert.id,
            "status": alert.status,
            "acknowledged_by": alert.acknowledged_by,
            "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
        }
    except ValueError as e:
        logger.error(f"Failed to acknowledge alert: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to acknowledge alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== AUDIT ENDPOINTS ====================

@router.post("/audits", response_model=AuditResponse, status_code=201)
async def create_audit(audit: AuditCreate, audit_service: AuditService = Depends(get_audit_service)):
    """Create audit plan"""
    try:
        audit_data = audit.dict()
        result = await audit_service.create_audit(audit_data)
        logger.info(f"Audit created: {result.id} - {result.audit_name}")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Audit creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audits", response_model=List[AuditResponse])
async def list_audits(
    tenant_id: str,
    status: Optional[AuditStatus] = None,
    audit_type: Optional[AuditType] = None,
    audit_service: AuditService = Depends(get_audit_service)
):
    """List audits with filters"""
    try:
        result = await audit_service.list_audits(tenant_id, status, audit_type)
        logger.info(f"Listed {len(result)} audits for tenant {tenant_id}")
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"List audits failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audits/{audit_id}", response_model=AuditResponse)
async def get_audit(audit_id: int, audit_service: AuditService = Depends(get_audit_service)):
    """Get audit by ID"""
    try:
        result = await audit_service.get_audit(audit_id)
        if not result:
            raise HTTPException(status_code=404, detail="Audit not found")
        logger.info(f"Retrieved audit {audit_id}")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Get audit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audits/{audit_id}/findings", status_code=201)
async def add_finding(audit_id: int, finding: FindingCreate, audit_service: AuditService = Depends(get_audit_service)):
    """Add finding to audit"""
    try:
        finding_data = finding.dict()
        result = await audit_service.add_finding(audit_id, finding_data)
        logger.info(f"Finding added to audit {audit_id}: {result.finding_number}")
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Add finding failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audits/{audit_id}/report")
async def get_audit_report(audit_id: int, audit_service: AuditService = Depends(get_audit_service)):
    """Generate audit report"""
    try:
        result = await audit_service.generate_report(audit_id)
        logger.info(f"Generated report for audit {audit_id}")
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Generate audit report failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/audits/{audit_id}/close")
async def close_audit(audit_id: int, audit_service: AuditService = Depends(get_audit_service)):
    """Close audit"""
    try:
        result = await audit_service.close_audit(audit_id)
        logger.info(f"Audit closed: {audit_id}")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Close audit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CAPA ENDPOINTS ====================

@router.post("/capa", response_model=CAPAResponse, status_code=201)
async def create_capa(capa: CAPACreate, capa_service: CAPAService = Depends(get_capa_service)):
    """Create CAPA using service layer"""
    try:
        capa_data = {
            "tenant_id": capa.tenant_id,
            "capa_number": capa.capa_number,
            "capa_type": capa.capa_type,
            "source": capa.source,
            "source_reference_id": capa.source_reference_id,
            "source_reference_code": capa.source_reference_code,
            "title": capa.title,
            "problem_description": capa.problem_description,
            "root_cause_analysis": capa.root_cause_analysis,
            "action_plan": capa.action_plan,
            "assigned_to": capa.assigned_to,
            "assigned_to_name": capa.assigned_to_name,
            "priority": capa.priority,
            "due_date": capa.due_date,
        }

        db_capa = await capa_service.create_capa(capa_data)
        logger.info(f"CAPA created: {db_capa.id} - {db_capa.capa_number}")
        return db_capa

    except ValueError as e:
        logger.error(f"CAPA creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"CAPA creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capa", response_model=List[CAPAResponse])
async def list_capa(
    tenant_id: str,
    status: Optional[CAPAStatus] = None,
    source: Optional[CAPASource] = None,
    priority: Optional[str] = None,
    capa_service: CAPAService = Depends(get_capa_service)
):
    """List CAPAs with filters using service layer"""
    try:
        # Convert enums to strings if needed
        status_str = status.value if status else None
        source_str = source.value if source else None

        capas = await capa_service.list_capas(tenant_id, status_str, source_str, priority)
        logger.info(f"Listed {len(capas)} CAPAs for tenant {tenant_id}")
        return capas

    except Exception as e:
        logger.error(f"List CAPA failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capa/{capa_id}", response_model=CAPAResponse)
async def get_capa(capa_id: int, capa_service: CAPAService = Depends(get_capa_service)):
    """Get CAPA by ID using service layer"""
    try:
        capa = await capa_service.get_capa(capa_id)
        logger.info(f"Retrieved CAPA: {capa_id}")
        return capa

    except ValueError as e:
        logger.error(f"Get CAPA failed: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Get CAPA failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/capa/{capa_id}")
async def update_capa(
    capa_id: int,
    updates: CAPAUpdate,
    capa_service: CAPAService = Depends(get_capa_service)
):
    """Update CAPA using service layer"""
    try:
        update_data = updates.dict(exclude_unset=True)
        capa = await capa_service.update_capa(capa_id, update_data)
        logger.info(f"CAPA updated: {capa_id}")
        return capa

    except ValueError as e:
        logger.error(f"Update CAPA failed: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Update CAPA failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/capa/{capa_id}/verify")
async def verify_capa(capa_id: int, capa_service: CAPAService = Depends(get_capa_service)):
    """Verify CAPA effectiveness using service layer"""
    try:
        capa = await capa_service.verify_capa(capa_id)
        logger.info(f"CAPA verified: {capa_id}")
        return capa

    except ValueError as e:
        logger.error(f"Verify CAPA failed: {e}")
        # Check if it's a workflow validation error (400) or not found (404)
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Verify CAPA failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MANAGEMENT REVIEW ENDPOINTS ====================

@router.post("/management-reviews", response_model=ManagementReviewResponse, status_code=201)
async def create_management_review(review: ManagementReviewCreate, db: AsyncSession = Depends(get_db)):
    """Create management review"""
    try:
        db_review = ManagementReviewDB(
            tenant_id=review.tenant_id,
            review_code=review.review_code,
            review_name=review.review_name,
            review_type=review.review_type,
            review_date=review.review_date,
            review_period_from=review.review_period_from,
            review_period_to=review.review_period_to,
            chairperson=review.chairperson,
            chairperson_name=review.chairperson_name,
            attendees=review.attendees,
            action_items_count=0,
            action_items_completed=0
        )

        db.add(db_review)
        await db.commit()
        await db.refresh(db_review)

        logger.info(f"Management review created: {db_review.id} - {db_review.review_name}")
        return db_review

    except Exception as e:
        await db.rollback()
        logger.error(f"Management review creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/management-reviews", response_model=List[ManagementReviewResponse])
async def list_management_reviews(
    tenant_id: str,
    review_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List management reviews"""
    try:
        query = select(ManagementReviewDB).filter(ManagementReviewDB.tenant_id == tenant_id)

        if review_type:
            query = query.filter(ManagementReviewDB.review_type == review_type)

        result = await db.execute(query.order_by(ManagementReviewDB.review_date.desc()))
        reviews = result.scalars().all()

        return reviews

    except Exception as e:
        logger.error(f"List management reviews failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/management-reviews/{review_id}/prepare")
async def prepare_management_review(
    review_id: int,
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Auto-prepare Management Review by collecting data from all BCM modules (ISO 9.3)"""
    try:
        # Get review details
        result = await db.execute(select(ManagementReviewDB).filter(ManagementReviewDB.id == review_id))
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(status_code=404, detail="Management review not found")

        # Calculate review period
        period_from = review.review_period_from or (datetime.utcnow() - timedelta(days=180))
        period_to = review.review_period_to or datetime.utcnow()

        # Collect data
        preparation_package = {
            "review_id": review_id,
            "review_name": review.review_name,
            "preparation_date": datetime.utcnow().isoformat(),
            "review_period": {
                "from": period_from.isoformat(),
                "to": period_to.isoformat()
            },
            "inputs": {}
        }

        # INPUT 1: Previous Management Review Actions
        previous_reviews_result = await db.execute(
            select(ManagementReviewDB).filter(
                and_(
                    ManagementReviewDB.tenant_id == tenant_id,
                    ManagementReviewDB.id < review_id,
                    ManagementReviewDB.review_date < review.review_date
                )
            ).order_by(ManagementReviewDB.review_date.desc()).limit(1)
        )
        previous_review = previous_reviews_result.scalar_one_or_none()

        preparation_package["inputs"]["1_previous_actions"] = {
            "title": "Status of actions from previous reviews",
            "data": {
                "previous_review_id": previous_review.id if previous_review else None,
                "previous_review_date": previous_review.review_date.isoformat() if previous_review else None,
                "action_items_total": previous_review.action_items_count if previous_review else 0,
                "action_items_completed": previous_review.action_items_completed if previous_review else 0,
                "completion_rate": (previous_review.action_items_completed / previous_review.action_items_count * 100) if previous_review and previous_review.action_items_count > 0 else 0
            }
        }

        # INPUT 2: Get Exercise Results
        exercises_result = await db.execute(
            select(ExerciseDB).filter(
                and_(
                    ExerciseDB.tenant_id == tenant_id,
                    ExerciseDB.planned_date >= period_from,
                    ExerciseDB.planned_date <= period_to
                )
            )
        )
        exercises = exercises_result.scalars().all()

        preparation_package["inputs"]["2_exercise_results"] = {
            "title": "Results of exercises and tests",
            "data": {
                "total_exercises": len(exercises),
                "completed": len([e for e in exercises if e.status == ExerciseStatus.COMPLETED]),
                "success_rate": len([e for e in exercises if e.overall_success]) / len(exercises) * 100 if exercises else 0,
            }
        }

        # INPUT 3: KPIs and Monitoring Results
        kpi_result = await db.execute(
            select(KPIDB).filter(KPIDB.tenant_id == tenant_id)
        )
        kpis = kpi_result.scalars().all()

        preparation_package["inputs"]["3_monitoring_results"] = {
            "title": "Monitoring and measurement results",
            "data": {
                "total_kpis": len(kpis),
                "kpis_on_target": len([k for k in kpis if k.current_value and k.current_value >= k.target_value]),
                "kpis_below_target": len([k for k in kpis if k.current_value and k.current_value < k.target_value]),
            }
        }

        # INPUT 4: Audit Results
        audit_result = await db.execute(
            select(AuditPlanDB).filter(
                and_(
                    AuditPlanDB.tenant_id == tenant_id,
                    AuditPlanDB.planned_date >= period_from,
                    AuditPlanDB.planned_date <= period_to
                )
            )
        )
        audits = audit_result.scalars().all()

        preparation_package["inputs"]["4_audit_results"] = {
            "title": "Audit results",
            "data": {
                "audits_completed": len([a for a in audits if a.status == AuditStatus.CLOSED]),
                "total_findings": sum(a.findings_count for a in audits),
                "major_findings": sum(a.major_findings for a in audits),
                "minor_findings": sum(a.minor_findings for a in audits),
            }
        }

        # INPUT 5: CAPA
        capa_result = await db.execute(
            select(CAPADB).filter(
                and_(
                    CAPADB.tenant_id == tenant_id,
                    CAPADB.created_at >= period_from,
                    CAPADB.created_at <= period_to
                )
            )
        )
        capas = capa_result.scalars().all()

        preparation_package["inputs"]["5_nc_and_capa"] = {
            "title": "Nonconformities and corrective actions",
            "data": {
                "total_capas": len(capas),
                "capas_closed": len([c for c in capas if c.status == CAPAStatus.CLOSED]),
                "capas_overdue": len([c for c in capas if c.due_date and c.due_date < datetime.utcnow() and c.status != CAPAStatus.CLOSED]),
            }
        }

        # Generate Executive Summary
        total_issues = preparation_package["inputs"]["5_nc_and_capa"]["data"]["total_capas"]
        critical_issues = preparation_package["inputs"]["5_nc_and_capa"]["data"]["capas_overdue"]

        # Calculate health score (0-100)
        health_score = 100

        # Deduct for previous actions not completed
        if preparation_package["inputs"]["1_previous_actions"]["data"]["completion_rate"] < 100:
            health_score -= (100 - preparation_package["inputs"]["1_previous_actions"]["data"]["completion_rate"]) * 0.2

        # Deduct for KPIs below target
        kpi_health = preparation_package["inputs"]["3_monitoring_results"]["data"]
        if kpi_health["total_kpis"] > 0:
            kpi_on_target_pct = (kpi_health["kpis_on_target"] / kpi_health["total_kpis"]) * 100
            health_score -= (100 - kpi_on_target_pct) * 0.3

        # Deduct for critical issues
        health_score -= min(critical_issues * 5, 30)
        health_score = max(0, int(health_score))

        preparation_package["executive_summary"] = {
            "bcms_health_score": health_score,
            "overall_status": "excellent" if health_score >= 90 else "good" if health_score >= 75 else "needs_attention" if health_score >= 60 else "critical",
            "total_issues": total_issues,
            "critical_issues": critical_issues,
        }

        logger.info(f"Management review {review_id} preparation completed. Health score: {health_score}")

        return preparation_package

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Management review preparation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== REPORTING ENDPOINTS ====================

@router.get("/reports/performance-summary")
async def get_performance_summary(
    tenant_id: str,
    period_from: datetime,
    period_to: datetime,
    db: AsyncSession = Depends(get_db)
):
    """Generate performance summary report"""
    try:
        # Get exercise statistics
        exercises_result = await db.execute(
            select(ExerciseDB).filter(
                ExerciseDB.tenant_id == tenant_id,
                ExerciseDB.planned_date >= period_from,
                ExerciseDB.planned_date <= period_to
            )
        )
        exercises = exercises_result.scalars().all()

        # Get audit statistics
        audits_result = await db.execute(
            select(AuditPlanDB).filter(
                AuditPlanDB.tenant_id == tenant_id,
                AuditPlanDB.planned_date >= period_from,
                AuditPlanDB.planned_date <= period_to
            )
        )
        audits = audits_result.scalars().all()

        # Get CAPA statistics
        capa_result = await db.execute(
            select(CAPADB).filter(
                CAPADB.tenant_id == tenant_id,
                CAPADB.created_at >= period_from,
                CAPADB.created_at <= period_to
            )
        )
        capas = capa_result.scalars().all()

        report = {
            "period": {
                "from": period_from.isoformat(),
                "to": period_to.isoformat(),
            },
            "exercises": {
                "total": len(exercises),
                "completed": len([e for e in exercises if e.status == ExerciseStatus.COMPLETED]),
                "success_rate": len([e for e in exercises if e.overall_success]) / len(exercises) * 100 if exercises else 0,
            },
            "audits": {
                "total": len(audits),
                "completed": len([a for a in audits if a.status == AuditStatus.CLOSED]),
                "total_findings": sum(a.findings_count for a in audits),
                "major_findings": sum(a.major_findings for a in audits),
            },
            "capa": {
                "total": len(capas),
                "closed": len([c for c in capas if c.status == CAPAStatus.CLOSED]),
            },
        }

        return report

    except Exception as e:
        logger.error(f"Performance summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/compliance-status")
async def get_compliance_status(tenant_id: str, db: AsyncSession = Depends(get_db)):
    """Get ISO 22301 compliance status"""
    try:
        # Get active KPIs
        kpis_result = await db.execute(
            select(KPIDB).filter(KPIDB.tenant_id == tenant_id, KPIDB.status == 'active')
        )
        kpis = kpis_result.scalars().all()

        # Count by status
        kpi_status = {
            'excellent': len([k for k in kpis if k.current_status == PerformanceStatus.EXCELLENT]),
            'good': len([k for k in kpis if k.current_status == PerformanceStatus.GOOD]),
            'warning': len([k for k in kpis if k.current_status == PerformanceStatus.WARNING]),
            'critical': len([k for k in kpis if k.current_status == PerformanceStatus.CRITICAL]),
        }

        # Calculate overall compliance score
        total_score = kpi_status['excellent'] * 100 + kpi_status['good'] * 75 + kpi_status['warning'] * 50 + kpi_status['critical'] * 25
        max_score = len(kpis) * 100
        compliance_score = (total_score / max_score * 100) if max_score > 0 else 0

        return {
            "tenant_id": tenant_id,
            "compliance_score": round(compliance_score, 1),
            "kpi_status": kpi_status,
            "total_kpis": len(kpis),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Compliance status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HEALTH & STATUS ====================

@router.get("/status")
async def get_service_status():
    """Get service status"""
    return {
        "service": "validation",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
