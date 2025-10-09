"""
Prediction Endpoints

REST API endpoints for predictive analytics and forecasting
"""

import logging
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel, Field

from storage import PostgreSQLStorage
from api.auth.dependencies import get_current_active_user, require_admin

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class PredictionCreate(BaseModel):
    """Prediction creation request"""
    prediction_type: str = Field(..., description="incident_forecast, financial_forecast, etc.")
    scenario_template_id: Optional[str] = None
    input_parameters: dict = Field(..., description="Input data for prediction")
    organization_id: Optional[str] = None  # Optional - can be standalone


class PredictionResponse(BaseModel):
    """Prediction response"""
    id: str
    tenant_id: str
    prediction_type: str
    scenario_template_id: Optional[str]
    input_parameters: dict
    prediction_result: Optional[dict]
    confidence_score: Optional[float]
    predicted_date: Optional[datetime]
    predicted_value: Optional[float]
    factors: Optional[dict]
    recommendations: Optional[dict]
    assumptions: Optional[List[str]]
    model_used: Optional[str]
    model_version: Optional[str]
    methodology: Optional[str]
    status: str
    organization_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PredictionList(BaseModel):
    """Prediction list response"""
    total: int
    items: List[PredictionResponse]
    limit: int


# ============================================
# DEPENDENCIES
# ============================================

def get_storage(request: Request) -> PostgreSQLStorage:
    """Get storage dependency"""
    return request.app.state.app_state.storage


# ============================================
# ENDPOINTS
# ============================================

