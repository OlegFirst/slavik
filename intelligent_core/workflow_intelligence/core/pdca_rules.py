"""
🔄 PDCA Rules Engine - REAL IMPLEMENTATION

NO MOCKS. NO OPTIONALS. REAL DEPENDENCIES.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Import PDCA metrics for monitoring
try:
    import sys
    from pathlib import Path
    # Add metrics to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from metrics.pdca_metrics import (
        track_pdca_phase,
        track_pdca_metrics,
        initialize_pdca_metrics
    )
    METRICS_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ PDCA metrics imported successfully")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ PDCA metrics not available: {e}")
    METRICS_AVAILABLE = False
    # Mock decorator if metrics not available
    def track_pdca_phase(phase):
        def decorator(func):
            return func
        return decorator


# ============================================================================
# PDCA CYCLE DATA
# ============================================================================

@dataclass
class PDCACycleData:
    """PDCA cycle data"""

    workflow_id: str
    module: str
    cycle_started_at: datetime

    # PLAN
    plan_data: Dict[str, Any]
    plan_recommendations: List[str]

    # DO
    do_data: Dict[str, Any] = None
    do_duration: Optional[float] = None

    # CHECK
    check_data: Dict[str, Any] = None
    deviations: List[str] = None
    benchmarks: Dict[str, float] = None
    quality_score: Optional[float] = None

    # ACT
    lessons_learned: List[str] = None
    patterns_detected: List[str] = None
    improvements: List[str] = None

    cycle_completed_at: Optional[datetime] = None
    user_id: Optional[str] = None
    similar_cases_count: int = 0


# ============================================================================
# PDCA RULES ENGINE - REAL IMPLEMENTATION
# ============================================================================

class PDCARulesEngine:
    """
    REAL PDCA Rules Engine

    NO MOCKS - все зависимости REQUIRED!
    """

    def __init__(
        self,
        db_session: AsyncSession,
        tenant_id: str,
        case_library,  # REQUIRED
        knowledge_base,  # REQUIRED
        pattern_detector  # REQUIRED
    ):
        """
        Initialize with REAL dependencies

        Args:
            db_session: PostgreSQL session (REQUIRED)
            tenant_id: Tenant ID for RLS (REQUIRED)
            case_library: CaseLibrary instance (REQUIRED)
            knowledge_base: KnowledgeBase instance (REQUIRED)
            pattern_detector: PatternDetector instance (REQUIRED)
        """
        # Validate all required
        if not all([db_session, tenant_id, case_library, knowledge_base, pattern_detector]):
            raise ValueError("All dependencies are REQUIRED! No optionals allowed.")

        # Real dependencies
        self.db = db_session
        self.tenant_id = tenant_id
        self.case_library = case_library
        self.knowledge_base = knowledge_base
        self.pattern_detector = pattern_detector

        # PostgreSQL repository
        from workflow_intelligence.storage.pdca_repository import PDCACycleRepository
        self.pdca_repo = PDCACycleRepository(db_session, tenant_id)

        # In-memory cache (for current session only)
        self.active_cycles: Dict[str, PDCACycleData] = {}

        logger.info("✅ PDCA Rules Engine initialized with REAL dependencies")

    # ========================================================================
    # PLAN PHASE
    # ========================================================================

    @track_pdca_phase("plan")
    async def plan_workflow(
        self,
        workflow_id: str,
        module: str,
        workflow_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        PLAN phase - REAL implementation

        Uses:
        - Case Library for similar cases
        - Knowledge Base for best practices
        - PostgreSQL for benchmarks
        """
        logger.info(f"[PDCA PLAN] workflow={workflow_id}, module={module}")

        # 1. Find similar cases (REAL Case Library)
        similar_cases = await self.case_library.find_cases(
            problem_type=module,
            min_success_rate=0.8,
            exclude_org_id=self.tenant_id,
            limit=10
        )

        logger.info(f"Found {len(similar_cases)} similar cases")

        # 2. Extract recommendations
        recommendations = []
        for case in similar_cases:
            if case.get('success_patterns'):
                recommendations.extend(case['success_patterns'][:2])
        recommendations = list(set(recommendations))[:5]

        # 3. Get benchmarks from PostgreSQL
        benchmarks = await self.pdca_repo.get_benchmarks(module)

        # 4. Predict outcomes
        expected_outcomes = {}
        if benchmarks['total_cycles'] > 0:
            expected_outcomes = {
                'estimated_duration': benchmarks['median_duration'],
                'expected_quality': benchmarks['avg_quality_score'],
                'success_probability': benchmarks['success_rate']
            }

        # 5. Create cycle
        cycle = PDCACycleData(
            workflow_id=workflow_id,
            module=module,
            cycle_started_at=datetime.utcnow(),
            plan_data={
                'workflow_data': workflow_data,
                'expected_outcomes': expected_outcomes,
                'estimated_duration': expected_outcomes.get('estimated_duration', 0)
            },
            plan_recommendations=recommendations,
            user_id=user_id,
            similar_cases_count=len(similar_cases)
        )

        self.active_cycles[workflow_id] = cycle

        logger.info(f"✅ PLAN complete: {len(recommendations)} recommendations")

        return {
            'recommendations': recommendations,
            'expected_outcomes': expected_outcomes,
            'similar_cases_count': len(similar_cases),
            'benchmarks': benchmarks
        }

    # ========================================================================
    # DO PHASE
    # ========================================================================

    @track_pdca_phase("do")
    async def track_execution(
        self,
        workflow_id: str,
        execution_data: Dict[str, Any]
    ):
        """DO phase - track execution"""

        cycle = self.active_cycles.get(workflow_id)
        if not cycle:
            logger.warning(f"No active cycle for {workflow_id}")
            return

        cycle.do_data = execution_data
        cycle.do_duration = (
            datetime.utcnow() - cycle.cycle_started_at
        ).total_seconds()

        logger.info(f"[PDCA DO] workflow={workflow_id}, duration={cycle.do_duration:.1f}s")

    # ========================================================================
    # CHECK PHASE
    # ========================================================================

    @track_pdca_phase("check")
    async def check_workflow(
        self,
        workflow_id: str,
        final_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        CHECK phase - REAL validation

        Uses:
        - PostgreSQL benchmarks
        - Quality standards from Knowledge Base
        """
        logger.info(f"[PDCA CHECK] workflow={workflow_id}")

        cycle = self.active_cycles.get(workflow_id)
        if not cycle:
            logger.warning(f"No active cycle for {workflow_id}")
            return {}

        # 1. Get benchmarks from PostgreSQL
        benchmarks = await self.pdca_repo.get_benchmarks(cycle.module)

        # 2. Find deviations
        deviations = []

        # Duration deviation
        if cycle.do_duration and benchmarks['median_duration'] > 0:
            if cycle.do_duration > benchmarks['median_duration'] * 1.2:
                deviations.append(
                    f"Duration exceeded: {cycle.do_duration:.1f}s vs "
                    f"{benchmarks['median_duration']:.1f}s median"
                )

        # Quality deviation (if provided)
        if 'quality_score' in final_data:
            if final_data['quality_score'] < benchmarks['avg_quality_score'] * 0.9:
                deviations.append(
                    f"Quality below average: {final_data['quality_score']:.1f} vs "
                    f"{benchmarks['avg_quality_score']:.1f} avg"
                )

        # 3. Calculate score
        base_score = 100
        penalty_per_deviation = 10
        score = max(0, base_score - len(deviations) * penalty_per_deviation)

        # 4. Save to cycle
        cycle.check_data = final_data
        cycle.deviations = deviations
        cycle.benchmarks = benchmarks
        cycle.quality_score = score

        logger.info(f"✅ CHECK complete: score={score}, deviations={len(deviations)}")

        return {
            'score': score,
            'deviations': deviations,
            'benchmarks': benchmarks
        }

    # ========================================================================
    # ACT PHASE
    # ========================================================================

    @track_pdca_phase("act")
    async def complete_cycle(
        self,
        workflow_id: str
    ) -> Dict[str, Any]:
        """
        ACT phase - REAL learning

        Uses:
        - Pattern Detector for ML insights
        - Knowledge Base for lesson storage
        - PostgreSQL for persistence
        """
        logger.info(f"[PDCA ACT] workflow={workflow_id}")

        cycle = self.active_cycles.pop(workflow_id, None)
        if not cycle:
            logger.warning(f"No active cycle for {workflow_id}")
            return {}

        # 1. Extract lessons with Pattern Detector (REAL ML)
        patterns_data = {
            'plan': cycle.plan_data,
            'do': cycle.do_data,
            'check': cycle.check_data,
            'deviations': cycle.deviations or []
        }

        detected_patterns = await self.pattern_detector.detect_patterns(patterns_data)
        cycle.patterns_detected = [p.get('pattern_name', 'unknown') for p in detected_patterns]

        # 2. Extract lessons
        lessons = []

        if cycle.deviations:
            for deviation in cycle.deviations:
                lessons.append(f"Issue: {deviation}")
        else:
            lessons.append(f"Success: {cycle.module} workflow completed with no deviations")

        # Add ML insights
        for pattern in detected_patterns:
            if pattern.get('description'):
                lessons.append(pattern['description'])

        cycle.lessons_learned = lessons

        # 3. Suggest improvements
        improvements = []

        if cycle.do_duration and cycle.benchmarks:
            if cycle.do_duration > cycle.benchmarks.get('median_duration', 0) * 1.3:
                improvements.append(
                    f"Optimize execution time: target < {cycle.benchmarks['median_duration']:.1f}s"
                )

        if len(cycle.deviations or []) > 0:
            improvements.append("Review process to reduce deviations")

        cycle.improvements = improvements
        cycle.cycle_completed_at = datetime.utcnow()

        # 4. Save to PostgreSQL (REAL persistence)
        cycle_dict = asdict(cycle)
        cycle_id = await self.pdca_repo.save_cycle(cycle_dict)

        logger.info(f"✅ Cycle saved to PostgreSQL: {cycle_id}")

        # 5. Save lessons to Knowledge Base (REAL learning)
        if lessons:
            try:
                await self.knowledge_base.save_lesson({
                    'source': 'pdca_workflow',
                    'module': cycle.module,
                    'workflow_id': workflow_id,
                    'lessons': lessons,
                    'patterns': cycle.patterns_detected,
                    'quality_score': cycle.quality_score,
                    'metadata': {
                        'duration': cycle.do_duration,
                        'deviations_count': len(cycle.deviations or [])
                    }
                })

                await self.pdca_repo.update_cycle_metadata(
                    workflow_id,
                    saved_to_knowledge_base=True
                )

                logger.info(f"✅ Lessons saved to Knowledge Base")
            except Exception as e:
                logger.error(f"Failed to save lessons: {e}")

        logger.info(f"✅ ACT complete: {len(lessons)} lessons, {len(cycle.patterns_detected)} patterns")

        # Track metrics if available
        if METRICS_AVAILABLE:
            try:
                cycle_dict = asdict(cycle)
                track_pdca_metrics(cycle_dict, cycle.module, self.tenant_id)
                logger.info("📊 PDCA metrics tracked successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to track PDCA metrics: {e}")

        return {
            'cycle_id': cycle_id,
            'lessons': lessons,
            'patterns': cycle.patterns_detected,
            'improvements': improvements,
            'duration': cycle.do_duration,
            'quality_score': cycle.quality_score
        }


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

# Will be initialized in enable_pdca.py with real dependencies
_pdca_rules_engine: Optional[PDCARulesEngine] = None


def get_pdca_engine() -> PDCARulesEngine:
    """Get initialized PDCA engine"""
    if _pdca_rules_engine is None:
        raise RuntimeError(
            "PDCA Engine not initialized! "
            "Call initialize_pdca_engine() first."
        )
    return _pdca_rules_engine


def initialize_pdca_engine(
    db_session: AsyncSession,
    tenant_id: str,
    case_library,
    knowledge_base,
    pattern_detector
) -> PDCARulesEngine:
    """Initialize global PDCA engine with REAL dependencies"""
    global _pdca_rules_engine

    _pdca_rules_engine = PDCARulesEngine(
        db_session=db_session,
        tenant_id=tenant_id,
        case_library=case_library,
        knowledge_base=knowledge_base,
        pattern_detector=pattern_detector
    )

    logger.info("✅ Global PDCA Engine initialized")
    return _pdca_rules_engine


# ============================================================================
# EVENT BUS INTEGRATION
# ============================================================================

async def enable_pdca_for_workflow_engine(event_bus, pdca_engine: PDCARulesEngine):
    """
    Enable PDCA rules for Workflow Engine

    Subscribes to workflow events from PLATFORM EventBus
    """

    @event_bus.subscribe("workflow.started")
    async def on_workflow_started(event):
        """PLAN phase trigger"""
        try:
            await pdca_engine.plan_workflow(
                workflow_id=event.data.get('workflow_id'),
                module=event.data.get('module'),
                workflow_data=event.data.get('workflow_data', {}),
                user_id=event.data.get('user_id')
            )
        except Exception as e:
            logger.error(f"PDCA PLAN failed: {e}", exc_info=True)

    @event_bus.subscribe("workflow.stage.changed")
    async def on_stage_changed(event):
        """DO phase tracking"""
        try:
            await pdca_engine.track_execution(
                workflow_id=event.data.get('workflow_id'),
                execution_data=event.data
            )
        except Exception as e:
            logger.error(f"PDCA DO failed: {e}", exc_info=True)

    @event_bus.subscribe("workflow.completed")
    async def on_workflow_completed(event):
        """CHECK + ACT phases"""
        try:
            workflow_id = event.data.get('workflow_id')

            # CHECK
            check_result = await pdca_engine.check_workflow(
                workflow_id=workflow_id,
                final_data=event.data
            )

            # ACT
            act_result = await pdca_engine.complete_cycle(workflow_id)

            logger.info(
                f"✅ PDCA cycle complete: workflow={workflow_id}, "
                f"score={check_result.get('score')}, "
                f"lessons={len(act_result.get('lessons', []))}"
            )
        except Exception as e:
            logger.error(f"PDCA CHECK/ACT failed: {e}", exc_info=True)

    logger.info("✅ PDCA enabled for Workflow Engine (platform EventBus)")
