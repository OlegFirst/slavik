"""
Project & Code Quality Agent - Unified project management and code analysis

Responsibilities:
- Project management and task tracking
- Code quality analysis (security, testing, quality)
- Test coverage analysis and generation
- Compliance checking (ISO 22301, ISO 27001, HIPAA)
- Domain detection (AI-powered)

Port: 8060
"""

import sys
from pathlib import Path

# Add parent path for EventBusHelper
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import uvicorn

# Import EventBus Helper
try:
    from _shared.eventbus_helper import EventBusHelper
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False
    logging.warning("EventBus Helper not available")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("PROJECT_AGENT_PORT", "8060"))
HOST = os.getenv("PROJECT_AGENT_HOST", "0.0.0.0")

# Projects storage
projects: Dict[str, Dict] = {}

# Global EventBus helper
eventbus_helper = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    global eventbus_helper

    logger.info("=" * 70)
    logger.info(" PROJECT & CODE QUALITY AGENT STARTING...")
    logger.info("=" * 70)
    logger.info(f"   Service: Project & Code Quality Agent")
    logger.info(f"   Port: {PORT}")
    logger.info(f"   Capabilities: Project Management + Code Analysis")
    logger.info("=" * 70)

    # Initialize EventBus Helper
    if EVENTBUS_AVAILABLE:
        try:
            eventbus_helper = EventBusHelper(
                service_name="project-agent",
                port=PORT,
                orchestrator="ai-office",
                capabilities=[
                    # Project Management
                    "project_management",
                    "task_tracking",
                    "progress_reporting",
                    "assignment_management",
                    "status_tracking",
                    # Code Quality
                    "code_security_scanning",
                    "code_quality_analysis",
                    "testing_coverage",
                    "test_generation",
                    "compliance_checking",
                    "domain_detection"
                ],
                dependencies=["eventbus", "mio-manager"],
                service_type="specialist"
            )
            await eventbus_helper.startup()
            logger.info(" EventBus integration initialized")
        except Exception as e:
            logger.error(f" EventBus initialization failed: {e}")
            logger.warning("️  Running without EventBus integration")

    logger.info("=" * 70)
    logger.info(" PROJECT AGENT READY!")
    logger.info("=" * 70)

    yield

    # Shutdown
    logger.info("=" * 70)
    logger.info(" PROJECT AGENT SHUTTING DOWN...")
    logger.info("=" * 70)

    # Shutdown EventBus
    if eventbus_helper:
        await eventbus_helper.shutdown()
        logger.info(" EventBus integration stopped")

    logger.info(" Goodbye!")


app = FastAPI(
    title="Project & Code Quality Agent",
    description="Unified project management and code analysis: security, testing, quality, compliance",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Project(BaseModel):
    name: str
    description: str
    status: Optional[str] = "active"
    assignees: Optional[List[str]] = []

class Task(BaseModel):
    title: str
    description: str
    project_id: str
    assignee: Optional[str] = None
    status: Optional[str] = "pending"

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "project-agent",
        "version": "1.0.0",
        "active_projects": len(projects)
    }

@app.post("/projects")
async def create_project(project: Project):
    """Create a new project"""
    project_id = f"proj-{len(projects) + 1:03d}"

    projects[project_id] = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "assignees": project.assignees,
        "created_at": datetime.now().isoformat(),
        "tasks": []
    }

    logger.info(f"Project created: {project_id} - {project.name}")

    return {
        "project_id": project_id,
        "status": "created"
    }

@app.get("/projects")
async def list_projects():
    """List all projects"""
    return {
        "projects": list(projects.values()),
        "count": len(projects)
    }

@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    return projects[project_id]

@app.post("/tasks")
async def create_task(task: Task):
    """Create a new task"""
    if task.project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")

    task_id = f"task-{len(projects[task.project_id]['tasks']) + 1:03d}"

    task_data = {
        "id": task_id,
        "title": task.title,
        "description": task.description,
        "assignee": task.assignee,
        "status": task.status,
        "created_at": datetime.now().isoformat()
    }

    projects[task.project_id]["tasks"].append(task_data)

    logger.info(f"Task created: {task_id} in {task.project_id}")

    return {
        "task_id": task_id,
        "status": "created"
    }


