"""
Main Digital Twin Engine

Orchestrates all digital twin operations:
- Organization management
- Data collection coordination
- Engine orchestration (simulations, metrics, predictions)
- Lifecycle management
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from core.models.base import (
    Organization,
    OrganizationCreate,
    OrganizationUpdate,
    SimulationParameters,
    SimulationResult,
    HealthScore,
    Prediction,
    TheoryOfChange,
    ImpactPassport,
    QualityScore,
)

from .simulation_engine import SimulationEngine
from .metrics_engine import MetricsEngine
from .prediction_engine import PredictionEngine
from .toc_engine import ToCEngine
from .impact_passport_engine import ImpactPassportEngine

logger = logging.getLogger(__name__)


# ============================================
# MAIN DIGITAL TWIN ENGINE
# ============================================

class DigitalTwinEngine:
    """
    Main Digital Twin Engine

    Orchestrates all digital twin operations and lifecycle management
    """

    def __init__(self):
        """Initialize all sub-engines"""
        logger.info("Initializing Digital Twin Engine...")

        # Initialize sub-engines
        self.simulation_engine = SimulationEngine()
        self.metrics_engine = MetricsEngine()
        self.prediction_engine = PredictionEngine()
        self.toc_engine = ToCEngine()
        self.impact_passport_engine = ImpactPassportEngine()

        logger.info("Digital Twin Engine initialized successfully")

    # ============================================
    # ORGANIZATION MANAGEMENT
    # ============================================

    async def create_twin(
        self,
        org_data: OrganizationCreate,
        auto_assess: bool = True
    ) -> Organization:
        """
        Create new digital twin

        Args:
            org_data: Organization creation data
            auto_assess: Automatically calculate initial assessments

        Returns:
            Created Organization digital twin
        """
        logger.info(f"Creating digital twin for: {org_data.name}")

        # Create organization
        organization = Organization(
            name=org_data.name,
            org_type=org_data.org_type,
            industry=org_data.industry,
            employee_count=org_data.employee_count,
            annual_revenue=org_data.annual_revenue,
            headquarters=org_data.headquarters,
            contacts=org_data.contacts,
            description=org_data.description,
            metadata=org_data.metadata,
        )

        # Add source information if provided
        if org_data.source and org_data.source_id:
            from core.models.base import DataSource
            organization.sources.append(DataSource(
                source_type=org_data.source,
                source_id=org_data.source_id,
            ))
            organization.source_ids[org_data.source.value] = org_data.source_id

        # Initial assessments
        if auto_assess:
            logger.info("Performing initial assessments...")

            # Calculate initial quality score
            quality_score = await self.metrics_engine.calculate_quality_score(organization)
            organization.quality_score = quality_score.overall

            # Calculate initial health score
            health_score = await self.metrics_engine.calculate_health_score(organization)
            organization.health_score = health_score.overall

            # Set initial maturity level based on data completeness
            organization.maturity_level = self._assess_initial_maturity(organization, quality_score)

            logger.info(
                f"Initial assessment: health={organization.health_score:.1f}, "
                f"quality={organization.quality_score:.1f}, "
                f"maturity={organization.maturity_level}"
            )

        logger.info(f"Digital twin created: {organization.twin_id}")

        return organization

    async def update_twin(
        self,
        organization: Organization,
        updates: OrganizationUpdate,
        reassess: bool = True
    ) -> Organization:
        """
        Update existing digital twin

        Args:
            organization: Existing organization
            updates: Update data
            reassess: Recalculate assessments after update

        Returns:
            Updated Organization
        """
        logger.info(f"Updating digital twin: {organization.twin_id}")

        # Apply updates
        update_data = updates.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(organization, field):
                setattr(organization, field, value)

        organization.updated_at = datetime.utcnow()

        # Reassess if requested
        if reassess:
            quality_score = await self.metrics_engine.calculate_quality_score(organization)
            organization.quality_score = quality_score.overall

            health_score = await self.metrics_engine.calculate_health_score(organization)
            organization.health_score = health_score.overall

        logger.info(f"Digital twin updated: {organization.twin_id}")

        return organization

    async def get_twin_snapshot(
        self,
        organization: Organization
    ) -> Dict[str, Any]:
        """
        Get complete snapshot of digital twin

        Args:
            organization: Organization digital twin

        Returns:
            Complete snapshot with all metrics
        """
        logger.info(f"Generating snapshot for: {organization.twin_id}")

        # Calculate all current metrics
        health_score = await self.metrics_engine.calculate_health_score(organization)
        quality_score = await self.metrics_engine.calculate_quality_score(organization)

        snapshot = {
            'twin_id': organization.twin_id,
            'organization': organization.model_dump(),
            'health_score': health_score.model_dump(),
            'quality_score': quality_score.model_dump(),
            'snapshot_time': datetime.utcnow().isoformat(),
            'data_sources': len(organization.sources),
            'maturity_level': organization.maturity_level,
        }

        return snapshot

    # ============================================
    # SIMULATION OPERATIONS
    # ============================================

    async def run_simulation(
        self,
        organization: Organization,
        params: SimulationParameters
    ) -> SimulationResult:
        """
        Run simulation scenario

        Args:
            organization: Organization digital twin
            params: Simulation parameters

        Returns:
            SimulationResult
        """
        logger.info(
            f"Running {params.scenario.value} simulation for {organization.name}"
        )

        result = await self.simulation_engine.run_simulation(organization, params)

        logger.info(
            f"Simulation completed: impact={result.impact_score:.1f}, "
            f"recovery={result.recovery_time_days} days"
        )

        return result

    async def run_all_scenarios(
        self,
        organization: Organization,
        severity: float = 0.5,
        duration_months: int = 6
    ) -> List[SimulationResult]:
        """
        Run all available simulation scenarios

        Args:
            organization: Organization digital twin
            severity: Default severity (0-1)
            duration_months: Default duration

        Returns:
            List of simulation results
        """
        logger.info(f"Running all scenarios for {organization.name}")

        scenarios = self.simulation_engine.list_scenarios()
        results = []

        for scenario_type in scenarios:
            params = SimulationParameters(
                scenario=scenario_type,
                duration_months=duration_months,
                severity=severity
            )

            result = await self.simulation_engine.run_simulation(organization, params)
            results.append(result)

        logger.info(f"Completed {len(results)} simulations")

        return results

    # ============================================
    # METRICS & PREDICTIONS
    # ============================================

    async def calculate_health(
        self,
        organization: Organization
    ) -> HealthScore:
        """Calculate health score"""
        return await self.metrics_engine.calculate_health_score(organization)

    async def calculate_quality(
        self,
        organization: Organization
    ) -> QualityScore:
        """Calculate data quality score"""
        return await self.metrics_engine.calculate_quality_score(organization)

    async def predict_financial_trend(
        self,
        organization: Organization,
        timeframe_months: int = 12
    ) -> Prediction:
        """Predict financial trend"""
        # Get historical data (placeholder - would come from storage)
        time_series = []

        return await self.prediction_engine.predict_financial_trend(
            organization,
            time_series,
            timeframe_months
        )

    async def predict_risk(
        self,
        organization: Organization,
        timeframe_months: int = 12
    ) -> Prediction:
        """Predict risk score"""
        time_series = []  # Would fetch from storage

        return await self.prediction_engine.predict_risk(
            organization,
            time_series,
            timeframe_months
        )

    async def predict_growth(
        self,
        organization: Organization,
        timeframe_months: int = 12
    ) -> Prediction:
        """Predict organizational growth"""
        time_series = []  # Would fetch from storage

        return await self.prediction_engine.predict_growth(
            organization,
            time_series,
            timeframe_months
        )

    async def generate_all_predictions(
        self,
        organization: Organization,
        timeframe_months: int = 12
    ) -> Dict[str, Prediction]:
        """
        Generate all available predictions

        Args:
            organization: Organization digital twin
            timeframe_months: Prediction timeframe

        Returns:
            Dictionary of predictions by type
        """
        logger.info(f"Generating predictions for {organization.name}")

        time_series = []  # Would fetch from storage

        predictions = {
            'financial': await self.prediction_engine.predict_financial_trend(
                organization, time_series, timeframe_months
            ),
            'risk': await self.prediction_engine.predict_risk(
                organization, time_series, timeframe_months
            ),
            'growth': await self.prediction_engine.predict_growth(
                organization, time_series, timeframe_months
            ),
            'impact': await self.prediction_engine.predict_impact(
                organization, time_series, timeframe_months
            ),
        }

        logger.info(f"Generated {len(predictions)} predictions")

        return predictions

    # ============================================
    # THEORY OF CHANGE & IMPACT
    # ============================================

    async def generate_theory_of_change(
        self,
        organization: Organization,
        focus_area: Optional[str] = None
    ) -> TheoryOfChange:
        """Generate Theory of Change"""
        return await self.toc_engine.generate_toc(organization, focus_area)

    async def generate_impact_passport(
        self,
        organization: Organization,
        validity_months: int = 12
    ) -> ImpactPassport:
        """Generate Impact Passport"""
        # Get supporting data
        health_score = await self.metrics_engine.calculate_health_score(organization)
        toc = await self.toc_engine.generate_toc(organization)

        return await self.impact_passport_engine.generate_passport(
            organization,
            health_score,
            toc,
            validity_months
        )

    async def verify_impact_passport(
        self,
        passport: ImpactPassport,
        organization: Organization
    ) -> Dict[str, Any]:
        """Verify Impact Passport"""
        return await self.impact_passport_engine.verify_passport(passport, organization)

    # ============================================
    # COMPREHENSIVE ANALYSIS
    # ============================================

    async def perform_full_analysis(
        self,
        organization: Organization,
        include_simulations: bool = True,
        include_predictions: bool = True,
        include_toc: bool = True,
        include_passport: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of digital twin

        Args:
            organization: Organization digital twin
            include_simulations: Run all simulation scenarios
            include_predictions: Generate predictions
            include_toc: Generate Theory of Change
            include_passport: Generate Impact Passport

        Returns:
            Complete analysis results
        """
        logger.info(f"Performing full analysis for {organization.name}")

        analysis = {
            'twin_id': organization.twin_id,
            'organization_name': organization.name,
            'analysis_timestamp': datetime.utcnow().isoformat(),
        }

        # Core metrics (always included)
        logger.info("Calculating core metrics...")
        analysis['health_score'] = (
            await self.metrics_engine.calculate_health_score(organization)
        ).model_dump()

        analysis['quality_score'] = (
            await self.metrics_engine.calculate_quality_score(organization)
        ).model_dump()

        # Simulations
        if include_simulations:
            logger.info("Running simulations...")
            simulations = await self.run_all_scenarios(organization)
            analysis['simulations'] = [s.model_dump() for s in simulations]

            # Calculate average impact
            avg_impact = sum(s.impact_score for s in simulations if s.impact_score) / len(simulations)
            analysis['average_impact_score'] = round(avg_impact, 2)

        # Predictions
        if include_predictions:
            logger.info("Generating predictions...")
            predictions = await self.generate_all_predictions(organization)
            analysis['predictions'] = {
                k: v.model_dump() for k, v in predictions.items()
            }

        # Theory of Change
        if include_toc:
            logger.info("Generating Theory of Change...")
            toc = await self.generate_theory_of_change(organization)
            analysis['theory_of_change'] = toc.model_dump()

        # Impact Passport
        if include_passport:
            logger.info("Generating Impact Passport...")
            passport = await self.generate_impact_passport(organization)
            analysis['impact_passport'] = passport.model_dump()

        logger.info(f"Full analysis completed for {organization.twin_id}")

        return analysis

    # ============================================
    # UTILITY METHODS
    # ============================================

    def _assess_initial_maturity(
        self,
        organization: Organization,
        quality_score: QualityScore
    ) -> int:
        """Assess initial maturity level based on data completeness"""
        completeness = quality_score.dimensions.get('completeness', 0)

        if completeness >= 90:
            return 5
        elif completeness >= 75:
            return 4
        elif completeness >= 60:
            return 3
        elif completeness >= 40:
            return 2
        else:
            return 1

    async def get_engine_status(self) -> Dict[str, Any]:
        """Get status of all engines"""
        return {
            'main_engine': 'operational',
            'sub_engines': {
                'simulation': {
                    'status': 'operational',
                    'scenarios': len(self.simulation_engine.scenarios)
                },
                'metrics': {'status': 'operational'},
                'prediction': {'status': 'operational'},
                'toc': {'status': 'operational'},
                'impact_passport': {'status': 'operational'},
            },
            'timestamp': datetime.utcnow().isoformat()
        }

    def list_available_scenarios(self) -> List[str]:
        """List available simulation scenarios"""
        return [s.value for s in self.simulation_engine.list_scenarios()]

    def get_scenario_info(self, scenario_name: str) -> Dict[str, Any]:
        """Get information about specific scenario"""
        from core.models.base import SimulationScenarioType

        try:
            scenario_type = SimulationScenarioType(scenario_name)
            return self.simulation_engine.get_scenario_info(scenario_type)
        except ValueError:
            return {'error': f'Unknown scenario: {scenario_name}'}
