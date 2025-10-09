# -*- coding: utf-8 -*-
"""
TheHive Integration Client for BCM Platform
Integrates with TheHive for incident management
"""
import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class TheHiveCase:
    """TheHive case data structure"""
    id: str
    title: str
    description: str
    severity: int
    status: str
    owner: Optional[str] = None
    tags: List[str] = None
    tlp: int = 2  # TLP:AMBER by default
    pap: int = 2  # PAP:AMBER by default
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    custom_fields: Optional[Dict] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.custom_fields is None:
            self.custom_fields = {}

@dataclass
class TheHiveTask:
    """TheHive task data structure"""
    title: str
    description: str
    status: str = "Waiting"
    owner: Optional[str] = None
    case_id: Optional[str] = None
    
@dataclass
class TheHiveAlert:
    """TheHive alert data structure"""
    title: str
    description: str
    type: str
    source: str
    severity: int
    tags: List[str] = None
    tlp: int = 2
    pap: int = 2
    artifacts: List[Dict] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.artifacts is None:
            self.artifacts = []

class TheHiveClient:
    """TheHive API Client for BCM Platform"""
    
    def __init__(self, url: str, api_key: str, verify_ssl: bool = True):
        """
        Initialize TheHive client
        
        Args:
            url: TheHive instance URL (e.g., http://localhost:9000)
            api_key: TheHive API key
            verify_ssl: Whether to verify SSL certificates
        """
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
        
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make HTTP request to TheHive API"""
        url = f"{self.url}/api{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, verify=self.verify_ssl)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, verify=self.verify_ssl)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, verify=self.verify_ssl)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, verify=self.verify_ssl)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"TheHive API request failed: {e}")
            raise
    
    def create_case(self, case: TheHiveCase) -> Dict:
        """Create a new case in TheHive"""
        case_data = {
            'title': case.title,
            'description': case.description,
            'severity': case.severity,
            'tags': case.tags,
            'tlp': case.tlp,
            'pap': case.pap,
            'customFields': case.custom_fields
        }
        
        if case.owner:
            case_data['owner'] = case.owner
            
        logger.info(f"Creating TheHive case: {case.title}")
        result = self._make_request('POST', '/case', case_data)
        return result
    
    def get_case(self, case_id: str) -> Dict:
        """Get case details by ID"""
        return self._make_request('GET', f'/case/{case_id}')
    
    def update_case(self, case_id: str, updates: Dict) -> Dict:
        """Update case details"""
        return self._make_request('PUT', f'/case/{case_id}', updates)
    
    def close_case(self, case_id: str, resolution: str = "Resolved") -> Dict:
        """Close a case"""
        return self.update_case(case_id, {
            'status': 'Resolved',
            'resolutionStatus': resolution
        })
    
    def list_cases(self, 
                   status: Optional[str] = None,
                   severity: Optional[int] = None,
                   tags: Optional[List[str]] = None,
                   limit: int = 50) -> List[Dict]:
        """List cases with optional filters"""
        query = {
            'range': f'0-{limit}'
        }
        
        # Build query filters
        filters = []
        if status:
            filters.append({'_field': 'status', '_value': status})
        if severity:
            filters.append({'_field': 'severity', '_value': severity})
        if tags:
            for tag in tags:
                filters.append({'_field': 'tags', '_value': tag})
        
        if filters:
            query['query'] = {'_and': filters}
            
        return self._make_request('POST', '/case/_search', query)
    
    def create_task(self, case_id: str, task: TheHiveTask) -> Dict:
        """Create a task for a case"""
        task_data = {
            'title': task.title,
            'description': task.description,
            'status': task.status
        }
        
        if task.owner:
            task_data['owner'] = task.owner
            
        return self._make_request('POST', f'/case/{case_id}/task', task_data)
    
    def update_task(self, task_id: str, updates: Dict) -> Dict:
        """Update task details"""
        return self._make_request('PUT', f'/case/task/{task_id}', updates)
    
    def list_tasks(self, case_id: str) -> List[Dict]:
        """List tasks for a case"""
        return self._make_request('GET', f'/case/{case_id}/task')
    
    def create_alert(self, alert: TheHiveAlert) -> Dict:
        """Create an alert in TheHive"""
        alert_data = {
            'title': alert.title,
            'description': alert.description,
            'type': alert.type,
            'source': alert.source,
            'severity': alert.severity,
            'tags': alert.tags,
            'tlp': alert.tlp,
            'pap': alert.pap,
            'artifacts': alert.artifacts,
            'date': int(datetime.now().timestamp() * 1000)
        }
        
        logger.info(f"Creating TheHive alert: {alert.title}")
        return self._make_request('POST', '/alert', alert_data)
    
    def promote_alert_to_case(self, alert_id: str, case_template: str = None) -> Dict:
        """Promote alert to case"""
        data = {}
        if case_template:
            data['caseTemplate'] = case_template
            
        return self._make_request('POST', f'/alert/{alert_id}/createCase', data)
    
    def add_case_artifact(self, case_id: str, artifact_type: str, data: str, 
                         message: str = None, tags: List[str] = None) -> Dict:
        """Add artifact to case"""
        artifact_data = {
            'dataType': artifact_type,
            'data': data,
            'message': message or f"Artifact added by BCM Platform",
            'tags': tags or []
        }
        
        return self._make_request('POST', f'/case/{case_id}/artifact', artifact_data)
    
    def get_case_observables(self, case_id: str) -> List[Dict]:
        """Get observables/artifacts for a case"""
        return self._make_request('GET', f'/case/{case_id}/artifact')

class BCMTheHiveIntegration:
    """BCM Platform integration with TheHive"""
    
    def __init__(self, thehive_client: TheHiveClient, 
                 odoo_webhook_url: str = None):
        """
        Initialize BCM-TheHive integration
        
        Args:
            thehive_client: TheHive client instance
            odoo_webhook_url: Odoo webhook URL for notifications
        """
        self.thehive = thehive_client
        self.odoo_webhook_url = odoo_webhook_url
        
    def create_bcm_incident_case(self, incident_data: Dict) -> Dict:
        """Create TheHive case from BCM incident"""
        
        # Map BCM incident to TheHive case
        case = TheHiveCase(
            id="",  # Will be set by TheHive
            title=f"BCM Incident: {incident_data.get('name', 'Unknown')}",
            description=self._format_incident_description(incident_data),
            severity=self._map_bcm_severity_to_thehive(
                incident_data.get('severity', 'medium')
            ),
            status="Open",
            tags=['bcm-incident', 'business-continuity'] + 
                 incident_data.get('tags', []),
            custom_fields={
                'bcm_incident_id': incident_data.get('id'),
                'bcm_company_id': incident_data.get('company_id'),
                'incident_type': incident_data.get('incident_type'),
                'business_impact': incident_data.get('business_impact'),
                'affected_processes': incident_data.get('affected_processes', [])
            }
        )
        
        # Create case in TheHive
        result = self.thehive.create_case(case)
        
        # Create initial tasks based on BCM incident type
        if result.get('_id'):
            self._create_bcm_response_tasks(result['_id'], incident_data)
            
        # Notify Odoo about case creation
        if self.odoo_webhook_url:
            self._notify_odoo_case_created(result, incident_data)
            
        return result
    
    def sync_case_to_bcm_incident(self, case_id: str, 
                                  bcm_incident_id: str) -> Dict:
        """Sync TheHive case updates back to BCM incident"""
        case_data = self.thehive.get_case(case_id)
        
        # Map TheHive status to BCM status
        bcm_status = self._map_thehive_status_to_bcm(case_data.get('status'))
        
        # Prepare update data for BCM incident
        update_data = {
            'thehive_case_id': case_id,
            'status': bcm_status,
            'resolution': case_data.get('resolutionStatus'),
            'last_sync': datetime.now().isoformat()
        }
        
        # Get tasks and add to update
        tasks = self.thehive.list_tasks(case_id)
        update_data['response_tasks'] = [
            {
                'title': task.get('title'),
                'status': task.get('status'),
                'owner': task.get('owner')
            }
            for task in tasks
        ]
        
        # Send update to BCM incident via webhook
        if self.odoo_webhook_url:
            self._notify_odoo_incident_update(bcm_incident_id, update_data)
            
        return update_data
    
    def create_bcm_exercise_case(self, exercise_data: Dict) -> Dict:
        """Create TheHive case for BCM exercise/drill"""
        case = TheHiveCase(
            id="",
            title=f"BCM Exercise: {exercise_data.get('name', 'Unknown')}",
            description=self._format_exercise_description(exercise_data),
            severity=1,  # Low severity for exercises
            status="Open",
            tags=['bcm-exercise', 'drill', 'training'],
            custom_fields={
                'bcm_exercise_id': exercise_data.get('id'),
                'exercise_type': exercise_data.get('exercise_type'),
                'scenario': exercise_data.get('scenario'),
                'participants': exercise_data.get('participants', [])
            }
        )
        
        result = self.thehive.create_case(case)
        
        # Create exercise tasks
        if result.get('_id'):
            self._create_exercise_tasks(result['_id'], exercise_data)
            
        return result
    
    def _format_incident_description(self, incident_data: Dict) -> str:
        """Format BCM incident data for TheHive description"""
        description = f"""
