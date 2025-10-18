"""
Intelligent Event Router - Example Usage
=========================================

Demonstrates how to use the IntelligentEventRouter for AI-powered
event routing with semantic matching, priority queues, and load balancing.

Run this example:
    cd /Users/MD/AI-Platform-ISO
    python -m infrastructure.eventbus.examples.intelligent_routing_example
"""

import asyncio
import logging
from datetime import datetime
from infrastructure.eventbus.backends.memory import InMemoryEventBus
from infrastructure.eventbus.intelligent_router import (
    IntelligentEventRouter,
    SubscriberCapabilities
)
from infrastructure.eventbus.core.events import Event, EventPriority

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Example Subscriber Handlers
# ============================================================================

class RiskAnalyzerSubscriber:
    """Simulates a risk analysis service subscriber"""

    def __init__(self, name: str, processing_time: float = 0.5):
        self.name = name
        self.processing_time = processing_time
        self.events_processed = 0

    async def handle_risk_event(self, event: Event):
        """Handle risk-related events"""
        self.events_processed += 1

        logger.info(
            f"[{self.name}] Processing risk event: {event.type} "
            f"(priority={event.priority.name})"
        )

        # Simulate processing
        await asyncio.sleep(self.processing_time)

        # Extract and process data
        if "assessment" in event.type:
            logger.info(
                f"[{self.name}] Completed risk assessment: "
                f"{event.data.get('description', 'N/A')}"
            )
        elif "threat" in event.type:
            logger.warning(
                f"[{self.name}] Threat detected: "
                f"{event.data.get('threat_type', 'unknown')}"
            )

        logger.info(
            f"[{self.name}] Event {event.id[:8]} processed "
            f"(total: {self.events_processed})"
        )


class ComplianceCheckerSubscriber:
    """Simulates a compliance checking service subscriber"""

    def __init__(self, name: str, processing_time: float = 0.3):
        self.name = name
        self.processing_time = processing_time
        self.events_processed = 0

    async def handle_compliance_event(self, event: Event):
        """Handle compliance-related events"""
        self.events_processed += 1

        logger.info(
            f"[{self.name}] Processing compliance event: {event.type}"
        )

        # Simulate processing
        await asyncio.sleep(self.processing_time)

        # Check compliance
        standard = event.data.get("standard", "ISO 22301")
        status = event.data.get("status", "pending")

        logger.info(
            f"[{self.name}] Compliance check for {standard}: {status}"
        )
        logger.info(
            f"[{self.name}] Event {event.id[:8]} processed "
            f"(total: {self.events_processed})"
        )


class WorkflowOrchestratorSubscriber:
    """Simulates a workflow orchestration service subscriber"""

    def __init__(self, name: str, processing_time: float = 0.7):
        self.name = name
        self.processing_time = processing_time
        self.events_processed = 0

    async def handle_workflow_event(self, event: Event):
        """Handle workflow-related events"""
        self.events_processed += 1

        logger.info(
            f"[{self.name}] Processing workflow event: {event.type}"
        )

        # Simulate complex processing
        await asyncio.sleep(self.processing_time)

        # Process workflow state change
        if "stage_changed" in event.type:
            old_stage = event.data.get("old_stage", "unknown")
            new_stage = event.data.get("new_stage", "unknown")
            logger.info(
                f"[{self.name}] Workflow transition: {old_stage} → {new_stage}"
            )

        logger.info(
            f"[{self.name}] Event {event.id[:8]} processed "
            f"(total: {self.events_processed})"
        )


class IncidentResponseSubscriber:
    """Simulates an incident response service subscriber"""

    def __init__(self, name: str, processing_time: float = 0.2):
        self.name = name
        self.processing_time = processing_time
        self.events_processed = 0

    async def handle_incident_event(self, event: Event):
        """Handle incident-related events"""
        self.events_processed += 1

        logger.warning(
            f"[{self.name}] INCIDENT EVENT: {event.type} "
            f"(priority={event.priority.name})"
        )

        # Fast processing for incidents
        await asyncio.sleep(self.processing_time)

        severity = event.data.get("severity", "medium")
        logger.warning(
            f"[{self.name}] Incident severity: {severity} - "
            f"initiating response protocol"
        )
        logger.info(
            f"[{self.name}] Event {event.id[:8]} processed "
            f"(total: {self.events_processed})"
        )


