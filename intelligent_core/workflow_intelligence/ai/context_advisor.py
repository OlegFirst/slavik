"""
 CONTEXT-AWARE AI ADVISOR

AI который ПОНИМАЕТ где пользователь в workflow и даёт контекстные советы.

Philosophy: AI doesn't hallucinate when it knows the context.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import json

from ..core.workflow_engine import WorkflowEngine, WorkflowContext
from ..case_library.models import CaseQuery, CaseSearchResult

logger = logging.getLogger(__name__)


# ============================================================================
# AI ADVISOR
# ============================================================================

class ContextAdvisor:
    """
    Context-Aware AI Advisor

    Даёт советы на основе:
    1. Текущего состояния workflow (state machine)
    2. Похожих успешных cases (case library)
    3. Benchmarks (статистика)
    4. ML predictions (risk factors)
    """

    def __init__(
        self,
        workflow_engine: WorkflowEngine,
        case_library,
        ml_predictor=None,
        llm_client=None
    ):
        """
        Args:
            workflow_engine: Workflow Engine instance
            case_library: Case Library repository
            ml_predictor: ML Predictor для предсказаний (optional)
            llm_client: LLM client (Claude, OpenAI, etc)
        """
        self.workflow_engine = workflow_engine
        self.case_library = case_library
        self.ml_predictor = ml_predictor
        self.llm_client = llm_client

        logger.info(f"Context Advisor initialized for module: {workflow_engine.module}")

    # ========================================================================
    # MAIN METHODS
    # ========================================================================

    async def get_contextual_advice(
        self,
        workflow_id: str,
        user_message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Получить контекстные советы

        Args:
            workflow_id: ID workflow
            user_message: Вопрос/запрос пользователя (если есть)
            **kwargs: Дополнительные параметры

        Returns:
            {
                "message": "AI advice text",
                "similar_cases": [...],
                "benchmarks": {...},
                "prediction": {...},
                "suggested_actions": [...],
                "context": {...}
            }
        """

        # 1. Получить workflow context
        context = await self.workflow_engine.get_context(workflow_id)

        # 2. Найти похожие successful cases
        similar_cases = await self._find_similar_cases(context)

        # 3. Получить benchmarks
        benchmarks = await self._get_benchmarks(context)

        # 4. Предсказать outcome (если ML доступен)
        prediction = await self._predict_outcome(context)

        # 5. Построить промпт с полным контекстом
        prompt = await self._build_contextual_prompt(
            context=context,
            similar_cases=similar_cases,
            benchmarks=benchmarks,
            prediction=prediction,
            user_message=user_message
        )

        # 6. Вызвать LLM
        response = await self._generate_advice(prompt)

        # 7. Извлечь suggested actions
        suggested_actions = self._extract_suggested_actions(response, context)

        return {
            "message": response.get("text", ""),
            "similar_cases": self._format_cases_for_response(similar_cases),
            "benchmarks": benchmarks,
            "prediction": prediction,
            "suggested_actions": suggested_actions,
            "context": context.to_dict(),
            "proactive": user_message is None
        }

    async def suggest_next_steps(self, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Предложить следующие шаги

        Returns:
            [{"action": "...", "reason": "...", "priority": "high"}]
        """
        context = await self.workflow_engine.get_context(workflow_id)

        suggestions = []

        # Если есть gaps, предложить их закрыть
        for gap in context.gaps:
            if gap.get("severity") == "high":
                suggestions.append({
                    "action": f"fix_{gap['type']}",
                    "action_label": f"Fix: {gap['message']}",
                    "reason": "Required to proceed",
                    "priority": "high",
                    "gap": gap
                })

        # Если gaps закрыты, предложить переход
        if context.can_proceed_to_next_stage:
            suggestions.append({
                "action": "proceed_to_next_stage",
                "action_label": f"Move to: {context.next_stage}",
                "reason": "All requirements met",
                "priority": "high",
                "next_stage": context.next_stage
            })

        # AI-powered suggestions (из available_actions)
        for action in context.available_actions:
            if action.get("requires_ai"):
                # Из similar cases понять когда это полезно
                if await self._should_suggest_ai_action(action, context):
                    suggestions.append({
                        "action": action["id"],
                        "action_label": action["label"],
                        "reason": "Based on similar successful workflows",
                        "priority": "medium",
                        "ai_powered": True
                    })

        return suggestions

    async def proactive_notification(self, workflow_id: str) -> Optional[Dict]:
        """
        Проактивное уведомление когда нужна помощь

        Returns:
            Notification dict или None
        """
        context = await self.workflow_engine.get_context(workflow_id)

        # Проверить если пользователь застрял
        if await self._is_stuck(context):
            return {
                "type": "stuck",
                "message": "Looks like you might need help. Would you like some suggestions?",
                "suggestions": await self.suggest_next_steps(workflow_id)
            }

        # Проверить если ML предсказывает риск
        if self.ml_predictor:
            prediction = await self.ml_predictor.predict(context)
            if prediction.get("risk_level") == "high":
                return {
                    "type": "risk_alert",
                    "message": "I detected some risk factors that might affect success.",
                    "risk_factors": prediction.get("risk_factors", []),
                    "recommendations": prediction.get("recommendations", [])
                }

        # Milestone reached
        if context.progress_percentage in [25, 50, 75]:
            return {
                "type": "milestone",
                "message": f"Great progress! You're {context.progress_percentage}% complete.",
                "benchmarks": await self._get_benchmarks(context)
            }

        return None

    # ========================================================================
    # SIMILAR CASES
    # ========================================================================

    async def _find_similar_cases(
        self,
        context: WorkflowContext,
        limit: int = 3
    ) -> List[CaseSearchResult]:
        """Найти похожие успешные cases"""

        # Извлечь org context из workflow data
        org_context = self._extract_org_context(context)

        # Построить query
        query = CaseQuery(
            module=context.module,
            industry=org_context.get("industry"),
            org_size=org_context.get("size"),
            maturity_level=org_context.get("maturity_level"),
            current_stage=context.current_stage,
            min_success_rate=0.8,  # Только успешные
            sort_by="similarity",
            limit=limit
        )

        # Semantic search query
        query.query_text = self._build_search_query(context)

        try:
            similar_cases = await self.case_library.find_similar(query)
            return similar_cases

        except Exception as e:
            logger.error(f"Failed to find similar cases: {e}")
            return []

    def _extract_org_context(self, context: WorkflowContext) -> Dict:
        """Извлечь organization context"""
        workflow_data = context.workflow_data

        return {
            "industry": workflow_data.get("industry", "unknown"),
            "size": workflow_data.get("org_size", "medium"),
            "maturity_level": workflow_data.get("maturity_level", "basic")
        }

    def _build_search_query(self, context: WorkflowContext) -> str:
        """Построить semantic search query"""

        # Описание текущей ситуации для semantic search
        query = f"""
        {context.module} workflow at stage {context.current_stage}.
        Progress: {context.progress_percentage}%.
        """

        if context.gaps:
            query += f"\nCurrent challenges: {', '.join(g['type'] for g in context.gaps)}."

        return query

    # ========================================================================
    # BENCHMARKS
    # ========================================================================

    async def _get_benchmarks(self, context: WorkflowContext) -> Optional[Dict]:
        """Получить benchmarks"""

        org_context = self._extract_org_context(context)

        try:
            benchmarks = await self.case_library.get_benchmarks(
                module=context.module,
                industry=org_context.get("industry")
            )

            return benchmarks.dict() if benchmarks else None

        except Exception as e:
            logger.error(f"Failed to get benchmarks: {e}")
            return None

    # ========================================================================
    # ML PREDICTION
    # ========================================================================

    async def _predict_outcome(self, context: WorkflowContext) -> Optional[Dict]:
        """Предсказать outcome через ML"""

        if not self.ml_predictor:
            return None

        try:
            prediction = await self.ml_predictor.predict(context)
            return prediction

        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return None

    # ========================================================================
    # PROMPT BUILDING
    # ========================================================================

    async def _build_contextual_prompt(
        self,
        context: WorkflowContext,
        similar_cases: List[CaseSearchResult],
        benchmarks: Optional[Dict],
        prediction: Optional[Dict],
        user_message: Optional[str]
    ) -> str:
        """
        Построить промпт с ПОЛНЫМ контекстом

        Это главный метод - здесь AI получает всё что нужно!
        """

        # Base context
        prompt = f"""
You are an expert {context.module.upper()} advisor helping a user complete their workflow.

# CURRENT SITUATION

Module: {context.module}
Current Stage: {context.current_stage_label}
Progress: {context.progress_percentage:.1f}%

Started: {context.started_at.strftime('%Y-%m-%d') if context.started_at else 'Unknown'}
Updated: {context.updated_at.strftime('%Y-%m-%d %H:%M')}
Estimated Completion: {context.estimated_completion.strftime('%Y-%m-%d') if context.estimated_completion else 'Unknown'}

Steps Completed: {len(context.completed_steps)}
"""

        # Gaps
        if context.gaps:
            prompt += f"\n# CURRENT GAPS (what's missing)\n\n"
            for gap in context.gaps:
                prompt += f"- [{gap['severity'].upper()}] {gap['message']}\n"

        # Issues
        if context.issues:
            prompt += f"\n# ISSUES (warnings)\n\n"
            for issue in context.issues:
                prompt += f"- [{issue['severity'].upper()}] {issue['message']}\n"

        # Available actions
        prompt += f"\n# AVAILABLE ACTIONS\n\n"
        for action in context.available_actions:
            prompt += f"- {action['label']}"
            if action.get('requires_ai'):
                prompt += " (AI-powered)"
            prompt += "\n"

        # Similar successful cases
        if similar_cases:
            prompt += f"\n# LEARN FROM SIMILAR SUCCESSFUL CASES\n\n"
            for i, result in enumerate(similar_cases, 1):
                case = result.case
                prompt += f"""
Case {i}: {case.organization_context.industry} organization ({case.organization_context.size})
- Completed in: {case.metrics.total_duration_days:.1f} days
- Steps: {case.metrics.total_steps}
- User satisfaction: {case.metrics.user_satisfaction or 'N/A'}/5

What worked well:
{self._format_list(case.success_patterns[:3])}

Challenges faced and resolved:
{self._format_challenges(case)}

Relevance: {', '.join(result.relevance_factors)}
"""

        # Benchmarks
        if benchmarks:
            prompt += f"\n# INDUSTRY BENCHMARKS\n\n"
            prompt += f"Average duration: {benchmarks.get('avg_duration_days', 'N/A'):.1f} days\n"
            prompt += f"Median duration: {benchmarks.get('median_duration_days', 'N/A'):.1f} days\n"
            prompt += f"Success rate: {(benchmarks.get('success_rate', 0) * 100):.1f}%\n"
            prompt += f"Your progress: {context.progress_percentage:.1f}%\n"

            if benchmarks.get('common_challenges'):
                prompt += f"\nCommon challenges in your industry:\n"
                for challenge in benchmarks['common_challenges'][:3]:
                    prompt += f"- {challenge}\n"

            if benchmarks.get('best_practices'):
                prompt += f"\nBest practices:\n"
                for practice in benchmarks['best_practices'][:5]:
                    prompt += f"- {practice}\n"

        # ML Prediction
        if prediction:
            prompt += f"\n# PREDICTIVE ANALYSIS\n\n"
            prompt += f"Success probability: {(prediction.get('success_probability', 0) * 100):.1f}%\n"
            prompt += f"Estimated duration: {prediction.get('estimated_duration_days', 0):.1f} days\n"
            prompt += f"Risk level: {prediction.get('risk_level', 'unknown').upper()}\n"

            if prediction.get('risk_factors'):
                prompt += f"\nRisk factors:\n"
                for factor in prediction['risk_factors']:
                    prompt += f"- {factor}\n"

        # User message
        if user_message:
            prompt += f"\n# USER QUESTION\n\n{user_message}\n"

        # Task
        prompt += f"""

# YOUR TASK

"""

        if user_message:
            prompt += f"""
Answer the user's question in the context of their current workflow state.
Be specific and actionable.
"""
        else:
            # Proactive advice
            prompt += f"""
Provide proactive guidance:
1. Acknowledge their current progress
2. Compare to similar organizations (if data available)
3. Suggest specific next steps
4. Warn about common pitfalls
5. Be encouraging but realistic

Use examples from similar cases to make advice concrete.
"""

        prompt += f"""

IMPORTANT:
- Be conversational and supportive
- Reference specific data (don't make up numbers)
- Suggest concrete actions from "AVAILABLE ACTIONS"
- Explain WHY based on similar cases or benchmarks
- Don't repeat what they already know
"""

        return prompt

    def _format_list(self, items: List[str], max_items: int = 5) -> str:
        """Format list для промпта"""
        return "\n".join(f"  • {item}" for item in items[:max_items])

    def _format_challenges(self, case) -> str:
        """Format challenges из case"""
        challenges = []

        for step in case.journey:
            for c in step.challenges:
                challenges.append(
                    f"  • {c.type}: {c.description}\n    Resolution: {c.resolution}"
                )

        return "\n".join(challenges[:3]) if challenges else "  No major challenges"

    # ========================================================================
    # LLM GENERATION
    # ========================================================================

    async def _generate_advice(self, prompt: str) -> Dict[str, Any]:
        """Генерация через LLM"""

        if not self.llm_client:
            # Fallback: template-based response
            return {
                "text": "AI advice unavailable (LLM client not configured). Please check available actions."
            }

        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.7  # Чуть больше creativity для советов
            )

            return {
                "text": response.get("text", ""),
                "model": response.get("model", "unknown"),
                "tokens_used": response.get("tokens_used", 0)
            }

        except Exception as e:
            logger.error(f"LLM generation failed: {e}", exc_info=True)
            return {
                "text": "I encountered an error generating advice. Please try again or check available actions."
            }

    # ========================================================================
    # ACTION EXTRACTION
    # ========================================================================

    def _extract_suggested_actions(
        self,
        response: Dict,
        context: WorkflowContext
    ) -> List[Dict]:
        """Извлечь suggested actions из response"""

        # TODO: Умный парсинг LLM response для извлечения actions

        # Пока просто возвращаем available_actions с приоритетами
        actions = []

        for action in context.available_actions:
            priority = "medium"

            # High priority if addresses gaps
            if any(gap.get("severity") == "high" for gap in context.gaps):
                if "fix" in action["id"] or "validate" in action["id"]:
                    priority = "high"

            # High priority if can proceed
            if context.can_proceed_to_next_stage:
                if "next" in action["id"] or "proceed" in action["id"]:
                    priority = "high"

            actions.append({
                **action,
                "priority": priority
            })

        return actions

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _format_cases_for_response(
        self,
        case_results: List[CaseSearchResult]
    ) -> List[Dict]:
        """Format cases для API response"""

        return [
            {
                "case_id": result.case.case_id,
                "organization": f"{result.case.organization_context.industry} ({result.case.organization_context.size})",
                "duration_days": result.case.metrics.total_duration_days,
                "success_patterns": result.case.success_patterns[:3],
                "satisfaction": result.case.metrics.user_satisfaction,
                "similarity_score": result.similarity_score,
                "relevance": result.relevance_factors
            }
            for result in case_results
        ]

    async def _should_suggest_ai_action(
        self,
        action: Dict,
        context: WorkflowContext
    ) -> bool:
        """Определить нужно ли предлагать AI action"""

        # Из similar cases: если AI помогал на этой стадии, предлагаем
        # TODO: Implement logic based on case library

        # Пока простая эвристика
        if context.progress_percentage < 30:
            return True  # Early stage, AI helps

        return False

    async def _is_stuck(self, context: WorkflowContext) -> bool:
        """Определить застрял ли пользователь"""

        # Если долго нет обновлений
        if context.updated_at:
            hours_since_update = (datetime.utcnow() - context.updated_at).total_seconds() / 3600

            if hours_since_update > 48:  # 2 дня
                return True

        # Если есть high-severity gaps долгое время
        if any(g.get("severity") == "high" for g in context.gaps):
            return True

        return False


# ============================================================================
# PROMPT BUILDER (для более сложных кейсов)
# ============================================================================

class AdvancedPromptBuilder:
    """Построение сложных промптов с разными стратегиями"""

    @staticmethod
    def build_multi_perspective_prompt(context: WorkflowContext) -> str:
        """Промпт с множественными перспективами"""

        return f"""
Analyze the workflow from multiple perspectives:

CFO Perspective: Financial impact and ROI
CTO Perspective: Technical feasibility and dependencies
CISO Perspective: Security and compliance risks
COO Perspective: Operational continuity

Current situation:
{json.dumps(context.to_dict(), indent=2)}

Provide recommendations from each perspective.
"""

    @staticmethod
    def build_scenario_analysis_prompt(context: WorkflowContext) -> str:
        """Промпт для scenario analysis"""

        return f"""
Analyze "what-if" scenarios:

1. Best case: Everything proceeds smoothly
2. Most likely case: Typical challenges occur
3. Worst case: Major obstacles arise

For each scenario:
- Probability
- Duration estimate
- Key risks
- Mitigation strategies

Current state:
{json.dumps(context.to_dict(), indent=2)}
"""