**BCM Incident Details**

**Incident Type:** {incident_data.get('incident_type', 'Unknown')}
**Severity:** {incident_data.get('severity', 'Unknown')}
**Business Impact:** {incident_data.get('business_impact', 'Not specified')}

**Description:**
{incident_data.get('description', 'No description provided')}

**Affected Processes:**
{chr(10).join('- ' + process for process in incident_data.get('affected_processes', []))}

**Detection Time:** {incident_data.get('detection_time', 'Unknown')}
**Reporter:** {incident_data.get('reported_by', 'Unknown')}

---
*This case was automatically created by BCM Platform*
"""
        return description.strip()
    
    def _format_exercise_description(self, exercise_data: Dict) -> str:
        """Format BCM exercise data for TheHive description"""
        description = f"""
**BCM Exercise/Drill**

**Exercise Type:** {exercise_data.get('exercise_type', 'Unknown')}
**Scenario:** {exercise_data.get('scenario', 'Not specified')}

**Objectives:**
{chr(10).join('- ' + obj for obj in exercise_data.get('objectives', []))}

**Participants:**
{chr(10).join('- ' + participant for participant in exercise_data.get('participants', []))}

**Start Time:** {exercise_data.get('start_time', 'TBD')}
**Duration:** {exercise_data.get('duration', 'Unknown')}

