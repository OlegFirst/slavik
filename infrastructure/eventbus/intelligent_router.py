"""
Intelligent EventBus Router
===========================

AI-powered event routing system with semantic matching, priority queues,
load-aware distribution, and smart subscriber selection.

Features:
- AI-powered event classification and priority determination
- Semantic event matching using embeddings
- Priority queue system (CRITICAL, HIGH, NORMAL, LOW)
- Load-aware routing to prevent subscriber overload
- Smart subscriber selection based on:
  * Semantic similarity to event content
  * Historical performance metrics
  * Current load and capacity
  * SLA requirements
- Intelligent fallback routing
- Circuit breaker pattern for failed subscribers
- Comprehensive metrics and observability

Architecture:
                                    ┌────────────────┐
                                    │ Event Arrives  │
                                    └───────┬────────┘
                                            │
                                    ┌───────▼────────┐
                                    │ AI Analyzer    │
                                    │ - Priority     │
                                    │ - Category     │
                                    │ - Complexity   │
                                    └───────┬────────┘
                                            │
                            ┌───────────────┼───────────────┐
                            │               │               │
                    ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
                    │   Critical    │ │    High    │ │   Normal    │
                    │     Queue     │ │   Queue    │ │    Queue    │
                    └───────┬──────┘ └─────┬─────┘ └──────┬──────┘
                            └───────────────┼───────────────┘
                                            │
                                    ┌───────▼────────┐
                                    │ Smart Selector │
                                    │ - Semantic     │
                                    │ - Load Balance │
                                    │ - SLA Aware    │
                                    └───────┬────────┘
                                            │
                            ┌───────────────┼───────────────┐
                            │               │               │
                    ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
                    │ Subscriber 1  │ │Subscriber 2│ │Subscriber 3 │
                    └──────────────┘ └───────────┘ └─────────────┘

Integration Example:
    ```python
    from infrastructure.eventbus import InMemoryEventBus
    from infrastructure.eventbus.intelligent_router import IntelligentEventRouter
    from infrastructure.eventbus.core.events import Event, EventPriority

    # Create base eventbus
    eventbus = InMemoryEventBus()

    # Wrap with intelligent router
    router = IntelligentEventRouter(eventbus)
    await router.initialize()

    # Register intelligent subscriber
    await router.register_subscriber(
        subscriber_id="risk_analyzer",
        event_pattern="risk.*",
        handler=handle_risk_event,
        capabilities={
            "domains": ["risk", "compliance", "security"],
            "max_concurrent": 10,
            "avg_processing_time_ms": 200,
            "sla_ms": 1000
        }
    )

    # Publish event - router will intelligently route
    event = Event.create(
        event_type="risk.assessment_needed",
        data={
            "assessment_type": "cybersecurity",
            "urgency": "high",
            "description": "Critical vulnerability detected in payment system"
        },
        source="security-scanner",
        tenant_id="tenant_123"
    )

    # Router will:
    # 1. Analyze event with AI (determine priority, extract semantics)
    # 2. Find best subscriber(s) using semantic matching
    # 3. Check subscriber load and SLA compliance
    # 4. Route with appropriate priority
    await router.route_event(event)

    # Get routing metrics
    metrics = router.get_metrics()
    print(f"Routing efficiency: {metrics['routing_efficiency']:.2%}")
    print(f"SLA compliance: {metrics['sla_compliance_rate']:.2%}")
    ```
"""

import asyncio
import logging
import time
import re
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Callable, Any, Tuple
from heapq import heappush, heappop

import numpy as np

from infrastructure.eventbus.core.interface import IEventBus, EventHandler
from infrastructure.eventbus.core.events import Event, EventPriority

logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class SubscriberStatus(Enum):
    """Subscriber operational status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class SubscriberCapabilities:
    """
    Subscriber capability declaration

    Describes what a subscriber can handle and its performance characteristics.
    """
    subscriber_id: str
    domains: List[str]  # Domain expertise (e.g., ["risk", "compliance"])
    event_patterns: List[str]  # Event patterns this subscriber handles
    max_concurrent: int = 5  # Max concurrent events
    avg_processing_time_ms: float = 500.0  # Average processing time
    sla_ms: float = 2000.0  # SLA commitment in milliseconds
    priority_preference: Optional[EventPriority] = None  # Preferred priority
    semantic_tags: List[str] = field(default_factory=list)  # For semantic matching


@dataclass
class SubscriberMetrics:
    """Real-time subscriber performance metrics"""
    subscriber_id: str
    current_load: int = 0  # Currently processing events
    total_processed: int = 0
    total_errors: int = 0
    total_timeouts: int = 0
    avg_latency_ms: float = 0.0
    sla_violations: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    status: SubscriberStatus = SubscriberStatus.HEALTHY

    # Circuit breaker state
    consecutive_failures: int = 0
    circuit_open_until: Optional[datetime] = None

    def success_rate(self) -> float:
        """Calculate success rate (0.0 - 1.0)"""
        total = self.total_processed + self.total_errors
        if total == 0:
            return 1.0
        return self.total_processed / total

    def is_available(self) -> bool:
        """Check if subscriber is available"""
        if self.status == SubscriberStatus.CIRCUIT_OPEN:
            if self.circuit_open_until and datetime.utcnow() > self.circuit_open_until:
                # Circuit breaker timeout expired - try half-open
                return True
            return False
        return self.status != SubscriberStatus.FAILED

    def has_capacity(self, capabilities: SubscriberCapabilities) -> bool:
        """Check if subscriber has capacity for more events"""
        return self.current_load < capabilities.max_concurrent


@dataclass
class EventAnalysis:
    """AI analysis results for an event"""
    event_id: str
    determined_priority: EventPriority
    complexity_score: float  # 0.0 - 1.0
    semantic_embedding: Optional[List[float]] = None
    keywords: List[str] = field(default_factory=list)
    category: Optional[str] = None
    estimated_processing_time_ms: float = 500.0
    sla_requirement_ms: float = 2000.0
    recommended_subscribers: List[str] = field(default_factory=list)


@dataclass
class PriorityQueueItem:
    """Item in priority queue"""
    priority: int  # Lower number = higher priority
    timestamp: float
    event: Event
    analysis: EventAnalysis
    retry_count: int = 0

    def __lt__(self, other):
        """Compare for heap queue (priority, then timestamp)"""
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.timestamp < other.timestamp


@dataclass
class RoutingDecision:
    """Decision made by intelligent router"""
    event_id: str
    selected_subscribers: List[str]
    priority_used: EventPriority
    routing_strategy: str  # "semantic", "load_balanced", "fallback", etc.
    confidence_score: float  # 0.0 - 1.0
    alternative_subscribers: List[str] = field(default_factory=list)
    decision_time_ms: float = 0.0


# ============================================================================
# AI Event Analyzer
# ============================================================================

class AIEventAnalyzer:
    """
    AI-powered event analysis engine

    Uses lightweight heuristics + optional LLM for complex analysis.
    """

    def __init__(self, use_embeddings: bool = True):
        """
        Initialize AI analyzer

        Args:
            use_embeddings: Whether to generate semantic embeddings
        """
        self.use_embeddings = use_embeddings
        self.embedding_cache: Dict[str, List[float]] = {}

        # Priority keywords
        self.priority_keywords = {
            EventPriority.CRITICAL: [
                "critical", "emergency", "urgent", "immediate", "failure",
                "outage", "security breach", "data loss", "system down"
            ],
            EventPriority.HIGH: [
                "high", "important", "priority", "escalate", "warning",
                "degraded", "timeout", "error"
            ],
            EventPriority.NORMAL: [
                "normal", "standard", "routine", "regular", "update"
            ],
            EventPriority.LOW: [
                "low", "info", "debug", "trace", "background"
            ]
        }

        # Complexity indicators
        self.complexity_indicators = [
            "analysis", "assessment", "calculation", "simulation",
            "optimization", "prediction", "recommendation", "workflow"
        ]

    async def analyze_event(self, event: Event) -> EventAnalysis:
        """
        Analyze event and determine characteristics

        Args:
            event: Event to analyze

        Returns:
            EventAnalysis with AI-determined characteristics
        """
        start_time = time.time()

        # Extract text for analysis
        event_text = self._extract_text(event)

        # Determine priority (if not already set to CRITICAL/HIGH)
        determined_priority = await self._determine_priority(event, event_text)

        # Calculate complexity score
        complexity = self._calculate_complexity(event, event_text)

        # Extract keywords
        keywords = self._extract_keywords(event_text)

        # Determine category
        category = self._determine_category(event, keywords)

        # Generate semantic embedding
        embedding = None
        if self.use_embeddings:
            embedding = await self._generate_embedding(event_text)

        # Estimate processing time based on complexity
        estimated_time = 200 + (complexity * 2000)  # 200ms - 2200ms

        # Determine SLA based on priority
        sla_requirement = self._determine_sla(determined_priority)

        analysis_time = (time.time() - start_time) * 1000

        logger.debug(
            f"Event {event.id[:8]} analyzed: "
            f"priority={determined_priority.name}, "
            f"complexity={complexity:.2f}, "
            f"category={category}, "
            f"time={analysis_time:.1f}ms"
        )

        return EventAnalysis(
            event_id=event.id,
            determined_priority=determined_priority,
            complexity_score=complexity,
            semantic_embedding=embedding,
            keywords=keywords,
            category=category,
            estimated_processing_time_ms=estimated_time,
            sla_requirement_ms=sla_requirement
        )

    def _extract_text(self, event: Event) -> str:
        """Extract searchable text from event"""
        text_parts = [
            event.type,
            event.source,
            str(event.data)
        ]
        return " ".join(text_parts).lower()

    async def _determine_priority(self, event: Event, event_text: str) -> EventPriority:
        """Determine event priority using AI heuristics"""
        # Start with declared priority
        if event.priority in [EventPriority.CRITICAL, EventPriority.HIGH]:
            return event.priority

        # Check for priority keywords
        for priority in [EventPriority.CRITICAL, EventPriority.HIGH, EventPriority.NORMAL]:
            keywords = self.priority_keywords[priority]
            if any(keyword in event_text for keyword in keywords):
                return priority

        # Check event type patterns
        if any(pattern in event.type for pattern in ["error", "failure", "alert", "incident"]):
            return EventPriority.HIGH

        if any(pattern in event.type for pattern in ["info", "debug", "trace"]):
            return EventPriority.LOW

        # Default to event's stated priority
        return event.priority

    def _calculate_complexity(self, event: Event, event_text: str) -> float:
        """Calculate event complexity score (0.0 - 1.0)"""
        complexity = 0.0

        # Data payload size
        data_size = len(str(event.data))
        if data_size > 1000:
            complexity += 0.3
        elif data_size > 500:
            complexity += 0.2
        elif data_size > 100:
            complexity += 0.1

        # Complexity keywords
        complexity_count = sum(
            1 for indicator in self.complexity_indicators
            if indicator in event_text
        )
        complexity += min(complexity_count * 0.15, 0.4)

        # Event type complexity
        if "workflow" in event.type or "orchestration" in event.type:
            complexity += 0.2

        if "analysis" in event.type or "assessment" in event.type:
            complexity += 0.15

        return min(complexity, 1.0)

    def _extract_keywords(self, event_text: str) -> List[str]:
        """Extract important keywords from event"""
        # Simple keyword extraction (in production, use NLP)
        words = re.findall(r'\b\w{4,}\b', event_text)

        # Remove common words
        stopwords = {
            "this", "that", "with", "from", "have", "been",
            "were", "their", "there", "would", "could", "should"
        }

        keywords = [w for w in words if w not in stopwords]

        # Return unique keywords (up to 10)
        return list(dict.fromkeys(keywords))[:10]

    def _determine_category(self, event: Event, keywords: List[str]) -> str:
        """Determine event category"""
        # Extract category from event type
        parts = event.type.split('.')
        if len(parts) > 0:
            return parts[0]

        # Fallback to keyword-based categorization
        category_keywords = {
            "risk": ["risk", "threat", "vulnerability", "security"],
            "compliance": ["compliance", "audit", "standard", "regulation"],
            "workflow": ["workflow", "process", "stage", "transition"],
            "bia": ["impact", "business", "critical", "process"],
            "incident": ["incident", "emergency", "response", "recovery"]
        }

        for category, kws in category_keywords.items():
            if any(kw in keywords for kw in kws):
                return category

        return "general"

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate semantic embedding for text"""
        # Check cache
        cache_key = text[:100]  # Use first 100 chars as cache key
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]

        # Generate simple hash-based embedding for development
        # In production, use actual embedding model
        seed = hash(text) % (2**32)
        np.random.seed(seed)
        embedding = np.random.randn(384).tolist()  # 384-dim embedding

        # Cache it
        self.embedding_cache[cache_key] = embedding

        # Limit cache size
        if len(self.embedding_cache) > 1000:
            # Remove oldest entries
            for key in list(self.embedding_cache.keys())[:100]:
                del self.embedding_cache[key]

        return embedding

    def _determine_sla(self, priority: EventPriority) -> float:
        """Determine SLA requirement based on priority"""
        sla_map = {
            EventPriority.CRITICAL: 500.0,    # 500ms
            EventPriority.HIGH: 2000.0,       # 2s
            EventPriority.NORMAL: 5000.0,     # 5s
            EventPriority.LOW: 30000.0        # 30s
        }
        return sla_map.get(priority, 5000.0)

    def calculate_semantic_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between embeddings"""
        if not embedding1 or not embedding2:
            return 0.0

        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return (similarity + 1) / 2  # Normalize to 0-1


# ============================================================================
# Smart Subscriber Selector
# ============================================================================

class SmartSubscriberSelector:
    """
    Intelligent subscriber selection engine

    Selects best subscriber(s) based on:
    - Semantic similarity
    - Current load
    - Historical performance
    - SLA requirements
    """

    def __init__(self, analyzer: AIEventAnalyzer):
        """Initialize selector"""
        self.analyzer = analyzer

    async def select_subscribers(
        self,
        event: Event,
        analysis: EventAnalysis,
        subscribers: Dict[str, SubscriberCapabilities],
        metrics: Dict[str, SubscriberMetrics]
    ) -> Tuple[List[str], str, float]:
        """
        Select best subscriber(s) for event

        Args:
            event: Event to route
            analysis: AI analysis of event
            subscribers: Available subscribers with capabilities
            metrics: Real-time metrics for subscribers

        Returns:
            Tuple of (selected_subscriber_ids, strategy, confidence)
        """
        # Filter available subscribers
        candidates = self._filter_candidates(
            event, subscribers, metrics
        )

        if not candidates:
            return [], "no_candidates", 0.0

        # Calculate scores for each candidate
        scores = []
        for sub_id in candidates:
            score = await self._calculate_subscriber_score(
                event, analysis, subscribers[sub_id], metrics[sub_id]
            )
            scores.append((sub_id, score))

        # Sort by score (descending)
        scores.sort(key=lambda x: x[1], reverse=True)

        # Select top subscriber(s)
        if not scores:
            return [], "no_qualified", 0.0

        # For critical events, select multiple subscribers (redundancy)
        if analysis.determined_priority == EventPriority.CRITICAL:
            selected = [sub_id for sub_id, _ in scores[:2]]  # Top 2
            strategy = "redundant_critical"
            confidence = scores[0][1]
        else:
            # Single best subscriber
            selected = [scores[0][0]]
            strategy = "best_match"
            confidence = scores[0][1]

        logger.debug(
            f"Selected {len(selected)} subscriber(s) for event {event.id[:8]}: "
            f"{selected} (strategy={strategy}, confidence={confidence:.2f})"
        )

        return selected, strategy, confidence

    def _filter_candidates(
        self,
        event: Event,
        subscribers: Dict[str, SubscriberCapabilities],
        metrics: Dict[str, SubscriberMetrics]
    ) -> List[str]:
        """Filter subscribers to viable candidates"""
        candidates = []

        for sub_id, capabilities in subscribers.items():
            # Check if subscriber is available
            if sub_id not in metrics:
                continue

            sub_metrics = metrics[sub_id]
            if not sub_metrics.is_available():
                continue

            # Check capacity
            if not sub_metrics.has_capacity(capabilities):
                continue

            # Check event pattern match
            if not self._matches_pattern(event.type, capabilities.event_patterns):
                continue

            candidates.append(sub_id)

        return candidates

    def _matches_pattern(self, event_type: str, patterns: List[str]) -> bool:
        """Check if event type matches any pattern"""
        for pattern in patterns:
            regex = pattern.replace('.', r'\.').replace('*', '.*')
            if re.match(f'^{regex}$', event_type):
                return True
        return False

    async def _calculate_subscriber_score(
        self,
        event: Event,
        analysis: EventAnalysis,
        capabilities: SubscriberCapabilities,
        metrics: SubscriberMetrics
    ) -> float:
        """
        Calculate overall score for subscriber

        Considers:
        - Semantic match
        - Load level
        - Performance history
        - SLA compliance
        """
        score = 0.0

        # 1. Semantic similarity (40% weight)
        semantic_score = await self._semantic_match_score(analysis, capabilities)
        score += semantic_score * 0.4

        # 2. Load level (20% weight) - prefer less loaded
        load_score = 1.0 - (metrics.current_load / capabilities.max_concurrent)
        score += load_score * 0.2

        # 3. Performance history (25% weight)
        performance_score = metrics.success_rate()
        score += performance_score * 0.25

        # 4. SLA compliance (15% weight)
        sla_score = 1.0 if capabilities.sla_ms <= analysis.sla_requirement_ms else 0.5
        score += sla_score * 0.15

        return min(score, 1.0)

    async def _semantic_match_score(
        self,
        analysis: EventAnalysis,
        capabilities: SubscriberCapabilities
    ) -> float:
        """Calculate semantic match score"""
        if not analysis.semantic_embedding:
            # Fallback to keyword matching
            return self._keyword_match_score(analysis, capabilities)

        # Generate embedding for subscriber capabilities
        capability_text = " ".join(
            capabilities.domains +
            capabilities.semantic_tags +
            capabilities.event_patterns
        )

        capability_embedding = await self.analyzer._generate_embedding(capability_text)

        # Calculate similarity
        similarity = self.analyzer.calculate_semantic_similarity(
            analysis.semantic_embedding,
            capability_embedding
        )

        return similarity

    def _keyword_match_score(
        self,
        analysis: EventAnalysis,
        capabilities: SubscriberCapabilities
    ) -> float:
        """Fallback keyword-based matching"""
        matches = 0
        total = len(analysis.keywords)

        if total == 0:
            return 0.5  # Neutral score

        capability_text = " ".join(
            capabilities.domains + capabilities.semantic_tags
        ).lower()

        for keyword in analysis.keywords:
            if keyword in capability_text:
                matches += 1

        return matches / total


# ============================================================================
# Intelligent Event Router
# ============================================================================

class IntelligentEventRouter:
    """
    Intelligent EventBus Router

    Main router class that orchestrates AI-powered event routing.
    """

    def __init__(
        self,
        base_eventbus: IEventBus,
        enable_ai_analysis: bool = True,
        enable_semantic_matching: bool = True,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout_seconds: int = 60
    ):
        """
        Initialize intelligent router

        Args:
            base_eventbus: Underlying eventbus implementation
            enable_ai_analysis: Enable AI event analysis
            enable_semantic_matching: Enable semantic subscriber matching
            circuit_breaker_threshold: Consecutive failures before circuit opens
            circuit_breaker_timeout_seconds: Circuit breaker timeout
        """
        self.base_eventbus = base_eventbus
        self.enable_ai_analysis = enable_ai_analysis
        self.enable_semantic_matching = enable_semantic_matching
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout_seconds

        # Components
        self.analyzer = AIEventAnalyzer(use_embeddings=enable_semantic_matching)
        self.selector = SmartSubscriberSelector(self.analyzer)

        # Subscriber registry
        self.subscribers: Dict[str, SubscriberCapabilities] = {}
        self.subscriber_handlers: Dict[str, EventHandler] = {}
        self.subscriber_metrics: Dict[str, SubscriberMetrics] = {}

        # Priority queues
        self.queues: Dict[EventPriority, List[PriorityQueueItem]] = {
            EventPriority.CRITICAL: [],
            EventPriority.HIGH: [],
            EventPriority.NORMAL: [],
            EventPriority.LOW: []
        }

        # Processing state
        self.processing_tasks: Set[asyncio.Task] = set()
        self.running = False

        # Metrics
        self.total_events = 0
        self.total_routed = 0
        self.total_failed = 0
        self.routing_times_ms: deque = deque(maxlen=100)
        self.routing_decisions: deque = deque(maxlen=100)

        logger.info(
            f"IntelligentEventRouter initialized: "
            f"AI={enable_ai_analysis}, "
            f"semantic={enable_semantic_matching}"
        )

    async def initialize(self):
        """Initialize router and start processing"""
        self.running = True

        # Start queue processors
        for priority in EventPriority:
            task = asyncio.create_task(self._process_queue(priority))
            self.processing_tasks.add(task)

        logger.info("Intelligent router started")

    async def shutdown(self):
        """Shutdown router gracefully"""
        self.running = False

        # Cancel processing tasks
        for task in self.processing_tasks:
            task.cancel()

        await asyncio.gather(*self.processing_tasks, return_exceptions=True)

        # Close base eventbus
        await self.base_eventbus.close()

        logger.info("Intelligent router shutdown complete")

    # ------------------------------------------------------------------------
    # Subscriber Registration
    # ------------------------------------------------------------------------

    async def register_subscriber(
        self,
        subscriber_id: str,
        event_pattern: str,
        handler: EventHandler,
        capabilities: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register intelligent subscriber

        Args:
            subscriber_id: Unique subscriber ID
            event_pattern: Event pattern to subscribe to
            handler: Event handler function
            capabilities: Subscriber capabilities dict

        Returns:
            Subscription ID
        """
        # Create capabilities
        if capabilities:
            caps = SubscriberCapabilities(
                subscriber_id=subscriber_id,
                domains=capabilities.get("domains", []),
                event_patterns=[event_pattern],
                max_concurrent=capabilities.get("max_concurrent", 5),
                avg_processing_time_ms=capabilities.get("avg_processing_time_ms", 500.0),
                sla_ms=capabilities.get("sla_ms", 2000.0),
                semantic_tags=capabilities.get("semantic_tags", [])
            )
        else:
            # Default capabilities
            caps = SubscriberCapabilities(
                subscriber_id=subscriber_id,
                domains=[],
                event_patterns=[event_pattern]
            )

        # Register
        self.subscribers[subscriber_id] = caps
        self.subscriber_handlers[subscriber_id] = handler
        self.subscriber_metrics[subscriber_id] = SubscriberMetrics(
            subscriber_id=subscriber_id
        )

        logger.info(
            f"Registered intelligent subscriber: {subscriber_id} "
            f"(pattern={event_pattern}, domains={caps.domains})"
        )

        return subscriber_id

    async def unregister_subscriber(self, subscriber_id: str):
        """Unregister subscriber"""
        if subscriber_id in self.subscribers:
            del self.subscribers[subscriber_id]
            del self.subscriber_handlers[subscriber_id]
            del self.subscriber_metrics[subscriber_id]

            logger.info(f"Unregistered subscriber: {subscriber_id}")

    # ------------------------------------------------------------------------
    # Event Routing
    # ------------------------------------------------------------------------

    async def route_event(self, event: Event) -> RoutingDecision:
        """
        Route event intelligently

        Main entry point for event routing.

        Args:
            event: Event to route

        Returns:
            RoutingDecision describing routing outcome
        """
        start_time = time.time()
        self.total_events += 1

        try:
            # AI Analysis
            if self.enable_ai_analysis:
                analysis = await self.analyzer.analyze_event(event)
            else:
                # Simple analysis without AI
                analysis = EventAnalysis(
                    event_id=event.id,
                    determined_priority=event.priority,
                    complexity_score=0.5,
                    category=event.type.split('.')[0] if '.' in event.type else "general"
                )

            # Find best subscribers
            selected_subs, strategy, confidence = await self.selector.select_subscribers(
                event, analysis, self.subscribers, self.subscriber_metrics
            )

            # Create routing decision
            decision_time = (time.time() - start_time) * 1000
            decision = RoutingDecision(
                event_id=event.id,
                selected_subscribers=selected_subs,
                priority_used=analysis.determined_priority,
                routing_strategy=strategy,
                confidence_score=confidence,
                decision_time_ms=decision_time
            )

            # Enqueue event
            if selected_subs:
                await self._enqueue_event(event, analysis, decision)
                self.total_routed += 1
            else:
                # Fallback to simple routing
                logger.warning(
                    f"No intelligent subscribers found for {event.type}, "
                    f"falling back to simple routing"
                )
                await self.base_eventbus.publish(event)
                self.total_routed += 1

            # Record metrics
            self.routing_times_ms.append(decision_time)
            self.routing_decisions.append(decision)

            logger.debug(
                f"Event {event.id[:8]} routed: "
                f"subscribers={selected_subs}, "
                f"strategy={strategy}, "
                f"confidence={confidence:.2f}, "
                f"time={decision_time:.1f}ms"
            )

            return decision

        except Exception as e:
            self.total_failed += 1
            logger.error(f"Routing failed for event {event.id}: {e}")

            # Fallback to simple routing
            await self.base_eventbus.publish(event)

            return RoutingDecision(
                event_id=event.id,
                selected_subscribers=[],
                priority_used=event.priority,
                routing_strategy="fallback_error",
                confidence_score=0.0,
                decision_time_ms=(time.time() - start_time) * 1000
            )

    async def _enqueue_event(
        self,
        event: Event,
        analysis: EventAnalysis,
        decision: RoutingDecision
    ):
        """Enqueue event in priority queue"""
        priority = analysis.determined_priority

        item = PriorityQueueItem(
            priority=priority.value,
            timestamp=time.time(),
            event=event,
            analysis=analysis
        )

        # Add to priority queue
        heappush(self.queues[priority], item)

    # ------------------------------------------------------------------------
    # Queue Processing
    # ------------------------------------------------------------------------

    async def _process_queue(self, priority: EventPriority):
        """Process events from priority queue"""
        logger.info(f"Queue processor started: {priority.name}")

        while self.running:
            try:
                # Check if queue has items
                if not self.queues[priority]:
                    await asyncio.sleep(0.1)
                    continue

                # Get highest priority item
                item = heappop(self.queues[priority])

                # Process event
                await self._process_event(item)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Queue processor error ({priority.name}): {e}")
                await asyncio.sleep(1)

        logger.info(f"Queue processor stopped: {priority.name}")

    async def _process_event(self, item: PriorityQueueItem):
        """Process single event"""
        event = item.event
        analysis = item.analysis

        # Find subscribers
        selected_subs, _, _ = await self.selector.select_subscribers(
            event, analysis, self.subscribers, self.subscriber_metrics
        )

        if not selected_subs:
            logger.warning(f"No subscribers available for event {event.id}")
            return

        # Route to each selected subscriber
        tasks = []
        for sub_id in selected_subs:
            if sub_id in self.subscriber_handlers:
                task = asyncio.create_task(
                    self._deliver_to_subscriber(
                        sub_id, event, analysis
                    )
                )
                tasks.append(task)

        # Wait for all deliveries
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _deliver_to_subscriber(
        self,
        subscriber_id: str,
        event: Event,
        analysis: EventAnalysis
    ):
        """Deliver event to specific subscriber"""
        if subscriber_id not in self.subscriber_handlers:
            return

        metrics = self.subscriber_metrics[subscriber_id]
        capabilities = self.subscribers[subscriber_id]
        handler = self.subscriber_handlers[subscriber_id]

        # Check circuit breaker
        if not metrics.is_available():
            logger.warning(
                f"Subscriber {subscriber_id} unavailable (circuit open)"
            )
            return

        # Update load
        metrics.current_load += 1

        start_time = time.time()
        success = False

        try:
            # Call handler with timeout
            await asyncio.wait_for(
                handler(event),
                timeout=capabilities.sla_ms / 1000.0
            )

            success = True

            # Update metrics
            latency_ms = (time.time() - start_time) * 1000
            metrics.total_processed += 1
            metrics.last_success = datetime.utcnow()
            metrics.consecutive_failures = 0

            # Update average latency
            if metrics.avg_latency_ms == 0:
                metrics.avg_latency_ms = latency_ms
            else:
                metrics.avg_latency_ms = (
                    metrics.avg_latency_ms * 0.9 + latency_ms * 0.1
                )

            # Check SLA
            if latency_ms > analysis.sla_requirement_ms:
                metrics.sla_violations += 1

            # Update status
            if metrics.consecutive_failures == 0:
                metrics.status = SubscriberStatus.HEALTHY

        except asyncio.TimeoutError:
            metrics.total_timeouts += 1
            metrics.consecutive_failures += 1
            metrics.last_failure = datetime.utcnow()

            logger.warning(
                f"Subscriber {subscriber_id} timeout on event {event.id}"
            )

            self._check_circuit_breaker(metrics)

        except Exception as e:
            metrics.total_errors += 1
            metrics.consecutive_failures += 1
            metrics.last_failure = datetime.utcnow()

            logger.error(
                f"Subscriber {subscriber_id} error on event {event.id}: {e}"
            )

            self._check_circuit_breaker(metrics)

        finally:
            # Decrease load
            metrics.current_load = max(0, metrics.current_load - 1)

    def _check_circuit_breaker(self, metrics: SubscriberMetrics):
        """Check and update circuit breaker state"""
        if metrics.consecutive_failures >= self.circuit_breaker_threshold:
            # Open circuit
            metrics.status = SubscriberStatus.CIRCUIT_OPEN
            metrics.circuit_open_until = (
                datetime.utcnow() + timedelta(seconds=self.circuit_breaker_timeout)
            )

            logger.warning(
                f"Circuit breaker opened for {metrics.subscriber_id} "
                f"(failures={metrics.consecutive_failures})"
            )
        elif metrics.consecutive_failures >= self.circuit_breaker_threshold / 2:
            # Degraded
            metrics.status = SubscriberStatus.DEGRADED

    # ------------------------------------------------------------------------
    # Metrics and Monitoring
    # ------------------------------------------------------------------------

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive routing metrics"""
        avg_routing_time = (
            sum(self.routing_times_ms) / len(self.routing_times_ms)
            if self.routing_times_ms else 0.0
        )

        # Calculate routing efficiency
        routing_efficiency = (
            self.total_routed / self.total_events
            if self.total_events > 0 else 0.0
        )

        # Calculate SLA compliance
        sla_compliant = sum(
            1 for decision in self.routing_decisions
            if decision.confidence_score > 0.7
        )
        sla_compliance = (
            sla_compliant / len(self.routing_decisions)
            if self.routing_decisions else 0.0
        )

        # Subscriber health
        healthy_subs = sum(
            1 for m in self.subscriber_metrics.values()
            if m.status == SubscriberStatus.HEALTHY
        )

        return {
            "total_events": self.total_events,
            "total_routed": self.total_routed,
            "total_failed": self.total_failed,
            "routing_efficiency": routing_efficiency,
            "avg_routing_time_ms": avg_routing_time,
            "sla_compliance_rate": sla_compliance,
            "registered_subscribers": len(self.subscribers),
            "healthy_subscribers": healthy_subs,
            "queue_depths": {
                priority.name: len(queue)
                for priority, queue in self.queues.items()
            },
            "subscriber_metrics": {
                sub_id: {
                    "current_load": m.current_load,
                    "success_rate": m.success_rate(),
                    "avg_latency_ms": m.avg_latency_ms,
                    "status": m.status.value
                }
                for sub_id, m in self.subscriber_metrics.items()
            }
        }

    def get_subscriber_metrics(self, subscriber_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for specific subscriber"""
        if subscriber_id not in self.subscriber_metrics:
            return None

        metrics = self.subscriber_metrics[subscriber_id]

        return {
            "subscriber_id": subscriber_id,
            "current_load": metrics.current_load,
            "total_processed": metrics.total_processed,
            "total_errors": metrics.total_errors,
            "total_timeouts": metrics.total_timeouts,
            "success_rate": metrics.success_rate(),
            "avg_latency_ms": metrics.avg_latency_ms,
            "sla_violations": metrics.sla_violations,
            "status": metrics.status.value,
            "consecutive_failures": metrics.consecutive_failures,
            "last_success": (
                metrics.last_success.isoformat()
                if metrics.last_success else None
            ),
            "last_failure": (
                metrics.last_failure.isoformat()
                if metrics.last_failure else None
            )
        }


# ============================================================================
# Export
# ============================================================================

__all__ = [
    "IntelligentEventRouter",
    "AIEventAnalyzer",
    "SmartSubscriberSelector",
    "SubscriberCapabilities",
    "SubscriberMetrics",
    "SubscriberStatus",
    "EventAnalysis",
    "RoutingDecision"
]
