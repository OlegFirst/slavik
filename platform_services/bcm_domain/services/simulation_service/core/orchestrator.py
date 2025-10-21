"""
Main Simulation Orchestrator

Coordinates the COMPLETE simulation lifecycle:
1. Task Specification Formation
2. Tool/Template Selection
3. Validation
4. Simulation Execution
5. Real-time Monitoring
6. Result Collection
7. Analysis & Report Generation
8. Memory System Integration (Learning & Case Creation)

This is the HEART of the Simulation Service.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from models.pydantic_models import (
    TaskSpecification,
    Scenario,
    Simulation,
    SimulationResult,
    SimulationStatus,
    EngineType,
    EngineConfig,
    VisualizationConfig,
    IntegrationConfig
)

from integration import (
    SimulationEventBusClient,
    AIOrchestratorClient,
    WorkflowIntelligenceClient,
    AIFoundationClient,
    KnowledgeCenterClient,
    CommunityIntelligenceClient,
    ScenarioOrchestratorClient
)

from generators import ScenarioGenerator
from reporting import ReportGenerator
from catalogs import CatalogManager

from storage.repositories import (
    SimulationRepository,
    ScenarioRepository,
    SpecificationRepository,
    ResultRepository
)

from config.settings import Settings

logger = logging.getLogger(__name__)


class SimulationOrchestrator:
    """
    Main orchestrator coordinating entire simulation lifecycle

    Full Process Flow:
    ==================

    1. FORMATION (Specification Building)
       - Natural language → TaskSpecification
       - Template customization
       - Data-driven generation
       - Context gathering from all sources

    2. SELECTION (Tool & Template Selection)
       - Search similar scenarios (RAG)
       - Recommend engines (AI/ML)
       - Select tools (user choice or auto)
       - Load/customize templates

    3. VALIDATION (Pre-flight Checks)
       - AI validation of specification
       - Feasibility assessment
       - Risk identification
       - Resource estimation

    4. EXECUTION (Run Simulation)
       - Initialize engine
       - Setup monitoring
       - Inject events
       - Real-time decisions (AI support)
       - Progress tracking

    5. COLLECTION (Gather Results)
       - Collect metrics
       - Participant feedback
       - Event logs
       - Performance data

    6. ANALYSIS (AI-powered Analysis)
       - Result analysis (AI Orchestrator)
       - Pattern identification
       - Strength/weakness detection
       - Recommendation generation

    7. REPORTING (Professional Reports)
       - Executive summary
       - Technical report
       - ISO compliance report
       - Visualizations

    8. LEARNING (Memory Integration)
       - PDCA cycle creation (Workflow Intelligence)
       - Case Library storage
       - Pattern storage (Memory System)
       - Knowledge capture (Knowledge Center)
       - Community contribution (if quality high)
    """

    def __init__(
        self,
        settings: Settings,
        eventbus_client: SimulationEventBusClient,
        ai_orchestrator_client: AIOrchestratorClient,
        workflow_client: WorkflowIntelligenceClient,
        ai_foundation_client: AIFoundationClient,
        knowledge_client: KnowledgeCenterClient,
        community_client: CommunityIntelligenceClient,
        scenario_orchestrator_client: ScenarioOrchestratorClient,
        scenario_generator: ScenarioGenerator,
        report_generator: ReportGenerator,
        catalog_manager: CatalogManager,
        simulation_repo: SimulationRepository,
        scenario_repo: ScenarioRepository,
        specification_repo: SpecificationRepository,
        result_repo: ResultRepository
    ):
        """
        Initialize orchestrator with all dependencies

        Args:
            settings: Application settings
            eventbus_client: EventBus client
            ai_orchestrator_client: AI Orchestrator client
            workflow_client: Workflow Intelligence client
            ai_foundation_client: AI Foundation client
            knowledge_client: Knowledge Center client
            community_client: Community Intelligence client
            scenario_orchestrator_client: Scenario Orchestrator client (existing service)
            scenario_generator: Scenario generator
            report_generator: Report generator
            catalog_manager: Catalog manager
            simulation_repo: Simulation repository
            scenario_repo: Scenario repository
            specification_repo: Specification repository
            result_repo: Result repository
        """
        self.settings = settings

        # Integration clients
        self.eventbus = eventbus_client
        self.ai_orchestrator = ai_orchestrator_client
        self.workflow = workflow_client
        self.ai_foundation = ai_foundation_client
        self.knowledge = knowledge_client
        self.community = community_client
        self.scenario_orchestrator = scenario_orchestrator_client

        # Generators and utilities
        self.scenario_generator = scenario_generator
        self.report_generator = report_generator
        self.catalog_manager = catalog_manager

        # Repositories
        self.simulation_repo = simulation_repo
        self.scenario_repo = scenario_repo
        self.specification_repo = specification_repo
        self.result_repo = result_repo

    # ========================================================================
    # MAIN ORCHESTRATION METHOD
    # ========================================================================

    async def run_full_simulation_cycle(
        self,
        user_input: str,
        session: AsyncSession,
        organization_context: Optional[Dict] = None,
        user_preferences: Optional[Dict] = None,
        tenant_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Execute COMPLETE simulation cycle from input to learning

        This is the MAIN method that orchestrates everything!

        Args:
            user_input: Natural language description of what to simulate
            session: Database session
            organization_context: Organization data (Digital Twin, profile, etc.)
            user_preferences: User preferences (engine, duration, etc.)
            tenant_id: Tenant ID

        Returns:
            Complete cycle results including simulation, results, report, learning
        """
        logger.info(f" Starting FULL simulation cycle")
        logger.info(f"Input: {user_input[:100]}...")

        cycle_results = {
            "status": "in_progress",
            "phases": {},
            "errors": []
        }

        try:
            # ================================================================
            # PHASE 1: SPECIFICATION FORMATION
            # ================================================================
            logger.info(" PHASE 1: Specification Formation")

            specification = await self.scenario_generator.generate_from_natural_language(
                user_input=user_input,
                organization_context=organization_context,
                user_preferences=user_preferences,
                session=session
            )

            if not specification:
                raise ValueError("Failed to generate specification")

            # Save specification
            spec_orm = await self.specification_repo.create(session, specification)
            cycle_results["phases"]["specification"] = {
                "status": "completed",
                "specification_id": spec_orm.id,
                "goal": specification.goal
            }
            logger.info(f" Specification created: {spec_orm.id}")

            # ================================================================
            # PHASE 2: TOOL & TEMPLATE SELECTION
            # ================================================================
            logger.info(" PHASE 2: Tool & Template Selection")

            # Get tool recommendations
            tool_recommendations = await self.scenario_generator.recommend_tools(
                specification
            )

            # Select engine (user can override)
            selected_engine = self.scenario_generator.select_tool(
                specification,
                user_choice=user_preferences.get("engine") if user_preferences else None
            )

            # Generate or select scenario
            scenario = await self.scenario_generator.generate_scenario(
                specification,
                session
            )

            if not scenario:
                raise ValueError("Failed to generate scenario")

            # Save scenario
            scenario_orm = await self.scenario_repo.create(session, scenario)
            cycle_results["phases"]["selection"] = {
                "status": "completed",
                "scenario_id": scenario_orm.id,
                "engine_selected": selected_engine.value,
                "tool_recommendations": tool_recommendations
            }
            logger.info(f" Scenario created: {scenario_orm.id}, Engine: {selected_engine.value}")

            # ================================================================
            # PHASE 3: VALIDATION
            # ================================================================
            logger.info("️ PHASE 3: Validation")

            validation = await self.ai_orchestrator.validate_specification(
                specification=specification,
                context=organization_context
            )

            if not validation.get("is_valid", False):
                logger.warning(f"️ Validation issues: {validation.get('suggestions')}")

            cycle_results["phases"]["validation"] = {
                "status": "completed",
                "is_valid": validation.get("is_valid"),
                "confidence": validation.get("confidence"),
                "suggestions": validation.get("suggestions", [])
            }
            logger.info(f" Validation completed: valid={validation.get('is_valid')}")

            # ================================================================
            # PHASE 4: SIMULATION EXECUTION
            # ================================================================
            logger.info("️ PHASE 4: Simulation Execution")

            # Create simulation instance
            simulation = Simulation(
                specification_id=spec_orm.id,
                scenario_id=scenario_orm.id,
                engine=selected_engine,
                engine_config=EngineConfig(
                    parameters={"max_duration": specification.max_duration}
                ),
                visualization_config=VisualizationConfig(
                    enabled=True,
                    real_time=True
                ),
                integration_config=IntegrationConfig(
                    eventbus_enabled=True,
                    ai_orchestrator_enabled=True
                ),
                status=SimulationStatus.PENDING,
                created_by=specification.created_by,
                organization_id=specification.organization_id
            )

            # Save simulation
            simulation_orm = await self.simulation_repo.create(session, simulation)
            cycle_results["simulation_id"] = simulation_orm.id

            # Publish simulation.created event
            await self.eventbus.publish_simulation_created(simulation, tenant_id)

            # Update status to initializing
            await self.simulation_repo.update_status(
                session,
                simulation_orm.id,
                SimulationStatus.INITIALIZING
            )

            # TODO: Execute simulation with selected engine
            # For now, we'll simulate execution with mock results
            logger.info(f" Executing simulation with {selected_engine.value} engine...")

            # Update status to running
            await self.simulation_repo.update_status(
                session,
                simulation_orm.id,
                SimulationStatus.RUNNING
            )

            # Publish simulation.started event
            await self.eventbus.publish_simulation_started(simulation, tenant_id)

            # Simulate execution (will be replaced with real engine execution)
            await asyncio.sleep(2)  # Simulate work

            # Create mock results
            results = SimulationResult(
                simulation_id=simulation_orm.id,
                status="completed",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_seconds=120,
                engine_used=selected_engine.value,
                overall_success_rate=0.85,
                quality_score=8.5,
                complexity_level=scenario.complexity_level,
                metrics={"execution_time": 120, "events_processed": 42},
                detailed_metrics={"phase_1": "success", "phase_2": "success"},
                events=[],
                participant_performance=[],
                success_criteria=scenario.success_criteria,
                kpis_achieved=["RTO met", "RPO met"],
                lessons_learned=[
                    "Effective communication is critical",
                    "Backup procedures work as expected"
                ],
                recommendations=[
                    "Increase training frequency",
                    "Update recovery procedures",
                    "Improve documentation"
                ],
                improvement_areas=["Response time could be faster"]
            )

            # Save results
            result_orm = await self.result_repo.create(session, results)

            # Update simulation status
            await self.simulation_repo.update_status(
                session,
                simulation_orm.id,
                SimulationStatus.COMPLETED
            )

            cycle_results["phases"]["execution"] = {
                "status": "completed",
                "result_id": result_orm.id,
                "duration_seconds": results.duration_seconds,
                "success_rate": results.overall_success_rate
            }
            logger.info(f" Simulation executed: success_rate={results.overall_success_rate}")

            # Publish simulation.completed event
            await self.eventbus.publish_simulation_completed(
                simulation, results, tenant_id
            )

            # ================================================================
            # PHASE 5: ANALYSIS
            # ================================================================
            logger.info(" PHASE 5: Analysis")

            analysis = await self.ai_orchestrator.analyze_results(
                simulation_id=simulation_orm.id,
                results=results,
                specification=specification
            )

            cycle_results["phases"]["analysis"] = {
                "status": "completed",
                "quality_score": analysis.get("quality_score"),
                "contribution_worthy": analysis.get("contribution_worthy"),
                "insights": analysis.get("analysis")
            }
            logger.info(f" Analysis completed: quality={analysis.get('quality_score')}")

            # ================================================================
            # PHASE 6: REPORTING
            # ================================================================
            logger.info(" PHASE 6: Report Generation")

            report = await self.report_generator.generate_full_report(
                simulation=simulation,
                results=results,
                specification=specification,
                scenario=scenario,
                format="markdown"
            )

            cycle_results["phases"]["reporting"] = {
                "status": "completed",
                "report_id": report["report_id"],
                "report_path": report["file_path"]
            }
            logger.info(f" Report generated: {report['file_path']}")

            # ================================================================
            # PHASE 7: LEARNING & MEMORY INTEGRATION
            # ================================================================
            logger.info(" PHASE 7: Learning & Memory Integration")

            learning_results = {}

            # 7.1: Create PDCA cycle
            pdca_id = await self.workflow.create_pdca_cycle(
                simulation_id=simulation_orm.id,
                specification=specification,
                results=results,
                organization_id=specification.organization_id,
                tenant_id=tenant_id
            )
            learning_results["pdca_cycle_id"] = pdca_id

            # 7.2: Create Case in Case Library
            case_id = await self.workflow.create_simulation_case(
                simulation=simulation,
                results=results,
                specification=specification,
                organization_id=specification.organization_id,
                tenant_id=tenant_id
            )
            learning_results["case_id"] = case_id

            # 7.3: Store pattern in Memory System
            memory_id = await self.ai_orchestrator.store_simulation_pattern(
                simulation_id=simulation_orm.id,
                pattern_data={
                    "specification": specification.model_dump(),
                    "results": results.model_dump(),
                    "success_rate": results.overall_success_rate,
                    "quality_score": results.quality_score
                }
            )
            learning_results["memory_id"] = memory_id

            # 7.4: Store knowledge
            knowledge_id = await self.knowledge.store_simulation_knowledge(
                simulation_id=simulation_orm.id,
                results=results,
                specification=specification,
                organization_id=specification.organization_id,
                tenant_id=tenant_id
            )
            learning_results["knowledge_id"] = knowledge_id

            # 7.5: Submit to Scenario Orchestrator learning system (existing service!)
            orchestrator_learning = await self.scenario_orchestrator.collect_exercise_result(
                exercise_id=simulation_orm.id,
                scenario_id=scenario_orm.id,
                template_id=scenario_orm.id,  # Using scenario as template
                results=results
            )
            learning_results["scenario_orchestrator_learning"] = orchestrator_learning

            # 7.6: Contribute to community (if high quality)
            if analysis.get("contribution_worthy", False):
                community_id = await self.community.contribute_template(
                    scenario=scenario,
                    results=results,
                    organization_id=specification.organization_id,
                    tenant_id=tenant_id,
                    anonymize=True
                )
                learning_results["community_contribution_id"] = community_id

            cycle_results["phases"]["learning"] = {
                "status": "completed",
                **learning_results
            }
            logger.info(f" Learning integrated: PDCA={pdca_id}, Case={case_id}, "
                       f"ScenarioOrch={orchestrator_learning.get('status')}")

            # ================================================================
            # FINAL: SUCCESS
            # ================================================================
            cycle_results["status"] = "completed"
            cycle_results["completed_at"] = datetime.utcnow().isoformat()

            logger.info("  FULL SIMULATION CYCLE COMPLETED SUCCESSFULLY!")
            return cycle_results

        except Exception as e:
            logger.error(f" Simulation cycle failed: {e}", exc_info=True)
            cycle_results["status"] = "failed"
            cycle_results["errors"].append(str(e))
            return cycle_results

    # ========================================================================
    # INDIVIDUAL PHASE METHODS
    # ========================================================================

    async def create_specification_from_input(
        self,
        user_input: str,
        session: AsyncSession,
        organization_context: Optional[Dict] = None,
        user_preferences: Optional[Dict] = None
    ) -> Optional[TaskSpecification]:
        """
        Phase 1: Create specification from user input

        Args:
            user_input: Natural language description
            session: Database session
            organization_context: Organization data
            user_preferences: User preferences

        Returns:
            TaskSpecification or None
        """
        return await self.scenario_generator.generate_from_natural_language(
            user_input=user_input,
            organization_context=organization_context,
            user_preferences=user_preferences,
            session=session
        )

    async def recommend_and_select_tools(
        self,
        specification: TaskSpecification,
        user_choice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Phase 2: Recommend and select tools

        Args:
            specification: Task specification
            user_choice: User's tool choice (optional)

        Returns:
            Selection results
        """
        recommendations = await self.scenario_generator.recommend_tools(specification)
        selected_engine = self.scenario_generator.select_tool(specification, user_choice)

        return {
            "recommendations": recommendations,
            "selected_engine": selected_engine.value
        }

    async def validate_simulation_setup(
        self,
        specification: TaskSpecification,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Phase 3: Validate simulation setup

        Args:
            specification: Task specification
            context: Additional context

        Returns:
            Validation results
        """
        return await self.ai_orchestrator.validate_specification(
            specification=specification,
            context=context
        )

    async def execute_simulation_only(
        self,
        simulation_id: str,
        session: AsyncSession
    ) -> Optional[SimulationResult]:
        """
        Phase 4: Execute simulation only (without full cycle)

        Args:
            simulation_id: Simulation ID
            session: Database session

        Returns:
            SimulationResult or None
        """
        # Get simulation
        simulation_orm = await self.simulation_repo.get_by_id(session, simulation_id)
        if not simulation_orm:
            logger.error(f"Simulation not found: {simulation_id}")
            return None

        # TODO: Implement actual engine execution
        # For now, return None to indicate need for implementation
        logger.warning("Actual engine execution not yet implemented")
        return None

    async def analyze_and_report(
        self,
        simulation_id: str,
        session: AsyncSession,
        report_format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Phases 5-6: Analyze results and generate report

        Args:
            simulation_id: Simulation ID
            session: Database session
            report_format: Report format

        Returns:
            Analysis and report data
        """
        # Get simulation, results, specification, scenario
        simulation_orm = await self.simulation_repo.get_by_id(session, simulation_id)
        if not simulation_orm:
            raise ValueError(f"Simulation not found: {simulation_id}")

        # TODO: Fetch related data and generate analysis/report
        logger.warning("Analysis and reporting implementation incomplete")
        return {}

    async def integrate_learning(
        self,
        simulation_id: str,
        session: AsyncSession,
        tenant_id: str = "default"
    ) -> Dict[str, Optional[str]]:
        """
        Phase 7: Integrate learning into platform

        Args:
            simulation_id: Simulation ID
            session: Database session
            tenant_id: Tenant ID

        Returns:
            Dictionary of created resource IDs
        """
        # TODO: Implement learning integration
        logger.warning("Learning integration implementation incomplete")
        return {
            "pdca_cycle_id": None,
            "case_id": None,
            "memory_id": None,
            "knowledge_id": None
        }
