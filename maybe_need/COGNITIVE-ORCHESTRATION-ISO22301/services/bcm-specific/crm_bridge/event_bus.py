#!/usr/bin/env python3
"""
BCM Event Bus - реализует паттерн bridge для связи CRM с BCM модулями
Основано на паттерне из bcm_content_training_bridge
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import httpx

logger = logging.getLogger("bcm_event_bus")

class BcmEvent(BaseModel):
    """BCM Event structure"""
    event_type: str
    source_module: str
    target_module: Optional[str] = None
    project_id: int
    user_id: Optional[int] = None
    data: Dict[str, Any]
    timestamp: datetime = datetime.now()
    priority: str = "normal"  # low, normal, high, critical
    status: str = "pending"  # pending, processing, completed, failed

class BcmEventHandler:
    """Base event handler"""
    def __init__(self, odoo_api_url: str, db_gateway_url: str):
        self.odoo_api_url = odoo_api_url
        self.db_gateway_url = db_gateway_url
        self.session = None

    async def handle_event(self, event: BcmEvent) -> bool:
        """Override in subclasses"""
        raise NotImplementedError

class CrmProjectEventHandler(BcmEventHandler):
    """Handle CRM project lifecycle events"""

    async def handle_event(self, event: BcmEvent) -> bool:
        """Handle CRM project events"""
        try:
            if event.event_type == "project.won":
                return await self._initialize_bcm_workspace(event)
            elif event.event_type == "project.stage_changed":
                return await self._update_project_stage(event)
            elif event.event_type == "project.lost":
                return await self._archive_project_workspace(event)

            return True
        except Exception as e:
            logger.error(f"CRM event handling error: {e}")
            return False

    async def _initialize_bcm_workspace(self, event: BcmEvent) -> bool:
        """Initialize BCM workspace when project is won"""
        project_id = event.project_id
        client_data = event.data

        async with httpx.AsyncClient() as client:
            # Create organization context
            context_data = {
                "database": "odoo",
                "operation": "odoo_create",
                "model": "bcm.context",
                "data": {
                    "name": client_data.get("partner_name", "Unknown Organization"),
                    "crm_project_id": project_id,
                    "maturity_level": "initial",
                    "industry": client_data.get("industry", "general"),
                    "employee_count": client_data.get("employee_count", 0),
                    "compliance_target": client_data.get("compliance_target", "iso_22301"),
                    "setup_date": datetime.now().isoformat()
                }
            }

            response = await client.post(f"{self.db_gateway_url}/query", json=context_data)
            if response.status_code != 200:
                logger.error(f"Failed to create BCM context: {response.text}")
                return False

            # Schedule initial assessment
            assessment_data = {
                "database": "odoo",
                "operation": "odoo_create",
                "model": "bcm.audit",
                "data": {
                    "name": f"Initial BCM Assessment - {client_data.get('partner_name')}",
                    "crm_project_id": project_id,
                    "audit_type": "initial_assessment",
                    "scheduled_date": (datetime.now() + timedelta(days=7)).isoformat(),
                    "assessor_id": client_data.get("project_manager_id"),
                    "status": "scheduled"
                }
            }

            response = await client.post(f"{self.db_gateway_url}/query", json=assessment_data)
            if response.status_code != 200:
                logger.error(f"Failed to schedule assessment: {response.text}")
                return False

            # Create plan templates
            templates_data = {
                "database": "odoo",
                "operation": "odoo_create",
                "model": "bcm.plan",
                "data": {
                    "name": f"BCM Implementation Plan - {client_data.get('partner_name')}",
                    "crm_project_id": project_id,
                    "plan_type": "implementation",
                    "status": "draft",
                    "target_date": (datetime.now() + timedelta(days=90)).isoformat()
                }
            }

            response = await client.post(f"{self.db_gateway_url}/query", json=templates_data)
            logger.info(f"✅ BCM workspace initialized for project {project_id}")

            return True

    async def _update_project_stage(self, event: BcmEvent) -> bool:
        """Update BCM components when project stage changes"""
        stage_name = event.data.get("stage_name", "")
        project_id = event.project_id

        # Stage-specific actions
        stage_actions = {
            "implementation": self._start_implementation_phase,
            "testing": self._schedule_testing_exercises,
            "go_live": self._activate_bcm_plans,
            "support": self._transition_to_support_mode
        }

        handler = stage_actions.get(stage_name.lower())
        if handler:
            return await handler(project_id, event.data)

        return True

    async def _start_implementation_phase(self, project_id: int, data: Dict[str, Any]) -> bool:
        """Start implementation activities"""
        async with httpx.AsyncClient() as client:
            # Schedule training sessions
            training_data = {
                "database": "odoo",
                "operation": "odoo_create",
                "model": "bcm.training",
                "data": {
                    "name": f"BCM Awareness Training - Project {project_id}",
                    "crm_project_id": project_id,
                    "training_type": "awareness",
                    "scheduled_date": (datetime.now() + timedelta(days=14)).isoformat(),
                    "duration": 4.0,
                    "status": "scheduled"
                }
            }

            await client.post(f"{self.db_gateway_url}/query", json=training_data)
            logger.info(f"✅ Implementation phase started for project {project_id}")
            return True

class AuditEventHandler(BcmEventHandler):
    """Handle audit lifecycle events"""

    async def handle_event(self, event: BcmEvent) -> bool:
        """Handle audit events"""
        try:
            if event.event_type == "audit.completed":
                return await self._process_audit_completion(event)
            elif event.event_type == "audit.finding_created":
                return await self._escalate_critical_findings(event)
            elif event.event_type == "audit.compliance_updated":
                return await self._update_crm_compliance_score(event)

            return True
        except Exception as e:
            logger.error(f"Audit event handling error: {e}")
            return False

    async def _process_audit_completion(self, event: BcmEvent) -> bool:
        """Process completed audit"""
        audit_data = event.data
        project_id = event.project_id

        async with httpx.AsyncClient() as client:
            # Update CRM with compliance score
            compliance_score = audit_data.get("compliance_score", 0)

            # Update project in CRM
            crm_update = {
                "database": "odoo",
                "operation": "odoo_write",
                "model": "crm.lead",
                "ids": [project_id],
                "data": {
                    "description": f"Latest Audit Results:\nCompliance Score: {compliance_score}%\nLast Audit: {datetime.now().strftime('%Y-%m-%d')}"
                }
            }

            await client.post(f"{self.db_gateway_url}/query", json=crm_update)

            # Generate action items for low compliance areas
            if compliance_score < 70:
                await self._create_improvement_actions(project_id, audit_data)

            logger.info(f"✅ Audit completion processed for project {project_id}")
            return True

    async def _create_improvement_actions(self, project_id: int, audit_data: Dict[str, Any]) -> bool:
        """Create improvement actions for low compliance areas"""
        async with httpx.AsyncClient() as client:
            findings = audit_data.get("findings", [])

            for finding in findings:
                if finding.get("severity") in ["high", "critical"]:
                    action_data = {
                        "database": "odoo",
                        "operation": "odoo_create",
                        "model": "bcm.action_item",
                        "data": {
                            "name": f"Address: {finding.get('title')}",
                            "crm_project_id": project_id,
                            "description": finding.get("description"),
                            "priority": finding.get("severity"),
                            "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
                            "status": "open"
                        }
                    }

                    await client.post(f"{self.db_gateway_url}/query", json=action_data)

        return True

class IncidentEventHandler(BcmEventHandler):
    """Handle incident events"""

    async def handle_event(self, event: BcmEvent) -> bool:
        """Handle incident events"""
        try:
            if event.event_type == "incident.critical":
                return await self._escalate_to_crm(event)
            elif event.event_type == "incident.resolved":
                return await self._update_incident_stats(event)
            elif event.event_type == "incident.exercise_scheduled":
                return await self._notify_stakeholders(event)

            return True
        except Exception as e:
            logger.error(f"Incident event handling error: {e}")
            return False

    async def _escalate_to_crm(self, event: BcmEvent) -> bool:
        """Escalate critical incident to CRM"""
        incident_data = event.data
        project_id = event.project_id

        async with httpx.AsyncClient() as client:
            # Create CRM activity for critical incident
            activity_data = {
                "database": "odoo",
                "operation": "odoo_create",
                "model": "mail.activity",
                "data": {
                    "res_model": "crm.lead",
                    "res_id": project_id,
                    "activity_type_id": 1,  # TODO: use correct activity type
                    "summary": f"CRITICAL INCIDENT: {incident_data.get('title')}",
                    "note": f"Severity: {incident_data.get('severity')}\nDescription: {incident_data.get('description')}",
                    "date_deadline": datetime.now().date().isoformat(),
                    "user_id": incident_data.get("assigned_to_id")
                }
            }

            await client.post(f"{self.db_gateway_url}/query", json=activity_data)

            # Update project priority
            priority_update = {
                "database": "odoo",
                "operation": "odoo_write",
                "model": "crm.lead",
                "ids": [project_id],
                "data": {
                    "priority": "3"  # High priority
                }
            }

            await client.post(f"{self.db_gateway_url}/query", json=priority_update)

            logger.info(f"🚨 Critical incident escalated to CRM for project {project_id}")
            return True

class GamificationEventHandler(BcmEventHandler):
    """Handle gamification events - based on bcm_content_training_bridge pattern"""

    async def handle_event(self, event: BcmEvent) -> bool:
        """Handle gamification events"""
        try:
            if event.event_type == "content.created":
                return await self._award_creation_points(event)
            elif event.event_type == "training.completed":
                return await self._award_completion_badge(event)
            elif event.event_type == "assessment.passed":
                return await self._award_certification_badge(event)

            return True
        except Exception as e:
            logger.error(f"Gamification event handling error: {e}")
            return False

    async def _award_creation_points(self, event: BcmEvent) -> bool:
        """Award points for content creation"""
        user_id = event.user_id
        content_type = event.data.get("content_type")
        points = 50 if content_type == "template" else 30

        async with httpx.AsyncClient() as client:
            achievement_data = {
                "database": "odoo",
                "operation": "odoo_create",
                "model": "bcm.user.achievement",
                "data": {
                    "user_id": user_id,
                    "points": points,
                    "action_type": "create",
                    "content_type": content_type,
                    "content_ref": f"{content_type},{event.data.get('content_id')}"
                }
            }

            await client.post(f"{self.db_gateway_url}/query", json=achievement_data)
            logger.info(f"🏆 Awarded {points} points to user {user_id} for {content_type} creation")
            return True

class BcmEventBus:
    """Main Event Bus orchestrator"""

    def __init__(self, odoo_api_url: str, db_gateway_url: str):
        self.handlers = {}
        self.event_queue = asyncio.Queue()
        self.running = False

        # Initialize handlers
        self.handlers["crm"] = CrmProjectEventHandler(odoo_api_url, db_gateway_url)
        self.handlers["audit"] = AuditEventHandler(odoo_api_url, db_gateway_url)
        self.handlers["incident"] = IncidentEventHandler(odoo_api_url, db_gateway_url)
        self.handlers["gamification"] = GamificationEventHandler(odoo_api_url, db_gateway_url)

    async def publish_event(self, event: BcmEvent) -> bool:
        """Publish event to the bus"""
        await self.event_queue.put(event)
        logger.info(f"📨 Event published: {event.event_type} from {event.source_module}")
        return True

    async def start_processing(self):
        """Start event processing loop"""
        self.running = True
        logger.info("🚀 BCM Event Bus started")

        while self.running:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._process_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Event processing error: {e}")

    async def stop_processing(self):
        """Stop event processing"""
        self.running = False
        logger.info("🛑 BCM Event Bus stopped")

    async def _process_event(self, event: BcmEvent) -> bool:
        """Process single event"""
        try:
            # Route event to appropriate handler
            handler_name = event.source_module.split("_")[0]  # e.g. "crm" from "crm_project"
            handler = self.handlers.get(handler_name)

            if not handler:
                logger.warning(f"No handler found for {handler_name}")
                return False

            # Process event
            event.status = "processing"
            success = await handler.handle_event(event)

            event.status = "completed" if success else "failed"
            logger.info(f"✅ Event processed: {event.event_type} -> {event.status}")

            return success

        except Exception as e:
            logger.error(f"Event processing failed: {e}")
            event.status = "failed"
            return False

    async def get_event_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            "queue_size": self.event_queue.qsize(),
            "handlers_count": len(self.handlers),
            "status": "running" if self.running else "stopped",
            "handlers": list(self.handlers.keys())
        }