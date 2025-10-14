"""
Risk Repository - Data Access Layer
"""

from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta

from models.database import (
    RiskDB,
    FAIRAnalysisDB,
    MonteCarloSimulationDB,
    RiskTreatmentPlanDB,
    AIRiskAdvisorDB
)
from models.domain import Risk, FAIRAnalysis, MonteCarloSimulation, RiskTreatmentPlan


class RiskRepository:
    """Repository for Risk data access"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================================
    # Risk CRUD
    # =========================================================================

    async def create(self, risk: Risk) -> RiskDB:
        """Create new risk assessment"""
        db_risk = RiskDB(
            organization_id=risk.organization_id,
            risk_title=risk.risk_title,
            risk_code=risk.risk_code,
            risk_category=risk.risk_category.value if risk.risk_category else None,
            description=risk.description,
            threat_source=risk.threat_source,
            vulnerabilities=risk.vulnerabilities,
            likelihood=risk.likelihood.value if risk.likelihood else None,
            impact=risk.impact.value if risk.impact else None,
            inherent_risk_score=risk.likelihood.value * risk.impact.value if (risk.likelihood and risk.impact) else 0,
            treatment_strategy=risk.treatment_strategy.value if risk.treatment_strategy else None,
            residual_likelihood=risk.residual_likelihood.value if risk.residual_likelihood else None,
            residual_impact=risk.residual_impact.value if risk.residual_impact else None,
            residual_risk_score=(
                risk.residual_likelihood.value * risk.residual_impact.value
                if (risk.residual_likelihood and risk.residual_impact) else None
            ),
            risk_owner_id=risk.risk_owner_id,
            related_processes=risk.related_processes,
            related_assets=risk.related_assets,
            status=risk.status.value if risk.status else 'identified',
            last_reviewed_at=risk.last_reviewed_at,
            next_review_date=risk.next_review_date,
        )

        self.db.add(db_risk)
        await self.db.commit()
        await self.db.refresh(db_risk)
        return db_risk

    async def get_by_id(self, risk_id: UUID) -> Optional[RiskDB]:
        """Get risk by ID"""
        stmt = select(RiskDB).where(
            and_(RiskDB.id == risk_id, RiskDB.is_active == True)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_organization(
        self,
        organization_id: UUID,
        category: Optional[str] = None,
        status: Optional[str] = None,
        min_score: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[RiskDB]:
        """List risks for organization with filters"""
        stmt = select(RiskDB).where(
            and_(
                RiskDB.organization_id == organization_id,
                RiskDB.is_active == True
            )
        )

        if category:
            stmt = stmt.where(RiskDB.risk_category == category)

        if status:
            stmt = stmt.where(RiskDB.status == status)

        if min_score:
            stmt = stmt.where(RiskDB.inherent_risk_score >= min_score)

        stmt = stmt.order_by(desc(RiskDB.inherent_risk_score)).offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, risk_id: UUID, risk_update: Risk) -> Optional[RiskDB]:
        """Update risk"""
        db_risk = await self.get_by_id(risk_id)
        if not db_risk:
            return None

        # Update fields
        db_risk.risk_title = risk_update.risk_title
        db_risk.risk_code = risk_update.risk_code
        db_risk.risk_category = risk_update.risk_category.value if risk_update.risk_category else None
        db_risk.description = risk_update.description
        db_risk.threat_source = risk_update.threat_source
        db_risk.vulnerabilities = risk_update.vulnerabilities
        db_risk.likelihood = risk_update.likelihood.value if risk_update.likelihood else None
        db_risk.impact = risk_update.impact.value if risk_update.impact else None
        db_risk.inherent_risk_score = (
            risk_update.likelihood.value * risk_update.impact.value
            if (risk_update.likelihood and risk_update.impact) else 0
        )
        db_risk.treatment_strategy = risk_update.treatment_strategy.value if risk_update.treatment_strategy else None
        db_risk.residual_likelihood = risk_update.residual_likelihood.value if risk_update.residual_likelihood else None
        db_risk.residual_impact = risk_update.residual_impact.value if risk_update.residual_impact else None
        db_risk.residual_risk_score = (
            risk_update.residual_likelihood.value * risk_update.residual_impact.value
            if (risk_update.residual_likelihood and risk_update.residual_impact) else None
        )
        db_risk.risk_owner_id = risk_update.risk_owner_id
        db_risk.related_processes = risk_update.related_processes
        db_risk.related_assets = risk_update.related_assets
        db_risk.status = risk_update.status.value if risk_update.status else db_risk.status
        db_risk.last_reviewed_at = risk_update.last_reviewed_at
        db_risk.next_review_date = risk_update.next_review_date

        await self.db.commit()
        await self.db.refresh(db_risk)
        return db_risk

    async def delete(self, risk_id: UUID) -> bool:
        """Soft delete risk"""
        db_risk = await self.get_by_id(risk_id)
        if not db_risk:
            return False

        db_risk.is_active = False
        await self.db.commit()
        return True

    # =========================================================================
    # FAIR Analysis
    # =========================================================================

    async def create_fair_analysis(self, analysis: FAIRAnalysis, organization_id: UUID) -> FAIRAnalysisDB:
        """Create FAIR analysis"""
        db_analysis = FAIRAnalysisDB(
            risk_id=analysis.risk_id,
            organization_id=organization_id,
            threat_event_frequency=int(analysis.threat_event_frequency),
            vulnerability_score=int(analysis.vulnerability_score * 100),
            loss_event_frequency=int(analysis.loss_event_frequency),
            primary_loss_min=int(analysis.primary_loss_min),
            primary_loss_max=int(analysis.primary_loss_max),
            primary_loss_most_likely=int(analysis.primary_loss_most_likely),
            secondary_loss_min=int(analysis.secondary_loss_min),
            secondary_loss_max=int(analysis.secondary_loss_max),
            annual_loss_expectancy=int(analysis.annual_loss_expectancy),
            risk_rating=analysis.risk_rating,
            confidence_interval_low=int(analysis.confidence_interval_low),
            confidence_interval_high=int(analysis.confidence_interval_high),
            analyzed_by=analysis.analyzed_by
        )

        self.db.add(db_analysis)
        await self.db.commit()
        await self.db.refresh(db_analysis)
        return db_analysis

    async def get_fair_analysis(self, risk_id: UUID) -> Optional[FAIRAnalysisDB]:
        """Get latest FAIR analysis for risk"""
        stmt = select(FAIRAnalysisDB).where(
            FAIRAnalysisDB.risk_id == risk_id
        ).order_by(desc(FAIRAnalysisDB.analyzed_at)).limit(1)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # =========================================================================
    # Monte Carlo Simulation
    # =========================================================================

    async def create_monte_carlo(self, simulation: MonteCarloSimulation, organization_id: UUID) -> MonteCarloSimulationDB:
        """Create Monte Carlo simulation"""
        db_sim = MonteCarloSimulationDB(
            risk_id=simulation.risk_id,
            organization_id=organization_id,
            iterations=simulation.iterations,
            factors=simulation.factors,
            mean_loss=int(simulation.mean_loss),
            median_loss=int(simulation.median_loss),
            percentile_95=int(simulation.percentile_95),
            percentile_99=int(simulation.percentile_99),
            distribution_data=simulation.distribution_data
        )

        self.db.add(db_sim)
        await self.db.commit()
        await self.db.refresh(db_sim)
        return db_sim

    async def get_monte_carlo(self, risk_id: UUID) -> Optional[MonteCarloSimulationDB]:
        """Get latest Monte Carlo simulation for risk"""
        stmt = select(MonteCarloSimulationDB).where(
            MonteCarloSimulationDB.risk_id == risk_id
        ).order_by(desc(MonteCarloSimulationDB.simulated_at)).limit(1)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # =========================================================================
    # Treatment Plans
    # =========================================================================

    async def create_treatment_plan(self, plan: RiskTreatmentPlan, organization_id: UUID) -> RiskTreatmentPlanDB:
        """Create treatment plan"""
        db_plan = RiskTreatmentPlanDB(
            risk_id=plan.risk_id,
            organization_id=organization_id,
            strategy=plan.strategy.value if plan.strategy else None,
            description=plan.description,
            actions=plan.actions,
            responsible_party=plan.responsible_party,
            start_date=plan.start_date,
            target_date=plan.target_date,
            completion_date=plan.completion_date,
            estimated_cost=int(plan.estimated_cost) if plan.estimated_cost else None,
            actual_cost=int(plan.actual_cost) if plan.actual_cost else None,
            expected_residual_likelihood=plan.expected_residual_likelihood.value if plan.expected_residual_likelihood else None,
            expected_residual_impact=plan.expected_residual_impact.value if plan.expected_residual_impact else None,
            status=plan.status
        )

        self.db.add(db_plan)
        await self.db.commit()
        await self.db.refresh(db_plan)
        return db_plan

    async def list_treatment_plans(self, risk_id: UUID) -> List[RiskTreatmentPlanDB]:
        """List all treatment plans for risk"""
        stmt = select(RiskTreatmentPlanDB).where(
            RiskTreatmentPlanDB.risk_id == risk_id
        ).order_by(desc(RiskTreatmentPlanDB.created_at))

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_treatment_plan(self, plan_id: UUID) -> Optional[RiskTreatmentPlanDB]:
        """Get treatment plan by ID"""
        stmt = select(RiskTreatmentPlanDB).where(RiskTreatmentPlanDB.id == plan_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_treatment_plan(self, plan_id: UUID, plan_update: RiskTreatmentPlan) -> Optional[RiskTreatmentPlanDB]:
        """Update treatment plan"""
        db_plan = await self.get_treatment_plan(plan_id)
        if not db_plan:
            return None

        db_plan.strategy = plan_update.strategy.value if plan_update.strategy else db_plan.strategy
        db_plan.description = plan_update.description
        db_plan.actions = plan_update.actions
        db_plan.responsible_party = plan_update.responsible_party
        db_plan.start_date = plan_update.start_date
        db_plan.target_date = plan_update.target_date
        db_plan.completion_date = plan_update.completion_date
        db_plan.estimated_cost = int(plan_update.estimated_cost) if plan_update.estimated_cost else db_plan.estimated_cost
        db_plan.actual_cost = int(plan_update.actual_cost) if plan_update.actual_cost else db_plan.actual_cost
        db_plan.expected_residual_likelihood = (
            plan_update.expected_residual_likelihood.value
            if plan_update.expected_residual_likelihood else db_plan.expected_residual_likelihood
        )
        db_plan.expected_residual_impact = (
            plan_update.expected_residual_impact.value
            if plan_update.expected_residual_impact else db_plan.expected_residual_impact
        )
        db_plan.status = plan_update.status

        await self.db.commit()
        await self.db.refresh(db_plan)
        return db_plan

    # =========================================================================
    # Analytics
    # =========================================================================

    async def get_risk_stats(self, organization_id: UUID) -> Dict[str, Any]:
        """Get risk statistics for organization"""
        stmt = select(RiskDB).where(
            and_(
                RiskDB.organization_id == organization_id,
                RiskDB.is_active == True
            )
        )

        result = await self.db.execute(stmt)
        risks = result.scalars().all()

        return {
            "total": len(risks),
            "critical": len([r for r in risks if r.inherent_risk_score >= 20]),
            "high": len([r for r in risks if 15 <= r.inherent_risk_score < 20]),
            "medium": len([r for r in risks if 8 <= r.inherent_risk_score < 15]),
            "low": len([r for r in risks if r.inherent_risk_score < 8]),
        }

    async def get_risks_by_category(self, organization_id: UUID) -> Dict[str, int]:
        """Get risk count by category"""
        stmt = select(
            RiskDB.risk_category,
            func.count(RiskDB.id).label('count')
        ).where(
            and_(
                RiskDB.organization_id == organization_id,
                RiskDB.is_active == True
            )
        ).group_by(RiskDB.risk_category)

        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}

    async def get_risks_by_status(self, organization_id: UUID) -> Dict[str, int]:
        """Get risk count by status"""
        stmt = select(
            RiskDB.status,
            func.count(RiskDB.id).label('count')
        ).where(
            and_(
                RiskDB.organization_id == organization_id,
                RiskDB.is_active == True
            )
        ).group_by(RiskDB.status)

        result = await self.db.execute(stmt)
        return {row[0]: row[1] for row in result.all()}

    async def get_top_risks(self, organization_id: UUID, limit: int = 10) -> List[RiskDB]:
        """Get top risks by score"""
        stmt = select(RiskDB).where(
            and_(
                RiskDB.organization_id == organization_id,
                RiskDB.is_active == True
            )
        ).order_by(desc(RiskDB.inherent_risk_score)).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_risk_history(self, organization_id: UUID, days: int = 90) -> List[Dict[str, Any]]:
        """
        Get risk history with date grouping for trend analysis

        Returns daily risk counts by severity and status over the specified period
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # Query risks created within the time period, grouped by date
        stmt = select(
            func.date_trunc('day', RiskDB.created_at).label('date'),
            func.count(RiskDB.id).label('total_count'),
            func.sum(
                func.case((RiskDB.inherent_risk_score >= 20, 1), else_=0)
            ).label('critical_count'),
            func.sum(
                func.case((and_(RiskDB.inherent_risk_score >= 15, RiskDB.inherent_risk_score < 20), 1), else_=0)
            ).label('high_count'),
            func.sum(
                func.case((and_(RiskDB.inherent_risk_score >= 8, RiskDB.inherent_risk_score < 15), 1), else_=0)
            ).label('medium_count'),
            func.sum(
                func.case((RiskDB.inherent_risk_score < 8, 1), else_=0)
            ).label('low_count'),
            func.avg(RiskDB.inherent_risk_score).label('avg_risk_score'),
            func.sum(
                func.case((RiskDB.status == 'identified', 1), else_=0)
            ).label('new_risks'),
            func.sum(
                func.case((RiskDB.status == 'closed', 1), else_=0)
            ).label('resolved_risks')
        ).where(
            and_(
                RiskDB.organization_id == organization_id,
                RiskDB.created_at >= start_date
            )
        ).group_by(
            func.date_trunc('day', RiskDB.created_at)
        ).order_by(
            func.date_trunc('day', RiskDB.created_at)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # Convert to list of dictionaries
        history = []
        for row in rows:
            history.append({
                'date': row.date.strftime('%Y-%m-%d') if row.date else None,
                'total_count': int(row.total_count or 0),
                'critical_count': int(row.critical_count or 0),
                'high_count': int(row.high_count or 0),
                'medium_count': int(row.medium_count or 0),
                'low_count': int(row.low_count or 0),
                'avg_risk_score': float(row.avg_risk_score or 0),
                'new_risks': int(row.new_risks or 0),
                'resolved_risks': int(row.resolved_risks or 0)
            })

        return history
