#!/usr/bin/env python3
"""
MSP (Managed Service Provider) Server
Централизованное управление Universal Orchestration Platform

Возможности:
- Управление пользователями и проектами
- Мониторинг и аналитика
- Централизованное логирование
- Управление ресурсами
- API для интеграции с корпоративными системами
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import uuid

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import httpx
from anthropic_service import anthropic_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('msp_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create MSP FastAPI app
app = FastAPI(
    title="MSP Server - Universal Orchestration Platform",
    description="Managed Service Provider для централизованного управления",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# In-memory storage (в продакшене использовать базу данных)
users_db = {}
projects_db = {}
tasks_db = {}
analytics_db = {}
orchestrator_instances = {}

# Models
class User(BaseModel):
    user_id: str
    username: str
    email: str
    role: str  # "admin", "user", "viewer"
    created_at: datetime
    last_login: Optional[datetime] = None
    projects: List[str] = []
    api_key: str

class Project(BaseModel):
    project_id: str
    name: str
    description: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    status: str  # "active", "archived", "deleted"
    settings: Dict[str, Any] = {}
    collaborators: List[str] = []

class TaskRequest(BaseModel):
    user_id: str
    project_id: str
    task_type: str  # "analyze", "generate", "visualize", "full"
    input_data: Dict[str, Any]
    settings: Dict[str, Any] = {}

class AnalyticsQuery(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    task_type: Optional[str] = None

class OrchestratorInstance(BaseModel):
    instance_id: str
    url: str
    status: str  # "active", "inactive", "maintenance"
    load: int  # 0-100
    last_heartbeat: datetime
    version: str
    capabilities: List[str] = []

# Utility functions
def generate_api_key() -> str:
    """Generate unique API key"""
    return f"uop_{uuid.uuid4().hex[:16]}"

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify API key and return user_id"""
    api_key = credentials.credentials

    for user_id, user in users_db.items():
        if user.api_key == api_key:
            # Update last login
            users_db[user_id].last_login = datetime.now()
            return user_id

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key"
    )

def log_analytics_event(event_type: str, user_id: str, data: Dict[str, Any]):
    """Log analytics event"""
    event_id = str(uuid.uuid4())
    analytics_db[event_id] = {
        "event_id": event_id,
        "event_type": event_type,
        "user_id": user_id,
        "timestamp": datetime.now(),
        "data": data
    }

async def get_best_orchestrator_instance() -> str:
    """Get best available orchestrator instance based on load"""
    active_instances = [
        inst for inst in orchestrator_instances.values()
        if inst.status == "active" and
        (datetime.now() - inst.last_heartbeat).seconds < 60
    ]

    if not active_instances:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No orchestrator instances available"
        )

    # Select instance with lowest load
    best_instance = min(active_instances, key=lambda x: x.load)
    return best_instance.url

# Routes

