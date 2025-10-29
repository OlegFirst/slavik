"""
Governance Service for BCM Platform
Manages data retention, quotas, backup policies, and system governance
"""

import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from enum import Enum
import logging
import json
import os
import shutil

logger = logging.getLogger(__name__)


class RetentionPolicy(str, Enum):
    SHORT_TERM = "short_term"  # 30 days
    MEDIUM_TERM = "medium_term"  # 1 year
    LONG_TERM = "long_term"  # 7 years
    PERMANENT = "permanent"


class DataCategory(str, Enum):
    INCIDENT_DATA = "incident_data"
    AUDIT_LOGS = "audit_logs"
    TRAINING_RECORDS = "training_records"
    EXERCISE_RESULTS = "exercise_results"
    POLICY_DOCUMENTS = "policy_documents"
    RISK_ASSESSMENTS = "risk_assessments"
    BUSINESS_IMPACT = "business_impact"
    BACKUP_DATA = "backup_data"


class QuotaType(str, Enum):
    STORAGE = "storage"
    API_CALLS = "api_calls"
    USERS = "users"
    DOCUMENTS = "documents"
    EXERCISES = "exercises"


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"
    UNKNOWN = "unknown"


class RetentionRule(BaseModel):
    id: str
    tenant_id: str
    data_category: DataCategory
    policy: RetentionPolicy
    retention_days: int
    auto_delete: bool = True
    legal_hold: bool = False
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_applied: Optional[datetime] = None


class QuotaLimit(BaseModel):
    id: str
    tenant_id: str
    quota_type: QuotaType
    limit_value: float
    current_usage: float = 0.0
    unit: str  # GB, count, etc.
    soft_limit_percent: float = 80.0
    hard_limit_percent: float = 95.0
    alert_enabled: bool = True
    description: Optional[str] = None


class BackupPolicy(BaseModel):
    id: str
    tenant_id: str
    name: str
    data_categories: List[DataCategory]
    frequency: str  # daily, weekly, monthly
    retention_days: int = 90
    encryption_enabled: bool = True
    compression_enabled: bool = True
    storage_location: str = "primary"
    last_backup: Optional[datetime] = None
    next_backup: Optional[datetime] = None
    status: str = "active"


class ComplianceCheck(BaseModel):
    id: str
    tenant_id: str
    check_name: str
    description: str
    category: str
    status: ComplianceStatus
    last_checked: datetime = Field(default_factory=datetime.utcnow)
    next_check: Optional[datetime] = None
    findings: List[str] = Field(default_factory=list)
    remediation_steps: List[str] = Field(default_factory=list)
    risk_level: str = "medium"


class SystemHealth(BaseModel):
    service_name: str
    status: str  # healthy, degraded, unhealthy
    uptime: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    response_time: float
    last_check: datetime = Field(default_factory=datetime.utcnow)
    alerts: List[str] = Field(default_factory=list)