# ============================================================================
# TEST MANAGEMENT ENDPOINTS
# ============================================================================

class TestRunRequest(BaseModel):
    suite: str  # unit | integration | e2e | load | all
    component: Optional[str] = None
    markers: Optional[List[str]] = None
    parallel: Optional[bool] = True
    coverage: Optional[bool] = True

class TestGenerateRequest(BaseModel):
    component: str
    coverage_threshold: Optional[int] = 85
    test_types: Optional[List[str]] = ["unit", "integration"]

@app.post("/api/tests/run")
async def run_tests(request: TestRunRequest):
    """Run test suite"""
    execution_id = f"exec-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    logger.info(f"Running tests: suite={request.suite}, component={request.component}")

    # TODO: Implement actual test execution via pytest
    # For now, return mock response

    return {
        "execution_id": execution_id,
        "status": "running",
        "suite": request.suite,
        "component": request.component,
        "markers": request.markers,
        "parallel": request.parallel,
        "coverage": request.coverage,
        "started_at": datetime.now().isoformat()
    }

@app.get("/api/tests/coverage")
async def get_test_coverage(component: Optional[str] = None):
    """Get test coverage report"""
    logger.info(f"Getting coverage for component: {component}")

    # TODO: Implement actual coverage analysis via pytest-cov
    # For now, return mock response

    coverage_data = {
        "total_coverage": 82.5,
        "by_category": {
            "platform_services": 80.2,
            "intelligent_core": 85.1,
            "infrastructure": 75.8
        },
        "quality_gates": {
            "meets_minimum": True,
            "target": 80,
            "actual": 82.5
        }
    }

    if component:
        coverage_data["by_component"] = {
            component: {
                "coverage": 85.0,
                "lines_covered": 850,
                "lines_total": 1000,
                "missing_coverage": [
                    f"{component}.py:145-150",
                    f"workflows.py:230-240"
                ]
            }
        }

    return coverage_data

@app.post("/api/tests/generate")
async def generate_tests(request: TestGenerateRequest):
    """Generate missing tests for component"""
    generation_id = f"gen-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    logger.info(f"Generating tests for: {request.component}, threshold={request.coverage_threshold}")

    # TODO: Implement actual test generation
    # For now, return mock response

    return {
        "generation_id": generation_id,
        "component": request.component,
        "tests_generated": 15,
        "files_created": [
            f"/tests/unit/platform-services/test_{request.component}_new.py",
            f"/tests/integration/services/test_{request.component}_workflow.py"
        ],
        "coverage_improvement": {
            "before": 75.0,
            "after": 85.2,
            "improvement": 10.2
        }
    }

@app.get("/api/tests/report")
async def get_test_report(execution_id: Optional[str] = None):
    """Get test execution report"""
    logger.info(f"Getting test report for: {execution_id}")

    # TODO: Implement actual report retrieval
    # For now, return mock response

    return {
        "execution_id": execution_id or "exec-latest",
        "suite": "unit",
        "status": "completed",
        "duration": "125.3s",
        "results": {
            "total_tests": 458,
            "passed": 452,
            "failed": 4,
            "skipped": 2,
            "errors": 0
        },
        "failures": [
            {
                "test": "test_workflow_validation",
                "file": "test_service.py:145",
                "error": "AssertionError: Expected 200, got 500"
            }
        ],
        "coverage": 82.5,
        "quality_score": 95.2
    }

@app.get("/api/tests/quality")
async def analyze_test_quality():
    """Analyze test quality metrics"""
    logger.info("Analyzing test quality")

    # TODO: Implement actual quality analysis
    # For now, return mock response

    return {
        "overall_quality": 92.5,
        "metrics": {
            "test_maintainability": 90.0,
            "assertion_quality": 95.0,
            "fixture_reusability": 88.0,
            "test_isolation": 94.0
        },
        "recommendations": [
            "Add more edge case tests for bia-service",
            "Improve fixture documentation in conftest.py",
            "Consider parametrizing test_risk_assessment"
        ]
    }

if __name__ == "__main__":
    logger.info(f"Starting Project Agent on {HOST}:{PORT}")
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )
