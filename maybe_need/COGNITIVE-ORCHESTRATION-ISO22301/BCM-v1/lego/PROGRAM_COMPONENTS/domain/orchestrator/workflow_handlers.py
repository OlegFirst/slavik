"""
Workflow Handlers for BCM BPMN Processes
Maps BPMN tasks to actual system operations
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import uuid

from .event_bus import EventBus, Event, EventType, event_bus
from .ai_orchestrator import AIOrchestrator, orchestrator

logger = logging.getLogger(__name__)


@dataclass
class WorkflowContext:
    """Context for workflow execution"""
    process_id: str
    tenant_id: str
    user_id: str
    variables: Dict[str, Any]
    current_task: str
    status: str = "active"
    created_at: datetime = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()


class BIAWorkflowHandler:
    """Handler for BIA Subprocess from BPMN"""
    
    def __init__(self):
        self.event_bus = event_bus
        self.contexts: Dict[str, WorkflowContext] = {}
    
    async def start_bia_process(self, tenant_id: str, user_id: str, 
                                departments: List[str]) -> str:
        """Start BIA subprocess - maps to SubProcess_BIA in BPMN"""
        process_id = str(uuid.uuid4())
        
        context = WorkflowContext(
            process_id=process_id,
            tenant_id=tenant_id,
            user_id=user_id,
            variables={
                "departments": departments,
                "surveys_completed": [],
                "metrics": {},
                "critical_processes": []
            },
            current_task="Task_BIA_Survey"
        )
        
        self.contexts[process_id] = context
        
        # Emit BIA started event
        await event_bus.publish(Event(
            id=str(uuid.uuid4()),
            type=EventType.BIA_STARTED,
            timestamp=datetime.utcnow(),
            actor=user_id,
            tenant_id=tenant_id,
            module="bcm_bia",
            data={"process_id": process_id, "departments": departments}
        ))
        
        # Start survey collection
        await self.collect_bia_surveys(context)
        
        return process_id
    
    async def collect_bia_surveys(self, context: WorkflowContext):
        """Task_BIA_Survey - Multi-instance for each department"""
        departments = context.variables["departments"]
        
        # In real implementation, this would create tasks for each department
        survey_tasks = []
        for dept in departments:
            task = self._create_survey_task(context.tenant_id, dept)
            survey_tasks.append(task)
        
        # Wait for all surveys (in production, this would be async with callbacks)
        # For now, simulate completion
        await asyncio.sleep(1)
        
        context.variables["surveys_completed"] = departments
        context.current_task = "Task_BIA_Calculate"
        
        # Move to calculation
        await self.calculate_bia_metrics(context)
    
    async def calculate_bia_metrics(self, context: WorkflowContext):
        """Task_BIA_Calculate - Calculate MTPD/RTO/RPO"""
        
        # Simulate BIA calculation engine
        metrics = {
            "mtpd": {},  # Maximum Tolerable Period of Disruption
            "rto": {},   # Recovery Time Objective
            "rpo": {},   # Recovery Point Objective
            "criticality": {}
        }
        
        for dept in context.variables["departments"]:
            # In production, this would call the actual BIA engine
            metrics["mtpd"][dept] = "4 hours"
            metrics["rto"][dept] = "2 hours"
            metrics["rpo"][dept] = "1 hour"
            metrics["criticality"][dept] = self._calculate_criticality(dept)
        
        context.variables["metrics"] = metrics
        context.current_task = "Task_BIA_Prioritize"
        
        # Move to prioritization
        await self.prioritize_processes(context)
    
    async def prioritize_processes(self, context: WorkflowContext):
        """Task_BIA_Prioritize - Business rule task"""
        
        metrics = context.variables["metrics"]
        critical_processes = []
        
        # Apply criticality matrix (business rules)
        for dept, criticality in metrics["criticality"].items():
            if criticality >= 4:  # Critical threshold
                critical_processes.append({
                    "department": dept,
                    "criticality": criticality,
                    "mtpd": metrics["mtpd"][dept],
                    "rto": metrics["rto"][dept],
                    "rpo": metrics["rpo"][dept]
                })
        
        context.variables["critical_processes"] = critical_processes
        context.status = "completed"
        
        # Emit BIA completed event - triggers AI Orchestrator
        await event_bus.publish(Event(
            id=str(uuid.uuid4()),
            type=EventType.BIA_COMPLETED,
            timestamp=datetime.utcnow(),
            actor=context.user_id,
            tenant_id=context.tenant_id,
            module="bcm_bia",
            data={
                "process_id": context.process_id,
                "critical_processes": critical_processes,
                "metrics": metrics,
                "has_critical_processes": len(critical_processes) > 0
            }
        ))
    
    def _create_survey_task(self, tenant_id: str, department: str) -> Dict:
        """Create survey task for department"""
        return {
            "id": str(uuid.uuid4()),
            "type": "bia_survey",
            "department": department,
            "questions": [
                "What are your critical business functions?",
                "What is the maximum tolerable downtime?",
                "What resources are essential for recovery?",
                "What are the upstream/downstream dependencies?"
            ],
            "status": "pending"
        }
    
    def _calculate_criticality(self, department: str) -> int:
        """Calculate criticality score (1-5)"""
        # Simplified logic - in production would use actual metrics
        critical_depts = ["Emergency", "ICU", "Surgery", "IT", "Finance"]
        if any(crit in department for crit in critical_depts):
            return 5
        return 3


class IncidentWorkflowHandler:
    """Handler for Incident Management Subprocess"""
    
    def __init__(self):
        self.event_bus = event_bus
        self.orchestrator = orchestrator
        self.active_incidents: Dict[str, Dict] = {}
    
    async def handle_incident_detected(self, event: Event):
        """Incident_Start - Triggered by event"""
        incident_data = event.data
        incident_id = incident_data.get("id", str(uuid.uuid4()))
        
        self.active_incidents[incident_id] = {
            "id": incident_id,
            "tenant_id": event.tenant_id,
            "status": "detected",
            "severity": incident_data.get("severity", "medium"),
            "type": incident_data.get("type", "unknown"),
            "detected_at": datetime.utcnow(),
            "response_plan": None
        }
        
        # Task_Inc_NotifyAI - Notify AI Orchestrator
        await self.notify_ai_orchestrator(incident_id)
    
    async def notify_ai_orchestrator(self, incident_id: str):
        """Task_Inc_NotifyAI"""
        incident = self.active_incidents[incident_id]
        
        # Emit incident opened event for AI processing
        await event_bus.publish(Event(
            id=str(uuid.uuid4()),
            type=EventType.INCIDENT_OPENED,
            timestamp=datetime.utcnow(),
            actor="system",
            tenant_id=incident["tenant_id"],
            module="bcm_incident",
            data=incident
        ))
        
        # AI Orchestrator will process and suggest response
        # Simulate receiving response (in production, this would be async)
        await asyncio.sleep(2)
        await self.receive_response_plan(incident_id)
    
    async def receive_response_plan(self, incident_id: str):
        """Task_Inc_ReceiveSuggestion"""
        incident = self.active_incidents[incident_id]
        
        # Response plan from AI Orchestrator
        response_plan = {
            "incident_id": incident_id,
            "immediate_actions": [
                "Activate incident response team",
                "Assess impact on critical processes",
                "Initiate communication protocol"
            ],
            "recovery_steps": [
                "Switch to backup systems",
                "Redirect traffic to DR site",
                "Monitor service restoration"
            ],
            "communication": {
                "internal": ["Send all-hands notification"],
                "external": ["Update status page", "Notify key customers"]
            },
            "estimated_resolution": "2 hours"
        }
        
        incident["response_plan"] = response_plan
        incident["status"] = "responding"
        
        # Move to execution
        await self.execute_response(incident_id)
    
    async def execute_response(self, incident_id: str):
        """Task_Inc_Execute"""
        incident = self.active_incidents[incident_id]
        
        # Log response execution
        execution_log = {
            "incident_id": incident_id,
            "started_at": datetime.utcnow(),
            "actions_taken": [],
            "status": "in_progress"
        }
        
        # Execute each action (simulated)
        for action in incident["response_plan"]["immediate_actions"]:
            execution_log["actions_taken"].append({
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
                "result": "completed"
            })
        
        incident["execution_log"] = execution_log
        incident["status"] = "contained"
        
        # Document lessons learned
        await self.document_lessons(incident_id)
    
    async def document_lessons(self, incident_id: str):
        """Task_Inc_Document"""
        incident = self.active_incidents[incident_id]
        
        lessons = {
            "incident_id": incident_id,
            "what_went_well": [
                "Quick detection through monitoring",
                "Effective team communication"
            ],
            "what_needs_improvement": [
                "Initial response time",
                "Documentation updates"
            ],
            "action_items": [
                "Update incident response playbook",
                "Schedule additional training"
            ]
        }
        
        incident["lessons_learned"] = lessons
        incident["status"] = "resolved"
        incident["resolved_at"] = datetime.utcnow()
        
        # Emit incident resolved event
        await event_bus.publish(Event(
            id=str(uuid.uuid4()),
            type=EventType.INCIDENT_RESOLVED,
            timestamp=datetime.utcnow(),
            actor="system",
            tenant_id=incident["tenant_id"],
            module="bcm_incident",
            data=incident
        ))


class AuditWorkflowHandler:
    """Handler for Audit Subprocess"""
    
    def __init__(self):
        self.event_bus = event_bus
        self.audit_sessions: Dict[str, Dict] = {}
    
    async def start_audit_process(self, tenant_id: str, auditor_id: str,
                                  audit_type: str = "ISO_22301") -> str:
        """Start audit subprocess - maps to SubProcess_Audit"""
        audit_id = str(uuid.uuid4())
        
        self.audit_sessions[audit_id] = {
            "id": audit_id,
            "tenant_id": tenant_id,
            "auditor_id": auditor_id,
            "type": audit_type,
            "started_at": datetime.utcnow(),
            "checklist": self._generate_audit_checklist(audit_type),
            "evidence": [],
            "findings": [],
            "capa_plan": None,
            "status": "in_progress"
        }
        
        # Emit audit started event
        await event_bus.publish(Event(
            id=str(uuid.uuid4()),
            type=EventType.AUDIT_STARTED,
            timestamp=datetime.utcnow(),
            actor=auditor_id,
            tenant_id=tenant_id,
            module="bcm_audit",
            data={"audit_id": audit_id, "type": audit_type}
        ))
        
        return audit_id
    
    def _generate_audit_checklist(self, audit_type: str) -> List[Dict]:
        """Generate audit checklist based on ISO 22301"""
        if audit_type != "ISO_22301":
            return []
        
        return [
            {
                "clause": "4.1",
                "title": "Understanding the organization and its context",
                "questions": [
                    "Has the organization determined external and internal issues?",
                    "Are these issues reviewed and updated?"
                ],
                "compliant": None,
                "evidence": []
            },
            {
                "clause": "4.2",
                "title": "Understanding needs and expectations of interested parties",
                "questions": [
                    "Have interested parties been identified?",
                    "Are their requirements documented?"
                ],
                "compliant": None,
                "evidence": []
            },
            {
                "clause": "5.2",
                "title": "Policy",
                "questions": [
                    "Is there a documented BCM policy?",
                    "Is it communicated throughout the organization?"
                ],
                "compliant": None,
                "evidence": []
            },
            {
                "clause": "6.1",
                "title": "Actions to address risks and opportunities",
                "questions": [
                    "Are risks and opportunities identified?",
                    "Are mitigation plans in place?"
                ],
                "compliant": None,
                "evidence": []
            },
            {
                "clause": "8.2",
                "title": "Business impact analysis",
                "questions": [
                    "Has BIA been conducted?",
                    "Are RTO/RPO defined for critical processes?"
                ],
                "compliant": None,
                "evidence": []
            },
            {
                "clause": "8.4",
                "title": "Business continuity plans",
                "questions": [
                    "Are BCPs documented and current?",
                    "Do they cover all critical processes?"
                ],
                "compliant": None,
                "evidence": []
            },
            {
                "clause": "8.5",
                "title": "Exercise program",
                "questions": [
                    "Is there an exercise schedule?",
                    "Are exercises conducted as planned?"
                ],
                "compliant": None,
                "evidence": []
            }
        ]
    
    async def complete_checklist(self, audit_id: str, 
                                 checklist_responses: List[Dict]):
        """Task_Audit_Checklist"""
        audit = self.audit_sessions[audit_id]
        
        # Update checklist with responses
        for i, response in enumerate(checklist_responses):
            if i < len(audit["checklist"]):
                audit["checklist"][i]["compliant"] = response.get("compliant")
                audit["checklist"][i]["evidence"] = response.get("evidence", [])
        
        # Identify non-compliances
        findings = []
        for item in audit["checklist"]:
            if item["compliant"] is False:
                findings.append({
                    "clause": item["clause"],
                    "title": item["title"],
                    "severity": "major" if item["clause"].startswith("8") else "minor",
                    "description": f"Non-compliance with ISO 22301 clause {item['clause']}"
                })
        
        audit["findings"] = findings
        
        # Move to AI analysis
        await self.ai_compliance_analysis(audit_id)
    
    async def ai_compliance_analysis(self, audit_id: str):
        """Task_Audit_AIAnalysis"""
        audit = self.audit_sessions[audit_id]
        
        # AI analyzes compliance gaps
        analysis = {
            "compliance_score": self._calculate_compliance_score(audit["checklist"]),
            "critical_gaps": [f for f in audit["findings"] if f["severity"] == "major"],
            "recommendations": self._generate_recommendations(audit["findings"]),
            "risk_level": "high" if len(audit["findings"]) > 5 else "medium"
        }
        
        audit["ai_analysis"] = analysis
        
        # Create CAPA plan
        await self.create_capa_plan(audit_id)
    
    async def create_capa_plan(self, audit_id: str):
        """Task_Audit_CAPA"""
        audit = self.audit_sessions[audit_id]
        
        capa_items = []
        for finding in audit["findings"]:
            capa_items.append({
                "id": str(uuid.uuid4()),
                "finding_ref": finding["clause"],
                "corrective_action": f"Address non-compliance in {finding['title']}",
                "preventive_action": f"Implement controls to prevent recurrence",
                "responsible": "BCM Manager",
                "target_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "status": "open"
            })
        
        audit["capa_plan"] = {
            "id": str(uuid.uuid4()),
            "audit_id": audit_id,
            "items": capa_items,
            "created_at": datetime.utcnow().isoformat()
        }
        
        audit["status"] = "completed"
        
        # Emit audit completed event
        await event_bus.publish(Event(
            id=str(uuid.uuid4()),
            type=EventType.AUDIT_COMPLETED,
            timestamp=datetime.utcnow(),
            actor=audit["auditor_id"],
            tenant_id=audit["tenant_id"],
            module="bcm_audit",
            data={
                "audit_id": audit_id,
                "findings_count": len(audit["findings"]),
                "compliance_score": audit["ai_analysis"]["compliance_score"],
                "capa_items": len(capa_items)
            }
        ))
    
    def _calculate_compliance_score(self, checklist: List[Dict]) -> float:
        """Calculate overall compliance score"""
        total = len(checklist)
        compliant = sum(1 for item in checklist if item["compliant"] is True)
        return round((compliant / total) * 100, 2) if total > 0 else 0
    
    def _generate_recommendations(self, findings: List[Dict]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if any(f["clause"].startswith("8.2") for f in findings):
            recommendations.append("Conduct comprehensive BIA for all processes")
        
        if any(f["clause"].startswith("8.4") for f in findings):
            recommendations.append("Update and test all business continuity plans")
        
        if any(f["clause"].startswith("8.5") for f in findings):
            recommendations.append("Establish regular exercise schedule")
        
        return recommendations


class GovernanceWorkflowHandler:
    """Handler for Management Review Process"""
    
    def __init__(self):
        self.event_bus = event_bus
    
    async def conduct_management_review(self, tenant_id: str, 
                                       review_data: Dict) -> Dict:
        """Task_ManagementReview"""
        
        review = {
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "date": datetime.utcnow().isoformat(),
            "kpi_achievement": review_data.get("kpi_achievement", 0),
            "incidents_handled": review_data.get("incidents_handled", 0),
            "compliance_score": review_data.get("compliance_score", 0),
            "audit_findings": review_data.get("audit_findings", []),
            "decisions": [],
            "improvements_needed": False
        }
        
        # Apply strategic decision rules
        decisions = self._make_strategic_decisions(review)
        review["decisions"] = decisions
        
        # Determine if improvements are needed
        review["improvements_needed"] = (
            review["compliance_score"] < 80 or
            review["kpi_achievement"] < 75 or
            len(review["audit_findings"]) > 5
        )
        
        # Emit management review completed
        await event_bus.publish(Event(
            id=str(uuid.uuid4()),
            type=EventType.MANAGEMENT_REVIEW_COMPLETED,
            timestamp=datetime.utcnow(),
            actor="leadership",
            tenant_id=tenant_id,
            module="bcm_governance",
            data=review
        ))
        
        return review
    
    def _make_strategic_decisions(self, review: Dict) -> List[Dict]:
        """Business rule task for strategic decisions"""
        decisions = []
        
        if review["compliance_score"] < 70:
            decisions.append({
                "type": "critical",
                "decision": "Immediate compliance remediation required",
                "action": "Allocate resources for compliance improvement"
            })
        
        if review["kpi_achievement"] < 60:
            decisions.append({
                "type": "improvement",
                "decision": "Review and update KPI targets",
                "action": "Conduct root cause analysis of KPI gaps"
            })
        
        if review["incidents_handled"] > 10:
            decisions.append({
                "type": "preventive",
                "decision": "Strengthen incident prevention measures",
                "action": "Increase exercise frequency"
            })
        
        return decisions


# Main workflow orchestrator that ties everything together
class BCMWorkflowOrchestrator:
    """Main orchestrator for all BCM workflows"""
    
    def __init__(self):
        self.bia_handler = BIAWorkflowHandler()
        self.incident_handler = IncidentWorkflowHandler()
        self.audit_handler = AuditWorkflowHandler()
        self.governance_handler = GovernanceWorkflowHandler()
        
        # Register event handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all workflow event handlers"""
        
        # BIA events
        event_bus.register_handler(
            EventType.CONTEXT_IMPORTED,
            lambda e: asyncio.create_task(
                self.bia_handler.start_bia_process(
                    e.tenant_id, e.actor, e.data.get("departments", [])
                )
            )
        )
        
        # Incident events
        event_bus.register_handler(
            EventType.INCIDENT_OPENED,
            lambda e: asyncio.create_task(
                self.incident_handler.handle_incident_detected(e)
            )
        )
        
        # Audit events
        event_bus.register_handler(
            EventType.AUDIT_SCHEDULED,
            lambda e: asyncio.create_task(
                self.audit_handler.start_audit_process(
                    e.tenant_id, e.actor, e.data.get("type", "ISO_22301")
                )
            )
        )
    
    async def execute_pdca_cycle(self, tenant_id: str, user_id: str) -> str:
        """Execute complete PDCA cycle as defined in BPMN"""
        cycle_id = str(uuid.uuid4())
        
        logger.info(f"Starting PDCA cycle {cycle_id} for tenant {tenant_id}")
        
        # This would coordinate the entire PDCA cycle
        # matching the flow defined in BCM_PDCA_Collaboration.bpmn
        
        return cycle_id


# Singleton instance
workflow_orchestrator = BCMWorkflowOrchestrator()
