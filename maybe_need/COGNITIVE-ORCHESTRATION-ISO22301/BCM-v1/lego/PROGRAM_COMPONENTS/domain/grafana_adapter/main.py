"""
Grafana Adapter Service - KPI Dashboards & Metrics
ISO 22301 BCM Platform Grafana Integration
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
import asyncio
import json
import os
import httpx
import uuid
import base64
from contextlib import asynccontextmanager
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
EVENTBUS_URL = os.getenv("EVENTBUS_URL", "http://localhost:8001")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8081,http://localhost:8069").split(",")

# Grafana Models
class GrafanaConfig(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    base_url: HttpUrl
    api_key: str = Field(..., min_length=1)
    tenant_id: str = Field(..., min_length=1)
    organization_id: Optional[int] = None
    is_active: bool = Field(default=True)
    settings: Dict[str, Any] = Field(default={})

class Dashboard(BaseModel):
    id: Optional[str] = None
    uid: str
    title: str
    description: Optional[str] = None
    tags: List[str] = Field(default=[])
    folder_id: Optional[int] = None
    folder_title: Optional[str] = None
    url: Optional[str] = None
    version: Optional[int] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

class Panel(BaseModel):
    id: int
    title: str
    type: str  # graph, stat, table, etc.
    targets: List[Dict[str, Any]] = Field(default=[])
    gridPos: Dict[str, int] = Field(default={})
    datasource: Optional[str] = None
    options: Dict[str, Any] = Field(default={})

class DashboardData(BaseModel):
    dashboard: Dict[str, Any]
    meta: Dict[str, Any]

class Annotation(BaseModel):
    id: Optional[int] = None
    dashboard_id: Optional[int] = None
    panel_id: Optional[int] = None
    time: datetime
    time_end: Optional[datetime] = None
    text: str
    tags: List[str] = Field(default=[])
    user_id: Optional[int] = None

class DataSource(BaseModel):
    id: Optional[int] = None
    uid: str
    name: str
    type: str  # prometheus, influxdb, postgres, etc.
    url: str
    access: str = Field(default="proxy")  # direct, proxy
    is_default: bool = Field(default=False)
    basic_auth: bool = Field(default=False)
    database: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None

# Grafana Adapter
class GrafanaAdapter:
    def __init__(self, config: GrafanaConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
        )
        self.base_url = str(config.base_url).rstrip('/')
    
    async def test_connection(self) -> bool:
        """Test connection to Grafana instance"""
        try:
            response = await self.client.get(f"{self.base_url}/api/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Grafana connection test failed: {e}")
            return False
    
    async def get_dashboards(self, folder_id: Optional[int] = None, tag: Optional[str] = None) -> List[Dashboard]:
        """Get list of dashboards"""
        try:
            params = {}
            if folder_id is not None:
                params["folderIds"] = folder_id
            if tag:
                params["tag"] = tag
            
            response = await self.client.get(f"{self.base_url}/api/search", params=params)
            
            if response.status_code == 200:
                dashboards_data = response.json()
                dashboards = []
                
                for dash_data in dashboards_data:
                    if dash_data.get("type") == "dash-db":
                        dashboard = Dashboard(
                            id=str(dash_data.get("id")),
                            uid=dash_data.get("uid"),
                            title=dash_data.get("title"),
                            tags=dash_data.get("tags", []),
                            folder_id=dash_data.get("folderId"),
                            folder_title=dash_data.get("folderTitle"),
                            url=dash_data.get("url"),
                            created=datetime.fromisoformat(dash_data.get("created").replace('Z', '+00:00')) if dash_data.get("created") else None,
                            updated=datetime.fromisoformat(dash_data.get("updated").replace('Z', '+00:00')) if dash_data.get("updated") else None
                        )
                        dashboards.append(dashboard)
                
                return dashboards
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to get dashboards")
                
        except Exception as e:
            logger.error(f"Failed to get Grafana dashboards: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_dashboard(self, dashboard_uid: str) -> DashboardData:
        """Get dashboard by UID"""
        try:
            response = await self.client.get(f"{self.base_url}/api/dashboards/uid/{dashboard_uid}")
            
            if response.status_code == 200:
                data = response.json()
                return DashboardData(
                    dashboard=data.get("dashboard", {}),
                    meta=data.get("meta", {})
                )
            else:
                raise HTTPException(status_code=response.status_code, detail="Dashboard not found")
                
        except Exception as e:
            logger.error(f"Failed to get Grafana dashboard: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def create_dashboard(self, dashboard_data: Dict[str, Any], folder_id: Optional[int] = None) -> Dict[str, Any]:
        """Create new dashboard"""
        try:
            payload = {
                "dashboard": dashboard_data,
                "overwrite": False
            }
            
            if folder_id is not None:
                payload["folderId"] = folder_id
            
            response = await self.client.post(f"{self.base_url}/api/dashboards/db", json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to create dashboard")
                
        except Exception as e:
            logger.error(f"Failed to create Grafana dashboard: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_dashboard(self, dashboard_data: Dict[str, Any], folder_id: Optional[int] = None) -> Dict[str, Any]:
        """Update existing dashboard"""
        try:
            payload = {
                "dashboard": dashboard_data,
                "overwrite": True
            }
            
            if folder_id is not None:
                payload["folderId"] = folder_id
            
            response = await self.client.post(f"{self.base_url}/api/dashboards/db", json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to update dashboard")
                
        except Exception as e:
            logger.error(f"Failed to update Grafana dashboard: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def delete_dashboard(self, dashboard_uid: str) -> bool:
        """Delete dashboard"""
        try:
            response = await self.client.delete(f"{self.base_url}/api/dashboards/uid/{dashboard_uid}")
            return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Failed to delete Grafana dashboard: {e}")
            return False
    
    async def get_datasources(self) -> List[DataSource]:
        """Get list of data sources"""
        try:
            response = await self.client.get(f"{self.base_url}/api/datasources")
            
            if response.status_code == 200:
                datasources_data = response.json()
                datasources = []
                
                for ds_data in datasources_data:
                    datasource = DataSource(
                        id=ds_data.get("id"),
                        uid=ds_data.get("uid"),
                        name=ds_data.get("name"),
                        type=ds_data.get("type"),
                        url=ds_data.get("url"),
                        access=ds_data.get("access", "proxy"),
                        is_default=ds_data.get("isDefault", False),
                        basic_auth=ds_data.get("basicAuth", False),
                        database=ds_data.get("database"),
                        user=ds_data.get("user")
                    )
                    datasources.append(datasource)
                
                return datasources
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to get data sources")
                
        except Exception as e:
            logger.error(f"Failed to get Grafana data sources: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def create_datasource(self, datasource: DataSource) -> Dict[str, Any]:
        """Create new data source"""
        try:
            ds_data = {
                "name": datasource.name,
                "type": datasource.type,
                "url": datasource.url,
                "access": datasource.access,
                "isDefault": datasource.is_default,
                "basicAuth": datasource.basic_auth
            }
            
            if datasource.database:
                ds_data["database"] = datasource.database
            if datasource.user:
                ds_data["user"] = datasource.user
            if datasource.password:
                ds_data["password"] = datasource.password
            
            response = await self.client.post(f"{self.base_url}/api/datasources", json=ds_data)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to create data source")
                
        except Exception as e:
            logger.error(f"Failed to create Grafana data source: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def create_annotation(self, annotation: Annotation) -> Dict[str, Any]:
        """Create annotation"""
        try:
            annotation_data = {
                "time": int(annotation.time.timestamp() * 1000),
                "text": annotation.text,
                "tags": annotation.tags
            }
            
            if annotation.time_end:
                annotation_data["timeEnd"] = int(annotation.time_end.timestamp() * 1000)
            if annotation.dashboard_id:
                annotation_data["dashboardId"] = annotation.dashboard_id
            if annotation.panel_id:
                annotation_data["panelId"] = annotation.panel_id
            
            response = await self.client.post(f"{self.base_url}/api/annotations", json=annotation_data)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to create annotation")
                
        except Exception as e:
            logger.error(f"Failed to create Grafana annotation: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_dashboard_snapshot_url(self, dashboard_uid: str, time_from: Optional[datetime] = None, time_to: Optional[datetime] = None) -> str:
        """Get snapshot URL for dashboard"""
        params = {}
        if time_from:
            params["from"] = int(time_from.timestamp() * 1000)
        if time_to:
            params["to"] = int(time_to.timestamp() * 1000)
        
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{self.base_url}/d/{dashboard_uid}"
        if param_str:
            url += f"?{param_str}"
        
        return url
    
    async def generate_dashboard_pdf(self, dashboard_uid: str, time_from: Optional[datetime] = None, time_to: Optional[datetime] = None) -> bytes:
        """Generate PDF report of dashboard (requires Grafana Enterprise or external service)"""
        # This would typically require Grafana Enterprise or external PDF service
        # For now, return placeholder
        logger.warning("PDF generation requires Grafana Enterprise or external service")
        return b"PDF generation not available in OSS version"

# BCM Dashboard Templates
class BCMDashboards:
    @staticmethod
    def create_bcm_overview_dashboard() -> Dict[str, Any]:
        """Create BCM overview dashboard template"""
        return {
            "title": "BCM Platform Overview",
            "tags": ["BCM", "Overview"],
            "panels": [
                {
                    "id": 1,
                    "title": "BIA Coverage",
                    "type": "stat",
                    "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
                    "targets": [
                        {
                            "expr": "bia_coverage_percentage",
                            "refId": "A"
                        }
                    ],
                    "options": {
                        "colorMode": "background",
                        "graphMode": "area",
                        "orientation": "horizontal"
                    }
                },
                {
                    "id": 2,
                    "title": "Plan Updates Status",
                    "type": "stat",
                    "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0},
                    "targets": [
                        {
                            "expr": "plans_up_to_date_percentage",
                            "refId": "A"
                        }
                    ]
                },
                {
                    "id": 3,
                    "title": "CAPA On-Time Completion",
                    "type": "stat",
                    "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0},
                    "targets": [
                        {
                            "expr": "capa_on_time_percentage",
                            "refId": "A"
                        }
                    ]
                },
                {
                    "id": 4,
                    "title": "Training Completion Rate",
                    "type": "stat",
                    "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0},
                    "targets": [
                        {
                            "expr": "training_completion_rate",
                            "refId": "A"
                        }
                    ]
                },
                {
                    "id": 5,
                    "title": "Incident Trends",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                    "targets": [
                        {
                            "expr": "incident_count_by_severity",
                            "refId": "A"
                        }
                    ]
                },
                {
                    "id": 6,
                    "title": "Exercise Completion",
                    "type": "timeseries",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                    "targets": [
                        {
                            "expr": "exercise_completion_rate",
                            "refId": "A"
                        }
                    ]
                }
            ]
        }
    
    @staticmethod
    def create_incident_dashboard() -> Dict[str, Any]:
        """Create incident management dashboard"""
        return {
            "title": "BCM Incident Management",
            "tags": ["BCM", "Incidents"],
            "panels": [
                {
                    "id": 1,
                    "title": "Open Incidents by Severity",
                    "type": "piechart",
                    "gridPos": {"h": 8, "w": 8, "x": 0, "y": 0},
                    "targets": [
                        {
                            "expr": "incidents_by_severity",
                            "refId": "A"
                        }
                    ]
                },
                {
                    "id": 2,
                    "title": "Mean Time to Recovery (MTTR)",
                    "type": "stat",
                    "gridPos": {"h": 8, "w": 8, "x": 8, "y": 0},
                    "targets": [
                        {
                            "expr": "avg(mttr_hours)",
                            "refId": "A"
                        }
                    ]
                },
                {
                    "id": 3,
                    "title": "Recovery Point Objective (RPO) Adherence",
                    "type": "gauge",
                    "gridPos": {"h": 8, "w": 8, "x": 16, "y": 0},
                    "targets": [
                        {
                            "expr": "rpo_adherence_percentage",
                            "refId": "A"
                        }
                    ]
                }
            ]
        }

# Grafana Manager
class GrafanaManager:
    def __init__(self):
        self.configs: Dict[str, GrafanaConfig] = {}
        self.adapters: Dict[str, GrafanaAdapter] = {}
    
    async def add_config(self, config: GrafanaConfig) -> str:
        config_id = config.id or str(uuid.uuid4())
        config.id = config_id
        
        # Create adapter and test connection
        adapter = GrafanaAdapter(config)
        if not await adapter.test_connection():
            raise HTTPException(status_code=400, detail="Grafana connection failed")
        
        self.configs[config_id] = config
        self.adapters[config_id] = adapter
        
        logger.info(f"Added Grafana config {config_id}: {config.name}")
        return config_id
    
    async def get_adapter(self, config_id: str) -> GrafanaAdapter:
        if config_id not in self.adapters:
            raise HTTPException(status_code=404, detail="Grafana configuration not found")
        return self.adapters[config_id]
    
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

# Global Grafana manager
grafana_manager = GrafanaManager()

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Grafana Adapter Service...")
    yield
    logger.info("Shutting down Grafana Adapter Service...")

# Create FastAPI app
app = FastAPI(
    title="BCM Grafana Adapter Service",
    description="Grafana integration for ISO 22301 BCM Platform KPI dashboards",
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
    return {"status": "healthy", "service": "grafana_adapter"}

# Configuration Management
@app.post("/api/grafana/configs")
async def add_grafana_config(config: GrafanaConfig):
    config_id = await grafana_manager.add_config(config)
    return {"config_id": config_id, "status": "configured"}

@app.get("/api/grafana/configs")
async def get_grafana_configs(tenant_id: str):
    configs = [
        config for config in grafana_manager.configs.values()
        if config.tenant_id == tenant_id
    ]
    return {"configs": configs}

# Dashboard Management
@app.get("/api/grafana/{config_id}/dashboards")
async def get_dashboards(config_id: str, folder_id: Optional[int] = None, tag: Optional[str] = None):
    adapter = await grafana_manager.get_adapter(config_id)
    dashboards = await adapter.get_dashboards(folder_id, tag)
    return {"dashboards": dashboards}

@app.get("/api/grafana/{config_id}/dashboards/{dashboard_uid}")
async def get_dashboard(config_id: str, dashboard_uid: str):
    adapter = await grafana_manager.get_adapter(config_id)
    dashboard_data = await adapter.get_dashboard(dashboard_uid)
    return {"dashboard_data": dashboard_data}

@app.post("/api/grafana/{config_id}/dashboards")
async def create_dashboard(
    config_id: str,
    dashboard_data: Dict[str, Any],
    folder_id: Optional[int] = None,
    tenant_id: str = ""
):
    adapter = await grafana_manager.get_adapter(config_id)
    result = await adapter.create_dashboard(dashboard_data, folder_id)
    
    # Publish event
    await grafana_manager.publish_event("grafana.dashboard.created", tenant_id, {
        "config_id": config_id,
        "dashboard_uid": result.get("uid"),
        "dashboard_title": dashboard_data.get("title")
    })
    
    return {"result": result}

@app.put("/api/grafana/{config_id}/dashboards")
async def update_dashboard(
    config_id: str,
    dashboard_data: Dict[str, Any],
    folder_id: Optional[int] = None,
    tenant_id: str = ""
):
    adapter = await grafana_manager.get_adapter(config_id)
    result = await adapter.update_dashboard(dashboard_data, folder_id)
    
    # Publish event
    await grafana_manager.publish_event("grafana.dashboard.updated", tenant_id, {
        "config_id": config_id,
        "dashboard_uid": result.get("uid"),
        "dashboard_title": dashboard_data.get("title")
    })
    
    return {"result": result}

@app.delete("/api/grafana/{config_id}/dashboards/{dashboard_uid}")
async def delete_dashboard(config_id: str, dashboard_uid: str, tenant_id: str = ""):
    adapter = await grafana_manager.get_adapter(config_id)
    success = await adapter.delete_dashboard(dashboard_uid)
    
    if success:
        # Publish event
        await grafana_manager.publish_event("grafana.dashboard.deleted", tenant_id, {
            "config_id": config_id,
            "dashboard_uid": dashboard_uid
        })
    
    return {"success": success}

# Data Source Management
@app.get("/api/grafana/{config_id}/datasources")
async def get_datasources(config_id: str):
    adapter = await grafana_manager.get_adapter(config_id)
    datasources = await adapter.get_datasources()
    return {"datasources": datasources}

@app.post("/api/grafana/{config_id}/datasources")
async def create_datasource(config_id: str, datasource: DataSource, tenant_id: str = ""):
    adapter = await grafana_manager.get_adapter(config_id)
    result = await adapter.create_datasource(datasource)
    
    # Publish event
    await grafana_manager.publish_event("grafana.datasource.created", tenant_id, {
        "config_id": config_id,
        "datasource_name": datasource.name,
        "datasource_type": datasource.type
    })
    
    return {"result": result}

# Annotations
@app.post("/api/grafana/{config_id}/annotations")
async def create_annotation(config_id: str, annotation: Annotation, tenant_id: str = ""):
    adapter = await grafana_manager.get_adapter(config_id)
    result = await adapter.create_annotation(annotation)
    
    # Publish event
    await grafana_manager.publish_event("grafana.annotation.created", tenant_id, {
        "config_id": config_id,
        "annotation_text": annotation.text,
        "tags": annotation.tags
    })
    
    return {"result": result}

# Dashboard URLs and Snapshots
@app.get("/api/grafana/{config_id}/dashboards/{dashboard_uid}/url")
async def get_dashboard_url(
    config_id: str,
    dashboard_uid: str,
    time_from: Optional[datetime] = None,
    time_to: Optional[datetime] = None
):
    adapter = await grafana_manager.get_adapter(config_id)
    url = await adapter.get_dashboard_snapshot_url(dashboard_uid, time_from, time_to)
    return {"url": url}

# BCM Template Dashboards
@app.post("/api/grafana/{config_id}/bcm/overview")
async def create_bcm_overview_dashboard(config_id: str, tenant_id: str):
    """Create BCM overview dashboard from template"""
    adapter = await grafana_manager.get_adapter(config_id)
    dashboard_data = BCMDashboards.create_bcm_overview_dashboard()
    
    result = await adapter.create_dashboard(dashboard_data)
    
    # Publish event
    await grafana_manager.publish_event("grafana.bcm.overview.created", tenant_id, {
        "config_id": config_id,
        "dashboard_uid": result.get("uid")
    })
    
    return {"result": result, "dashboard_type": "BCM Overview"}

@app.post("/api/grafana/{config_id}/bcm/incidents")
async def create_bcm_incident_dashboard(config_id: str, tenant_id: str):
    """Create BCM incident dashboard from template"""
    adapter = await grafana_manager.get_adapter(config_id)
    dashboard_data = BCMDashboards.create_incident_dashboard()
    
    result = await adapter.create_dashboard(dashboard_data)
    
    # Publish event
    await grafana_manager.publish_event("grafana.bcm.incidents.created", tenant_id, {
        "config_id": config_id,
        "dashboard_uid": result.get("uid")
    })
    
    return {"result": result, "dashboard_type": "BCM Incidents"}

# KPI Sync Integration
@app.post("/api/grafana/{config_id}/kpi/sync")
async def sync_bcm_kpis(config_id: str, tenant_id: str, kpi_data: Dict[str, Any]):
    """Sync BCM KPIs to Grafana annotations"""
    adapter = await grafana_manager.get_adapter(config_id)
    
    # Create annotation for KPI update
    annotation = Annotation(
        time=datetime.utcnow(),
        text=f"KPI Update: {kpi_data.get('period', 'Unknown period')}",
        tags=["KPI", "BCM", "Automated"]
    )
    
    result = await adapter.create_annotation(annotation)
    
    # Publish event
    await grafana_manager.publish_event("grafana.kpi.synced", tenant_id, {
        "config_id": config_id,
        "kpi_data": kpi_data,
        "annotation_id": result.get("id")
    })
    
    return {"result": result, "status": "KPIs synced"}

# Mock Data Endpoints for Testing
from mock_data import get_mock_grafana_configs, get_mock_dashboards, get_mock_datasources, get_mock_bcm_kpis, get_mock_incident_metrics, get_mock_training_metrics, get_mock_exercise_metrics, get_mock_dashboard_panels, get_mock_annotations, get_mock_alert_rules

@app.get("/api/grafana/mock/configs")
async def get_mock_grafana_config_data():
    """Get mock Grafana configuration data for testing"""
    return {"mock_configs": get_mock_grafana_configs()}

@app.get("/api/grafana/mock/dashboards")
async def get_mock_dashboard_data():
    """Get mock dashboard data for testing"""
    return {"mock_dashboards": get_mock_dashboards()}

@app.get("/api/grafana/mock/datasources")
async def get_mock_datasource_data():
    """Get mock data source configurations"""
    return {"mock_datasources": get_mock_datasources()}

@app.get("/api/grafana/mock/kpis")
async def get_mock_bcm_kpi_data():
    """Get mock BCM KPI data"""
    return {"bcm_kpis": get_mock_bcm_kpis()}

@app.get("/api/grafana/mock/incident-metrics")
async def get_mock_incident_metric_data():
    """Get mock incident metrics for dashboards"""
    return {"incident_metrics": get_mock_incident_metrics()}

@app.get("/api/grafana/mock/training-metrics")
async def get_mock_training_metric_data():
    """Get mock training metrics"""
    return {"training_metrics": get_mock_training_metrics()}

@app.get("/api/grafana/mock/exercise-metrics")
async def get_mock_exercise_metric_data():
    """Get mock exercise metrics"""
    return {"exercise_metrics": get_mock_exercise_metrics()}

@app.get("/api/grafana/mock/panels")
async def get_mock_panel_data():
    """Get mock dashboard panel configurations"""
    return {"dashboard_panels": get_mock_dashboard_panels()}

@app.get("/api/grafana/mock/annotations")
async def get_mock_annotation_data():
    """Get mock annotations"""
    return {"mock_annotations": get_mock_annotations()}

@app.get("/api/grafana/mock/alert-rules")
async def get_mock_alert_rule_data():
    """Get mock alert rules for BCM monitoring"""
    return {"alert_rules": get_mock_alert_rules()}

@app.post("/api/grafana/mock/setup-demo-config")
async def setup_demo_grafana_config(tenant_id: str):
    """Setup demo Grafana configuration for testing"""
    mock_configs = get_mock_grafana_configs()
    demo_config = mock_configs[0]
    demo_config["tenant_id"] = tenant_id
    
    from main import GrafanaConfig
    config = GrafanaConfig(**demo_config)
    config_id = await grafana_manager.add_config(config)
    
    return {
        "status": "configured",
        "config_id": config_id,
        "description": "Demo Grafana configuration setup"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)