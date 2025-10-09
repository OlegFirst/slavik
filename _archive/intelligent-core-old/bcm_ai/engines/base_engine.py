"""
Base Engine Class
Business logic layer for BCM AI system
"""
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from datetime import datetime
import json


class BaseEngine(ABC):
    """
    Base class for all BCM AI Engines

    Responsibilities:
    - Tools management (DB operations)
    - Analyzer invocation
    - Case Library integration
    - ML predictions (optional)
    - Result synthesis
    """

    def __init__(
        self,
        tools=None,
        analyzer=None,
        case_library=None,
        ml_predictor=None
    ):
        """
        Initialize Engine

        Args:
            tools: Tools for DB operations (e.g., RiskTools)
            analyzer: LLM analyzer (e.g., RiskAnalyzer)
            case_library: Case library repository
            ml_predictor: ML model for predictions (optional)
        """
        self.tools = tools
        self.analyzer = analyzer
        self.case_library = case_library
        self.ml_predictor = ml_predictor

    @abstractmethod
    async def execute(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action with parameters

        Must be implemented by subclass

        Args:
            action: Action name (e.g., 'analyze_risk', 'calculate_rto')
            params: Action parameters

        Returns:
            {
                'response': str,
                'data': dict,
                'actions': list,
                'confidence': float,
                'timestamp': str
            }
        """
        pass

    async def _use_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        Use a Tool to perform DB operation

        Args:
            tool_name: Name of the tool method
            params: Parameters for the tool

        Returns:
            Tool execution result
        """
        if not self.tools:
            raise ValueError("Tools not configured for this engine")

        tool_method = getattr(self.tools, tool_name, None)
        if not tool_method:
            raise ValueError(f"Tool '{tool_name}' not found")

        try:
            result = await tool_method(**params)
            return result
        except Exception as e:
            print(f"Tool execution error ({tool_name}): {e}")
            raise

    async def _analyze_with_analyzer(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke Analyzer for LLM analysis

        Args:
            context: Analysis context

        Returns:
            {
                'insights': list,
                'recommendations': list,
                'confidence': float
            }
        """
        if not self.analyzer:
            return {
                'insights': [],
                'recommendations': [],
                'confidence': 0.0
            }

        try:
            analysis = await self.analyzer.analyze(context)
            return analysis
        except Exception as e:
            print(f"Analyzer error: {e}")
            return {
                'insights': [],
                'recommendations': [],
                'confidence': 0.0,
                'error': str(e)
            }

    async def _find_similar_cases(
        self,
        filters: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar cases from Case Library

        Args:
            filters: Search filters (industry, module, action_type)
            limit: Max number of cases to return

        Returns:
            List of similar cases
        """
        if not self.case_library:
            return []

        try:
            cases = await self.case_library.search(
                industry=filters.get('industry'),
                module=filters.get('module'),
                action_type=filters.get('action_type'),
                limit=limit
            )
            return cases
        except Exception as e:
            print(f"Case Library search error: {e}")
            return []

    async def _record_to_case_library(self, case_data: Dict[str, Any]) -> Optional[str]:
        """
        Record result to Case Library for learning

        Args:
            case_data: Case data to record

        Returns:
            Case ID if successful, None otherwise
        """
        if not self.case_library:
            return None

        try:
            case_id = await self.case_library.record_case(case_data)
            return case_id
        except Exception as e:
            print(f"Case Library recording error: {e}")
            return None

    async def _predict_with_ml(
        self,
        prediction_type: str,
        features: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Make ML prediction (optional)

        Args:
            prediction_type: Type of prediction
            features: Feature dictionary

        Returns:
            Prediction result or None
        """
        if not self.ml_predictor:
            return None

        try:
            prediction = await self.ml_predictor.predict(
                prediction_type=prediction_type,
                features=features
            )
            return prediction
        except Exception as e:
            print(f"ML prediction error: {e}")
            return None

    def _synthesize_result(
        self,
        tool_data: Any,
        analysis: Dict[str, Any],
        similar_cases: List[Dict[str, Any]],
        ml_prediction: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synthesize final result from all sources

        Args:
            tool_data: Data from Tools (DB)
            analysis: Analysis from Analyzer (LLM)
            similar_cases: Similar cases from Case Library
            ml_prediction: ML prediction (optional)

        Returns:
            Synthesized result
        """
        # Build response text
        response_parts = []

        # Add LLM insights
        if analysis.get('insights'):
            response_parts.extend(analysis['insights'])

        # Add recommendations
        if analysis.get('recommendations'):
            response_parts.append("\n💡 Рекомендации:")
            response_parts.extend([f"  • {rec}" for rec in analysis['recommendations']])

        # Add similar cases context
        if similar_cases:
            response_parts.append(f"\n📊 На основе {len(similar_cases)} похожих случаев")

        # Add ML prediction
        if ml_prediction:
            response_parts.append(
                f"\n🤖 ML прогноз: {ml_prediction.get('prediction', 'N/A')}"
            )

        return {
            'response': '\n'.join(response_parts),
            'data': {
                'tool_data': tool_data,
                'analysis': analysis,
                'similar_cases': similar_cases,
                'ml_prediction': ml_prediction
            },
            'actions': self._generate_actions(tool_data, analysis),
            'confidence': analysis.get('confidence', 0.0),
            'timestamp': datetime.utcnow().isoformat()
        }

    def _generate_actions(
        self,
        tool_data: Any,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate suggested actions

        Override in subclass for specific actions
        """
        return []
