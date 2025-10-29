"""
Mock data for TheHive Adapter testing
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

def get_mock_thehive_configs() -> List[Dict[str, Any]]:
    """Generate mock TheHive configurations"""
    return [
        {
            "id": "thehive_001",
            "name": "Corporate Security TheHive",
            "base_url": "https://security.company.com",
            "api_key": "mock_thehive_api_key_12345",
            "tenant_id": "tenant_001",
            "is_active": True,
            "organization": "Company Security Operations",
            "settings": {
                "auto_import_alerts": True,
                "default_assignee": "soc_team@company.com",
                "case_templates": ["bcm_incident", "security_incident", "data_breach"]
            }
        },
        {
            "id": "thehive_002",
            "name": "Regional SOC TheHive",
            "base_url": "https://soc-regional.company.com", 
            "api_key": "mock_thehive_regional_key_67890",
            "tenant_id": "tenant_002",
            "is_active": True,
            "organization": "Regional Security Team",
            "settings": {
                "auto_import_alerts": False,
                "escalation_enabled": True,
                "parent_instance": "thehive_001"
            }
        }
    ]

def get_mock_cases() -> List[Dict[str, Any]]:
    """Generate mock cases"""
    base_time = datetime.utcnow()
    return [
        {
            "id": "case_001",
            "title": "Critical System Outage - ERP Platform",
            "description": "Complete outage of main ERP system affecting all business operations. Impact assessment shows critical business processes halted.",
            "severity": 4,  # Critical
            "tlp": 2,       # TLP:AMBER
            "pap": 2,       # PAP:AMBER
            "status": "Open",
            "tags": ["BCM", "System-Outage", "ERP", "Critical-Impact"],
            "assignee": "bcm_manager@company.com",
            "owner": "incident_response_team",
            "thehive_case_id": "case_thehive_001",
            "created_at": base_time - timedelta(hours=3),
            "updated_at": base_time - timedelta(minutes=15)
        },
        {
            "id": "case_002", 
            "title": "Data Center Power Failure",
            "description": "Primary data center experiencing power issues. Backup generators activated but estimated runtime is 6 hours.",
            "severity": 3,  # High
            "tlp": 1,       # TLP:GREEN
            "pap": 2,       # PAP:AMBER
            "status": "Open",
            "tags": ["BCM", "Infrastructure", "Power", "Data-Center"],
            "assignee": "facilities_manager@company.com",
            "owner": "infrastructure_team",
            "thehive_case_id": "case_thehive_002",
            "created_at": base_time - timedelta(hours=1, minutes=30),
            "updated_at": base_time - timedelta(minutes=5)
        },
        {
            "id": "case_003",
            "title": "Cyber Security Incident - Ransomware Detection", 
            "description": "Suspected ransomware activity detected on multiple endpoints. Containment measures initiated.",
            "severity": 4,  # Critical
            "tlp": 3,       # TLP:RED
            "pap": 3,       # PAP:RED
            "status": "Open",
            "tags": ["Security", "Ransomware", "Cyber-Attack", "Containment"],
            "assignee": "security_analyst@company.com",
            "owner": "security_operations_center",
            "thehive_case_id": "case_thehive_003",
            "created_at": base_time - timedelta(minutes=45),
            "updated_at": base_time - timedelta(minutes=2)
        },
        {
            "id": "case_004",
            "title": "COVID-19 Office Closure",
            "description": "Local health authorities mandated office closure due to COVID-19 exposure. Activating remote work procedures.",
            "severity": 2,  # Medium
            "tlp": 1,       # TLP:GREEN  
            "pap": 1,       # PAP:GREEN
            "status": "Resolved",
            "tags": ["BCM", "Pandemic", "Remote-Work", "Health-Safety"],
            "assignee": "hr_manager@company.com",
            "owner": "business_continuity_team", 
            "thehive_case_id": "case_thehive_004",
            "created_at": base_time - timedelta(days=7),
            "updated_at": base_time - timedelta(days=5),
            "resolved_at": base_time - timedelta(days=5)
        },
        {
            "id": "case_005",
            "title": "Supply Chain Disruption",
            "description": "Key supplier unable to deliver critical components due to logistics issues. Alternate sourcing required.",
            "severity": 2,  # Medium
            "tlp": 2,       # TLP:AMBER
            "pap": 2,       # PAP:AMBER
            "status": "Open", 
            "tags": ["BCM", "Supply-Chain", "Logistics", "Sourcing"],
            "assignee": "procurement_manager@company.com",
            "owner": "supply_chain_team",
            "thehive_case_id": "case_thehive_005", 
            "created_at": base_time - timedelta(days=2),
            "updated_at": base_time - timedelta(hours=6)
        }
    ]

def get_mock_alerts() -> List[Dict[str, Any]]:
    """Generate mock alerts"""
    base_time = datetime.utcnow()
    return [
        {
            "id": "alert_001",
            "title": "Network Performance Degradation",
            "description": "Monitoring systems detected significant network performance degradation across multiple segments",
            "severity": 2,  # Medium
            "tlp": 1,       # TLP:GREEN
            "pap": 1,       # PAP:GREEN
            "type": "performance_issue",
            "source": "network_monitoring",
            "source_ref": "nm_alert_12345",
            "status": "New",
            "tags": ["Network", "Performance", "Monitoring"],
            "artifacts": [
                {
                    "data_type": "ip",
                    "data": "192.168.1.100",
                    "message": "Gateway router showing high latency"
                },
                {
                    "data_type": "url", 
                    "data": "https://monitoring.company.com/dashboard/network",
                    "message": "Network monitoring dashboard"
                }
            ],
            "thehive_alert_id": "alert_thehive_001",
            "created_at": base_time - timedelta(minutes=30)
        },
        {
            "id": "alert_002",
            "title": "Suspicious Login Activity",
            "description": "Multiple failed login attempts detected from unusual geographic locations",
            "severity": 3,  # High
            "tlp": 2,       # TLP:AMBER
            "pap": 2,       # PAP:AMBER
            "type": "security_anomaly",
            "source": "security_monitoring",
            "source_ref": "sm_alert_67890", 
            "status": "Updated",
            "tags": ["Security", "Authentication", "Anomaly"],
            "artifacts": [
                {
                    "data_type": "ip",
                    "data": "203.0.113.45",
                    "message": "Source IP from suspicious location"
                },
                {
                    "data_type": "user",
                    "data": "admin@company.com",
                    "message": "Targeted user account"
                }
            ],
            "thehive_alert_id": "alert_thehive_002",
            "created_at": base_time - timedelta(hours=2)
        },
        {
            "id": "alert_003",
            "title": "Database Connection Failure",
            "description": "Critical application unable to connect to primary database server",
            "severity": 4,  # Critical
            "tlp": 2,       # TLP:AMBER
            "pap": 2,       # PAP:AMBER
            "type": "system_failure",
            "source": "application_monitoring", 
            "source_ref": "app_alert_54321",
            "status": "Imported",
            "tags": ["Database", "Connection", "Critical-App"],
            "artifacts": [
                {
                    "data_type": "hostname",
                    "data": "db-primary.company.com",
                    "message": "Primary database server"
                },
                {
                    "data_type": "application",
                    "data": "CRM-Production",
                    "message": "Affected application"
                }
            ],
            "thehive_alert_id": "alert_thehive_003",
            "created_at": base_time - timedelta(minutes=10)
        }
    ]

def get_mock_observables() -> List[Dict[str, Any]]:
    """Generate mock observables"""
    return [
        {
            "id": "obs_001",
            "case_id": "case_001",
            "data_type": "ip",
            "data": "192.168.1.50",
            "message": "ERP server primary IP address",
            "tlp": 2,
            "ioc": False,
            "sighted": True,
            "tags": ["ERP", "Server", "Primary"],
            "thehive_observable_id": "obs_thehive_001"
        },
        {
            "id": "obs_002",
            "case_id": "case_001", 
            "data_type": "hostname",
            "data": "erp-prod-01.company.com",
            "message": "ERP production server hostname",
            "tlp": 2,
            "ioc": False,
            "sighted": True,
            "tags": ["ERP", "Production", "Hostname"],
            "thehive_observable_id": "obs_thehive_002"
        },
        {
            "id": "obs_003",
            "case_id": "case_003",
            "data_type": "file_hash",
            "data": "d41d8cd98f00b204e9800998ecf8427e",
            "message": "Suspicious file hash detected by endpoint protection",
            "tlp": 3,
            "ioc": True,
            "sighted": True,
            "tags": ["Ransomware", "Hash", "IOC"],
            "thehive_observable_id": "obs_thehive_003" 
        },
        {
            "id": "obs_004",
            "case_id": "case_003",
            "data_type": "domain",
            "data": "malicious-c2.example.com",
            "message": "Suspected command and control domain",
            "tlp": 3,
            "ioc": True,
            "sighted": False,
            "tags": ["C2", "Domain", "Malware"],
            "thehive_observable_id": "obs_thehive_004"
        }
    ]

def get_mock_tasks() -> List[Dict[str, Any]]:
    """Generate mock tasks"""
    base_time = datetime.utcnow()
    return [
        {
            "id": "task_001",
            "case_id": "case_001",
            "title": "Initial Impact Assessment",
            "description": "Assess the impact of ERP system outage on business operations and identify affected processes",
            "status": "Completed",
            "assignee": "bcm_analyst@company.com",
            "owner": "bcm_team", 
            "order": 1,
            "category": "Assessment",
            "thehive_task_id": "task_thehive_001",
            "created_at": base_time - timedelta(hours=3),
            "updated_at": base_time - timedelta(hours=2, minutes=45)
        },
        {
            "id": "task_002",
            "case_id": "case_001",
            "title": "Activate Recovery Team",
            "description": "Contact and activate the ERP recovery team including technical leads and business stakeholders",
            "status": "Completed",
            "assignee": "incident_coordinator@company.com",
            "owner": "incident_response",
            "order": 2,
            "category": "Coordination",
            "thehive_task_id": "task_thehive_002", 
            "created_at": base_time - timedelta(hours=2, minutes=45),
            "updated_at": base_time - timedelta(hours=2, minutes=15)
        },
        {
            "id": "task_003",
            "case_id": "case_001",
            "title": "Execute Recovery Procedures",
            "description": "Implement ERP system recovery procedures including database restoration and application restart",
            "status": "InProgress",
            "assignee": "system_admin@company.com",
            "owner": "technical_team",
            "order": 3,
            "category": "Recovery",
            "thehive_task_id": "task_thehive_003",
            "created_at": base_time - timedelta(hours=2, minutes=15),
            "updated_at": base_time - timedelta(minutes=30)
        },
        {
            "id": "task_004", 
            "case_id": "case_002",
            "title": "Monitor Power Systems",
            "description": "Continuously monitor backup power systems and coordinate with facilities management",
            "status": "InProgress",
            "assignee": "facilities_tech@company.com",
            "owner": "facilities_team",
            "order": 1,
            "category": "Monitoring",
            "thehive_task_id": "task_thehive_004",
            "created_at": base_time - timedelta(hours=1, minutes=30),
            "updated_at": base_time - timedelta(minutes=10)
        }
    ]

def get_mock_case_templates() -> List[Dict[str, Any]]:
    """Generate mock case templates for BCM incidents"""
    return [
        {
            "name": "BCM Incident Response",
            "description": "Standard template for business continuity incidents",
            "severity": 3,
            "tlp": 2,
            "pap": 2,
            "tags": ["BCM", "Incident-Response"],
            "task_templates": [
                {
                    "title": "Initial Assessment",
                    "description": "Conduct initial impact assessment and classify incident severity",
                    "order": 1,
                    "category": "Assessment"
                },
                {
                    "title": "Stakeholder Notification", 
                    "description": "Notify relevant stakeholders and management of incident status",
                    "order": 2,
                    "category": "Communication"
                },
                {
                    "title": "Activate Response Team",
                    "description": "Activate appropriate incident response team based on incident type and severity",
                    "order": 3,
                    "category": "Coordination"
                },
                {
                    "title": "Execute Recovery Plan",
                    "description": "Execute documented recovery procedures and workarounds",
                    "order": 4,
                    "category": "Recovery"
                },
                {
                    "title": "Monitor Progress",
                    "description": "Monitor recovery progress and adjust procedures as needed", 
                    "order": 5,
                    "category": "Monitoring"
                },
                {
                    "title": "Post-Incident Review",
                    "description": "Conduct post-incident review and document lessons learned",
                    "order": 6,
                    "category": "Review"
                }
            ]
        },
        {
            "name": "Cyber Security Incident",
            "description": "Template for cyber security related incidents",
            "severity": 4,
            "tlp": 3,
            "pap": 3,
            "tags": ["Security", "Cyber-Attack"],
            "task_templates": [
                {
                    "title": "Containment",
                    "description": "Immediate containment of security incident to prevent spread",
                    "order": 1,
                    "category": "Containment"
                },
                {
                    "title": "Forensic Analysis",
                    "description": "Collect and analyze digital evidence related to the incident",
                    "order": 2,
                    "category": "Investigation"
                },
                {
                    "title": "Eradication",
                    "description": "Remove malicious components and close security gaps",
                    "order": 3, 
                    "category": "Eradication"
                },
                {
                    "title": "Recovery",
                    "description": "Restore systems to normal operations with enhanced monitoring",
                    "order": 4,
                    "category": "Recovery"
                }
            ]
        }
    ]

def get_mock_incident_metrics() -> Dict[str, Any]:
    """Generate mock incident metrics and KPIs"""
    return {
        "summary": {
            "total_cases": 15,
            "open_cases": 8,
            "resolved_cases": 7,
            "average_resolution_time_hours": 12.5,
            "cases_by_severity": {
                "critical": 3,
                "high": 5, 
                "medium": 4,
                "low": 3
            }
        },
        "trends": {
            "cases_this_month": 15,
            "cases_last_month": 12,
            "trend": "+25%",
            "most_common_tags": [
                {"tag": "BCM", "count": 8},
                {"tag": "System-Outage", "count": 5},
                {"tag": "Security", "count": 3}
            ]
        },
        "performance": {
            "mttr_target_hours": 8,
            "mttr_actual_hours": 12.5,
            "mttr_performance": "Below target",
            "sla_compliance": 76.2,
            "escalation_rate": 23.1
        },
        "team_performance": [
            {
                "team": "BCM Team",
                "assigned_cases": 8,
                "resolved_cases": 5,
                "avg_resolution_time": 10.2
            },
            {
                "team": "Security Operations", 
                "assigned_cases": 4,
                "resolved_cases": 2,
                "avg_resolution_time": 16.8
            },
            {
                "team": "Infrastructure Team",
                "assigned_cases": 3,
                "resolved_cases": 0,
                "avg_resolution_time": None
            }
        ]
    }