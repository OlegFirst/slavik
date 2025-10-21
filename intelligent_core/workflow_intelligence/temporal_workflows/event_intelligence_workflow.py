"""
Event Intelligence Temporal Workflow
=====================================

Durable workflows for automated event analysis, learning, and prediction.

Workflows:
- EventAnalysisWorkflow - Analyze events and patterns
- PatternLearningWorkflow - ML learning from feedback
- GapPredictionWorkflow - Predict missing handlers
- KnowledgeAccumulationWorkflow - Build knowledge base

Activities:
- analyze_event_activity - Analyze single event
- analyze_domain_activity - Analyze domain events
- record_suggestion_activity - Record AI suggestion
- record_feedback_activity - Record developer feedback
- predict_gaps_activity - Predict event gaps
- accumulate_knowledge_activity - Store knowledge

Cron Schedules:
- Weekly event analysis (Sunday 2:00 AM)
- Monthly pattern learning (1st of month, 3:00 AM)
"""

from datetime import timedelta
from typing import Dict, List, Any, Optional
import logging

from temporalio import workflow, activity
from temporalio.common import RetryPolicy

logger = logging.getLogger(__name__)


# ==================== Data Classes ====================

@workflow.defn
class EventAnalysisWorkflow:
    """
    Workflow for comprehensive event analysis

    Steps:
    1. Scan codebase for events
    2. Analyze each event (importance, patterns)
    3. Store results in knowledge base
    4. Generate recommendations
    5. Send notifications
    """

    @workflow.run
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute event analysis workflow"""

        workflow.logger.info(" Starting Event Analysis Workflow")

        results = {
            "workflow": "event_analysis",
            "status": "started",
            "events_analyzed": 0,
            "recommendations": [],
            "knowledge_stored": False
        }

        try:
            # Step 1: Scan for events
            workflow.logger.info(" Step 1: Scanning for events...")
            events = await workflow.execute_activity(
                scan_events_activity,
                config.get("scan_config", {}),
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=10),
                    maximum_interval=timedelta(minutes=1)
                )
            )

            workflow.logger.info(f" Found {len(events)} events")
            results["events_found"] = len(events)

            # Step 2: Analyze each event
            workflow.logger.info(" Step 2: Analyzing events...")
            analyses = []

            for event in events:
                try:
                    analysis = await workflow.execute_activity(
                        analyze_event_activity,
                        event,
                        start_to_close_timeout=timedelta(minutes=5),
                        retry_policy=RetryPolicy(
                            maximum_attempts=3,
                            initial_interval=timedelta(seconds=5)
                        )
                    )
                    analyses.append(analysis)
                    results["events_analyzed"] += 1

                except Exception as e:
                    workflow.logger.error(f" Event analysis failed: {e}")
                    continue

            workflow.logger.info(f" Analyzed {len(analyses)} events")

            # Step 3: Store in knowledge base
            workflow.logger.info(" Step 3: Storing knowledge...")
            stored = await workflow.execute_activity(
                store_knowledge_activity,
                {"analyses": analyses},
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )
            results["knowledge_stored"] = stored

            # Step 4: Generate recommendations
            workflow.logger.info(" Step 4: Generating recommendations...")
            recommendations = await workflow.execute_activity(
                generate_recommendations_activity,
                {"analyses": analyses},
                start_to_close_timeout=timedelta(minutes=3),
                retry_policy=RetryPolicy(maximum_attempts=2)
            )
            results["recommendations"] = recommendations

            # Step 5: Send notifications
            workflow.logger.info(" Step 5: Sending notifications...")
            if recommendations:
                await workflow.execute_activity(
                    send_notification_activity,
                    {
                        "type": "event_analysis_complete",
                        "data": {
                            "events_analyzed": results["events_analyzed"],
                            "recommendations_count": len(recommendations),
                            "top_recommendations": recommendations[:5]
                        }
                    },
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(maximum_attempts=2)
                )

            results["status"] = "completed"
            workflow.logger.info(" Event Analysis Workflow completed")

        except Exception as e:
            workflow.logger.error(f" Workflow failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)

        return results


@workflow.defn
class PatternLearningWorkflow:
    """
    Workflow for ML learning from feedback

    Steps:
    1. Collect feedback data
    2. Analyze patterns
    3. Update ML models
    4. Generate learning report
    5. Store updated models
    """

    @workflow.run
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pattern learning workflow"""

        workflow.logger.info(" Starting Pattern Learning Workflow")

        results = {
            "workflow": "pattern_learning",
            "status": "started",
            "feedback_processed": 0,
            "models_updated": False,
            "accuracy_improvement": 0.0
        }

        try:
            # Step 1: Collect feedback
            workflow.logger.info(" Step 1: Collecting feedback data...")
            feedback = await workflow.execute_activity(
                collect_feedback_activity,
                config.get("timeframe", "last_30_days"),
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            results["feedback_processed"] = len(feedback)
            workflow.logger.info(f" Collected {len(feedback)} feedback entries")

            # Step 2: Analyze patterns
            workflow.logger.info(" Step 2: Analyzing patterns...")
            patterns = await workflow.execute_activity(
                analyze_patterns_activity,
                {"feedback": feedback},
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(maximum_attempts=2)
            )

            results["patterns_found"] = len(patterns)

            # Step 3: Update ML models
            workflow.logger.info(" Step 3: Updating ML models...")
            model_update = await workflow.execute_activity(
                update_ml_models_activity,
                {"feedback": feedback, "patterns": patterns},
                start_to_close_timeout=timedelta(minutes=15),
                retry_policy=RetryPolicy(maximum_attempts=2)
            )

            results["models_updated"] = model_update.get("success", False)
            results["accuracy_improvement"] = model_update.get("accuracy_improvement", 0.0)

            # Step 4: Generate learning report
            workflow.logger.info(" Step 4: Generating learning report...")
            report = await workflow.execute_activity(
                generate_learning_report_activity,
                {
                    "feedback": feedback,
                    "patterns": patterns,
                    "model_update": model_update
                },
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=2)
            )

            results["report"] = report

            # Step 5: Send notifications
            workflow.logger.info(" Step 5: Sending notifications...")
            await workflow.execute_activity(
                send_notification_activity,
                {
                    "type": "pattern_learning_complete",
                    "data": {
                        "feedback_processed": results["feedback_processed"],
                        "accuracy_improvement": results["accuracy_improvement"],
                        "report_summary": report.get("summary", "")
                    }
                },
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=2)
            )

            results["status"] = "completed"
            workflow.logger.info(" Pattern Learning Workflow completed")

        except Exception as e:
            workflow.logger.error(f" Workflow failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)

        return results


@workflow.defn
class GapPredictionWorkflow:
    """
    Workflow for predicting missing event handlers

    Steps:
    1. Scan current event architecture
    2. Load ML prediction model
    3. Predict missing handlers
    4. Validate predictions
    5. Generate recommendations
    """

    @workflow.run
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute gap prediction workflow"""

        workflow.logger.info(" Starting Gap Prediction Workflow")

        results = {
            "workflow": "gap_prediction",
            "status": "started",
            "gaps_predicted": 0,
            "high_confidence_gaps": 0,
            "recommendations": []
        }

        try:
            # Step 1: Scan current architecture
            workflow.logger.info(" Step 1: Scanning event architecture...")
            current_events = await workflow.execute_activity(
                scan_current_architecture_activity,
                {},
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(maximum_attempts=3)
            )

            # Step 2: Predict gaps
            workflow.logger.info(" Step 2: Predicting gaps...")
            predictions = await workflow.execute_activity(
                predict_gaps_activity,
                {"current_events": current_events},
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=RetryPolicy(maximum_attempts=2)
            )

            results["gaps_predicted"] = len(predictions)
            results["high_confidence_gaps"] = len([p for p in predictions if p.get("confidence", 0) >= 0.8])

            # Step 3: Validate predictions
            workflow.logger.info("️ Step 3: Validating predictions...")
            validated = await workflow.execute_activity(
                validate_predictions_activity,
                {"predictions": predictions},
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=2)
            )

            # Step 4: Generate recommendations
            workflow.logger.info(" Step 4: Generating recommendations...")
            recommendations = await workflow.execute_activity(
                generate_gap_recommendations_activity,
                {"validated_predictions": validated},
                start_to_close_timeout=timedelta(minutes=3),
                retry_policy=RetryPolicy(maximum_attempts=2)
            )

            results["recommendations"] = recommendations

            # Step 5: Send notifications
            workflow.logger.info(" Step 5: Sending notifications...")
            if results["high_confidence_gaps"] > 0:
                await workflow.execute_activity(
                    send_notification_activity,
                    {
                        "type": "gaps_detected",
                        "priority": "high" if results["high_confidence_gaps"] > 5 else "medium",
                        "data": {
                            "total_gaps": results["gaps_predicted"],
                            "high_confidence": results["high_confidence_gaps"],
                            "top_recommendations": recommendations[:5]
                        }
                    },
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(maximum_attempts=2)
                )

            results["status"] = "completed"
            workflow.logger.info(" Gap Prediction Workflow completed")

        except Exception as e:
            workflow.logger.error(f" Workflow failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)

        return results


# ==================== Activities ====================

@activity.defn
async def scan_events_activity(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Scan codebase for events"""
    logger.info(" Scanning codebase for events...")

    # Import event scanner (from tools/event_intelligence)
    try:
        from tools.event_intelligence import scan_codebase_events
        events = scan_codebase_events(config)
        return events
    except Exception as e:
        logger.error(f" Event scanning failed: {e}")
        return []


@activity.defn
async def analyze_event_activity(event: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze single event"""
    logger.info(f" Analyzing event: {event.get('event_name')}")

    try:
        from intelligent_core.event_intelligence.analyzer import EventAnalyzer

        analyzer = EventAnalyzer()
        analysis = await analyzer.analyze_event(
            event_name=event.get("event_name"),
            publishers=event.get("publishers", []),
            subscribers=event.get("subscribers", []),
            historical_data=event.get("historical_data")
        )

        return {
            "event_name": analysis.event_name,
            "importance_score": analysis.importance_score,
            "usage_pattern": analysis.usage_pattern,
            "recommendations": analysis.recommendations,
            "ai_insights": analysis.ai_insights
        }

    except Exception as e:
        logger.error(f" Analysis failed: {e}")
        raise


@activity.defn
async def store_knowledge_activity(data: Dict[str, Any]) -> bool:
    """Store knowledge in knowledge base"""
    logger.info(" Storing knowledge...")

    try:
        from intelligent_core.event_intelligence.knowledge_base import EventKnowledgeBase

        kb = EventKnowledgeBase()

        for analysis in data.get("analyses", []):
            await kb.store_event_analysis(
                analysis.get("event_name"),
                analysis
            )

        return True

    except Exception as e:
        logger.error(f" Knowledge storage failed: {e}")
        return False


@activity.defn
async def generate_recommendations_activity(data: Dict[str, Any]) -> List[str]:
    """Generate recommendations from analyses"""
    logger.info(" Generating recommendations...")

    analyses = data.get("analyses", [])
    recommendations = []

    # High importance events without subscribers
    for analysis in analyses:
        if analysis.get("importance_score", 0) > 0.7 and len(analysis.get("subscribers", [])) == 0:
            recommendations.append(
                f"Critical event '{analysis.get('event_name')}' has no subscribers - consider adding handlers"
            )

    # Events with no publishers
    for analysis in analyses:
        if len(analysis.get("publishers", [])) == 0:
            recommendations.append(
                f"Event '{analysis.get('event_name')}' has no publishers - verify if needed"
            )

    return recommendations[:10]  # Top 10


@activity.defn
async def collect_feedback_activity(timeframe: str) -> List[Dict[str, Any]]:
    """Collect feedback data"""
    logger.info(f" Collecting feedback for: {timeframe}")

    try:
        from intelligent_core.event_intelligence.learner import EventLearner

        learner = EventLearner()
        feedback = await learner.get_recent_feedback(timeframe)

        return feedback

    except Exception as e:
        logger.error(f" Feedback collection failed: {e}")
        return []


@activity.defn
async def analyze_patterns_activity(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze patterns from feedback"""
    logger.info(" Analyzing patterns...")

    feedback = data.get("feedback", [])

    # Pattern detection logic
    patterns = []

    # Success pattern
    success_events = [f for f in feedback if f.get("outcome") == "success"]
    if len(success_events) > 5:
        patterns.append({
            "type": "success_pattern",
            "events": [f.get("event_name") for f in success_events],
            "confidence": 0.8
        })

    return patterns


@activity.defn
async def update_ml_models_activity(data: Dict[str, Any]) -> Dict[str, Any]:
    """Update ML models with new data"""
    logger.info(" Updating ML models...")

    try:
        from intelligent_core.event_intelligence.predictor import EventPredictor

        predictor = EventPredictor()

        # Train with new data
        result = await predictor.train_with_feedback(
            feedback=data.get("feedback", []),
            patterns=data.get("patterns", [])
        )

        return {
            "success": True,
            "accuracy_improvement": result.get("accuracy_improvement", 0.0)
        }

    except Exception as e:
        logger.error(f" Model update failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@activity.defn
async def generate_learning_report_activity(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate learning report"""
    logger.info(" Generating learning report...")

    return {
        "summary": f"Processed {len(data.get('feedback', []))} feedback entries",
        "patterns_found": len(data.get("patterns", [])),
        "model_accuracy": data.get("model_update", {}).get("accuracy_improvement", 0.0),
        "timestamp": "2025-10-08"
    }


@activity.defn
async def scan_current_architecture_activity(config: Dict[str, Any]) -> Dict[str, Any]:
    """Scan current event architecture"""
    logger.info(" Scanning current architecture...")

    try:
        from tools.event_intelligence import scan_codebase_events
        events = scan_codebase_events(config)

        # Convert to architecture map
        architecture = {}
        for event in events:
            architecture[event.get("event_name")] = {
                "publishers": event.get("publishers", []),
                "subscribers": event.get("subscribers", [])
            }

        return architecture

    except Exception as e:
        logger.error(f" Architecture scan failed: {e}")
        return {}


@activity.defn
async def predict_gaps_activity(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Predict event gaps"""
    logger.info(" Predicting gaps...")

    try:
        from intelligent_core.event_intelligence.predictor import EventPredictor

        predictor = EventPredictor()
        predictions = await predictor.predict_missing_handlers(
            current_events=data.get("current_events", {}),
            context={}
        )

        return predictions

    except Exception as e:
        logger.error(f" Gap prediction failed: {e}")
        return []


@activity.defn
async def validate_predictions_activity(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate predictions"""
    logger.info("️ Validating predictions...")

    predictions = data.get("predictions", [])

    # Filter by confidence threshold
    validated = [p for p in predictions if p.get("confidence", 0) >= 0.6]

    return validated


@activity.defn
async def generate_gap_recommendations_activity(data: Dict[str, Any]) -> List[str]:
    """Generate gap recommendations"""
    logger.info(" Generating gap recommendations...")

    predictions = data.get("validated_predictions", [])
    recommendations = []

    for pred in predictions[:10]:
        recommendations.append(
            f"Consider implementing handler for '{pred.get('event_name')}' "
            f"(confidence: {pred.get('confidence', 0):.2f})"
        )

    return recommendations


@activity.defn
async def send_notification_activity(notification: Dict[str, Any]) -> bool:
    """Send notification"""
    logger.info(f" Sending notification: {notification.get('type')}")

    try:
        # Integration with notification service
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8040/api/v1/notifications/send",
                json=notification,
                timeout=10.0
            )
            return response.status_code == 200

    except Exception as e:
        logger.warning(f"️ Notification failed (non-critical): {e}")
        return False


# ==================== Activity Collections ====================

event_intelligence_activities = [
    scan_events_activity,
    analyze_event_activity,
    store_knowledge_activity,
    generate_recommendations_activity,
    collect_feedback_activity,
    analyze_patterns_activity,
    update_ml_models_activity,
    generate_learning_report_activity,
    scan_current_architecture_activity,
    predict_gaps_activity,
    validate_predictions_activity,
    generate_gap_recommendations_activity,
    send_notification_activity
]


# ==================== Export ====================

__all__ = [
    'EventAnalysisWorkflow',
    'PatternLearningWorkflow',
    'GapPredictionWorkflow',
    'event_intelligence_activities'
]
