"""
AI Foundation Integration for Database Intelligence

Connects DB Intelligence with AI Foundation for advanced analysis and decision-making.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class AIIntegration:
    """
    Integrates Database Intelligence with AI Foundation

    Data Flow:
    DB Intelligence → EventBus → AI Orchestrator → AI Foundation → Decision → Action
    """

    def __init__(
        self,
        orchestrator_url: str = "http://localhost:8002",
        ai_foundation_url: str = "http://localhost:8030"
    ):
        self.orchestrator_url = orchestrator_url
        self.ai_foundation_url = ai_foundation_url

    # =========================================================================
    # EventBus Integration
    # =========================================================================

    async def publish_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        details: Any
    ):
        """
        Publish alert to EventBus for AI Orchestrator to consume
        """
        try:
            from infrastructure.eventbus import create_eventbus, Event

            bus = create_eventbus('redis')  # or 'rabbitmq'

            event = Event.create(
                event_type=f"db.alert.{severity}",
                data={
                    "alert_type": alert_type,
                    "severity": severity,
                    "message": message,
                    "details": details,
                    "source": "db-intelligence",
                    "timestamp": datetime.now().isoformat()
                },
                source="db-intelligence"
            )

            await bus.publish(event)
            logger.info(f"Published alert: {alert_type} ({severity})")

        except Exception as e:
            logger.error(f"Failed to publish alert to EventBus: {e}")

    async def publish_optimization_suggestion(
        self,
        query_hash: str,
        query_text: str,
        issue_type: str,
        severity: str,
        suggestion: str,
        estimated_improvement: str
    ):
        """
        Publish optimization suggestion for AI analysis
        """
        try:
            from infrastructure.eventbus import create_eventbus, Event

            bus = create_eventbus('redis')

            event = Event.create(
                event_type="db.optimization.suggestion",
                data={
                    "query_hash": query_hash,
                    "query_text": query_text[:500],  # Truncate
                    "issue_type": issue_type,
                    "severity": severity,
                    "suggestion": suggestion,
                    "estimated_improvement": estimated_improvement,
                    "timestamp": datetime.now().isoformat()
                },
                source="db-intelligence"
            )

            await bus.publish(event)
            logger.info(f"Published optimization suggestion: {issue_type}")

        except Exception as e:
            logger.error(f"Failed to publish suggestion: {e}")

    async def subscribe_to_ai_events(self):
        """
        Subscribe to AI-generated events
        """
        try:
            from infrastructure.eventbus import create_eventbus

            bus = create_eventbus('redis')

            # When AI completes analysis
            await bus.subscribe('ai.analysis.completed', self.handle_ai_analysis_completed)

            # When AI makes recommendation
            await bus.subscribe('ai.recommendation.created', self.handle_ai_recommendation)

            # When workflow executes query
            await bus.subscribe('workflow.query.executed', self.handle_workflow_query)

            logger.info("Subscribed to AI events")

        except Exception as e:
            logger.error(f"Failed to subscribe to AI events: {e}")

    async def handle_ai_analysis_completed(self, event):
        """Handle AI analysis completion event"""
        logger.info(f"AI analysis completed: {event.data.get('analysis_id')}")
        # Could track which queries were used during analysis

    async def handle_ai_recommendation(self, event):
        """Handle AI recommendation event"""
        logger.info(f"AI recommendation created: {event.data.get('recommendation_type')}")

    async def handle_workflow_query(self, event):
        """Handle workflow query execution event"""
        logger.debug(f"Workflow query executed: {event.data.get('duration_ms')}ms")

    # =========================================================================
    # AI Foundation Direct API
    # =========================================================================

    async def analyze_query_with_ai(
        self,
        query: str,
        explain_plan: List[str],
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send query to AI Foundation for advanced analysis

        Uses LLM to understand query semantics and provide intelligent suggestions
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ai_foundation_url}/llm/analyze",
                    json={
                        "type": "database_query_analysis",
                        "query": query,
                        "explain_plan": explain_plan,
                        "metrics": metrics,
                        "prompt": f"""
                        Analyze this database query for optimization opportunities:

                        Query: {query}

                        EXPLAIN output:
                        {chr(10).join(explain_plan)}

                        Metrics:
                        - Average duration: {metrics.get('avg_duration_ms')}ms
                        - Execution count: {metrics.get('execution_count')}
                        - Max duration: {metrics.get('max_duration_ms')}ms

                        Provide:
                        1. Semantic analysis - what is this query trying to achieve?
                        2. Performance issues identified
                        3. Specific optimization recommendations
                        4. Estimated performance improvement
                        5. Risk assessment for applying optimizations
                        """
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"AI analysis failed: {response.status_code}")
                    return {"error": "AI analysis unavailable"}

        except Exception as e:
            logger.error(f"Failed to analyze query with AI: {e}")
            return {"error": str(e)}

    async def get_ai_recommendation_for_suggestion(
        self,
        suggestion: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get AI recommendation on whether to apply a database optimization

        Returns:
        {
            "should_apply": bool,
            "confidence": float (0-1),
            "reasoning": str,
            "risks": List[str],
            "estimated_improvement": str
        }
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ai_foundation_url}/llm/recommend",
                    json={
                        "type": "database_optimization_decision",
                        "suggestion": suggestion,
                        "prompt": f"""
                        Database Intelligence suggests the following optimization:

                        Issue: {suggestion['issue_type']}
                        Severity: {suggestion['severity']}
                        Query: {suggestion['query_text']}
                        Suggestion: {suggestion['suggestion']}

                        Should we apply this optimization automatically?

                        Consider:
                        1. Is it safe to apply without human review?
                        2. What are the potential risks?
                        3. What's the estimated performance improvement?
                        4. Could this break existing functionality?

                        Respond with:
                        - should_apply: true/false
                        - confidence: 0.0-1.0
                        - reasoning: detailed explanation
                        - risks: list of potential risks
                        - estimated_improvement: quantified if possible
                        """
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "should_apply": False,
                        "confidence": 0.0,
                        "reasoning": "AI recommendation unavailable",
                        "risks": ["Unable to assess risks"],
                        "estimated_improvement": "Unknown"
                    }

        except Exception as e:
            logger.error(f"Failed to get AI recommendation: {e}")
            return {
                "should_apply": False,
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}",
                "risks": ["AI service unavailable"],
                "estimated_improvement": "Unknown"
            }

    # =========================================================================
    # AI Orchestrator Integration
    # =========================================================================

    async def notify_orchestrator_of_critical_issue(
        self,
        issue_type: str,
        severity: str,
        details: Dict[str, Any]
    ):
        """
        Directly notify AI Orchestrator of critical database issues
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/events/critical",
                    json={
                        "source": "db-intelligence",
                        "issue_type": issue_type,
                        "severity": severity,
                        "details": details,
                        "timestamp": datetime.now().isoformat(),
                        "requires_immediate_action": severity == "critical"
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    logger.info(f"Notified orchestrator of {issue_type}")
                else:
                    logger.warning(f"Orchestrator notification failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to notify orchestrator: {e}")

    async def request_orchestrator_action(
        self,
        action_type: str,
        action_data: Dict[str, Any],
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Request AI Orchestrator to take specific action

        Actions:
        - kill_query: Kill a specific query
        - create_index: Create database index
        - vacuum_table: Run VACUUM on table
        - alert_developers: Send notification to developers
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.orchestrator_url}/actions/request",
                    json={
                        "requester": "db-intelligence",
                        "action_type": action_type,
                        "action_data": action_data,
                        "priority": priority,
                        "timestamp": datetime.now().isoformat()
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Action request accepted: {result.get('action_id')}")
                    return result
                else:
                    logger.error(f"Action request failed: {response.status_code}")
                    return {"error": "Action request failed"}

        except Exception as e:
            logger.error(f"Failed to request action: {e}")
            return {"error": str(e)}

    # =========================================================================
    # RAG Integration (for context-aware recommendations)
    # =========================================================================

    async def enrich_suggestion_with_context(
        self,
        suggestion: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich optimization suggestion with historical context from RAG

        Queries knowledge base for:
        - Similar past optimizations
        - Domain-specific best practices
        - Historical performance data
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ai_foundation_url}/rag/query",
                    json={
                        "query": f"Database optimization: {suggestion['issue_type']} for query type {suggestion.get('query_type', 'unknown')}",
                        "collection": "database_optimizations",
                        "limit": 5
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    rag_results = response.json()

                    # Enrich suggestion with RAG context
                    suggestion['context'] = {
                        "similar_cases": rag_results.get('results', []),
                        "best_practices": rag_results.get('recommendations', []),
                        "success_rate": rag_results.get('success_rate', 0.0)
                    }

                    return suggestion
                else:
                    return suggestion  # Return original if RAG fails

        except Exception as e:
            logger.error(f"Failed to enrich with RAG context: {e}")
            return suggestion

    # =========================================================================
    # Learning Loop (feedback to AI)
    # =========================================================================

    async def report_optimization_outcome(
        self,
        suggestion_id: str,
        applied: bool,
        outcome: Dict[str, Any]
    ):
        """
        Report outcome of applied optimization back to AI for learning

        This creates a feedback loop for AI to improve future recommendations
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ai_foundation_url}/learning/feedback",
                    json={
                        "type": "database_optimization_outcome",
                        "suggestion_id": suggestion_id,
                        "applied": applied,
                        "outcome": outcome,
                        "timestamp": datetime.now().isoformat()
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    logger.info(f"Reported optimization outcome for {suggestion_id}")
                else:
                    logger.warning(f"Failed to report outcome: {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to report outcome: {e}")

    async def get_learned_patterns(self) -> List[Dict[str, Any]]:
        """
        Get AI-learned patterns about database performance

        Returns patterns like:
        - Queries of type X are usually slow
        - Index on column Y improves performance by Z%
        - Vacuuming table W should happen every N days
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ai_foundation_url}/learning/patterns",
                    params={"domain": "database_performance"},
                    timeout=10.0
                )

                if response.status_code == 200:
                    return response.json().get('patterns', [])
                else:
                    return []

        except Exception as e:
            logger.error(f"Failed to get learned patterns: {e}")
            return []


# =============================================================================
# Global Instance
# =============================================================================

_ai_integration: Optional[AIIntegration] = None


def get_ai_integration() -> AIIntegration:
    """Get global AI integration instance"""
    global _ai_integration
    if _ai_integration is None:
        import os
        _ai_integration = AIIntegration(
            orchestrator_url=os.getenv("ORCHESTRATOR_URL", "http://localhost:8002"),
            ai_foundation_url=os.getenv("AI_FOUNDATION_URL", "http://localhost:8030")
        )
    return _ai_integration