# ============================================================================
# Example Scenarios
# ============================================================================

async def scenario_1_basic_routing():
    """
    Scenario 1: Basic Intelligent Routing

    Demonstrates:
    - Subscriber registration with capabilities
    - Event routing with AI analysis
    - Priority-based processing
    """
    logger.info("\n" + "="*70)
    logger.info("SCENARIO 1: Basic Intelligent Routing")
    logger.info("="*70 + "\n")

    # Create eventbus and intelligent router
    eventbus = InMemoryEventBus()
    router = IntelligentEventRouter(
        base_eventbus=eventbus,
        enable_ai_analysis=True,
        enable_semantic_matching=True
    )

    await router.initialize()

    # Create subscribers
    risk_analyzer = RiskAnalyzerSubscriber("RiskAnalyzer-1", processing_time=0.3)
    compliance_checker = ComplianceCheckerSubscriber("ComplianceChecker-1", processing_time=0.2)

    # Register subscribers with capabilities
    await router.register_subscriber(
        subscriber_id="risk_analyzer_1",
        event_pattern="risk.*",
        handler=risk_analyzer.handle_risk_event,
        capabilities={
            "domains": ["risk", "security", "threat_analysis"],
            "max_concurrent": 5,
            "avg_processing_time_ms": 300,
            "sla_ms": 1000,
            "semantic_tags": ["risk", "assessment", "vulnerability", "threat"]
        }
    )

    await router.register_subscriber(
        subscriber_id="compliance_checker_1",
        event_pattern="compliance.*",
        handler=compliance_checker.handle_compliance_event,
        capabilities={
            "domains": ["compliance", "audit", "standards"],
            "max_concurrent": 10,
            "avg_processing_time_ms": 200,
            "sla_ms": 500,
            "semantic_tags": ["compliance", "ISO22301", "audit", "regulation"]
        }
    )

    # Publish various events
    events = [
        Event.create(
            event_type="risk.assessment_needed",
            data={
                "assessment_type": "cybersecurity",
                "urgency": "high",
                "description": "Critical vulnerability in payment gateway"
            },
            source="security-scanner",
            tenant_id="tenant_123",
            priority=EventPriority.HIGH
        ),
        Event.create(
            event_type="compliance.audit_required",
            data={
                "standard": "ISO 22301",
                "status": "pending",
                "audit_type": "annual_review"
            },
            source="compliance-service",
            tenant_id="tenant_123",
            priority=EventPriority.NORMAL
        ),
        Event.create(
            event_type="risk.threat_detected",
            data={
                "threat_type": "DDoS",
                "severity": "critical",
                "source_ip": "203.0.113.0"
            },
            source="network-monitor",
            tenant_id="tenant_123",
            priority=EventPriority.CRITICAL
        )
    ]

    # Route events
    for event in events:
        decision = await router.route_event(event)
        logger.info(
            f"Routed event {event.id[:8]}: "
            f"subscribers={decision.selected_subscribers}, "
            f"strategy={decision.routing_strategy}, "
            f"confidence={decision.confidence_score:.2f}"
        )

    # Wait for processing
    await asyncio.sleep(2)

    # Get metrics
    metrics = router.get_metrics()
    logger.info("\n" + "-"*70)
    logger.info("ROUTING METRICS:")
    logger.info(f"  Total events: {metrics['total_events']}")
    logger.info(f"  Total routed: {metrics['total_routed']}")
    logger.info(f"  Routing efficiency: {metrics['routing_efficiency']:.2%}")
    logger.info(f"  Avg routing time: {metrics['avg_routing_time_ms']:.2f}ms")
    logger.info(f"  SLA compliance: {metrics['sla_compliance_rate']:.2%}")

    logger.info("\nSUBSCRIBER METRICS:")
    for sub_id, sub_metrics in metrics['subscriber_metrics'].items():
        logger.info(f"  {sub_id}:")
        logger.info(f"    Success rate: {sub_metrics['success_rate']:.2%}")
        logger.info(f"    Avg latency: {sub_metrics['avg_latency_ms']:.2f}ms")
        logger.info(f"    Status: {sub_metrics['status']}")

    # Shutdown
    await router.shutdown()

    logger.info("\nScenario 1 complete!\n")


