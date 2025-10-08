"""
Learning Tasks - ML Model Updates and Pattern Extraction
=========================================================
"""
import logging
from datetime import datetime
from typing import Dict, Any
from celery import Task

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from celery_app import app
from shared.eventbus import get_eventbus

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """Base task with EventBus notifications"""

    def on_success(self, retval, task_id, args, kwargs):
        """Task succeeded - publish event"""
        eventbus = get_eventbus()
        if eventbus:
            eventbus.publish_sync(
                'task.completed',
                {
                    'task_id': task_id,
                    'task_name': self.name,
                    'result': retval,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Task failed - publish event"""
        eventbus = get_eventbus()
        if eventbus:
            eventbus.publish_sync(
                'task.failed',
                {
                    'task_id': task_id,
                    'task_name': self.name,
                    'error': str(exc),
                    'timestamp': datetime.utcnow().isoformat()
                }
            )


@app.task(base=CallbackTask, bind=True, max_retries=3)
def update_all_models(self) -> Dict[str, Any]:
    """
    Daily task: Update all learning models

    Runs at 2 AM daily
    """
    logger.info("🔄 Starting daily model update...")

    try:
        # Import here to avoid circular dependencies
        from intelligent_core.ai_foundation.learning.self_learning_engine import SelfLearningEngine

        engine = SelfLearningEngine()

        # Fetch new training data from last 24 hours
        training_data = engine.fetch_recent_training_data(hours=24)

        if not training_data:
            logger.info("No new training data - skipping update")
            return {'status': 'skipped', 'reason': 'no_new_data'}

        # Update models
        results = engine.incremental_update(training_data)

        # Validate new models
        validation_results = engine.validate_models()

        # Deploy if validation passed
        if validation_results['passed']:
            engine.deploy_models()
            logger.info(f"✅ Models updated successfully: {results}")

            return {
                'status': 'success',
                'models_updated': results['models'],
                'accuracy_improvement': results.get('accuracy_delta', 0),
                'validation': validation_results
            }
        else:
            logger.warning("⚠️ Validation failed - keeping old models")
            return {
                'status': 'validation_failed',
                'validation': validation_results
            }

    except Exception as exc:
        logger.error(f"❌ Model update failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@app.task(base=CallbackTask, bind=True)
def extract_patterns(self) -> Dict[str, Any]:
    """
    Hourly task: Extract patterns from recent activities
    """
    logger.info("🔍 Extracting patterns from recent activities...")

    try:
        from intelligent_core.workflow_intelligence.case_library.pattern_detector import PatternDetector

        detector = PatternDetector()

        # Analyze last hour's workflow executions
        patterns = detector.extract_patterns_from_recent(hours=1)

        if patterns:
            # Store patterns to case library
            detector.store_patterns(patterns)

            logger.info(f"✅ Extracted {len(patterns)} new patterns")
            return {
                'status': 'success',
                'patterns_count': len(patterns),
                'patterns': [p.to_dict() for p in patterns]
            }
        else:
            return {'status': 'no_patterns', 'patterns_count': 0}

    except Exception as exc:
        logger.error(f"❌ Pattern extraction failed: {exc}")
        raise


@app.task(base=CallbackTask, bind=True, max_retries=2)
def full_model_retrain(self) -> Dict[str, Any]:
    """
    Weekly task: Full model retraining

    Runs every Sunday at 3 AM
    """
    logger.info("🔄 Starting weekly full model retraining...")

    try:
        from intelligent_core.ai_foundation.learning.self_learning_engine import SelfLearningEngine

        engine = SelfLearningEngine()

        # Fetch all training data from last 30 days
        training_data = engine.fetch_recent_training_data(hours=24*30)

        # Full retrain
        results = engine.full_retrain(training_data)

        # Comprehensive validation
        validation = engine.comprehensive_validation()

        if validation['passed']:
            engine.deploy_models()
            logger.info(f"✅ Full retraining completed: {results}")

            return {
                'status': 'success',
                'models_retrained': results['models'],
                'training_samples': len(training_data),
                'validation': validation
            }
        else:
            logger.error("❌ Validation failed after retraining")
            return {
                'status': 'validation_failed',
                'validation': validation
            }

    except Exception as exc:
        logger.error(f"❌ Model retraining failed: {exc}")
        raise self.retry(exc=exc, countdown=3600)  # Retry after 1 hour


@app.task(base=CallbackTask)
def learn_from_case(case_id: str, outcome: str) -> Dict[str, Any]:
    """
    Reactive task: Learn from completed case

    Triggered by: case.completed event
    """
    logger.info(f"📚 Learning from case: {case_id}")

    try:
        from intelligent_core.workflow_intelligence.case_library.case_library import CaseLibrary

        library = CaseLibrary()

        # Store case with outcome
        library.store_case(case_id, outcome)

        # Extract lessons learned
        lessons = library.extract_lessons(case_id)

        # Update similarity index
        library.update_similarity_index()

        return {
            'status': 'success',
            'case_id': case_id,
            'lessons_count': len(lessons)
        }

    except Exception as exc:
        logger.error(f"❌ Learning from case failed: {exc}")
        raise
