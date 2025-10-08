"""TheHive integration processor"""

import logging
from typing import Dict, Any
import asyncio

from services.eventbus import EventBusService
from services.thehive_client import TheHiveClient

logger = logging.getLogger(__name__)

class TheHiveProcessor:
    """Main processor for TheHive integration"""
    
    def __init__(self, eventbus_service: EventBusService, thehive_client: TheHiveClient):
        self.eventbus = eventbus_service
        self.thehive = thehive_client
        self.case_mapping = {}  # incident_id -> case_id mapping
        
    async def handle_incident_opened(self, event_data: Dict[str, Any]):
        """Handle bcm.incident.opened event"""
        try:
            logger.info(f"Processing incident opened event: {event_data}")
            
            tenant_id = event_data.get('tenant_id')
            incident_data = event_data.get('data', {})
            incident_id = incident_data.get('incident_id')
            
            if not tenant_id or not incident_id:
                logger.error("Missing tenant_id or incident_id in event")
                return
            
            # Check if case already exists for this incident
            existing_case = await self._find_existing_case(incident_id, tenant_id)
            if existing_case:
                logger.info(f"Case already exists for incident {incident_id}: {existing_case['id']}")
                return
            
            # Create new case in TheHive
            await self._create_case_from_incident(tenant_id, incident_data)
            
        except Exception as e:
            logger.error(f"Error handling incident opened event: {str(e)}")
    
    async def handle_incident_updated(self, event_data: Dict[str, Any]):
        """Handle bcm.incident.updated event"""
        try:
            logger.info(f"Processing incident updated event: {event_data}")
            
            tenant_id = event_data.get('tenant_id')
            incident_data = event_data.get('data', {})
            incident_id = incident_data.get('incident_id')
            
            if not tenant_id or not incident_id:
                logger.error("Missing tenant_id or incident_id in event")
                return
            
            # Find existing case
            existing_case = await self._find_existing_case(incident_id, tenant_id)
            if not existing_case:
                logger.warning(f"No existing case found for incident {incident_id}")
                return
            
            # Update case with new incident data
            await self._update_case_from_incident(existing_case['id'], incident_data)
            
        except Exception as e:
            logger.error(f"Error handling incident updated event: {str(e)}")
    
    async def handle_incident_resolved(self, event_data: Dict[str, Any]):
        """Handle bcm.incident.resolved event"""
        try:
            logger.info(f"Processing incident resolved event: {event_data}")
            
            tenant_id = event_data.get('tenant_id')
            incident_data = event_data.get('data', {})
            incident_id = incident_data.get('incident_id')
            
            if not tenant_id or not incident_id:
                logger.error("Missing tenant_id or incident_id in event")
                return
            
            # Find existing case
            existing_case = await self._find_existing_case(incident_id, tenant_id)
            if not existing_case:
                logger.warning(f"No existing case found for incident {incident_id}")
                return
            
            # Close case in TheHive
            resolution = incident_data.get('resolution', 'Resolved from BCM Platform')
            success = await self.thehive.close_case(existing_case['id'], resolution)
            
            if success:
                # Publish case closure event
                await self.eventbus.publish({
                    'event_type': 'bcm.thehive.case_closed',
                    'tenant_id': tenant_id,
                    'data': {
                        'incident_id': incident_id,
                        'thehive_case_id': existing_case['id'],
                        'resolution': resolution,
                        'closed_automatically': True
                    }
                })
                
        except Exception as e:
            logger.error(f"Error handling incident resolved event: {str(e)}")
    
    async def handle_thehive_case_webhook(self, webhook_data: Dict[str, Any]):
        """Handle webhook from TheHive for case updates"""
        try:
            logger.info(f"Processing TheHive case webhook: {webhook_data}")
            
            case_object = webhook_data.get('object', {})
            case_id = case_object.get('id')
            tags = case_object.get('tags', [])
            
            # Extract tenant and incident IDs from tags
            tenant_id = self._extract_tenant_from_tags(tags)
            incident_id = self._extract_incident_from_tags(tags)
            
            if not tenant_id or not incident_id:
                logger.warning("Case webhook missing tenant or incident tags")
                return
            
            # Map case status updates back to BCM
            case_status = case_object.get('status')
            case_severity = case_object.get('severity')
            
            # Publish BCM incident update event
            await self.eventbus.publish({
                'event_type': 'bcm.incident.updated',
                'tenant_id': tenant_id,
                'data': {
                    'incident_id': incident_id,
                    'thehive_case_id': case_id,
                    'thehive_status': case_status,
                    'thehive_severity': case_severity,
                    'updated_from_thehive': True,
                    'webhook_operation': webhook_data.get('operation')
                }
            })
            
        except Exception as e:
            logger.error(f"Error handling TheHive case webhook: {str(e)}")
    
    async def handle_thehive_task_webhook(self, webhook_data: Dict[str, Any]):
        """Handle webhook from TheHive for task updates"""
        try:
            logger.info(f"Processing TheHive task webhook: {webhook_data}")
            
            task_object = webhook_data.get('object', {})
            case_id = task_object.get('caseId')
            task_id = task_object.get('id')
            task_status = task_object.get('status')
            
            # Get case details to find incident mapping
            case_data = await self.thehive.get_case(case_id)
            if not case_data:
                logger.warning(f"Case {case_id} not found for task webhook")
                return
            
            tags = case_data.get('tags', [])
            tenant_id = self._extract_tenant_from_tags(tags)
            incident_id = self._extract_incident_from_tags(tags)
            
            if not tenant_id or not incident_id:
                logger.warning("Task webhook missing tenant or incident context")
                return
            
            # Publish task update event
            await self.eventbus.publish({
                'event_type': 'bcm.thehive.task_updated',
                'tenant_id': tenant_id,
                'data': {
                    'incident_id': incident_id,
                    'thehive_case_id': case_id,
                    'thehive_task_id': task_id,
                    'task_status': task_status,
                    'task_title': task_object.get('title'),
                    'webhook_operation': webhook_data.get('operation')
                }
            })
            
        except Exception as e:
            logger.error(f"Error handling TheHive task webhook: {str(e)}")
    
    async def _create_case_from_incident(self, tenant_id: str, incident_data: Dict[str, Any]):
        """Create TheHive case from BCM incident"""
        try:
            incident_id = incident_data.get('incident_id')
            title = incident_data.get('title', f"BCM Incident {incident_id}")
            description = incident_data.get('description', 'Incident created from BCM Platform')
            severity_str = incident_data.get('severity', 'medium')
            incident_type = incident_data.get('type', 'security')
            
            # Map BCM severity to TheHive
            severity = self.thehive._map_bcm_severity_to_hive(severity_str)
            
            # Prepare tags
            tags = [
                f"bcm_incident:{incident_id}",
                f"tenant:{tenant_id}",
                f"type:{incident_type}",
                f"severity:{severity_str}",
                "source:bcm_platform"
            ]
            
            # Add custom tags from incident
            if 'tags' in incident_data:
                tags.extend(incident_data['tags'])
            
            # Create case
            case_data = await self.thehive.create_case(
                title=title,
                description=description,
                severity=severity,
                tags=tags,
                tenant_id=tenant_id,
                incident_id=incident_id
            )
            
            if case_data:
                case_id = case_data['id']
                
                # Store mapping
                self.case_mapping[incident_id] = case_id
                
                # Add observables if provided
                await self._add_incident_observables(case_id, incident_data)
                
                # Create initial tasks
                await self._create_initial_tasks(case_id, incident_data)
                
                # Publish case creation event
                await self.eventbus.publish({
                    'event_type': 'bcm.thehive.case_created',
                    'tenant_id': tenant_id,
                    'data': {
                        'incident_id': incident_id,
                        'thehive_case_id': case_id,
                        'case_url': f"{self.thehive.base_url}/cases/{case_id}/details",
                        'created_automatically': True
                    }
                })
                
                logger.info(f"Created TheHive case {case_id} for incident {incident_id}")
            
        except Exception as e:
            logger.error(f"Error creating case from incident: {str(e)}")
    
    async def _update_case_from_incident(self, case_id: str, incident_data: Dict[str, Any]):
        """Update TheHive case with incident data"""
        try:
            updates = {}
            
            # Update description if provided
            if 'description' in incident_data:
                updates['description'] = incident_data['description']
            
            # Update severity if changed
            if 'severity' in incident_data:
                severity = self.thehive._map_bcm_severity_to_hive(incident_data['severity'])
                updates['severity'] = severity
            
            # Update status mapping
            if 'status' in incident_data:
                bcm_status = incident_data['status']
                hive_status = self._map_bcm_status_to_hive(bcm_status)
                if hive_status:
                    updates['status'] = hive_status
            
            if updates:
                await self.thehive.update_case(case_id, updates)
                logger.info(f"Updated TheHive case {case_id} from incident data")
            
        except Exception as e:
            logger.error(f"Error updating case from incident: {str(e)}")
    
    async def _add_incident_observables(self, case_id: str, incident_data: Dict[str, Any]):
        """Add observables from incident data to TheHive case"""
        try:
            observables = incident_data.get('observables', [])
            
            for observable in observables:
                await self.thehive.add_observable(
                    case_id=case_id,
                    data_type=observable.get('type', 'other'),
                    data=observable.get('value', ''),
                    message=observable.get('description', ''),
                    tags=observable.get('tags', [])
                )
            
            # Add common incident attributes as observables
            if 'source_ip' in incident_data:
                await self.thehive.add_observable(
                    case_id=case_id,
                    data_type='ip',
                    data=incident_data['source_ip'],
                    message='Source IP from incident'
                )
            
            if 'affected_systems' in incident_data:
                for system in incident_data['affected_systems']:
                    await self.thehive.add_observable(
                        case_id=case_id,
                        data_type='other',
                        data=system,
                        message='Affected system'
                    )
                    
        except Exception as e:
            logger.error(f"Error adding observables: {str(e)}")
    
    async def _create_initial_tasks(self, case_id: str, incident_data: Dict[str, Any]):
        """Create initial response tasks in TheHive case"""
        try:
            incident_type = incident_data.get('type', 'general')
            severity = incident_data.get('severity', 'medium')
            
            # Standard response tasks based on incident type
            if incident_type == 'security':
                tasks = [
                    "Initial triage and assessment",
                    "Containment actions",
                    "Evidence collection",
                    "Impact analysis",
                    "Communication to stakeholders"
                ]
            elif incident_type == 'operational':
                tasks = [
                    "Service restoration",
                    "Root cause analysis",
                    "Business impact assessment",
                    "Recovery plan execution"
                ]
            else:
                tasks = [
                    "Incident assessment",
                    "Response coordination",
                    "Documentation and reporting"
                ]
            
            # Add critical tasks for high severity incidents
            if severity in ['high', 'critical']:
                tasks.insert(0, "Immediate escalation notification")
                tasks.append("Executive briefing preparation")
            
            # Create tasks in TheHive
            for task_title in tasks:
                await self.thehive.create_task(
                    case_id=case_id,
                    title=task_title,
                    description=f"Automated task for {incident_type} incident response"
                )
                
        except Exception as e:
            logger.error(f"Error creating initial tasks: {str(e)}")
    
    async def _find_existing_case(self, incident_id: str, tenant_id: str) -> Dict[str, Any]:
        """Find existing TheHive case for incident"""
        try:
            # Check local mapping first
            if incident_id in self.case_mapping:
                case_id = self.case_mapping[incident_id]
                case_data = await self.thehive.get_case(case_id)
                if case_data:
                    return case_data
            
            # Search by incident tag
            query = {
                "query": {
                    "_and": [
                        {"_field": "tags", "_value": f"bcm_incident:{incident_id}"},
                        {"_field": "tags", "_value": f"tenant:{tenant_id}"}
                    ]
                },
                "range": "0-1"
            }
            
            cases = await self.thehive.search_cases(query)
            
            if cases:
                case_data = cases[0]
                # Update local mapping
                self.case_mapping[incident_id] = case_data['id']
                return case_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding existing case: {str(e)}")
            return None
    
    def _extract_tenant_from_tags(self, tags: list) -> str:
        """Extract tenant ID from tags"""
        for tag in tags:
            if tag.startswith('tenant:'):
                return tag.split(':', 1)[1]
        return None
    
    def _extract_incident_from_tags(self, tags: list) -> str:
        """Extract incident ID from tags"""
        for tag in tags:
            if tag.startswith('bcm_incident:'):
                return tag.split(':', 1)[1]
        return None
    
    def _map_bcm_status_to_hive(self, bcm_status: str) -> str:
        """Map BCM incident status to TheHive case status"""
        status_mapping = {
            'new': 'Open',
            'assigned': 'Open',
            'in_progress': 'Open',
            'resolved': 'Resolved',
            'closed': 'Resolved',
            'cancelled': 'Resolved'
        }
        return status_mapping.get(bcm_status.lower())