---
*This exercise case was created by BCM Platform*
"""
        return description.strip()
    
    def _map_bcm_severity_to_thehive(self, bcm_severity: str) -> int:
        """Map BCM severity to TheHive severity (1-4)"""
        mapping = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        return mapping.get(bcm_severity.lower(), 2)
    
    def _map_thehive_status_to_bcm(self, thehive_status: str) -> str:
        """Map TheHive status to BCM incident status"""
        mapping = {
            'Open': 'active',
            'Resolved': 'resolved',
            'Deleted': 'cancelled'
        }
        return mapping.get(thehive_status, 'active')
    
    def _create_bcm_response_tasks(self, case_id: str, incident_data: Dict):
        """Create standard BCM response tasks"""
        standard_tasks = [
            {
                'title': 'Initial Assessment and Triage',
                'description': 'Assess incident impact and determine response level'
            },
            {
                'title': 'Stakeholder Notification',
                'description': 'Notify relevant stakeholders and management'
            },
            {
                'title': 'Activate Business Continuity Plan',
                'description': 'Implement relevant BCP procedures'
            },
            {
                'title': 'Communication Management',
                'description': 'Manage internal and external communications'
            },
            {
                'title': 'Recovery Operations',
                'description': 'Execute recovery procedures'
            },
            {
                'title': 'Post-Incident Review',
                'description': 'Conduct lessons learned and improvement actions'
            }
        ]
        
        for task_data in standard_tasks:
            task = TheHiveTask(
                title=task_data['title'],
                description=task_data['description'],
                status='Waiting'
            )
            self.thehive.create_task(case_id, task)
    
    def _create_exercise_tasks(self, case_id: str, exercise_data: Dict):
        """Create exercise-specific tasks"""
        exercise_tasks = [
            {
                'title': 'Exercise Preparation',
                'description': 'Set up exercise environment and materials'
            },
            {
                'title': 'Participant Briefing',
                'description': 'Brief participants on exercise objectives and procedures'
            },
            {
                'title': 'Exercise Execution',
                'description': 'Run the exercise scenario'
            },
            {
                'title': 'Observation and Monitoring',
                'description': 'Monitor participant responses and document findings'
            },
            {
                'title': 'Exercise Debrief',
                'description': 'Conduct post-exercise debrief session'
            },
            {
                'title': 'Report Generation',
                'description': 'Create exercise evaluation report'
            }
        ]
        
        for task_data in exercise_tasks:
            task = TheHiveTask(
                title=task_data['title'],
                description=task_data['description'],
                status='Waiting'
            )
            self.thehive.create_task(case_id, task)
    
    def _notify_odoo_case_created(self, thehive_case: Dict, incident_data: Dict):
        """Notify Odoo about TheHive case creation"""
        if not self.odoo_webhook_url:
            return
            
        webhook_data = {
            'event': 'thehive.case.created',
            'thehive_case_id': thehive_case.get('_id'),
            'bcm_incident_id': incident_data.get('id'),
            'case_url': f"{self.thehive.url}/index.html#!/case/{thehive_case.get('_id')}/details",
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                self.odoo_webhook_url,
                json=webhook_data,
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"Notified Odoo about case creation: {thehive_case.get('_id')}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to notify Odoo: {e}")
    
    def _notify_odoo_incident_update(self, incident_id: str, update_data: Dict):
        """Notify Odoo about incident updates"""
        if not self.odoo_webhook_url:
            return
            
        webhook_data = {
            'event': 'thehive.incident.updated',
            'bcm_incident_id': incident_id,
            'update_data': update_data,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                self.odoo_webhook_url,
                json=webhook_data,
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"Notified Odoo about incident update: {incident_id}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to notify Odoo: {e}")
