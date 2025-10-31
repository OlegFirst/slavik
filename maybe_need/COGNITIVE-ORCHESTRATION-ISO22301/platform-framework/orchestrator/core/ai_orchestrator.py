"""
AI Orchestrator for BCM Platform
Intelligent event processing and decision engine
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import uuid

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from .event_bus import EventBus, Event, EventType, event_bus

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions the orchestrator can take"""
    GENERATE_PLAN = "generate_plan"
    SUGGEST_RESPONSE = "suggest_response"
    SCHEDULE_TRAINING = "schedule_training"
    RECOMMEND_SCENARIO = "recommend_scenario"
    ANALYZE_COMPLIANCE = "analyze_compliance"
    CREATE_TASK = "create_task"
    SEND_NOTIFICATION = "send_notification"
    TRIGGER_WORKFLOW = "trigger_workflow"


@dataclass
class OrchestratorRule:
    """Rule definition for orchestrator"""
    name: str
    event_type: EventType
    conditions: Dict[str, Any]
    actions: List[ActionType]
    priority: int = 1
    enabled: bool = True


@dataclass
class Decision:
    """AI Orchestrator decision record"""
    id: str
    timestamp: datetime
    event: Event
    rules_applied: List[str]
    actions_taken: List[Dict[str, Any]]
    reasoning: str
    confidence: float
    approved: Optional[bool] = None
    approved_by: Optional[str] = None