async def scenario_2_load_balancing():
    """
    Scenario 2: Load-Aware Routing

    Demonstrates:
    - Multiple subscribers for same event type
    - Load-based routing decisions
    - Capacity management
    """
    logger.info("\n" + "="*70)
    logger.info("SCENARIO 2: Load-Aware Routing & Load Balancing")
    logger.info("="*70 + "\n")

    # Create eventbus and router
    eventbus = InMemoryEventBus()
    router = IntelligentEventRouter(
        base_eventbus=eventbus,
        enable_ai_analysis=True,
        enable_semantic_matching=True
    )

    await router.initialize()

    # Create multiple risk analyzer instances
    risk_analyzer_1 = RiskAnalyzerSubscriber("RiskAnalyzer-1", processing_time=0.5)
    risk_analyzer_2 = RiskAnalyzerSubscriber("RiskAnalyzer-2", processing_time=0.3)
    risk_analyzer_3 = RiskAnalyzerSubscriber("RiskAnalyzer-3", processing_time=0.4)

    # Register with different capacities
    await router.register_subscriber(
        subscriber_id="risk_analyzer_1",
        event_pattern="risk.*",
        handler=risk_analyzer_1.handle_risk_event,
        capabilities={
            "domains": ["risk", "security"],
            "max_concurrent": 3,  # Lower capacity
            "avg_processing_time_ms": 500,
            "sla_ms": 1000,
            "semantic_tags": ["risk", "assessment"]
        }
    )

    await router.register_subscriber(
        subscriber_id="risk_analyzer_2",
        event_pattern="risk.*",
        handler=risk_analyzer_2.handle_risk_event,
        capabilities={
            "domains": ["risk", "security", "threat"],
            "max_concurrent": 5,  # Higher capacity
            "avg_processing_time_ms": 300,
            "sla_ms": 800,
            "semantic_tags": ["risk", "threat", "vulnerability"]
        }
    )

    await router.register_subscriber(
        subscriber_id="risk_analyzer_3",
        event_pattern="risk.*",
        handler=risk_analyzer_3.handle_risk_event,
        capabilities={
            "domains": ["risk"],
            "max_concurrent": 4,
            "avg_processing_time_ms": 400,
            "sla_ms": 1200,
            "semantic_tags": ["risk"]
        }
    )

    # Publish burst of events
    logger.info("Publishing burst of 15 risk events...")

    for i in range(15):
        event = Event.create(
            event_type="risk.assessment_needed",
            data={
                "assessment_id": i,
                "type": "security_assessment",
                "description": f"Assessment request #{i}"
            },
            source="risk-service",
            tenant_id="tenant_123",
            priority=EventPriority.NORMAL
        )

        decision = await router.route_event(event)
        logger.info(
            f"Event #{i}: routed to {decision.selected_subscribers} "
            f"(confidence={decision.confidence_score:.2f})"
        )

        # Small delay to simulate realistic event flow
        await asyncio.sleep(0.1)

    # Wait for processing
    await asyncio.sleep(3)

    # Show load distribution
    metrics = router.get_metrics()
    logger.info("\n" + "-"*70)
    logger.info("LOAD DISTRIBUTION:")

    for sub_id, sub_metrics in metrics['subscriber_metrics'].items():
        analyzer = None
        if sub_id == "risk_analyzer_1":
            analyzer = risk_analyzer_1
        elif sub_id == "risk_analyzer_2":
            analyzer = risk_analyzer_2
        elif sub_id == "risk_analyzer_3":
            analyzer = risk_analyzer_3

        if analyzer:
            logger.info(
                f"  {sub_id}: "
                f"processed={analyzer.events_processed}, "
                f"load={sub_metrics['current_load']}, "
                f"latency={sub_metrics['avg_latency_ms']:.0f}ms"
            )

    # Shutdown
    await router.shutdown()

    logger.info("\nScenario 2 complete!\n")


async def scenario_3_priority_handling():
    """
    Scenario 3: Priority-Based Routing

    Demonstrates:
    - AI-powered priority determination
    - Priority queue processing order
    - Critical event handling
    """
    logger.info("\n" + "="*70)
    logger.info("SCENARIO 3: Priority-Based Event Routing")
    logger.info("="*70 + "\n")

    # Create eventbus and router
    eventbus = InMemoryEventBus()
    router = IntelligentEventRouter(
        base_eventbus=eventbus,
        enable_ai_analysis=True,
        enable_semantic_matching=True
    )

    await router.initialize()

    # Create incident response subscriber
    incident_responder = IncidentResponseSubscriber("IncidentResponder-1", processing_time=0.2)

    await router.register_subscriber(
        subscriber_id="incident_responder_1",
        event_pattern="incident.*",
        handler=incident_responder.handle_incident_event,
        capabilities={
            "domains": ["incident", "emergency", "response"],
            "max_concurrent": 10,
            "avg_processing_time_ms": 200,
            "sla_ms": 500,
            "semantic_tags": ["incident", "emergency", "critical", "urgent"]
        }
    )

    # Publish events with different priorities
    events = [
        # Low priority
        Event.create(
            event_type="incident.report_filed",
            data={"incident_id": 1, "severity": "low", "type": "informational"},
            source="reporting-system",
            tenant_id="tenant_123",
            priority=EventPriority.LOW
        ),
        # Normal priority
        Event.create(
            event_type="incident.investigation_needed",
            data={"incident_id": 2, "severity": "medium", "type": "system_error"},
            source="monitoring-system",
            tenant_id="tenant_123",
            priority=EventPriority.NORMAL
        ),
        # Critical priority (AI should detect urgency)
        Event.create(
            event_type="incident.emergency_alert",
            data={
                "incident_id": 3,
                "severity": "critical",
                "type": "security_breach",
                "description": "Urgent: Data exfiltration detected in production database"
            },
            source="security-system",
            tenant_id="tenant_123",
            priority=EventPriority.CRITICAL
        ),
        # High priority
        Event.create(
            event_type="incident.service_degraded",
            data={"incident_id": 4, "severity": "high", "type": "performance"},
            source="monitoring-system",
            tenant_id="tenant_123",
            priority=EventPriority.HIGH
        ),
        # Another critical (AI analysis should upgrade this)
        Event.create(
            event_type="incident.system_failure",
            data={
                "incident_id": 5,
                "severity": "critical",
                "type": "system_down",
                "description": "Critical failure in payment processing system"
            },
            source="payment-system",
            tenant_id="tenant_123",
            priority=EventPriority.NORMAL  # Will be upgraded by AI
        )
    ]

    # Route all events
    logger.info("Publishing events with various priorities...\n")

    for event in events:
        decision = await router.route_event(event)
        logger.info(
            f"Event {event.data.get('incident_id')}: "
            f"declared_priority={event.priority.name}, "
            f"routed_priority={decision.priority_used.name}, "
            f"strategy={decision.routing_strategy}"
        )

    # Wait for processing
    await asyncio.sleep(2)

    # Show processing order (should be by priority)
    logger.info("\n" + "-"*70)
    logger.info("PRIORITY QUEUE STATUS:")
    metrics = router.get_metrics()
    for priority, depth in metrics['queue_depths'].items():
        logger.info(f"  {priority}: {depth} events")

    logger.info(f"\nTotal events processed: {incident_responder.events_processed}")

    # Shutdown
    await router.shutdown()

    logger.info("\nScenario 3 complete!\n")


