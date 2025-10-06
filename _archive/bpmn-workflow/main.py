"""
BPMN Workflow Service - FastAPI + BPMN Engine
ISO 22301 BCM Platform BPMN Process Management
"""

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio
import json
import os
import httpx
import uuid
import xml.etree.ElementTree as ET
from contextlib import asynccontextmanager
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
EVENTBUS_URL = os.getenv("EVENTBUS_URL", "http://localhost:8001")
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://bcm:bcm@localhost/bcm_platform")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8081,http://localhost:8069").split(",")

# BPMN Process Models
class BPMNProcess(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    bpmn_xml: str = Field(..., description="BPMN 2.0 XML content")
    tenant_id: str = Field(..., min_length=1, max_length=255)
    version: str = Field(default="1.0")
    is_active: bool = Field(default=True)
    created_by: Optional[str] = None
    
class ProcessInstance(BaseModel):
    id: Optional[str] = None
    process_id: str
    tenant_id: str
    status: str = Field(default="ACTIVE")  # ACTIVE, COMPLETED, SUSPENDED, TERMINATED
    variables: Dict[str, Any] = Field(default={})
    current_activities: List[str] = Field(default=[])
    started_by: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Task(BaseModel):
    id: Optional[str] = None
    process_instance_id: str
    activity_id: str
    name: str
    task_type: str  # USER_TASK, SCRIPT_TASK, SERVICE_TASK, etc.
    assignee: Optional[str] = None
    status: str = Field(default="ACTIVE")  # ACTIVE, COMPLETED, CANCELLED
    variables: Dict[str, Any] = Field(default={})
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

# BPMN Engine Class
class BPMNEngine:
    def __init__(self):
        self.processes: Dict[str, BPMNProcess] = {}
        self.instances: Dict[str, ProcessInstance] = {}
        self.tasks: Dict[str, Task] = {}
        
    async def deploy_process(self, process: BPMNProcess) -> str:
        """Deploy a BPMN process definition"""
        process_id = process.id or str(uuid.uuid4())
        process.id = process_id
        
        # Validate BPMN XML
        try:
            root = ET.fromstring(process.bpmn_xml)
            # Basic validation - check if it's valid BPMN structure
            if root.tag != "{http://www.omg.org/spec/BPMN/20100524/MODEL}definitions":
                raise ValueError("Invalid BPMN XML format")
        except ET.ParseError as e:
            raise HTTPException(status_code=400, detail=f"Invalid BPMN XML: {str(e)}")
        
        self.processes[process_id] = process
        logger.info(f"Deployed BPMN process {process_id}: {process.name}")
        
        # Publish event
        await self.publish_event("bpmn.process.deployed", process.tenant_id, {
            "process_id": process_id,
            "process_name": process.name,
            "version": process.version
        })
        
        return process_id
    
    async def start_process(self, process_id: str, tenant_id: str, variables: Dict[str, Any] = {}, started_by: str = None) -> str:
        """Start a new process instance"""
        if process_id not in self.processes:
            raise HTTPException(status_code=404, detail=f"Process {process_id} not found")
        
        process = self.processes[process_id]
        if process.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        instance_id = str(uuid.uuid4())
        instance = ProcessInstance(
            id=instance_id,
            process_id=process_id,
            tenant_id=tenant_id,
            variables=variables,
            started_by=started_by,
            started_at=datetime.utcnow()
        )
        
        # Parse BPMN and find start events
        root = ET.fromstring(process.bpmn_xml)
        ns = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
        start_events = root.findall(".//bpmn:startEvent", ns)
        
        if start_events:
            # Find tasks connected to start events
            tasks = await self.find_next_activities(root, start_events[0], instance_id)
            for task_def in tasks:
                await self.create_task(instance_id, task_def)
        
        self.instances[instance_id] = instance
        logger.info(f"Started process instance {instance_id} for process {process_id}")
        
        # Publish event
        await self.publish_event("bpmn.instance.started", tenant_id, {
            "instance_id": instance_id,
            "process_id": process_id,
            "variables": variables,
            "started_by": started_by
        })
        
        return instance_id
    
    async def find_next_activities(self, root: ET.Element, current_element: ET.Element, instance_id: str) -> List[Dict[str, Any]]:
        """Find next activities from current BPMN element"""
        ns = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
        tasks = []
        
        # Find outgoing sequence flows
        outgoing = current_element.findall("bpmn:outgoing", ns)
        
        for flow_id in outgoing:
            flow_id_text = flow_id.text
            # Find the sequence flow
            seq_flow = root.find(f".//bpmn:sequenceFlow[@id='{flow_id_text}']", ns)
            if seq_flow is not None:
                target_ref = seq_flow.get("targetRef")
                # Find target activity
                target = root.find(f".//*[@id='{target_ref}']", ns)
                if target is not None:
                    task_def = {
                        "activity_id": target_ref,
                        "name": target.get("name", target_ref),
                        "task_type": target.tag.split("}")[-1].upper(),
                        "instance_id": instance_id
                    }
                    tasks.append(task_def)
        
        return tasks
    
    async def create_task(self, instance_id: str, task_def: Dict[str, Any]):
        """Create a new task"""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            process_instance_id=instance_id,
            activity_id=task_def["activity_id"],
            name=task_def["name"],
            task_type=task_def["task_type"],
            created_at=datetime.utcnow()
        )
        self.tasks[task_id] = task
        
        instance = self.instances[instance_id]
        instance.current_activities.append(task_def["activity_id"])
        
        logger.info(f"Created task {task_id}: {task.name}")
    
    async def complete_task(self, task_id: str, tenant_id: str, variables: Dict[str, Any] = {}, completed_by: str = None):
        """Complete a task and move process forward"""
        if task_id not in self.tasks:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        instance = self.instances[task.process_instance_id]
        
        if instance.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update task
        task.status = "COMPLETED"
        task.completed_at = datetime.utcnow()
        task.variables.update(variables)
        
        # Update instance variables
        instance.variables.update(variables)
        
        # Remove from current activities
        if task.activity_id in instance.current_activities:
            instance.current_activities.remove(task.activity_id)
        
        # Find next activities
        process = self.processes[instance.process_id]
        root = ET.fromstring(process.bpmn_xml)
        ns = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"}
        current_element = root.find(f".//*[@id='{task.activity_id}']", ns)
        
        if current_element is not None:
            next_tasks = await self.find_next_activities(root, current_element, instance.id)
            
            if not next_tasks:
                # No more tasks - process completed
                instance.status = "COMPLETED"
                instance.completed_at = datetime.utcnow()
                
                await self.publish_event("bpmn.instance.completed", tenant_id, {
                    "instance_id": instance.id,
                    "process_id": instance.process_id,
                    "variables": instance.variables
                })
            else:
                # Create next tasks
                for task_def in next_tasks:
                    await self.create_task(instance.id, task_def)
        
        logger.info(f"Completed task {task_id}")
        
        # Publish event
        await self.publish_event("bpmn.task.completed", tenant_id, {
            "task_id": task_id,
            "instance_id": instance.id,
            "activity_id": task.activity_id,
            "variables": variables,
            "completed_by": completed_by
        })
    
    async def publish_event(self, event_type: str, tenant_id: str, data: Dict[str, Any]):
        """Publish event to EventBus"""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(f"{EVENTBUS_URL}/api/events/publish", json={
                    "event_type": event_type,
                    "tenant_id": tenant_id,
                    "data": data
                })
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")

