"""
Scenario Orchestrator - BCM Scenario Management Service
FastAPI application for scenario generation and analysis with AI integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import httpx
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BCM Scenario Orchestrator",
    description="Scenario generation and analysis for BCM Platform with AI integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# External service URLs (using existing services)
AI_ORCHESTRATOR_URL = os.getenv("AI_ORCHESTRATOR_URL", "http://ai_orchestrator:8000")
ODOO_URL = os.getenv("ODOO_URL", "http://odoo:8069")

class ScenarioGenerationRequest(BaseModel):
    category: str  # epidemic, blackout, cyber, supply, natural, terrorism
    complexity: int = 3  # 1-5 scale
    duration_hours: int = 4
    participants: int = 10
    affected_systems: List[str] = []
    custom_objectives: List[str] = []
    organization_context: Optional[str] = None

# AI-powered scenario generation endpoint
@app.post("/scenarios/generate")
async def generate_ai_scenario(request: ScenarioGenerationRequest):
    """Generate AI-powered BCM scenario using existing AI Orchestrator"""

    try:
        logger.info(f"Generating scenario: {request.category} - complexity {request.complexity}")

        # Build AI context for scenario generation
        ai_prompt = f"""
Generate a comprehensive BCM exercise scenario with the following parameters:

SCENARIO REQUIREMENTS:
- Category: {request.category}
- Complexity: {request.complexity}/5
- Duration: {request.duration_hours} hours
- Participants: {request.participants}
- Affected Systems: {', '.join(request.affected_systems)}
- Organization Context: {request.organization_context or 'Generic organization'}

DELIVERABLES REQUIRED:
1. Scenario title and background story
2. Hour-by-hour timeline with escalation points
3. Exercise injects (emails, calls, alerts)
4. Success metrics and evaluation criteria
5. JaamSim simulation parameters (if complexity >= 4)

Format as structured JSON for BCM Scenario Hub integration.
"""

        # Query existing AI Orchestrator
        async with httpx.AsyncClient() as client:
            ai_response = await client.post(
                f"{AI_ORCHESTRATOR_URL}/nlp/query",
                json={
                    "query": ai_prompt,
                    "context": {
                        "scenario_type": "bcm_exercise",
                        "complexity": request.complexity,
                        "category": request.category
                    },
                    "user_role": "scenario_generator"
                },
                timeout=60.0
            )

            if ai_response.status_code != 200:
                logger.error(f"AI Orchestrator error: {ai_response.status_code}")
                raise HTTPException(status_code=500, detail="AI generation failed")

            ai_result = ai_response.json()

        # Process AI response into scenario format
        scenario_data = {
            "title": f"{request.category.title()} BCM Exercise Scenario",
            "category": request.category,
            "level": "full" if request.complexity >= 4 else "tabletop",
            "meta_duration": request.duration_hours,
            "meta_participants": request.participants,
            "content_md": _format_ai_response_to_markdown(ai_result.get("response", ""), request),
            "is_ai_generated": True,
            "ai_generation_params": {
                "complexity": request.complexity,
                "ai_model": "existing_ai_orchestrator",
                "generated_at": datetime.now().isoformat()
            },
            "jaamsim_config": _generate_jaamsim_config(request) if request.complexity >= 4 else None
        }

        # For PHASE 1: Save locally, Odoo integration in next phase
        scenario_id = f"ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Save scenario locally for now
        import os
        scenarios_dir = "/app/generated_scenarios"
        os.makedirs(scenarios_dir, exist_ok=True)

        scenario_file = f"{scenarios_dir}/scenario_{scenario_id}.json"
        with open(scenario_file, 'w') as f:
            json.dump(scenario_data, f, indent=2)

        return {
            "status": "success",
            "scenario_id": scenario_id,
            "title": scenario_data["title"],
            "file_path": scenario_file,
            "ai_generated": True,
            "created_at": datetime.now().isoformat(),
            "note": "Scenario saved locally. Odoo integration in Phase 2."
        }

    except Exception as e:
        logger.error(f"Scenario generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _save_to_odoo_scenario_hub(scenario_data: Dict) -> Dict:
    """Save scenario to existing Odoo BCM Scenario Hub"""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ODOO_URL}/api/v1/bcm_scenario",
                json=scenario_data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Odoo save failed: {response.status_code} - {response.text}")
                # Return mock ID for development
                return {"id": f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}

    except Exception as e:
        logger.error(f"Odoo connection error: {e}")
        return {"id": f"local_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}

def _format_ai_response_to_markdown(ai_response: str, request: ScenarioGenerationRequest) -> str:
    """Format AI response into Markdown for Odoo BCM Scenario Hub"""

    return f"""# {request.category.title()} BCM Exercise Scenario

