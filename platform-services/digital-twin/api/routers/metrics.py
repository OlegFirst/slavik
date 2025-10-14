"""
Metrics Endpoints

REST API endpoints for metrics, health scores, and predictions
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel, Field

from storage import PostgreSQLStorage, RedisCache

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class MetricSeriesCreate(BaseModel):
    """Metric series creation request"""
    twin_id: str = Field(..., description="Digital Twin ID")
    metric_name: str = Field(..., description="Metric name")
    aggregation: Optional[str] = Field(None, description="Aggregation type")
    points: dict = Field(..., description="Data points array")


class HealthScoreCreate(BaseModel):
    """Health score creation request"""
    twin_id: str = Field(..., description="Digital Twin ID")
    overall: float = Field(..., ge=0, le=1, description="Overall score")
    financial: float = Field(..., ge=0, le=1, description="Financial score")
    operational: float = Field(..., ge=0, le=1, description="Operational score")
    impact: float = Field(..., ge=0, le=1, description="Impact score")
    sustainability: float = Field(..., ge=0, le=1, description="Sustainability score")


class PredictionCreate(BaseModel):
    """Prediction creation request"""
    id: str = Field(..., description="Prediction ID")
    twin_id: str = Field(..., description="Digital Twin ID")
    prediction_type: str = Field(..., description="Prediction type")
    timeframe_months: int = Field(..., ge=1, description="Timeframe in months")
    predicted_value: float = Field(..., description="Predicted value")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level")
    lower_bound: Optional[float] = Field(None, description="Lower confidence bound")
    upper_bound: Optional[float] = Field(None, description="Upper confidence bound")
    assumptions: Optional[dict] = Field(None, description="Assumptions list")
    factors: Optional[dict] = Field(None, description="Influencing factors")
    methodology: Optional[str] = Field(None, description="Prediction methodology")


class MetricSeriesResponse(BaseModel):
    """Metric series response"""
    id: int
    twin_id: str
    metric_name: str
    aggregation: Optional[str]
    points: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HealthScoreResponse(BaseModel):
    """Health score response"""
    id: int
    twin_id: str
    overall: float
    financial: float
    operational: float
    impact: float
    sustainability: float
    calculated_at: datetime

    class Config:
        from_attributes = True


class PredictionResponse(BaseModel):
    """Prediction response"""
    id: str
    twin_id: str
    prediction_type: str
    timeframe_months: int
    predicted_value: float
    confidence: float
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    assumptions: Optional[dict]
    factors: Optional[dict]
    methodology: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# DEPENDENCIES
# ============================================

def get_storage(request: Request) -> PostgreSQLStorage:
    """Get storage dependency"""
    return request.app.state.app_state.storage


def get_cache(request: Request) -> RedisCache:
    """Get cache dependency"""
    return request.app.state.app_state.cache


# ============================================
# METRIC SERIES ENDPOINTS
# ============================================

@router.post("/series", response_model=MetricSeriesResponse, status_code=201)
async def create_metric_series(
    metric: MetricSeriesCreate,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache)
):
    """
    Create metric series

    Stores time series metrics data
    """
    try:
        # Verify twin exists
        org = await storage.get_organization(twin_id=metric.twin_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Create metric series
        metric_model = await storage.create_metric_series(metric.model_dump())

        # Cache it
        await cache.cache_metrics(
            metric.twin_id,
            metric.metric_name,
            metric.model_dump()
        )

        logger.info(f"Created metric series: {metric.metric_name} for {metric.twin_id}")

        return MetricSeriesResponse.model_validate(metric_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create metric series: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/series/{twin_id}", response_model=List[MetricSeriesResponse])
async def get_metrics(
    twin_id: str,
    metric_name: Optional[str] = Query(None, description="Filter by metric name"),
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache)
):
    """
    Get metric series

    Retrieves time series metrics for digital twin
    """
    try:
        # Try cache if specific metric requested
        if metric_name:
            cached = await cache.get_metrics(twin_id, metric_name)
            if cached:
                logger.debug(f"Cache hit for metrics: {twin_id}:{metric_name}")
                return [MetricSeriesResponse(**cached)]

        # Get from database
        metrics = await storage.get_metrics(twin_id, metric_name)

        if not metrics:
            return []

        # Cache individual metrics
        for metric in metrics:
            await cache.cache_metrics(
                twin_id,
                metric.metric_name,
                {
                    'id': metric.id,
                    'twin_id': metric.twin_id,
                    'metric_name': metric.metric_name,
                    'aggregation': metric.aggregation,
                    'points': metric.points,
                    'created_at': metric.created_at.isoformat(),
                    'updated_at': metric.updated_at.isoformat()
                }
            )

        return [MetricSeriesResponse.model_validate(m) for m in metrics]

    except Exception as e:
        logger.error(f"Failed to get metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# HEALTH SCORE ENDPOINTS
# ============================================

@router.post("/health", response_model=HealthScoreResponse, status_code=201)
async def create_health_score(
    health: HealthScoreCreate,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache)
):
    """
    Create health score

    Stores health score snapshot
    """
    try:
        # Verify twin exists
        org = await storage.get_organization(twin_id=health.twin_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Create health score
        health_data = health.model_dump()
        health_data['calculated_at'] = datetime.utcnow()

        health_model = await storage.create_health_score(health_data)

        # Cache it
        await cache.cache_health_score(health.twin_id, health.model_dump())

        # Update organization health score
        await storage.update_organization(org.id, {
            'health_score': health.overall
        })

        logger.info(f"Created health score for {health.twin_id}: {health.overall}")

        return HealthScoreResponse.model_validate(health_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create health score: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/{twin_id}", response_model=List[HealthScoreResponse])
async def get_health_scores(
    twin_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache)
):
    """
    Get health score history

    Retrieves health score snapshots over time
    """
    try:
        # Try cache for latest
        if limit == 1:
            cached = await cache.get_health_score(twin_id)
            if cached:
                logger.debug(f"Cache hit for health score: {twin_id}")
                return [HealthScoreResponse(**cached)]

        # Get from database
        health_scores = await storage.get_health_scores(twin_id, limit)

        if not health_scores:
            return []

        # Cache latest
        if health_scores:
            latest = health_scores[0]
            await cache.cache_health_score(
                twin_id,
                {
                    'id': latest.id,
                    'twin_id': latest.twin_id,
                    'overall': latest.overall,
                    'financial': latest.financial,
                    'operational': latest.operational,
                    'impact': latest.impact,
                    'sustainability': latest.sustainability,
                    'calculated_at': latest.calculated_at.isoformat()
                }
            )

        return [HealthScoreResponse.model_validate(h) for h in health_scores]

    except Exception as e:
        logger.error(f"Failed to get health scores: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/{twin_id}/latest", response_model=HealthScoreResponse)
async def get_latest_health_score(
    twin_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache)
):
    """
    Get latest health score

    Retrieves most recent health score snapshot
    """
    try:
        # Try cache
        cached = await cache.get_health_score(twin_id)
        if cached:
            return HealthScoreResponse(**cached)

        # Get from database
        health_scores = await storage.get_health_scores(twin_id, limit=1)

        if not health_scores:
            raise HTTPException(status_code=404, detail="No health scores found")

        latest = health_scores[0]

        # Cache it
        await cache.cache_health_score(
            twin_id,
            {
                'id': latest.id,
                'twin_id': latest.twin_id,
                'overall': latest.overall,
                'financial': latest.financial,
                'operational': latest.operational,
                'impact': latest.impact,
                'sustainability': latest.sustainability,
                'calculated_at': latest.calculated_at.isoformat()
            }
        )

        return HealthScoreResponse.model_validate(latest)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get latest health score: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PREDICTION ENDPOINTS
# ============================================

@router.post("/predictions", response_model=PredictionResponse, status_code=201)
async def create_prediction(
    prediction: PredictionCreate,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache)
):
    """
    Create prediction

    Stores prediction result
    """
    try:
        # Verify twin exists
        org = await storage.get_organization(twin_id=prediction.twin_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Create prediction
        pred_model = await storage.create_prediction(prediction.model_dump())

        # Cache it
        await cache.cache_prediction(prediction.id, prediction.model_dump())

        logger.info(f"Created prediction: {prediction.id} for {prediction.twin_id}")

        return PredictionResponse.model_validate(pred_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/{pred_id}", response_model=PredictionResponse)
async def get_prediction(
    pred_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache)
):
    """
    Get prediction by ID

    Retrieves prediction with caching
    """
    try:
        # Try cache
        cached = await cache.get_prediction(pred_id)
        if cached:
            logger.debug(f"Cache hit for prediction: {pred_id}")
            return PredictionResponse(**cached)

        # Get from database - need to implement get_prediction in storage
        predictions = await storage.get_predictions(twin_id=None, prediction_type=None)
        pred_model = next((p for p in predictions if p.id == pred_id), None)

        if not pred_model:
            raise HTTPException(status_code=404, detail="Prediction not found")

        # Cache it
        await cache.cache_prediction(
            pred_id,
            {
                'id': pred_model.id,
                'twin_id': pred_model.twin_id,
                'prediction_type': pred_model.prediction_type,
                'timeframe_months': pred_model.timeframe_months,
                'predicted_value': pred_model.predicted_value,
                'confidence': pred_model.confidence,
                'lower_bound': pred_model.lower_bound,
                'upper_bound': pred_model.upper_bound,
                'assumptions': pred_model.assumptions,
                'factors': pred_model.factors,
                'methodology': pred_model.methodology,
                'created_at': pred_model.created_at.isoformat()
            }
        )

        return PredictionResponse.model_validate(pred_model)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/twin/{twin_id}", response_model=List[PredictionResponse])
async def get_predictions(
    twin_id: str,
    prediction_type: Optional[str] = Query(None, description="Filter by prediction type"),
    storage: PostgreSQLStorage = Depends(get_storage)
):
    """
    Get predictions for twin

    Retrieves predictions with optional type filter
    """
    try:
        # Get from database
        predictions = await storage.get_predictions(twin_id, prediction_type)

        if not predictions:
            return []

        return [PredictionResponse.model_validate(p) for p in predictions]

    except Exception as e:
        logger.error(f"Failed to get predictions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/{twin_id}")
async def get_metrics_dashboard(
    twin_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache)
):
    """
    Get metrics dashboard

    Returns comprehensive metrics overview for digital twin
    """
    try:
        # Verify twin exists
        org = await storage.get_organization(twin_id=twin_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Get latest health score
        health_scores = await storage.get_health_scores(twin_id, limit=1)
        latest_health = health_scores[0] if health_scores else None

        # Get recent metrics
        metrics = await storage.get_metrics(twin_id, metric_name=None)

        # Get recent predictions
        predictions = await storage.get_predictions(twin_id, prediction_type=None)

        # Build dashboard
        dashboard = {
            'twin_id': twin_id,
            'organization': {
                'id': org.id,
                'name': org.name,
                'org_type': org.org_type,
                'industry': org.industry,
                'employee_count': org.employee_count,
                'annual_revenue': org.annual_revenue
            },
            'health': {
                'overall': latest_health.overall if latest_health else org.health_score,
                'financial': latest_health.financial if latest_health else None,
                'operational': latest_health.operational if latest_health else None,
                'impact': latest_health.impact if latest_health else None,
                'sustainability': latest_health.sustainability if latest_health else None,
                'last_updated': latest_health.calculated_at.isoformat() if latest_health else None
            } if latest_health else None,
            'scores': {
                'health': org.health_score,
                'maturity': org.maturity_level,
                'completeness': org.completeness_score,
                'quality': org.quality_score,
                'risk': org.risk_score
            },
            'metrics': {
                'available': [m.metric_name for m in metrics],
                'count': len(metrics)
            },
            'predictions': {
                'count': len(predictions),
                'types': list(set(p.prediction_type for p in predictions))
            }
        }

        return dashboard

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metrics dashboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
