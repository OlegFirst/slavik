"""
Event Bus Adapters for BCM Platform
Connects existing integrations with the central Event Bus
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
import structlog

# Import Event Bus
import sys
sys.path.append('../core/event_bus')
from event_bus import EventBus, Event, EventType, emit_incident_opened, emit_document_analyzed

logger = structlog.get_logger()


class TheHiveEventAdapter:
    """Adapter for TheHive integration with Event Bus"""
    
    def __init__(self, event_bus: EventBus, thehive_client):
        self.event_bus = event_bus
        self.thehive_client = thehive_client
        
        # Register event handlers
        self.event_bus.register_handler(EventType.INCIDENT_OPENED, self.handle_incident_opened)
        self.event_bus.register_handler(EventType.INCIDENT_UPDATED, self.handle_incident_updated)
    
    async def handle_incident_opened(self, event: Event):
        """Handle incident opened event - create case in TheHive"""
        try:
            incident_data = event.data
            
            # Create case in TheHive
            case_data = {
                'title': incident_data.get('title', 'BCM Incident'),
                'description': incident_data.get('description', ''),
                'severity': self._map_severity(incident_data.get('severity', 'medium')),
                'tags': ['bcm', 'incident', event.tenant_id],
                'customFields': {
                    'bcm_incident_id': incident_data.get('id'),
                    'bcm_tenant_id': event.tenant_id,
                    'bcm_company_id': event.company_id
                }
            }
            
            thehive_case = await self.thehive_client.create_case(case_data)
            
            # Update incident with TheHive case ID
            await self._update_incident_with_case_id(
                incident_data.get('id'), 
                thehive_case.get('_id'),
                event.tenant_id
            )
            
            logger.info("Created TheHive case for BCM incident", 
                       incident_id=incident_data.get('id'),
                       case_id=thehive_case.get('_id'))
        
        except Exception as e:
            logger.error("Failed to create TheHive case", 
                        incident_id=event.data.get('id'), 
                        error=str(e))
    
    async def handle_incident_updated(self, event: Event):
        """Handle incident updated event - update case in TheHive"""
        try:
            incident_data = event.data
            case_id = incident_data.get('thehive_case_id')
            
            if case_id:
                update_data = {
                    'description': incident_data.get('description', ''),
                    'severity': self._map_severity(incident_data.get('severity', 'medium')),
                    'status': self._map_status(incident_data.get('status', 'open'))
                }
                
                await self.thehive_client.update_case(case_id, update_data)
                
                logger.info("Updated TheHive case", 
                           incident_id=incident_data.get('id'),
                           case_id=case_id)
        
        except Exception as e:
            logger.error("Failed to update TheHive case", error=str(e))
    
    def _map_severity(self, bcm_severity: str) -> int:
        """Map BCM severity to TheHive severity levels"""
        mapping = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        return mapping.get(bcm_severity, 2)
    
    def _map_status(self, bcm_status: str) -> str:
        """Map BCM incident status to TheHive case status"""
        mapping = {
            'open': 'Open',
            'in_progress': 'Open',
            'resolved': 'Resolved',
            'closed': 'Resolved'
        }
        return mapping.get(bcm_status, 'Open')
    
    async def _update_incident_with_case_id(self, incident_id: str, case_id: str, tenant_id: str):
        """Update BCM incident with TheHive case ID"""
        # This would typically call the BCM API to update the incident
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"http://bcm-api:8001/api/v1/companies/{tenant_id}/incidents/{incident_id}",
                    json={"thehive_case_id": case_id},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
        except Exception as e:
            logger.error("Failed to update incident with case ID", error=str(e))


class MoodleEventAdapter:
    """Adapter for Moodle LMS integration with Event Bus"""
    
    def __init__(self, event_bus: EventBus, moodle_client):
        self.event_bus = event_bus
        self.moodle_client = moodle_client
        
        # Register event handlers
        self.event_bus.register_handler(EventType.TRAINING_SCHEDULED, self.handle_training_scheduled)
        self.event_bus.register_handler(EventType.TRAINING_COMPLETED, self.handle_training_completed)
    
    async def handle_training_scheduled(self, event: Event):
        """Handle training scheduled event"""
        try:
            training_data = event.data
            
            # Create or enroll user in Moodle course
            user_data = {
                'username': event.actor,
                'email': training_data.get('user_email'),
                'firstname': training_data.get('user_first_name', ''),
                'lastname': training_data.get('user_last_name', '')
            }
            
            # Get or create user
            user_id = await self.moodle_client.get_or_create_user(user_data)
            
            # Enroll in course
            course_id = training_data.get('course_id')
            if course_id:
                await self.moodle_client.enroll_user(user_id, course_id)
                
                logger.info("Enrolled user in Moodle course", 
                           user_id=user_id, 
                           course_id=course_id,
                           tenant_id=event.tenant_id)
        
        except Exception as e:
            logger.error("Failed to handle training scheduled", error=str(e))
    
    async def handle_training_completed(self, event: Event):
        """Handle training completed event - update KPIs"""
        try:
            training_data = event.data
            
            # Emit KPI update event
            kpi_event = Event(
                id=f"kpi_training_{event.id}",
                type=EventType.KPI_CALCULATED,
                timestamp=datetime.utcnow(),
                actor="system",
                tenant_id=event.tenant_id,
                company_id=event.company_id,
                module="bcm_kpi",
                data={
                    'kpi_name': 'training_completion',
                    'user_id': event.actor,
                    'course_id': training_data.get('course_id'),
                    'completion_date': training_data.get('completion_date'),
                    'score': training_data.get('score', 0)
                },
                correlation_id=event.correlation_id
            )
            
            await self.event_bus.publish(kpi_event)
            
            logger.info("Published KPI update for training completion", 
                       user_id=event.actor,
                       course_id=training_data.get('course_id'))
        
        except Exception as e:
            logger.error("Failed to handle training completed", error=str(e))


class SimulationEventAdapter:
    """Adapter for Simulation/Exercise integration with Event Bus"""
    
    def __init__(self, event_bus: EventBus, simulation_client):
        self.event_bus = event_bus
        self.simulation_client = simulation_client
        
        # Register event handlers
        self.event_bus.register_handler(EventType.EXERCISE_SCHEDULED, self.handle_exercise_scheduled)
    
    async def handle_exercise_scheduled(self, event: Event):
        """Handle exercise scheduled event - start simulation if required"""
        try:
            exercise_data = event.data
            
            if exercise_data.get('simulation_enabled', False):
                simulation_config = {
                    'scenario_type': exercise_data.get('scenario_type', 'system_failure'),
                    'duration': exercise_data.get('duration_minutes', 60),
                    'participants': exercise_data.get('participants', []),
                    'objectives': exercise_data.get('objectives', []),
                    'tenant_id': event.tenant_id,
                    'exercise_id': exercise_data.get('id')
                }
                
                # Start simulation
                simulation_id = await self.simulation_client.start_simulation(simulation_config)
                
                # Update exercise with simulation ID
                await self._update_exercise_with_simulation_id(
                    exercise_data.get('id'),
                    simulation_id,
                    event.tenant_id
                )
                
                logger.info("Started simulation for exercise", 
                           exercise_id=exercise_data.get('id'),
                           simulation_id=simulation_id)
        
        except Exception as e:
            logger.error("Failed to start simulation for exercise", error=str(e))
    
    async def _update_exercise_with_simulation_id(self, exercise_id: str, simulation_id: str, tenant_id: str):
        """Update exercise with simulation ID"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"http://bcm-api:8001/api/v1/companies/{tenant_id}/exercises/{exercise_id}",
                    json={"simulation_id": simulation_id},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
        except Exception as e:
            logger.error("Failed to update exercise with simulation ID", error=str(e))