## Scenario Overview
{ai_response[:500]}

## Exercise Parameters
- **Complexity Level**: {request.complexity}/5
- **Duration**: {request.duration_hours} hours
- **Participants**: {request.participants}
- **Category**: {request.category}

## Affected Systems
{', '.join(request.affected_systems) if request.affected_systems else 'To be determined during exercise'}

## Custom Objectives
{chr(10).join(f'- {obj}' for obj in request.custom_objectives) if request.custom_objectives else '- Standard BCM exercise objectives'}

## AI Generation Details
- **Generated by**: BCM Scenario Orchestrator
- **AI Model**: Existing AI Orchestrator Service
- **Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*This scenario was automatically generated using AI and should be reviewed before execution.*
"""

def _generate_jaamsim_config(request: ScenarioGenerationRequest) -> str:
    """Generate JaamSim configuration for complex scenarios"""

    if request.complexity < 4:
        return None

    return f"""# AI-Generated JaamSim Configuration
# Scenario: {request.category.title()} Exercise
# Complexity: {request.complexity}/5

RecordEdits

# Scenario-specific distributions
Define DiscreteDistribution {{ ImpactDistribution }}
Define ExponentialDistribution {{ RecoveryDistribution }}

ImpactDistribution ValueList {{ 1 2 3 4 5 }}
ImpactDistribution ProbabilityList {{ 0.1 0.2 0.4 0.2 0.1 }}

RecoveryDistribution Mean {{ {request.duration_hours} h }}

# Simulation entities
Define EntityGenerator {{ IncidentSource }}
Define Queue {{ ResponseQueue }}
Define Server {{ ResponseTeam }}
Define EntitySink {{ ResolvedIncidents }}

# Configure for {request.participants} participants
ResponseTeam Capacity {{ {min(request.participants, 10)} }}

