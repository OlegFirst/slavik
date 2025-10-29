"""
Mock data for Grafana Adapter testing
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

def get_mock_grafana_configs() -> List[Dict[str, Any]]:
    """Generate mock Grafana configurations"""
    return [
        {
            "id": "grafana_001",
            "name": "Corporate Grafana Dashboard",
            "base_url": "https://monitoring.company.com",
            "api_key": "mock_grafana_token_12345",
            "tenant_id": "tenant_001",
            "organization_id": 1,
            "is_active": True,
            "settings": {
                "default_dashboard": "bcm_overview",
                "refresh_interval": "30s",
                "time_zone": "UTC",
                "theme": "dark"
            }
        },
        {
            "id": "grafana_002", 
            "name": "Regional Monitoring",
            "base_url": "https://grafana-regional.company.com",
            "api_key": "mock_grafana_regional_67890",
            "tenant_id": "tenant_002",
            "organization_id": 2,
            "is_active": True,
            "settings": {
                "default_dashboard": "regional_overview",
                "refresh_interval": "1m",
                "time_zone": "America/New_York"
            }
        }
    ]

def get_mock_dashboards() -> List[Dict[str, Any]]:
    """Generate mock dashboards"""
    base_time = datetime.utcnow()
    return [
        {
            "id": "dash_001",
            "uid": "bcm-overview-001",
            "title": "BCM Platform Overview",
            "description": "High-level overview of business continuity management metrics and KPIs",
            "tags": ["BCM", "Overview", "KPI"],
            "folder_id": 0,
            "folder_title": "General",
            "url": "/d/bcm-overview-001/bcm-platform-overview",
            "version": 12,
            "created": base_time - timedelta(days=90),
            "updated": base_time - timedelta(days=2)
        },
        {
            "id": "dash_002",
            "uid": "bcm-incidents-001", 
            "title": "BCM Incident Management",
            "description": "Real-time incident tracking and response metrics",
            "tags": ["BCM", "Incidents", "Response"],
            "folder_id": 1,
            "folder_title": "BCM Dashboards",
            "url": "/d/bcm-incidents-001/bcm-incident-management",
            "version": 8,
            "created": base_time - timedelta(days=60),
            "updated": base_time - timedelta(hours=6)
        },
        {
            "id": "dash_003",
            "uid": "bcm-training-001",
            "title": "BCM Training & Competency",
            "description": "Training completion rates and competency assessments",
            "tags": ["BCM", "Training", "Competency"],
            "folder_id": 1,
            "folder_title": "BCM Dashboards", 
            "url": "/d/bcm-training-001/bcm-training-competency",
            "version": 5,
            "created": base_time - timedelta(days=45),
            "updated": base_time - timedelta(days=1)
        },
        {
            "id": "dash_004",
            "uid": "bcm-bia-metrics-001",
            "title": "BIA Metrics & Analysis",
            "description": "Business Impact Analysis results and trends",
            "tags": ["BCM", "BIA", "Analysis"],
            "folder_id": 1,
            "folder_title": "BCM Dashboards",
            "url": "/d/bcm-bia-metrics-001/bia-metrics-analysis", 
            "version": 3,
            "created": base_time - timedelta(days=30),
            "updated": base_time - timedelta(hours=12)
        },
        {
            "id": "dash_005",
            "uid": "bcm-exercises-001",
            "title": "BCM Exercises & Testing",
            "description": "Exercise planning, execution and results tracking",
            "tags": ["BCM", "Exercises", "Testing"],
            "folder_id": 1,
            "folder_title": "BCM Dashboards",
            "url": "/d/bcm-exercises-001/bcm-exercises-testing",
            "version": 7,
            "created": base_time - timedelta(days=75),
            "updated": base_time - timedelta(days=3)
        }
    ]

def get_mock_datasources() -> List[Dict[str, Any]]:
    """Generate mock data sources"""
    return [
        {
            "id": 1,
            "uid": "postgres-bcm-001",
            "name": "BCM PostgreSQL",
            "type": "postgres",
            "url": "postgres://bcm-db:5432/bcm_platform",
            "access": "proxy",
            "is_default": True,
            "basic_auth": False,
            "database": "bcm_platform",
            "user": "grafana_reader"
        },
        {
            "id": 2,
            "uid": "prometheus-001",
            "name": "System Metrics (Prometheus)",
            "type": "prometheus", 
            "url": "http://prometheus:9090",
            "access": "proxy",
            "is_default": False,
            "basic_auth": False
        },
        {
            "id": 3,
            "uid": "elasticsearch-logs-001",
            "name": "Application Logs (Elasticsearch)",
            "type": "elasticsearch",
            "url": "https://elasticsearch:9200",
            "access": "proxy", 
            "is_default": False,
            "basic_auth": True,
            "database": "bcm-logs-*",
            "user": "grafana_logs"
        },
        {
            "id": 4,
            "uid": "influxdb-metrics-001", 
            "name": "BCM Metrics (InfluxDB)",
            "type": "influxdb",
            "url": "http://influxdb:8086",
            "access": "proxy",
            "is_default": False,
            "basic_auth": False,
            "database": "bcm_metrics"
        }
    ]

def get_mock_bcm_kpis() -> Dict[str, Any]:
    """Generate mock BCM KPI data"""
    base_time = datetime.utcnow()
    return {
        "current_period": {
            "period": "2024-Q1",
            "start_date": "2024-01-01",
            "end_date": "2024-03-31",
            "bia_coverage": 87.5,
            "plans_up_to_date": 92.3,
            "capa_on_time": 78.9,
            "training_completion": 85.2,
            "exercise_completion": 100.0,
            "incident_mttr_hours": 4.2,
            "rto_adherence": 94.1,
            "rpo_adherence": 96.7
        },
        "historical_data": [
            {
                "period": "2023-Q4",
                "bia_coverage": 83.2,
                "plans_up_to_date": 89.1,
                "capa_on_time": 72.4,
                "training_completion": 81.7,
                "exercise_completion": 100.0,
                "incident_mttr_hours": 5.1,
                "rto_adherence": 91.8,
                "rpo_adherence": 94.2
            },
            {
                "period": "2024-Q1",
                "bia_coverage": 87.5,
                "plans_up_to_date": 92.3,
                "capa_on_time": 78.9, 
                "training_completion": 85.2,
                "exercise_completion": 100.0,
                "incident_mttr_hours": 4.2,
                "rto_adherence": 94.1,
                "rpo_adherence": 96.7
            }
        ],
        "targets": {
            "bia_coverage": 90.0,
            "plans_up_to_date": 95.0,
            "capa_on_time": 85.0,
            "training_completion": 90.0,
            "exercise_completion": 100.0,
            "incident_mttr_hours": 4.0,
            "rto_adherence": 95.0,
            "rpo_adherence": 98.0
        },
        "trends": {
            "bia_coverage": "+4.3",
            "plans_up_to_date": "+3.2", 
            "capa_on_time": "+6.5",
            "training_completion": "+3.5",
            "incident_mttr_hours": "-0.9",
            "rto_adherence": "+2.3",
            "rpo_adherence": "+2.5"
        }
    }

def get_mock_incident_metrics() -> Dict[str, Any]:
    """Generate mock incident metrics for dashboards"""
    base_time = datetime.utcnow()
    return {
        "current_incidents": {
            "total_open": 8,
            "critical": 2,
            "high": 3,
            "medium": 2,
            "low": 1,
            "avg_age_hours": 6.5,
            "escalated": 2
        },
        "resolution_metrics": {
            "mttr_current_month": 4.2,
            "mttr_last_month": 5.1,
            "mttr_target": 4.0,
            "resolution_rate": 92.3,
            "first_call_resolution": 67.8
        },
        "incident_trends": [
            {
                "date": (base_time - timedelta(days=30)).strftime("%Y-%m-%d"),
                "incidents": 12,
                "avg_severity": 2.3,
                "mttr": 5.8
            },
            {
                "date": (base_time - timedelta(days=23)).strftime("%Y-%m-%d"),
                "incidents": 8,
                "avg_severity": 2.1,
                "mttr": 4.9
            },
            {
                "date": (base_time - timedelta(days=16)).strftime("%Y-%m-%d"),
                "incidents": 15,
                "avg_severity": 2.8,
                "mttr": 6.2
            },
            {
                "date": (base_time - timedelta(days=9)).strftime("%Y-%m-%d"),
                "incidents": 6,
                "avg_severity": 1.9,
                "mttr": 3.1
            },
            {
                "date": (base_time - timedelta(days=2)).strftime("%Y-%m-%d"),
                "incidents": 9,
                "avg_severity": 2.4,
                "mttr": 4.2
            }
        ],
        "impact_analysis": {
            "business_processes_affected": 15,
            "estimated_revenue_impact": 125000,
            "customer_impact": "Medium",
            "reputation_risk": "Low"
        }
    }

def get_mock_training_metrics() -> Dict[str, Any]:
    """Generate mock training metrics"""
    return {
        "completion_rates": {
            "overall": 85.2,
            "by_role": {
                "executives": 78.5,
                "managers": 89.3,
                "employees": 84.7,
                "contractors": 81.2
            },
            "by_department": {
                "IT": 92.1,
                "HR": 87.4,
                "Finance": 83.6,
                "Operations": 88.9,
                "Sales": 79.2
            }
        },
        "course_performance": {
            "bcm_fundamentals": {
                "completion_rate": 94.5,
                "avg_score": 87.2,
                "pass_rate": 96.8
            },
            "incident_response": {
                "completion_rate": 76.8,
                "avg_score": 83.5,
                "pass_rate": 89.3
            },
            "crisis_communication": {
                "completion_rate": 88.9,
                "avg_score": 91.4,
                "pass_rate": 97.2
            }
        },
        "certification_status": {
            "certified": 189,
            "in_progress": 45,
            "overdue": 23,
            "not_started": 8,
            "compliance_rate": 77.1
        },
        "competency_gaps": [
            {
                "competency": "Crisis Communication",
                "gap_percentage": 23.4,
                "affected_roles": ["Manager", "Department Head"]
            },
            {
                "competency": "Risk Assessment",
                "gap_percentage": 18.7,
                "affected_roles": ["Analyst", "Coordinator"]
            }
        ]
    }

def get_mock_exercise_metrics() -> Dict[str, Any]:
    """Generate mock exercise metrics"""
    base_time = datetime.utcnow()
    return {
        "exercise_summary": {
            "planned_this_quarter": 4,
            "completed_this_quarter": 4,
            "completion_rate": 100.0,
            "avg_score": 87.5,
            "improvement_actions": 12
        },
        "recent_exercises": [
            {
                "name": "IT Disaster Recovery Test",
                "date": (base_time - timedelta(days=15)).strftime("%Y-%m-%d"),
                "type": "Full Scale",
                "score": 92.3,
                "participants": 25,
                "duration_hours": 4,
                "objectives_met": 8,
                "objectives_total": 9
            },
            {
                "name": "Communication Tree Test",
                "date": (base_time - timedelta(days=45)).strftime("%Y-%m-%d"), 
                "type": "Tabletop",
                "score": 85.7,
                "participants": 12,
                "duration_hours": 2,
                "objectives_met": 6,
                "objectives_total": 7
            },
            {
                "name": "Supply Chain Disruption Simulation",
                "date": (base_time - timedelta(days=75)).strftime("%Y-%m-%d"),
                "type": "Simulation",
                "score": 78.9,
                "participants": 18,
                "duration_hours": 6,
                "objectives_met": 7,
                "objectives_total": 10
            }
        ],
        "performance_trends": {
            "score_trend": "+5.2",
            "participation_trend": "+12.5",
            "objectives_met_trend": "+3.1"
        },
        "improvement_actions": [
            {
                "category": "Communication",
                "actions": 5,
                "completed": 3,
                "overdue": 1
            },
            {
                "category": "Technical",
                "actions": 4,
                "completed": 4,
                "overdue": 0
            },
            {
                "category": "Process",
                "actions": 3,
                "completed": 2,
                "overdue": 1
            }
        ]
    }

def get_mock_dashboard_panels() -> Dict[str, Any]:
    """Generate mock dashboard panel configurations"""
    return {
        "bcm_overview": {
            "panels": [
                {
                    "id": 1,
                    "title": "BIA Coverage",
                    "type": "stat",
                    "targets": [{"expr": "bia_coverage_percentage", "refId": "A"}],
                    "options": {"colorMode": "background", "unit": "percent"}
                },
                {
                    "id": 2, 
                    "title": "Plans Up to Date",
                    "type": "stat",
                    "targets": [{"expr": "plans_up_to_date_percentage", "refId": "A"}],
                    "options": {"colorMode": "background", "unit": "percent"}
                },
                {
                    "id": 3,
                    "title": "Training Completion",
                    "type": "gauge",
                    "targets": [{"expr": "training_completion_rate", "refId": "A"}],
                    "options": {"min": 0, "max": 100, "unit": "percent"}
                },
                {
                    "id": 4,
                    "title": "Incident Trends",
                    "type": "timeseries", 
                    "targets": [{"expr": "incidents_by_severity_over_time", "refId": "A"}],
                    "options": {"legend": {"displayMode": "table"}}
                },
                {
                    "id": 5,
                    "title": "MTTR Performance",
                    "type": "timeseries",
                    "targets": [{"expr": "mttr_hours_trend", "refId": "A"}],
                    "options": {"unit": "hours"}
                }
            ]
        },
        "incident_management": {
            "panels": [
                {
                    "id": 1,
                    "title": "Open Incidents by Severity",
                    "type": "piechart",
                    "targets": [{"expr": "incidents_by_severity", "refId": "A"}]
                },
                {
                    "id": 2,
                    "title": "MTTR vs Target",
                    "type": "stat",
                    "targets": [{"expr": "avg_mttr_hours", "refId": "A"}],
                    "options": {"colorMode": "value"}
                },
                {
                    "id": 3,
                    "title": "Resolution Timeline",
                    "type": "timeseries",
                    "targets": [{"expr": "incident_resolution_timeline", "refId": "A"}]
                }
            ]
        }
    }

def get_mock_annotations() -> List[Dict[str, Any]]:
    """Generate mock annotations"""
    base_time = datetime.utcnow()
    return [
        {
            "id": 1,
            "time": base_time - timedelta(days=7),
            "text": "Quarterly BCM Exercise Completed - Score: 92.3%",
            "tags": ["Exercise", "BCM", "Achievement"]
        },
        {
            "id": 2,
            "time": base_time - timedelta(days=14),
            "text": "Critical Incident: ERP System Outage - Recovery Time: 3.2 hours",
            "tags": ["Incident", "Critical", "ERP"]
        },
        {
            "id": 3,
            "time": base_time - timedelta(days=30),
            "text": "BIA Review Completed - Coverage improved to 87.5%",
            "tags": ["BIA", "Review", "Improvement"]
        },
        {
            "id": 4,
            "time": base_time - timedelta(days=2),
            "text": "Training Campaign Launched - Target: 90% completion by month end",
            "tags": ["Training", "Campaign", "Target"]
        }
    ]

def get_mock_alert_rules() -> List[Dict[str, Any]]:
    """Generate mock alert rules for BCM monitoring"""
    return [
        {
            "id": 1,
            "name": "BCM KPI Below Target",
            "condition": "bia_coverage < 85 OR plans_up_to_date < 90 OR training_completion < 85",
            "frequency": "1m",
            "severity": "warning",
            "notifications": ["bcm_team", "email"],
            "message": "BCM KPI has fallen below target threshold"
        },
        {
            "id": 2,
            "name": "Critical Incident Response Time",
            "condition": "incident_severity = 'critical' AND response_time > 30m",
            "frequency": "30s",
            "severity": "critical",
            "notifications": ["sms", "pager", "teams"],
            "message": "Critical incident response time exceeded threshold"
        },
        {
            "id": 3,
            "name": "Training Compliance Alert",
            "condition": "training_compliance_rate < 75",
            "frequency": "1d",
            "severity": "warning",
            "notifications": ["hr_team", "email"],
            "message": "Training compliance rate below acceptable level"
        },
        {
            "id": 4,
            "name": "Exercise Overdue",
            "condition": "days_since_last_exercise > 90",
            "frequency": "1d", 
            "severity": "warning",
            "notifications": ["bcm_coordinator", "email"],
            "message": "BCM exercise is overdue - quarterly requirement not met"
        }
    ]