"""
Strategic Analyzers Endpoints

10 Analyzers:
1. Compliance Analyzer
2. Risk Analyzer
3. Governance Analyzer
4. Lifecycle Analyzer
5. Learning Analyzer
6. Performance Analyzer
7. Emergency Analyzer
8. Impact Analyzer
9. Plan Analyzer
10. Scenario Analyzer
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyzers", tags=["Analyzers"])

# Import analyzers
try:
    from expertise_center.domains.bcm.analyzers.compliance_analyzer import ComplianceGuardian
    from expertise_center.domains.bcm.analyzers.risk_analyzer import RiskAdvisor
    from expertise_center.domains.bcm.analyzers.governance_analyzer import GovernanceBrain
    from expertise_center.domains.bcm.analyzers.lifecycle_analyzer import LifecycleMonitor
    from expertise_center.domains.bcm.analyzers.learning_analyzer import LearningCoach
    from expertise_center.domains.bcm.analyzers.performance_analyzer import PerformanceAnalyst
    from expertise_center.domains.bcm.analyzers.emergency_analyzer import EmergencyResponse
    from expertise_center.domains.bcm.analyzers.impact_analyzer import ImpactOracle
    from expertise_center.domains.bcm.analyzers.plan_analyzer import PlanGenerator
    from expertise_center.domains.bcm.analyzers.scenario_analyzer import ScenarioCreator
except ImportError as e:
    logger.error(f"Failed to import analyzers: {e}")
    # Graceful degradation
    ComplianceGuardian = None
    RiskAdvisor = None
    GovernanceBrain = None
    LifecycleMonitor = None
    LearningCoach = None
    PerformanceAnalyst = None
    EmergencyResponse = None
    ImpactOracle = None
    PlanGenerator = None
    ScenarioCreator = None


# ==================== Models ====================

class AnalyzerRequest(BaseModel):
    data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    organization_id: Optional[str] = None


class AnalyzerResponse(BaseModel):
    analyzer: str
    analysis: Dict[str, Any]
    insights: List[str] = []
    recommendations: List[str] = []
    metadata: Dict[str, Any] = {}


# ==================== Analyzer Registry ====================

ANALYZERS = {}


def get_analyzer(analyzer_type: str):
    """Get or create analyzer instance"""
    if analyzer_type not in ANALYZERS:
        analyzer_class = {
            "compliance": ComplianceGuardian,
            "risk": RiskAdvisor,
            "governance": GovernanceBrain,
            "lifecycle": LifecycleMonitor,
            "learning": LearningCoach,
            "performance": PerformanceAnalyst,
            "emergency": EmergencyResponse,
            "impact": ImpactOracle,
            "plan": PlanGenerator,
            "scenario": ScenarioCreator,
        }.get(analyzer_type)

        if not analyzer_class:
            raise HTTPException(status_code=404, detail=f"Analyzer '{analyzer_type}' not found")

        if analyzer_class is None:
            raise HTTPException(
                status_code=503,
                detail=f"Analyzer '{analyzer_type}' not available (import failed)"
            )

        ANALYZERS[analyzer_type] = analyzer_class()

    return ANALYZERS[analyzer_type]


async def run_analyzer(
    analyzer_type: str,
    data: Dict[str, Any],
    context: Dict[str, Any],
    organization_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run analyzer on data

    Returns:
        Dict with analysis, insights, recommendations, metadata
    """
    analyzer = get_analyzer(analyzer_type)

    try:
        # Most analyzers have an `analyze()` method
        if hasattr(analyzer, 'analyze'):
            result = await analyzer.analyze(data, context or {})
        elif hasattr(analyzer, 'process'):
            result = await analyzer.process(data, context or {})
        else:
            # Fallback: try calling the instance
            result = await analyzer(data, context or {})

        return {
            "analysis": result,
            "insights": result.get("insights", []) if isinstance(result, dict) else [],
            "recommendations": result.get("recommendations", []) if isinstance(result, dict) else [],
            "metadata": {
                "analyzer": analyzer_type,
                "organization_id": organization_id or "default"
            }
        }
    except Exception as e:
        logger.error(f"Analyzer {analyzer_type} failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analyzer execution failed: {str(e)}"
        )


# ==================== Compliance Analyzer ====================

