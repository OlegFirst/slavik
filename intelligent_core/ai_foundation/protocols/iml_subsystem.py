"""
IMLSubsystem - Machine Learning Subsystem Protocol
===================================================

Protocol interface that EVERY ML subsystem must implement.

Examples of implementations:
- workflow_intelligence/ml/workflow_ml_subsystem.py
- expertise_center/ml/expert_ml_subsystem.py
- orchestration/ml/orchestration_ml_subsystem.py
- ai_foundation/ml/base_ml_subsystem.py (reference implementation)

Each implementation has its own:
- Models
- Feature engineering
- Training logic
- Prediction logic
- Domain-specific optimizations

But all follow this protocol for coordination.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd


class IMLSubsystem(ABC):
    """
    Protocol for ML subsystems - defines standard interface.

    Every module that has ML capabilities must implement this interface.
    The coordinator polls all implementations and aggregates results.
    """

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return subsystem metadata for discovery and coordination.

        Returns:
            dict: Metadata including:
                - name: str - Subsystem name (e.g., 'workflow_ml')
                - domain: str - Domain of expertise (e.g., 'workflow', 'expertise', 'orchestration')
                - version: str - Subsystem version
                - capabilities: List[str] - What this subsystem can do
                - models: List[str] - Available model names
                - status: str - 'active', 'training', 'degraded', 'offline'

        Example:
            {
                'name': 'workflow_ml',
                'domain': 'workflow',
                'version': '1.0.0',
                'capabilities': ['duration_prediction', 'bottleneck_detection', 'anomaly_detection'],
                'models': ['workflow_duration', 'process_efficiency', 'task_priority'],
                'status': 'active'
            }
        """
        pass

    @abstractmethod
    def train(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train models on provided data.

        Args:
            data: Training data (domain-specific schema)
            config: Training configuration
                - model_type: str - Which model to train
                - hyperparameters: dict - Model-specific hyperparameters
                - validation_split: float - Validation data percentage

        Returns:
            dict: Training results
                - success: bool
                - model_id: str - Trained model identifier
                - metrics: dict - Training metrics
                - duration: float - Training time in seconds
                - timestamp: str - ISO format timestamp

        Note:
            Each subsystem has its own feature engineering and training logic.
            The coordinator doesn't control HOW you train, just that you follow this interface.
        """
        pass

    @abstractmethod
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction based on input features.

        Args:
            features: Input features (domain-specific)
                Example for workflow:
                {
                    'process_id': 'proc_123',
                    'task_history': [...],
                    'current_step': 'step_5',
                    'context': {...}
                }

        Returns:
            dict: Prediction result in STANDARD format
                - subsystem: str - Name of this subsystem
                - domain: str - Domain of prediction
                - prediction: Any - The actual prediction (domain-specific)
                - confidence: float - Confidence score [0.0-1.0]
                - model_used: str - Which model made prediction
                - timestamp: str - ISO format timestamp
                - explanation: Optional[dict] - Explainability data

        Example:
            {
                'subsystem': 'workflow_ml',
                'domain': 'workflow',
                'prediction': {'duration_hours': 4.5, 'bottleneck_step': 'step_3'},
                'confidence': 0.87,
                'model_used': 'workflow_duration_v2',
                'timestamp': '2025-10-22T10:30:00Z',
                'explanation': {'feature_importance': {...}}
            }
        """
        pass

    @abstractmethod
    def evaluate(self, test_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluate model performance on test data.

        Args:
            test_data: Test dataset (domain-specific schema)

        Returns:
            dict: Evaluation metrics
                - accuracy: float
                - precision: float
                - recall: float
                - f1_score: float
                - domain_metrics: dict - Domain-specific metrics
                - timestamp: str
        """
        pass

    @abstractmethod
    def register_with_coordinator(self, coordinator: Any) -> bool:
        """
        Register this subsystem with the central coordinator.

        Args:
            coordinator: SubsystemCoordinator instance

        Returns:
            bool: True if registration successful

        Note:
            Call coordinator.register_ml(self.get_metadata()['name'], self)
        """
        pass

    @abstractmethod
    def get_health_status(self) -> Dict[str, Any]:
        """
        Return current health status of this subsystem.

        Returns:
            dict: Health status
                - healthy: bool
                - status: str - 'healthy', 'degraded', 'critical', 'offline'
                - last_prediction: str - ISO timestamp
                - last_training: str - ISO timestamp
                - model_count: int
                - error_rate: float - [0.0-1.0]
                - issues: List[str] - Any current issues
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return list of capabilities this subsystem provides.

        Returns:
            List[str]: Capability names

        Example:
            ['duration_prediction', 'bottleneck_detection', 'resource_optimization']
        """
        pass


class MLDataStandard:
    """
    Standard data format for ML subsystem communication.

    All subsystems should format their data according to this standard
    for coordinator aggregation.
    """

    @staticmethod
    def format_prediction(
        subsystem_name: str,
        domain: str,
        prediction: Any,
        confidence: float,
        model_used: str,
        explanation: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Format prediction in standard way.

        Args:
            subsystem_name: Name of subsystem making prediction
            domain: Domain of expertise
            prediction: The actual prediction data
            confidence: Confidence score [0.0-1.0]
            model_used: Model identifier
            explanation: Optional explainability data

        Returns:
            dict: Standardized prediction format
        """
        return {
            'subsystem': subsystem_name,
            'domain': domain,
            'prediction': prediction,
            'confidence': confidence,
            'model_used': model_used,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'explanation': explanation or {}
        }

    @staticmethod
    def format_training_result(
        success: bool,
        model_id: str,
        metrics: Dict[str, float],
        duration: float
    ) -> Dict[str, Any]:
        """Format training result in standard way."""
        return {
            'success': success,
            'model_id': model_id,
            'metrics': metrics,
            'duration': duration,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