@app.get("/", response_class=HTMLResponse)
async def msp_dashboard():
    """MSP Dashboard Interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MSP Dashboard - Universal Orchestration Platform</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0; padding: 20px; background: #f5f7fa; color: #2c3e50;
            }
            .header {
                background: #3498db; color: white; padding: 20px;
                border-radius: 8px; margin-bottom: 20px;
            }
            .stats-grid {
                display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px; margin-bottom: 30px;
            }
            .stat-card {
                background: white; padding: 20px; border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .stat-number { font-size: 2rem; font-weight: bold; color: #3498db; }
            .stat-label { color: #7f8c8d; margin-top: 5px; }
            .section {
                background: white; padding: 20px; border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px;
            }
            .btn {
                background: #3498db; color: white; padding: 10px 20px;
                border: none; border-radius: 5px; cursor: pointer;
                text-decoration: none; display: inline-block;
            }
            .btn:hover { background: #2980b9; }
            .status-active { color: #27ae60; font-weight: bold; }
            .status-inactive { color: #e74c3c; font-weight: bold; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ecf0f1; }
            th { background: #ecf0f1; font-weight: 600; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏢 MSP Dashboard</h1>
            <p>Централизованное управление Universal Orchestration Platform</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="totalUsers">0</div>
                <div class="stat-label">Активных пользователей</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalProjects">0</div>
                <div class="stat-label">Проектов</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalTasks">0</div>
                <div class="stat-label">Задач выполнено</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="activeInstances">0</div>
                <div class="stat-label">Активных инстансов</div>
            </div>
        </div>

        <div class="section">
            <h2>🖥️ Orchestrator Instances</h2>
            <table>
                <thead>
                    <tr>
                        <th>Instance ID</th>
                        <th>URL</th>
                        <th>Status</th>
                        <th>Load</th>
                        <th>Version</th>
                        <th>Last Heartbeat</th>
                    </tr>
                </thead>
                <tbody id="instancesList">
                    <tr>
                        <td colspan="6">Загрузка...</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>👥 Recent Users</h2>
            <table>
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Last Login</th>
                        <th>Projects</th>
                    </tr>
                </thead>
                <tbody id="usersList">
                    <tr>
                        <td colspan="5">Загрузка...</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>📊 Recent Tasks</h2>
            <table>
                <thead>
                    <tr>
                        <th>Task ID</th>
                        <th>Type</th>
                        <th>User</th>
                        <th>Project</th>
                        <th>Status</th>
                        <th>Started</th>
                    </tr>
                </thead>
                <tbody id="tasksList">
                    <tr>
                        <td colspan="6">Загрузка...</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <script>
            async function loadDashboard() {
                try {
                    // Load stats
                    const statsResponse = await fetch('/api/stats');
                    const stats = await statsResponse.json();

                    document.getElementById('totalUsers').textContent = stats.total_users;
                    document.getElementById('totalProjects').textContent = stats.total_projects;
                    document.getElementById('totalTasks').textContent = stats.total_tasks;
                    document.getElementById('activeInstances').textContent = stats.active_instances;

                    // Load instances
                    const instancesResponse = await fetch('/api/instances');
                    const instances = await instancesResponse.json();

                    const instancesList = document.getElementById('instancesList');
                    instancesList.innerHTML = instances.map(inst => `
                        <tr>
                            <td>${inst.instance_id}</td>
                            <td>${inst.url}</td>
                            <td class="status-${inst.status}">${inst.status}</td>
                            <td>${inst.load}%</td>
                            <td>${inst.version}</td>
                            <td>${new Date(inst.last_heartbeat).toLocaleString()}</td>
                        </tr>
                    `).join('');

                    // Load users
                    const usersResponse = await fetch('/api/users');
                    const users = await usersResponse.json();

                    const usersList = document.getElementById('usersList');
                    usersList.innerHTML = users.slice(0, 10).map(user => `
                        <tr>
                            <td>${user.username}</td>
                            <td>${user.email}</td>
                            <td>${user.role}</td>
                            <td>${user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}</td>
                            <td>${user.projects.length}</td>
                        </tr>
                    `).join('');

                    // Load recent tasks
                    const tasksResponse = await fetch('/api/tasks/recent');
                    const tasks = await tasksResponse.json();

                    const tasksList = document.getElementById('tasksList');
                    tasksList.innerHTML = tasks.slice(0, 10).map(task => `
                        <tr>
                            <td>${task.task_id}</td>
                            <td>${task.task_type}</td>
                            <td>${task.user_id}</td>
                            <td>${task.project_id}</td>
                            <td>${task.status}</td>
                            <td>${new Date(task.created_at).toLocaleString()}</td>
                        </tr>
                    `).join('');

                } catch (error) {
                    console.error('Failed to load dashboard:', error);
                }
            }

            // Load dashboard on page load
            loadDashboard();

            // Refresh every 30 seconds
            setInterval(loadDashboard, 30000);
        </script>
    </body>
    </html>
    """

@app.post("/api/users/register")
async def register_user(username: str, email: str, role: str = "user"):
    """Register new user"""
    user_id = str(uuid.uuid4())
    api_key = generate_api_key()

    user = User(
        user_id=user_id,
        username=username,
        email=email,
        role=role,
        created_at=datetime.now(),
        api_key=api_key
    )

    users_db[user_id] = user

    log_analytics_event("user_registered", user_id, {
        "username": username,
        "email": email,
        "role": role
    })

    logger.info(f"User registered: {username} ({user_id})")

    return {"user_id": user_id, "api_key": api_key, "message": "User registered successfully"}

@app.post("/api/projects/create")
async def create_project(
    name: str,
    description: str,
    user_id: str = Depends(verify_api_key)
):
    """Create new project"""
    project_id = str(uuid.uuid4())

    project = Project(
        project_id=project_id,
        name=name,
        description=description,
        owner_id=user_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        status="active"
    )

    projects_db[project_id] = project
    users_db[user_id].projects.append(project_id)

    log_analytics_event("project_created", user_id, {
        "project_id": project_id,
        "name": name
    })

    logger.info(f"Project created: {name} ({project_id}) by {user_id}")

    return {"project_id": project_id, "message": "Project created successfully"}

