"""
Example: BIA Service Integration with Self-Aware Components

This demonstrates how to integrate the self-aware service components
into the existing BIA service.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .self_aware_base import (
    SelfAwareService,
    EventPriority,
    EventContext,
    HandlingDecision
)
from .health_monitor import check_database_health, check_redis_health, check_eventbus_health
from .capability_registry import Capability, ExpertiseLevel
from .load_manager import LoadPolicy
from .collaboration_mixin import Vote, VoteType

logger = logging.getLogger(__name__)


class SelfAwareBIAService(SelfAwareService):
    """
    Self-aware BIA Service with graceful choreography.

    Demonstrates:
    - Intelligent event handling
    - Load-aware processing
    - Graceful degradation
    - Service collaboration
    - Health monitoring
    """

    def __init__(
        self,
        db_session,
        redis_client,
        eventbus_client,
        bia_repository,
        ai_client=None
    ):
        """
        Initialize self-aware BIA service.

        Args:
            db_session: Database session
            redis_client: Redis client
            eventbus_client: EventBus client
            bia_repository: BIA repository
            ai_client: Optional AI client for decisions
        """
        # Initialize base
        super().__init__(
            service_name="bia",
            capabilities=[
                "bia.assessment.create",
                "bia.assessment.update",
                "bia.assessment.complete",
                "bia.process.create",
                "bia.process.analyze",
                "bia.criticality.assess",
                "bia.dependencies.map",
                "bia.rto.calculate",
                "bia.impact.analyze"
            ],
            load_policy=LoadPolicy(
                degradation_threshold=0.85,
                recovery_threshold=0.60,
                enable_auto_degradation=True,
                enable_load_shedding=True
            ),
            enable_ai_decisions=True,
            enable_collaboration=True
        )

        self.db = db_session
        self.redis = redis_client
        self.eventbus = eventbus_client
        self.repository = bia_repository
        self.ai_client = ai_client

        # Mark essential capabilities (never degraded)
        self.mark_essential("bia.assessment.create")
        self.mark_essential("bia.assessment.complete")
        self.mark_essential("bia.process.create")

        # Register event handlers
        self._register_handlers()

        # Setup health monitoring
        self._setup_health_monitoring()

        # Setup collaboration
        self._setup_collaboration()

        # Setup load management callbacks
        self.load_manager.set_degradation_callback(self.degrade_gracefully)
        self.load_manager.set_recovery_callback(self.recover_from_degradation)

        logger.info("SelfAwareBIAService initialized")

    def _register_handlers(self):
        """Register event handlers"""
        # Assessment events
        self.register_handler("bia.assessment.create", self.handle_assessment_create, EventPriority.HIGH)
        self.register_handler("bia.assessment.update", self.handle_assessment_update, EventPriority.NORMAL)
        self.register_handler("bia.assessment.complete", self.handle_assessment_complete, EventPriority.HIGH)

        # Process events
        self.register_handler("bia.process.*", self.handle_process_event, EventPriority.NORMAL)

        # Analysis events (can be deferred)
        self.register_handler("bia.*.analyze", self.handle_analysis_event, EventPriority.LOW)

        # Incoming events from other services
        self.register_handler("risk.assessment.completed", self.handle_risk_completed, EventPriority.NORMAL)
        self.register_handler("compliance.gap.identified", self.handle_compliance_gap, EventPriority.NORMAL)

    def _setup_health_monitoring(self):
        """Setup health checks for dependencies"""
        self.health_monitor.register_check(
            "database",
            lambda: check_database_health(self.db)
        )

        self.health_monitor.register_check(
            "redis",
            lambda: check_redis_health(self.redis)
        )

        self.health_monitor.register_check(
            "eventbus",
            lambda: check_eventbus_health(self.eventbus)
        )

        logger.info("Health monitoring configured")

    def _setup_collaboration(self):
        """Setup collaboration handlers"""
        # Register vote handlers for consensus decisions
        self.collaboration.register_vote_handler(
            "plan_approval",
            self.vote_on_plan_approval
        )

        self.collaboration.register_vote_handler(
            "criticality_assessment",
            self.vote_on_criticality
        )

        # Register service capabilities for discovery
        self.collaboration.register_service_capabilities("risk", {
            "risk.assessment.create",
            "risk.scenario.evaluate",
            "risk.mitigation.plan"
        })

        self.collaboration.register_service_capabilities("compliance", {
            "compliance.assessment.create",
            "compliance.gap.analyze"
        })

        self.collaboration.register_service_capabilities("plans", {
            "plans.create",
            "plans.review",
            "plans.approve"
        })

        logger.info("Collaboration configured")

    # Event Handlers

    async def handle_assessment_create(self, ctx: EventContext) -> Dict[str, Any]:
        """Handle BIA assessment creation"""
        logger.info(f"Creating BIA assessment for tenant {ctx.tenant_id}")

        # Track request
        await self.load_manager.track_request_start()
        start_time = datetime.utcnow()

        try:
            data = ctx.event_data

            # Create assessment
            assessment = await self.repository.create_assessment(
                tenant_id=ctx.tenant_id,
                name=data.get("name"),
                process_data=data.get("process_data"),
                criticality=data.get("criticality")
            )

            # Publish event for other services
            await self.eventbus.publish(
                "bia.assessment.created",
                {
                    "assessment_id": assessment.id,
                    "tenant_id": ctx.tenant_id,
                    "criticality": assessment.criticality,
                    "correlation_id": ctx.correlation_id
                }
            )

            # Record success
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.health_monitor.record_request(duration_ms, error=False)

            return {"assessment_id": assessment.id, "status": "created"}

        except Exception as e:
            logger.error(f"Error creating assessment: {e}", exc_info=True)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.health_monitor.record_request(duration_ms, error=True)
            raise

        finally:
            await self.load_manager.track_request_end()

    async def handle_assessment_update(self, ctx: EventContext) -> Dict[str, Any]:
        """Handle BIA assessment update"""
        logger.info(f"Updating BIA assessment {ctx.event_data.get('assessment_id')}")

        await self.load_manager.track_request_start()

        try:
            data = ctx.event_data
            assessment_id = data.get("assessment_id")

            # Update assessment
            await self.repository.update_assessment(
                assessment_id=assessment_id,
                updates=data.get("updates", {})
            )

            return {"assessment_id": assessment_id, "status": "updated"}

        finally:
            await self.load_manager.track_request_end()

    async def handle_assessment_complete(self, ctx: EventContext) -> Dict[str, Any]:
        """Handle BIA assessment completion"""
        logger.info(f"Completing BIA assessment {ctx.event_data.get('assessment_id')}")

        await self.load_manager.track_request_start()

        try:
            data = ctx.event_data
            assessment_id = data.get("assessment_id")

            # Complete assessment
            assessment = await self.repository.complete_assessment(assessment_id)

            # Check if critical process identified
            if assessment.criticality in ["CRITICAL", "HIGH"]:
                # Request consensus from other services
                decision = await self.collaboration.request_consensus(
                    participants=["risk", "compliance"],
                    context={
                        "type": "criticality_assessment",
                        "assessment_id": assessment_id,
                        "criticality": assessment.criticality
                    }
                )

                if decision.consensus_reached:
                    logger.info(f"Consensus reached: {decision.decision}")

            # Publish completion event
            await self.eventbus.publish(
                "bia.assessment.completed",
                {
                    "assessment_id": assessment_id,
                    "tenant_id": ctx.tenant_id,
                    "criticality": assessment.criticality,
                    "rto_hours": assessment.rto_hours,
                    "correlation_id": ctx.correlation_id
                }
            )

            return {"assessment_id": assessment_id, "status": "completed"}

        finally:
            await self.load_manager.track_request_end()

    async def handle_process_event(self, ctx: EventContext) -> Dict[str, Any]:
        """Handle BIA process events"""
        logger.info(f"Handling process event: {ctx.event_type}")

        # Check load before processing
        if not await self.load_manager.can_accept(priority=ctx.priority.value):
            logger.warning(f"Service overloaded, deferring {ctx.event_type}")
            await self.load_manager.defer_event({
                "event_type": ctx.event_type,
                "event_data": ctx.event_data,
                "tenant_id": ctx.tenant_id
            })
            return {"status": "deferred"}

        # Process based on specific event
        if ctx.event_type == "bia.process.create":
            return await self._create_process(ctx)
        elif ctx.event_type == "bia.process.analyze":
            return await self._analyze_process(ctx)

        return {"status": "handled"}

    async def handle_analysis_event(self, ctx: EventContext) -> Dict[str, Any]:
        """Handle analysis events (can be deferred under load)"""
        logger.info(f"Handling analysis event: {ctx.event_type}")

        # Analysis can be deferred if under load
        load_level = await self.load_manager.get_load_level()
        if load_level.value in ["high", "critical"]:
            logger.info(f"Deferring analysis due to load: {load_level.value}")
            await self.load_manager.defer_event({
                "event_type": ctx.event_type,
                "event_data": ctx.event_data
            })
            return {"status": "deferred"}

        # Perform analysis
        return await self._perform_analysis(ctx)

    async def handle_risk_completed(self, ctx: EventContext) -> Dict[str, Any]:
        """Handle risk assessment completion from Risk Service"""
        logger.info("Risk assessment completed - checking BIA impact")

        data = ctx.event_data
        risk_level = data.get("risk_level")

        # If high risk, may need to update BIA
        if risk_level in ["HIGH", "CRITICAL"]:
            process_id = data.get("process_id")
            if process_id:
                await self._update_bia_from_risk(process_id, risk_level)

        return {"status": "processed"}

    async def handle_compliance_gap(self, ctx: EventContext) -> Dict[str, Any]:
        """Handle compliance gap identification"""
        logger.info("Compliance gap identified - checking BIA coverage")

        data = ctx.event_data
        gap_area = data.get("area")

        # Check if BIA covers this area
        coverage = await self._check_bia_coverage(gap_area)

        if not coverage:
            logger.warning(f"BIA gap identified in {gap_area}")
            # Could trigger new BIA assessment

        return {"status": "processed", "coverage": coverage}

    # Collaboration Handlers

    async def vote_on_plan_approval(self, context: Dict[str, Any]) -> Vote:
        """Vote on plan approval based on BIA data"""
        plan_id = context.get("plan_id")

        logger.info(f"Voting on plan approval: {plan_id}")

        # Get BIA data for this plan
        bia_coverage = await self._get_bia_coverage_for_plan(plan_id)

        # Determine vote based on coverage
        if bia_coverage >= 0.9:
            return Vote(
                service=self.service_name,
                vote=VoteType.APPROVE,
                confidence=0.95,
                reasoning=f"BIA coverage {bia_coverage:.0%} - all critical processes covered",
                metadata={"coverage": bia_coverage}
            )
        elif bia_coverage >= 0.7:
            return Vote(
                service=self.service_name,
                vote=VoteType.APPROVE,
                confidence=0.7,
                reasoning=f"BIA coverage {bia_coverage:.0%} - acceptable",
                metadata={"coverage": bia_coverage}
            )
        else:
            return Vote(
                service=self.service_name,
                vote=VoteType.REJECT,
                confidence=0.9,
                reasoning=f"BIA coverage {bia_coverage:.0%} - insufficient",
                metadata={"coverage": bia_coverage}
            )

    async def vote_on_criticality(self, context: Dict[str, Any]) -> Vote:
        """Vote on criticality assessment"""
        assessment_id = context.get("assessment_id")
        proposed_criticality = context.get("criticality")

        logger.info(f"Voting on criticality for assessment {assessment_id}")

        # Get assessment data
        assessment = await self.repository.get_assessment(assessment_id)

        # Agree with BIA's own assessment
        if assessment.criticality == proposed_criticality:
            return Vote(
                service=self.service_name,
                vote=VoteType.APPROVE,
                confidence=1.0,
                reasoning="Matches BIA assessment"
            )
        else:
            return Vote(
                service=self.service_name,
                vote=VoteType.ABSTAIN,
                confidence=0.5,
                reasoning="Differs from BIA assessment"
            )

    # Helper Methods

    async def _create_process(self, ctx: EventContext):
        """Create BIA process"""
        # Implementation
        pass

    async def _analyze_process(self, ctx: EventContext):
        """Analyze BIA process"""
        # Implementation
        pass

    async def _perform_analysis(self, ctx: EventContext):
        """Perform detailed analysis"""
        # Implementation
        pass

    async def _update_bia_from_risk(self, process_id: int, risk_level: str):
        """Update BIA based on risk assessment"""
        # Implementation
        pass

    async def _check_bia_coverage(self, area: str) -> bool:
        """Check if BIA covers an area"""
        # Implementation
        return True

    async def _get_bia_coverage_for_plan(self, plan_id: int) -> float:
        """Get BIA coverage percentage for plan"""
        # Implementation
        return 0.85

    # Lifecycle Methods

    async def start(self):
        """Start the service and all components"""
        logger.info("Starting SelfAwareBIAService")

        # Start health monitoring
        await self.health_monitor.start()

        # Start load management
        await self.load_manager.start()

        logger.info("SelfAwareBIAService started successfully")

    async def stop(self):
        """Stop the service and all components"""
        logger.info("Stopping SelfAwareBIAService")

        # Stop health monitoring
        await self.health_monitor.stop()

        # Stop load management
        await self.load_manager.stop()

        logger.info("SelfAwareBIAService stopped")


# Example Usage in main.py

"""
# In main.py lifespan:

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup

    # Initialize self-aware BIA service
    global bia_service
    bia_service = SelfAwareBIAService(
        db_session=get_db(),
        redis_client=get_cache(),
        eventbus_client=get_eventbus(),
        bia_repository=BIARepository()
    )

    # Start service
    await bia_service.start()

    # Subscribe to events
    eventbus = get_eventbus()

    async def handle_event(event_data: dict, tenant_id: str = None):
        # Use self-aware handling
        result = await bia_service.on_event(
            event_type=event_data.get("event_type"),
            event_data=event_data,
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL
        )

        if result.decision == HandlingDecision.HANDLE:
            # Execute handler
            await result.handler(EventContext(
                event_type=event_data.get("event_type"),
                event_data=event_data,
                tenant_id=tenant_id
            ))
        elif result.decision == HandlingDecision.DEFER:
            logger.info(f"Deferred event: {result.reasoning}")
        elif result.decision == HandlingDecision.DELEGATE:
            logger.info(f"Delegating to: {result.delegate_to}")

    # Subscribe to relevant topics
    await eventbus.subscribe("bia.*", handle_event)
    await eventbus.subscribe("risk.assessment.completed", handle_event)
    await eventbus.subscribe("compliance.gap.identified", handle_event)

    yield

    # Shutdown
    await bia_service.stop()
"""


# Example API Endpoint

"""
@app.post("/api/bia/assessments")
async def create_assessment(
    data: AssessmentCreate,
    current_user = Depends(get_current_user)
):
    # Create event context
    ctx = EventContext(
        event_type="bia.assessment.create",
        event_data=data.dict(),
        tenant_id=current_user.tenant_id,
        priority=EventPriority.HIGH
    )

    # Let self-aware service decide
    result = await bia_service.on_event(
        ctx.event_type,
        ctx.event_data,
        tenant_id=ctx.tenant_id,
        priority=ctx.priority
    )

    if result.decision == HandlingDecision.HANDLE:
        # Execute
        return await result.handler(ctx)
    elif result.decision == HandlingDecision.DEFER:
        return JSONResponse(
            status_code=503,
            content={"message": "Service busy, request queued"}
        )
    else:
        return JSONResponse(
            status_code=503,
            content={"message": f"Cannot handle request: {result.reasoning}"}
        )
"""