# Exercise duration
Define SimulationRun {{ {request.category.title()}Exercise }}
{request.category.title()}Exercise RunDuration {{ {request.duration_hours} h }}
"""

# Get available scenarios from existing Odoo
@app.get("/scenarios/available")
async def get_available_scenarios():
    """Get scenarios from existing Odoo BCM Scenario Hub"""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ODOO_URL}/api/v1/bcm_scenario")

            if response.status_code == 200:
                return response.json()
            else:
                return {"scenarios": [], "source": "odoo_error"}

    except Exception as e:
        logger.error(f"Error fetching scenarios: {e}")
        return {"scenarios": [], "source": "connection_error"}

# =====================================================
# EXPERIENCE ACCUMULATION & LEARNING SYSTEM (PHASE 5)
# =====================================================

class ExerciseResult(BaseModel):
    """Exercise completion result for learning"""
    exercise_id: str
    scenario_id: str
    template_id: str
    exercise_type: str
    duration_actual_hours: float
    participants_count: int
    success_metrics: Dict[str, Any]
    participant_feedback: List[Dict[str, Any]]
    simulation_metrics: Optional[Dict[str, Any]] = None
    lessons_learned: List[str] = []
    improvement_suggestions: List[str] = []
    effectiveness_score: float = 0.0  # 0-10 scale

class ScenarioLearning(BaseModel):
    """Learning data accumulated for scenario improvement"""
    scenario_id: str
    total_uses: int
    avg_effectiveness: float
    common_issues: List[str]
    success_patterns: List[str]
    improvement_recommendations: List[str]

# Experience accumulation storage
scenario_experience_db = {}  # In-memory для development, move to Redis/Supabase для production

@app.post("/learning/exercise-result")
async def collect_exercise_result(result: ExerciseResult):
    """Collect exercise results for learning accumulation"""
    try:
        logger.info(f"Collecting exercise result: {result.exercise_id}")

        # Store exercise result
        result_key = f"exercise_result_{result.exercise_id}"
        scenario_experience_db[result_key] = result.dict()

        # Update scenario learning data
        scenario_key = f"scenario_learning_{result.scenario_id}"

        if scenario_key not in scenario_experience_db:
            scenario_experience_db[scenario_key] = {
                'scenario_id': result.scenario_id,
                'total_uses': 0,
                'effectiveness_scores': [],
                'exercise_results': [],
                'patterns': {
                    'successful_elements': [],
                    'common_issues': [],
                    'improvement_areas': []
                }
            }

        # Accumulate learning data
        learning_data = scenario_experience_db[scenario_key]
        learning_data['total_uses'] += 1
        learning_data['effectiveness_scores'].append(result.effectiveness_score)
        learning_data['exercise_results'].append(result.exercise_id)

        # Extract patterns from feedback
        if result.participant_feedback:
            positive_feedback = [f for f in result.participant_feedback if f.get('rating', 0) >= 7]
            negative_feedback = [f for f in result.participant_feedback if f.get('rating', 0) <= 4]

            for feedback in positive_feedback:
                if feedback.get('comment'):
                    learning_data['patterns']['successful_elements'].append(feedback['comment'])

            for feedback in negative_feedback:
                if feedback.get('comment'):
                    learning_data['patterns']['common_issues'].append(feedback['comment'])

        # Add lessons learned
        learning_data['patterns']['improvement_areas'].extend(result.lessons_learned)

        # Calculate updated metrics
        avg_effectiveness = sum(learning_data['effectiveness_scores']) / len(learning_data['effectiveness_scores'])
        learning_data['avg_effectiveness'] = round(avg_effectiveness, 2)

        # Generate AI-powered improvement recommendations
        if learning_data['total_uses'] >= 3:  # Enough data для analysis
            recommendations = await _generate_scenario_improvements(learning_data)
            learning_data['ai_recommendations'] = recommendations

        # Notify AI Orchestrator of new learning data
        await _notify_ai_orchestrator_learning(result, learning_data)

        return {
            "status": "success",
            "exercise_id": result.exercise_id,
            "scenario_learning_updated": True,
            "total_scenario_uses": learning_data['total_uses'],
            "avg_effectiveness": learning_data['avg_effectiveness']
        }

    except Exception as e:
        logger.error(f"Error collecting exercise result: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning/scenario/{scenario_id}/insights")
async def get_scenario_learning_insights(scenario_id: str):
    """Get accumulated learning insights for scenario"""
    try:
        scenario_key = f"scenario_learning_{scenario_id}"

        if scenario_key not in scenario_experience_db:
            return {
                "status": "success",
                "scenario_id": scenario_id,
                "insights": {
                    "total_uses": 0,
                    "avg_effectiveness": 0,
                    "recommendations": ["Not enough data - need at least 3 exercise completions"]
                }
            }

        learning_data = scenario_experience_db[scenario_key]

        # Generate insights summary
        insights = {
            "total_uses": learning_data['total_uses'],
            "avg_effectiveness": learning_data.get('avg_effectiveness', 0),
            "effectiveness_trend": learning_data['effectiveness_scores'][-5:],  # Last 5 scores
            "successful_elements": list(set(learning_data['patterns']['successful_elements'][-10:])),
            "common_issues": list(set(learning_data['patterns']['common_issues'][-10:])),
            "ai_recommendations": learning_data.get('ai_recommendations', []),
            "improvement_areas": list(set(learning_data['patterns']['improvement_areas'][-10:]))
        }

        return {
            "status": "success",
            "scenario_id": scenario_id,
            "insights": insights
        }

    except Exception as e:
        logger.error(f"Error getting scenario insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _generate_scenario_improvements(learning_data: Dict) -> List[str]:
    """Generate AI-powered scenario improvement recommendations"""
    try:
        # Build learning context для AI
        learning_prompt = f"""
Analyze the following BCM scenario learning data and provide improvement recommendations:

SCENARIO USAGE DATA:
- Total uses: {learning_data['total_uses']}
- Average effectiveness: {learning_data['avg_effectiveness']}/10
- Effectiveness trend: {learning_data['effectiveness_scores'][-5:]}

SUCCESSFUL ELEMENTS:
{chr(10).join(f'- {elem}' for elem in learning_data['patterns']['successful_elements'][-5:])}

COMMON ISSUES:
{chr(10).join(f'- {issue}' for issue in learning_data['patterns']['common_issues'][-5:])}

IMPROVEMENT AREAS:
{chr(10).join(f'- {area}' for area in learning_data['patterns']['improvement_areas'][-5:])}