@app.post("/api/tasks/submit")
async def submit_task(
    task_request: TaskRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(verify_api_key)
):
    """Submit task to orchestrator"""

    # Verify user has access to project
    if task_request.project_id not in users_db[user_id].projects:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to project"
        )

    task_id = str(uuid.uuid4())

    # Get best orchestrator instance
    orchestrator_url = await get_best_orchestrator_instance()

    # Create task record
    task_record = {
        "task_id": task_id,
        "user_id": user_id,
        "project_id": task_request.project_id,
        "task_type": task_request.task_type,
        "status": "submitted",
        "created_at": datetime.now(),
        "orchestrator_url": orchestrator_url,
        "input_data": task_request.input_data,
        "settings": task_request.settings
    }

    tasks_db[task_id] = task_record

    # Submit to orchestrator in background
    background_tasks.add_task(
        forward_task_to_orchestrator,
        task_id,
        orchestrator_url,
        task_request
    )

    log_analytics_event("task_submitted", user_id, {
        "task_id": task_id,
        "task_type": task_request.task_type,
        "project_id": task_request.project_id
    })

    logger.info(f"Task submitted: {task_id} ({task_request.task_type}) by {user_id}")

    return {"task_id": task_id, "status": "submitted", "message": "Task submitted successfully"}

async def forward_task_to_orchestrator(
    task_id: str,
    orchestrator_url: str,
    task_request: TaskRequest
):
    """Forward task to orchestrator instance"""
    try:
        async with httpx.AsyncClient() as client:
            # Determine endpoint based on task type
            endpoint_map = {
                "analyze": "/analyze-project",
                "directory": "/analyze-directory",
                "github": "/analyze-github"
            }

            endpoint = endpoint_map.get(task_request.task_type, "/analyze-project")

            response = await client.post(
                f"{orchestrator_url}{endpoint}",
                json=task_request.input_data,
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                tasks_db[task_id]["status"] = "processing"
                tasks_db[task_id]["orchestrator_task_id"] = result.get("task_id")
                logger.info(f"Task {task_id} forwarded to orchestrator")
            else:
                tasks_db[task_id]["status"] = "failed"
                tasks_db[task_id]["error"] = f"Orchestrator returned {response.status_code}"
                logger.error(f"Task {task_id} failed to forward: {response.status_code}")

    except Exception as e:
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)
        logger.error(f"Task {task_id} forwarding failed: {e}")

