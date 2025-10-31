#!/usr/bin/env python3
"""
CRM Bridge Service - мост между Odoo CRM и централизованными gateway
Реализует архитектуру из ODOO_MODULES_INTEGRATION_STRATEGY.md
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel
import os
from event_bus import BcmEventBus, BcmEvent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crm_bridge")

app = FastAPI(
    title="BCM CRM Bridge",
    description="Bridge between Odoo CRM and centralized gateways",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
class Config:
    ODOO_API_URL = os.getenv("ODOO_API_URL", "http://odoo:8069")
    ODOO_DB = os.getenv("ODOO_DB", "bcm_platform")
    DATABASE_GATEWAY_URL = os.getenv("DATABASE_GATEWAY_URL", "http://unified_database_gateway:8888")
    API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://unified_api_gateway:8777")

# Models
class CrmProject(BaseModel):
    id: int
    name: str
    partner_id: int
    partner_name: str
    stage_id: int
    stage_name: str
    bcm_maturity_score: float = 0.0
    iso_compliance: float = 0.0
    implementation_progress: float = 0.0

class BcmEventBusMessage(BaseModel):
    event_type: str
    source_module: str
    project_id: int
    data: Dict[str, Any]
    timestamp: datetime = datetime.now()

class BcmWorkspaceData(BaseModel):
    project_id: int
    organization_context: Dict[str, Any]
    bcm_audits: List[Dict[str, Any]] = []
    bcm_incidents: List[Dict[str, Any]] = []
    bcm_plans: List[Dict[str, Any]] = []
    bcm_trainings: List[Dict[str, Any]] = []

# CRM Bridge Class
class CrmBridgeService:
    def __init__(self):
        self.odoo_session = None
        self.active_projects = {}
        self.event_bus = BcmEventBus(Config.ODOO_API_URL, Config.DATABASE_GATEWAY_URL)

    async def authenticate_odoo(self):
        """Authenticate with Odoo"""
        async with httpx.AsyncClient() as client:
            auth_data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "db": Config.ODOO_DB,
                    "login": "admin",
                    "password": "admin"
                },
                "id": 1
            }

            try:
                response = await client.post(
                    f"{Config.ODOO_API_URL}/web/session/authenticate",
                    json=auth_data
                )
                result = response.json()

                if result.get("result") and result["result"].get("uid"):
                    self.odoo_session = result["result"]["session_id"]
                    logger.info("✅ Authenticated with Odoo CRM")
                    return True

            except Exception as e:
                logger.error(f"❌ Odoo authentication failed: {e}")

        return False

    async def get_crm_projects(self) -> List[CrmProject]:
        """Get active BCM projects from Odoo CRM"""
        if not self.odoo_session:
            await self.authenticate_odoo()

        async with httpx.AsyncClient() as client:
            # Search for CRM leads/opportunities that are BCM projects
            search_data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": "crm.lead",
                    "method": "search_read",
                    "args": [
                        [("active", "=", True)],  # Active projects only
                        ["name", "partner_id", "stage_id", "tag_ids", "description"]
                    ]
                },
                "id": 2
            }

            try:
                response = await client.post(
                    f"{Config.ODOO_API_URL}/web/dataset/call_kw",
                    json=search_data,
                    headers={"Cookie": f"session_id={self.odoo_session}"}
                )
                result = response.json()

                if result.get("result"):
                    projects = []
                    for lead in result["result"]:
                        # Convert to CrmProject
                        project = CrmProject(
                            id=lead["id"],
                            name=lead["name"],
                            partner_id=lead["partner_id"][0] if lead["partner_id"] else 0,
                            partner_name=lead["partner_id"][1] if lead["partner_id"] else "Unknown",
                            stage_id=lead["stage_id"][0] if lead["stage_id"] else 0,
                            stage_name=lead["stage_id"][1] if lead["stage_id"] else "Unknown"
                        )
                        projects.append(project)

                    return projects

            except Exception as e:
                logger.error(f"Error fetching CRM projects: {e}")

        return []

    async def create_bcm_workspace(self, project: CrmProject):
        """Create BCM workspace structure when project is won"""
        workspace_data = {
            "project_id": project.id,
            "organization_context": {
                "name": project.partner_name,
                "bcm_maturity": "initial",
                "created_date": datetime.now().isoformat()
            }
        }

        # Initialize BCM modules through database gateway
        async with httpx.AsyncClient() as client:
            try:
                # Create organization context
                context_data = {
                    "database": "odoo",
                    "operation": "odoo_create",
                    "model": "bcm.context",
                    "data": {
                        "name": project.partner_name,
                        "crm_project_id": project.id,
                        "maturity_level": "initial"
                    }
                }

                await client.post(
                    f"{Config.DATABASE_GATEWAY_URL}/query",
                    json=context_data
                )

                # Schedule initial audit
                audit_data = {
                    "database": "odoo",
                    "operation": "odoo_create",
                    "model": "bcm.audit",
                    "data": {
                        "name": f"Initial Assessment - {project.partner_name}",
                        "crm_project_id": project.id,
                        "audit_type": "initial",
                        "scheduled_date": datetime.now().isoformat()
                    }
                }

                await client.post(
                    f"{Config.DATABASE_GATEWAY_URL}/query",
                    json=audit_data
                )

                logger.info(f"✅ BCM workspace created for project {project.id}")

            except Exception as e:
                logger.error(f"Error creating BCM workspace: {e}")

    async def handle_bcm_event(self, event: BcmEventBusMessage):
        """Handle events from BCM modules"""
        logger.info(f"📨 Received BCM event: {event.event_type} from {event.source_module}")

        # Convert to internal event format and publish to Event Bus
        bcm_event = BcmEvent(
            event_type=event.event_type,
            source_module=event.source_module,
            project_id=event.project_id,
            data=event.data,
            timestamp=event.timestamp
        )

        await self.event_bus.publish_event(bcm_event)

        # Legacy handling for immediate response
        if event.event_type == "audit.completed":
            await self.update_crm_compliance(event)
        elif event.event_type == "incident.critical":
            await self.escalate_to_crm(event)
        elif event.event_type == "plan.activated":
            await self.notify_crm_stakeholders(event)

    async def update_crm_compliance(self, event: BcmEventBusMessage):
        """Update CRM project with compliance score from audit"""
        if not self.odoo_session:
            await self.authenticate_odoo()

        async with httpx.AsyncClient() as client:
            try:
                # Update CRM lead with new compliance score
                update_data = {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "model": "crm.lead",
                        "method": "write",
                        "args": [
                            [event.project_id],
                            {
                                "description": f"ISO Compliance: {event.data.get('compliance_score', 0)}%\nLast Updated: {datetime.now()}"
                            }
                        ]
                    },
                    "id": 3
                }

                await client.post(
                    f"{Config.ODOO_API_URL}/web/dataset/call_kw",
                    json=update_data,
                    headers={"Cookie": f"session_id={self.odoo_session}"}
                )

                logger.info(f"✅ Updated CRM project {event.project_id} with compliance score")

            except Exception as e:
                logger.error(f"Error updating CRM compliance: {e}")

# Global service instance
crm_bridge = CrmBridgeService()

@app.on_event("startup")
async def startup_event():
    """Initialize CRM Bridge on startup"""
    await crm_bridge.authenticate_odoo()
    # Start Event Bus processing in background
    asyncio.create_task(crm_bridge.event_bus.start_processing())

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "crm_bridge",
        "timestamp": datetime.now().isoformat(),
        "odoo_connected": crm_bridge.odoo_session is not None
    }

@app.get("/projects", response_model=List[CrmProject])
async def get_bcm_projects():
    """Get all BCM projects from CRM"""
    return await crm_bridge.get_crm_projects()

@app.post("/projects/{project_id}/workspace")
async def create_project_workspace(project_id: int):
    """Create BCM workspace for project"""
    projects = await crm_bridge.get_crm_projects()
    project = next((p for p in projects if p.id == project_id), None)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await crm_bridge.create_bcm_workspace(project)
    return {"message": f"BCM workspace created for project {project_id}"}

@app.post("/events/bcm")
async def handle_bcm_event(event: BcmEventBusMessage):
    """Handle BCM module events"""
    await crm_bridge.handle_bcm_event(event)
    return {"message": "Event processed"}

@app.get("/projects/{project_id}/workspace")
async def get_project_workspace(project_id: int) -> BcmWorkspaceData:
    """Get full BCM workspace data for project"""
    async with httpx.AsyncClient() as client:
        try:
            # Get all BCM data related to this project
            queries = [
                {"database": "odoo", "operation": "odoo_search", "model": "bcm.context", "domain": [("crm_project_id", "=", project_id)]},
                {"database": "odoo", "operation": "odoo_search", "model": "bcm.audit", "domain": [("crm_project_id", "=", project_id)]},
                {"database": "odoo", "operation": "odoo_search", "model": "bcm.incident", "domain": [("crm_project_id", "=", project_id)]},
                {"database": "odoo", "operation": "odoo_search", "model": "bcm.plan", "domain": [("crm_project_id", "=", project_id)]},
                {"database": "odoo", "operation": "odoo_search", "model": "bcm.training", "domain": [("crm_project_id", "=", project_id)]},
            ]

            results = []
            for query in queries:
                response = await client.post(f"{Config.DATABASE_GATEWAY_URL}/query", json=query)
                results.append(response.json() if response.status_code == 200 else [])

            return BcmWorkspaceData(
                project_id=project_id,
                organization_context=results[0][0] if results[0] else {},
                bcm_audits=results[1] or [],
                bcm_incidents=results[2] or [],
                bcm_plans=results[3] or [],
                bcm_trainings=results[4] or []
            )

        except Exception as e:
            logger.error(f"Error getting workspace data: {e}")
            raise HTTPException(status_code=500, detail="Error fetching workspace data")

@app.get("/integration/test")
async def test_integration():
    """Test all integrations"""
    results = {}

    # Test Odoo connection
    results["odoo"] = await crm_bridge.authenticate_odoo()

    # Test Database Gateway
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{Config.DATABASE_GATEWAY_URL}/health")
            results["database_gateway"] = response.status_code == 200
        except:
            results["database_gateway"] = False

        # Test API Gateway
        try:
            response = await client.get(f"{Config.API_GATEWAY_URL}/health")
            results["api_gateway"] = response.status_code == 200
        except:
            results["api_gateway"] = False

    return {
        "integration_status": results,
        "all_systems_go": all(results.values())
    }

@app.get("/eventbus/stats")
async def get_event_bus_stats():
    """Get Event Bus statistics"""
    return await crm_bridge.event_bus.get_event_stats()

@app.post("/eventbus/publish")
async def publish_event_to_bus(event_data: dict):
    """Publish event directly to Event Bus"""
    try:
        event = BcmEvent(
            event_type=event_data["event_type"],
            source_module=event_data["source_module"],
            project_id=event_data["project_id"],
            data=event_data.get("data", {}),
            user_id=event_data.get("user_id"),
            priority=event_data.get("priority", "normal")
        )

        success = await crm_bridge.event_bus.publish_event(event)
        return {"published": success, "event_id": str(event.timestamp)}

    except Exception as e:
        logger.error(f"Event publishing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Specific Event Bus endpoints for common BCM events
@app.post("/eventbus/project-won")
async def project_won_event(project_data: dict):
    """Trigger project won event"""
    event = BcmEvent(
        event_type="project.won",
        source_module="crm_project",
        project_id=project_data["project_id"],
        data=project_data
    )

    await crm_bridge.event_bus.publish_event(event)
    return {"message": "Project won event triggered", "project_id": project_data["project_id"]}

@app.post("/eventbus/audit-completed")
async def audit_completed_event(audit_data: dict):
    """Trigger audit completed event"""
    event = BcmEvent(
        event_type="audit.completed",
        source_module="bcm_audit",
        project_id=audit_data["project_id"],
        data=audit_data
    )

    await crm_bridge.event_bus.publish_event(event)
    return {"message": "Audit completed event triggered", "compliance_score": audit_data.get("compliance_score")}

@app.post("/eventbus/incident-critical")
async def critical_incident_event(incident_data: dict):
    """Trigger critical incident event"""
    event = BcmEvent(
        event_type="incident.critical",
        source_module="bcm_incident",
        project_id=incident_data["project_id"],
        data=incident_data,
        priority="critical"
    )

    await crm_bridge.event_bus.publish_event(event)
    return {"message": "Critical incident event triggered", "incident_id": incident_data.get("incident_id")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8778, log_level="info")