# Global BPMN engine instance
bpmn_engine = BPMNEngine()

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting BPMN Service...")
    yield
    logger.info("Shutting down BPMN Service...")

# Create FastAPI app
app = FastAPI(
    title="BCM BPMN Workflow Service",
    description="BPMN process management for ISO 22301 BCM Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bpmn_workflow"}

# Deploy BPMN process
@app.post("/api/bpmn/processes")
async def deploy_process(process: BPMNProcess):
    process_id = await bpmn_engine.deploy_process(process)
    return {"process_id": process_id, "status": "deployed"}

# Get all processes for tenant
@app.get("/api/bpmn/processes")
async def get_processes(tenant_id: str):
    processes = [
        p for p in bpmn_engine.processes.values() 
        if p.tenant_id == tenant_id
    ]
    return {"processes": processes}

# Get process by ID
@app.get("/api/bpmn/processes/{process_id}")
async def get_process(process_id: str, tenant_id: str):
    if process_id not in bpmn_engine.processes:
        raise HTTPException(status_code=404, detail="Process not found")
    
    process = bpmn_engine.processes[process_id]
    if process.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {"process": process}

# Start process instance
@app.post("/api/bpmn/processes/{process_id}/start")
async def start_process(
    process_id: str,
    tenant_id: str,
    variables: Dict[str, Any] = {},
    started_by: Optional[str] = None
):
    instance_id = await bpmn_engine.start_process(process_id, tenant_id, variables, started_by)
    return {"instance_id": instance_id, "status": "started"}

