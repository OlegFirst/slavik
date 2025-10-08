"""
EventBus Subscribers for Reactive Learning

This module implements comprehensive event-driven learning by subscribing to
platform events and triggering automatic ML updates, pattern detection, and
knowledge base enrichment.

Architecture:
- Subscribes to 10+ event types from across the platform
- Triggers reactive learning in response to real-world platform usage
- Updates ML models, competency tracking, knowledge graphs automatically
- Enables true "platform that learns from itself" behavior

Event Sources:
- Community Intelligence (case.*, review.*)
- Workflow Intelligence (workflow.*)
- BIA Engine (bia.*)
- Incident Management (incident.*)

Learning Actions:
- ML model retraining with new data
- Pattern detection from event streams
- Knowledge graph updates
- Competency model adjustments
- Vector DB indexing
"""

import logging
from typing import Dict, Any
from datetime import datetime
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import learning engines
from learning.engines.self_learning_engine import SelfLearningEngine
from learning.engines.pattern_detector import PatternDetector
from learning.engines.ml_predictor import ExerciseSuccessPredictor
from learning.engines.competency_tracker import CompetencyTracker
from knowledge.indexer.vector_indexer import VectorIndexer
from knowledge.loader.case_loader import CaseCollector

# Import EventBus
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
    from shared.eventbus import EventBusClient, get_eventbus
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False
    EventBusClient = None

logger = logging.getLogger(__name__)


class LearningEventSubscriber:
    """
    Centralized event subscriber for reactive learning

    Manages all event subscriptions and coordinates learning actions
    across different platform events.
    """

    def __init__(
        self,
        eventbus: EventBusClient,
        self_learning_engine: SelfLearningEngine,
        pattern_detector: PatternDetector,
        competency_tracker: CompetencyTracker,
        vector_indexer: VectorIndexer = None,
        case_collector: CaseCollector = None
    ):
        """
        Initialize learning event subscriber

        Args:
            eventbus: EventBusClient instance
            self_learning_engine: ML self-learning engine
            pattern_detector: Pattern detection engine
            competency_tracker: Competency tracking engine
            vector_indexer: Vector indexer for knowledge base (optional)
            case_collector: Case collector for workflow cases (optional)
        """
        self.eventbus = eventbus
        self.self_learning = self_learning_engine
        self.pattern_detector = pattern_detector
        self.competency_tracker = competency_tracker
        self.vector_indexer = vector_indexer
        self.case_collector = case_collector

        # Statistics tracking
        self.events_processed = {
            'case_approved': 0,
            'case_rejected': 0,
            'review_submitted': 0,
            'workflow_completed': 0,
            'workflow_failed': 0,
            'workflow_milestone': 0,
            'bia_completed': 0,
            'bia_validated': 0,
            'incident_resolved': 0,
            'incident_pattern': 0,
            'exercise_completed': 0,
            'prediction_made': 0
        }

        logger.info("✅ LearningEventSubscriber initialized")

    # ========================================================================
    # COMMUNITY INTELLIGENCE EVENTS
    # ========================================================================

    async def handle_case_approved(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle case.approved event - Learn from approved workflow case

        Actions:
        1. Update ML model with new positive training example
        2. Index case into vector DB for similarity search
        3. Extract success patterns
        4. Update competency models
        """
        try:
            case_id = event_data.get('case_id')
            case_data = event_data.get('case_data', {})
            module = case_data.get('module', 'unknown')

            logger.info(f"📚 Learning from approved case: {case_id} (module={module})")

            # 1. Add to ML training dataset (positive example)
            features = self._extract_case_features(case_data)
            if features:
                self.self_learning.training_buffer.append({
                    'features': features,
                    'target': case_data.get('metrics', {}).get('success_score', 100),
                    'case_id': case_id,
                    'source': 'community_intelligence'
                })

                # Trigger model retraining if threshold reached
                if len(self.self_learning.training_buffer) >= self.self_learning.retrain_threshold:
                    self.self_learning._retrain_model()

            # 2. Index into vector DB for semantic search
            if self.vector_indexer and self.case_collector:
                try:
                    await self.vector_indexer.index_case(case_data)
                    logger.info(f"  ✅ Indexed case {case_id} into vector DB")
                except Exception as e:
                    logger.warning(f"  ⚠️ Failed to index case: {e}")

            # 3. Update competency models from successful case
            if 'competencies_demonstrated' in case_data:
                competencies = case_data['competencies_demonstrated']
                user_id = case_data.get('user_id', 'unknown')

                for competency, score in competencies.items():
                    await self.competency_tracker.update_competency(
                        user_id=user_id,
                        competency=competency,
                        score=score,
                        evidence_type='approved_case',
                        evidence_id=case_id
                    )

            self.events_processed['case_approved'] += 1
            logger.info(f"  ✅ Learned from approved case {case_id}")

        except Exception as e:
            logger.error(f"❌ Error handling case.approved: {e}", exc_info=True)

    async def handle_case_rejected(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle case.rejected event - Analyze rejection patterns

        Actions:
        1. Record as negative training example
        2. Detect rejection patterns
        3. Update quality filters
        """
        try:
            case_id = event_data.get('case_id')
            rejection_reasons = event_data.get('rejection_reasons', [])
            case_data = event_data.get('case_data', {})

            logger.info(f"🔍 Analyzing rejected case: {case_id}")

            # Add rejection pattern to analysis
            rejection_pattern = {
                'case_id': case_id,
                'module': case_data.get('module'),
                'reasons': rejection_reasons,
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': case_data.get('metadata', {})
            }

            # Store rejection for pattern analysis
            # This helps identify common quality issues
            if not hasattr(self, 'rejection_patterns'):
                self.rejection_patterns = []

            self.rejection_patterns.append(rejection_pattern)

            # Detect patterns if we have enough data
            if len(self.rejection_patterns) >= 10:
                patterns = await self._detect_rejection_patterns()
                if patterns:
                    logger.info(f"  🔍 Detected {len(patterns)} rejection patterns")
                    # TODO: Update quality filters, notify experts

            self.events_processed['case_rejected'] += 1
            logger.info(f"  ✅ Analyzed rejection for case {case_id}")

        except Exception as e:
            logger.error(f"❌ Error handling case.rejected: {e}", exc_info=True)

    async def handle_review_submitted(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle review.submitted event - Learn from peer feedback

        Actions:
        1. Extract quality signals from reviews
        2. Update recommendation algorithms
        3. Adjust case ranking models
        """
        try:
            review_id = event_data.get('review_id')
            case_id = event_data.get('case_id')
            rating = event_data.get('rating', 0)
            feedback = event_data.get('feedback', '')

            logger.info(f"💬 Learning from peer review: {review_id} (rating={rating})")

            # Use review as quality signal for ML
            # High ratings = good training examples
            # Low ratings = potentially problematic patterns

            quality_signal = {
                'case_id': case_id,
                'review_id': review_id,
                'rating': rating,
                'feedback': feedback,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Store for quality model training
            if not hasattr(self, 'quality_signals'):
                self.quality_signals = []

            self.quality_signals.append(quality_signal)

            # Update case quality scores
            # Cases with high peer ratings get boosted in recommendations
            if rating >= 4:  # High rating (assuming 1-5 scale)
                logger.info(f"  ⭐ High-quality case detected: {case_id}")
                # TODO: Boost in recommendation system

            self.events_processed['review_submitted'] += 1
            logger.info(f"  ✅ Learned from review {review_id}")

        except Exception as e:
            logger.error(f"❌ Error handling review.submitted: {e}", exc_info=True)

    # ========================================================================
    # WORKFLOW INTELLIGENCE EVENTS
    # ========================================================================

    async def handle_workflow_completed(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle workflow.completed event - Extract success patterns

        Actions:
        1. Record workflow outcome for pattern detection
        2. Update success prediction models
        3. Extract best practices
        4. Update knowledge base
        """
        try:
            workflow_id = event_data.get('workflow_id')
            module = event_data.get('module', 'unknown')
            context = event_data.get('context', {})
            metrics = context.get('metrics', {})

            logger.info(f"✅ Learning from completed workflow: {workflow_id} (module={module})")

            # Build workflow result for pattern detection
            workflow_result = {
                'workflow_id': workflow_id,
                'module': module,
                'outcome': 'success',
                'duration': metrics.get('duration_minutes', 0),
                'steps_completed': metrics.get('steps_completed', 0),
                'quality_score': metrics.get('quality_score', 0),
                'timestamp': datetime.utcnow().isoformat(),
                'context': context
            }

            # 1. Detect success patterns
            if not hasattr(self, 'workflow_results'):
                self.workflow_results = []

            self.workflow_results.append(workflow_result)

            # Detect patterns every 20 workflows
            if len(self.workflow_results) >= 20:
                patterns = self.pattern_detector.detect_patterns(self.workflow_results)

                if patterns:
                    logger.info(f"  🔍 Detected {len(patterns)} workflow patterns")

                    # TODO: Create knowledge articles from patterns
                    # TODO: Update best practice library

                # Clear buffer after pattern detection
                self.workflow_results = self.workflow_results[-50:]  # Keep last 50

            # 2. Update ML models for workflow prediction
            features = self._extract_workflow_features(context)
            if features:
                self.self_learning.training_buffer.append({
                    'features': features,
                    'target': metrics.get('quality_score', 100),
                    'workflow_id': workflow_id,
                    'source': 'workflow_intelligence'
                })

            self.events_processed['workflow_completed'] += 1
            logger.info(f"  ✅ Learned from workflow {workflow_id}")

        except Exception as e:
            logger.error(f"❌ Error handling workflow.completed: {e}", exc_info=True)

    async def handle_workflow_failed(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle workflow.failed event - Analyze failure patterns

        Actions:
        1. Record failure for pattern analysis
        2. Update risk prediction models
        3. Identify common failure modes
        """
        try:
            workflow_id = event_data.get('workflow_id')
            error_type = event_data.get('error_type', 'unknown')
            error_details = event_data.get('error_details', {})

            logger.info(f"⚠️ Analyzing failed workflow: {workflow_id} (error={error_type})")

            # Record failure for pattern analysis
            failure = {
                'workflow_id': workflow_id,
                'error_type': error_type,
                'error_details': error_details,
                'timestamp': datetime.utcnow().isoformat()
            }

            if not hasattr(self, 'workflow_failures'):
                self.workflow_failures = []

            self.workflow_failures.append(failure)

            # Detect failure patterns
            if len(self.workflow_failures) >= 10:
                await self._detect_failure_patterns()

            self.events_processed['workflow_failed'] += 1
            logger.info(f"  ✅ Analyzed failure for workflow {workflow_id}")

        except Exception as e:
            logger.error(f"❌ Error handling workflow.failed: {e}", exc_info=True)

    async def handle_workflow_milestone_reached(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle workflow.milestone_reached event - Update competency models

        Actions:
        1. Track milestone completion rates
        2. Update user competency scores
        3. Identify high-performing users
        """
        try:
            workflow_id = event_data.get('workflow_id')
            milestone = event_data.get('milestone')
            user_id = event_data.get('user_id', 'unknown')

            logger.info(f"🎯 Milestone reached: {milestone} (workflow={workflow_id})")

            # Map milestones to competencies
            milestone_competencies = {
                'bia_assessment_complete': 'business_impact_analysis',
                'risk_assessment_complete': 'risk_assessment',
                'plan_generated': 'continuity_planning',
                'exercise_designed': 'exercise_design',
                'validation_complete': 'quality_assurance'
            }

            competency = milestone_competencies.get(milestone)

            if competency and user_id != 'unknown':
                # Award competency points for milestone
                await self.competency_tracker.update_competency(
                    user_id=user_id,
                    competency=competency,
                    score=10,  # +10 points per milestone
                    evidence_type='milestone',
                    evidence_id=f"{workflow_id}_{milestone}"
                )

                logger.info(f"  ✅ Updated competency '{competency}' for user {user_id}")

            self.events_processed['workflow_milestone'] += 1

        except Exception as e:
            logger.error(f"❌ Error handling workflow.milestone_reached: {e}", exc_info=True)

    # ========================================================================
    # BIA EVENTS
    # ========================================================================

    async def handle_bia_completed(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle bia.completed event - Update knowledge graph

        Actions:
        1. Extract BIA patterns and insights
        2. Update industry-specific knowledge
        3. Index for similarity search
        """
        try:
            bia_id = event_data.get('bia_id')
            organization = event_data.get('organization', {})
            results = event_data.get('results', {})

            logger.info(f"📊 Learning from BIA completion: {bia_id}")

            # Extract knowledge from BIA
            bia_knowledge = {
                'bia_id': bia_id,
                'industry': organization.get('industry'),
                'org_size': organization.get('size'),
                'critical_processes': results.get('critical_processes', []),
                'recovery_objectives': results.get('recovery_objectives', {}),
                'dependencies': results.get('dependencies', []),
                'timestamp': datetime.utcnow().isoformat()
            }

            # Store for knowledge graph updates
            if not hasattr(self, 'bia_knowledge'):
                self.bia_knowledge = []

            self.bia_knowledge.append(bia_knowledge)

            # TODO: Update knowledge graph
            # TODO: Index BIA patterns for recommendations

            self.events_processed['bia_completed'] += 1
            logger.info(f"  ✅ Extracted knowledge from BIA {bia_id}")

        except Exception as e:
            logger.error(f"❌ Error handling bia.completed: {e}", exc_info=True)

    async def handle_bia_validated(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle bia.validated event - Strengthen knowledge base

        Actions:
        1. Mark validated BIAs as high-quality examples
        2. Use for training quality models
        3. Extract validated best practices
        """
        try:
            bia_id = event_data.get('bia_id')
            validation_score = event_data.get('validation_score', 0)
            validator = event_data.get('validator')

            logger.info(f"✅ BIA validated: {bia_id} (score={validation_score})")

            # High-quality validated BIAs are excellent training data
            if validation_score >= 80:
                logger.info(f"  ⭐ High-quality BIA detected: {bia_id}")
                # TODO: Add to gold-standard training set
                # TODO: Extract as best practice example

            self.events_processed['bia_validated'] += 1

        except Exception as e:
            logger.error(f"❌ Error handling bia.validated: {e}", exc_info=True)

    # ========================================================================
    # INCIDENT EVENTS
    # ========================================================================

    async def handle_incident_resolved(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle incident.resolved event - Learn from resolution

        Actions:
        1. Extract resolution patterns
        2. Update incident response models
        3. Build lessons learned database
        """
        try:
            incident_id = event_data.get('incident_id')
            incident_type = event_data.get('incident_type')
            resolution = event_data.get('resolution', {})

            logger.info(f"🚨 Learning from incident resolution: {incident_id} (type={incident_type})")

            # Extract lessons learned
            lesson = {
                'incident_id': incident_id,
                'incident_type': incident_type,
                'resolution_time': resolution.get('duration_minutes'),
                'actions_taken': resolution.get('actions', []),
                'effectiveness': resolution.get('effectiveness_score', 0),
                'timestamp': datetime.utcnow().isoformat()
            }

            if not hasattr(self, 'incident_lessons'):
                self.incident_lessons = []

            self.incident_lessons.append(lesson)

            # TODO: Create knowledge article from effective resolutions
            # TODO: Update incident response playbooks

            self.events_processed['incident_resolved'] += 1
            logger.info(f"  ✅ Learned from incident {incident_id}")

        except Exception as e:
            logger.error(f"❌ Error handling incident.resolved: {e}", exc_info=True)

    async def handle_incident_pattern_detected(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle incident.pattern_detected event - Update pattern library

        Actions:
        1. Record detected pattern
        2. Update pattern recognition models
        3. Alert to preventive measures
        """
        try:
            pattern_id = event_data.get('pattern_id')
            pattern_type = event_data.get('pattern_type')
            incidents = event_data.get('incidents', [])

            logger.info(f"🔍 Incident pattern detected: {pattern_id} (type={pattern_type})")

            # Record pattern for library
            pattern = {
                'pattern_id': pattern_id,
                'pattern_type': pattern_type,
                'incident_count': len(incidents),
                'incidents': incidents,
                'timestamp': datetime.utcnow().isoformat()
            }

            if not hasattr(self, 'incident_patterns'):
                self.incident_patterns = []

            self.incident_patterns.append(pattern)

            # TODO: Update pattern recognition models
            # TODO: Generate preventive recommendations

            self.events_processed['incident_pattern'] += 1
            logger.info(f"  ✅ Recorded incident pattern {pattern_id}")

        except Exception as e:
            logger.error(f"❌ Error handling incident.pattern_detected: {e}", exc_info=True)

    # ========================================================================
    # TRAINING/EXERCISE EVENTS (Bonus subscribers)
    # ========================================================================

    async def handle_exercise_completed(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle exercise.completed event - Learn from exercise outcomes

        Actions:
        1. Record exercise results for ML training
        2. Update difficulty adjustment models
        3. Detect training gaps
        """
        try:
            exercise_id = event_data.get('exercise_id')
            results = event_data.get('results', {})
            score = results.get('overall_score', 0)

            logger.info(f"🎓 Learning from exercise: {exercise_id} (score={score})")

            # Add to pattern detection
            exercise_result = {
                'exercise_id': exercise_id,
                'overall_score': score,
                'key_issues': results.get('issues', []),
                'strengths': results.get('strengths', []),
                'conducted_at': datetime.utcnow().isoformat()
            }

            if not hasattr(self, 'exercise_results'):
                self.exercise_results = []

            self.exercise_results.append(exercise_result)

            # Detect patterns from exercises
            if len(self.exercise_results) >= 10:
                patterns = self.pattern_detector.detect_patterns(self.exercise_results)
                if patterns:
                    logger.info(f"  🔍 Detected {len(patterns)} exercise patterns")

            self.events_processed['exercise_completed'] += 1

        except Exception as e:
            logger.error(f"❌ Error handling exercise.completed: {e}", exc_info=True)

    async def handle_prediction_made(self, event_data: Dict[str, Any], tenant_id: str):
        """
        Handle prediction.made event - Track prediction for accuracy measurement

        Actions:
        1. Record prediction for later validation
        2. Enable self-learning loop when actual outcome arrives
        """
        try:
            prediction_id = event_data.get('prediction_id')
            predicted_value = event_data.get('predicted_value')

            logger.info(f"🔮 Recording prediction: {prediction_id}")

            # Record prediction in self-learning engine
            self.self_learning.record_prediction(
                prediction_id=prediction_id,
                prediction_data=event_data
            )

            self.events_processed['prediction_made'] += 1

        except Exception as e:
            logger.error(f"❌ Error handling prediction.made: {e}", exc_info=True)

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _extract_case_features(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ML features from case data"""
        try:
            org_context = case_data.get('organization_context', {})
            metrics = case_data.get('metrics', {})

            # Map industry to numeric
            industry_map = {
                'healthcare': 1, 'finance': 2, 'manufacturing': 3,
                'retail': 4, 'technology': 5, 'other': 0
            }

            # Map org size to numeric
            size_map = {'small': 1, 'medium': 2, 'large': 3, 'enterprise': 4}

            return {
                'industry': industry_map.get(org_context.get('industry', 'other'), 0),
                'org_size': size_map.get(org_context.get('size', 'medium'), 2),
                'maturity_level': org_context.get('maturity_level', 2),
                'completion_time': metrics.get('completion_time_hours', 0),
                'team_size': metrics.get('team_size', 1),
                'module_complexity': metrics.get('complexity_score', 5)
            }
        except Exception as e:
            logger.warning(f"Failed to extract case features: {e}")
            return {}

    def _extract_workflow_features(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ML features from workflow context"""
        try:
            return {
                'team_competency': context.get('team_avg_competency', 50),
                'preparation_days': context.get('preparation_days', 7),
                'scenario_type': hash(context.get('scenario_type', 'unknown')) % 100,
                'previous_attempts': context.get('previous_attempts', 0),
                'resources_allocated': context.get('resources', 5)
            }
        except Exception as e:
            logger.warning(f"Failed to extract workflow features: {e}")
            return {}

    async def _detect_rejection_patterns(self) -> list:
        """Detect patterns in case rejections"""
        from collections import Counter

        # Analyze rejection reasons
        all_reasons = []
        for rejection in self.rejection_patterns:
            all_reasons.extend(rejection.get('reasons', []))

        reason_counts = Counter(all_reasons)

        patterns = []
        for reason, count in reason_counts.most_common(5):
            if count >= 3:  # At least 3 occurrences
                patterns.append({
                    'type': 'rejection_reason',
                    'reason': reason,
                    'count': count,
                    'severity': 'high' if count >= 5 else 'medium'
                })

        return patterns

    async def _detect_failure_patterns(self) -> list:
        """Detect patterns in workflow failures"""
        from collections import Counter

        # Analyze error types
        error_counts = Counter(
            failure.get('error_type') for failure in self.workflow_failures
        )

        patterns = []
        for error_type, count in error_counts.most_common(5):
            if count >= 3:
                patterns.append({
                    'type': 'workflow_failure',
                    'error_type': error_type,
                    'count': count,
                    'severity': 'critical' if count >= 5 else 'high'
                })

        return patterns

    def get_statistics(self) -> Dict[str, Any]:
        """Get subscriber statistics"""
        return {
            'events_processed': self.events_processed,
            'total_events': sum(self.events_processed.values()),
            'ml_training_buffer_size': len(self.self_learning.training_buffer),
            'model_version': self.self_learning.current_model_version,
            'timestamp': datetime.utcnow().isoformat()
        }


# ============================================================================
# SETUP FUNCTION
# ============================================================================

async def setup_event_subscribers(eventbus: EventBusClient) -> LearningEventSubscriber:
    """
    Setup all event subscribers for reactive learning

    This function:
    1. Initializes learning engines
    2. Creates subscriber instance
    3. Registers all event handlers
    4. Starts listening to events

    Call this during application startup.

    Args:
        eventbus: EventBusClient instance

    Returns:
        LearningEventSubscriber: Configured subscriber instance

    Example:
        ```python
        @app.on_event("startup")
        async def startup():
            eventbus = init_eventbus(settings.RABBITMQ_URL)
            await eventbus.connect()

            # Setup reactive learning
            subscriber = await setup_event_subscribers(eventbus)
        ```
    """

    if not EVENTBUS_AVAILABLE:
        logger.warning("⚠️ EventBus not available - reactive learning disabled")
        return None

    logger.info("🚀 Setting up reactive learning event subscribers...")

    # Initialize learning engines
    self_learning_engine = SelfLearningEngine()
    pattern_detector = PatternDetector()

    # Initialize competency tracker (with mock DB for now)
    try:
        from learning.engines.competency_tracker import CompetencyTracker
        competency_tracker = CompetencyTracker()
    except Exception as e:
        logger.warning(f"CompetencyTracker not available: {e}")
        # Create mock tracker
        class MockCompetencyTracker:
            async def update_competency(self, *args, **kwargs):
                pass
        competency_tracker = MockCompetencyTracker()

    # Initialize vector indexer (optional)
    vector_indexer = None
    try:
        from knowledge.indexer.vector_indexer import VectorIndexer
        vector_indexer = VectorIndexer()
        logger.info("  ✅ Vector indexer initialized")
    except Exception as e:
        logger.warning(f"  ⚠️ Vector indexer not available: {e}")

    # Initialize case collector (optional)
    case_collector = None
    try:
        from knowledge.loader.case_loader import CaseCollector
        case_collector = CaseCollector()
        logger.info("  ✅ Case collector initialized")
    except Exception as e:
        logger.warning(f"  ⚠️ Case collector not available: {e}")

    # Create subscriber
    subscriber = LearningEventSubscriber(
        eventbus=eventbus,
        self_learning_engine=self_learning_engine,
        pattern_detector=pattern_detector,
        competency_tracker=competency_tracker,
        vector_indexer=vector_indexer,
        case_collector=case_collector
    )

    # Register event handlers
    logger.info("📡 Registering event handlers...")

    # Community Intelligence events
    await eventbus.subscribe(
        'case.approved',
        subscriber.handle_case_approved,
        queue_name='ai_foundation_case_approved'
    )
    logger.info("  ✅ Subscribed to: case.approved")

    await eventbus.subscribe(
        'case.rejected',
        subscriber.handle_case_rejected,
        queue_name='ai_foundation_case_rejected'
    )
    logger.info("  ✅ Subscribed to: case.rejected")

    await eventbus.subscribe(
        'review.submitted',
        subscriber.handle_review_submitted,
        queue_name='ai_foundation_review_submitted'
    )
    logger.info("  ✅ Subscribed to: review.submitted")

    # Workflow Intelligence events
    await eventbus.subscribe(
        'workflow.completed',
        subscriber.handle_workflow_completed,
        queue_name='ai_foundation_workflow_completed'
    )
    logger.info("  ✅ Subscribed to: workflow.completed")

    await eventbus.subscribe(
        'workflow.failed',
        subscriber.handle_workflow_failed,
        queue_name='ai_foundation_workflow_failed'
    )
    logger.info("  ✅ Subscribed to: workflow.failed")

    await eventbus.subscribe(
        'workflow.milestone_reached',
        subscriber.handle_workflow_milestone_reached,
        queue_name='ai_foundation_workflow_milestone'
    )
    logger.info("  ✅ Subscribed to: workflow.milestone_reached")

    # BIA events
    await eventbus.subscribe(
        'bia.completed',
        subscriber.handle_bia_completed,
        queue_name='ai_foundation_bia_completed'
    )
    logger.info("  ✅ Subscribed to: bia.completed")

    await eventbus.subscribe(
        'bia.validated',
        subscriber.handle_bia_validated,
        queue_name='ai_foundation_bia_validated'
    )
    logger.info("  ✅ Subscribed to: bia.validated")

    # Incident events
    await eventbus.subscribe(
        'incident.resolved',
        subscriber.handle_incident_resolved,
        queue_name='ai_foundation_incident_resolved'
    )
    logger.info("  ✅ Subscribed to: incident.resolved")

    await eventbus.subscribe(
        'incident.pattern_detected',
        subscriber.handle_incident_pattern_detected,
        queue_name='ai_foundation_incident_pattern'
    )
    logger.info("  ✅ Subscribed to: incident.pattern_detected")

    # Exercise/Training events (bonus)
    await eventbus.subscribe(
        'exercise.completed',
        subscriber.handle_exercise_completed,
        queue_name='ai_foundation_exercise_completed'
    )
    logger.info("  ✅ Subscribed to: exercise.completed")

    await eventbus.subscribe(
        'prediction.made',
        subscriber.handle_prediction_made,
        queue_name='ai_foundation_prediction_made'
    )
    logger.info("  ✅ Subscribed to: prediction.made")

    logger.info("✅ Reactive learning subscribers ready!")
    logger.info(f"   📊 Total subscribers: 12")
    logger.info(f"   🎯 Event sources: Community Intelligence, Workflow Intelligence, BIA, Incidents, Training")
    logger.info(f"   🧠 Learning actions: ML updates, Pattern detection, Knowledge indexing, Competency tracking")

    return subscriber
