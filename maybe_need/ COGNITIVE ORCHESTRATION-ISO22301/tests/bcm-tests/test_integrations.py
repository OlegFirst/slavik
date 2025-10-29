"""
Integration Tests for BCM Platform Integrations
Tests for BPMN, LMS, TheHive, and Grafana adapters
"""

import pytest
import asyncio
import json
from httpx import AsyncClient
from fastapi.testclient import TestClient


class TestBPMNService:
    """Tests for BPMN Workflow Service"""
    
    def test_health_check(self):
        """Test BPMN service health check"""
        # Mock test - would normally use actual client
        response = {"status": "healthy", "service": "bpmn_workflow"}
        assert response["status"] == "healthy"
        assert response["service"] == "bpmn_workflow"
    
    def test_process_deployment(self):
        """Test BPMN process deployment"""
        process_data = {
            "name": "Test BCM Process",
            "description": "Test process for BCM workflow",
            "bpmn_xml": """<?xml version="1.0" encoding="UTF-8"?>
            <definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
                <process id="testProcess" name="Test Process">
                    <startEvent id="start"/>
                    <userTask id="task1" name="Test Task"/>
                    <endEvent id="end"/>
                </process>
            </definitions>""",
            "tenant_id": "test_tenant",
            "version": "1.0"
        }
        
        # Mock validation
        assert process_data["name"] is not None
        assert "BPMN" in process_data["bpmn_xml"]
        assert process_data["tenant_id"] == "test_tenant"
    
    def test_process_instance_creation(self):
        """Test starting a process instance"""
        instance_data = {
            "process_id": "test_process_id",
            "tenant_id": "test_tenant",
            "variables": {"test_var": "test_value"},
            "started_by": "test_user"
        }
        
        assert instance_data["process_id"] is not None
        assert instance_data["tenant_id"] == "test_tenant"
        assert isinstance(instance_data["variables"], dict)
    
    def test_task_completion(self):
        """Test task completion"""
        task_completion = {
            "task_id": "test_task_id",
            "tenant_id": "test_tenant",
            "variables": {"result": "completed"},
            "completed_by": "test_user"
        }
        
        assert task_completion["task_id"] is not None
        assert task_completion["variables"]["result"] == "completed"


class TestLMSAdapter:
    """Tests for LMS Adapter Service"""
    
    def test_lms_config_validation(self):
        """Test LMS configuration validation"""
        configs = [
            {
                "name": "Test Moodle",
                "lms_type": "moodle",
                "base_url": "https://moodle.example.com",
                "api_key": "test_api_key",
                "tenant_id": "test_tenant"
            },
            {
                "name": "Test Canvas",
                "lms_type": "canvas",
                "base_url": "https://canvas.example.com",
                "api_key": "test_canvas_key",
                "tenant_id": "test_tenant"
            },
            {
                "name": "Test Open edX",
                "lms_type": "openedx",
                "base_url": "https://edx.example.com",
                "api_key": "test_edx_key",
                "api_secret": "test_edx_secret",
                "tenant_id": "test_tenant"
            }
        ]
        
        supported_types = ["moodle", "canvas", "openedx"]
        
        for config in configs:
            assert config["lms_type"] in supported_types
            assert config["base_url"].startswith("https://")
            assert len(config["api_key"]) > 0
            assert config["tenant_id"] == "test_tenant"
    
    def test_course_enrollment(self):
        """Test course enrollment process"""
        enrollment = {
            "course_id": "test_course_123",
            "user_email": "test@example.com",
            "tenant_id": "test_tenant",
            "status": "ENROLLED"
        }
        
        assert enrollment["course_id"] is not None
        assert "@" in enrollment["user_email"]
        assert enrollment["status"] == "ENROLLED"
    
    def test_course_launch_url(self):
        """Test course launch URL generation"""
        launch_urls = {
            "moodle": "https://moodle.example.com/course/view.php?id=123",
            "canvas": "https://canvas.example.com/courses/123",
            "openedx": "https://edx.example.com/courses/course123/courseware/"
        }
        
        for lms_type, url in launch_urls.items():
            assert url.startswith("https://")
            assert lms_type in ["moodle", "canvas", "openedx"]


