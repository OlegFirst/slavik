"""
AI Coordinator - Bridge between MIO Manager and ai-foundation
==============================================================

Provides AI capabilities to MIO Manager:
- RAG-powered context retrieval
- LLM-powered decision making
- ML-powered predictions
- Context-aware analysis
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add intelligent-core to path
INTELLIGENT_CORE = Path(__file__).parent.parent.parent.parent.parent / 'intelligent-core'
sys.path.insert(0, str(INTELLIGENT_CORE))

# Import ai-foundation components
try:
    from intelligent_core.ai_foundation import (
        RAGPipeline,
        LLMRouter,
        ContextBuilder,
        PredictiveModel,
        AnomalyDetector
    )
    AI_FOUNDATION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ai-foundation not available: {e}")
    AI_FOUNDATION_AVAILABLE = False

logger = logging.getLogger(__name__)


class AICoordinator:
    """
    Coordinates AI capabilities for MIO Manager

    Provides:
    - Intelligent analysis of platform state
    - Context-aware decision making
    - Predictive insights
    - Conversational responses
    """

    def __init__(self):
        """Initialize AI components"""
        if not AI_FOUNDATION_AVAILABLE:
            logger.warning("AI Foundation not available - running in fallback mode")
            self.enabled = False
            return

        self.enabled = True

        try:
            # Initialize AI components
            self.llm = LLMRouter()
            self.rag = RAGPipeline()
            self.context = ContextBuilder()
            self.predictor = PredictiveModel()
            self.anomaly_detector = AnomalyDetector()

            logger.info(" AI Coordinator initialized with full capabilities")

        except Exception as e:
            logger.error(f" Failed to initialize AI components: {e}")
            self.enabled = False

    async def analyze_platform_state(
        self,
        metrics: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze platform state with AI

        Args:
            metrics: Platform metrics (CPU, memory, services, etc.)
            context: Additional context

        Returns:
            Analysis result with insights and recommendations
        """
        if not self.enabled:
            return self._fallback_analysis(metrics)

        try:
            # Build comprehensive context
            full_context = await self.context.build_context({
                'type': 'platform_analysis',
                'metrics': metrics,
                'additional_context': context or {},
                'timestamp': datetime.utcnow().isoformat()
            })

            # Retrieve relevant knowledge
            knowledge = await self.rag.retrieve(
                query="platform health analysis best practices",
                context=full_context
            )

            # Run anomaly detection
            anomalies = await self.anomaly_detector.detect(metrics)

            # Predict future issues
            predictions = await self.predictor.predict_issues(
                metrics=metrics,
                history=context.get('history', []) if context else []
            )

            # Generate AI insights
            analysis_prompt = f"""
            Analyze the following platform state:

            Metrics:
            {self._format_metrics(metrics)}

            Anomalies Detected:
            {self._format_anomalies(anomalies)}

            Predictions:
            {predictions}

            Relevant Knowledge:
            {knowledge}

            Provide:
            1. Overall health assessment (healthy/warning/critical)
            2. Key insights
            3. Recommended actions
            4. Priority level
            """

            insights = await self.llm.generate(
                prompt=analysis_prompt,
                context=full_context
            )

            return {
                'status': 'success',
                'health': self._extract_health(insights),
                'insights': insights,
                'anomalies': anomalies,
                'predictions': predictions,
                'recommendations': self._extract_recommendations(insights),
                'priority': self._extract_priority(insights),
                'analyzed_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f" AI analysis failed: {e}")
            return self._fallback_analysis(metrics)

    async def generate_conversational_response(
        self,
        user_message: str,
        conversation_history: List[Dict],
        platform_state: Dict
    ) -> Dict[str, Any]:
        """
        Generate conversational response (для chat interface)

        Args:
            user_message: User's message
            conversation_history: Previous messages
            platform_state: Current platform state

        Returns:
            Response with text, actions, and context
        """
        if not self.enabled:
            return {
                'response': "AI capabilities not available. Please check ai-foundation integration.",
                'actions': [],
                'confidence': 0.0
            }

        try:
            # Build conversation context
            conv_context = await self.context.build_context({
                'type': 'conversation',
                'current_message': user_message,
                'history': conversation_history,
                'platform_state': platform_state,
                'timestamp': datetime.utcnow().isoformat()
            })

            # Retrieve relevant knowledge
            knowledge = await self.rag.retrieve(
                query=user_message,
                context=conv_context
            )

            # Generate response
            response = await self.llm.chat(
                message=user_message,
                history=conversation_history,
                context=conv_context,
                knowledge=knowledge
            )

            # Parse for actionable items
            actions = await self._extract_actions(response, user_message)

            return {
                'response': response,
                'actions': actions,
                'confidence': 0.85,  # TODO: Calculate based on context
                'knowledge_sources': knowledge.get('sources', []),
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f" Conversational response generation failed: {e}")
            return {
                'response': f"Sorry, I encountered an error: {str(e)}",
                'actions': [],
                'confidence': 0.0
            }

    async def decide_action(
        self,
        situation: Dict[str, Any],
        available_actions: List[str],
        constraints: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make intelligent decision about what action to take

        Args:
            situation: Current situation description
            available_actions: List of possible actions
            constraints: Any constraints (budget, time, resources)

        Returns:
            Recommended action with reasoning
        """
        if not self.enabled:
            return self._fallback_decision(available_actions)

        try:
            # Build decision context
            decision_context = await self.context.build_context({
                'type': 'decision_making',
                'situation': situation,
                'available_actions': available_actions,
                'constraints': constraints or {},
                'timestamp': datetime.utcnow().isoformat()
            })

            # Retrieve relevant decision patterns
            patterns = await self.rag.retrieve(
                query=f"decision making for {situation.get('type', 'general')} situation",
                context=decision_context
            )

            # Generate decision
            decision_prompt = f"""
            Given the situation:
            {situation}

            Available actions:
            {', '.join(available_actions)}

            Constraints:
            {constraints}

            Relevant patterns from past decisions:
            {patterns}

            Recommend the best action and explain why.
            Consider: effectiveness, cost, risk, time.
            """

            decision = await self.llm.generate(
                prompt=decision_prompt,
                context=decision_context
            )

            return {
                'recommended_action': self._extract_action(decision, available_actions),
                'reasoning': decision,
                'confidence': self._calculate_confidence(decision, patterns),
                'alternatives': self._extract_alternatives(decision, available_actions),
                'risks': self._extract_risks(decision),
                'decided_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f" Decision making failed: {e}")
            return self._fallback_decision(available_actions)

    async def learn_from_outcome(
        self,
        decision: Dict[str, Any],
        action_taken: str,
        outcome: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Learn from decision outcome (for continuous improvement)

        Args:
            decision: Original decision
            action_taken: Action that was taken
            outcome: Result of the action

        Returns:
            Learning summary
        """
        if not self.enabled:
            return {'learned': False, 'reason': 'AI not available'}

        try:
            # Store learning example
            learning_example = {
                'decision': decision,
                'action': action_taken,
                'outcome': outcome,
                'timestamp': datetime.utcnow().isoformat()
            }

            # TODO: Store in database for pattern extraction
            # await self.learning_tracker.record(learning_example)

            logger.info(f" Learned from outcome: {outcome.get('success', False)}")

            return {
                'learned': True,
                'example_id': f"learning_{datetime.utcnow().timestamp()}",
                'will_improve': True
            }

        except Exception as e:
            logger.error(f" Learning failed: {e}")
            return {'learned': False, 'error': str(e)}

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _format_metrics(self, metrics: Dict) -> str:
        """Format metrics for LLM"""
        lines = []
        for key, value in metrics.items():
            lines.append(f"- {key}: {value}")
        return '\n'.join(lines)

    def _format_anomalies(self, anomalies: List) -> str:
        """Format anomalies for LLM"""
        if not anomalies:
            return "No anomalies detected"
        return '\n'.join([f"- {a}" for a in anomalies])

    def _extract_health(self, insights: str) -> str:
        """Extract health status from insights"""
        insights_lower = insights.lower()
        if 'critical' in insights_lower or 'severe' in insights_lower:
            return 'critical'
        elif 'warning' in insights_lower or 'concern' in insights_lower:
            return 'warning'
        else:
            return 'healthy'

    def _extract_recommendations(self, insights: str) -> List[str]:
        """Extract recommendations from insights"""
        # Simple extraction - TODO: improve with NLP
        recommendations = []
        lines = insights.split('\n')
        for line in lines:
            if 'recommend' in line.lower() or 'should' in line.lower():
                recommendations.append(line.strip())
        return recommendations

    def _extract_priority(self, insights: str) -> str:
        """Extract priority from insights"""
        insights_lower = insights.lower()
        if 'urgent' in insights_lower or 'immediate' in insights_lower:
            return 'high'
        elif 'soon' in insights_lower or 'important' in insights_lower:
            return 'medium'
        else:
            return 'low'

    async def _extract_actions(self, response: str, user_message: str) -> List[Dict]:
        """Extract actionable items from response"""
        actions = []

        # Simple pattern matching - TODO: improve with intent recognition
        response_lower = response.lower()
        message_lower = user_message.lower()

        if 'deploy' in message_lower and 'deploy' in response_lower:
            actions.append({'type': 'deploy', 'confidence': 0.8})

        if 'restart' in message_lower and 'restart' in response_lower:
            actions.append({'type': 'restart', 'confidence': 0.8})

        if 'create pr' in message_lower or 'pull request' in message_lower:
            actions.append({'type': 'create_pr', 'confidence': 0.9})

        return actions

    def _extract_action(self, decision: str, available_actions: List[str]) -> str:
        """Extract recommended action from decision"""
        decision_lower = decision.lower()
        for action in available_actions:
            if action.lower() in decision_lower:
                return action
        return available_actions[0]  # Default to first

    def _calculate_confidence(self, decision: str, patterns: Dict) -> float:
        """Calculate confidence in decision"""
        # Simple heuristic - TODO: improve with ML
        if patterns and len(patterns.get('matches', [])) > 5:
            return 0.9
        elif patterns and len(patterns.get('matches', [])) > 2:
            return 0.7
        else:
            return 0.5

    def _extract_alternatives(self, decision: str, available_actions: List[str]) -> List[str]:
        """Extract alternative actions from decision"""
        # TODO: improve extraction
        return [a for a in available_actions if a.lower() in decision.lower()]

    def _extract_risks(self, decision: str) -> List[str]:
        """Extract risks from decision"""
        risks = []
        lines = decision.split('\n')
        for line in lines:
            if 'risk' in line.lower() or 'concern' in line.lower():
                risks.append(line.strip())
        return risks

    # ========================================================================
    # Fallback Methods (когда AI не доступен)
    # ========================================================================

    def _fallback_analysis(self, metrics: Dict) -> Dict:
        """Fallback analysis without AI"""
        return {
            'status': 'fallback',
            'health': 'unknown',
            'insights': 'AI analysis not available',
            'recommendations': ['Check ai-foundation integration'],
            'priority': 'low'
        }

    def _fallback_decision(self, available_actions: List[str]) -> Dict:
        """Fallback decision without AI"""
        return {
            'recommended_action': available_actions[0] if available_actions else 'none',
            'reasoning': 'Fallback decision (AI not available)',
            'confidence': 0.0,
            'alternatives': [],
            'risks': ['AI not available for proper analysis']
        }