async def scenario_4_semantic_matching():
    """
    Scenario 4: Semantic Event Matching

    Demonstrates:
    - Semantic similarity-based routing
    - Best subscriber selection
    - Domain expertise matching
    """
    logger.info("\n" + "="*70)
    logger.info("SCENARIO 4: Semantic Event Matching")
    logger.info("="*70 + "\n")

    # Create eventbus and router with semantic matching
    eventbus = InMemoryEventBus()
    router = IntelligentEventRouter(
        base_eventbus=eventbus,
        enable_ai_analysis=True,
        enable_semantic_matching=True  # Enable semantic matching
    )

    await router.initialize()

    # Create specialized subscribers
    workflow_orchestrator = WorkflowOrchestratorSubscriber("WorkflowOrchestrator-1")
    risk_analyzer = RiskAnalyzerSubscriber("RiskAnalyzer-1")
    compliance_checker = ComplianceCheckerSubscriber("ComplianceChecker-1")

    # Register with detailed semantic tags
    await router.register_subscriber(
        subscriber_id="workflow_orchestrator_1",
        event_pattern="workflow.*",
        handler=workflow_orchestrator.handle_workflow_event,
        capabilities={
            "domains": ["workflow", "orchestration", "process"],
            "max_concurrent": 5,
            "avg_processing_time_ms": 700,
            "sla_ms": 2000,
            "semantic_tags": [
                "workflow", "orchestration", "process", "stage",
                "transition", "automation", "execution"
            ]
        }
    )

    await router.register_subscriber(
        subscriber_id="risk_analyzer_1",
        event_pattern="risk.*",
        handler=risk_analyzer.handle_risk_event,
        capabilities={
            "domains": ["risk", "security", "threat"],
            "max_concurrent": 5,
            "avg_processing_time_ms": 300,
            "sla_ms": 1000,
            "semantic_tags": [
                "risk", "threat", "vulnerability", "security",
                "assessment", "analysis", "mitigation"
            ]
        }
    )

    await router.register_subscriber(
        subscriber_id="compliance_checker_1",
        event_pattern="compliance.*",
        handler=compliance_checker.handle_compliance_event,
        capabilities={
            "domains": ["compliance", "audit", "standards"],
            "max_concurrent": 10,
            "avg_processing_time_ms": 200,
            "sla_ms": 500,
            "semantic_tags": [
                "compliance", "audit", "standard", "regulation",
                "ISO22301", "certification", "requirements"
            ]
        }
    )

    # Publish semantically diverse events
    events = [
        Event.create(
            event_type="workflow.stage_changed",
            data={
                "workflow_id": "wf_001",
                "old_stage": "analysis",
                "new_stage": "execution",
                "description": "BIA workflow moved to execution phase"
            },
            source="workflow-engine",
            tenant_id="tenant_123",
            priority=EventPriority.NORMAL
        ),
        Event.create(
            event_type="risk.vulnerability_detected",
            data={
                "vulnerability_id": "CVE-2024-1234",
                "severity": "high",
                "description": "SQL injection vulnerability in web application"
            },
            source="security-scanner",
            tenant_id="tenant_123",
            priority=EventPriority.HIGH
        ),
        Event.create(
            event_type="compliance.certification_review",
            data={
                "standard": "ISO 22301",
                "review_type": "annual",
                "description": "Annual compliance certification review required"
            },
            source="compliance-service",
            tenant_id="tenant_123",
            priority=EventPriority.NORMAL
        )
    ]

    # Route events and show semantic matching
    logger.info("Routing events with semantic matching...\n")

    for event in events:
        decision = await router.route_event(event)
        logger.info(
            f"Event type: {event.type}\n"
            f"  Matched subscriber: {decision.selected_subscribers}\n"
            f"  Confidence: {decision.confidence_score:.2%}\n"
            f"  Strategy: {decision.routing_strategy}\n"
        )

    # Wait for processing
    await asyncio.sleep(2)

    # Show subscriber performance
    metrics = router.get_metrics()
    logger.info("-"*70)
    logger.info("SUBSCRIBER PERFORMANCE:")

    for sub_id, sub_metrics in metrics['subscriber_metrics'].items():
        logger.info(
            f"\n{sub_id}:"
            f"\n  Success rate: {sub_metrics['success_rate']:.2%}"
            f"\n  Avg latency: {sub_metrics['avg_latency_ms']:.2f}ms"
            f"\n  Status: {sub_metrics['status']}"
        )

    # Shutdown
    await router.shutdown()

    logger.info("\nScenario 4 complete!\n")


