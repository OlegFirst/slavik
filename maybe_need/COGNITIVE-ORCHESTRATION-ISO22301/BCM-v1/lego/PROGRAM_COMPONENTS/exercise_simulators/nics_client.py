# -*- coding: utf-8 -*-
"""
NICS (Next Generation Incident Command System) Integration Client for BCM Platform
Provides advanced incident command and coordination capabilities for complex BCM exercises
"""
import os
import json
import logging
import asyncio
import aiohttp
import websockets
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import uuid
from enum import Enum

logger = logging.getLogger(__name__)

class NICSRole(Enum):
    """NICS user roles for BCM exercises"""
    INCIDENT_COMMANDER = "IC"
    OPERATIONS_CHIEF = "OPS"
    PLANNING_CHIEF = "PLAN"
    LOGISTICS_CHIEF = "LOG"
    FINANCE_ADMIN_CHIEF = "FA"
    SAFETY_OFFICER = "SO"
    INFORMATION_OFFICER = "IO"
    BCM_COORDINATOR = "BCM"
    SECTION_CHIEF = "SC"
    DIVISION_SUPERVISOR = "DIV"
    GROUP_SUPERVISOR = "GRP"

@dataclass
class NICSIncident:
    """NICS incident definition for BCM exercise"""
    id: str
    name: str
    description: str
    incident_type: str  # bcm_exercise, actual_incident, training
    location: Dict[str, Any]  # lat, lng, address
    start_time: datetime
    estimated_end_time: Optional[datetime]
    priority: str  # low, medium, high, critical
    status: str  # new, active, contained, controlled, closed
    commander: str
    organization: str
    company_id: str
    parent_incident: Optional[str] = None

@dataclass
class NICSResource:
    """NICS resource for incident response"""
    id: str
    name: str
    resource_type: str  # personnel, equipment, facility, team
    category: str  # bcm_team, it_support, communications, logistics
    status: str  # available, assigned, out_of_service, enroute
    location: Optional[Dict[str, Any]] = None
    capabilities: List[str] = None
    contact_info: Optional[Dict[str, str]] = None
    assignment: Optional[str] = None

@dataclass
class NICSMessage:
    """NICS message/communication"""
    id: str
    incident_id: str
    sender_id: str
    recipient_id: Optional[str]  # None for broadcast
    message_type: str  # sitrep, tasking, request, update, alert
    subject: str
    content: str
    priority: str  # routine, priority, immediate, flash
    timestamp: datetime
    acknowledged: bool = False
    requires_response: bool = False

@dataclass
class NICSForm:
    """NICS form for structured reporting"""
    id: str
    incident_id: str
    form_type: str  # ics201, ics202, ics204, bcm_impact, bcm_recovery
    form_data: Dict[str, Any]
    created_by: str
    created_at: datetime
    status: str  # draft, submitted, approved, archived