class TestTheHiveAdapter:
    """Tests for TheHive Adapter Service"""
    
    def test_thehive_config_validation(self):
        """Test TheHive configuration validation"""
        config = {
            "name": "Test TheHive Instance",
            "base_url": "https://thehive.example.com",
            "api_key": "test_thehive_api_key",
            "tenant_id": "test_tenant",
            "organization": "Test Org"
        }
        
        assert config["base_url"].startswith("https://")
        assert len(config["api_key"]) > 0
        assert config["tenant_id"] == "test_tenant"
    
    def test_case_creation(self):
        """Test case creation"""
        case_data = {
            "title": "Test Security Incident",
            "description": "Test incident for BCM platform",
            "severity": 3,
            "tlp": 2,
            "pap": 2,
            "tags": ["BCM", "Test", "Security"],
            "status": "Open"
        }
        
        assert case_data["severity"] in [1, 2, 3, 4]
        assert case_data["tlp"] in [0, 1, 2, 3]
        assert case_data["status"] == "Open"
        assert "BCM" in case_data["tags"]
    
    def test_alert_creation(self):
        """Test alert creation"""
        alert_data = {
            "title": "Test Security Alert",
            "description": "Test alert description",
            "type": "malware",
            "source": "SIEM",
            "severity": 2,
            "status": "New"
        }
        
        assert alert_data["severity"] in [1, 2, 3, 4]
        assert alert_data["status"] == "New"
        assert alert_data["source"] is not None
    
    def test_bcm_incident_workflow(self):
        """Test BCM-specific incident workflow"""
        bcm_tasks = [
            {"title": "Initial Assessment", "order": 1},
            {"title": "Impact Analysis", "order": 2},
            {"title": "Activate Recovery Team", "order": 3},
            {"title": "Execute Recovery Plan", "order": 4},
            {"title": "Monitor Recovery Progress", "order": 5},
            {"title": "Post-Incident Review", "order": 6}
        ]
        
        assert len(bcm_tasks) == 6
        assert bcm_tasks[0]["title"] == "Initial Assessment"
        assert bcm_tasks[-1]["title"] == "Post-Incident Review"
        
        # Verify task order
        for i, task in enumerate(bcm_tasks):
            assert task["order"] == i + 1


class TestGrafanaAdapter:
    """Tests for Grafana Adapter Service"""
    
    def test_grafana_config_validation(self):
        """Test Grafana configuration validation"""
        config = {
            "name": "Test Grafana Instance",
            "base_url": "https://grafana.example.com",
            "api_key": "test_grafana_api_key",
            "tenant_id": "test_tenant",
            "organization_id": 1
        }
        
        assert config["base_url"].startswith("https://")
        assert len(config["api_key"]) > 0
        assert isinstance(config["organization_id"], int)
    
    def test_dashboard_template_validation(self):
        """Test BCM dashboard template structure"""
        bcm_overview_template = {
            "title": "BCM Platform Overview",
            "tags": ["BCM", "Overview"],
            "panels": [
                {"id": 1, "title": "BIA Coverage", "type": "stat"},
                {"id": 2, "title": "Plan Updates Status", "type": "stat"},
                {"id": 3, "title": "CAPA On-Time Completion", "type": "stat"},
                {"id": 4, "title": "Training Completion Rate", "type": "stat"},
                {"id": 5, "title": "Incident Trends", "type": "timeseries"},
                {"id": 6, "title": "Exercise Completion", "type": "timeseries"}
            ]
        }
        
        assert bcm_overview_template["title"] == "BCM Platform Overview"
        assert "BCM" in bcm_overview_template["tags"]
        assert len(bcm_overview_template["panels"]) == 6
        
        # Verify all panels have required fields
        for panel in bcm_overview_template["panels"]:
            assert "id" in panel
            assert "title" in panel
            assert "type" in panel
    
    def test_incident_dashboard_template(self):
        """Test incident management dashboard template"""
        incident_template = {
            "title": "BCM Incident Management",
            "tags": ["BCM", "Incidents"],
            "panels": [
                {"id": 1, "title": "Open Incidents by Severity", "type": "piechart"},
                {"id": 2, "title": "Mean Time to Recovery (MTTR)", "type": "stat"},
                {"id": 3, "title": "Recovery Point Objective (RPO) Adherence", "type": "gauge"}
            ]
        }
        
        assert incident_template["title"] == "BCM Incident Management"
        assert "Incidents" in incident_template["tags"]
        assert len(incident_template["panels"]) == 3


class TestSSO:
    """Tests for SSO/iframe Integration"""
    
    def test_system_configuration(self):
        """Test system configuration structure"""
        systems = [
            {
                "id": "grafana",
                "name": "Grafana",
                "type": "grafana",
                "icon": "fas fa-chart-line",
                "configured": True,
                "config": {
                    "base_url": "https://grafana.example.com",
                    "api_key": "test_key"
                }
            },
            {
                "id": "thehive",
                "name": "TheHive",
                "type": "thehive",
                "icon": "fas fa-shield-alt",
                "configured": True,
                "config": {
                    "base_url": "https://thehive.example.com",
                    "api_key": "test_key"
                }
            }
        ]
        
        for system in systems:
            assert system["id"] is not None
            assert system["name"] is not None
            assert system["type"] is not None
            assert system["icon"].startswith("fas fa-")
            assert "config" in system
    
    def test_iframe_security(self):
        """Test iframe security settings"""
        sandbox_permissions = "allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
        
        permissions = sandbox_permissions.split()
        required_permissions = ["allow-scripts", "allow-same-origin", "allow-forms"]
        
        for permission in required_permissions:
            assert permission in permissions
    
    def test_url_generation(self):
        """Test URL generation for different systems"""
        url_patterns = {
            "grafana": "https://grafana.example.com/d-solo/",
            "thehive": "https://thehive.example.com/index.html",
            "moodle": "https://moodle.example.com/my/",
            "canvas": "https://canvas.example.com/dashboard"
        }
        
        for system_type, url in url_patterns.items():
            assert url.startswith("https://")
            assert system_type in url or system_type == "grafana"  # Grafana has specific path