@router.post("/", response_model=PredictionResponse, status_code=201)
async def create_prediction(
    prediction: PredictionCreate,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Create and run prediction

    Works in two modes:
    1. With organization data (accurate predictions)
    2. Standalone (generic predictions)

    Prediction types:
    - incident_forecast: When incident might occur
    - recovery_time: How long recovery will take
    - impact_assessment: What impact will be
    - risk_probability: Probability of risk
    - financial_forecast: Financial projections
    - resource_needs: Resource requirements
    """
    try:
        prediction_id = f"pred-{uuid4().hex[:12]}"

        # Verify organization ownership if specified
        if prediction.organization_id:
            org = await storage.get_organization(prediction.organization_id)
            if not org or org.tenant_id != current_user.tenant_id:
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to create prediction for this organization"
                )

        # Verify scenario if specified
        if prediction.scenario_template_id:
            scenario = await storage.get_scenario_template(prediction.scenario_template_id)
            if not scenario:
                raise HTTPException(status_code=404, detail="Scenario not found")
            if scenario.tenant_id != current_user.tenant_id and not scenario.is_public:
                raise HTTPException(status_code=403, detail="Not authorized")

        # Run prediction engine
        from core.engine.prediction_engine import PredictionEngine

        engine = PredictionEngine()
        params = prediction.input_parameters

        # Execute prediction based on type
        if prediction.prediction_type == "financial_forecast":
            if prediction.organization_id:
                # With org data
                org = await storage.get_organization(prediction.organization_id)
                from core.models.base import Organization

                organization = Organization(
                    id=org.id,
                    twin_id=org.twin_id,
                    name=org.name,
                    org_type=org.org_type,
                    industry=org.industry,
                    employee_count=org.employee_count or 100,
                    annual_revenue=org.annual_revenue or 1000000.0,
                    annual_budget=org.annual_budget or 500000.0,
                    headquarters=org.headquarters or {},
                    contacts=org.contacts or {},
                    metadata=org.metadata or {}
                )

                result = await engine.predict_financial_trend(
                    organization=organization,
                    time_series=[],  # Would load from history
                    timeframe_months=params.get('timeframe_months', 12)
                )

                prediction_data = {
                    'id': prediction_id,
                    'tenant_id': current_user.tenant_id,
                    'prediction_type': prediction.prediction_type,
                    'scenario_template_id': prediction.scenario_template_id,
                    'input_parameters': params,
                    'prediction_result': {
                        'predicted_value': result.predicted_value,
                        'lower_bound': result.lower_bound,
                        'upper_bound': result.upper_bound
                    },
                    'confidence_score': result.confidence,
                    'predicted_value': result.predicted_value,
                    'factors': result.factors,
                    'recommendations': {},
                    'assumptions': result.assumptions,
                    'model_used': 'linear_regression',
                    'model_version': '1.0',
                    'methodology': result.methodology,
                    'status': 'completed',
                    'organization_id': prediction.organization_id
                }

            else:
                # Standalone (generic)
                current_value = params.get('current_value', 1000000)
                growth_rate = params.get('growth_rate', 0.05)
                timeframe = params.get('timeframe_months', 12)

                predicted_value = current_value * (1 + growth_rate) ** (timeframe / 12)

                prediction_data = {
                    'id': prediction_id,
                    'tenant_id': current_user.tenant_id,
                    'prediction_type': prediction.prediction_type,
                    'scenario_template_id': prediction.scenario_template_id,
                    'input_parameters': params,
                    'prediction_result': {
                        'predicted_value': predicted_value,
                        'lower_bound': predicted_value * 0.8,
                        'upper_bound': predicted_value * 1.2
                    },
                    'confidence_score': 0.5,
                    'predicted_value': predicted_value,
                    'factors': {'growth_rate': growth_rate},
                    'recommendations': {},
                    'assumptions': ['Generic standalone prediction', 'Link organization for accuracy'],
                    'model_used': 'simple_growth',
                    'model_version': '1.0',
                    'methodology': 'Simple compound growth calculation',
                    'status': 'completed',
                    'organization_id': None
                }

        elif prediction.prediction_type == "impact_assessment":
            # Generic impact assessment
            severity = params.get('severity', 'medium')
            duration_days = params.get('duration_days', 14)

            severity_map = {'low': 0.3, 'medium': 0.6, 'high': 0.8, 'critical': 1.0}
            impact_score = severity_map.get(severity, 0.6) * 100

            prediction_data = {
                'id': prediction_id,
                'tenant_id': current_user.tenant_id,
                'prediction_type': prediction.prediction_type,
                'scenario_template_id': prediction.scenario_template_id,
                'input_parameters': params,
                'prediction_result': {
                    'impact_score': impact_score,
                    'duration_days': duration_days,
                    'severity': severity
                },
                'confidence_score': 0.7,
                'predicted_value': impact_score,
                'factors': {'severity': severity, 'duration': duration_days},
                'recommendations': {'mitigation': 'Implement recovery plan'},
                'assumptions': ['Based on severity and duration', 'Generic assessment'],
                'model_used': 'impact_model',
                'model_version': '1.0',
                'methodology': 'Severity-based impact calculation',
                'status': 'completed',
                'organization_id': prediction.organization_id
            }

        else:
            # Fallback for other types
            prediction_data = {
                'id': prediction_id,
                'tenant_id': current_user.tenant_id,
                'prediction_type': prediction.prediction_type,
                'scenario_template_id': prediction.scenario_template_id,
                'input_parameters': params,
                'prediction_result': {},
                'confidence_score': 0.5,
                'factors': {},
                'recommendations': {},
                'assumptions': [f'Prediction type {prediction.prediction_type} not fully implemented'],
                'model_used': 'placeholder',
                'model_version': '1.0',
                'methodology': 'Placeholder',
                'status': 'completed',
                'organization_id': prediction.organization_id
            }

        prediction_model = await storage.create_prediction(prediction_data)

        logger.info(f"Created prediction: {prediction_model.id} by {current_user.email}")

        return PredictionResponse.model_validate(prediction_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=PredictionList)
async def list_predictions(
    prediction_type: Optional[str] = Query(None, description="Filter by type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    organization_id: Optional[str] = Query(None, description="Filter by organization"),
    limit: int = Query(100, ge=1, le=1000),
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    List predictions

    Returns tenant's predictions with optional filters
    """
    try:
        predictions = await storage.list_predictions(
            tenant_id=current_user.tenant_id,
            prediction_type=prediction_type,
            status=status,
            organization_id=organization_id,
            limit=limit
        )

        items = [PredictionResponse.model_validate(p) for p in predictions]

        return PredictionList(
            total=len(items),
            items=items,
            limit=limit
        )

    except Exception as e:
        logger.error(f"Failed to list predictions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Get prediction by ID

    Verifies ownership
    """
    try:
        prediction = await storage.get_prediction(prediction_id)

        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")

        if prediction.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this prediction")

        return PredictionResponse.model_validate(prediction)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{prediction_id}")
async def delete_prediction(
    prediction_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(require_admin)
):
    """
    Delete prediction

    Admin only
    """
    try:
        # Verify ownership
        prediction = await storage.get_prediction(prediction_id)

        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")

        if prediction.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this prediction")

        await storage.delete_prediction(prediction_id)

        logger.info(f"Deleted prediction: {prediction_id}")

        return {"status": "deleted", "prediction_id": prediction_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types/available")
async def get_available_prediction_types():
    """
    Get list of available prediction types
    """
    types = [
        {
            "value": "incident_forecast",
            "label": "Incident Forecast",
            "description": "Predict when incidents might occur"
        },
        {
            "value": "recovery_time",
            "label": "Recovery Time Prediction",
            "description": "Estimate how long recovery will take"
        },
        {
            "value": "impact_assessment",
            "label": "Impact Assessment",
            "description": "Predict the impact of scenarios"
        },
        {
            "value": "risk_probability",
            "label": "Risk Probability",
            "description": "Calculate probability of risks"
        },
        {
            "value": "financial_forecast",
            "label": "Financial Forecast",
            "description": "Project financial metrics"
        },
        {
            "value": "resource_needs",
            "label": "Resource Needs",
            "description": "Predict resource requirements"
        }
    ]

    return {
        "total": len(types),
        "types": types
    }


@router.get("/organization/{org_id}/summary")
async def get_organization_predictions_summary(
    org_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Get predictions summary for organization

    Returns summary of all predictions for specific organization
    """
    try:
        # Verify org ownership
        org = await storage.get_organization(org_id)
        if not org or org.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Get all predictions for org
        predictions = await storage.list_predictions(
            tenant_id=current_user.tenant_id,
            organization_id=org_id,
            limit=1000
        )

        # Group by type
        summary = {}
        for pred in predictions:
            pred_type = pred.prediction_type
            if pred_type not in summary:
                summary[pred_type] = {
                    'total': 0,
                    'completed': 0,
                    'pending': 0,
                    'failed': 0,
                    'avg_confidence': 0.0,
                    'latest': None
                }

            summary[pred_type]['total'] += 1
            summary[pred_type][pred.status] = summary[pred_type].get(pred.status, 0) + 1

            if pred.confidence_score:
                summary[pred_type]['avg_confidence'] += pred.confidence_score

            # Track latest
            if not summary[pred_type]['latest'] or pred.created_at > summary[pred_type]['latest']['created_at']:
                summary[pred_type]['latest'] = {
                    'id': pred.id,
                    'status': pred.status,
                    'created_at': pred.created_at.isoformat(),
                    'confidence': pred.confidence_score
                }

        # Calculate averages
        for pred_type in summary:
            if summary[pred_type]['total'] > 0:
                summary[pred_type]['avg_confidence'] /= summary[pred_type]['total']

        return {
            'organization_id': org_id,
            'organization_name': org.name,
            'total_predictions': len(predictions),
            'by_type': summary
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get predictions summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monte-carlo", response_model=PredictionResponse, status_code=201)
async def run_monte_carlo_prediction(
    prediction: PredictionCreate,
    n_iterations: int = Query(10000, ge=100, le=100000, description="Number of Monte Carlo iterations"),
    distribution: str = Query("normal", regex="^(normal|lognormal|uniform)$", description="Distribution type"),
    storage: PostgreSQLStorage = Depends(get_storage),
    current_user = Depends(get_current_active_user)
):
    """
    Run Monte Carlo probabilistic prediction

    Returns full probability distribution instead of single value

    Provides:
    - Mean, median, std deviation
    - 5th and 95th percentiles (worst/best case)
    - 95% confidence interval
    - Full distribution for visualization

    Example Request:
        POST /api/v1/predictions/monte-carlo?n_iterations=10000&distribution=normal
        {
            "prediction_type": "financial_forecast",
            "organization_id": "org-123",
            "input_parameters": {
                "current_value": 1000000,
                "mean_growth_rate": 0.05,
                "volatility": 0.15,
                "timeframe_months": 12
            }
        }

    Example Response:
        {
            "id": "pred-mc-abc123",
            "prediction_type": "financial_forecast",
            "prediction_result": {
                "mean": 1050000,
                "median": 1048000,
                "percentile_5": 850000,    // Worst case (5%)
                "percentile_95": 1250000,  // Best case (95%)
                "confidence_interval_95": [820000, 1280000],
                "std_dev": 150000,
                "distribution": [...]       // Full distribution for viz
            },
            "confidence_score": 0.95,
            "model_used": "monte_carlo_normal",
            "iterations": 10000
        }
    """
    try:
        # Initialize Monte Carlo engine
        from core.engine.monte_carlo_engine import MonteCarloEngine

        mc_engine = MonteCarloEngine(n_iterations=n_iterations)

        # Verify ownership if organization specified
        if prediction.organization_id:
            org = await storage.get_organization(prediction.organization_id)
            if not org or org.tenant_id != current_user.tenant_id:
                raise HTTPException(403, "Not authorized")

        params = prediction.input_parameters

        # Run Monte Carlo simulation based on prediction type
        if prediction.prediction_type == "financial_forecast":
            # Extract parameters
            current_value = params.get("current_value")
            mean_growth_rate = params.get("mean_growth_rate")
            volatility = params.get("volatility")
            timeframe_months = params.get("timeframe_months", 12)

            if not all([current_value is not None, mean_growth_rate is not None, volatility is not None]):
                raise HTTPException(
                    400,
                    "Missing required parameters: current_value, mean_growth_rate, volatility"
                )

            mc_result = await mc_engine.simulate_financial_forecast(
                current_value=current_value,
                mean_growth_rate=mean_growth_rate,
                volatility=volatility,
                timeframe_months=timeframe_months,
                distribution=distribution
            )

        elif prediction.prediction_type == "impact_assessment":
            # Extract parameters
            scenario_type = params.get("scenario_type")
            organization_params = params.get("organization_params", {})
            scenario_params = params.get("scenario_params", {})

            if not scenario_type:
                raise HTTPException(400, "Missing required parameter: scenario_type")

            # If organization linked, use org data
            if prediction.organization_id:
                org = await storage.get_organization(prediction.organization_id)
                organization_params = {
                    "revenue": org.annual_revenue or 1000000.0,
                    "employees": org.employee_count or 100,
                    "maturity": 3  # Could come from org settings
                }

            mc_result = await mc_engine.simulate_impact_assessment(
                scenario_type=scenario_type,
                organization_params=organization_params,
                scenario_params=scenario_params
            )

        else:
            raise HTTPException(
                400,
                f"Monte Carlo not supported for prediction type: {prediction.prediction_type}"
            )

        # Save prediction to database
        prediction_id = f"pred-mc-{uuid4().hex[:12]}"

        prediction_data = {
            "id": prediction_id,
            "tenant_id": current_user.tenant_id,
            "prediction_type": prediction.prediction_type,
            "scenario_template_id": prediction.scenario_template_id,
            "organization_id": prediction.organization_id,
            "input_parameters": {
                **params,
                "n_iterations": n_iterations,
                "distribution": distribution
            },
            "prediction_result": {
                "method": "monte_carlo",
                "mean": mc_result.mean,
                "median": mc_result.median,
                "std_dev": mc_result.std_dev,
                "percentile_5": mc_result.percentile_5,
                "percentile_25": mc_result.percentile_25,
                "percentile_75": mc_result.percentile_75,
                "percentile_95": mc_result.percentile_95,
                "confidence_interval_95": list(mc_result.confidence_interval_95),
                "distribution": mc_result.distribution,  # For visualization
                "convergence_reached": mc_result.convergence_reached
            },
            "confidence_score": 0.95 if mc_result.convergence_reached else 0.80,
            "predicted_value": mc_result.mean,
            "factors": {
                "distribution_type": distribution,
                "iterations": mc_result.iterations,
                "convergence": mc_result.convergence_reached
            },
            "recommendations": {},
            "assumptions": [
                f"Monte Carlo with {n_iterations} iterations",
                f"{distribution.capitalize()} distribution",
                "Full probability distribution available"
            ],
            "model_used": f"monte_carlo_{distribution}",
            "model_version": "1.0",
            "methodology": f"Monte Carlo simulation with {n_iterations} iterations using {distribution} distribution",
            "status": "completed"
        }

        prediction_model = await storage.create_prediction(prediction_data)

        logger.info(
            f"Monte Carlo prediction created: {prediction_model.id}, "
            f"type={prediction.prediction_type}, "
            f"mean={mc_result.mean:.2f}, "
            f"iterations={n_iterations}"
        )

        return PredictionResponse.model_validate(prediction_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to run Monte Carlo prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
