"""
Validation Service Repository Layer
Data access layer for all validation entities

This layer abstracts database operations and provides a clean interface for services.
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import (
    Exercise as ExerciseDB,
    ExerciseScenario as ExerciseScenarioDB,
    ExerciseObservation as ExerciseObservationDB,
    ExerciseAction as ExerciseActionDB,
    KPI as KPIDB,
    KPICategory as KPICategoryDB,
    KPIMeasurement as KPIMeasurementDB,
    KPIDashboard as KPIDashboardDB,
    KPIAlert as KPIAlertDB,
    AuditPlan as AuditPlanDB,
    AuditFinding as AuditFindingDB,
    CAPA as CAPADB,
    ManagementReview as ManagementReviewDB,
)


class ValidationRepository:
    """Repository for all validation entities"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== EXERCISE REPOSITORY ====================

    async def create_exercise(self, exercise_data: Dict) -> ExerciseDB:
        """Create a new exercise"""
        db_exercise = ExerciseDB(**exercise_data)
        self.db.add(db_exercise)
        await self.db.commit()
        await self.db.refresh(db_exercise)
        return db_exercise

    async def get_exercise(self, exercise_id: int) -> Optional[ExerciseDB]:
        """Get exercise by ID"""
        result = await self.db.execute(
            select(ExerciseDB).filter(ExerciseDB.id == exercise_id)
        )
        return result.scalar_one_or_none()

    async def get_exercise_by_code(self, exercise_code: str) -> Optional[ExerciseDB]:
        """Get exercise by code"""
        result = await self.db.execute(
            select(ExerciseDB).filter(ExerciseDB.exercise_code == exercise_code)
        )
        return result.scalar_one_or_none()

    async def list_exercises(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        exercise_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ExerciseDB]:
        """List exercises with filters"""
        query = select(ExerciseDB).filter(ExerciseDB.tenant_id == tenant_id)

        if status:
            query = query.filter(ExerciseDB.status == status)
        if exercise_type:
            query = query.filter(ExerciseDB.exercise_type == exercise_type)

        query = query.order_by(ExerciseDB.planned_date.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_exercise(self, exercise_id: int, updates: Dict) -> Optional[ExerciseDB]:
        """Update exercise"""
        exercise = await self.get_exercise(exercise_id)
        if not exercise:
            return None

        for field, value in updates.items():
            setattr(exercise, field, value)

        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

    async def delete_exercise(self, exercise_id: int) -> bool:
        """Delete exercise"""
        exercise = await self.get_exercise(exercise_id)
        if not exercise:
            return False

        await self.db.delete(exercise)
        await self.db.commit()
        return True

    # ==================== EXERCISE SCENARIO REPOSITORY ====================

    async def create_scenario(self, scenario_data: Dict) -> ExerciseScenarioDB:
        """Create exercise scenario"""
        db_scenario = ExerciseScenarioDB(**scenario_data)
        self.db.add(db_scenario)
        await self.db.commit()
        await self.db.refresh(db_scenario)
        return db_scenario

    async def get_scenario(self, scenario_id: int) -> Optional[ExerciseScenarioDB]:
        """Get scenario by ID"""
        result = await self.db.execute(
            select(ExerciseScenarioDB).filter(ExerciseScenarioDB.id == scenario_id)
        )
        return result.scalar_one_or_none()

    async def list_scenarios(
        self,
        tenant_id: str,
        scenario_type: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[ExerciseScenarioDB]:
        """List exercise scenarios"""
        query = select(ExerciseScenarioDB).filter(
            ExerciseScenarioDB.tenant_id == tenant_id,
            ExerciseScenarioDB.is_active == True
        )

        if scenario_type:
            query = query.filter(ExerciseScenarioDB.scenario_type == scenario_type)
        if category:
            query = query.filter(ExerciseScenarioDB.category == category)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ==================== EXERCISE OBSERVATION REPOSITORY ====================

    async def create_observation(self, observation_data: Dict) -> ExerciseObservationDB:
        """Create exercise observation"""
        db_observation = ExerciseObservationDB(**observation_data)
        self.db.add(db_observation)
        await self.db.commit()
        await self.db.refresh(db_observation)
        return db_observation

    async def list_observations_for_exercise(self, exercise_id: int) -> List[ExerciseObservationDB]:
        """List observations for an exercise"""
        result = await self.db.execute(
            select(ExerciseObservationDB).filter(
                ExerciseObservationDB.exercise_id == exercise_id
            )
        )
        return list(result.scalars().all())

    async def list_actions_for_exercise(self, exercise_id: int) -> List[ExerciseActionDB]:
        """List actions for an exercise"""
        result = await self.db.execute(
            select(ExerciseActionDB).filter(
                ExerciseActionDB.exercise_id == exercise_id
            )
        )
        return list(result.scalars().all())

    # ==================== KPI REPOSITORY ====================

    async def create_kpi(self, kpi_data: Dict) -> KPIDB:
        """Create KPI"""
        db_kpi = KPIDB(**kpi_data)
        self.db.add(db_kpi)
        await self.db.commit()
        await self.db.refresh(db_kpi)
        return db_kpi

    async def get_kpi(self, kpi_id: int) -> Optional[KPIDB]:
        """Get KPI by ID"""
        result = await self.db.execute(
            select(KPIDB).filter(KPIDB.id == kpi_id)
        )
        return result.scalar_one_or_none()

    async def get_kpi_by_code(self, kpi_code: str) -> Optional[KPIDB]:
        """Get KPI by code"""
        result = await self.db.execute(
            select(KPIDB).filter(KPIDB.kpi_code == kpi_code)
        )
        return result.scalar_one_or_none()

    async def list_kpis(
        self,
        tenant_id: str,
        category_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[KPIDB]:
        """List KPIs with filters"""
        query = select(KPIDB).filter(KPIDB.tenant_id == tenant_id)

        if category_id:
            query = query.filter(KPIDB.category_id == category_id)
        if status:
            query = query.filter(KPIDB.status == status)

        query = query.order_by(KPIDB.sequence, KPIDB.kpi_name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_kpi(self, kpi_id: int, updates: Dict) -> Optional[KPIDB]:
        """Update KPI"""
        kpi = await self.get_kpi(kpi_id)
        if not kpi:
            return None

        for field, value in updates.items():
            setattr(kpi, field, value)

        await self.db.commit()
        await self.db.refresh(kpi)
        return kpi

    # ==================== KPI MEASUREMENT REPOSITORY ====================

    async def create_kpi_measurement(self, measurement_data: Dict) -> KPIMeasurementDB:
        """Create KPI measurement"""
        db_measurement = KPIMeasurementDB(**measurement_data)
        self.db.add(db_measurement)
        await self.db.commit()
        await self.db.refresh(db_measurement)
        return db_measurement

    async def get_kpi_measurements(
        self,
        kpi_id: int,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[KPIMeasurementDB]:
        """Get KPI measurements"""
        query = select(KPIMeasurementDB).filter(KPIMeasurementDB.kpi_id == kpi_id)

        if from_date:
            query = query.filter(KPIMeasurementDB.measurement_date >= from_date)
        if to_date:
            query = query.filter(KPIMeasurementDB.measurement_date <= to_date)

        query = query.order_by(KPIMeasurementDB.measurement_date.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_latest_kpi_measurement(self, kpi_id: int) -> Optional[KPIMeasurementDB]:
        """Get latest KPI measurement"""
        result = await self.db.execute(
            select(KPIMeasurementDB)
            .filter(KPIMeasurementDB.kpi_id == kpi_id)
            .order_by(KPIMeasurementDB.measurement_date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    # ==================== AUDIT REPOSITORY ====================

    async def create_audit(self, audit_data: Dict) -> AuditPlanDB:
        """Create audit plan"""
        db_audit = AuditPlanDB(**audit_data)
        self.db.add(db_audit)
        await self.db.commit()
        await self.db.refresh(db_audit)
        return db_audit

    async def get_audit(self, audit_id: int) -> Optional[AuditPlanDB]:
        """Get audit by ID"""
        result = await self.db.execute(
            select(AuditPlanDB).filter(AuditPlanDB.id == audit_id)
        )
        return result.scalar_one_or_none()

    async def list_audits(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        audit_type: Optional[str] = None
    ) -> List[AuditPlanDB]:
        """List audits with filters"""
        query = select(AuditPlanDB).filter(AuditPlanDB.tenant_id == tenant_id)

        if status:
            query = query.filter(AuditPlanDB.status == status)
        if audit_type:
            query = query.filter(AuditPlanDB.audit_type == audit_type)

        query = query.order_by(AuditPlanDB.planned_date.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_audit(self, audit_id: int, updates: Dict) -> Optional[AuditPlanDB]:
        """Update audit"""
        audit = await self.get_audit(audit_id)
        if not audit:
            return None

        for field, value in updates.items():
            setattr(audit, field, value)

        await self.db.commit()
        await self.db.refresh(audit)
        return audit

    # ==================== AUDIT FINDING REPOSITORY ====================

    async def create_audit_finding(self, finding_data: Dict) -> AuditFindingDB:
        """Create audit finding"""
        db_finding = AuditFindingDB(**finding_data)
        self.db.add(db_finding)
        await self.db.commit()
        await self.db.refresh(db_finding)
        return db_finding

    async def list_audit_findings(self, audit_id: int) -> List[AuditFindingDB]:
        """List findings for an audit"""
        result = await self.db.execute(
            select(AuditFindingDB).filter(AuditFindingDB.audit_id == audit_id)
        )
        return list(result.scalars().all())

    # ==================== CAPA REPOSITORY ====================

    async def create_capa(self, capa_data: Dict) -> CAPADB:
        """Create CAPA"""
        db_capa = CAPADB(**capa_data)
        self.db.add(db_capa)
        await self.db.commit()
        await self.db.refresh(db_capa)
        return db_capa

    async def get_capa(self, capa_id: int) -> Optional[CAPADB]:
        """Get CAPA by ID"""
        result = await self.db.execute(
            select(CAPADB).filter(CAPADB.id == capa_id)
        )
        return result.scalar_one_or_none()

    async def list_capas(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        source: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[CAPADB]:
        """List CAPAs with filters"""
        query = select(CAPADB).filter(CAPADB.tenant_id == tenant_id)

        if status:
            query = query.filter(CAPADB.status == status)
        if source:
            query = query.filter(CAPADB.source == source)
        if priority:
            query = query.filter(CAPADB.priority == priority)

        query = query.order_by(CAPADB.due_date)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_capa(self, capa_id: int, updates: Dict) -> Optional[CAPADB]:
        """Update CAPA"""
        capa = await self.get_capa(capa_id)
        if not capa:
            return None

        for field, value in updates.items():
            setattr(capa, field, value)

        await self.db.commit()
        await self.db.refresh(capa)
        return capa

    # ==================== MANAGEMENT REVIEW REPOSITORY ====================

    async def create_management_review(self, review_data: Dict) -> ManagementReviewDB:
        """Create management review"""
        db_review = ManagementReviewDB(**review_data)
        self.db.add(db_review)
        await self.db.commit()
        await self.db.refresh(db_review)
        return db_review

    async def get_management_review(self, review_id: int) -> Optional[ManagementReviewDB]:
        """Get management review by ID"""
        result = await self.db.execute(
            select(ManagementReviewDB).filter(ManagementReviewDB.id == review_id)
        )
        return result.scalar_one_or_none()

    async def list_management_reviews(
        self,
        tenant_id: str,
        review_type: Optional[str] = None
    ) -> List[ManagementReviewDB]:
        """List management reviews"""
        query = select(ManagementReviewDB).filter(
            ManagementReviewDB.tenant_id == tenant_id
        )

        if review_type:
            query = query.filter(ManagementReviewDB.review_type == review_type)

        query = query.order_by(ManagementReviewDB.review_date.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ==================== KPI ALERT REPOSITORY ====================

    async def create_kpi_alert(self, alert_data: Dict) -> KPIAlertDB:
        """Create KPI alert"""
        db_alert = KPIAlertDB(**alert_data)
        self.db.add(db_alert)
        await self.db.commit()
        await self.db.refresh(db_alert)
        return db_alert

    async def list_active_alerts(
        self,
        tenant_id: str,
        severity: Optional[str] = None
    ) -> List[KPIAlertDB]:
        """List active KPI alerts"""
        query = select(KPIAlertDB).filter(
            KPIAlertDB.tenant_id == tenant_id,
            KPIAlertDB.status == "active"
        )

        if severity:
            query = query.filter(KPIAlertDB.severity == severity)

        query = query.order_by(KPIAlertDB.triggered_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_alert(self, alert_id: int, updates: Dict) -> Optional[KPIAlertDB]:
        """Update alert"""
        result = await self.db.execute(
            select(KPIAlertDB).filter(KPIAlertDB.id == alert_id)
        )
        alert = result.scalar_one_or_none()

        if not alert:
            return None

        for field, value in updates.items():
            setattr(alert, field, value)

        await self.db.commit()
        await self.db.refresh(alert)
        return alert