async def scenario_5_circuit_breaker():
    """
    Scenario 5: Circuit Breaker Pattern

    Demonstrates:
    - Automatic failure detection
    - Circuit breaker activation
    - Fallback routing
    """
    logger.info("\n" + "="*70)
    logger.info("SCENARIO 5: Circuit Breaker & Fault Tolerance")
    logger.info("="*70 + "\n")

    # Create eventbus and router with circuit breaker
    eventbus = InMemoryEventBus()
    router = IntelligentEventRouter(
        base_eventbus=eventbus,
        enable_ai_analysis=True,
        enable_semantic_matching=True,
        circuit_breaker_threshold=3,  # Open after 3 failures
        circuit_breaker_timeout_seconds=5  # 5 second timeout
    )

    await router.initialize()

    # Create a failing subscriber
    class FailingSubscriber:
        def __init__(self, name: str):
            self.name = name
            self.call_count = 0

        async def handle_event(self, event: Event):
            self.call_count += 1
            logger.warning(f"[{self.name}] Attempt #{self.call_count} - FAILING")
            # Simulate failure
            raise Exception(f"Simulated failure in {self.name}")

    # Create working and failing subscribers
    failing_sub = FailingSubscriber("FailingSubscriber")
    working_sub = RiskAnalyzerSubscriber("WorkingSubscriber", processing_time=0.2)

    # Register both
    await router.register_subscriber(
        subscriber_id="failing_subscriber",
        event_pattern="test.*",
        handler=failing_sub.handle_event,
        capabilities={
            "domains": ["test"],
            "max_concurrent": 5,
            "avg_processing_time_ms": 100,
            "sla_ms": 500
        }
    )

    await router.register_subscriber(
        subscriber_id="working_subscriber",
        event_pattern="test.*",
        handler=working_sub.handle_risk_event,
        capabilities={
            "domains": ["test"],
            "max_concurrent": 5,
            "avg_processing_time_ms": 200,
            "sla_ms": 1000
        }
    )

    # Publish events to trigger circuit breaker
    logger.info("Publishing events to trigger circuit breaker...\n")

    for i in range(6):
        event = Event.create(
            event_type="test.event",
            data={"test_id": i},
            source="test-system",
            tenant_id="tenant_123",
            priority=EventPriority.NORMAL
        )

        await router.route_event(event)
        await asyncio.sleep(0.5)

        # Check subscriber status
        failing_metrics = router.get_subscriber_metrics("failing_subscriber")
        if failing_metrics:
            logger.info(
                f"Failing subscriber status: {failing_metrics['status']}, "
                f"consecutive failures: {failing_metrics['consecutive_failures']}"
            )

    # Wait for processing
    await asyncio.sleep(2)

    # Show final metrics
    metrics = router.get_metrics()
    logger.info("\n" + "-"*70)
    logger.info("CIRCUIT BREAKER METRICS:")

    for sub_id in ["failing_subscriber", "working_subscriber"]:
        sub_metrics = router.get_subscriber_metrics(sub_id)
        if sub_metrics:
            logger.info(
                f"\n{sub_id}:"
                f"\n  Status: {sub_metrics['status']}"
                f"\n  Success rate: {sub_metrics['success_rate']:.2%}"
                f"\n  Consecutive failures: {sub_metrics['consecutive_failures']}"
                f"\n  Total errors: {sub_metrics['total_errors']}"
            )

    # Shutdown
    await router.shutdown()

    logger.info("\nScenario 5 complete!\n")


# ============================================================================
# Main
# ============================================================================

async def main():
    """Run all example scenarios"""
    logger.info("\n" + "="*70)
    logger.info("INTELLIGENT EVENT ROUTER - COMPREHENSIVE EXAMPLES")
    logger.info("="*70 + "\n")

    try:
        # Run all scenarios
        await scenario_1_basic_routing()
        await scenario_2_load_balancing()
        await scenario_3_priority_handling()
        await scenario_4_semantic_matching()
        await scenario_5_circuit_breaker()

        logger.info("\n" + "="*70)
        logger.info("ALL SCENARIOS COMPLETED SUCCESSFULLY!")
        logger.info("="*70 + "\n")

    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