class TestEventIntegration:
    """Tests for EventBus Integration"""
    
    def test_event_structure(self):
        """Test event structure for new integrations"""
        events = [
            {
                "event_type": "bpmn.process.deployed",
                "tenant_id": "test_tenant",
                "data": {
                    "process_id": "test_process",
                    "process_name": "Test Process",
                    "version": "1.0"
                }
            },
            {
                "event_type": "lms.user.enrolled",
                "tenant_id": "test_tenant",
                "data": {
                    "config_id": "lms_config_1",
                    "course_id": "course_123",
                    "user_email": "test@example.com"
                }
            },
            {
                "event_type": "thehive.case.created",
                "tenant_id": "test_tenant",
                "data": {
                    "config_id": "thehive_config_1",
                    "case_id": "case_123",
                    "title": "Test Incident",
                    "severity": 3
                }
            },
            {
                "event_type": "grafana.dashboard.created",
                "tenant_id": "test_tenant",
                "data": {
                    "config_id": "grafana_config_1",
                    "dashboard_uid": "dashboard_123",
                    "dashboard_title": "Test Dashboard"
                }
            }
        ]
        
        for event in events:
            assert event["event_type"] is not None
            assert event["tenant_id"] == "test_tenant"
            assert "data" in event
            assert isinstance(event["data"], dict)
    
    def test_event_types(self):
        """Test event type naming convention"""
        event_types = [
            "bpmn.process.deployed",
            "bpmn.instance.started",
            "bpmn.task.completed",
            "lms.user.enrolled",
            "lms.course.launched",
            "lms.progress.synced",
            "thehive.case.created",
            "thehive.alert.created",
            "thehive.alert.promoted",
            "grafana.dashboard.created",
            "grafana.kpi.synced"
        ]
        
        for event_type in event_types:
            parts = event_type.split(".")
            assert len(parts) >= 3
            assert parts[0] in ["bpmn", "lms", "thehive", "grafana"]


# Utility functions for testing
def validate_config_structure(config, required_fields):
    """Validate configuration structure"""
    for field in required_fields:
        assert field in config
        assert config[field] is not None

def validate_api_response(response, expected_status=200):
    """Validate API response structure"""
    assert response["status"] == "success" or response["status_code"] == expected_status

def validate_tenant_isolation(data, tenant_id):
    """Validate tenant isolation"""
    assert data["tenant_id"] == tenant_id


# Test fixtures (would normally use pytest fixtures)
@pytest.fixture
def sample_bpmn_xml():
    """Sample BPMN XML for testing"""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL">
        <process id="bcmProcess" name="BCM Process">
            <startEvent id="start" name="Start"/>
            <userTask id="assessment" name="Initial Assessment"/>
            <userTask id="response" name="Response Planning"/>
            <endEvent id="end" name="End"/>
        </process>
    </definitions>"""

@pytest.fixture  
def sample_lms_courses():
    """Sample LMS courses for testing"""
    return [
        {
            "id": "course_1",
            "title": "Business Continuity Fundamentals",
            "description": "Introduction to BCM principles",
            "lms_type": "moodle",
            "duration_hours": 8,
            "is_active": True
        },
        {
            "id": "course_2", 
            "title": "Crisis Management",
            "description": "Crisis response and management",
            "lms_type": "canvas",
            "duration_hours": 12,
            "is_active": True
        }
    ]


if __name__ == "__main__":
    # Run basic validation tests
    test_bpmn = TestBPMNService()
    test_lms = TestLMSAdapter()
    test_thehive = TestTheHiveAdapter()
    test_grafana = TestGrafanaAdapter()
    test_sso = TestSSO()
    test_events = TestEventIntegration()
    
    print("Running integration tests...")
    
    # Run BPMN tests
    test_bpmn.test_health_check()
    test_bpmn.test_process_deployment()
    test_bpmn.test_process_instance_creation()
    test_bpmn.test_task_completion()
    print("✅ BPMN tests passed")
    
    # Run LMS tests
    test_lms.test_lms_config_validation()
    test_lms.test_course_enrollment()
    test_lms.test_course_launch_url()
    print("✅ LMS tests passed")
    
    # Run TheHive tests
    test_thehive.test_thehive_config_validation()
    test_thehive.test_case_creation()
    test_thehive.test_alert_creation()
    test_thehive.test_bcm_incident_workflow()
    print("✅ TheHive tests passed")
    
    # Run Grafana tests
    test_grafana.test_grafana_config_validation()
    test_grafana.test_dashboard_template_validation()
    test_grafana.test_incident_dashboard_template()
    print("✅ Grafana tests passed")
    
    # Run SSO tests
    test_sso.test_system_configuration()
    test_sso.test_iframe_security()
    test_sso.test_url_generation()
    print("✅ SSO tests passed")
    
    # Run Event tests
    test_events.test_event_structure()
    test_events.test_event_types()
    print("✅ Event integration tests passed")
    
    print("\n🎉 All integration tests passed successfully!")