Provide 3-5 specific, actionable recommendations для improving this scenario's effectiveness.
"""

        # Query AI Orchestrator для improvement suggestions
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_ORCHESTRATOR_URL}/nlp/query",
                json={
                    "query": learning_prompt,
                    "context": {
                        "type": "scenario_improvement",
                        "scenario_id": learning_data['scenario_id'],
                        "learning_data": learning_data
                    },
                    "user_role": "scenario_optimizer"
                },
                timeout=60.0
            )

            if response.status_code == 200:
                ai_result = response.json()
                ai_response = ai_result.get("response", "")

                # Extract recommendations from AI response
                recommendations = []
                lines = ai_response.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith(('-', '•', '1.', '2.', '3.', '4.', '5.')):
                        # Clean up line и add to recommendations
                        clean_line = line.lstrip('-•123456789. ').strip()
                        if clean_line:
                            recommendations.append(clean_line)

                return recommendations[:5]  # Top 5 recommendations

    except Exception as e:
        logger.error(f"Error generating scenario improvements: {e}")

    # Fallback recommendations
    return [
        "Increase scenario complexity gradually based on participant feedback",
        "Add more realistic time constraints based on actual exercise duration",
        "Enhance participant briefing based on common confusion points",
        "Consider additional stakeholder roles based on lessons learned"
    ]

async def _notify_ai_orchestrator_learning(exercise_result: ExerciseResult, learning_data: Dict):
    """Notify AI Orchestrator of new learning data"""
    try:
        learning_notification = {
            "type": "exercise_learning",
            "exercise_result": exercise_result.dict(),
            "accumulated_learning": {
                "scenario_id": learning_data['scenario_id'],
                "total_uses": learning_data['total_uses'],
                "avg_effectiveness": learning_data.get('avg_effectiveness', 0),
                "patterns": learning_data['patterns']
            }
        }

        async with httpx.AsyncClient() as client:
            await client.post(
                f"{AI_ORCHESTRATOR_URL}/learning/update",
                json=learning_notification,
                timeout=10.0
            )

            logger.info(f"Notified AI Orchestrator of learning data for scenario {learning_data['scenario_id']}")

    except Exception as e:
        logger.error(f"Failed to notify AI Orchestrator: {e}")

@app.get("/learning/dashboard")
async def get_learning_dashboard():
    """Get learning dashboard data"""
    try:
        # Aggregate all scenario learning data
        all_scenarios = []
        total_exercises = 0
        avg_platform_effectiveness = 0

        for key, data in scenario_experience_db.items():
            if key.startswith('scenario_learning_'):
                all_scenarios.append(data)
                total_exercises += data['total_uses']

        if all_scenarios:
            effectiveness_scores = [s.get('avg_effectiveness', 0) for s in all_scenarios]
            avg_platform_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores)

        # Get recent exercise results
        recent_results = []
        for key, data in scenario_experience_db.items():
            if key.startswith('exercise_result_'):
                recent_results.append(data)

        recent_results.sort(key=lambda x: x.get('completed_at', ''), reverse=True)

        return {
            "status": "success",
            "dashboard": {
                "total_scenarios_with_data": len(all_scenarios),
                "total_exercises_completed": total_exercises,
                "avg_platform_effectiveness": round(avg_platform_effectiveness, 2),
                "recent_exercise_results": recent_results[:10],
                "top_performing_scenarios": sorted(all_scenarios, key=lambda x: x.get('avg_effectiveness', 0), reverse=True)[:5],
                "scenarios_needing_improvement": [s for s in all_scenarios if s.get('avg_effectiveness', 0) < 6.0]
            }
        }

    except Exception as e:
        logger.error(f"Error generating learning dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Import routers
try:
    from app.api.v1.endpoints.scenarios import router as scenarios_router
    app.include_router(scenarios_router, prefix="/api/v1")
except ImportError as e:
    logger.warning(f"Could not import scenarios router: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for scenario orchestrator"""
    return {
        "status": "healthy",
        "service": "scenario_orchestrator",
        "version": "1.0.0",
        "capabilities": ["scenario_generation", "scenario_analysis", "scenario_optimization"],
        "timestamp": datetime.now().isoformat()
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "BCM Scenario Orchestrator",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "scenarios": "/api/v1/scenarios"
        }
    }

# Basic scenario endpoints (fallback if module import fails)
@app.get("/api/v1/scenarios/status")
async def scenarios_status():
    """Get scenario service status"""
    return {
        "status": "active",
        "service": "scenario_orchestrator",
        "scenarios_available": True,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085)