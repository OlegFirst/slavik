"""
Mock data for BPMN Service testing
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Mock BPMN Process XML
MOCK_BPMN_XML = """<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL" 
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             id="BCM_Incident_Response"
             targetNamespace="http://bcm.platform/bpmn">
  
  <process id="incident_response" name="BCM Incident Response">
    <startEvent id="start_incident" name="Incident Detected">
      <outgoing>seq_1</outgoing>
    </startEvent>
    
    <sequenceFlow id="seq_1" sourceRef="start_incident" targetRef="assess_impact"/>
    
    <userTask id="assess_impact" name="Assess Impact">
      <incoming>seq_1</incoming>
      <outgoing>seq_2</outgoing>
    </userTask>
    
    <sequenceFlow id="seq_2" sourceRef="assess_impact" targetRef="activate_team"/>
    
    <userTask id="activate_team" name="Activate Response Team">
      <incoming>seq_2</incoming>
      <outgoing>seq_3</outgoing>
    </userTask>
    
    <sequenceFlow id="seq_3" sourceRef="activate_team" targetRef="execute_plan"/>
    
    <userTask id="execute_plan" name="Execute Recovery Plan">
      <incoming>seq_3</incoming>
      <outgoing>seq_4</outgoing>
    </userTask>
    
    <sequenceFlow id="seq_4" sourceRef="execute_plan" targetRef="monitor_progress"/>
    
    <userTask id="monitor_progress" name="Monitor Recovery">
      <incoming>seq_4</incoming>
      <outgoing>seq_5</outgoing>
    </userTask>
    
    <sequenceFlow id="seq_5" sourceRef="monitor_progress" targetRef="end_incident"/>
    
    <endEvent id="end_incident" name="Incident Resolved">
      <incoming>seq_5</incoming>
    </endEvent>
  </process>
  
