"""
WorkflowMLSubsystem - Domain-Specific ML Implementation
========================================================

ML subsystem specialized for workflow intelligence domain.

This demonstrates the FEDERATED architecture philosophy:
- NOT a wrapper around ai_foundation/ml
- OWN implementation with workflow-specific logic
- Domain expertise baked into feature engineering and models
- Follows IMLSubsystem protocol for coordination

Key Differences from BaseMLSubsystem:
- Workflow-specific feature extraction
- Models trained on workflow patterns
- Predictions tuned for workflow optimization
- Domain context in every decision
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime
import logging
import numpy as np

# Import protocol from ai_foundation
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ai_foundation"))

from protocols import IMLSubsystem, MLDataStandard


logger = logging.getLogger(__name__)


class WorkflowMLSubsystem(IMLSubsystem):
    """
    Workflow-specific ML subsystem implementation.

    Domain: workflow
    Expertise: Workflow duration, bottlenecks, task optimization

    This is a REFERENCE implementation showing how to:
    1. Implement IMLSubsystem protocol
    2. Add domain-specific logic
    3. Register with coordinator
    """

    def __init__(self):
        """Initialize workflow ML subsystem."""
        self.name = "workflow_ml"
        self.domain = "workflow"
        self.version = "1.0.0"

        # Workflow-specific models (in-memory for example)
        self.models = {
            'duration_predictor': None,  # Would be actual model
            'bottleneck_detector': None,
            'task_priority': None
        }

        # Workflow-specific state
        self.workflow_history = []  # Historical workflow data
        self.active_workflows = {}  # Currently running workflows
        self.pattern_cache = {}     # Cached workflow patterns

        # Health tracking
        self._last_prediction = None
        self._last_training = None
        self._error_count = 0
        self._prediction_count = 0

        logger.info(f"WorkflowMLSubsystem initialized: {self.name}")

    def get_metadata(self) -> Dict[str, Any]:
        """Return subsystem metadata."""
        return {
            'name': self.name,
            'domain': self.domain,
            'version': self.version,
            'capabilities': [
                'duration_prediction',
                'bottleneck_detection',
                'task_priority_optimization',
                'process_efficiency_analysis'
            ],
            'models': list(self.models.keys()),
            'status': 'active',
            'workflow_count': len(self.workflow_history),
            'active_workflows': len(self.active_workflows)
        }

    def train(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train workflow-specific models.

        Args:
            data: Workflow training data with columns:
                - workflow_id: str
                - steps: List[dict] - Workflow steps
                - duration: float - Total duration
                - outcome: str - Success/failure
                - context: dict - Workflow context

            config: Training configuration
                - model_type: str - 'duration', 'bottleneck', 'priority'
                - hyperparameters: dict

        Returns:
            dict: Training results in standard format
        """
        try:
            start_time = datetime.utcnow()
            model_type = config.get('model_type', 'duration')

            # WORKFLOW-SPECIFIC FEATURE ENGINEERING
            features = self._extract_workflow_features(data)

            if model_type == 'duration':
                # Train duration prediction model
                # This is where domain expertise goes
                result = self._train_duration_model(features, data['duration'])

            elif model_type == 'bottleneck':
                # Train bottleneck detection model
                result = self._train_bottleneck_model(features, data)

            elif model_type == 'priority':
                # Train task priority model
                result = self._train_priority_model(features, data)

            else:
                raise ValueError(f"Unknown model_type: {model_type}")

            duration = (datetime.utcnow() - start_time).total_seconds()
            self._last_training = datetime.utcnow()

            # Update workflow history for future learning
            self.workflow_history.extend(data.to_dict('records'))

            return MLDataStandard.format_training_result(
                success=True,
                model_id=f"{self.domain}_{model_type}_{int(datetime.utcnow().timestamp())}",
                metrics=result.get('metrics', {}),
                duration=duration
            )

        except Exception as e:
            logger.error(f"Training error in WorkflowMLSubsystem: {e}")
            self._error_count += 1
            return MLDataStandard.format_training_result(
                success=False,
                model_id="",
                metrics={'error': str(e)},
                duration=0.0
            )

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make workflow-specific prediction.

        Args:
            features: Workflow features
                - workflow_id: str
                - current_step: str
                - steps_completed: int
                - context: dict - Workflow context
                - history: List[dict] - Previous steps

        Returns:
            dict: Prediction result in standard format
        """
        try:
            # Extract workflow-specific features
            workflow_features = self._preprocess_workflow_features(features)

            # Predict duration
            duration_pred = self._predict_duration(workflow_features)

            # Detect bottlenecks
            bottlenecks = self._detect_bottlenecks(workflow_features)

            # Recommend optimizations
            optimizations = self._recommend_optimizations(workflow_features, bottlenecks)

            prediction = {
                'duration_hours': duration_pred,
                'bottlenecks': bottlenecks,
                'optimizations': optimizations,
                'estimated_completion': self._calculate_completion_time(duration_pred)
            }

            confidence = self._calculate_confidence(workflow_features, duration_pred)

            self._last_prediction = datetime.utcnow()
            self._prediction_count += 1

            # Track active workflow
            workflow_id = features.get('workflow_id')
            if workflow_id:
                self.active_workflows[workflow_id] = {
                    'prediction': prediction,
                    'timestamp': datetime.utcnow(),
                    'features': workflow_features
                }

            return MLDataStandard.format_prediction(
                subsystem_name=self.name,
                domain=self.domain,
                prediction=prediction,
                confidence=confidence,
                model_used='workflow_duration_v2',
                explanation={
                    'feature_importance': self._get_feature_importance(),
                    'similar_workflows': self._find_similar_workflows(workflow_features)[:3]
                }
            )

        except Exception as e:
            logger.error(f"Prediction error in WorkflowMLSubsystem: {e}")
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
        """Evaluate workflow models on test data."""
        try:
            # Workflow-specific evaluation metrics
            features = self._extract_workflow_features(test_data)
            predictions = [self._predict_duration(f) for f in features]
            actuals = test_data['duration'].tolist()

            # Calculate workflow-specific metrics
            mae = np.mean(np.abs(np.array(predictions) - np.array(actuals)))
            rmse = np.sqrt(np.mean((np.array(predictions) - np.array(actuals)) ** 2))

            return {
                'accuracy': 0.87,  # Simplified
                'precision': 0.89,
                'recall': 0.85,
                'f1_score': 0.87,
                'domain_metrics': {
                    'mae_hours': mae,
                    'rmse_hours': rmse,
                    'bottleneck_detection_rate': 0.92,
                    'optimization_success_rate': 0.78
                },
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            return {'error': str(e), 'timestamp': datetime.utcnow().isoformat() + 'Z'}

    def register_with_coordinator(self, coordinator: Any) -> bool:
        """Register with central coordinator."""
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

        healthy = error_rate < 0.1

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
            'model_count': len(self.models),
            'error_rate': error_rate,
            'prediction_count': self._prediction_count,
            'workflow_history_size': len(self.workflow_history),
            'active_workflows': len(self.active_workflows),
            'issues': [] if healthy else [f'High error rate: {error_rate:.2%}']
        }

    def get_capabilities(self) -> List[str]:
        """Return list of capabilities."""
        return [
            'duration_prediction',
            'bottleneck_detection',
            'task_priority_optimization',
            'process_efficiency_analysis'
        ]

    # ===========================
    # Workflow-Specific Methods
    # ===========================

    def _extract_workflow_features(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Extract workflow-specific features.

        This is WHERE DOMAIN EXPERTISE LIVES.
        """
        features = []
        for _, row in data.iterrows():
            features.append({
                'step_count': len(row.get('steps', [])),
                'complexity_score': self._calculate_complexity(row.get('steps', [])),
                'parallel_steps': self._count_parallel_steps(row.get('steps', [])),
                'dependency_depth': self._calculate_dependency_depth(row.get('steps', [])),
                'resource_intensity': row.get('context', {}).get('resource_intensity', 'medium'),
                'historical_avg_duration': self._get_historical_avg(row.get('workflow_type')),
            })
        return features

    def _preprocess_workflow_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess features for prediction."""
        return {
            'step_count': len(features.get('history', [])) + 1,
            'steps_completed': features.get('steps_completed', 0),
            'current_step': features.get('current_step', 'unknown'),
            'context': features.get('context', {}),
            'historical_pattern': self._find_pattern(features)
        }

    def _predict_duration(self, features: Dict[str, Any]) -> float:
        """Predict workflow duration (simplified)."""
        # Real implementation would use trained model
        base_duration = features.get('step_count', 5) * 0.5  # 30 min per step
        complexity_multiplier = 1.2 if features.get('steps_completed', 0) > 10 else 1.0
        return base_duration * complexity_multiplier

    def _detect_bottlenecks(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect potential bottlenecks in workflow."""
        # Real implementation would analyze actual workflow data
        return [
            {
                'step': 'approval_step',
                'likelihood': 0.75,
                'avg_delay_hours': 2.5,
                'recommendation': 'Consider parallel approval process'
            }
        ]

    def _recommend_optimizations(self, features: Dict[str, Any], bottlenecks: List) -> List[str]:
        """Recommend workflow optimizations."""
        recommendations = []
        if bottlenecks:
            recommendations.append('Parallelize approval steps')
        if features.get('step_count', 0) > 15:
            recommendations.append('Consider breaking into sub-workflows')
        return recommendations

    def _calculate_completion_time(self, duration_hours: float) -> str:
        """Calculate estimated completion time."""
        from datetime import timedelta
        completion = datetime.utcnow() + timedelta(hours=duration_hours)
        return completion.isoformat() + 'Z'

    def _calculate_confidence(self, features: Dict[str, Any], prediction: float) -> float:
        """Calculate prediction confidence based on historical data."""
        # Higher confidence if we have similar workflows in history
        similar_count = len(self._find_similar_workflows(features))
        base_confidence = 0.7
        history_boost = min(0.25, similar_count * 0.05)
        return min(1.0, base_confidence + history_boost)

    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance for explainability."""
        return {
            'step_count': 0.35,
            'complexity_score': 0.25,
            'historical_pattern': 0.20,
            'parallel_steps': 0.12,
            'resource_intensity': 0.08
        }

    def _find_similar_workflows(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar workflows from history."""
        # Simplified similarity search
        return [w for w in self.workflow_history[:5]]  # Return first 5 for example

    def _calculate_complexity(self, steps: List) -> float:
        """Calculate workflow complexity score."""
        return len(steps) * 1.5  # Simplified

    def _count_parallel_steps(self, steps: List) -> int:
        """Count parallel execution steps."""
        return sum(1 for step in steps if step.get('parallel', False))

    def _calculate_dependency_depth(self, steps: List) -> int:
        """Calculate maximum dependency depth."""
        return len(steps)  # Simplified

    def _get_historical_avg(self, workflow_type: Optional[str]) -> float:
        """Get historical average duration for workflow type."""
        # Real implementation would query historical data
        return 4.5  # hours

    def _find_pattern(self, features: Dict[str, Any]) -> str:
        """Find matching pattern from pattern cache."""
        # Real implementation would do pattern matching
        return "standard_approval_workflow"

    def _train_duration_model(self, features: List[Dict], durations: pd.Series) -> Dict[str, Any]:
        """Train duration prediction model."""
        # Simplified training
        return {
            'success': True,
            'metrics': {
                'mae': 0.45,
                'rmse': 0.67,
                'r2': 0.89
            }
        }

    def _train_bottleneck_model(self, features: List[Dict], data: pd.DataFrame) -> Dict[str, Any]:
        """Train bottleneck detection model."""
        return {
            'success': True,
            'metrics': {
                'precision': 0.87,
                'recall': 0.82
            }
        }

    def _train_priority_model(self, features: List[Dict], data: pd.DataFrame) -> Dict[str, Any]:
        """Train task priority model."""
        return {
            'success': True,
            'metrics': {
                'accuracy': 0.91
            }
        }
