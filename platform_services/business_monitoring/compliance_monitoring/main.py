#!/usr/bin/env python3
"""
ISO 22301 Compliance Monitoring Service
Centralizes ISO 22301 compliance tracking, audit management, and business continuity metrics.

This service focuses on compliance-specific features, not infrastructure monitoring:
- Compliance tracking (audit requirements, RCA analysis, nonconformities)
- ISO 22301 clause mapping and validation
- Custom business metrics (MTPD, RTO, RPO compliance)
- WebSocket for real-time compliance alerts
- Service auto-registration for dynamic discovery

Infrastructure monitoring (health checks, metrics scraping) is handled by Prometheus.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from prometheus_client import make_asgi_app
import httpx
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import os
import json
import aiofiles
from collections import defaultdict, deque
import time
import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Setup logging with structured format for compliance tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s] %(message)s'
)
logger = logging.getLogger("iso22301_compliance_service")

app = FastAPI(
    title="ISO 22301 Compliance API",
    description="ISO 22301 Business Continuity Management System - Compliance tracking, audit management, and service registration",
    version="2.0.0"
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
    # Use local data directory instead of /var/lib (which may not be writable)
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    COMPLIANCE_DATA_DIR = os.getenv("COMPLIANCE_DATA_DIR", os.path.join(PROJECT_ROOT, "data", "compliance"))
    PROMETHEUS_SD_DIR = os.getenv("PROMETHEUS_SD_DIR", os.path.join(PROJECT_ROOT, "infrastructure", "observability", "config", "prometheus", "sd_configs"))
    NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8035")
    ALERT_EMAIL = os.getenv("ALERT_EMAIL", "compliance@bcm.example.com")

    # ISO 22301 Service Registry with Clause Mapping
    # REAL intelligent-core services currently deployed in AI-Platform-ISO
    MONITORED_SERVICES = {
        # INTELLIGENT-CORE Services (Actually deployed)
        "intelligent_core_main": {
            "url": "http://intelligent-core:9000",
            "type": "platform",
            "iso_clauses": ["4.1", "6.1", "8.1"],  # Context, Risk, Operational Planning
            "description": "Intelligent Core Main - Central coordination hub",
            "compliance_critical": True
        },
        "ai_foundation": {
            "url": "http://ai-foundation:8030",
            "type": "ai_foundation",
            "iso_clauses": ["8.3", "9.1"],  # Strategies & Performance Evaluation
            "description": "AI Foundation - RAG, LLM, ML models, embeddings",
            "compliance_critical": True
        },
        "community_intelligence": {
            "url": "http://community-intelligence:8031",
            "type": "intelligence",
            "iso_clauses": ["7.4", "9.1"],  # Communication & Monitoring
            "description": "Community Intelligence - Peer review, reputation, synthesis",
            "compliance_critical": False
        },
        "collective": {
            "url": "http://collective:8032",
            "type": "intelligence",
            "iso_clauses": ["10.2"],  # Continual Improvement
            "description": "Collective Agents - Distributed agent networks, privacy",
            "compliance_critical": False
        },
        "ai_orchestration": {
            "url": "http://ai-orchestration:8002",
            "type": "orchestration",
            "iso_clauses": ["8.3", "8.4"],  # Strategies & Procedures
            "description": "AI Orchestration - Decision making, delegation, memory",
            "compliance_critical": True
        },
        "coordination_center": {
            "url": "http://coordination-center:8004",
            "type": "orchestration",
            "iso_clauses": ["5.3", "8.4.2"],  # Leadership & Incident Response
            "description": "Coordination Center - Execution tracking, task management",
            "compliance_critical": True
        },
        "predictive_service": {
            "url": "http://predictive:8033",
            "type": "intelligence",
            "iso_clauses": ["9.1", "10.2"],  # Performance & Improvement
            "description": "Predictive Service - Journey prediction, proactive recommendations",
            "compliance_critical": False
        },
        "ai_workflow_optimizer": {
            "url": "http://ai-workflow-optimizer:8006",
            "type": "optimization",
            "iso_clauses": ["10.2"],  # Continual Improvement
            "description": "AI Workflow Optimizer - Process optimization engine",
            "compliance_critical": False
        },

        # OBSERVABILITY Services
        "notification_service": {
            "url": "http://notification-service:8035",
            "type": "platform",
            "iso_clauses": ["7.4"],  # Communication
            "description": "Notification Service - Email, Slack, SMS alerts",
            "compliance_critical": True
        },
        "process_analytics": {
            "url": "http://process-analytics:8780",
            "type": "analytics",
            "iso_clauses": ["9.1", "9.3"],  # Performance & Management Review
            "description": "Process Analytics - Process mining, bottleneck detection",
            "compliance_critical": False
        },
        "compliance_monitoring": {
            "url": "http://compliance-monitoring:8779",
            "type": "compliance",
            "iso_clauses": ["9.2", "10.1"],  # Audit & Nonconformity
            "description": "ISO 22301 Compliance Monitoring - This service",
            "compliance_critical": True
        },
    }

# ==================== MODELS ====================

class ComplianceAlert(BaseModel):
    """ISO 22301 compliance-specific alert"""
    id: str
    service: str
    severity: str  # low, medium, high, critical
    title: str
    description: str
    iso_clauses: List[str]  # Affected ISO clauses
    compliance_impact: str  # Compliance impact assessment
    timestamp: datetime = datetime.now()
    status: str = "active"  # active, acknowledged, resolved
    resolved_at: Optional[datetime] = None
    remediation_plan: Optional[str] = None

class NonconformityRecord(BaseModel):
    """ISO 22301 Nonconformity (Clause 10.1)"""
    id: str
    service: str
    iso_clause: str
    description: str
    severity: str  # minor, major, critical
    detected_at: datetime = datetime.now()
    root_cause_analysis: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    status: str = "open"  # open, in_progress, resolved, verified
    resolved_at: Optional[datetime] = None
    verified_by: Optional[str] = None

class AuditRequirement(BaseModel):
    """ISO 22301 Audit Requirement (Clause 9.2)"""
    id: str
    iso_clause: str
    requirement_text: str
    service: str
    compliance_status: str  # compliant, non_compliant, partial, not_applicable
    evidence: Optional[str] = None
    last_audit: Optional[datetime] = None
    next_audit: Optional[datetime] = None
    auditor_notes: Optional[str] = None

class ServiceRegistration(BaseModel):
    """Service registration for auto-discovery"""
    name: str
    url: str
    type: str  # bcm, platform, gateway, intelligence, analytics
    iso_clauses: List[str]
    description: str
    compliance_critical: bool = False
    metrics_endpoint: str = "/metrics"
    health_endpoint: str = "/health"
    custom_metrics: Optional[List[str]] = None

class ComplianceMetrics(BaseModel):
    """ISO 22301 Business Continuity Metrics"""
    service: str
    timestamp: datetime = datetime.now()
    rto_compliance: Optional[float] = None  # % of services meeting RTO
    rpo_compliance: Optional[float] = None  # % of services meeting RPO
    mtpd_compliance: Optional[float] = None  # % of processes meeting MTPD
    test_coverage: Optional[float] = None  # % of plans tested
    audit_score: Optional[float] = None  # Latest audit score
    nonconformities_count: Optional[int] = None
    custom_metrics: Optional[Dict[str, Any]] = None

class ComplianceStatus(BaseModel):
    """Overall ISO 22301 compliance status"""
    overall_compliance: str  # compliant, partial, non_compliant
    compliance_score: float  # 0-100
    critical_services_status: str
    total_services: int
    compliant_services: int
    services_with_issues: int
    active_nonconformities: int
    open_audit_findings: int
    last_audit_date: Optional[datetime]
    next_audit_date: Optional[datetime]
    last_updated: datetime

# ==================== STORAGE ====================

class ComplianceStorage:
    """In-memory storage for ISO 22301 compliance data"""

    def __init__(self):
        self.alerts = {}  # compliance alerts
        self.nonconformities = {}  # nonconformity records
        self.audit_requirements = {}  # audit requirements tracking
        self.compliance_metrics = defaultdict(lambda: deque(maxlen=1440))  # 24h of data
        self.connected_websockets = set()
        self.service_registry = dict(Config.MONITORED_SERVICES)  # Dynamic registry

        logger.info("ISO 22301 Compliance Storage initialized")

    def add_alert(self, alert: ComplianceAlert):
        """Add compliance alert and broadcast"""
        self.alerts[alert.id] = alert
        asyncio.create_task(self._broadcast_alert(alert))
        asyncio.create_task(self._send_alert_notification(alert))
        logger.warning(
            f"Compliance Alert: {alert.title} | Service: {alert.service} | "
            f"ISO Clauses: {', '.join(alert.iso_clauses)} | Severity: {alert.severity}"
        )

    def add_nonconformity(self, nonconformity: NonconformityRecord):
        """Record ISO 22301 nonconformity (Clause 10.1)"""
        self.nonconformities[nonconformity.id] = nonconformity
        logger.error(
            f"Nonconformity Detected: {nonconformity.description} | "
            f"Service: {nonconformity.service} | ISO Clause: {nonconformity.iso_clause} | "
            f"Severity: {nonconformity.severity}"
        )

    def add_compliance_metrics(self, metrics: ComplianceMetrics):
        """Record compliance metrics"""
        self.compliance_metrics[metrics.service].append(metrics)
        logger.info(
            f"Compliance Metrics Updated: {metrics.service} | "
            f"RTO: {metrics.rto_compliance}% | RPO: {metrics.rpo_compliance}% | "
            f"MTPD: {metrics.mtpd_compliance}%"
        )

    async def _broadcast_alert(self, alert: ComplianceAlert):
        """Broadcast alert to WebSocket clients"""
        if self.connected_websockets:
            message = {
                "type": "compliance_alert",
                "data": alert.dict()
            }
            disconnected = set()
            for websocket in self.connected_websockets:
                try:
                    await websocket.send_text(json.dumps(message, default=str))
                except:
                    disconnected.add(websocket)
            self.connected_websockets -= disconnected

    async def _send_alert_notification(self, alert: ComplianceAlert):
        """Send compliance alert via notification service"""
        if not Config.NOTIFICATION_SERVICE_URL or alert.severity == "low":
            return

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{Config.NOTIFICATION_SERVICE_URL}/email/send",
                    json={
                        "to": [Config.ALERT_EMAIL],
                        "subject": f"[ISO 22301 COMPLIANCE] {alert.severity.upper()}: {alert.title}",
                        "body": f"""
