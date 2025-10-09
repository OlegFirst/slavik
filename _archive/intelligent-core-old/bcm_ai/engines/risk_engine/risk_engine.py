"""
Risk Engine
Business logic for Risk Management
"""
from typing import Dict, Any, List, Optional
from ..base_engine import BaseEngine
from .risk_tools import RiskTools


class RiskEngine(BaseEngine):
    """
    Risk Management Engine

    Responsibilities:
    - Process risk analysis (FAIR methodology)
    - Risk treatment planning
    - Integration with BIA data
    - Case Library learning
    """

    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute risk action

        Actions:
        - analyze_process_risks: Analyze risks for a process
        - calculate_fair: Calculate FAIR risk metrics
        - suggest_mitigations: Suggest risk mitigations
        - create_treatment_plan: Create risk treatment plan
        """
        action_map = {
            'analyze_process_risks': self.analyze_process_risks,
            'calculate_fair': self.calculate_fair,
            'suggest_mitigations': self.suggest_mitigations,
            'create_treatment_plan': self.create_treatment_plan
        }

        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")

        return await handler(**params)

    async def analyze_process_risks(
        self,
        process_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze risks for a process

        Steps:
        1. Get process details (Tool)
        2. Get dependencies (Tool)
        3. Get existing risks (Tool)
        4. Analyze with LLM (Analyzer)
        5. Find similar cases (Case Library)
        6. Synthesize result
        7. Save to DB (Tool)
        8. Record to Case Library
        """
        # 1. Get process data
        process = await self._use_tool('get_process_details', {'process_id': process_id})
        dependencies = await self._use_tool('get_process_dependencies', {'process_id': process_id})
        existing_risks = await self._use_tool('get_existing_risks', {'process_id': process_id})

        # 2. Prepare context for analyzer
        analysis_context = {
            'process': process,
            'dependencies': dependencies,
            'existing_risks': existing_risks,
            'industry': context.get('industry') if context else None,
            'org_size': context.get('size') if context else None
        }

        # 3. LLM Analysis
        llm_analysis = await self._analyze_with_analyzer(analysis_context)

        # 4. Find similar cases
        similar_cases = await self._find_similar_cases({
            'industry': context.get('industry') if context else None,
            'module': 'risk',
            'action_type': 'analyze_process_risks'
        })

        # 5. ML Prediction (optional)
        ml_prediction = None
        if self.ml_predictor:
            ml_prediction = await self._predict_with_ml(
                'risk_severity',
                {
                    'process_tier': process.get('tier'),
                    'rto_hours': process.get('rto_hours'),
                    'dependency_count': len(dependencies),
                    'spof_count': sum(1 for d in dependencies if d.get('single_point_of_failure'))
                }
            )

        # 6. Synthesize result
        result = self._synthesize_result(
            tool_data={
                'process': process,
                'dependencies': dependencies,
                'existing_risks': existing_risks
            },
            analysis=llm_analysis,
            similar_cases=similar_cases,
            ml_prediction=ml_prediction
        )

        # 7. Save analysis to DB
        analysis_id = await self._use_tool('save_risk_analysis', {
            'analysis': {
                'process_id': process_id,
                'severity': self._calculate_severity(llm_analysis, dependencies),
                'vulnerabilities': llm_analysis.get('insights', []),
                'recommendations': llm_analysis.get('recommendations', []),
                'fair_analysis': {},  # TODO: implement FAIR
                'metadata': {
                    'similar_cases_count': len(similar_cases),
                    'ml_prediction': ml_prediction
                }
            }
        })

        # 8. Record to Case Library
        if analysis_id:
            await self._record_to_case_library({
                'industry': context.get('industry') if context else None,
                'module': 'risk',
                'action_type': 'analyze_process_risks',
                'context': analysis_context,
                'result': result,
                'success': True
            })

        # 9. Add analysis_id to result
        result['data']['analysis_id'] = analysis_id

        return result

    async def calculate_fair(
        self,
        process_id: str,
        threat_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate FAIR risk metrics

        FAIR: Factor Analysis of Information Risk
        TEF (Threat Event Frequency) × LM (Loss Magnitude) = ALE (Annual Loss Expectancy)
        """
        # Get process data
        process = await self._use_tool('get_process_details', {'process_id': process_id})

        # FAIR calculation
        tef = threat_data.get('threat_event_frequency', 1)  # events/year
        lm = threat_data.get('loss_magnitude', 0)  # $ per event
        ale = tef * lm

        # Prepare context for LLM interpretation
        fair_context = {
            'process': process,
            'tef': tef,
            'lm': lm,
            'ale': ale,
            'threat_data': threat_data
        }

        # LLM analysis of FAIR results
        analysis = await self._analyze_with_analyzer(fair_context)

        return {
            'response': f"🔢 FAIR Analysis:\n"
                       f"  • Threat Event Frequency: {tef}/year\n"
                       f"  • Loss Magnitude: ${lm:,}\n"
                       f"  • Annual Loss Expectancy: ${ale:,}\n\n"
                       f"{analysis.get('insights', [''])[0] if analysis.get('insights') else ''}",
            'data': {
                'fair_metrics': {
                    'tef': tef,
                    'lm': lm,
                    'ale': ale
                },
                'analysis': analysis
            },
            'actions': [],
            'confidence': analysis.get('confidence', 0.0),
            'timestamp': result.get('timestamp')
        }

    async def suggest_mitigations(self, risk_id: str) -> Dict[str, Any]:
        """Suggest risk mitigation strategies"""
        # Get risk details
        risks = await self._use_tool('get_risk_assessments', {'process_id': None})
        risk = next((r for r in risks if r.get('id') == risk_id), None)

        if not risk:
            return {'response': 'Risk not found', 'data': {}, 'actions': []}

        # Analyze with LLM
        analysis = await self._analyze_with_analyzer({'risk': risk})

        return self._synthesize_result(
            tool_data={'risk': risk},
            analysis=analysis,
            similar_cases=[]
        )

    async def create_treatment_plan(
        self,
        risk_id: str,
        treatment_type: str,
        responsible: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create risk treatment plan"""
        # Get risk details
        risks = await self._use_tool('get_risk_assessments', {'process_id': None})
        risk = next((r for r in risks if r.get('id') == risk_id), None)

        if not risk:
            return {'response': 'Risk not found', 'data': {}, 'actions': []}

        # Get AI recommendations
        analysis = await self._analyze_with_analyzer({
            'risk': risk,
            'treatment_type': treatment_type
        })

        # Create treatment
        treatment_id = await self._use_tool('create_risk_treatment', {
            'treatment': {
                'risk_id': risk_id,
                'process_id': risk.get('process_id'),
                'treatment_type': treatment_type,
                'actions': analysis.get('recommendations', []),
                'priority': 'high' if risk.get('severity', 0) >= 4 else 'medium',
                'responsible': responsible
            }
        })

        return {
            'response': f"✅ Treatment plan created (ID: {treatment_id})\n"
                       f"Type: {treatment_type}\n"
                       f"Actions: {len(analysis.get('recommendations', []))}",
            'data': {
                'treatment_id': treatment_id,
                'actions': analysis.get('recommendations', [])
            },
            'actions': [
                {
                    'type': 'view_treatment',
                    'label': '📋 View Treatment Plan',
                    'data': {'treatment_id': treatment_id}
                }
            ],
            'confidence': analysis.get('confidence', 0.0),
            'timestamp': datetime.utcnow().isoformat()
        }

    def _calculate_severity(
        self,
        analysis: Dict[str, Any],
        dependencies: List[Dict[str, Any]]
    ) -> int:
        """Calculate severity score (1-5)"""
        # Base severity from analysis confidence
        base = int(analysis.get('confidence', 0.5) * 5)

        # Increase for SPOF
        spof_count = sum(1 for d in dependencies if d.get('single_point_of_failure'))
        if spof_count > 0:
            base = min(base + 1, 5)

        return base

    def _generate_actions(
        self,
        tool_data: Any,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate suggested actions"""
        actions = []

        process = tool_data.get('process', {})
        if process:
            actions.append({
                'type': 'create_treatment_plan',
                'label': '📋 Create Treatment Plan',
                'data': {'process_id': process.get('id')}
            })

            actions.append({
                'type': 'view_dependencies',
                'label': '🔗 View Dependencies',
                'data': {'process_id': process.get('id')}
            })

        return actions
