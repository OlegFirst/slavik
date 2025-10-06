"""
Meta-Learning Engine - Learn from all AI colleague interactions

Improves routing accuracy, response quality, and predicts patterns
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class InteractionRecord:
    """Single interaction record for learning"""
    def __init__(
        self,
        query: str,
        colleague_used: str,
        intent_detected: str,
        routing_confidence: float,
        response_confidence: float,
        user_feedback: Optional[float] = None,
        actions_taken: int = 0,
        timestamp: Optional[datetime] = None
    ):
        self.query = query
        self.colleague_used = colleague_used
        self.intent_detected = intent_detected
        self.routing_confidence = routing_confidence
        self.response_confidence = response_confidence
        self.user_feedback = user_feedback
        self.actions_taken = actions_taken
        self.timestamp = timestamp or datetime.utcnow()


class MetaLearningEngine:
    """
    Meta-Learning Engine for AI Intelligence Layer

    Learns from all colleague interactions to:
    - Improve routing accuracy over time
    - Identify patterns in queries
    - Predict future issues
    - Optimize colleague performance
    - Recommend system improvements
    """

    def __init__(self):
        self.interaction_history: List[InteractionRecord] = []
        self.intent_patterns: Dict[str, Dict] = defaultdict(lambda: {
            "total_queries": 0,
            "colleagues_used": defaultdict(int),
            "avg_routing_confidence": [],
            "avg_response_confidence": [],
            "keywords": set()
        })
        self.colleague_performance: Dict[str, Dict] = defaultdict(lambda: {
            "total_queries": 0,
            "avg_response_confidence": [],
            "avg_user_feedback": [],
            "common_intents": defaultdict(int),
            "peak_hours": defaultdict(int)
        })
        self.routing_corrections: Dict[str, List[Dict]] = defaultdict(list)
        self.learning_stats = {
            "total_interactions": 0,
            "total_feedback_received": 0,
            "routing_accuracy_improvement": 0.0,
            "patterns_identified": 0
        }

        logger.info("MetaLearningEngine initialized")

    async def record_interaction(
        self,
        query: str,
        colleague_used: str,
        intent_detected: str,
        routing_confidence: float,
        response_confidence: float,
        actions_taken: int = 0
    ) -> Dict[str, Any]:
        """
        Record an interaction for learning

        Args:
            query: User query
            colleague_used: Which colleague handled it
            intent_detected: Detected intent type
            routing_confidence: Routing confidence score
            response_confidence: Response confidence score
            actions_taken: Number of actions user took

        Returns:
            Learning insights
        """
        record = InteractionRecord(
            query=query,
            colleague_used=colleague_used,
            intent_detected=intent_detected,
            routing_confidence=routing_confidence,
            response_confidence=response_confidence,
            actions_taken=actions_taken
        )

        self.interaction_history.append(record)
        self.learning_stats["total_interactions"] += 1

        # Update intent patterns
        self._update_intent_patterns(record)

        # Update colleague performance
        self._update_colleague_performance(record)

        # Detect patterns every 10 interactions
        if len(self.interaction_history) % 10 == 0:
            self._detect_patterns()

        logger.debug(f"Recorded interaction for {colleague_used}")

        return {
            "recorded": True,
            "total_interactions": len(self.interaction_history),
            "routing_accuracy": await self.get_routing_accuracy()
        }

    async def record_user_feedback(
        self,
        interaction_id: int,
        feedback_score: float,
        correct_colleague: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record user feedback for an interaction

        Args:
            interaction_id: Index in interaction history
            feedback_score: User satisfaction (0.0-1.0)
            correct_colleague: If user indicates wrong routing

        Returns:
            Updated learning insights
        """
        if interaction_id >= len(self.interaction_history):
            return {"error": "Invalid interaction_id"}

        record = self.interaction_history[interaction_id]
        record.user_feedback = feedback_score

        self.learning_stats["total_feedback_received"] += 1

        # Update colleague performance
        perf = self.colleague_performance[record.colleague_used]
        perf["avg_user_feedback"].append(feedback_score)

        # Record routing correction if needed
        if correct_colleague and correct_colleague != record.colleague_used:
            self.routing_corrections[record.intent_detected].append({
                "query": record.query[:100],
                "wrong_colleague": record.colleague_used,
                "correct_colleague": correct_colleague,
                "timestamp": datetime.utcnow().isoformat()
            })
            logger.info(f"Routing correction recorded: {record.colleague_used} → {correct_colleague}")

        return {
            "feedback_recorded": True,
            "total_feedback": self.learning_stats["total_feedback_received"],
            "colleague_avg_feedback": sum(perf["avg_user_feedback"]) / len(perf["avg_user_feedback"])
        }

    def _update_intent_patterns(self, record: InteractionRecord):
        """Update intent pattern learning"""
        pattern = self.intent_patterns[record.intent_detected]
        pattern["total_queries"] += 1
        pattern["colleagues_used"][record.colleague_used] += 1
        pattern["avg_routing_confidence"].append(record.routing_confidence)
        pattern["avg_response_confidence"].append(record.response_confidence)

        # Extract keywords
        keywords = set(record.query.lower().split())
        pattern["keywords"].update(keywords)

    def _update_colleague_performance(self, record: InteractionRecord):
        """Update colleague performance metrics"""
        perf = self.colleague_performance[record.colleague_used]
        perf["total_queries"] += 1
        perf["avg_response_confidence"].append(record.response_confidence)
        perf["common_intents"][record.intent_detected] += 1

        # Track peak usage hours
        hour = record.timestamp.hour
        perf["peak_hours"][hour] += 1

    def _detect_patterns(self):
        """Detect patterns in interaction history"""
        recent = self.interaction_history[-50:]  # Last 50 interactions

        # Pattern 1: Commonly misrouted intents
        intent_accuracy = {}
        for intent, data in self.intent_patterns.items():
            if data["total_queries"] >= 3:
                corrections = len(self.routing_corrections.get(intent, []))
                accuracy = 1.0 - (corrections / data["total_queries"])
                intent_accuracy[intent] = accuracy

        # Pattern 2: Peak usage times
        hour_usage = defaultdict(int)
        for record in recent:
            hour_usage[record.timestamp.hour] += 1

        # Pattern 3: Colleague specialization strength
        colleague_strength = {}
        for colleague, perf in self.colleague_performance.items():
            if perf["avg_response_confidence"]:
                avg_conf = sum(perf["avg_response_confidence"]) / len(perf["avg_response_confidence"])
                colleague_strength[colleague] = avg_conf

        self.learning_stats["patterns_identified"] += 1
        logger.info("Pattern detection complete")

    async def get_routing_accuracy(self) -> float:
        """
        Calculate overall routing accuracy

        Returns:
            Routing accuracy (0.0-1.0)
        """
        if not self.interaction_history:
            return 0.0

        total_interactions = len(self.interaction_history)
        total_corrections = sum(len(corrections) for corrections in self.routing_corrections.values())

        accuracy = 1.0 - (total_corrections / total_interactions) if total_interactions > 0 else 0.0
        return round(accuracy, 3)

    async def get_routing_recommendation(self, query: str, intent: str) -> Optional[str]:
        """
        Get ML-based routing recommendation

        Args:
            query: User query
            intent: Detected intent

        Returns:
            Recommended colleague or None
        """
        # Check if we have learned patterns for this intent
        if intent in self.intent_patterns:
            pattern = self.intent_patterns[intent]

            # Find most successful colleague for this intent
            colleagues = pattern["colleagues_used"]
            if colleagues:
                # Consider routing corrections
                corrections = self.routing_corrections.get(intent, [])
                if corrections:
                    # Prefer corrected colleague
                    correct_colleague_counts = defaultdict(int)
                    for correction in corrections:
                        correct_colleague_counts[correction["correct_colleague"]] += 1

                    if correct_colleague_counts:
                        recommended = max(correct_colleague_counts.items(), key=lambda x: x[1])[0]
                        logger.info(f"ML recommendation for {intent}: {recommended} (learned from corrections)")
                        return recommended

                # Otherwise use most common
                recommended = max(colleagues.items(), key=lambda x: x[1])[0]
                return recommended

        return None

    async def get_performance_insights(self, colleague: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance insights for colleague(s)

        Args:
            colleague: Specific colleague or None for all

        Returns:
            Performance insights
        """
        if colleague:
            if colleague not in self.colleague_performance:
                return {"error": f"No data for {colleague}"}

            perf = self.colleague_performance[colleague]
            return {
                "colleague": colleague,
                "total_queries": perf["total_queries"],
                "avg_response_confidence": round(sum(perf["avg_response_confidence"]) / len(perf["avg_response_confidence"]), 3) if perf["avg_response_confidence"] else 0.0,
                "avg_user_feedback": round(sum(perf["avg_user_feedback"]) / len(perf["avg_user_feedback"]), 3) if perf["avg_user_feedback"] else None,
                "top_intents": sorted(perf["common_intents"].items(), key=lambda x: x[1], reverse=True)[:3],
                "peak_hours": sorted(perf["peak_hours"].items(), key=lambda x: x[1], reverse=True)[:3]
            }
        else:
            # All colleagues summary
            return {
                "total_colleagues": len(self.colleague_performance),
                "colleagues": [
                    {
                        "name": col,
                        "queries": perf["total_queries"],
                        "avg_confidence": round(sum(perf["avg_response_confidence"]) / len(perf["avg_response_confidence"]), 3) if perf["avg_response_confidence"] else 0.0
                    }
                    for col, perf in self.colleague_performance.items()
                ]
            }

    async def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get overall learning insights and recommendations

        Returns:
            Learning insights dictionary
        """
        routing_accuracy = await self.get_routing_accuracy()

        # Identify improvement areas
        improvements = []

        # Check for frequently misrouted intents
        for intent, corrections in self.routing_corrections.items():
            if len(corrections) >= 3:
                improvements.append(f"Intent '{intent}' frequently misrouted - consider routing rules update")

        # Check for low-confidence patterns
        low_conf_intents = []
        for intent, pattern in self.intent_patterns.items():
            if pattern["avg_routing_confidence"]:
                avg_conf = sum(pattern["avg_routing_confidence"]) / len(pattern["avg_routing_confidence"])
                if avg_conf < 0.7:
                    low_conf_intents.append(intent)

        if low_conf_intents:
            improvements.append(f"Low routing confidence for: {', '.join(low_conf_intents[:3])}")

        # Identify top performing colleagues
        top_performers = sorted(
            self.colleague_performance.items(),
            key=lambda x: sum(x[1]["avg_response_confidence"]) / len(x[1]["avg_response_confidence"]) if x[1]["avg_response_confidence"] else 0,
            reverse=True
        )[:3]

        return {
            "total_interactions": len(self.interaction_history),
            "routing_accuracy": routing_accuracy,
            "total_feedback": self.learning_stats["total_feedback_received"],
            "patterns_identified": self.learning_stats["patterns_identified"],
            "intent_patterns_learned": len(self.intent_patterns),
            "routing_corrections_made": sum(len(c) for c in self.routing_corrections.values()),
            "top_performers": [{"colleague": name, "avg_confidence": round(sum(perf["avg_response_confidence"]) / len(perf["avg_response_confidence"]), 3) if perf["avg_response_confidence"] else 0.0} for name, perf in top_performers],
            "improvement_recommendations": improvements
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get quick statistics"""
        return {
            "meta_learning_engine": "active",
            "total_interactions": len(self.interaction_history),
            "intents_tracked": len(self.intent_patterns),
            "colleagues_tracked": len(self.colleague_performance),
            "total_feedback": self.learning_stats["total_feedback_received"]
        }