ISO 22301 Compliance Alert

Service: {alert.service}
Severity: {alert.severity}
Title: {alert.title}
Description: {alert.description}

ISO 22301 Clauses Affected: {', '.join(alert.iso_clauses)}
Compliance Impact: {alert.compliance_impact}

Timestamp: {alert.timestamp.isoformat()}

This is an automated compliance alert from ISO 22301 Compliance Service.
Action may be required to maintain compliance.
                        """
                    }
                )
                logger.info(f"Compliance alert notification sent: {alert.id}")
        except Exception as e:
            logger.error(f"Failed to send compliance alert notification: {e}")

    def register_service(self, registration: ServiceRegistration):
        """Register new service in the catalog"""
        self.service_registry[registration.name] = {
            "url": registration.url,
            "type": registration.type,
            "iso_clauses": registration.iso_clauses,
            "description": registration.description,
            "compliance_critical": registration.compliance_critical,
            "metrics_endpoint": registration.metrics_endpoint,
            "health_endpoint": registration.health_endpoint,
            "custom_metrics": registration.custom_metrics or []
        }
        logger.info(
            f"Service Registered: {registration.name} | "
            f"ISO Clauses: {', '.join(registration.iso_clauses)} | "
            f"Critical: {registration.compliance_critical}"
        )

    def deregister_service(self, service_name: str):
        """Remove service from catalog"""
        if service_name in self.service_registry:
            del self.service_registry[service_name]
            logger.info(f"Service Deregistered: {service_name}")

    async def save_to_disk(self):
        """Save compliance data to disk for persistence"""
        try:
            # Prepare data snapshot
            data = {
                'alerts': {k: v.dict() for k, v in self.alerts.items()},
                'nonconformities': {k: v.dict() for k, v in self.nonconformities.items()},
                'audit_requirements': {k: v.dict() for k, v in self.audit_requirements.items()},
                'service_registry': self.service_registry,
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            }

            # Save daily snapshot
            snapshot_file = os.path.join(
                Config.COMPLIANCE_DATA_DIR,
                'backups',
                f'compliance_snapshot_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.json'
            )

            async with aiofiles.open(snapshot_file, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))

            # Save as "latest" for easy loading
            latest_file = os.path.join(Config.COMPLIANCE_DATA_DIR, 'backups', 'latest.json')
            async with aiofiles.open(latest_file, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))

            logger.info(f" Compliance data saved to {snapshot_file}")

        except Exception as e:
            logger.error(f"Failed to save compliance data: {e}")

    async def load_from_disk(self):
        """Load compliance data from disk on startup"""
        try:
            latest_file = os.path.join(Config.COMPLIANCE_DATA_DIR, 'backups', 'latest.json')

            if not os.path.exists(latest_file):
                logger.info("No previous compliance data found (first run)")
                return

            async with aiofiles.open(latest_file, 'r') as f:
                data = json.loads(await f.read())

            # Restore alerts
            for alert_id, alert_data in data.get('alerts', {}).items():
                # Convert ISO strings back to datetime
                if 'timestamp' in alert_data:
                    alert_data['timestamp'] = datetime.fromisoformat(alert_data['timestamp'])
                if 'resolved_at' in alert_data and alert_data['resolved_at']:
                    alert_data['resolved_at'] = datetime.fromisoformat(alert_data['resolved_at'])

                self.alerts[alert_id] = ComplianceAlert(**alert_data)

            # Restore nonconformities
            for nc_id, nc_data in data.get('nonconformities', {}).items():
                if 'detected_at' in nc_data:
                    nc_data['detected_at'] = datetime.fromisoformat(nc_data['detected_at'])
                if 'resolved_at' in nc_data and nc_data['resolved_at']:
                    nc_data['resolved_at'] = datetime.fromisoformat(nc_data['resolved_at'])

                self.nonconformities[nc_id] = NonconformityRecord(**nc_data)

            # Restore audit requirements
            for audit_id, audit_data in data.get('audit_requirements', {}).items():
                if 'last_audit' in audit_data and audit_data['last_audit']:
                    audit_data['last_audit'] = datetime.fromisoformat(audit_data['last_audit'])
                if 'next_audit' in audit_data and audit_data['next_audit']:
                    audit_data['next_audit'] = datetime.fromisoformat(audit_data['next_audit'])

                self.audit_requirements[audit_id] = AuditRequirement(**audit_data)

            logger.info(f" Compliance data loaded: {len(self.alerts)} alerts, {len(self.nonconformities)} nonconformities")

        except Exception as e:
            logger.error(f"Failed to load compliance data: {e}")

# Global storage instance
storage = ComplianceStorage()

# ==================== AUTOMATION TOOLKIT INTEGRATION ====================

# Import Automation Toolkit integration
try:
    import sys
    sys.path.insert(0, str(os.path.join(os.path.dirname(__file__), 'integrations')))
    from automation_toolkit import AutomationToolkitIntegration

    toolkit = AutomationToolkitIntegration()
    logger.info(" Automation Toolkit integration loaded")
except ImportError as e:
    toolkit = None
    logger.warning(f"️  Automation Toolkit not available: {e}")

# Setup scheduler for automated jobs
scheduler = AsyncIOScheduler()

# ==================== STARTUP / SHUTDOWN ====================

start_time = time.time()

@app.on_event("startup")
async def startup_event():
    """Initialize compliance service on startup"""
    # Create required directories
    os.makedirs(Config.COMPLIANCE_DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(Config.COMPLIANCE_DATA_DIR, 'alerts'), exist_ok=True)
    os.makedirs(os.path.join(Config.COMPLIANCE_DATA_DIR, 'nonconformities'), exist_ok=True)
    os.makedirs(os.path.join(Config.COMPLIANCE_DATA_DIR, 'audits'), exist_ok=True)
    os.makedirs(os.path.join(Config.COMPLIANCE_DATA_DIR, 'metrics'), exist_ok=True)
    os.makedirs(os.path.join(Config.COMPLIANCE_DATA_DIR, 'backups'), exist_ok=True)
    os.makedirs(os.path.join(Config.COMPLIANCE_DATA_DIR, 'automation'), exist_ok=True)
    os.makedirs(Config.PROMETHEUS_SD_DIR, exist_ok=True)

    logger.info("ISO 22301 Compliance Service started successfully")
    logger.info(f" Compliance data directory: {Config.COMPLIANCE_DATA_DIR}")
    logger.info(f" Prometheus SD directory: {Config.PROMETHEUS_SD_DIR}")

    # Load previous compliance data
    await storage.load_from_disk()

    logger.info(f"Monitoring {len(storage.service_registry)} BCM services for compliance")

    # Start automated jobs if toolkit is available
    if toolkit:
        scheduler.start()
        logger.info(" Automation Toolkit scheduler started")

        # Add daily backup job
        @scheduler.scheduled_job('cron', hour=3, minute=0, id='daily_backup')
        async def job_daily_backup():
            """Save compliance data snapshot daily at 3 AM"""
            try:
                logger.info(" Running daily compliance data backup...")
                await storage.save_to_disk()
                logger.info(" Daily backup complete")
            except Exception as e:
                logger.error(f" Daily backup failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Automation Toolkit scheduler stopped")
    logger.info("ISO 22301 Compliance Service shutting down")

# ==================== CORE ENDPOINTS ====================

@app.get("/health")
async def health_check():
    """Health check for compliance service itself"""
    return {
        "status": "healthy",
        "service": "iso22301_compliance_service",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": time.time() - start_time,
        "registered_services": len(storage.service_registry)
    }

# ==================== COMPLIANCE ENDPOINTS ====================

@app.get("/compliance/status", response_model=ComplianceStatus)
async def get_compliance_status():
    """Get overall ISO 22301 compliance status"""
    services = storage.service_registry
    critical_services = {k: v for k, v in services.items() if v.get("compliance_critical", False)}

    # Calculate compliance metrics
    total_services = len(services)
    compliant_services = total_services - len([a for a in storage.alerts.values() if a.status == "active"])
    services_with_issues = len([a for a in storage.alerts.values() if a.status == "active"])

    active_nonconformities = len([n for n in storage.nonconformities.values() if n.status != "resolved"])
    open_audit_findings = len([a for a in storage.audit_requirements.values()
                                if a.compliance_status in ["non_compliant", "partial"]])

    # Calculate overall compliance score
    compliance_score = 100.0
    if total_services > 0:
        compliance_score = (compliant_services / total_services) * 100

    # Adjust for nonconformities and audit findings
    compliance_score -= (active_nonconformities * 2)  # -2% per nonconformity
    compliance_score -= (open_audit_findings * 1)  # -1% per audit finding
    compliance_score = max(0, min(100, compliance_score))

    # Determine overall compliance status
    if compliance_score >= 90:
        overall_compliance = "compliant"
    elif compliance_score >= 70:
        overall_compliance = "partial"
    else:
        overall_compliance = "non_compliant"

    # Critical services status
    critical_issues = sum(1 for a in storage.alerts.values()
                         if a.status == "active" and a.service in critical_services)
    if critical_issues == 0:
        critical_services_status = "compliant"
    elif critical_issues <= 2:
        critical_services_status = "partial"
    else:
        critical_services_status = "non_compliant"

    return ComplianceStatus(
        overall_compliance=overall_compliance,
        compliance_score=round(compliance_score, 2),
        critical_services_status=critical_services_status,
        total_services=total_services,
        compliant_services=compliant_services,
        services_with_issues=services_with_issues,
        active_nonconformities=active_nonconformities,
        open_audit_findings=open_audit_findings,
        last_audit_date=None,  # TODO: Track from audit service
        next_audit_date=None,  # TODO: Track from audit service
        last_updated=datetime.now()
    )

@app.get("/compliance/iso-clauses")
async def get_iso_clause_coverage():
    """Get ISO 22301 clause coverage by services"""
    clause_map = defaultdict(list)

    for service_name, service_info in storage.service_registry.items():
        for clause in service_info.get("iso_clauses", []):
            clause_map[clause].append({
                "service": service_name,
                "type": service_info.get("type"),
                "critical": service_info.get("compliance_critical", False),
                "description": service_info.get("description")
            })

    return {
        "total_clauses_covered": len(clause_map),
        "clause_coverage": dict(clause_map),
        "uncovered_clauses": []  # TODO: Add complete ISO 22301 clause list validation
    }

@app.get("/compliance/services")
async def get_compliance_services():
    """Get all registered services with ISO compliance mapping"""
    return {
        "total_services": len(storage.service_registry),
        "services": storage.service_registry
    }

@app.get("/compliance/alerts")
async def get_compliance_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    service: Optional[str] = None
):
    """Get compliance alerts with filtering"""
    alerts = list(storage.alerts.values())

    if status:
        alerts = [a for a in alerts if a.status == status]
    if severity:
        alerts = [a for a in alerts if a.severity == severity]
    if service:
        alerts = [a for a in alerts if a.service == service]

    alerts.sort(key=lambda x: x.timestamp, reverse=True)
    return {
        "total": len(alerts),
        "alerts": [a.dict() for a in alerts]
    }

@app.post("/compliance/alerts")
async def create_compliance_alert(alert: ComplianceAlert):
    """Create new compliance alert"""
    storage.add_alert(alert)
    return {"status": "created", "alert_id": alert.id}

@app.put("/compliance/alerts/{alert_id}/acknowledge")
async def acknowledge_compliance_alert(alert_id: str):
    """Acknowledge compliance alert"""
    if alert_id not in storage.alerts:
        raise HTTPException(status_code=404, detail="Alert not found")

    storage.alerts[alert_id].status = "acknowledged"
    logger.info(f"Compliance alert acknowledged: {alert_id}")
    return {"status": "acknowledged"}

@app.put("/compliance/alerts/{alert_id}/resolve")
async def resolve_compliance_alert(alert_id: str, remediation_plan: Optional[str] = None):
    """Resolve compliance alert"""
    if alert_id not in storage.alerts:
        raise HTTPException(status_code=404, detail="Alert not found")

    storage.alerts[alert_id].status = "resolved"
    storage.alerts[alert_id].resolved_at = datetime.now()
    if remediation_plan:
        storage.alerts[alert_id].remediation_plan = remediation_plan

    logger.info(f"Compliance alert resolved: {alert_id}")
    return {"status": "resolved"}

# ==================== NONCONFORMITY MANAGEMENT (ISO 10.1) ====================

@app.get("/compliance/nonconformities")
async def get_nonconformities(
    status: Optional[str] = None,
    service: Optional[str] = None,
    iso_clause: Optional[str] = None
):
    """Get nonconformity records"""
    records = list(storage.nonconformities.values())

    if status:
        records = [r for r in records if r.status == status]
    if service:
        records = [r for r in records if r.service == service]
    if iso_clause:
        records = [r for r in records if r.iso_clause == iso_clause]

    records.sort(key=lambda x: x.detected_at, reverse=True)
    return {
        "total": len(records),
        "nonconformities": [r.dict() for r in records]
    }

@app.post("/compliance/nonconformities")
async def create_nonconformity(nonconformity: NonconformityRecord):
    """Create nonconformity record (ISO 22301 Clause 10.1)"""
    storage.add_nonconformity(nonconformity)
    return {"status": "created", "nonconformity_id": nonconformity.id}

@app.put("/compliance/nonconformities/{nonconformity_id}")
async def update_nonconformity(
    nonconformity_id: str,
    root_cause_analysis: Optional[str] = None,
    corrective_action: Optional[str] = None,
    preventive_action: Optional[str] = None,
    status: Optional[str] = None
):
    """Update nonconformity with RCA and corrective actions"""
    if nonconformity_id not in storage.nonconformities:
        raise HTTPException(status_code=404, detail="Nonconformity not found")

    record = storage.nonconformities[nonconformity_id]

    if root_cause_analysis:
        record.root_cause_analysis = root_cause_analysis
    if corrective_action:
        record.corrective_action = corrective_action
    if preventive_action:
        record.preventive_action = preventive_action
    if status:
        record.status = status
        if status == "resolved":
            record.resolved_at = datetime.now()

    logger.info(f"Nonconformity updated: {nonconformity_id} | Status: {status}")
    return {"status": "updated", "nonconformity": record.dict()}

# ==================== AUDIT MANAGEMENT (ISO 9.2) ====================

@app.get("/compliance/audit-requirements")
async def get_audit_requirements(
    iso_clause: Optional[str] = None,
    compliance_status: Optional[str] = None
):
    """Get audit requirements tracking"""
    requirements = list(storage.audit_requirements.values())

    if iso_clause:
        requirements = [r for r in requirements if r.iso_clause == iso_clause]
    if compliance_status:
        requirements = [r for r in requirements if r.compliance_status == compliance_status]

    return {
        "total": len(requirements),
        "requirements": [r.dict() for r in requirements]
    }

@app.post("/compliance/audit-requirements")
async def create_audit_requirement(requirement: AuditRequirement):
    """Create audit requirement tracking"""
    storage.audit_requirements[requirement.id] = requirement
    logger.info(f"Audit requirement created: {requirement.iso_clause} | Service: {requirement.service}")
    return {"status": "created", "requirement_id": requirement.id}

# ==================== COMPLIANCE METRICS ====================

@app.post("/compliance/metrics")
async def ingest_compliance_metrics(metrics: ComplianceMetrics):
    """Ingest compliance metrics (RTO, RPO, MTPD, etc.)"""
    storage.add_compliance_metrics(metrics)
    return {"status": "recorded"}

@app.get("/compliance/metrics/{service}")
async def get_service_compliance_metrics(service: str, hours: int = 24):
    """Get compliance metrics for specific service"""
    if service not in storage.compliance_metrics:
        raise HTTPException(status_code=404, detail="Service not found")

    cutoff_time = datetime.now() - timedelta(hours=hours)
    metrics = [
        m for m in storage.compliance_metrics[service]
        if m.timestamp >= cutoff_time
    ]

    return {
        "service": service,
        "timeframe_hours": hours,
        "metrics": [m.dict() for m in metrics]
    }

# ==================== SERVICE AUTO-REGISTRATION ====================

@app.post("/register-service")
async def register_service(registration: ServiceRegistration):
    """
    Register new BCM service for compliance monitoring and Prometheus scraping.
    Creates service discovery config for Prometheus.
    """
    # Register in catalog
    storage.register_service(registration)

    # Create Prometheus service discovery file
    sd_config = [{
        "targets": [registration.url.replace("http://", "").replace("https://", "")],
        "labels": {
            "job": registration.name,
            "service_type": registration.type,
            "iso_clauses": ",".join(registration.iso_clauses),
            "compliance_critical": str(registration.compliance_critical).lower(),
            "__metrics_path__": registration.metrics_endpoint
        }
    }]

    sd_file_path = f"{Config.PROMETHEUS_SD_DIR}/{registration.name}.json"

    try:
        async with aiofiles.open(sd_file_path, "w") as f:
            await f.write(json.dumps(sd_config, indent=2))

        logger.info(f"Prometheus SD config created: {sd_file_path}")

        return {
            "status": "registered",
            "service": registration.name,
            "prometheus_sd_file": sd_file_path,
            "iso_clauses": registration.iso_clauses,
            "message": "Service registered successfully. Prometheus will discover it automatically."
        }
    except Exception as e:
        logger.error(f"Failed to create Prometheus SD config: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Service registered but Prometheus SD config creation failed: {str(e)}"
        )

@app.delete("/deregister-service/{service_name}")
async def deregister_service(service_name: str):
    """
    Deregister service from compliance monitoring.
    Removes Prometheus service discovery config.
    """
    if service_name not in storage.service_registry:
        raise HTTPException(status_code=404, detail="Service not found")

    # Remove from catalog
    storage.deregister_service(service_name)

    # Remove Prometheus SD file
    sd_file_path = f"{Config.PROMETHEUS_SD_DIR}/{service_name}.json"

    try:
        if os.path.exists(sd_file_path):
            os.remove(sd_file_path)
            logger.info(f"Prometheus SD config removed: {sd_file_path}")
    except Exception as e:
        logger.error(f"Failed to remove Prometheus SD config: {e}")

    return {
        "status": "deregistered",
        "service": service_name,
        "message": "Service deregistered successfully"
    }

# ==================== AUTOMATION TOOLKIT API ENDPOINTS ====================

@app.post("/automation/discover-services")
async def automation_discover_services():
    """
    Auto-discover all services using AST analysis.
    Finds services with /health and /metrics endpoints.
    """
    if not toolkit:
        raise HTTPException(status_code=503, detail="Automation Toolkit not available")

    return await toolkit.discover_services()


@app.post("/automation/auto-register-services")
async def automation_auto_register():
    """
    Auto-discover and register all services with Prometheus.
    This is the main auto-discovery endpoint.
    """
    if not toolkit:
        raise HTTPException(status_code=503, detail="Automation Toolkit not available")

    return await toolkit.register_discovered_services()


@app.get("/automation/dependencies/{service_name}")
async def automation_get_dependencies(service_name: str):
    """
    Get dependency map for a service.
    Used for root cause analysis.
    """
    if not toolkit:
        raise HTTPException(status_code=503, detail="Automation Toolkit not available")

    return await toolkit.analyze_dependencies(service_name)


@app.post("/automation/root-cause/{failed_service}")
async def automation_find_root_cause(failed_service: str):
    """
    Find root cause of service failure by analyzing dependencies.
    Checks Prometheus metrics for all dependencies.
    """
    if not toolkit:
        raise HTTPException(status_code=503, detail="Automation Toolkit not available")

    return await toolkit.find_root_cause(failed_service)


@app.post("/automation/security-scan")
async def automation_security_scan():
    """
    Run Bandit security scan on all services.
    Returns OWASP Top 10 security issues.
    """
    if not toolkit:
        raise HTTPException(status_code=503, detail="Automation Toolkit not available")

    return await toolkit.run_security_scan()


@app.get("/automation/code-complexity/{service_name}")
async def automation_code_complexity(service_name: str):
    """
    Analyze code complexity using Radon.
    Returns cyclomatic complexity metrics.
    """
    if not toolkit:
        raise HTTPException(status_code=503, detail="Automation Toolkit not available")

    return await toolkit.analyze_code_complexity(service_name)


@app.get("/automation/metrics")
async def automation_prometheus_metrics():
    """
    Export Automation Toolkit metrics in Prometheus format.
    """
    if not toolkit:
        raise HTTPException(status_code=503, detail="Automation Toolkit not available")

    # Get latest metrics
    discovery = await toolkit.discover_services()
    security = await toolkit.run_security_scan()
    complexity = await toolkit.analyze_code_complexity()

    metrics = toolkit.export_prometheus_metrics(discovery, security, complexity)

    return HTMLResponse(content=metrics, media_type="text/plain")


# ==================== AUTOMATED JOBS (CRON) ====================

if toolkit:
    # Job 1: Auto-discovery every 5 minutes
    @scheduler.scheduled_job('interval', minutes=5, id='auto_discover')
    async def job_auto_discover():
        """Auto-discover new services every 5 minutes"""
        try:
            logger.info(" Running automated service discovery...")
            results = await toolkit.discover_services()

            # Save results to disk
            result_file = os.path.join(
                Config.COMPLIANCE_DATA_DIR,
                'automation',
                f'service_discovery_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.json'
            )
            async with aiofiles.open(result_file, 'w') as f:
                await f.write(json.dumps(results, indent=2, default=str))

            if 'coverage' in results:
                coverage = results['coverage']['percentage']
                logger.info(f" Service discovery complete: {coverage:.1f}% coverage")

                # Auto-register if new services found
                if coverage < 100:
                    logger.info(" Auto-registering discovered services...")
                    await toolkit.register_discovered_services()

        except Exception as e:
            logger.error(f" Auto-discovery job failed: {e}")


    # Job 2: Security scan every hour
    @scheduler.scheduled_job('interval', hours=1, id='security_scan')
    async def job_security_scan():
        """Run security scan every hour"""
        try:
            logger.info(" Running hourly security scan...")
            results = await toolkit.run_security_scan()

            # Save results to disk
            result_file = os.path.join(
                Config.COMPLIANCE_DATA_DIR,
                'automation',
                f'security_scan_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.json'
            )
            async with aiofiles.open(result_file, 'w') as f:
                await f.write(json.dumps(results, indent=2, default=str))

            if results.get('status') == 'issues_found':
                high = results.get('high_severity', 0)
                medium = results.get('medium_severity', 0)

                logger.warning(f"️  Security issues: HIGH={high}, MEDIUM={medium}")

                # Create compliance alert if HIGH issues found
                if high > 0:
                    alert = ComplianceAlert(
                        id=f"security_{int(time.time())}",
                        service="platform",
                        severity="high",
                        title=f"{high} HIGH severity security issues detected",
                        description=f"Bandit scan found {high} HIGH and {medium} MEDIUM severity issues",
                        iso_clauses=["A.12.6.1"],  # ISO 27001 Security
                        compliance_impact="Security vulnerability compliance risk"
                    )
                    storage.add_alert(alert)

        except Exception as e:
            logger.error(f" Security scan job failed: {e}")


    # Job 3: Code complexity analysis daily at 2 AM
    @scheduler.scheduled_job('cron', hour=2, minute=0, id='complexity_analysis')
    async def job_complexity_analysis():
        """Run code complexity analysis daily"""
        try:
            logger.info(" Running daily code complexity analysis...")
            results = await toolkit.analyze_code_complexity()

            # Save results to disk
            result_file = os.path.join(
                Config.COMPLIANCE_DATA_DIR,
                'automation',
                f'complexity_analysis_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.json'
            )
            async with aiofiles.open(result_file, 'w') as f:
                await f.write(json.dumps(results, indent=2, default=str))

            if 'avg_complexity' in results:
                avg = results['avg_complexity']
                high_funcs = len(results.get('high_complexity_functions', []))

                logger.info(f" Complexity: avg={avg:.1f}, high_complexity_functions={high_funcs}")

                # Alert if average complexity is too high
                if avg > 10:
                    alert = ComplianceAlert(
                        id=f"complexity_{int(time.time())}",
                        service="platform",
                        severity="warning",
                        title=f"Code complexity above threshold: {avg:.1f}",
                        description=f"Average cyclomatic complexity is {avg:.1f} (threshold: 10). {high_funcs} high-complexity functions detected.",
                        iso_clauses=["7.1"],  # ISO 22301 Resources
                        compliance_impact="Code maintainability risk"
                    )
                    storage.add_alert(alert)

        except Exception as e:
            logger.error(f" Complexity analysis job failed: {e}")


    logger.info(" Automated jobs configured:")
    logger.info("  - Service discovery: every 5 minutes")
    logger.info("  - Security scan: every hour")
    logger.info("  - Complexity analysis: daily at 2 AM")

# ==================== WEBSOCKET ====================

@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time compliance alerts"""
    await websocket.accept()
    storage.connected_websockets.add(websocket)
    logger.info("WebSocket client connected")

    try:
        while True:
            # Keep connection alive and allow client to send heartbeat
            await websocket.receive_text()
    except WebSocketDisconnect:
        storage.connected_websockets.discard(websocket)
        logger.info("WebSocket client disconnected")