class DocumentProcessorEventAdapter:
    """Adapter for Document Processor integration with Event Bus"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
        # Register event handlers
        self.event_bus.register_handler(EventType.DOC_UPLOADED, self.handle_document_uploaded)
    
    async def handle_document_uploaded(self, event: Event):
        """Handle document uploaded event - trigger analysis"""
        try:
            doc_data = event.data
            
            # Call document processor API for analysis
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://document-processor:8002/api/v1/analyze",
                    json={
                        'document_id': doc_data.get('document_id'),
                        'tenant_id': event.tenant_id,
                        'document_type': doc_data.get('document_type', 'unknown')
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    analysis_result = response.json()
                    
                    # Emit document analyzed event
                    await emit_document_analyzed(
                        event.tenant_id,
                        event.company_id,
                        "document-processor",
                        {
                            'document_id': doc_data.get('document_id'),
                            'analysis_result': analysis_result
                        },
                        analysis_result.get('compliance_score', 0.0)
                    )
                    
                    logger.info("Document analysis completed", 
                               document_id=doc_data.get('document_id'),
                               compliance_score=analysis_result.get('compliance_score'))
        
        except Exception as e:
            logger.error("Failed to process document analysis", error=str(e))


class NotificationEventAdapter:
    """Adapter for Notifications Worker integration with Event Bus"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
        # Register event handlers for notification triggers
        self.event_bus.register_handler(EventType.INCIDENT_OPENED, self.handle_critical_incident)
        self.event_bus.register_handler(EventType.CAPA_OVERDUE, self.handle_capa_overdue)
        self.event_bus.register_handler(EventType.KPI_THRESHOLD_BREACH, self.handle_kpi_breach)
        self.event_bus.register_handler(EventType.DOC_LOW_SCORE, self.handle_low_score_document)
    
    async def handle_critical_incident(self, event: Event):
        """Handle critical incident - send notifications"""
        incident_data = event.data
        severity = event.metadata.get('severity', 'medium')
        
        if severity == 'high':
            await self._send_notification({
                'type': 'incident_opened',
                'title': f"Critical Incident: {incident_data.get('title')}",
                'message': incident_data.get('description', ''),
                'tenant_id': event.tenant_id,
                'company_id': event.company_id,
                'urgency': 'high',
                'channels': ['email', 'slack']
            })
    
    async def handle_capa_overdue(self, event: Event):
        """Handle overdue CAPA - send notifications"""
        capa_data = event.data
        
        await self._send_notification({
            'type': 'capa_overdue',
            'title': f"Overdue CAPA: {capa_data.get('title')}",
            'message': f"CAPA #{capa_data.get('id')} is overdue. Please take action.",
            'tenant_id': event.tenant_id,
            'company_id': event.company_id,
            'urgency': 'high',
            'channels': ['email']
        })
    
    async def handle_kpi_breach(self, event: Event):
        """Handle KPI threshold breach - send notifications"""
        kpi_data = event.data
        
        await self._send_notification({
            'type': 'kpi_breach',
            'title': f"KPI Threshold Breach: {kpi_data.get('kpi_name')}",
            'message': f"KPI {kpi_data.get('kpi_name')} has breached threshold.",
            'tenant_id': event.tenant_id,
            'company_id': event.company_id,
            'urgency': 'medium',
            'channels': ['email']
        })
    
    async def handle_low_score_document(self, event: Event):
        """Handle low compliance score document - send notifications"""
        doc_data = event.data
        score = event.metadata.get('compliance_score', 0)
        
        await self._send_notification({
            'type': 'document_low_score',
            'title': f"Low Compliance Score Document",
            'message': f"Document has compliance score of {score:.2f}. Review recommended.",
            'tenant_id': event.tenant_id,
            'company_id': event.company_id,
            'urgency': 'low',
            'channels': ['email']
        })
    
    async def _send_notification(self, notification_data: Dict[str, Any]):
        """Send notification via notifications worker"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://notifications-worker:8003/api/v1/send",
                    json=notification_data,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                logger.info("Notification sent", 
                           type=notification_data['type'],
                           tenant_id=notification_data['tenant_id'])
        
        except Exception as e:
            logger.error("Failed to send notification", error=str(e))


class EventBusOrchestrator:
    """Main orchestrator for all Event Bus adapters"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.adapters: Dict[str, Any] = {}
    
    async def initialize_adapters(self, thehive_client=None, moodle_client=None, simulation_client=None):
        """Initialize all event adapters"""
        
        if thehive_client:
            self.adapters['thehive'] = TheHiveEventAdapter(self.event_bus, thehive_client)
            logger.info("TheHive event adapter initialized")
        
        if moodle_client:
            self.adapters['moodle'] = MoodleEventAdapter(self.event_bus, moodle_client)
            logger.info("Moodle event adapter initialized")
        
        if simulation_client:
            self.adapters['simulation'] = SimulationEventAdapter(self.event_bus, simulation_client)
            logger.info("Simulation event adapter initialized")
        
        # Always initialize document processor and notification adapters
        self.adapters['document_processor'] = DocumentProcessorEventAdapter(self.event_bus)
        self.adapters['notifications'] = NotificationEventAdapter(self.event_bus)
        
        logger.info("All event adapters initialized")
    
    async def start(self):
        """Start the event bus and all adapters"""
        await self.event_bus.connect()
        logger.info("Event Bus orchestrator started")
    
    async def stop(self):
        """Stop the event bus and all adapters"""
        await self.event_bus.disconnect()
        logger.info("Event Bus orchestrator stopped")
    
    def get_adapter(self, adapter_name: str):
        """Get specific adapter instance"""
        return self.adapters.get(adapter_name)
    
    async def emit_test_event(self, tenant_id: str, company_id: str):
        """Emit test event for validation"""
        test_event = Event(
            id="test_event_001",
            type=EventType.SYSTEM_HEALTH_CHECK,
            timestamp=datetime.utcnow(),
            actor="system",
            tenant_id=tenant_id,
            company_id=company_id,
            module="event_bus",
            data={"message": "Event Bus test event"},
            priority="normal"
        )
        
        await self.event_bus.publish(test_event)
        logger.info("Test event emitted", tenant_id=tenant_id)
