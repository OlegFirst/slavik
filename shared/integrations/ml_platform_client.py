"""
ML Platform Client - Unified Prediction Service

Provides centralized machine learning services:
- Shared prediction models
- Feedback collection
- Model versioning
- Feature store
- A/B testing

All services use this for ML predictions
"""

import logging
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class MLPlatformClient:
    """
    Client for platform-wide ML services

    Provides:
    - Universal predictions
    - Feedback submission
    - Model performance tracking
    - Feature engineering
    """

    def __init__(self, ml_service_url: str = "http://localhost:8060"):
        """
        Initialize ML Platform client

        Args:
            ml_service_url: ML Platform service endpoint (default: port 8060)
        """
        self.base_url = ml_service_url
        self.client = httpx.AsyncClient(timeout=60.0)  # ML can be slow

    async def predict(
        self,
        model_name: str,
        features: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        return_explanation: bool = False
    ) -> Dict[str, Any]:
        """
        Get prediction from ML model

        Args:
            model_name: Model identifier (e.g., 'exercise_success_predictor')
            features: Input features for prediction
            context: Additional context (user_id, tenant_id, etc.)
            return_explanation: Include model explanation (SHAP values)

        Returns:
            Prediction result with confidence and optional explanation

        Example:
            prediction = await ml_client.predict(
                model_name='exercise_success_predictor',
                features={
                    'scenario_type': 'cyber_incident',
                    'team_size': 12,
                    'avg_competency': 0.75,
                    'days_since_last': 45
                },
                context={'user_id': 'user123'}
            )
            # Returns:
            # {
            #     'prediction_id': 'pred_abc123',
            #     'prediction': 78.5,  # predicted score
            #     'confidence': 0.82,
            #     'model_version': 'v3',
            #     'explanation': {...}  # if requested
            # }
        """
        try:
            request_data = {
                'model_name': model_name,
                'features': features,
                'return_explanation': return_explanation
            }

            if context:
                request_data['context'] = context

            response = await self.client.post(
                f"{self.base_url}/api/ml/predict",
                json=request_data
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"ML prediction: {model_name} -> {result.get('prediction')} (conf: {result.get('confidence')})")
                return result
            else:
                logger.error(f"ML prediction failed: {response.status_code}")
                return self._fallback_prediction(features)

        except httpx.ConnectError:
            logger.warning("ML Platform unavailable - using fallback")
            return self._fallback_prediction(features)
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return self._fallback_prediction(features)

    async def predict_batch(
        self,
        model_name: str,
        batch_features: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Batch predictions for efficiency

        Args:
            model_name: Model identifier
            batch_features: List of feature dicts

        Returns:
            List of predictions
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/ml/predict/batch",
                json={
                    'model_name': model_name,
                    'batch': batch_features
                }
            )

            if response.status_code == 200:
                return response.json().get('predictions', [])
            return []

        except Exception as e:
            logger.error(f"Batch prediction error: {e}")
            return [self._fallback_prediction(f) for f in batch_features]

    async def submit_feedback(
        self,
        prediction_id: str,
        actual_outcome: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Submit actual outcome for prediction (closes feedback loop)

        Args:
            prediction_id: ID from prediction response
            actual_outcome: Real result (e.g., actual exercise score)
            metadata: Additional data (execution_time, issues_found, etc.)

        Returns:
            Success status

        Example:
            success = await ml_client.submit_feedback(
                prediction_id='pred_abc123',
                actual_outcome=82.0,  # actual score
                metadata={
                    'exercise_id': 'ex_123',
                    'participant_count': 12,
                    'duration_minutes': 120
                }
            )
        """
        try:
            request_data = {
                'prediction_id': prediction_id,
                'actual_outcome': actual_outcome,
                'feedback_timestamp': datetime.utcnow().isoformat()
            }

            if metadata:
                request_data['metadata'] = metadata

            response = await self.client.post(
                f"{self.base_url}/api/ml/feedback",
                json=request_data
            )

            success = response.status_code == 200
            if success:
                logger.info(f"Feedback submitted for {prediction_id}")
            return success

        except Exception as e:
            logger.error(f"Submit feedback error: {e}")
            return False

    async def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get model metadata

        Args:
            model_name: Model identifier

        Returns:
            Model information (version, performance, features, etc.)
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/ml/models/{model_name}"
            )

            if response.status_code == 200:
                return response.json()
            return None

        except Exception as e:
            logger.error(f"Get model info error: {e}")
            return None

    async def list_available_models(
        self,
        domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all available models

        Args:
            domain: Filter by domain (bcm, risk, compliance, etc.)

        Returns:
            List of available models with metadata
        """
        try:
            params = {'domain': domain} if domain else {}
            response = await self.client.get(
                f"{self.base_url}/api/ml/models",
                params=params
            )

            if response.status_code == 200:
                return response.json().get('models', [])
            return []

        except Exception as e:
            logger.error(f"List models error: {e}")
            return []

    async def get_feature_importance(
        self,
        model_name: str
    ) -> Optional[Dict[str, float]]:
        """
        Get feature importance scores

        Args:
            model_name: Model identifier

        Returns:
            Feature importance dict (feature_name -> importance)
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/ml/models/{model_name}/features"
            )

            if response.status_code == 200:
                return response.json().get('importance', {})
            return None

        except Exception as e:
            logger.error(f"Get feature importance error: {e}")
            return None

    async def get_model_performance(
        self,
        model_name: str,
        time_window_days: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Get model performance metrics

        Args:
            model_name: Model identifier
            time_window_days: Performance window

        Returns:
            Performance metrics (accuracy, MAE, drift, etc.)
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/ml/models/{model_name}/performance",
                params={'window_days': time_window_days}
            )

            if response.status_code == 200:
                return response.json()
            return None

        except Exception as e:
            logger.error(f"Get model performance error: {e}")
            return None

    def _fallback_prediction(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback prediction when ML Platform unavailable

        Uses simple heuristics based on features
        """
        logger.info("Using fallback prediction (ML Platform unavailable)")

        # Simple heuristic: hash features to consistent value
        feature_str = str(sorted(features.items()))
        hash_val = int(hashlib.md5(feature_str.encode()).hexdigest()[:8], 16)
        prediction = (hash_val % 30) + 55  # Range 55-85

        return {
            'prediction_id': f'fallback_{hash_val}',
            'prediction': prediction,
            'confidence': 0.5,
            'model_version': 'fallback',
            'source': 'heuristic',
            'warning': 'ML Platform unavailable - using fallback'
        }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class FeatureBuilder:
    """
    Helper for building ML feature sets

    Ensures consistent feature engineering across services
    """

    def __init__(self):
        self.features = {}

    def add_numeric(self, name: str, value: float) -> 'FeatureBuilder':
        """Add numeric feature"""
        self.features[name] = float(value)
        return self

    def add_categorical(self, name: str, value: str) -> 'FeatureBuilder':
        """Add categorical feature"""
        self.features[f"{name}_categorical"] = value
        return self

    def add_boolean(self, name: str, value: bool) -> 'FeatureBuilder':
        """Add boolean feature"""
        self.features[name] = 1.0 if value else 0.0
        return self

    def add_timestamp(self, name: str, timestamp: datetime) -> 'FeatureBuilder':
        """Add timestamp as features (hour, day_of_week, etc.)"""
        self.features[f"{name}_hour"] = timestamp.hour
        self.features[f"{name}_day_of_week"] = timestamp.weekday()
        self.features[f"{name}_is_weekend"] = 1.0 if timestamp.weekday() >= 5 else 0.0
        return self

    def add_list_aggregates(
        self,
        name: str,
        values: List[float]
    ) -> 'FeatureBuilder':
        """Add list aggregates (mean, min, max, std)"""
        if values:
            import statistics
            self.features[f"{name}_mean"] = statistics.mean(values)
            self.features[f"{name}_min"] = min(values)
            self.features[f"{name}_max"] = max(values)
            if len(values) > 1:
                self.features[f"{name}_std"] = statistics.stdev(values)
        return self

    def build(self) -> Dict[str, Any]:
        """Build feature dict"""
        return self.features


class ModelPerformanceTracker:
    """
    Tracks model performance metrics locally

    Useful for monitoring and alerting
    """

    def __init__(self):
        self.predictions = []
        self.errors = []

    def record_prediction(
        self,
        prediction_id: str,
        prediction: float,
        actual: Optional[float] = None
    ):
        """Record prediction and optional actual"""
        record = {
            'prediction_id': prediction_id,
            'prediction': prediction,
            'actual': actual,
            'timestamp': datetime.utcnow()
        }
        self.predictions.append(record)

        if actual is not None:
            error = abs(prediction - actual)
            self.errors.append(error)

    def get_mae(self) -> Optional[float]:
        """Get Mean Absolute Error"""
        if not self.errors:
            return None
        return sum(self.errors) / len(self.errors)

    def get_recent_performance(self, last_n: int = 10) -> Dict[str, Any]:
        """Get recent performance metrics"""
        recent_errors = self.errors[-last_n:]

        if not recent_errors:
            return {'status': 'no_data'}

        import statistics
        return {
            'mae': statistics.mean(recent_errors),
            'median_error': statistics.median(recent_errors),
            'max_error': max(recent_errors),
            'sample_count': len(recent_errors)
        }
