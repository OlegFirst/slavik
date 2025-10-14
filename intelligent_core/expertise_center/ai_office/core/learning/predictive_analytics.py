"""
Predictive Analytics - Predict BCM issues before they occur

Analyzes trends, patterns, and predicts future states
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class Trend:
    """Trend data structure"""
    def __init__(self, metric: str, direction: str, strength: float, prediction: Optional[str] = None):
        self.metric = metric
        self.direction = direction  # "increasing", "decreasing", "stable"
        self.strength = strength  # 0.0-1.0
        self.prediction = prediction


class PredictiveAnalytics:
    """
    Predictive Analytics for BCM Intelligence

    Capabilities:
    - Trend analysis (risk trends, BIA changes, incident patterns)
    - Anomaly detection
    - Predictive warnings
    - Capacity forecasting
    - Seasonal pattern recognition
    """

    def __init__(self):
        self.time_series_data: Dict[str, List[Dict]] = defaultdict(list)
        self.predictions: List[Dict] = []
        self.anomalies_detected: List[Dict] = []
        self.trend_cache: Dict[str, Trend] = {}
        self.prediction_accuracy: List[float] = []

        logger.info("PredictiveAnalytics initialized")

    async def record_metric(
        self,
        metric_name: str,
        value: float,
        metadata: Optional[Dict] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Record a metric value for analysis

        Args:
            metric_name: Name of metric (e.g., "risk_count", "incident_frequency")
            value: Metric value
            metadata: Additional context
            timestamp: Time of measurement

        Returns:
            Recording confirmation
        """
        record = {
            "value": value,
            "timestamp": timestamp or datetime.utcnow(),
            "metadata": metadata or {}
        }

        self.time_series_data[metric_name].append(record)

        # Detect anomalies on new data
        if len(self.time_series_data[metric_name]) >= 10:
            await self._check_anomaly(metric_name, value)

        logger.debug(f"Recorded metric: {metric_name} = {value}")

        return {
            "metric": metric_name,
            "value": value,
            "total_records": len(self.time_series_data[metric_name])
        }

    async def analyze_trend(
        self,
        metric_name: str,
        window_days: int = 30
    ) -> Optional[Trend]:
        """
        Analyze trend for a metric

        Args:
            metric_name: Metric to analyze
            window_days: Look-back window in days

        Returns:
            Trend object or None
        """
        if metric_name not in self.time_series_data:
            return None

        data = self.time_series_data[metric_name]
        if len(data) < 3:
            return None

        # Filter to window
        cutoff = datetime.utcnow() - timedelta(days=window_days)
        windowed_data = [d for d in data if d["timestamp"] >= cutoff]

        if len(windowed_data) < 3:
            windowed_data = data[-10:]  # Use last 10 if window too small

        values = [d["value"] for d in windowed_data]

        # Calculate trend using linear regression (simple approach)
        direction, strength = self._calculate_trend_direction(values)

        # Generate prediction
        prediction = None
        if strength > 0.6:  # Strong trend
            if direction == "increasing":
                prediction = f"{metric_name} likely to continue increasing. Consider proactive measures."
            elif direction == "decreasing":
                prediction = f"{metric_name} trending down. Monitor for reversal."

        trend = Trend(
            metric=metric_name,
            direction=direction,
            strength=strength,
            prediction=prediction
        )

        self.trend_cache[metric_name] = trend

        logger.info(f"Trend analyzed for {metric_name}: {direction} (strength: {strength:.2f})")

        return trend

    def _calculate_trend_direction(self, values: List[float]) -> Tuple[str, float]:
        """
        Calculate trend direction and strength

        Returns:
            (direction, strength) where direction is "increasing"/"decreasing"/"stable"
            and strength is 0.0-1.0
        """
        if len(values) < 3:
            return ("stable", 0.0)

        # Simple linear regression
        n = len(values)
        x = list(range(n))
        y = values

        # Calculate slope
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return ("stable", 0.0)

        slope = numerator / denominator

        # Calculate R-squared (strength)
        y_pred = [slope * x[i] + (y_mean - slope * x_mean) for i in range(n)]
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))

        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        strength = max(0.0, min(1.0, abs(r_squared)))

        # Determine direction
        threshold = 0.01 * y_mean if y_mean != 0 else 0.01
        if abs(slope) < threshold:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        return (direction, strength)

    async def _check_anomaly(self, metric_name: str, value: float):
        """Check if value is anomalous"""
        data = self.time_series_data[metric_name]
        recent_values = [d["value"] for d in data[-20:]]  # Last 20 values

        if len(recent_values) < 5:
            return

        # Calculate statistics
        mean = statistics.mean(recent_values)
        stdev = statistics.stdev(recent_values) if len(recent_values) > 1 else 0

        # Check if outside 2 standard deviations
        if stdev > 0 and abs(value - mean) > 2 * stdev:
            anomaly = {
                "metric": metric_name,
                "value": value,
                "expected_range": (mean - 2*stdev, mean + 2*stdev),
                "timestamp": datetime.utcnow().isoformat(),
                "severity": "high" if abs(value - mean) > 3 * stdev else "medium"
            }

            self.anomalies_detected.append(anomaly)
            logger.warning(f"Anomaly detected in {metric_name}: {value} (expected: {mean:.2f} ± {2*stdev:.2f})")

    async def predict_future_state(
        self,
        metric_name: str,
        forecast_days: int = 7
    ) -> Optional[Dict[str, Any]]:
        """
        Predict future state of a metric

        Args:
            metric_name: Metric to forecast
            forecast_days: Days into future

        Returns:
            Prediction dict or None
        """
        trend = await self.analyze_trend(metric_name, window_days=30)

        if not trend or trend.strength < 0.5:
            return None

        data = self.time_series_data[metric_name]
        recent_values = [d["value"] for d in data[-10:]]

        if len(recent_values) < 3:
            return None

        # Simple forecast based on trend
        current_value = recent_values[-1]
        avg_change = (recent_values[-1] - recent_values[0]) / len(recent_values)

        predicted_value = current_value + (avg_change * forecast_days)

        # Generate warning if needed
        warning = None
        if trend.direction == "increasing" and predicted_value > current_value * 1.5:
            warning = f"Significant increase predicted in {metric_name}. Recommend proactive intervention."
        elif trend.direction == "decreasing" and predicted_value < current_value * 0.5:
            warning = f"Significant decrease predicted in {metric_name}. Investigate potential causes."

        prediction = {
            "metric": metric_name,
            "current_value": current_value,
            "predicted_value": predicted_value,
            "forecast_days": forecast_days,
            "confidence": trend.strength,
            "trend_direction": trend.direction,
            "warning": warning,
            "prediction_date": (datetime.utcnow() + timedelta(days=forecast_days)).isoformat()
        }

        self.predictions.append(prediction)

        logger.info(f"Forecast for {metric_name}: {current_value} → {predicted_value} ({forecast_days} days)")

        return prediction

    async def detect_patterns(
        self,
        metric_name: str,
        pattern_type: str = "seasonal"
    ) -> Optional[Dict[str, Any]]:
        """
        Detect patterns in time series data

        Args:
            metric_name: Metric to analyze
            pattern_type: Type of pattern ("seasonal", "cyclical", "weekly")

        Returns:
            Pattern analysis or None
        """
        if metric_name not in self.time_series_data:
            return None

        data = self.time_series_data[metric_name]
        if len(data) < 14:  # Need at least 2 weeks
            return None

        if pattern_type == "weekly":
            # Analyze day-of-week patterns
            dow_values = defaultdict(list)
            for record in data:
                dow = record["timestamp"].weekday()  # 0=Monday, 6=Sunday
                dow_values[dow].append(record["value"])

            # Calculate averages per day
            dow_averages = {
                dow: sum(values) / len(values)
                for dow, values in dow_values.items()
                if values
            }

            if not dow_averages:
                return None

            # Find peak day
            peak_day = max(dow_averages.items(), key=lambda x: x[1])
            low_day = min(dow_averages.items(), key=lambda x: x[1])

            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

            return {
                "pattern_type": "weekly",
                "metric": metric_name,
                "peak_day": day_names[peak_day[0]],
                "peak_value": peak_day[1],
                "low_day": day_names[low_day[0]],
                "low_value": low_day[1],
                "variance": max(dow_averages.values()) - min(dow_averages.values()),
                "insight": f"{metric_name} peaks on {day_names[peak_day[0]]} and lowest on {day_names[low_day[0]]}"
            }

        return None

    async def get_risk_predictions(self) -> List[Dict[str, Any]]:
        """
        Get risk-specific predictions

        Returns:
            List of risk predictions
        """
        predictions = []

        # Analyze risk count trend
        if "risk_count" in self.time_series_data:
            trend = await self.analyze_trend("risk_count", window_days=30)
            if trend and trend.direction == "increasing" and trend.strength > 0.6:
                predictions.append({
                    "type": "risk_increase",
                    "severity": "high",
                    "message": "Risk count trending upward. Recommend comprehensive risk review.",
                    "confidence": trend.strength
                })

        # Analyze incident frequency
        if "incident_count" in self.time_series_data:
            trend = await self.analyze_trend("incident_count", window_days=14)
            if trend and trend.direction == "increasing":
                predictions.append({
                    "type": "incident_frequency",
                    "severity": "critical" if trend.strength > 0.7 else "high",
                    "message": "Incident frequency increasing. Review preventive controls.",
                    "confidence": trend.strength
                })

        return predictions

    async def get_analytics_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive analytics insights

        Returns:
            Analytics insights dictionary
        """
        # Get all active trends
        trends_summary = []
        for metric_name in self.time_series_data.keys():
            trend = await self.analyze_trend(metric_name, window_days=30)
            if trend and trend.strength > 0.5:
                trends_summary.append({
                    "metric": metric_name,
                    "direction": trend.direction,
                    "strength": round(trend.strength, 3),
                    "prediction": trend.prediction
                })

        # Get recent anomalies (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_anomalies = [
            a for a in self.anomalies_detected
            if datetime.fromisoformat(a["timestamp"]) >= cutoff
        ]

        return {
            "metrics_tracked": len(self.time_series_data),
            "total_data_points": sum(len(data) for data in self.time_series_data.values()),
            "active_trends": trends_summary,
            "recent_anomalies": recent_anomalies[-10:],
            "total_predictions": len(self.predictions),
            "total_anomalies": len(self.anomalies_detected),
            "prediction_accuracy": round(sum(self.prediction_accuracy) / len(self.prediction_accuracy), 3) if self.prediction_accuracy else None
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get quick statistics"""
        return {
            "predictive_analytics": "active",
            "metrics_tracked": len(self.time_series_data),
            "trends_cached": len(self.trend_cache),
            "predictions_made": len(self.predictions),
            "anomalies_detected": len(self.anomalies_detected)
        }