@router.post("/compliance/analyze", response_model=AnalyzerResponse)
async def analyze_compliance(request: AnalyzerRequest):
    """
    Analyze compliance with standards

    Example:
    ```json
    {
      "data": {
        "standard": "ISO22301",
        "current_practices": [...]
      },
      "context": {
        "organization_type": "corporate",
        "industry": "finance"
      }
    }
    ```
    """
    result = await run_analyzer(
        analyzer_type="compliance",
        data=request.data,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return AnalyzerResponse(
        analyzer="compliance",
        **result
    )


# ==================== Risk Analyzer ====================

@router.post("/risk/analyze", response_model=AnalyzerResponse)
async def analyze_risk(request: AnalyzerRequest):
    """
    Analyze risks

    Example:
    ```json
    {
      "data": {
        "threats": [...],
        "vulnerabilities": [...],
        "assets": [...]
      }
    }
    ```
    """
    result = await run_analyzer(
        analyzer_type="risk",
        data=request.data,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return AnalyzerResponse(
        analyzer="risk",
        **result
    )


# ==================== Governance Analyzer ====================

@router.post("/governance/analyze", response_model=AnalyzerResponse)
async def analyze_governance(request: AnalyzerRequest):
    """
    Analyze BCM governance structure

    Example:
    ```json
    {
      "data": {
        "structure": {...},
        "roles": [...],
        "responsibilities": [...]
      }
    }
    ```
    """
    result = await run_analyzer(
        analyzer_type="governance",
        data=request.data,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return AnalyzerResponse(
        analyzer="governance",
        **result
    )


# ==================== Lifecycle Analyzer ====================

@router.post("/lifecycle/analyze", response_model=AnalyzerResponse)
async def analyze_lifecycle(request: AnalyzerRequest):
    """
    Analyze BCM lifecycle status

    Example:
    ```json
    {
      "data": {
        "current_phase": "implementation",
        "maturity_level": "defined",
        "activities_completed": [...]
      }
    }
    ```
    """
    result = await run_analyzer(
        analyzer_type="lifecycle",
        data=request.data,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return AnalyzerResponse(
        analyzer="lifecycle",
        **result
    )


# ==================== Learning Analyzer ====================

@router.post("/learning/analyze", response_model=AnalyzerResponse)
async def analyze_learning(request: AnalyzerRequest):
    """
    Analyze learning and training needs

    Example:
    ```json
    {
      "data": {
        "current_training": [...],
        "competency_gaps": [...],
        "target_audience": [...]
      }
    }
    ```
    """
    result = await run_analyzer(
        analyzer_type="learning",
        data=request.data,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return AnalyzerResponse(
        analyzer="learning",
        **result
    )


# ==================== Performance Analyzer ====================

@router.post("/performance/analyze", response_model=AnalyzerResponse)
async def analyze_performance(request: AnalyzerRequest):
    """
    Analyze BCM performance

    Example:
    ```json
    {
      "data": {
        "kpis": [...],
        "metrics": {...},
        "benchmarks": [...]
      }
    }
    ```
    """
    result = await run_analyzer(
        analyzer_type="performance",
        data=request.data,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return AnalyzerResponse(
        analyzer="performance",
        **result
    )


# ==================== Emergency Analyzer ====================

@router.post("/emergency/analyze", response_model=AnalyzerResponse)
async def analyze_emergency(request: AnalyzerRequest):
    """
    Analyze emergency response capabilities

    Example:
    ```json
    {
      "data": {
        "incident_type": "natural_disaster",
        "response_capabilities": [...],
        "resources": [...]
      }
    }
    ```
    """
    result = await run_analyzer(
        analyzer_type="emergency",
        data=request.data,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return AnalyzerResponse(
        analyzer="emergency",
        **result
    )


# ==================== Impact Analyzer ====================

@router.post("/impact/analyze", response_model=AnalyzerResponse)
async def analyze_impact(request: AnalyzerRequest):
    """
    Analyze business impact

    Example:
    ```json
    {
      "data": {
        "process": "email_system",
        "downtime_scenarios": [...],
        "dependencies": [...]
      }
    }
    ```
    """
    result = await run_analyzer(
        analyzer_type="impact",
        data=request.data,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return AnalyzerResponse(
        analyzer="impact",
        **result
    )


# ==================== Plan Analyzer ====================

@router.post("/plan/analyze", response_model=AnalyzerResponse)
async def analyze_plan(request: AnalyzerRequest):
    """
    Analyze BCM plan

    Example:
    ```json
    {
      "data": {
        "plan_type": "IT_DR",
        "plan_content": {...},
        "coverage": [...]
      }
    }
    ```
    """
    result = await run_analyzer(
        analyzer_type="plan",
        data=request.data,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return AnalyzerResponse(
        analyzer="plan",
        **result
    )


# ==================== Scenario Analyzer ====================

@router.post("/scenario/analyze", response_model=AnalyzerResponse)
async def analyze_scenario(request: AnalyzerRequest):
    """
    Analyze BCM scenario

    Example:
    ```json
    {
      "data": {
        "scenario_type": "cyber_attack",
        "impact_areas": [...],
        "response_strategies": [...]
      }
    }
    ```
    """
    result = await run_analyzer(
        analyzer_type="scenario",
        data=request.data,
        context=request.context or {},
        organization_id=request.organization_id
    )

    return AnalyzerResponse(
        analyzer="scenario",
        **result
    )
