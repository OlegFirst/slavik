"""
Integration Endpoints

REST API endpoints for external service integrations (BIA Engine, Scenario AI)
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import os

from storage.postgres_storage import PostgreSQLStorage
from storage.redis_cache import RedisCache
from bridges.bia_engine.client import BIAEngineClient
from bridges.scenario_ai.client import ScenarioAIClient
from api.auth.dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations", tags=["integrations"])


# ============================================
# DEPENDENCIES
# ============================================

def get_storage() -> PostgreSQLStorage:
    """Get storage instance (placeholder - will be injected by app)"""
    from api.app import storage
    return storage


def get_cache() -> RedisCache:
    """Get cache instance (placeholder - will be injected by app)"""
    from api.app import cache
    return cache


def get_bia_client() -> BIAEngineClient:
    """Get BIA Engine client"""
    base_url = os.getenv('BIA_ENGINE_URL', 'http://bia-engine:8001')
    return BIAEngineClient(base_url=base_url)


def get_scenario_ai_client() -> ScenarioAIClient:
    """Get Scenario AI client"""
    base_url = os.getenv('SCENARIO_AI_URL', 'http://scenario-ai:8002')
    return ScenarioAIClient(base_url=base_url)


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class BIAAnalysisRequest(BaseModel):
    """BIA analysis request"""
    include_processes: bool = Field(default=True, description="Include process analysis")
    include_dependencies: bool = Field(default=True, description="Include dependency analysis")
    include_financial: bool = Field(default=True, description="Include financial impact")
    custom_parameters: Optional[Dict[str, Any]] = Field(default=None, description="Custom analysis parameters")


class BIAAnalysisResponse(BaseModel):
    """BIA analysis response"""
    status: str = Field(..., description="Analysis status")
    twin_id: str = Field(..., description="Digital Twin ID")
    analysis_id: Optional[str] = Field(None, description="BIA analysis ID")
    criticality_scores: Optional[Dict[str, float]] = Field(None, description="Process criticality scores")
    rto_rpo: Optional[Dict[str, Any]] = Field(None, description="RTO/RPO calculations")
    financial_impact: Optional[Dict[str, float]] = Field(None, description="Financial impact analysis")
    recommendations: Optional[List[str]] = Field(None, description="BIA recommendations")
    completed_at: Optional[datetime] = Field(None, description="Analysis completion timestamp")


class ScenarioGenerationRequest(BaseModel):
    """AI scenario generation request"""
    scenario_type: Optional[str] = Field(None, description="Scenario type (e.g. 'cyberattack', 'pandemic')")
    risk_level: Optional[str] = Field(default="medium", description="Risk level (low/medium/high/critical)")
    include_mitigation: bool = Field(default=True, description="Include mitigation strategies")
    custom_context: Optional[Dict[str, Any]] = Field(None, description="Custom context for scenario generation")


class ScenarioGenerationResponse(BaseModel):
    """AI scenario generation response"""
    status: str = Field(..., description="Generation status")
    twin_id: str = Field(..., description="Digital Twin ID")
    scenario_id: Optional[str] = Field(None, description="Generated scenario ID")
    scenario_type: Optional[str] = Field(None, description="Scenario type")
    description: Optional[str] = Field(None, description="Scenario description")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Scenario parameters")
    mitigation_strategies: Optional[List[str]] = Field(None, description="Mitigation strategies")
    simulation_id: Optional[str] = Field(None, description="Created simulation ID")


# ============================================
# BIA ENGINE ENDPOINTS
# ============================================

@router.post("/bia/analyze/{twin_id}", response_model=BIAAnalysisResponse)
async def analyze_with_bia_engine(
    twin_id: str,
    request: BIAAnalysisRequest = BIAAnalysisRequest(),
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache),
    current_user = Depends(get_current_active_user)
):
    """
    Run BIA (Business Impact Analysis) on digital twin using BIA Engine service

    This endpoint:
    1. Retrieves organization data from digital twin
    2. Sends data to BIA Engine for analysis
    3. Stores BIA results back in digital twin
    4. Returns comprehensive BIA report

    BIA Engine analyzes:
    - Process criticality
    - RTO/RPO objectives
    - Financial impact of downtime
    - Dependencies and SPOFs
    - Recovery priorities
    """
    try:
        logger.info(f"Starting BIA analysis for twin_id: {twin_id}")

        # Get organization/digital twin
        org_model = await storage.get_organization(twin_id=twin_id)
        if not org_model:
            raise HTTPException(status_code=404, detail=f"Digital twin not found: {twin_id}")

        # Prepare data for BIA Engine
        bcm_data = org_model.bcm_data or {}

        organization_data = {
            'name': org_model.name,
            'industry': org_model.industry,
            'employee_count': org_model.employee_count or 100,
            'annual_revenue': org_model.annual_revenue or 1000000.0,
            'processes': bcm_data.get('processes', []),
            'dependencies': bcm_data.get('dependencies', {}),
            'recovery_objectives': bcm_data.get('recovery_objectives', {}),
            'include_processes': request.include_processes,
            'include_dependencies': request.include_dependencies,
            'include_financial': request.include_financial
        }

        # Add custom parameters
        if request.custom_parameters:
            organization_data.update(request.custom_parameters)

        # Call BIA Engine
        bia_client = get_bia_client()

        try:
            # Check service health first
            health = await bia_client.health_check()
            if health.get('status') != 'healthy':
                logger.warning(f"BIA Engine health check warning: {health}")
                # Continue anyway - service might still work

            # Run analysis
            bia_result = await bia_client.analyze_organization(organization_data)

        finally:
            await bia_client.close()

        # Extract results
        analysis_id = bia_result.get('analysis_id')
        criticality_scores = bia_result.get('criticality_scores', {})
        rto_rpo = bia_result.get('rto_rpo', {})
        financial_impact = bia_result.get('financial_impact', {})
        recommendations = bia_result.get('recommendations', [])

        # Update digital twin with BIA results
        updated_bcm_data = {
            **bcm_data,
            'bia_analysis': {
                'analysis_id': analysis_id,
                'completed_at': datetime.utcnow().isoformat(),
                'criticality_scores': criticality_scores,
                'rto_rpo': rto_rpo,
                'financial_impact': financial_impact,
                'recommendations': recommendations
            }
        }

        await storage.update_organization(org_model.id, {
            'bcm_data': updated_bcm_data
        })

        # Cache result
        cache_key = f"dt:bia:{twin_id}"
        await cache.set(cache_key, bia_result, ttl=3600)  # Cache for 1 hour

        logger.info(f"BIA analysis completed for twin_id: {twin_id}")

        return BIAAnalysisResponse(
            status='completed',
            twin_id=twin_id,
            analysis_id=analysis_id,
            criticality_scores=criticality_scores,
            rto_rpo=rto_rpo,
            financial_impact=financial_impact,
            recommendations=recommendations,
            completed_at=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"BIA analysis failed for twin_id {twin_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"BIA analysis failed: {str(e)}"
        )


@router.get("/bia/status/{twin_id}")
async def get_bia_analysis_status(
    twin_id: str,
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache),
    current_user = Depends(get_current_active_user)
):
    """
    Get BIA analysis status and cached results for digital twin
    """
    try:
        # Check cache first
        cache_key = f"dt:bia:{twin_id}"
        cached_result = await cache.get(cache_key)

        if cached_result:
            return {
                'status': 'cached',
                'twin_id': twin_id,
                'result': cached_result,
                'source': 'cache'
            }

        # Get from database
        org_model = await storage.get_organization(twin_id=twin_id)
        if not org_model:
            raise HTTPException(status_code=404, detail=f"Digital twin not found: {twin_id}")

        bcm_data = org_model.bcm_data or {}
        bia_analysis = bcm_data.get('bia_analysis')

        if bia_analysis:
            return {
                'status': 'completed',
                'twin_id': twin_id,
                'result': bia_analysis,
                'source': 'database'
            }
        else:
            return {
                'status': 'not_analyzed',
                'twin_id': twin_id,
                'message': 'No BIA analysis found. Run /integrations/bia/analyze first.'
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get BIA status for twin_id {twin_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# SCENARIO AI ENDPOINTS (Placeholder)
# ============================================

@router.post("/ai-scenarios/generate/{twin_id}", response_model=ScenarioGenerationResponse)
async def generate_ai_scenario(
    twin_id: str,
    request: ScenarioGenerationRequest = ScenarioGenerationRequest(),
    storage: PostgreSQLStorage = Depends(get_storage),
    cache: RedisCache = Depends(get_cache),
    current_user = Depends(get_current_active_user)
):
    """
    Generate AI-powered BCM scenario for digital twin using Scenario Orchestrator service

    This endpoint:
    1. Analyzes organization context (industry, size, risk profile)
    2. Generates contextually relevant BCM scenario using AI
    3. Creates simulation with AI-generated parameters
    4. Returns scenario details and simulation ID

    AI considers:
    - Industry-specific risks
    - Organization size and maturity
    - Historical incident data
    - Current threat landscape
    """
    try:
        logger.info(f"Generating AI scenario for twin_id: {twin_id}")

        # Get organization
        org_model = await storage.get_organization(twin_id=twin_id)
        if not org_model:
            raise HTTPException(status_code=404, detail=f"Digital twin not found: {twin_id}")

        # Prepare context for AI
        bcm_data = org_model.bcm_data or {}

        context = {
            'industry': org_model.industry or 'general',
            'company_size': org_model.employee_count or 100,
            'annual_revenue': org_model.annual_revenue or 1000000.0,
            'geographic_locations': bcm_data.get('locations', []),
            'current_maturity': org_model.maturity_level,
            'risk_profile': {
                'risk_score': org_model.risk_score,
                'health_score': org_model.health_score
            }
        }

        # Add custom context
        if request.custom_context:
            context.update(request.custom_context)

        # Call Scenario AI
        ai_client = get_scenario_ai_client()

        try:
            # Check service health
            health = await ai_client.health_check()
            if health.get('status') != 'healthy':
                logger.warning(f"Scenario AI health check warning: {health}")

            # Generate scenario
            ai_result = await ai_client.generate_scenario(
                context=context,
                scenario_type=request.scenario_type,
                risk_level=request.risk_level
            )

        finally:
            await ai_client.close()

        # Extract scenario details
        scenario_id = ai_result.get('scenario_id')
        scenario_type = ai_result.get('scenario_type')
        description = ai_result.get('description')
        parameters = ai_result.get('parameters', {})
        mitigation_strategies = ai_result.get('mitigation_strategies', [])

        # Create simulation with AI-generated scenario
        from uuid import uuid4
        from core.models.base import SimulationScenarioType, SimulationStatus

        sim_id = f"sim-{uuid4().hex[:12]}"

        # Map AI scenario type to our enum
        try:
            sim_scenario = SimulationScenarioType(scenario_type)
        except ValueError:
            sim_scenario = SimulationScenarioType.CUSTOM

        sim_data = {
            'id': sim_id,
            'twin_id': twin_id,
            'scenario': sim_scenario,
            'status': SimulationStatus.PENDING,
            'parameters': parameters,
            'timeline': ai_result.get('timeline', {}),
            'custom_metadata': {
                'ai_generated': True,
                'scenario_id': scenario_id,
                'ai_description': description
            }
        }

        sim_model = await storage.create_simulation(sim_data)

        # Cache result
        cache_key = f"dt:ai-scenario:{twin_id}:{scenario_id}"
        await cache.set(cache_key, ai_result, ttl=3600)

        logger.info(f"AI scenario generated for twin_id: {twin_id}, simulation created: {sim_id}")

        return ScenarioGenerationResponse(
            status='completed',
            twin_id=twin_id,
            scenario_id=scenario_id,
            scenario_type=scenario_type,
            description=description,
            parameters=parameters,
            mitigation_strategies=mitigation_strategies,
            simulation_id=sim_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI scenario generation failed for twin_id {twin_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# HEALTH CHECK
# ============================================

@router.get("/health")
async def check_integrations_health():
    """
    Check health of all external integrations
    """
    health_status = {
        'timestamp': datetime.utcnow().isoformat(),
        'services': {}
    }

    # Check BIA Engine
    try:
        bia_client = get_bia_client()
        bia_health = await bia_client.health_check()
        await bia_client.close()
        health_status['services']['bia_engine'] = bia_health
    except Exception as e:
        health_status['services']['bia_engine'] = {
            'status': 'error',
            'error': str(e)
        }

    # Check Scenario AI
    try:
        ai_client = get_scenario_ai_client()
        ai_health = await ai_client.health_check()
        await ai_client.close()
        health_status['services']['scenario_ai'] = ai_health
    except Exception as e:
        health_status['services']['scenario_ai'] = {
            'status': 'error',
            'error': str(e)
        }

    return health_status
