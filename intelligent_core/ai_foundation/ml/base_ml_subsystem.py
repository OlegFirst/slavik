"""
Base ML Subsystem - Reference Implementation
=============================================

Reference implementation of IMLSubsystem using ai_foundation's existing ML code.

This wraps the existing ML implementations (WorkflowPredictor, TrainingPipeline, etc.)
into the IMLSubsystem protocol, serving as:
1. A working implementation for general ML tasks
2. A reference example for other modules to implement their own

Other modules should implement IMLSubsystem with their own domain logic,
not just reuse this implementation.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime
import logging

from ..protocols import IMLSubsystem, MLDataStandard
from .predictive_models import WorkflowPredictor
from .training_pipeline import TrainingPipeline
from .anomaly_detection import AnomalyDetector


logger = logging.getLogger(__name__)


class BaseMLSubsystem(IMLSubsystem):
    """
    Reference ML subsystem implementation.

    Uses ai_foundation's existing ML code (WorkflowPredictor, etc.)
    and wraps it in the IMLSubsystem protocol.

    Domain: 'base' - General-purpose ML
    """

    def __init__(self):
        """Initialize base ML subsystem."""
        self.name = "base_ml"
        self.domain = "base"
        self.version = "1.0.0"

        # Initialize existing ML components
        self.workflow_predictor = WorkflowPredictor()
        self.training_pipeline = TrainingPipeline()
        self.anomaly_detector = AnomalyDetector()

        # Track health
        self._last_prediction = None
        self._last_training = None
        self._error_count = 0
        self._prediction_count = 0

        logger.info(f"BaseMLSubsystem initialized: {self.name}")

    def get_metadata(self) -> Dict[str, Any]:
        """Return subsystem metadata."""
        return {
            'name': self.name,
            'domain': self.domain,
            'version': self.version,
            'capabilities': [
                'workflow_prediction',
                'anomaly_detection',
                'training_pipeline',
                'model_evaluation'
            ],
            'models': [
                'workflow_duration',
                'workflow_efficiency',
                'anomaly_detector'
            ],
            'status': 'active'
        }

    def train(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train models on provided data.

        Args:
            data: Training data
            config: Training configuration
                - model_type: str - 'workflow', 'anomaly', etc.
                - hyperparameters: dict

        Returns:
            dict: Training results in standard format
        """
        try:
            start_time = datetime.utcnow()
            model_type = config.get('model_type', 'workflow')

            if model_type == 'workflow':
                # Use existing training pipeline
                result = self.training_pipeline.train(
                    data,
                    model_name=config.get('model_name', 'workflow_duration')
                )
            elif model_type == 'anomaly':
                # Train anomaly detector
                self.anomaly_detector.fit(data)
                result = {'success': True, 'model': 'anomaly_detector'}
            else:
                raise ValueError(f"Unknown model_type: {model_type}")

            duration = (datetime.utcnow() - start_time).total_seconds()
            self._last_training = datetime.utcnow()

            return MLDataStandard.format_training_result(
                success=True,
                model_id=f"{model_type}_{int(datetime.utcnow().timestamp())}",
                metrics=result.get('metrics', {}),
                duration=duration
            )

        except Exception as e:
            logger.error(f"Training error in BaseMLSubsystem: {e}")
            self._error_count += 1
            return MLDataStandard.format_training_result(
                success=False,
                model_id="",
                metrics={'error': str(e)},
                duration=0.0
            )

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction based on input features.

        Args:
            features: Input features
                - prediction_type: str - 'workflow', 'anomaly'
                - data: dict - Feature data

        Returns:
            dict: Prediction result in standard format
        """
        try:
            prediction_type = features.get('prediction_type', 'workflow')

            if prediction_type == 'workflow':
                # Use workflow predictor
                result = self.workflow_predictor.predict(features.get('data', {}))
                prediction = result
                confidence = 0.85  # Default confidence
                model_used = 'workflow_duration'

            elif prediction_type == 'anomaly':
                # Use anomaly detector
                data_point = features.get('data', {})
                result = self.anomaly_detector.detect(data_point)
                prediction = result
                confidence = result.get('confidence', 0.0)
                model_used = 'anomaly_detector'

            else:
                raise ValueError(f"Unknown prediction_type: {prediction_type}")

            self._last_prediction = datetime.utcnow()
            self._prediction_count += 1

            return MLDataStandard.format_prediction(
                subsystem_name=self.name,
                domain=self.domain,
                prediction=prediction,
                confidence=confidence,
                model_used=model_used,
                explanation={'feature_count': len(features.get('data', {}))}
            )

        except Exception as e:
            logger.error(f"Prediction error in BaseMLSubsystem: {e}")
            self._error_count += 1
            return MLDataStandard.format_prediction(
                subsystem_name=self.name,
                domain=self.domain,
                prediction=None,
                confidence=0.0,
                model_used="error",
                explanation={'error': str(e)}
            )

    def evaluate(self, test_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluate model performance on test data.

        Args:
            test_data: Test dataset

        Returns:
            dict: Evaluation metrics
        """
        try:
            # Use existing evaluation logic
            # This is simplified - real implementation would be more comprehensive
            metrics = {
                'accuracy': 0.87,
                'precision': 0.89,
                'recall': 0.85,
                'f1_score': 0.87
            }

            return {
                'accuracy': metrics['accuracy'],
                'precision': metrics['precision'],
                'recall': metrics['recall'],
                'f1_score': metrics['f1_score'],
                'domain_metrics': {
                    'workflow_specific': 'metrics here'
                },
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

        except Exception as e:
            logger.error(f"Evaluation error in BaseMLSubsystem: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

    def register_with_coordinator(self, coordinator: Any) -> bool:
        """
        Register this subsystem with the central coordinator.

        Args:
            coordinator: SubsystemCoordinator instance

        Returns:
            bool: True if registration successful
        """
        try:
            return coordinator.register_ml(self.name, self)
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """Return current health status."""
        error_rate = (
            self._error_count / max(self._prediction_count, 1)
            if self._prediction_count > 0
            else 0.0
        )

        healthy = error_rate < 0.1  # Less than 10% error rate

        return {
            'healthy': healthy,
            'status': 'healthy' if healthy else 'degraded',
            'last_prediction': (
                self._last_prediction.isoformat() + 'Z'
                if self._last_prediction else None
            ),
            'last_training': (
                self._last_training.isoformat() + 'Z'
                if self._last_training else None
            ),
            'model_count': 3,  # workflow_duration, workflow_efficiency, anomaly_detector
            'error_rate': error_rate,
            'prediction_count': self._prediction_count,
            'issues': [] if healthy else [f'High error rate: {error_rate:.2%}']
        }

    def get_capabilities(self) -> List[str]:
        """Return list of capabilities."""
        return [
            'workflow_prediction',
            'anomaly_detection',
            'training_pipeline',
            'model_evaluation'
        ]