# Get process instances
@app.get("/api/bpmn/instances")
async def get_instances(tenant_id: str, status: Optional[str] = None):
    instances = [
        i for i in bpmn_engine.instances.values()
        if i.tenant_id == tenant_id and (not status or i.status == status)
    ]
    return {"instances": instances}

# Get process instance by ID
@app.get("/api/bpmn/instances/{instance_id}")
async def get_instance(instance_id: str, tenant_id: str):
    if instance_id not in bpmn_engine.instances:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    instance = bpmn_engine.instances[instance_id]
    if instance.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {"instance": instance}

# Get tasks for tenant or user
@app.get("/api/bpmn/tasks")
async def get_tasks(
    tenant_id: str,
    assignee: Optional[str] = None,
    status: Optional[str] = None
):
    tasks = []
    for task in bpmn_engine.tasks.values():
        instance = bpmn_engine.instances.get(task.process_instance_id)
        if instance and instance.tenant_id == tenant_id:
            if assignee and task.assignee != assignee:
                continue
            if status and task.status != status:
                continue
            tasks.append(task)
    
    return {"tasks": tasks}

# Complete task
@app.post("/api/bpmn/tasks/{task_id}/complete")
async def complete_task(
    task_id: str,
    tenant_id: str,
    variables: Dict[str, Any] = {},
    completed_by: Optional[str] = None
):
    await bpmn_engine.complete_task(task_id, tenant_id, variables, completed_by)
    return {"status": "completed"}

# Terminate process instance
@app.post("/api/bpmn/instances/{instance_id}/terminate")
async def terminate_instance(instance_id: str, tenant_id: str, reason: Optional[str] = None):
    if instance_id not in bpmn_engine.instances:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    instance = bpmn_engine.instances[instance_id]
    if instance.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    instance.status = "TERMINATED"
    instance.completed_at = datetime.utcnow()
    
    # Cancel all active tasks
    for task in bpmn_engine.tasks.values():
        if task.process_instance_id == instance_id and task.status == "ACTIVE":
            task.status = "CANCELLED"
    
    await bpmn_engine.publish_event("bpmn.instance.terminated", tenant_id, {
        "instance_id": instance_id,
        "reason": reason
    })
    
    return {"status": "terminated"}

# Mock Data Endpoints for Testing
from mock_data import get_mock_processes, get_mock_instances, get_mock_tasks, get_workflow_templates

@app.get("/api/bpmn/mock/processes")
async def get_mock_process_data():
    """Get mock process data for testing"""
    return {"mock_processes": get_mock_processes()}

@app.get("/api/bpmn/mock/instances")
async def get_mock_instance_data():
    """Get mock process instance data for testing"""
    return {"mock_instances": get_mock_instances()}

@app.get("/api/bpmn/mock/tasks")
async def get_mock_task_data():
    """Get mock task data for testing"""
    return {"mock_tasks": get_mock_tasks()}

@app.get("/api/bpmn/mock/templates")
async def get_workflow_template_data():
    """Get BCM workflow templates"""
    return {"workflow_templates": get_workflow_templates()}

@app.post("/api/bpmn/mock/deploy-demo-process")
async def deploy_demo_process(tenant_id: str):
    """Deploy demo BCM process for testing"""
    mock_processes = get_mock_processes()
    demo_process = mock_processes[0]  # BCM Incident Response
    demo_process["tenant_id"] = tenant_id
    
    # Deploy the demo process
    from main import BPMNProcess
    process = BPMNProcess(**demo_process)
    process_id = await bpmn_engine.deploy_process(process)
    
    return {
        "status": "deployed",
        "process_id": process_id,
        "process_name": demo_process["name"],
        "description": "Demo BCM Incident Response process deployed"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)  # BPMN Workflow Service