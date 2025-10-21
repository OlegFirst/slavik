"""
Prediction Tasks - Forecasting and Simulations
===============================================
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from celery_app import app
from tasks.learning_tasks import CallbackTask

logger = logging.getLogger(__name__)


@app.task(base=CallbackTask, bind=True)
def generate_daily_predictions(self) -> Dict[str, Any]:
    """
    Daily task: Generate predictions for all active workflows

    Runs at 6 AM daily
    """
    logger.info(" Generating daily predictions...")

    try:
        from intelligent_core.predictive.services.prediction_engine import PredictionEngine

        engine = PredictionEngine()

        # Get all active workflows
        active_workflows = engine.get_active_workflows()

        predictions = []
        for workflow in active_workflows:
            prediction = engine.predict_completion_time(workflow['id'])
            predictions.append(prediction)

            # Publish anomaly alerts
            if prediction.get('anomaly_detected'):
                publish_anomaly_alert(workflow['id'], prediction)

        logger.info(f" Generated {len(predictions)} predictions")

        return {
            'status': 'success',
            'predictions_count': len(predictions),
            'anomalies_detected': sum(1 for p in predictions if p.get('anomaly_detected'))
        }

    except Exception as exc:
        logger.error(f" Prediction generation failed: {exc}")
        raise


@app.task(base=CallbackTask, bind=True)
def run_monte_carlo_simulation(self, scenario_id: str, iterations: int = 10000) -> Dict[str, Any]:
    """
    Run Monte Carlo simulation for risk scenario

    Heavy computation - runs in background
    """
    logger.info(f" Running Monte Carlo simulation: {scenario_id} ({iterations} iterations)")

    try:
        from intelligent_core.predictive.services.monte_carlo import MonteCarloEngine

        engine = MonteCarloEngine()

        # Run simulation
        results = engine.run_simulation(scenario_id, iterations)

        # Store results
        engine.store_results(scenario_id, results)

        # Publish completion event
        from shared.eventbus import get_eventbus
        eventbus = get_eventbus()
        if eventbus:
            eventbus.publish_sync(
                'prediction.simulation_completed',
                {
                    'scenario_id': scenario_id,
                    'iterations': iterations,
                    'results': results
                }
            )

        logger.info(f" Simulation completed: {scenario_id}")

        return {
            'status': 'success',
            'scenario_id': scenario_id,
            'iterations': iterations,
            'results': results
        }

    except Exception as exc:
        logger.error(f" Simulation failed: {exc}")
        raise self.retry(exc=exc, countdown=300)


@app.task(base=CallbackTask)
def forecast_resource_needs(organization_id: str, horizon_days: int = 90) -> Dict[str, Any]:
    """
    Forecast resource needs for organization
    """
    logger.info(f" Forecasting resource needs: {organization_id} ({horizon_days} days)")

    try:
        from intelligent_core.predictive.services.forecasting import ForecastEngine

        engine = ForecastEngine()

        # Historical data
        historical = engine.get_historical_resource_usage(organization_id, days=365)

        # Forecast
        forecast = engine.forecast_resources(historical, horizon=horizon_days)

        return {
            'status': 'success',
            'organization_id': organization_id,
            'horizon_days': horizon_days,
            'forecast': forecast
        }

    except Exception as exc:
        logger.error(f" Forecasting failed: {exc}")
        raise


def publish_anomaly_alert(workflow_id: str, prediction: Dict):
    """Publish anomaly alert to EventBus"""
    from shared.eventbus import get_eventbus

    eventbus = get_eventbus()
    if eventbus:
        eventbus.publish_sync(
            'prediction.anomaly_detected',
            {
                'workflow_id': workflow_id,
                'prediction': prediction,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