class GovernanceService:
    """Service for managing BCM platform governance"""
    
    def __init__(self, config: Dict[str, Any]):
        self.eventbus_url = config.get("eventbus_url", "http://localhost:8001")
        self.storage_path = config.get("storage_path", "/data/bcm")
        self.backup_path = config.get("backup_path", "/backups/bcm")
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # In-memory storage for demo (replace with database)
        self.retention_rules = {}
        self.quota_limits = {}
        self.backup_policies = {}
        self.compliance_checks = {}
        self.system_health = {}
        
        # Default configurations
        self.default_quotas = {
            QuotaType.STORAGE: {"limit": 100.0, "unit": "GB"},
            QuotaType.USERS: {"limit": 1000, "unit": "count"},
            QuotaType.DOCUMENTS: {"limit": 50000, "unit": "count"},
            QuotaType.EXERCISES: {"limit": 100, "unit": "count"},
            QuotaType.API_CALLS: {"limit": 1000000, "unit": "calls/month"}
        }
    
    async def __aenter__(self):
        await self._initialize_defaults()
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.client.aclose()
    
    async def publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish governance events to EventBus"""
        try:
            event = {
                "event_type": event_type,
                "tenant_id": data.get("tenant_id", "demo"),
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "governance_service"
            }
            
            response = await self.client.post(
                f"{self.eventbus_url}/api/events/publish",
                json=event
            )
            response.raise_for_status()
            logger.info(f"Published event: {event_type}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
    
    # Retention Management
    async def create_retention_rule(self, rule: RetentionRule) -> RetentionRule:
        """Create a data retention rule"""
        try:
            self.retention_rules[rule.id] = rule
            
            # Publish event
            await self.publish_event("bcm.governance.retention_rule_created", {
                "rule_id": rule.id,
                "data_category": rule.data_category,
                "retention_days": rule.retention_days,
                "tenant_id": rule.tenant_id
            })
            
            return rule
        except Exception as e:
            logger.error(f"Failed to create retention rule: {e}")
            raise
    
    async def apply_retention_policies(self, tenant_id: str) -> Dict[str, Any]:
        """Apply retention policies and clean up old data"""
        try:
            results = {
                "processed_categories": [],
                "deleted_items": 0,
                "freed_space_gb": 0.0,
                "errors": []
            }
            
            rules = [r for r in self.retention_rules.values() if r.tenant_id == tenant_id]
            
            for rule in rules:
                try:
                    if not rule.auto_delete or rule.legal_hold:
                        continue
                    
                    # Calculate cutoff date
                    cutoff_date = datetime.utcnow() - timedelta(days=rule.retention_days)
                    
                    # Simulate data cleanup (replace with actual implementation)
                    deleted_count, freed_space = await self._cleanup_data_category(
                        rule.data_category, cutoff_date
                    )
                    
                    results["processed_categories"].append(rule.data_category.value)
                    results["deleted_items"] += deleted_count
                    results["freed_space_gb"] += freed_space
                    
                    # Update last applied
                    rule.last_applied = datetime.utcnow()
                    
                except Exception as e:
                    results["errors"].append(f"{rule.data_category}: {str(e)}")
            
            # Publish event
            await self.publish_event("bcm.governance.retention_applied", {
                "tenant_id": tenant_id,
                "processed_categories": results["processed_categories"],
                "deleted_items": results["deleted_items"],
                "freed_space_gb": results["freed_space_gb"]
            })
            
            return results
        except Exception as e:
            logger.error(f"Failed to apply retention policies: {e}")
            raise
    
    async def _cleanup_data_category(self, category: DataCategory, cutoff_date: datetime) -> tuple:
        """Simulate cleanup for a data category"""
        # This would integrate with actual data stores
        import random
        deleted_items = random.randint(10, 100)
        freed_space_gb = random.uniform(0.5, 5.0)
        
        logger.info(f"Cleaned up {category}: {deleted_items} items, {freed_space_gb:.2f} GB")
        return deleted_items, freed_space_gb
    
    # Quota Management
    async def set_quota_limit(self, quota: QuotaLimit) -> QuotaLimit:
        """Set or update quota limit"""
        try:
            self.quota_limits[quota.id] = quota
            
            # Check if quota is exceeded
            usage_percent = (quota.current_usage / quota.limit_value) * 100
            
            if usage_percent >= quota.hard_limit_percent:
                await self._trigger_quota_alert(quota, "hard_limit_exceeded")
            elif usage_percent >= quota.soft_limit_percent:
                await self._trigger_quota_alert(quota, "soft_limit_exceeded")
            
            return quota
        except Exception as e:
            logger.error(f"Failed to set quota limit: {e}")
            raise
    
    async def update_quota_usage(self, tenant_id: str, quota_type: QuotaType, 
                                usage_delta: float) -> QuotaLimit:
        """Update quota usage"""
        try:
            # Find quota for tenant and type
            quota = None
            for q in self.quota_limits.values():
                if q.tenant_id == tenant_id and q.quota_type == quota_type:
                    quota = q
                    break
            
            if not quota:
                # Create default quota
                quota = QuotaLimit(
                    id=f"{tenant_id}_{quota_type.value}",
                    tenant_id=tenant_id,
                    quota_type=quota_type,
                    **self.default_quotas.get(quota_type, {"limit": 1000, "unit": "count"})
                )
                self.quota_limits[quota.id] = quota
            
            quota.current_usage += usage_delta
            quota.current_usage = max(0, quota.current_usage)  # Ensure non-negative
            
            # Check for alerts
            usage_percent = (quota.current_usage / quota.limit_value) * 100
            if usage_percent >= quota.hard_limit_percent and quota.alert_enabled:
                await self._trigger_quota_alert(quota, "approaching_limit")
            
            return quota
        except Exception as e:
            logger.error(f"Failed to update quota usage: {e}")
            raise
    
    async def _trigger_quota_alert(self, quota: QuotaLimit, alert_type: str):
        """Trigger quota alert"""
        await self.publish_event("bcm.governance.quota_alert", {
            "tenant_id": quota.tenant_id,
            "quota_type": quota.quota_type,
            "alert_type": alert_type,
            "usage_percent": (quota.current_usage / quota.limit_value) * 100,
            "current_usage": quota.current_usage,
            "limit": quota.limit_value,
            "unit": quota.unit
        })
    
    async def get_quota_status(self, tenant_id: str) -> List[QuotaLimit]:
        """Get quota status for tenant"""
        return [q for q in self.quota_limits.values() if q.tenant_id == tenant_id]
    
    # Backup Management
    async def create_backup_policy(self, policy: BackupPolicy) -> BackupPolicy:
        """Create a backup policy"""
        try:
            self.backup_policies[policy.id] = policy
            
            # Schedule next backup
            await self._schedule_next_backup(policy)
            
            # Publish event
            await self.publish_event("bcm.governance.backup_policy_created", {
                "policy_id": policy.id,
                "name": policy.name,
                "frequency": policy.frequency,
                "tenant_id": policy.tenant_id
            })
            
            return policy
        except Exception as e:
            logger.error(f"Failed to create backup policy: {e}")
            raise
    
    async def execute_backup(self, policy_id: str) -> Dict[str, Any]:
        """Execute a backup according to policy"""
        try:
            policy = self.backup_policies.get(policy_id)
            if not policy:
                raise ValueError(f"Backup policy {policy_id} not found")
            
            backup_result = {
                "policy_id": policy_id,
                "start_time": datetime.utcnow(),
                "status": "success",
                "categories_backed_up": [],
                "total_size_gb": 0.0,
                "duration_seconds": 0
            }
            
            start_time = datetime.utcnow()
            
            for category in policy.data_categories:
                # Simulate backup process
                size_gb = await self._backup_data_category(category, policy)
                backup_result["categories_backed_up"].append(category.value)
                backup_result["total_size_gb"] += size_gb
            
            # Update policy
            policy.last_backup = datetime.utcnow()
            await self._schedule_next_backup(policy)
            
            backup_result["duration_seconds"] = (datetime.utcnow() - start_time).seconds
            
            # Publish event
            await self.publish_event("bcm.governance.backup_completed", {
                "policy_id": policy_id,
                "tenant_id": policy.tenant_id,
                "categories_count": len(backup_result["categories_backed_up"]),
                "size_gb": backup_result["total_size_gb"],
                "duration": backup_result["duration_seconds"]
            })
            
            return backup_result
        except Exception as e:
            logger.error(f"Failed to execute backup: {e}")
            raise
    
    async def _backup_data_category(self, category: DataCategory, policy: BackupPolicy) -> float:
        """Simulate backing up a data category"""
        import random
        await asyncio.sleep(0.1)  # Simulate backup time
        size_gb = random.uniform(0.1, 2.0)
        logger.info(f"Backed up {category.value}: {size_gb:.2f} GB")
        return size_gb
    
    async def _schedule_next_backup(self, policy: BackupPolicy):
        """Schedule the next backup"""
        now = datetime.utcnow()
        if policy.frequency == "daily":
            policy.next_backup = now + timedelta(days=1)
        elif policy.frequency == "weekly":
            policy.next_backup = now + timedelta(weeks=1)
        elif policy.frequency == "monthly":
            policy.next_backup = now + timedelta(days=30)
    
    # Compliance Management
    async def run_compliance_check(self, check_id: str) -> ComplianceCheck:
        """Run a specific compliance check"""
        try:
            check = self.compliance_checks.get(check_id)
            if not check:
                raise ValueError(f"Compliance check {check_id} not found")
            
            # Simulate compliance check
            check.status = await self._perform_compliance_check(check)
            check.last_checked = datetime.utcnow()
            check.next_check = datetime.utcnow() + timedelta(days=30)
            
            # Publish event
            await self.publish_event("bcm.governance.compliance_checked", {
                "check_id": check_id,
                "check_name": check.check_name,
                "status": check.status,
                "tenant_id": check.tenant_id,
                "findings_count": len(check.findings)
            })
            
            return check
        except Exception as e:
            logger.error(f"Failed to run compliance check: {e}")
            raise
    
    async def _perform_compliance_check(self, check: ComplianceCheck) -> ComplianceStatus:
        """Simulate performing a compliance check"""
        import random
        
        # Simulate different compliance scenarios
        statuses = [
            ComplianceStatus.COMPLIANT,
            ComplianceStatus.NON_COMPLIANT,
            ComplianceStatus.WARNING
        ]
        
        status = random.choice(statuses)
        
        if status == ComplianceStatus.NON_COMPLIANT:
            check.findings = ["Missing documentation", "Outdated procedures"]
            check.remediation_steps = ["Update procedures", "Complete documentation"]
        elif status == ComplianceStatus.WARNING:
            check.findings = ["Minor gaps in documentation"]
            check.remediation_steps = ["Review and update as needed"]
        else:
            check.findings = []
            check.remediation_steps = []
        
        return status
    
    # System Health Monitoring
    async def check_system_health(self) -> List[SystemHealth]:
        """Check health of all BCM services"""
        try:
            services = [
                "eventbus", "orchestrator", "docproc", 
                "notification", "lms_adapter", "thehive_adapter", 
                "sim_adapter", "governance"
            ]
            
            health_results = []
            
            for service in services:
                health = await self._check_service_health(service)
                health_results.append(health)
                self.system_health[service] = health
            
            # Publish overall health event
            unhealthy_services = [h.service_name for h in health_results if h.status != "healthy"]
            
            await self.publish_event("bcm.governance.health_check_completed", {
                "total_services": len(services),
                "healthy_services": len(services) - len(unhealthy_services),
                "unhealthy_services": unhealthy_services,
                "tenant_id": "demo"
            })
            
            return health_results
        except Exception as e:
            logger.error(f"Failed to check system health: {e}")
            return []
    
    async def _check_service_health(self, service_name: str) -> SystemHealth:
        """Check health of a specific service"""
        try:
            # Map service to port
            port_map = {
                "eventbus": 8001,
                "orchestrator": 8002,
                "docproc": 8003,
                "notification": 8004,
                "lms_adapter": 8006,
                "thehive_adapter": 8007,
                "sim_adapter": 8008,
                "governance": 8009
            }
            
            port = port_map.get(service_name, 8000)
            
            try:
                start_time = datetime.utcnow()
                response = await self.client.get(
                    f"http://localhost:{port}/health",
                    timeout=5.0
                )
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                if response.status_code == 200:
                    status = "healthy"
                    alerts = []
                else:
                    status = "degraded"
                    alerts = [f"HTTP {response.status_code}"]
                    
            except Exception as e:
                status = "unhealthy"
                response_time = 5000
                alerts = [str(e)]
            
            import random
            health = SystemHealth(
                service_name=service_name,
                status=status,
                uptime=random.uniform(90, 99.9),
                cpu_usage=random.uniform(10, 80),
                memory_usage=random.uniform(20, 70),
                disk_usage=random.uniform(5, 60),
                response_time=response_time,
                alerts=alerts
            )
            
            return health
        except Exception as e:
            logger.error(f"Failed to check {service_name} health: {e}")
            return SystemHealth(
                service_name=service_name,
                status="unknown",
                uptime=0,
                cpu_usage=0,
                memory_usage=0,
                disk_usage=0,
                response_time=0,
                alerts=[str(e)]
            )
    
    async def _initialize_defaults(self):
        """Initialize default policies and checks"""
        # Default retention rules
        retention_rules = [
            RetentionRule(
                id="RET-001",
                tenant_id="demo",
                data_category=DataCategory.INCIDENT_DATA,
                policy=RetentionPolicy.LONG_TERM,
                retention_days=2555,  # 7 years
                description="Incident data for regulatory compliance"
            ),
            RetentionRule(
                id="RET-002",
                tenant_id="demo",
                data_category=DataCategory.AUDIT_LOGS,
                policy=RetentionPolicy.LONG_TERM,
                retention_days=2555,
                description="Audit logs for compliance"
            ),
            RetentionRule(
                id="RET-003",
                tenant_id="demo",
                data_category=DataCategory.TRAINING_RECORDS,
                policy=RetentionPolicy.MEDIUM_TERM,
                retention_days=365,
                description="Training completion records"
            )
        ]
        
        for rule in retention_rules:
            self.retention_rules[rule.id] = rule
        
        # Default compliance checks
        compliance_checks = [
            ComplianceCheck(
                id="COMP-001",
                tenant_id="demo",
                check_name="ISO 22301 Documentation",
                description="Verify all required ISO 22301 documentation is present",
                category="documentation",
                status=ComplianceStatus.COMPLIANT
            ),
            ComplianceCheck(
                id="COMP-002",
                tenant_id="demo",
                check_name="Backup Policy Compliance",
                description="Ensure backup policies meet regulatory requirements",
                category="backup",
                status=ComplianceStatus.COMPLIANT
            ),
            ComplianceCheck(
                id="COMP-003",
                tenant_id="demo",
                check_name="Data Retention Compliance",
                description="Verify data retention policies are properly applied",
                category="retention",
                status=ComplianceStatus.WARNING
            )
        ]
        
        for check in compliance_checks:
            self.compliance_checks[check.id] = check
    
    # Analytics
    async def get_governance_metrics(self, tenant_id: str = "demo") -> Dict[str, Any]:
        """Get governance metrics for dashboard"""
        try:
            quotas = [q for q in self.quota_limits.values() if q.tenant_id == tenant_id]
            checks = [c for c in self.compliance_checks.values() if c.tenant_id == tenant_id]
            
            metrics = {
                "quotas": {
                    "total": len(quotas),
                    "over_soft_limit": len([q for q in quotas if (q.current_usage/q.limit_value)*100 >= q.soft_limit_percent]),
                    "over_hard_limit": len([q for q in quotas if (q.current_usage/q.limit_value)*100 >= q.hard_limit_percent]),
                },
                "compliance": {
                    "total_checks": len(checks),
                    "compliant": len([c for c in checks if c.status == ComplianceStatus.COMPLIANT]),
                    "non_compliant": len([c for c in checks if c.status == ComplianceStatus.NON_COMPLIANT]),
                    "warnings": len([c for c in checks if c.status == ComplianceStatus.WARNING])
                },
                "retention": {
                    "active_rules": len([r for r in self.retention_rules.values() if r.tenant_id == tenant_id]),
                    "auto_cleanup_enabled": len([r for r in self.retention_rules.values() 
                                               if r.tenant_id == tenant_id and r.auto_delete])
                },
                "backups": {
                    "active_policies": len([p for p in self.backup_policies.values() if p.tenant_id == tenant_id]),
                    "successful_backups": len([p for p in self.backup_policies.values() 
                                             if p.tenant_id == tenant_id and p.last_backup])
                },
                "system_health": {
                    "healthy_services": len([h for h in self.system_health.values() if h.status == "healthy"]),
                    "total_services": len(self.system_health),
                    "avg_response_time": sum(h.response_time for h in self.system_health.values()) / max(len(self.system_health), 1)
                }
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Failed to get governance metrics: {e}")
            return {}


# FastAPI service endpoint
if __name__ == "__main__":
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    
    app = FastAPI(title="Governance Service")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    config = {
        "eventbus_url": "http://localhost:8001",
        "storage_path": "/data/bcm",
        "backup_path": "/backups/bcm"
    }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "governance"}
    
    @app.post("/api/retention/apply")
    async def apply_retention(tenant_id: str = "demo"):
        async with GovernanceService(config) as service:
            result = await service.apply_retention_policies(tenant_id)
            return result
    
    @app.get("/api/quotas")
    async def get_quotas(tenant_id: str = "demo"):
        async with GovernanceService(config) as service:
            quotas = await service.get_quota_status(tenant_id)
            return {"quotas": [q.dict() for q in quotas]}
    
    @app.post("/api/backup/{policy_id}/execute")
    async def execute_backup(policy_id: str):
        async with GovernanceService(config) as service:
            result = await service.execute_backup(policy_id)
            return result
    
    @app.get("/api/health/check")
    async def check_health():
        async with GovernanceService(config) as service:
            health_results = await service.check_system_health()
            return {"services": [h.dict() for h in health_results]}
    
    @app.get("/api/metrics")
    async def get_metrics(tenant_id: str = "demo"):
        async with GovernanceService(config) as service:
            metrics = await service.get_governance_metrics(tenant_id)
            return metrics
    
    uvicorn.run(app, host="0.0.0.0", port=8009)
