"""
TheHive Adapter for BCM Platform

Integrates with TheHive for security incident case management:
- Automatically creates cases from BCM incidents
- Syncs case status and updates back to Odoo
- Manages observables and tasks
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from config import Config
from models import HiveCaseCreationRequest, HiveCaseUpdate, IncidentData
from services.eventbus import EventBusService
from services.thehive_client import TheHiveClient
from services.processor import TheHiveProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BCM TheHive Adapter",
    description="TheHive integration for BCM incident management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
eventbus_service: EventBusService = None
thehive_client: TheHiveClient = None
processor: TheHiveProcessor = None
config = Config()

@app.on_event("startup")
async def startup():
    """Initialize services and event subscriptions"""
    global eventbus_service, thehive_client, processor
    
    logger.info("Starting TheHive Adapter...")
    
    # Initialize services
    eventbus_service = EventBusService(config)
    thehive_client = TheHiveClient(config)
    processor = TheHiveProcessor(eventbus_service, thehive_client)
    
    # Connect to services
    await eventbus_service.connect()
    await thehive_client.connect()
    
    # Subscribe to relevant events
    await eventbus_service.subscribe("bcm.incident.opened", processor.handle_incident_opened)
    await eventbus_service.subscribe("bcm.incident.reported", processor.handle_incident_opened)
    await eventbus_service.subscribe("bcm.incident.updated", processor.handle_incident_updated)
    await eventbus_service.subscribe("bcm.incident.resolved", processor.handle_incident_resolved)
    
    logger.info("TheHive Adapter started successfully")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if eventbus_service:
        await eventbus_service.disconnect()
    if thehive_client:
        await thehive_client.disconnect()
    logger.info("TheHive Adapter shut down")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    dependencies = {
        "eventbus": "healthy" if eventbus_service and eventbus_service.is_connected() else "unhealthy",
        "thehive": "healthy" if thehive_client and await thehive_client.is_healthy() else "unhealthy"
    }
    
    status = "healthy" if all(dep == "healthy" for dep in dependencies.values()) else "unhealthy"
    
    return {
        "status": status,
        "service": "thehive-adapter",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": dependencies
    }

@app.post("/api/cases/create")
async def create_case_manual(case_request: HiveCaseCreationRequest):
    """Manually create TheHive case from BCM incident"""
    try:
        case_data = await thehive_client.create_case(
            title=case_request.title,
            description=case_request.description,
            severity=case_request.severity,
            tags=case_request.tags,
            tenant_id=case_request.tenant_id,
            incident_id=case_request.incident_id
        )
        
        if case_data:
            # Publish case creation event
            await eventbus_service.publish({
                "event_type": "bcm.thehive.case_created",
                "tenant_id": case_request.tenant_id,
                "data": {
                    "incident_id": case_request.incident_id,
                    "thehive_case_id": case_data["id"],
                    "case_url": f"{config.THEHIVE_URL}/cases/{case_data['id']}/details",
                    "created_manually": True
                }
            })
            
            return {
                "status": "success",
                "case_id": case_data["id"],
                "case_url": f"{config.THEHIVE_URL}/cases/{case_data['id']}/details"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create case in TheHive")
            
    except Exception as e:
        logger.error(f"Manual case creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cases/{case_id}")
async def get_case_details(case_id: str, tenant_id: str):
    """Get TheHive case details"""
    try:
        case_data = await thehive_client.get_case(case_id)
        
        if not case_data:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Filter by tenant if case has tenant tag
        case_tags = case_data.get("tags", [])
        if tenant_id and f"tenant:{tenant_id}" not in case_tags:
            raise HTTPException(status_code=403, detail="Access denied to case")
        
        return case_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get case details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/cases/{case_id}/update")
async def update_case(case_id: str, case_update: HiveCaseUpdate):
    """Update TheHive case"""
    try:
        success = await thehive_client.update_case(case_id, case_update.dict(exclude_unset=True))
        
        if success:
            # Publish case update event
            await eventbus_service.publish({
                "event_type": "bcm.thehive.case_updated",
                "tenant_id": case_update.tenant_id,
                "data": {
                    "case_id": case_id,
                    "updates": case_update.dict(exclude_unset=True),
                    "updated_manually": True
                }
            })
            
            return {"status": "success", "message": "Case updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update case")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update case: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cases/{case_id}/observables")
async def add_observable(case_id: str, observable_data: Dict[str, Any]):
    """Add observable to TheHive case"""
    try:
        observable = await thehive_client.add_observable(
            case_id,
            observable_data["data_type"],
            observable_data["data"],
            observable_data.get("message", ""),
            observable_data.get("tags", [])
        )
        
        if observable:
            return {"status": "success", "observable_id": observable["id"]}
        else:
            raise HTTPException(status_code=500, detail="Failed to add observable")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add observable: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cases/{case_id}/tasks")
async def create_task(case_id: str, task_data: Dict[str, Any]):
    """Create task in TheHive case"""
    try:
        task = await thehive_client.create_task(
            case_id,
            task_data["title"],
            task_data.get("description", ""),
            task_data.get("assignee", None)
        )
        
        if task:
            return {"status": "success", "task_id": task["id"]}
        else:
            raise HTTPException(status_code=500, detail="Failed to create task")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cases/search")
async def search_cases(
    tenant_id: str,
    status: str = None,
    severity: int = None,
    tags: str = None,
    limit: int = 20,
    offset: int = 0
):
    """Search TheHive cases by criteria"""
    try:
        # Build search query
        query = {"range": f"{offset}-{offset+limit-1}"}
        
        # Add tenant filter
        filters = [{"_field": "tags", "_value": f"tenant:{tenant_id}"}]
        
        if status:
            filters.append({"_field": "status", "_value": status})
        
        if severity:
            filters.append({"_field": "severity", "_value": severity})
        
        if tags:
            tag_list = tags.split(",")
            for tag in tag_list:
                filters.append({"_field": "tags", "_value": tag.strip()})
        
        query["query"] = {"_and": filters} if len(filters) > 1 else filters[0]
        
        cases = await thehive_client.search_cases(query)
        
        return {
            "cases": cases,
            "total": len(cases),
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Failed to search cases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhooks/thehive")
async def thehive_webhook(webhook_data: Dict[str, Any]):
    """Handle webhook from TheHive"""
    try:
        logger.info(f"Received TheHive webhook: {webhook_data}")
        
        object_type = webhook_data.get("objectType")
        operation = webhook_data.get("operation")
        
        if object_type == "case" and operation in ["Update", "Creation"]:
            await processor.handle_thehive_case_webhook(webhook_data)
        elif object_type == "task" and operation in ["Update", "Creation"]:
            await processor.handle_thehive_task_webhook(webhook_data)
        
        return {"status": "success", "message": "Webhook processed"}
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/statistics/{tenant_id}")
async def get_statistics(tenant_id: str):
    """Get case statistics for tenant"""
    try:
        stats = await thehive_client.get_case_statistics(tenant_id)
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8004,
        log_level="info"
    )