</definitions>"""

def get_mock_processes() -> List[Dict[str, Any]]:
    """Generate mock BPMN processes"""
    return [
        {
            "id": "proc_001",
            "name": "BCM Incident Response",
            "description": "Standard incident response workflow for business continuity",
            "bpmn_xml": MOCK_BPMN_XML,
            "tenant_id": "tenant_001",
            "version": "1.0",
            "is_active": True,
            "created_by": "system_admin"
        },
        {
            "id": "proc_002", 
            "name": "BIA Review Process",
            "description": "Annual business impact analysis review workflow",
            "bpmn_xml": MOCK_BPMN_XML.replace("incident_response", "bia_review").replace("Incident", "BIA"),
            "tenant_id": "tenant_001",
            "version": "1.2",
            "is_active": True,
            "created_by": "bia_manager"
        },
        {
            "id": "proc_003",
            "name": "Plan Testing Workflow", 
            "description": "Quarterly plan testing and validation workflow",
            "bpmn_xml": MOCK_BPMN_XML.replace("incident_response", "plan_testing").replace("Incident", "Test"),
            "tenant_id": "tenant_001", 
            "version": "1.0",
            "is_active": True,
            "created_by": "test_coordinator"
        }
    ]

def get_mock_instances() -> List[Dict[str, Any]]:
    """Generate mock process instances"""
    base_time = datetime.utcnow()
    return [
        {
            "id": "inst_001",
            "process_id": "proc_001",
            "tenant_id": "tenant_001",
            "status": "ACTIVE",
            "variables": {
                "incident_id": "INC_2024_001",
                "severity": "HIGH",
                "affected_systems": ["CRM", "ERP"],
                "incident_manager": "john.doe@company.com"
            },
            "current_activities": ["assess_impact"],
            "started_by": "monitoring_system",
            "started_at": base_time - timedelta(hours=2)
        },
        {
            "id": "inst_002", 
            "process_id": "proc_001",
            "tenant_id": "tenant_001",
            "status": "COMPLETED",
            "variables": {
                "incident_id": "INC_2024_002",
                "severity": "MEDIUM",
                "affected_systems": ["Web Portal"],
                "incident_manager": "jane.smith@company.com",
                "resolution_time": "45 minutes"
            },
            "current_activities": [],
            "started_by": "user_001",
            "started_at": base_time - timedelta(days=1),
            "completed_at": base_time - timedelta(days=1, hours=-1)
        },
        {
            "id": "inst_003",
            "process_id": "proc_002", 
            "tenant_id": "tenant_001",
            "status": "ACTIVE",
            "variables": {
                "bia_year": "2024",
                "reviewer": "bia_team@company.com",
                "departments": ["IT", "Finance", "Operations"]
            },
            "current_activities": ["activate_team"],
            "started_by": "scheduler",
            "started_at": base_time - timedelta(days=3)
        }
    ]

def get_mock_tasks() -> List[Dict[str, Any]]:
    """Generate mock tasks"""
    base_time = datetime.utcnow()
    return [
        {
            "id": "task_001",
            "process_instance_id": "inst_001", 
            "activity_id": "assess_impact",
            "name": "Assess Impact",
            "task_type": "USER_TASK",
            "assignee": "john.doe@company.com",
            "status": "ACTIVE",
            "variables": {
                "priority": "HIGH",
                "deadline": (base_time + timedelta(hours=1)).isoformat()
            },
            "created_at": base_time - timedelta(hours=2)
        },
        {
            "id": "task_002",
            "process_instance_id": "inst_003",
            "activity_id": "activate_team", 
            "name": "Activate Response Team",
            "task_type": "USER_TASK",
            "assignee": "bia_team@company.com",
            "status": "ACTIVE",
            "variables": {
                "team_members": ["analyst1", "analyst2", "manager1"],
                "meeting_scheduled": (base_time + timedelta(hours=4)).isoformat()
            },
            "created_at": base_time - timedelta(days=3)
        },
        {
            "id": "task_003",
            "process_instance_id": "inst_002",
            "activity_id": "monitor_progress",
            "name": "Monitor Recovery", 
            "task_type": "USER_TASK",
            "assignee": "jane.smith@company.com",
            "status": "COMPLETED",
            "variables": {
                "monitoring_interval": "5 minutes",
                "completion_criteria": "System response time < 2s"
            },
            "created_at": base_time - timedelta(days=1),
            "completed_at": base_time - timedelta(days=1, hours=-1)
        }
    ]

def get_workflow_templates() -> List[Dict[str, Any]]:
    """Get predefined BCM workflow templates"""
    return [
        {
            "name": "BCM Incident Response",
            "category": "incident_management", 
            "description": "Standard incident response workflow with escalation paths",
            "steps": [
                "Detect and report incident",
                "Initial assessment and classification", 
                "Activate appropriate response team",
                "Execute recovery procedures",
                "Monitor recovery progress",
                "Post-incident review and documentation"
            ],
            "roles": ["Incident Manager", "Technical Team", "Communication Lead"],
            "estimated_duration": "2-8 hours"
        },
        {
            "name": "BIA Review and Update",
            "category": "bia_management",
            "description": "Annual business impact analysis review process",
            "steps": [
                "Schedule department interviews",
                "Collect business process data",
                "Analyze impact and recovery requirements", 
                "Update BIA documentation",
                "Review and approve changes",
                "Communicate updates to stakeholders"
            ],
            "roles": ["BIA Analyst", "Department Heads", "BCM Manager"],
            "estimated_duration": "4-6 weeks"
        },
        {
            "name": "Plan Testing Exercise",
            "category": "testing",
            "description": "Quarterly business continuity plan testing",
            "steps": [
                "Plan test scenario and scope",
                "Schedule test participants",
                "Execute test scenario",
                "Evaluate performance and gaps",
                "Document lessons learned", 
                "Update plans based on results"
            ],
            "roles": ["Test Coordinator", "Business Units", "IT Support"],
            "estimated_duration": "1-2 days"
        }
    ]