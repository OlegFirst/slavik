"""
Unit tests for Predictive Analytics
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from core.learning import PredictiveAnalytics


@pytest.fixture
def analytics():
    """Fixture for PredictiveAnalytics"""
    return PredictiveAnalytics()


@pytest.mark.asyncio
async def test_record_metric(analytics):
    """Test recording a metric"""
    result = await analytics.record_metric(
        metric_name="risk_count",
        value=25.0,
        metadata={"severity": "high"}
    )
    
    assert result["metric"] == "risk_count"
    assert result["value"] == 25.0
    assert result["total_records"] == 1
    assert "risk_count" in analytics.time_series_data


@pytest.mark.asyncio
async def test_trend_analysis(analytics):
    """Test trend analysis with increasing values"""
    # Record increasing trend
    for i in range(10):
        await analytics.record_metric(
            metric_name="risk_count",
            value=20.0 + i * 2
        )
    
    trend = await analytics.analyze_trend("risk_count", window_days=30)
    
    assert trend is not None
    assert trend.metric == "risk_count"
    assert trend.direction == "increasing"
    assert trend.strength > 0.8  # Strong upward trend


@pytest.mark.asyncio
async def test_trend_decreasing(analytics):
    """Test trend analysis with decreasing values"""
    # Record decreasing trend
    for i in range(10):
        await analytics.record_metric(
            metric_name="incident_count",
            value=50.0 - i * 3
        )
    
    trend = await analytics.analyze_trend("incident_count", window_days=30)
    
    assert trend is not None
    assert trend.direction == "decreasing"
    assert trend.strength > 0.8


@pytest.mark.asyncio
async def test_trend_stable(analytics):
    """Test trend analysis with stable values"""
    # Record stable values
    for i in range(10):
        await analytics.record_metric(
            metric_name="plan_count",
            value=15.0 + (i % 2) * 0.1  # Minor fluctuation
        )
    
    trend = await analytics.analyze_trend("plan_count", window_days=30)
    
    assert trend is not None
    assert trend.direction == "stable"


@pytest.mark.asyncio
async def test_anomaly_detection(analytics):
    """Test anomaly detection"""
    # Record normal values
    for i in range(20):
        await analytics.record_metric(
            metric_name="incident_count",
            value=5.0 + (i % 3) * 0.5
        )
    
    # Record anomaly
    await analytics.record_metric(
        metric_name="incident_count",
        value=25.0  # Significantly higher
    )
    
    assert len(analytics.anomalies_detected) > 0
    anomaly = analytics.anomalies_detected[-1]
    assert anomaly["metric"] == "incident_count"
    assert anomaly["severity"] in ["medium", "high"]


@pytest.mark.asyncio
async def test_predict_future_state(analytics):
    """Test future state prediction"""
    # Record increasing trend
    for i in range(10):
        await analytics.record_metric(
            metric_name="risk_count",
            value=20.0 + i * 2
        )
    
    prediction = await analytics.predict_future_state(
        metric_name="risk_count",
        forecast_days=7
    )
    
    assert prediction is not None
    assert prediction["metric"] == "risk_count"
    assert prediction["predicted_value"] > prediction["current_value"]
    assert prediction["forecast_days"] == 7
    assert 0.0 <= prediction["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_weekly_pattern_detection(analytics):
    """Test weekly pattern detection"""
    # Record data with weekly pattern
    base_date = datetime.utcnow() - timedelta(days=21)
    for day in range(21):
        date = base_date + timedelta(days=day)
        # Higher values on weekends
        value = 10.0 if date.weekday() >= 5 else 5.0
        
        await analytics.record_metric(
            metric_name="incident_count",
            value=value,
            timestamp=date
        )
    
    pattern = await analytics.detect_patterns(
        metric_name="incident_count",
        pattern_type="weekly"
    )
    
    assert pattern is not None
    assert pattern["pattern_type"] == "weekly"
    assert "peak_day" in pattern
    assert "low_day" in pattern


@pytest.mark.asyncio
async def test_risk_predictions(analytics):
    """Test risk-specific predictions"""
    # Record increasing risk trend
    for i in range(10):
        await analytics.record_metric(
            metric_name="risk_count",
            value=30.0 + i * 3
        )
    
    predictions = await analytics.get_risk_predictions()
    
    # Should detect increasing risk trend
    assert len(predictions) > 0
    risk_pred = predictions[0]
    assert risk_pred["type"] == "risk_increase"
    assert risk_pred["severity"] in ["high", "critical"]


@pytest.mark.asyncio
async def test_analytics_insights(analytics):
    """Test comprehensive analytics insights"""
    # Record multiple metrics
    for i in range(15):
        await analytics.record_metric("risk_count", 20.0 + i)
        await analytics.record_metric("incident_count", 5.0 + i * 0.5)
    
    insights = await analytics.get_analytics_insights()
    
    assert insights["metrics_tracked"] == 2
    assert insights["total_data_points"] == 30
    assert "active_trends" in insights
    assert "recent_anomalies" in insights


def test_calculate_trend_direction(analytics):
    """Test trend direction calculation"""
    # Increasing trend
    values_inc = [10, 12, 14, 16, 18, 20]
    direction, strength = analytics._calculate_trend_direction(values_inc)
    assert direction == "increasing"
    assert strength > 0.9
    
    # Decreasing trend
    values_dec = [20, 18, 16, 14, 12, 10]
    direction, strength = analytics._calculate_trend_direction(values_dec)
    assert direction == "decreasing"
    assert strength > 0.9
    
    # Stable
    values_stable = [15, 15, 15, 15, 15, 15]
    direction, strength = analytics._calculate_trend_direction(values_stable)
    assert direction == "stable"


def test_get_stats(analytics):
    """Test quick stats retrieval"""
    stats = analytics.get_stats()
    
    assert "predictive_analytics" in stats
    assert stats["predictive_analytics"] == "active"
    assert "metrics_tracked" in stats
    assert "predictions_made" in stats


@pytest.mark.asyncio
async def test_insufficient_data(analytics):
    """Test behavior with insufficient data"""
    # Record only 2 data points
    await analytics.record_metric("test_metric", 10.0)
    await analytics.record_metric("test_metric", 12.0)
    
    # Should return None for trend
    trend = await analytics.analyze_trend("test_metric")
    assert trend is None
    
    # Should return None for prediction
    prediction = await analytics.predict_future_state("test_metric")
    assert prediction is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