@app.get("/api/tasks/{task_id}/status")
async def get_task_status(task_id: str, user_id: str = Depends(verify_api_key)):
    """Get task status"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks_db[task_id]

    # Verify user has access
    if task["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to task"
        )

    # If task is processing, check orchestrator status
    if task["status"] == "processing" and "orchestrator_task_id" in task:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{task['orchestrator_url']}/status/{task['orchestrator_task_id']}"
                )
                if response.status_code == 200:
                    orchestrator_status = response.json()
                    task["progress"] = orchestrator_status.get("progress", 0)
                    task["message"] = orchestrator_status.get("message", "Processing...")

                    if orchestrator_status["status"] == "completed":
                        task["status"] = "completed"
                        task["result"] = orchestrator_status["result"]
                    elif orchestrator_status["status"] == "failed":
                        task["status"] = "failed"
                        task["error"] = orchestrator_status.get("error", "Unknown error")
        except Exception as e:
            logger.error(f"Failed to check orchestrator status for task {task_id}: {e}")

    return task

@app.post("/api/instances/register")
async def register_orchestrator_instance(
    instance_id: str,
    url: str,
    version: str,
    capabilities: List[str] = []
):
    """Register orchestrator instance"""
    instance = OrchestratorInstance(
        instance_id=instance_id,
        url=url,
        status="active",
        load=0,
        last_heartbeat=datetime.now(),
        version=version,
        capabilities=capabilities
    )

    orchestrator_instances[instance_id] = instance

    logger.info(f"Orchestrator instance registered: {instance_id} at {url}")

    return {"message": "Instance registered successfully"}

@app.post("/api/instances/{instance_id}/heartbeat")
async def heartbeat(instance_id: str, load: int):
    """Heartbeat from orchestrator instance"""
    if instance_id in orchestrator_instances:
        orchestrator_instances[instance_id].load = load
        orchestrator_instances[instance_id].last_heartbeat = datetime.now()
        orchestrator_instances[instance_id].status = "active"
        return {"message": "Heartbeat received"}
    else:
        raise HTTPException(status_code=404, detail="Instance not found")

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    now = datetime.now()
    active_instances = sum(
        1 for inst in orchestrator_instances.values()
        if inst.status == "active" and (now - inst.last_heartbeat).seconds < 60
    )

    return {
        "total_users": len(users_db),
        "total_projects": len(projects_db),
        "total_tasks": len(tasks_db),
        "active_instances": active_instances,
        "timestamp": now
    }

@app.get("/api/instances")
async def get_instances():
    """Get all orchestrator instances"""
    return list(orchestrator_instances.values())

@app.get("/api/users")
async def get_users(user_id: str = Depends(verify_api_key)):
    """Get all users (admin only)"""
    user = users_db[user_id]
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return list(users_db.values())

@app.get("/api/tasks/recent")
async def get_recent_tasks(user_id: str = Depends(verify_api_key)):
    """Get recent tasks"""
    user = users_db[user_id]

    if user.role == "admin":
        # Admin can see all tasks
        recent_tasks = sorted(
            tasks_db.values(),
            key=lambda x: x["created_at"],
            reverse=True
        )
    else:
        # Users can only see their own tasks
        recent_tasks = sorted(
            [task for task in tasks_db.values() if task["user_id"] == user_id],
            key=lambda x: x["created_at"],
            reverse=True
        )

    return recent_tasks[:50]

@app.get("/api/analytics")
async def get_analytics(
    query: AnalyticsQuery,
    user_id: str = Depends(verify_api_key)
):
    """Get analytics data"""
    user = users_db[user_id]
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Filter analytics data based on query
    filtered_events = []

    for event in analytics_db.values():
        if query.start_date and event["timestamp"] < query.start_date:
            continue
        if query.end_date and event["timestamp"] > query.end_date:
            continue
        if query.user_id and event["user_id"] != query.user_id:
            continue

        filtered_events.append(event)

    return {
        "events": filtered_events,
        "total_events": len(filtered_events),
        "query": query
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Проверяем Anthropic сервис
    anthropic_health = await anthropic_service.health_check()

    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "services": {
            "msp_server": "active",
            "database": "simulated",
            "orchestrator_instances": len(orchestrator_instances),
            "anthropic_service": anthropic_health["status"]
        }
    }

@app.post("/api/ai/analyze-project")
async def ai_analyze_project(
    project_data: Dict[str, Any],
    user_id: str = Depends(verify_api_key)
):
    """AI анализ проекта через Anthropic"""
    try:
        result = await anthropic_service.analyze_project_structure(project_data)

        log_analytics_event("ai_analysis", user_id, {
            "project_data_size": len(str(project_data)),
            "success": result["status"] == "success"
        })

        return result

    except Exception as e:
        logger.error(f"AI analysis failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/recommendations")
async def ai_get_recommendations(
    analysis_data: Dict[str, Any],
    user_id: str = Depends(verify_api_key)
):
    """Получение AI рекомендаций"""
    try:
        result = await anthropic_service.generate_recommendations(analysis_data)

        log_analytics_event("ai_recommendations", user_id, {
            "analysis_size": len(str(analysis_data)),
            "success": result["status"] == "success"
        })

        return result

    except Exception as e:
        logger.error(f"AI recommendations failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/explain-architecture")
async def ai_explain_architecture(
    architecture_data: Dict[str, Any],
    user_id: str = Depends(verify_api_key)
):
    """AI объяснение архитектуры"""
    try:
        result = await anthropic_service.explain_architecture(architecture_data)

        log_analytics_event("ai_explanation", user_id, {
            "architecture_size": len(str(architecture_data)),
            "success": result["status"] == "success"
        })

        return result

    except Exception as e:
        logger.error(f"AI explanation failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/assess-quality")
async def ai_assess_code_quality(
    code_data: Dict[str, Any],
    user_id: str = Depends(verify_api_key)
):
    """AI оценка качества кода"""
    try:
        result = await anthropic_service.assess_code_quality(code_data)

        log_analytics_event("ai_quality_assessment", user_id, {
            "code_size": len(str(code_data)),
            "success": result["status"] == "success"
        })

        return result

    except Exception as e:
        logger.error(f"AI quality assessment failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Initialize some demo data
async def initialize_demo_data():
    """Initialize demo data for testing"""
    # Create admin user
    admin_id = str(uuid.uuid4())
    admin_user = User(
        user_id=admin_id,
        username="admin",
        email="admin@example.com",
        role="admin",
        created_at=datetime.now(),
        api_key=generate_api_key()
    )
    users_db[admin_id] = admin_user

    # Create demo user
    demo_id = str(uuid.uuid4())
    demo_user = User(
        user_id=demo_id,
        username="demo",
        email="demo@example.com",
        role="user",
        created_at=datetime.now(),
        api_key=generate_api_key()
    )
    users_db[demo_id] = demo_user

    # Register main orchestrator instance
    main_instance = OrchestratorInstance(
        instance_id="main_orchestrator",
        url="http://localhost:9000",
        status="active",
        load=25,
        last_heartbeat=datetime.now(),
        version="1.0.0",
        capabilities=["analyze", "generate", "visualize", "github", "directory"]
    )
    orchestrator_instances["main_orchestrator"] = main_instance

    logger.info("Demo data initialized")
    logger.info(f"Admin API Key: {admin_user.api_key}")
    logger.info(f"Demo API Key: {demo_user.api_key}")

@app.on_event("startup")
async def startup_event():
    """Initialize MSP server"""
    await initialize_demo_data()
    logger.info("MSP Server started successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)