"""
Risk Specialist
Conversational specialist for Risk Management
"""
from typing import Dict, List, Any, Optional
from ..base_specialist import BaseSpecialist


class RiskSpecialist(BaseSpecialist):
    """
    Risk Management Specialist

    Conversational AI for:
    - Risk analysis (FAIR methodology)
    - Risk treatment planning
    - Risk monitoring
    """

    def _detect_intent(self, message: str, context: Dict[str, Any]) -> str:
        """
        Detect user intent from message

        Intents:
        - analyze_risk: Analyze risks for process
        - calculate_fair: Calculate FAIR metrics
        - suggest_mitigation: Suggest risk mitigation
        - create_treatment: Create treatment plan
        - monitor_risk: Setup risk monitoring
        """
        message_lower = message.lower()

        # Risk analysis
        if any(word in message_lower for word in ['analyze', 'анализ', 'риск', 'risk']):
            if 'fair' in message_lower:
                return 'calculate_fair'
            return 'analyze_risk'

        # Mitigation
        if any(word in message_lower for word in ['mitigat', 'снизить', 'reduce', 'treat']):
            return 'suggest_mitigation'

        # Treatment plan
        if any(word in message_lower for word in ['plan', 'план', 'create', 'создать']):
            return 'create_treatment'

        # Monitoring
        if any(word in message_lower for word in ['monitor', 'мониторинг', 'track', 'отслежива']):
            return 'monitor_risk'

        # Default
        return 'analyze_risk'

    async def _delegate_to_engine(
        self,
        intent: str,
        context: Dict[str, Any],
        knowledge: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Delegate to Risk Engine

        Maps intent to engine action
        """
        if not self.engine:
            return {
                'response': 'Risk Engine not configured',
                'data': {},
                'actions': [],
                'confidence': 0.0
            }

        # Map intent to action
        action_map = {
            'analyze_risk': ('analyze_process_risks', {
                'process_id': context.get('process_id'),
                'context': context
            }),
            'calculate_fair': ('calculate_fair', {
                'process_id': context.get('process_id'),
                'threat_data': context.get('threat_data', {})
            }),
            'suggest_mitigation': ('suggest_mitigations', {
                'risk_id': context.get('risk_id')
            }),
            'create_treatment': ('create_treatment_plan', {
                'risk_id': context.get('risk_id'),
                'treatment_type': context.get('treatment_type', 'reduce'),
                'responsible': context.get('responsible')
            })
        }

        if intent not in action_map:
            return {
                'response': f'Unknown intent: {intent}',
                'data': {},
                'actions': []
            }

        action, params = action_map[intent]

        # Execute via engine
        try:
            result = await self.engine.execute(action, params)
            return result
        except Exception as e:
            return {
                'response': f'Error executing {action}: {str(e)}',
                'data': {},
                'actions': [],
                'confidence': 0.0
            }

    def _suggest_actions(self, intent: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest next actions based on intent"""
        actions = []

        if intent == 'analyze_risk':
            # After risk analysis, suggest treatment
            actions.extend([
                {
                    'type': 'create_treatment',
                    'label': '📋 Create Treatment Plan',
                    'data': data
                },
                {
                    'type': 'calculate_fair',
                    'label': '🔢 Calculate FAIR Metrics',
                    'data': data
                }
            ])

        elif intent == 'calculate_fair':
            # After FAIR, suggest mitigation
            actions.append({
                'type': 'suggest_mitigation',
                'label': '💡 Suggest Mitigations',
                'data': data
            })

        elif intent == 'suggest_mitigation':
            # After mitigation suggestions, create plan
            actions.append({
                'type': 'create_treatment',
                'label': '✅ Create Treatment Plan',
                'data': data
            })

        return actions

    def _format_response(
        self,
        engine_result: Dict[str, Any],
        pdca_stage: str,
        knowledge: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Format response with risk-specific formatting"""
        # Base formatting
        response = super()._format_response(engine_result, pdca_stage, knowledge)

        # Add PDCA guidance for risk management
        pdca_guidance = {
            'plan': '📋 Planning: Identify risks and scope',
            'do': '🔍 Analysis: Analyzing risks with FAIR methodology',
            'check': '✅ Review: Validating risk assessment',
            'act': '🚀 Action: Implementing risk treatments'
        }

        # Enhance response
        response['pdca_guidance'] = pdca_guidance.get(pdca_stage, '')

        # Add risk-specific metadata
        response['metadata']['risk_analysis'] = True
        response['metadata']['fair_methodology'] = True

        return response
