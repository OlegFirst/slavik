"""
Scenario Intelligence API

REST API for executing and managing scenarios
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from prometheus_client import make_asgi_app
import uvicorn
import os

from scenario_engine import ScenarioEngine
from rag_integration import ScenarioRAGIntegration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Scenario Intelligence API",
    description="Execute and manage system and user scenarios",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Request/Response models
class ScenarioExecutionRequest(BaseModel):
    scenario_id: str
    context: Optional[Dict[str, Any]] = {}

class ScenarioSearchRequest(BaseModel):
    query: str
    scenario_type: Optional[str] = None
    category: Optional[str] = None
    limit: int = 5

class ScenarioGenerateRequest(BaseModel):
    description: str
    type: str = "user_workflow"
    category: Optional[str] = None
    requirements: List[str] = []

class ScenarioStoreRequest(BaseModel):
    scenario: Dict[str, Any]


# Endpoints

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "scenario-intelligence",
        "version": "1.0.0"
    }


@app.post("/scenarios/execute")
async def execute_scenario(request: ScenarioExecutionRequest):
    """Execute a scenario by ID"""

    try:
        engine = ScenarioEngine()
        rag = ScenarioRAGIntegration()

        # Get scenario from RAG
        scenario = await rag.get_scenario_by_id(request.scenario_id)

        if not scenario:
            # Try searching by ID
            scenarios = await rag.find_similar_scenarios(
                query=f"scenario {request.scenario_id}",
                scenario_type=None,
                limit=1
            )

            if not scenarios:
                raise HTTPException(status_code=404, detail=f"Scenario {request.scenario_id} not found")

            scenario = scenarios[0]

        # Execute
        result = await engine.execute_scenario(scenario, request.context)

        await engine.close()

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenarios/execute-file")
async def execute_scenario_file(file_path: str, context: Dict[str, Any] = {}):
    """Execute a scenario from a YAML file"""

    try:
        engine = ScenarioEngine()

        # Load scenario
        scenario = await engine.load_scenario(file_path)

        # Execute
        result = await engine.execute_scenario(scenario, context)

        await engine.close()

        return result

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Scenario file not found: {file_path}")
    except Exception as e:
        logger.error(f"Failed to execute scenario from file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenarios/search")
async def search_scenarios(request: ScenarioSearchRequest):
    """Search for scenarios using RAG"""

    try:
        rag = ScenarioRAGIntegration()

        scenarios = await rag.find_similar_scenarios(
            query=request.query,
            scenario_type=request.scenario_type,
            category=request.category,
            limit=request.limit
        )

        return {
            "query": request.query,
            "count": len(scenarios),
            "scenarios": scenarios
        }

    except Exception as e:
        logger.error(f"Failed to search scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    """Get scenario by ID"""

    try:
        rag = ScenarioRAGIntegration()

        scenario = await rag.get_scenario_by_id(scenario_id)

        if not scenario:
            raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")

        return {
            "scenario_id": scenario_id,
            "scenario": scenario
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenarios")
async def list_scenarios(
    scenario_type: Optional[str] = None,
    category: Optional[str] = None
):
    """List all scenarios"""

    try:
        rag = ScenarioRAGIntegration()

        scenarios = await rag.list_all_scenarios(
            scenario_type=scenario_type,
            category=category
        )

        return {
            "count": len(scenarios),
            "scenarios": scenarios
        }

    except Exception as e:
        logger.error(f"Failed to list scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenarios/store")
async def store_scenario(request: ScenarioStoreRequest):
    """Store a scenario in RAG"""

    try:
        rag = ScenarioRAGIntegration()

        success = await rag.store_scenario(request.scenario)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to store scenario")

        scenario_id = request.scenario.get('id') or request.scenario.get('scenario', {}).get('id')

        return {
            "status": "stored",
            "scenario_id": scenario_id
        }

    except Exception as e:
        logger.error(f"Failed to store scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenarios/generate")
async def generate_scenario(request: ScenarioGenerateRequest):
    """Generate new scenario using AI"""

    try:
        from intelligent_core.ai_foundation.llm.llm_router import LLMRouter

        llm = LLMRouter()

        system_prompt = """You are a scenario generation expert for BCM (Business Continuity Management) platforms.
Generate complete scenarios in YAML format based on user requirements.

The scenario should follow this structure:
scenario:
  id: "unique-scenario-id"
  type: "system_test" or "user_workflow"
  category: "specific category"
  level: 1-4
  description: "what this scenario does"
  business_value: "why this matters"
  steps: [list of steps]
  assertions: [validations]
  metrics: [prometheus metrics]
"""

        user_prompt = f"""
Generate a {request.type} scenario for: {request.description}

Category: {request.category or 'general'}
Requirements: {', '.join(request.requirements) if request.requirements else 'none'}

Output only valid YAML following the scenario structure.
"""

        scenario_yaml = await llm.query(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            task_type="content_generation",
            temperature=0.7
        )

        return {
            "status": "generated",
            "scenario_yaml": scenario_yaml
        }

    except Exception as e:
        logger.error(f"Failed to generate scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/scenarios/{scenario_id}")
async def delete_scenario(scenario_id: str):
    """Delete a scenario"""

    try:
        rag = ScenarioRAGIntegration()

        success = await rag.delete_scenario(scenario_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete scenario")

        return {
            "status": "deleted",
            "scenario_id": scenario_id
        }

    except Exception as e:
        logger.error(f"Failed to delete scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenarios/load-from-directory")
async def load_scenarios_from_directory(directory: str):
    """Load all scenarios from a directory into RAG"""

    try:
        import glob
        import yaml

        rag = ScenarioRAGIntegration()

        # Find all YAML files
        scenario_files = glob.glob(f"{directory}/**/*.yaml", recursive=True)

        loaded = []
        failed = []

        for file_path in scenario_files:
            try:
                with open(file_path, 'r') as f:
                    scenario = yaml.safe_load(f)

                success = await rag.store_scenario(scenario)

                if success:
                    scenario_id = scenario.get('scenario', {}).get('id') or scenario.get('id')
                    loaded.append(scenario_id)
                else:
                    failed.append(file_path)

            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                failed.append(file_path)

        return {
            "status": "completed",
            "loaded": len(loaded),
            "failed": len(failed),
            "loaded_scenarios": loaded,
            "failed_files": failed
        }

    except Exception as e:
        logger.error(f"Failed to load scenarios from directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    PORT = int(os.getenv("SCENARIO_INTELLIGENCE_PORT", "8090"))
    HOST = os.getenv("SCENARIO_INTELLIGENCE_HOST", "0.0.0.0")

    logger.info(f"🎬 Starting Scenario Intelligence API on {HOST}:{PORT}")

    uvicorn.run(
        "api:app",
        host=HOST,
        port=PORT,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )
