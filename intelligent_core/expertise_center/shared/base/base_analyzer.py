"""
Base Analyzer - Heavy AI Processing

Analyzers = Heavy computational AI (10)
- Deep data analysis
- Pattern recognition
- Predictive modeling
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

# AI Foundation integration
from intelligent_core.ai_foundation import RAGPipeline, LLMRouter, ContextBuilder, WorkflowPredictor, AnomalyDetector


class BaseAnalyzer(ABC):
    """
    Base class for Heavy AI Analyzers

    Used for:
    - Governance Analyzer
    - Impact Analyzer
    - Risk Analyzer
    - Compliance Analyzer
    - Emergency Analyzer
    - Scenario Analyzer
    - Performance Analyzer
    - Learning Analyzer
    - Plan Analyzer
    - Lifecycle Analyzer

    Integrated with ai-foundation:
    - self.rag: RAGPipeline for knowledge retrieval
    - self.llm: LLMRouter for AI-powered analysis
    - self.context_builder: ContextBuilder for context enrichment
    - self.predictor: WorkflowPredictor for forecasting
    - self.anomaly_detector: AnomalyDetector for anomaly detection
    """

    def __init__(
        self,
        analyzer_id: str,
        name: str,
        analysis_type: str,
        domain: str = "bcm"
    ):
        self.analyzer_id = analyzer_id
        self.name = name
        self.analysis_type = analysis_type
        self.domain = domain

        # AI Foundation integrations (available to all analyzers)
        self.rag = RAGPipeline()
        self.llm = LLMRouter()
        self.context_builder = ContextBuilder()
        self.predictor = WorkflowPredictor()
        self.anomaly_detector = AnomalyDetector()

    @abstractmethod
    async def analyze(
        self,
        data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform heavy analysis

        Args:
            data: Data to analyze
            config: Analysis configuration

        Returns:
            Analysis results
        """
        pass

    @abstractmethod
    async def extract_insights(
        self,
        analysis_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract actionable insights

        Args:
            analysis_result: Analysis results

        Returns:
            List of insights
        """
        pass

    async def get_metrics(self) -> Dict[str, Any]:
        """Get analyzer metrics"""
        return {}

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.analyzer_id} type={self.analysis_type}>"