class NICSClient:
    """NICS platform client for BCM Platform integration"""
    
    def __init__(self, nics_url: str, api_key: str, 
                 organization: str = "BCM_Platform"):
        self.nics_url = nics_url.rstrip('/')
        self.api_key = api_key
        self.organization = organization
        self.session = None
        self.websocket = None
        self.active_incidents = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'BCM-Platform-NICS-Client/1.0'
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.websocket:
            await self.websocket.close()
        if self.session:
            await self.session.close()
    
    async def authenticate(self) -> bool:
        """Authenticate with NICS platform"""
        try:
            async with self.session.get(f"{self.nics_url}/api/v1/auth/verify") as resp:
                if resp.status == 200:
                    auth_data = await resp.json()
                    logger.info(f"Authenticated with NICS: {auth_data.get('user', 'unknown')}")
                    return True
                else:
                    logger.error(f"NICS authentication failed: {resp.status}")
                    return False
        except Exception as e:
            logger.error(f"NICS authentication error: {e}")
            return False
    
    async def create_bcm_incident(self, incident: NICSIncident) -> str:
        """Create incident in NICS for BCM exercise"""
        incident_data = {
            'incidentname': incident.name,
            'description': incident.description,
            'incidenttypes': [incident.incident_type],
            'lat': incident.location.get('lat', 0.0),
            'lon': incident.location.get('lng', 0.0),
            'created': incident.start_time.isoformat(),
            'usersessionid': self.api_key,
            'workspaceid': 1,  # Default workspace
            'folder': f"BCM_Exercises_{incident.company_id}",
            'prefix': 'BCM',
            'parentincidentid': incident.parent_incident,
            'customfields': {
                'bcm_company_id': incident.company_id,
                'bcm_exercise_type': incident.incident_type,
                'bcm_priority': incident.priority,
                'bcm_commander': incident.commander,
                'bcm_estimated_duration': str(incident.estimated_end_time - incident.start_time) if incident.estimated_end_time else None
            }
        }
        
        try:
            async with self.session.post(
                f"{self.nics_url}/api/v1/incidents", 
                json=incident_data
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    nics_incident_id = result.get('incidentid')
                    
                    self.active_incidents[incident.id] = {
                        'nics_id': nics_incident_id,
                        'bcm_incident': incident,
                        'created_at': datetime.now()
                    }
                    
                    logger.info(f"Created NICS incident: {nics_incident_id} for BCM: {incident.id}")
                    return nics_incident_id
                else:
                    error_text = await resp.text()
                    raise Exception(f"Failed to create incident: {resp.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Failed to create NICS incident: {e}")
            raise
    
    async def add_incident_resource(self, incident_id: str, resource: NICSResource) -> bool:
        """Add resource to NICS incident"""
        nics_incident_id = self.active_incidents.get(incident_id, {}).get('nics_id')
        if not nics_incident_id:
            raise ValueError(f"Incident {incident_id} not found in NICS")
        
        resource_data = {
            'resourceId': resource.id,
            'incidentId': nics_incident_id,
            'type': resource.resource_type,
            'name': resource.name,
            'status': resource.status,
            'category': resource.category,
            'description': f"BCM Resource: {resource.name}",
            'location': resource.location,
            'capabilities': resource.capabilities or [],
            'contactinfo': resource.contact_info or {},
            'assignment': resource.assignment,
            'customfields': {
                'bcm_resource_type': resource.resource_type,
                'bcm_category': resource.category
            }
        }
        
        try:
            async with self.session.post(
                f"{self.nics_url}/api/v1/incidents/{nics_incident_id}/resources",
                json=resource_data
            ) as resp:
                if resp.status == 200:
                    logger.info(f"Added resource {resource.name} to incident {incident_id}")
                    return True
                else:
                    error_text = await resp.text()
                    logger.error(f"Failed to add resource: {resp.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to add resource to NICS: {e}")
            return False
    
    async def send_message(self, message: NICSMessage) -> bool:
        """Send message through NICS"""
        nics_incident_id = self.active_incidents.get(message.incident_id, {}).get('nics_id')
        if not nics_incident_id:
            raise ValueError(f"Incident {message.incident_id} not found in NICS")
        
        message_data = {
            'incidentId': nics_incident_id,
            'subject': message.subject,
            'message': message.content,
            'priority': message.priority,
            'msgtype': message.message_type,
            'to': message.recipient_id,
            'requiresAcknowledgment': message.requires_response,
            'customfields': {
                'bcm_message_id': message.id,
                'bcm_message_type': message.message_type
            }
        }
        
        try:
            async with self.session.post(
                f"{self.nics_url}/api/v1/incidents/{nics_incident_id}/messages",
                json=message_data
            ) as resp:
                if resp.status == 200:
                    logger.info(f"Sent NICS message: {message.subject}")
                    return True
                else:
                    error_text = await resp.text()
                    logger.error(f"Failed to send message: {resp.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to send NICS message: {e}")
            return False
    
    async def submit_form(self, form: NICSForm) -> bool:
        """Submit ICS/BCM form through NICS"""
        nics_incident_id = self.active_incidents.get(form.incident_id, {}).get('nics_id')
        if not nics_incident_id:
            raise ValueError(f"Incident {form.incident_id} not found in NICS")
        
        form_data = {
            'incidentId': nics_incident_id,
            'formTypeId': self._get_form_type_id(form.form_type),
            'message': f"BCM Form: {form.form_type}",
            'formData': form.form_data,
            'status': form.status,
            'customfields': {
                'bcm_form_id': form.id,
                'bcm_form_type': form.form_type,
                'bcm_created_by': form.created_by
            }
        }
        
        try:
            async with self.session.post(
                f"{self.nics_url}/api/v1/incidents/{nics_incident_id}/forms",
                json=form_data
            ) as resp:
                if resp.status == 200:
                    logger.info(f"Submitted NICS form: {form.form_type}")
                    return True
                else:
                    error_text = await resp.text()
                    logger.error(f"Failed to submit form: {resp.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to submit NICS form: {e}")
            return False
    
    def _get_form_type_id(self, form_type: str) -> int:
        """Map BCM form types to NICS form type IDs"""
        form_type_mapping = {
            'ics201': 1,    # Incident Briefing
            'ics202': 2,    # Incident Objectives
            'ics203': 3,    # Organization Assignment List
            'ics204': 4,    # Assignment List
            'ics205': 5,    # Incident Radio Communications Plan
            'bcm_impact': 100,      # Custom BCM Impact Assessment
            'bcm_recovery': 101,    # Custom BCM Recovery Plan
            'bcm_sitrep': 102,      # Custom BCM Situation Report
            'bcm_lessons': 103      # Custom BCM Lessons Learned
        }
        return form_type_mapping.get(form_type, 1)
    
    async def get_incident_status(self, incident_id: str) -> Dict[str, Any]:
        """Get current incident status from NICS"""
        nics_incident_id = self.active_incidents.get(incident_id, {}).get('nics_id')
        if not nics_incident_id:
            raise ValueError(f"Incident {incident_id} not found in NICS")
        
        try:
            async with self.session.get(
                f"{self.nics_url}/api/v1/incidents/{nics_incident_id}"
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    error_text = await resp.text()
                    raise Exception(f"Failed to get incident status: {resp.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Failed to get NICS incident status: {e}")
            raise
    
    async def start_websocket_monitoring(self, incident_id: str, 
                                       message_callback: callable):
        """Start WebSocket connection for real-time updates"""
        nics_incident_id = self.active_incidents.get(incident_id, {}).get('nics_id')
        if not nics_incident_id:
            raise ValueError(f"Incident {incident_id} not found in NICS")
        
        ws_url = f"{self.nics_url.replace('http', 'ws')}/api/v1/incidents/{nics_incident_id}/websocket"
        
        try:
            self.websocket = await websockets.connect(
                ws_url,
                extra_headers={
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            logger.info(f"Started NICS WebSocket monitoring for incident: {incident_id}")
            
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await message_callback(incident_id, data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid WebSocket message: {e}")
                except Exception as e:
                    logger.error(f"WebSocket message processing error: {e}")
                    
        except Exception as e:
            logger.error(f"NICS WebSocket connection failed: {e}")
            raise
    
    async def close_incident(self, incident_id: str) -> bool:
        """Close incident in NICS"""
        nics_incident_id = self.active_incidents.get(incident_id, {}).get('nics_id')
        if not nics_incident_id:
            raise ValueError(f"Incident {incident_id} not found in NICS")
        
        try:
            async with self.session.patch(
                f"{self.nics_url}/api/v1/incidents/{nics_incident_id}",
                json={'status': 'closed'}
            ) as resp:
                if resp.status == 200:
                    logger.info(f"Closed NICS incident: {incident_id}")
                    if incident_id in self.active_incidents:
                        del self.active_incidents[incident_id]
                    return True
                else:
                    error_text = await resp.text()
                    logger.error(f"Failed to close incident: {resp.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to close NICS incident: {e}")
            return False


class BCMNICSIntegration:
    """BCM Platform integration with NICS for advanced exercise management"""
    
    def __init__(self, nics_client: NICSClient, bcm_api_url: str, bcm_api_key: str):
        self.nics = nics_client
        self.bcm_api_url = bcm_api_url
        self.bcm_api_key = bcm_api_key
        self.active_exercises = {}
        
    async def create_bcm_exercise_in_nics(self, exercise_scenario: dict) -> str:
        """Create comprehensive BCM exercise in NICS"""
        try:
            # Create main incident
            incident = NICSIncident(
                id=exercise_scenario['id'],
                name=exercise_scenario['name'],
                description=exercise_scenario['description'],
                incident_type='bcm_exercise',
                location=exercise_scenario.get('location', {'lat': 0.0, 'lng': 0.0}),
                start_time=datetime.now(),
                estimated_end_time=datetime.now() + timedelta(
                    minutes=exercise_scenario.get('duration_minutes', 120)
                ),
                priority=exercise_scenario.get('priority', 'high'),
                status='active',
                commander=exercise_scenario.get('commander', 'BCM_Coordinator'),
                organization=exercise_scenario.get('company_id', 'default'),
                company_id=exercise_scenario['company_id']
            )
            
            nics_incident_id = await self.nics.create_bcm_incident(incident)
            
            # Add BCM resources
            await self._setup_bcm_resources(exercise_scenario['id'])
            
            # Create initial forms
            await self._create_initial_forms(exercise_scenario['id'], exercise_scenario)
            
            # Setup real-time monitoring
            await self.nics.start_websocket_monitoring(
                exercise_scenario['id'],
                self._handle_nics_update
            )
            
            self.active_exercises[exercise_scenario['id']] = {
                'nics_incident_id': nics_incident_id,
                'scenario': exercise_scenario,
                'status': 'active',
                'start_time': datetime.now(),
                'events': []
            }
            
            logger.info(f"Created BCM exercise in NICS: {exercise_scenario['id']}")
            return exercise_scenario['id']
            
        except Exception as e:
            logger.error(f"Failed to create BCM exercise in NICS: {e}")
            raise
    
    async def _setup_bcm_resources(self, exercise_id: str):
        """Setup standard BCM resources in NICS"""
        standard_resources = [
            NICSResource(
                id=f"bcm_coord_{exercise_id}",
                name="BCM Coordinator",
                resource_type="personnel",
                category="bcm_team",
                status="assigned",
                capabilities=["incident_command", "bcm_planning", "coordination"]
            ),
            NICSResource(
                id=f"it_team_{exercise_id}",
                name="IT Recovery Team", 
                resource_type="team",
                category="it_support",
                status="available",
                capabilities=["system_recovery", "data_backup", "network_restore"]
            ),
            NICSResource(
                id=f"comm_team_{exercise_id}",
                name="Communications Team",
                resource_type="team", 
                category="communications",
                status="available",
                capabilities=["stakeholder_comms", "media_relations", "internal_comms"]
            ),
            NICSResource(
                id=f"facilities_{exercise_id}",
                name="Alternate Facility",
                resource_type="facility",
                category="logistics",
                status="available", 
                capabilities=["alternate_site", "emergency_power", "communications"]
            )
        ]
        
        for resource in standard_resources:
            await self.nics.add_incident_resource(exercise_id, resource)
    
    async def _create_initial_forms(self, exercise_id: str, scenario: dict):
        """Create initial ICS and BCM forms"""
        # ICS-201 Incident Briefing
        ics201_form = NICSForm(
            id=f"{exercise_id}_ics201",
            incident_id=exercise_id,
            form_type="ics201",
            form_data={
                "incident_name": scenario['name'],
                "incident_commander": scenario.get('commander', 'BCM Coordinator'),
                "situation": scenario['description'],
                "mission": "Execute BCM exercise and validate response procedures",
                "execution": "Follow BCM exercise plan and evaluate responses",
                "command": "Unified command structure with BCM Coordinator lead",
                "safety": "Exercise safety protocols in effect"
            },
            created_by="BCM_Platform",
            created_at=datetime.now(),
            status="submitted"
        )
        
        # BCM Impact Assessment Form
        bcm_impact_form = NICSForm(
            id=f"{exercise_id}_impact",
            incident_id=exercise_id,
            form_type="bcm_impact",
            form_data={
                "scenario_type": scenario.get('scenario_type', 'general'),
                "affected_processes": scenario.get('affected_processes', []),
                "estimated_downtime": scenario.get('estimated_downtime', 'TBD'),
                "financial_impact": scenario.get('financial_impact', 'TBD'),
                "regulatory_impact": scenario.get('regulatory_impact', 'TBD'),
                "stakeholder_impact": scenario.get('stakeholder_impact', []),
                "rto_requirements": scenario.get('rto', '4 hours'),
                "rpo_requirements": scenario.get('rpo', '1 hour')
            },
            created_by="BCM_Platform",
            created_at=datetime.now(),
            status="draft"
        )
        
        await self.nics.submit_form(ics201_form)
        await self.nics.submit_form(bcm_impact_form)
    
    async def inject_exercise_event(self, exercise_id: str, event: dict):
        """Inject event into NICS exercise"""
        if exercise_id not in self.active_exercises:
            raise ValueError(f"Exercise {exercise_id} not found")
        
        message = NICSMessage(
            id=f"{exercise_id}_event_{len(self.active_exercises[exercise_id]['events'])}",
            incident_id=exercise_id,
            sender_id="BCM_Controller",
            recipient_id=None,  # Broadcast
            message_type="alert",
            subject=f"Exercise Inject: {event['title']}",
            content=event['description'],
            priority="immediate",
            timestamp=datetime.now(),
            requires_response=event.get('requires_response', True)
        )
        
        success = await self.nics.send_message(message)
        if success:
            self.active_exercises[exercise_id]['events'].append(event)
            logger.info(f"Injected event into exercise: {event['title']}")
        
        return success
    
    async def _handle_nics_update(self, exercise_id: str, update_data: dict):
        """Handle real-time updates from NICS"""
        try:
            update_type = update_data.get('type')
            timestamp = datetime.now()
            
            # Log update to exercise
            if exercise_id in self.active_exercises:
                self.active_exercises[exercise_id]['events'].append({
                    'type': 'nics_update',
                    'update_type': update_type,
                    'data': update_data,
                    'timestamp': timestamp.isoformat()
                })
            
            # Send update to BCM Platform
            await self._send_update_to_bcm(exercise_id, update_type, update_data)
            
            logger.debug(f"Processed NICS update for exercise {exercise_id}: {update_type}")
            
        except Exception as e:
            logger.error(f"Failed to handle NICS update: {e}")
    
    async def _send_update_to_bcm(self, exercise_id: str, update_type: str, data: dict):
        """Send update to BCM Platform"""
        try:
            update_payload = {
                'exercise_id': exercise_id,
                'update_type': update_type,
                'timestamp': datetime.now().isoformat(),
                'data': data,
                'source': 'NICS'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.bcm_api_url}/api/v1/exercises/{exercise_id}/updates",
                    json=update_payload,
                    headers={'Authorization': f'Bearer {self.bcm_api_key}'}
                ) as resp:
                    if resp.status != 200:
                        logger.warning(f"Failed to send update to BCM Platform: {resp.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send update to BCM Platform: {e}")
    
    async def complete_exercise(self, exercise_id: str) -> dict:
        """Complete exercise and generate report"""
        if exercise_id not in self.active_exercises:
            raise ValueError(f"Exercise {exercise_id} not found")
        
        try:
            # Close incident in NICS
            await self.nics.close_incident(exercise_id)
            
            # Generate exercise report
            exercise_info = self.active_exercises[exercise_id]
            report = {
                'exercise_id': exercise_id,
                'nics_incident_id': exercise_info['nics_incident_id'],
                'scenario': exercise_info['scenario'],
                'start_time': exercise_info['start_time'].isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_minutes': (datetime.now() - exercise_info['start_time']).total_seconds() / 60,
                'events_count': len(exercise_info['events']),
                'events': exercise_info['events'],
                'status': 'completed'
            }
            
            # Send final report to BCM Platform
            await self._send_final_report_to_bcm(exercise_id, report)
            
            # Clean up
            del self.active_exercises[exercise_id]
            
            logger.info(f"Completed NICS exercise: {exercise_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to complete NICS exercise: {e}")
            raise
    
    async def _send_final_report_to_bcm(self, exercise_id: str, report: dict):
        """Send final exercise report to BCM Platform"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.bcm_api_url}/api/v1/exercises/{exercise_id}/report",
                    json=report,
                    headers={'Authorization': f'Bearer {self.bcm_api_key}'}
                ) as resp:
                    if resp.status == 200:
                        logger.info(f"Sent final report to BCM Platform: {exercise_id}")
                    else:
                        logger.warning(f"Failed to send final report: {resp.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send final report to BCM Platform: {e}")
    
    def get_exercise_status(self, exercise_id: str) -> dict:
        """Get current exercise status"""
        if exercise_id not in self.active_exercises:
            raise ValueError(f"Exercise {exercise_id} not found")
        
        return self.active_exercises[exercise_id]
    
    def list_active_exercises(self) -> list:
        """List all active exercises"""
        return list(self.active_exercises.values())
