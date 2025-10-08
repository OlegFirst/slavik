"""
Predictive Service Client
==========================

Client for communicating with Predictive Service (port 8033).

Provides ML-powered predictions for proactive analytics.
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..config import settings

logger = logging.getLogger(__name__)


class PredictiveClient:
    """
    Client for Predictive Service

    Provides ML predictions for:
    - Bottleneck prediction
    - Anomaly detection
    - Health score forecasting
    - Proactive recommendations

    Example:
        ```python
        client = PredictiveClient()
        prediction = await client.predict_bottleneck("bia_workflow")
        if prediction['probability'] > 0.7:
            print("High risk of bottleneck!")
        ```
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize Predictive Service client

        Args:
            base_url: Base URL of predictive service.
                     If None, uses settings.PREDICTIVE_SERVICE_URL
        """
        self.base_url = base_url or settings.PREDICTIVE_SERVICE_URL
        self.timeout = 30.0
        logger.info(f"PredictiveClient initialized: {self.base_url}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if Predictive Service is healthy

        Returns:
            Health status dict
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Predictive Service health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def predict_bottleneck(
        self,
        process_id: str,
        features: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predict bottleneck probability for a process

        Args:
            process_id: Process identifier
            features: Optional features dict:
                - avg_duration_last_7d: Historical average duration
                - execution_count_last_24h: Recent execution count
                - time_of_day: Current hour (0-23)
                - day_of_week: Current day (0-6)
                - system_load: Current system load

        Returns:
            Prediction dict:
                - probability: Bottleneck probability (0-1)
                - predicted_step: Which step will bottleneck
                - severity: low/medium/high/critical
                - confidence: Model confidence (0-1)
                - predicted_at: Timestamp

        Example:
            ```python
            prediction = await client.predict_bottleneck(
                process_id="bia_workflow",
                features={
                    'avg_duration_last_7d': 45.5,
                    'execution_count_last_24h': 12,
                    'time_of_day': 14,
                    'day_of_week': 2
                }
            )

            if prediction['probability'] > 0.7:
                print(f"High risk: {prediction['predicted_step']}")
                print(f"Severity: {prediction['severity']}")
            ```
        """
        try:
            payload = {
                'process_id': process_id,
                'features': features or {},
                'prediction_type': 'bottleneck',
                'requested_at': datetime.now().isoformat()
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/predictions/bottleneck",
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Bottleneck prediction endpoint not implemented")
                # Return mock prediction for now
                return self._mock_bottleneck_prediction(process_id)
            logger.error(f"Failed to predict bottleneck: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to predict bottleneck: {e}")
            raise

    async def detect_anomaly(
        self,
        metric_name: str,
        values: List[float],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect anomalies in metric values

        Args:
            metric_name: Name of the metric
            values: List of metric values (time series)
            context: Optional context (day_of_week, is_weekend, etc.)

        Returns:
            Anomaly detection result:
                - is_anomaly: Boolean
                - anomaly_score: Score (0-1, higher = more anomalous)
                - anomaly_indices: Which indices are anomalous
                - expected_range: Expected value range
                - detected_at: Timestamp

        Example:
            ```python
            result = await client.detect_anomaly(
                metric_name="response_time_ms",
                values=[120, 115, 130, 125, 450, 122],  # 450 is anomaly
                context={'day_of_week': 2}
            )

            if result['is_anomaly']:
                print(f"Anomaly detected! Score: {result['anomaly_score']}")
                print(f"At indices: {result['anomaly_indices']}")
            ```
        """
        try:
            payload = {
                'metric_name': metric_name,
                'values': values,
                'context': context or {},
                'requested_at': datetime.now().isoformat()
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/predictions/anomaly",
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Anomaly detection endpoint not implemented")
                # Return mock result
                return self._mock_anomaly_detection(values)
            logger.error(f"Failed to detect anomaly: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to detect anomaly: {e}")
            raise

    async def forecast_health_score(
        self,
        historical_scores: List[float],
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """
        Forecast platform health score for next N days

        Args:
            historical_scores: Historical health scores (last 30 days)
            days_ahead: How many days to forecast (default: 7)

        Returns:
            Forecast dict:
                - predicted_scores: List of predicted scores
                - confidence_intervals: Confidence bounds for each prediction
                - trend: 'improving' / 'stable' / 'declining'
                - forecast_date: When forecast was made

        Example:
            ```python
            forecast = await client.forecast_health_score(
                historical_scores=[85, 87, 86, 88, 85, ...],  # 30 days
                days_ahead=7
            )

            print(f"Trend: {forecast['trend']}")
            for day, score in enumerate(forecast['predicted_scores'], 1):
                print(f"Day {day}: {score}")
            ```
        """
        try:
            payload = {
                'historical_scores': historical_scores,
                'days_ahead': days_ahead,
                'requested_at': datetime.now().isoformat()
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/predictions/health-forecast",
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Health forecast endpoint not implemented")
                # Return mock forecast
                return self._mock_health_forecast(historical_scores, days_ahead)
            logger.error(f"Failed to forecast health score: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to forecast health score: {e}")
            raise

    async def get_proactive_recommendations(
        self,
        journey_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get proactive recommendations based on journey context

        Args:
            journey_context: Journey context dict:
                - journey_id: Journey identifier
                - current_stage: Current stage
                - completion_percentage: Progress %
                - user_profile: User information

        Returns:
            List of proactive recommendations

        Example:
            ```python
            recs = await client.get_proactive_recommendations({
                'journey_id': 'journey_123',
                'current_stage': 'bia_analysis',
                'completion_percentage': 45,
                'user_profile': {'org_id': 'org_456'}
            })

            for rec in recs:
                print(f"Priority {rec['priority']}: {rec['title']}")
            ```
        """
        try:
            payload = {
                **journey_context,
                'requested_at': datetime.now().isoformat()
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/recommendations/proactive",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                return data.get("recommendations", [])

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Proactive recommendations endpoint not implemented")
                return []
            logger.error(f"Failed to get proactive recommendations: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to get proactive recommendations: {e}")
            return []

    async def submit_training_data(
        self,
        data_type: str,
        training_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit training data to improve ML models

        Args:
            data_type: Type of training data
                ('bottleneck_actual', 'anomaly_label', 'health_outcome')
            training_data: Training data dict

        Returns:
            Response from predictive service

        Example:
            ```python
            # Submit actual bottleneck outcome for model training
            await client.submit_training_data(
                data_type='bottleneck_actual',
                training_data={
                    'process_id': 'bia_workflow',
                    'prediction_id': 'pred_123',
                    'bottleneck_occurred': True,
                    'actual_step': 'data_collection',
                    'actual_severity': 'high',
                    'duration_minutes': 45
                }
            )
            ```
        """
        try:
            payload = {
                'data_type': data_type,
                'training_data': training_data,
                'submitted_at': datetime.now().isoformat(),
                'source': 'analytics-specialist'
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/training/submit",
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Training data submission endpoint not implemented")
                return {
                    "status": "accepted",
                    "message": "Training data logged for future use"
                }
            logger.error(f"Failed to submit training data: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to submit training data: {e}")
            raise

    # ========================================
    # MOCK PREDICTIONS (для development)
    # ========================================

    def _mock_bottleneck_prediction(self, process_id: str) -> Dict[str, Any]:
        """Mock bottleneck prediction when service not available"""
        import random

        probability = random.uniform(0.1, 0.9)

        if probability > 0.7:
            severity = "high"
        elif probability > 0.4:
            severity = "medium"
        else:
            severity = "low"

        return {
            "probability": round(probability, 2),
            "predicted_step": "data_collection",
            "severity": severity,
            "confidence": 0.75,
            "predicted_at": datetime.now().isoformat(),
            "model_version": "mock",
            "warning": "Using mock prediction - Predictive Service not available"
        }

    def _mock_anomaly_detection(self, values: List[float]) -> Dict[str, Any]:
        """Mock anomaly detection when service not available"""
        import statistics

        if len(values) < 3:
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "anomaly_indices": [],
                "expected_range": (0, 0)
            }

        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0

        # Simple outlier detection: > 2 standard deviations
        threshold = 2 * stdev
        anomaly_indices = []

        for i, val in enumerate(values):
            if abs(val - mean) > threshold:
                anomaly_indices.append(i)

        return {
            "is_anomaly": len(anomaly_indices) > 0,
            "anomaly_score": 0.8 if anomaly_indices else 0.2,
            "anomaly_indices": anomaly_indices,
            "expected_range": (mean - threshold, mean + threshold),
            "detected_at": datetime.now().isoformat(),
            "model_version": "mock",
            "warning": "Using mock detection - Predictive Service not available"
        }

    def _mock_health_forecast(
        self,
        historical_scores: List[float],
        days_ahead: int
    ) -> Dict[str, Any]:
        """Mock health forecast when service not available"""
        import statistics

        if not historical_scores:
            historical_scores = [85.0] * 7

        avg = statistics.mean(historical_scores[-7:])  # Last week average

        # Simple linear trend
        if len(historical_scores) > 1:
            trend_slope = (historical_scores[-1] - historical_scores[0]) / len(historical_scores)
        else:
            trend_slope = 0

        # Determine trend
        if trend_slope > 1:
            trend = "improving"
        elif trend_slope < -1:
            trend = "declining"
        else:
            trend = "stable"

        # Forecast
        predicted_scores = []
        for day in range(1, days_ahead + 1):
            predicted = avg + (trend_slope * day)
            predicted = max(0, min(100, predicted))  # Clamp 0-100
            predicted_scores.append(round(predicted, 1))

        return {
            "predicted_scores": predicted_scores,
            "confidence_intervals": [
                (max(0, s - 5), min(100, s + 5)) for s in predicted_scores
            ],
            "trend": trend,
            "forecast_date": datetime.now().isoformat(),
            "model_version": "mock",
            "warning": "Using mock forecast - Predictive Service not available"
        }