# ==================== DASHBOARD ====================

@app.get("/dashboard")
async def get_compliance_dashboard():
    """ISO 22301 Compliance Dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ISO 22301 Compliance Dashboard</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container { max-width: 1400px; margin: 0 auto; }
            h1 { color: white; margin-bottom: 10px; }
            .subtitle { color: rgba(255,255,255,0.9); margin-bottom: 30px; }
            .status-compliant { color: #28a745; font-weight: bold; }
            .status-partial { color: #ffc107; font-weight: bold; }
            .status-non_compliant { color: #dc3545; font-weight: bold; }
            .card {
                background: white;
                border-radius: 12px;
                margin: 15px 0;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            .metric-card h3 { margin: 0 0 10px 0; font-size: 16px; opacity: 0.9; }
            .metric-card .value { font-size: 36px; font-weight: bold; margin: 10px 0; }
            .metric-card .label { font-size: 14px; opacity: 0.8; }
            .header {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                color: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 20px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            .header h1 { margin: 0; font-size: 32px; }
            .service-list {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 15px;
            }
            .service-item {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #007bff;
            }
            .service-item.critical { border-left-color: #dc3545; }
            .service-item h4 { margin: 0 0 8px 0; color: #333; }
            .service-item p { margin: 5px 0; font-size: 13px; color: #666; }
            .iso-clause {
                display: inline-block;
                background: #007bff;
                color: white;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 11px;
                margin-right: 5px;
                margin-top: 5px;
            }
            a { color: #667eea; text-decoration: none; font-weight: 500; }
            a:hover { text-decoration: underline; }
        </style>
        <script>
            async function loadDashboard() {
                try {
                    // Load compliance status
                    const statusResponse = await fetch('/compliance/status');
                    const status = await statusResponse.json();

                    document.getElementById('compliance-score').textContent = status.compliance_score.toFixed(1) + '%';
                    document.getElementById('overall-status').textContent = status.overall_compliance.toUpperCase();
                    document.getElementById('overall-status').className = 'status-' + status.overall_compliance;

                    document.getElementById('total-services').textContent = status.total_services;
                    document.getElementById('compliant-services').textContent = status.compliant_services;
                    document.getElementById('active-nonconformities').textContent = status.active_nonconformities;
                    document.getElementById('audit-findings').textContent = status.open_audit_findings;

                    // Load services
                    const servicesResponse = await fetch('/compliance/services');
                    const servicesData = await servicesResponse.json();

                    let servicesHtml = '';
                    for (const [name, info] of Object.entries(servicesData.services)) {
                        const criticalClass = info.compliance_critical ? 'critical' : '';
                        const clausesHtml = info.iso_clauses.map(c =>
                            `<span class="iso-clause">${c}</span>`
                        ).join('');

                        servicesHtml += `
                            <div class="service-item ${criticalClass}">
                                <h4>${name.replace(/_/g, ' ').toUpperCase()}</h4>
                                <p><strong>Type:</strong> ${info.type}</p>
                                <p><strong>ISO Clauses:</strong><br>${clausesHtml}</p>
                                <p>${info.description}</p>
                                ${info.compliance_critical ? '<p style="color: #dc3545; font-weight: bold;"> COMPLIANCE CRITICAL</p>' : ''}
                            </div>
                        `;
                    }
                    document.getElementById('services-list').innerHTML = servicesHtml;

                } catch (error) {
                    console.error('Error loading dashboard:', error);
                }
            }

            window.onload = loadDashboard;
            setInterval(loadDashboard, 60000);  // Refresh every minute
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>ISO 22301 Compliance Dashboard</h1>
                <p class="subtitle">Business Continuity Management System - Real-time Compliance Monitoring</p>
            </div>

            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>COMPLIANCE SCORE</h3>
                    <div class="value" id="compliance-score">--</div>
                    <div class="label">Overall Compliance</div>
                </div>
                <div class="metric-card">
                    <h3>STATUS</h3>
                    <div class="value" id="overall-status" style="font-size: 24px;">--</div>
                    <div class="label">Compliance Status</div>
                </div>
                <div class="metric-card">
                    <h3>SERVICES</h3>
                    <div class="value"><span id="compliant-services">--</span>/<span id="total-services">--</span></div>
                    <div class="label">Compliant Services</div>
                </div>
                <div class="metric-card">
                    <h3>NONCONFORMITIES</h3>
                    <div class="value" id="active-nonconformities">--</div>
                    <div class="label">Active Issues (Clause 10.1)</div>
                </div>
                <div class="metric-card">
                    <h3>AUDIT FINDINGS</h3>
                    <div class="value" id="audit-findings">--</div>
                    <div class="label">Open Findings (Clause 9.2)</div>
                </div>
            </div>

            <div class="card">
                <h2>Registered BCM Services</h2>
                <div class="service-list" id="services-list">
                    Loading...
                </div>
            </div>

            <div class="card">
                <h3>API Endpoints</h3>
                <p><a href="/compliance/status" target="_blank">Compliance Status</a></p>
                <p><a href="/compliance/iso-clauses" target="_blank">ISO 22301 Clause Coverage</a></p>
                <p><a href="/compliance/services" target="_blank">Service Registry</a></p>
                <p><a href="/compliance/alerts" target="_blank">Compliance Alerts</a></p>
                <p><a href="/compliance/nonconformities" target="_blank">Nonconformities (Clause 10.1)</a></p>
                <p><a href="/compliance/audit-requirements" target="_blank">Audit Requirements (Clause 9.2)</a></p>
                <p><a href="/docs" target="_blank">Full API Documentation</a></p>
            </div>

            <div class="card" style="background: #f8f9fa; font-size: 12px; color: #666;">
                <p>Auto-refresh: Every 60 seconds | ISO 22301:2019 Compliance API v2.0.0</p>
                <p>Infrastructure monitoring (health checks, metrics) handled by Prometheus</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ============================================================================
# PROMETHEUS METRICS ENDPOINT
# ============================================================================

# Mount Prometheus metrics endpoint for infrastructure monitoring
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8779"))
    logger.info(f"Starting ISO 22301 Compliance Service on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