class AIOrchestrator:
    """AI-powered orchestration engine for BCM Platform"""
    
    def __init__(self, llm_api_key: Optional[str] = None):
        self.event_bus = event_bus
        self.llm = OpenAI(api_key=llm_api_key) if llm_api_key else None
        self.rules: List[OrchestratorRule] = []
        self.decisions: List[Decision] = []
        self.running = False
        
        # Initialize default rules
        self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize default orchestration rules"""
        
        # Rule 1: Generate BCP after BIA completion
        self.rules.append(OrchestratorRule(
            name="auto_generate_bcp",
            event_type=EventType.BIA_COMPLETED,
            conditions={
                "has_critical_processes": True,
                "plan_exists": False
            },
            actions=[ActionType.GENERATE_PLAN, ActionType.SEND_NOTIFICATION],
            priority=1
        ))
        
        # Rule 2: Suggest incident response actions
        self.rules.append(OrchestratorRule(
            name="incident_response",
            event_type=EventType.INCIDENT_OPENED,
            conditions={
                "severity": ["high", "critical"]
            },
            actions=[ActionType.SUGGEST_RESPONSE, ActionType.TRIGGER_WORKFLOW],
            priority=1
        ))
        
        # Rule 3: Schedule exercise if overdue
        self.rules.append(OrchestratorRule(
            name="schedule_overdue_exercise",
            event_type=EventType.EXERCISE_OVERDUE,
            conditions={
                "days_overdue": 30
            },
            actions=[ActionType.RECOMMEND_SCENARIO, ActionType.CREATE_TASK],
            priority=2
        ))
        
        # Rule 4: Analyze compliance after audit
        self.rules.append(OrchestratorRule(
            name="compliance_analysis",
            event_type=EventType.AUDIT_COMPLETED,
            conditions={
                "findings_count": 0  # Will check if > 0
            },
            actions=[ActionType.ANALYZE_COMPLIANCE, ActionType.GENERATE_PLAN],
            priority=1
        ))
        
        # Rule 5: Schedule training after plan approval
        self.rules.append(OrchestratorRule(
            name="schedule_training",
            event_type=EventType.PLAN_APPROVED,
            conditions={
                "plan_type": ["BCP", "DRP"]
            },
            actions=[ActionType.SCHEDULE_TRAINING, ActionType.SEND_NOTIFICATION],
            priority=2
        ))
    
    async def start(self):
        """Start the orchestrator"""
        self.running = True
        
        # Register event handlers
        for rule in self.rules:
            if rule.enabled:
                self.event_bus.register_handler(
                    rule.event_type,
                    lambda e, r=rule: asyncio.create_task(self.process_event(e, r))
                )
        
        logger.info("AI Orchestrator started with {} rules".format(len(self.rules)))
    
    async def stop(self):
        """Stop the orchestrator"""
        self.running = False
        logger.info("AI Orchestrator stopped")
    
    async def process_event(self, event: Event, rule: OrchestratorRule):
        """Process an event according to a rule"""
        try:
            # Check if conditions are met
            if not self._check_conditions(event, rule.conditions):
                return
            
            logger.info(f"Processing event {event.type.value} with rule {rule.name}")
            
            # Generate decision
            decision = await self._make_decision(event, rule)
            
            # Execute actions
            for action_type in rule.actions:
                await self._execute_action(action_type, event, decision)
            
            # Store decision for audit trail
            self.decisions.append(decision)
            
            # Emit decision event
            await self._emit_decision_event(decision)
            
        except Exception as e:
            logger.error(f"Error processing event with rule {rule.name}: {e}")
    
    def _check_conditions(self, event: Event, conditions: Dict[str, Any]) -> bool:
        """Check if event meets rule conditions"""
        for key, value in conditions.items():
            event_value = event.data.get(key) or event.metadata.get(key)
            
            if isinstance(value, list):
                if event_value not in value:
                    return False
            elif isinstance(value, bool):
                if bool(event_value) != value:
                    return False
            elif isinstance(value, (int, float)):
                if event_value <= value:
                    return False
            else:
                if event_value != value:
                    return False
        
        return True
    
    async def _make_decision(self, event: Event, rule: OrchestratorRule) -> Decision:
        """Make an intelligent decision based on event and rule"""
        reasoning = f"Event {event.type.value} triggered rule {rule.name}"
        confidence = 0.95  # Base confidence
        
        # Use LLM for complex reasoning if available
        if self.llm and event.type in [EventType.BIA_COMPLETED, EventType.INCIDENT_OPENED]:
            reasoning = await self._get_llm_reasoning(event, rule)
            confidence = 0.85  # Slightly lower for LLM decisions
        
        decision = Decision(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event=event,
            rules_applied=[rule.name],
            actions_taken=[],
            reasoning=reasoning,
            confidence=confidence
        )
        
        return decision
    
    async def _get_llm_reasoning(self, event: Event, rule: OrchestratorRule) -> str:
        """Get reasoning from LLM"""
        if not self.llm:
            return "LLM not available"
        
        prompt = PromptTemplate(
            input_variables=["event_type", "event_data", "rule_name"],
            template="""
            As a BCM expert, analyze this event and provide reasoning for the decision:
            
            Event Type: {event_type}
            Event Data: {event_data}
            Rule Applied: {rule_name}
            
            Provide a brief explanation of why this action should be taken:
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            reasoning = await chain.arun(
                event_type=event.type.value,
                event_data=json.dumps(event.data),
                rule_name=rule.name
            )
            return reasoning.strip()
        except Exception as e:
            logger.error(f"LLM reasoning failed: {e}")
            return "Automated decision based on rule conditions"
    
    async def _execute_action(self, action_type: ActionType, 
                            event: Event, decision: Decision):
        """Execute an orchestrator action"""
        try:
            if action_type == ActionType.GENERATE_PLAN:
                await self._generate_plan(event, decision)
            
            elif action_type == ActionType.SUGGEST_RESPONSE:
                await self._suggest_response(event, decision)
            
            elif action_type == ActionType.SCHEDULE_TRAINING:
                await self._schedule_training(event, decision)
            
            elif action_type == ActionType.RECOMMEND_SCENARIO:
                await self._recommend_scenario(event, decision)
            
            elif action_type == ActionType.ANALYZE_COMPLIANCE:
                await self._analyze_compliance(event, decision)
            
            elif action_type == ActionType.CREATE_TASK:
                await self._create_task(event, decision)
            
            elif action_type == ActionType.SEND_NOTIFICATION:
                await self._send_notification(event, decision)
            
            elif action_type == ActionType.TRIGGER_WORKFLOW:
                await self._trigger_workflow(event, decision)
            
            decision.actions_taken.append({
                "type": action_type.value,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "completed"
            })
            
        except Exception as e:
            logger.error(f"Error executing action {action_type.value}: {e}")
            decision.actions_taken.append({
                "type": action_type.value,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "failed",
                "error": str(e)
            })
    
    async def _generate_plan(self, event: Event, decision: Decision):
        """Generate a draft BCP/DRP plan"""
        logger.info(f"Generating plan for tenant {event.tenant_id}")
        
        # Extract BIA data
        bia_data = event.data
        critical_processes = bia_data.get("critical_processes", [])
        
        # Generate plan structure
        plan = {
            "id": str(uuid.uuid4()),
            "type": "BCP",
            "version": "1.0-draft",
            "created_by": "AI Orchestrator",
            "created_at": datetime.utcnow().isoformat(),
            "tenant_id": event.tenant_id,
            "sections": {
                "executive_summary": self._generate_executive_summary(bia_data),
                "critical_processes": critical_processes,
                "recovery_strategies": self._generate_recovery_strategies(critical_processes),
                "communication_plan": self._generate_communication_plan(),
                "testing_schedule": self._generate_testing_schedule()
            },
            "status": "draft",
            "requires_approval": True
        }
        
        # Emit plan generated event
        await event_bus.publish(Event(
            id=str(uuid.uuid4()),
            type=EventType.PLAN_GENERATED,
            timestamp=datetime.utcnow(),
            actor="AI Orchestrator",
            tenant_id=event.tenant_id,
            module="bcm_plans",
            data=plan,
            correlation_id=event.id
        ))
    
    def _generate_executive_summary(self, bia_data: Dict) -> str:
        """Generate executive summary for BCP"""
        return f"""
        This Business Continuity Plan has been automatically generated based on the 
        Business Impact Analysis completed on {datetime.utcnow().date()}.
        
        Critical Processes Identified: {len(bia_data.get('critical_processes', []))}
        Maximum Tolerable Period of Disruption: {bia_data.get('max_mtpd', '4 hours')}
        Recovery Time Objective: {bia_data.get('rto', '2 hours')}
        Recovery Point Objective: {bia_data.get('rpo', '1 hour')}
        """
    
    def _generate_recovery_strategies(self, processes: List[Dict]) -> List[Dict]:
        """Generate recovery strategies for critical processes"""
        strategies = []
        for process in processes:
            strategies.append({
                "process_id": process.get("id"),
                "process_name": process.get("name"),
                "strategy": "Failover to backup site",
                "resources_required": ["Backup systems", "Staff", "Communications"],
                "estimated_recovery_time": "2 hours"
            })
        return strategies
    
    def _generate_communication_plan(self) -> Dict:
        """Generate communication plan template"""
        return {
            "internal": {
                "crisis_team": ["CEO", "CTO", "BCM Manager"],
                "staff": "All hands notification via email and SMS",
                "stakeholders": "Board notification within 1 hour"
            },
            "external": {
                "customers": "Website banner and email notification",
                "vendors": "Direct contact for critical suppliers",
                "media": "Press release if incident > 4 hours"
            }
        }
    
    def _generate_testing_schedule(self) -> List[Dict]:
        """Generate testing schedule"""
        return [
            {
                "type": "Desktop Exercise",
                "frequency": "Quarterly",
                "next_date": (datetime.utcnow() + timedelta(days=90)).isoformat()
            },
            {
                "type": "Simulation",
                "frequency": "Semi-annual",
                "next_date": (datetime.utcnow() + timedelta(days=180)).isoformat()
            },
            {
                "type": "Full Test",
                "frequency": "Annual",
                "next_date": (datetime.utcnow() + timedelta(days=365)).isoformat()
            }
        ]
    
    async def _suggest_response(self, event: Event, decision: Decision):
        """Suggest incident response actions"""
        incident = event.data
        severity = incident.get("severity", "medium")
        
        suggestions = {
            "immediate_actions": [],
            "communication": [],
            "escalation": False
        }
        
        if severity in ["high", "critical"]:
            suggestions["immediate_actions"] = [
                "Activate crisis management team",
                "Assess impact on critical processes",
                "Initiate BCP if required"
            ]
            suggestions["communication"] = [
                "Notify executive team",
                "Prepare stakeholder communications"
            ]
            suggestions["escalation"] = True
        else:
            suggestions["immediate_actions"] = [
                "Document incident details",
                "Identify affected systems",
                "Implement workarounds"
            ]
        
        decision.actions_taken.append({
            "type": "response_suggested",
            "suggestions": suggestions
        })
    
    async def _schedule_training(self, event: Event, decision: Decision):
        """Schedule training for new plan"""
        plan = event.data
        
        training_schedule = {
            "plan_id": plan.get("id"),
            "sessions": [
                {
                    "name": "BCP Overview",
                    "audience": "All Staff",
                    "date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
                    "duration": "1 hour"
                },
                {
                    "name": "Crisis Team Training",
                    "audience": "Crisis Management Team",
                    "date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                    "duration": "2 hours"
                }
            ]
        }
        
        await event_bus.publish(Event(
            id=str(uuid.uuid4()),
            type=EventType.TRAINING_SCHEDULED,
            timestamp=datetime.utcnow(),
            actor="AI Orchestrator",
            tenant_id=event.tenant_id,
            module="bcm_training",
            data=training_schedule,
            correlation_id=event.id
        ))
    
    async def _recommend_scenario(self, event: Event, decision: Decision):
        """Recommend exercise scenario"""
        # Would integrate with scenario hub
        scenario = {
            "name": "Data Center Power Outage",
            "type": "Simulation",
            "duration": "4 hours",
            "objectives": [
                "Test BCP activation",
                "Validate communication procedures",
                "Assess recovery time"
            ]
        }
        
        decision.actions_taken.append({
            "type": "scenario_recommended",
            "scenario": scenario
        })
    
    async def _analyze_compliance(self, event: Event, decision: Decision):
        """Analyze compliance gaps"""
        audit_data = event.data
        findings = audit_data.get("findings", [])
        
        analysis = {
            "total_findings": len(findings),
            "critical": len([f for f in findings if f.get("severity") == "critical"]),
            "iso_clauses_affected": [],
            "recommended_actions": []
        }
        
        decision.actions_taken.append({
            "type": "compliance_analyzed",
            "analysis": analysis
        })
    
    async def _create_task(self, event: Event, decision: Decision):
        """Create task for follow-up"""
        task = {
            "id": str(uuid.uuid4()),
            "title": f"Follow-up: {event.type.value}",
            "description": decision.reasoning,
            "assigned_to": "BCM Manager",
            "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "priority": "high" if "critical" in str(event.data) else "medium"
        }
        
        decision.actions_taken.append({
            "type": "task_created",
            "task": task
        })
    
    async def _send_notification(self, event: Event, decision: Decision):
        """Send notification to relevant parties"""
        notification = {
            "recipients": self._get_notification_recipients(event),
            "subject": f"BCM Alert: {event.type.value}",
            "message": decision.reasoning,
            "channels": ["email", "dashboard"]
        }
        
        decision.actions_taken.append({
            "type": "notification_sent",
            "notification": notification
        })
    
    def _get_notification_recipients(self, event: Event) -> List[str]:
        """Determine notification recipients based on event type"""
        recipients = ["bcm_manager@org.com"]
        
        if event.type in [EventType.INCIDENT_OPENED, EventType.INCIDENT_ESCALATED]:
            recipients.extend(["cto@org.com", "security@org.com"])
        elif event.type == EventType.AUDIT_COMPLETED:
            recipients.extend(["compliance@org.com", "ceo@org.com"])
        
        return recipients
    
    async def _trigger_workflow(self, event: Event, decision: Decision):
        """Trigger automated workflow"""
        workflow = {
            "name": f"workflow_{event.type.value}",
            "triggered_at": datetime.utcnow().isoformat(),
            "steps": self._get_workflow_steps(event)
        }
        
        decision.actions_taken.append({
            "type": "workflow_triggered",
            "workflow": workflow
        })
    
    def _get_workflow_steps(self, event: Event) -> List[str]:
        """Get workflow steps based on event type"""
        if event.type == EventType.INCIDENT_OPENED:
            return [
                "Create incident ticket",
                "Assign to response team",
                "Start impact assessment",
                "Initiate communication protocol"
            ]
        elif event.type == EventType.BIA_COMPLETED:
            return [
                "Generate BCP draft",
                "Schedule review meeting",
                "Assign reviewers",
                "Set approval deadline"
            ]
        return []
    
    async def _emit_decision_event(self, decision: Decision):
        """Emit event about orchestrator decision"""
        # This creates an audit trail of all AI decisions
        logger.info(f"Decision made: {decision.id} - {decision.reasoning}")
    
    def get_decision_history(self, tenant_id: str, 
                           limit: int = 100) -> List[Decision]:
        """Get history of orchestrator decisions"""
        tenant_decisions = [
            d for d in self.decisions 
            if d.event.tenant_id == tenant_id
        ]
        return tenant_decisions[-limit:]
    
    def get_pending_approvals(self, tenant_id: str) -> List[Decision]:
        """Get decisions pending approval"""
        return [
            d for d in self.decisions
            if d.event.tenant_id == tenant_id and d.approved is None
        ]
    
    async def approve_decision(self, decision_id: str, 
                              approved_by: str,
                              approved: bool = True):
        """Approve or reject an orchestrator decision"""
        for decision in self.decisions:
            if decision.id == decision_id:
                decision.approved = approved
                decision.approved_by = approved_by
                logger.info(f"Decision {decision_id} {'approved' if approved else 'rejected'} by {approved_by}")
                break


# Singleton instance
orchestrator = AIOrchestrator()
