"""
Risk Specialist - Dialogue Interface for Risk Office

User-facing conversational agent that:
- Understands natural language requests
- Detects intent
- Delegates to RiskExpert for execution
- Provides guided workflow experience
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "ai_experts"))

from base.expert_agent import ExpertAgent


class RiskSpecialist(ExpertAgent):
    """
    Risk Specialist - conversational interface for risk management

    Example:
        >>> specialist = RiskSpecialist(expert, workflow)
        >>> response = await specialist.chat(
        ...     "Help me identify risks for our payment processing system",
        ...     context={'process_id': 'proc_123', 'industry': 'fintech'}
        ... )
    """

    def __init__(self, expert, workflow, knowledge_sources=None):
        """
        Initialize Risk Specialist

        Args:
            expert: RiskExpert instance (business logic)
            workflow: RiskWorkflow instance (state machine)
            knowledge_sources: Optional knowledge graph, case library
        """
        self.expert = expert
        self.workflow = workflow

        super().__init__(
            name="Risk Specialist",
            role_description="Risk management expert specializing in FAIR methodology and ISO 22301 compliance",
            knowledge_sources=knowledge_sources or [],
            tools=[],  # Tools are in Expert layer
            temperature=0.4  # Balanced for dialogue + accuracy
        )

    def _specialization(self) -> str:
        return """risk identification, likelihood analysis, impact assessment, FAIR methodology, and treatment planning.

You excel at:
- Guided risk assessment workflows
- Explaining FAIR methodology (TEF × LM = ALE)
- Contextual risk recommendations based on industry and organization size
- Helping users progress through risk workflow stages
- Providing actionable mitigation strategies

Your approach:
- Start by understanding the business process context
- Guide users through workflow stages (identify → analyze → assess → plan)
- Use industry benchmarks and similar cases
- Be precise about risk quantification
- Recommend treatments based on risk appetite and budget
"""

    async def chat(
        self,
        message: str,
        context: Dict[str, Any],
        history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Chat interface for risk management

        Args:
            message: User message
            context: Context (process_id, org_context, etc)
            history: Conversation history

        Returns:
            Response with action taken and next steps
        """

        # 1. Get current workflow state
        workflow_status = await self.expert.get_workflow_status()
        current_stage = workflow_status.get('current_stage')
        gaps = workflow_status.get('gaps', [])

        # 2. Detect intent
        intent = self._detect_intent(message, current_stage)

        # 3. Execute appropriate action
        result = await self._execute_action(intent, message, context, workflow_status)

        # 4. Format conversational response
        response = self._format_response(result, workflow_status, intent)

        return response

    def _detect_intent(self, message: str, current_stage: str) -> str:
        """
        Detect user intent from message

        Returns:
            Intent type (identify_risks, analyze_likelihood, etc)
        """
        message_lower = message.lower()

        # Intent keywords
        if any(word in message_lower for word in ['identify', 'find', 'discover', 'what are', 'list']):
            if 'risk' in message_lower:
                return 'identify_risks'

        if any(word in message_lower for word in ['likelihood', 'probability', 'how often', 'frequency']):
            return 'analyze_likelihood'

        if any(word in message_lower for word in ['impact', 'consequence', 'damage', 'loss']):
            return 'calculate_impact'

        if any(word in message_lower for word in ['fair', 'ale', 'tef', 'loss magnitude']):
            return 'fair_analysis'

        if any(word in message_lower for word in ['treatment', 'mitigate', 'reduce', 'control', 'plan']):
            return 'plan_treatments'

        if any(word in message_lower for word in ['status', 'where are we', 'progress', 'summary']):
            return 'get_status'

        # Default: suggest next step based on workflow
        return 'suggest_next_step'

    async def _execute_action(
        self,
        intent: str,
        message: str,
        context: Dict[str, Any],
        workflow_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute action via RiskExpert

        Args:
            intent: Detected intent
            message: Original user message
            context: Context with process_id, org_context
            workflow_status: Current workflow state

        Returns:
            Execution result
        """
        org_context = context.get('org_context', {})
        process_id = context.get('process_id')

        try:
            if intent == 'identify_risks':
                if not process_id:
                    return {
                        "success": False,
                        "error": "process_id required for risk identification",
                        "hint": "Please specify which business process to analyze"
                    }

                return await self.expert.identify_risks(
                    process_id=process_id,
                    org_context=org_context,
                    user_input=message
                )

            elif intent == 'analyze_likelihood':
                risk_ids = context.get('risk_ids')
                if not risk_ids:
                    # Get risks from workflow state
                    risks = workflow_status.get('metadata', {}).get('risks', [])
                    risk_ids = [r.get('id') for r in risks if r.get('id')]

                if not risk_ids:
                    return {
                        "success": False,
                        "error": "No risks found to analyze",
                        "hint": "First identify risks before analyzing likelihood"
                    }

                return await self.expert.analyze_likelihood(
                    risk_ids=risk_ids,
                    org_context=org_context
                )

            elif intent == 'calculate_impact':
                risk_ids = context.get('risk_ids')
                if not risk_ids:
                    risks = workflow_status.get('metadata', {}).get('risks', [])
                    risk_ids = [r.get('id') for r in risks if r.get('id')]

                if not risk_ids:
                    return {
                        "success": False,
                        "error": "No risks found",
                        "hint": "First identify risks and analyze likelihood"
                    }

                return await self.expert.calculate_impact(
                    risk_ids=risk_ids,
                    org_context=org_context
                )

            elif intent == 'fair_analysis':
                risk_ids = context.get('risk_ids')
                if not risk_ids:
                    risks = workflow_status.get('metadata', {}).get('risks', [])
                    risk_ids = [r.get('id') for r in risks if r.get('id')]

                if not risk_ids:
                    return {
                        "success": False,
                        "error": "No risks found",
                        "hint": "Complete impact calculation first"
                    }

                return await self.expert.fair_analysis(
                    risk_ids=risk_ids,
                    org_context=org_context
                )

            elif intent == 'plan_treatments':
                risk_ids = context.get('risk_ids')
                if not risk_ids:
                    risks = workflow_status.get('metadata', {}).get('risks', [])
                    risk_ids = [r.get('id') for r in risks if r.get('id')]

                if not risk_ids:
                    return {
                        "success": False,
                        "error": "No risks found",
                        "hint": "Complete FAIR analysis first"
                    }

                return await self.expert.plan_treatments(
                    risk_ids=risk_ids,
                    org_context=org_context
                )

            elif intent == 'get_status':
                return {
                    "success": True,
                    "status": workflow_status
                }

            else:  # suggest_next_step
                return {
                    "success": True,
                    "suggestion": self._suggest_next_step(workflow_status)
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "intent": intent
            }

    def _suggest_next_step(self, workflow_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest next step based on workflow state

        Args:
            workflow_status: Current workflow state

        Returns:
            Suggestion with action and explanation
        """
        current_stage = workflow_status.get('current_stage')
        gaps = workflow_status.get('gaps', [])
        available_actions = workflow_status.get('available_actions', [])

        if current_stage == 'not_started':
            return {
                "action": "identify_risks",
                "message": "Let's start by identifying risks for your business process. Which process would you like to analyze?",
                "available_actions": available_actions
            }

        elif current_stage == 'identify_risks':
            if gaps:
                return {
                    "action": "add_more_risks",
                    "message": f"We need at least 1 risk identified. {gaps[0].get('message', '')}",
                    "available_actions": available_actions
                }
            else:
                return {
                    "action": "analyze_likelihood",
                    "message": "Great! Now let's analyze the likelihood of these risks occurring.",
                    "available_actions": available_actions
                }

        elif current_stage == 'analyze_likelihood':
            return {
                "action": "calculate_impact",
                "message": "Next, we'll calculate the impact of these risks across financial, operational, reputational, and regulatory dimensions.",
                "available_actions": available_actions
            }

        elif current_stage == 'calculate_impact':
            return {
                "action": "fair_analysis",
                "message": "Now let's perform FAIR analysis to calculate Annual Loss Expectancy (ALE = TEF × LM).",
                "available_actions": available_actions
            }

        elif current_stage == 'fair_analysis':
            return {
                "action": "plan_treatments",
                "message": "Let's plan risk treatments. Based on FAIR metrics, we'll recommend reduce/accept/transfer/avoid strategies.",
                "available_actions": available_actions
            }

        elif current_stage == 'treatment_planning':
            return {
                "action": "review_results",
                "message": "Almost done! Let's review the risk assessment results and treatment plans.",
                "available_actions": available_actions
            }

        elif current_stage == 'completed':
            return {
                "action": "none",
                "message": "Risk assessment completed! You can start a new assessment or review existing results.",
                "available_actions": available_actions
            }

        else:
            return {
                "action": "get_status",
                "message": "I'm not sure where we are in the workflow. Let me check the status.",
                "available_actions": available_actions
            }

    def _format_response(
        self,
        result: Dict[str, Any],
        workflow_status: Dict[str, Any],
        intent: str
    ) -> Dict[str, Any]:
        """
        Format execution result into conversational response

        Args:
            result: Execution result from RiskExpert
            workflow_status: Current workflow state
            intent: Original intent

        Returns:
            Formatted conversational response
        """
        if not result.get('success'):
            return {
                "message": f"❌ {result.get('error', 'Unknown error')}",
                "hint": result.get('hint'),
                "workflow_status": workflow_status,
                "success": False
            }

        # Format based on intent
        if intent == 'identify_risks':
            risks_count = result.get('risks_identified', 0)
            return {
                "message": f"✅ Identified {risks_count} risks for the process.",
                "details": {
                    "risks": result.get('risk_ids'),
                    "recommendations": result.get('recommendations', [])
                },
                "next_step": "Would you like to analyze the likelihood of these risks?",
                "workflow_status": {
                    "current_stage": result.get('workflow_state'),
                    "progress": "risks_identified"
                },
                "success": True
            }

        elif intent == 'analyze_likelihood':
            return {
                "message": f"✅ Likelihood analysis completed for {len(result.get('likelihood_scores', {}))} risks.",
                "details": {
                    "scores": result.get('likelihood_scores'),
                    "recommendations": result.get('recommendations', [])
                },
                "next_step": "Next, let's calculate the impact of these risks.",
                "workflow_status": {
                    "current_stage": result.get('workflow_state'),
                    "progress": "likelihood_analyzed"
                },
                "success": True
            }

        elif intent == 'calculate_impact':
            return {
                "message": f"✅ Impact calculation completed.",
                "details": {
                    "impacts": result.get('impact_scores'),
                    "recommendations": result.get('recommendations', [])
                },
                "next_step": "Now let's perform FAIR analysis to calculate Annual Loss Expectancy.",
                "workflow_status": {
                    "current_stage": result.get('workflow_state'),
                    "progress": "impact_calculated"
                },
                "success": True
            }

        elif intent == 'fair_analysis':
            total_ale = result.get('total_ale', 0)
            return {
                "message": f"✅ FAIR analysis completed. Total ALE: ${total_ale:,.2f}",
                "details": {
                    "fair_metrics": result.get('fair_metrics'),
                    "total_ale": total_ale,
                    "recommendations": result.get('recommendations', [])
                },
                "next_step": "Let's plan risk treatments based on these metrics.",
                "workflow_status": {
                    "current_stage": result.get('workflow_state'),
                    "progress": "fair_completed"
                },
                "success": True
            }

        elif intent == 'plan_treatments':
            treatments_count = len(result.get('treatments', {}))
            return {
                "message": f"✅ Treatment plans created for {treatments_count} risks.",
                "details": {
                    "treatments": result.get('treatments'),
                    "recommendations": result.get('recommendations', [])
                },
                "next_step": "Risk assessment complete! Review the results or start a new assessment.",
                "workflow_status": {
                    "current_stage": result.get('workflow_state'),
                    "progress": "treatments_planned"
                },
                "success": True
            }

        elif intent == 'get_status':
            return {
                "message": f"📊 Current stage: {workflow_status.get('current_stage')}",
                "details": workflow_status,
                "success": True
            }

        else:  # suggest_next_step
            suggestion = result.get('suggestion', {})
            return {
                "message": suggestion.get('message', 'What would you like to do?'),
                "available_actions": suggestion.get('available_actions', []),
                "success": True
            }
