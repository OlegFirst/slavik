# -*- coding: utf-8 -*-
"""
TheHive Webhook Handler for BCM Platform
Handles webhooks from TheHive and syncs data back to Odoo
"""
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
import asyncio
import hashlib
import hmac

logger = logging.getLogger(__name__)

class TheHiveWebhookPayload(BaseModel):
    """TheHive webhook payload structure"""
    operation: str
    objectType: str
    objectId: str
    object: Dict
    requestId: str
    timestamp: int

class TheHiveWebhookHandler:
    """Handle TheHive webhooks and sync with BCM Platform"""
    
    def __init__(self, odoo_url: str, odoo_api_key: str, 
                 webhook_secret: str = None):
        """
        Initialize webhook handler
        
        Args:
            odoo_url: BCM Platform Odoo URL
            odoo_api_key: API key for Odoo authentication
            webhook_secret: Secret for webhook verification
        """
        self.odoo_url = odoo_url.rstrip('/')
        self.odoo_api_key = odoo_api_key
        self.webhook_secret = webhook_secret
        
        # FastAPI app for webhook endpoints
        self.app = FastAPI(title="TheHive BCM Webhook Handler")
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes for webhooks"""
        
        @self.app.post("/webhook/thehive")
        async def handle_thehive_webhook(
            request: Request, 
            background_tasks: BackgroundTasks
        ):
            """Main TheHive webhook endpoint"""
            try:
                # Get raw body for signature verification
                body = await request.body()
                
                # Verify webhook signature if secret is configured
                if self.webhook_secret:
                    signature = request.headers.get('X-TheHive-Signature')
                    if not self._verify_signature(body, signature):
                        raise HTTPException(status_code=403, detail="Invalid signature")
                
                # Parse payload
                payload_data = json.loads(body.decode('utf-8'))
                payload = TheHiveWebhookPayload(**payload_data)
                
                # Process webhook in background
                background_tasks.add_task(
                    self._process_webhook, payload
                )
                
                return {"status": "accepted", "requestId": payload.requestId}
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON payload: {e}")
                raise HTTPException(status_code=400, detail="Invalid JSON")
            except Exception as e:
                logger.error(f"Webhook processing error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    def _verify_signature(self, body: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        if not signature or not self.webhook_secret:
            return False
            
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    async def _process_webhook(self, payload: TheHiveWebhookPayload):
        """Process TheHive webhook payload"""
        try:
            logger.info(f"Processing TheHive webhook: {payload.operation} on {payload.objectType}")
            
            if payload.objectType == "case":
                await self._handle_case_webhook(payload)
            elif payload.objectType == "case_task":
                await self._handle_task_webhook(payload)
            elif payload.objectType == "alert":
                await self._handle_alert_webhook(payload)
            else:
                logger.warning(f"Unhandled object type: {payload.objectType}")
                
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
    
    async def _handle_case_webhook(self, payload: TheHiveWebhookPayload):
        """Handle case-related webhooks"""
        case_data = payload.object
        operation = payload.operation
        
        # Extract BCM incident ID from custom fields
        custom_fields = case_data.get('customFields', {})
        bcm_incident_id = None
        bcm_exercise_id = None
        
        for field_name, field_data in custom_fields.items():
            if field_name == 'bcm_incident_id':
                bcm_incident_id = field_data.get('string')
            elif field_name == 'bcm_exercise_id':
                bcm_exercise_id = field_data.get('string')
        
        if operation == "Creation":
            if bcm_incident_id:
                await self._sync_case_creation_to_incident(case_data, bcm_incident_id)
            elif bcm_exercise_id:
                await self._sync_case_creation_to_exercise(case_data, bcm_exercise_id)
                
        elif operation == "Update":
            if bcm_incident_id:
                await self._sync_case_update_to_incident(case_data, bcm_incident_id)
            elif bcm_exercise_id:
                await self._sync_case_update_to_exercise(case_data, bcm_exercise_id)
    
    async def _handle_task_webhook(self, payload: TheHiveWebhookPayload):
        """Handle task-related webhooks"""
        task_data = payload.object
        operation = payload.operation
        
        # Get parent case ID
        case_id = task_data.get('_parent')
        if not case_id:
            return
        
        # Find associated BCM incident/exercise
        bcm_record = await self._find_bcm_record_by_thehive_case(case_id)
        if not bcm_record:
            return
        
        await self._sync_task_update(task_data, bcm_record, operation)
    
    async def _handle_alert_webhook(self, payload: TheHiveWebhookPayload):
        """Handle alert-related webhooks"""
        alert_data = payload.object
        operation = payload.operation
        
        if operation == "Creation":
            # Check if alert should trigger BCM incident
            await self._evaluate_alert_for_bcm_incident(alert_data)
    
    async def _sync_case_creation_to_incident(self, case_data: Dict, incident_id: str):
        """Sync TheHive case creation to BCM incident"""
        update_data = {
            'thehive_case_id': case_data.get('_id'),
            'thehive_case_url': f"#!/case/{case_data.get('_id')}/details",
            'external_case_status': 'created',
            'last_sync_date': datetime.now().isoformat()
        }
        
        await self._update_bcm_record('bcm.incident', incident_id, update_data)
    
    async def _sync_case_creation_to_exercise(self, case_data: Dict, exercise_id: str):
        """Sync TheHive case creation to BCM exercise"""
        update_data = {
            'thehive_case_id': case_data.get('_id'),
            'thehive_case_url': f"#!/case/{case_data.get('_id')}/details",
            'external_tracking_status': 'active',
            'last_sync_date': datetime.now().isoformat()
        }
        
        await self._update_bcm_record('bcm.exercise', exercise_id, update_data)
    
    async def _sync_case_update_to_incident(self, case_data: Dict, incident_id: str):
        """Sync TheHive case updates to BCM incident"""
        
        # Map TheHive status to BCM status
        status_mapping = {
            'Open': 'active',
            'Resolved': 'resolved',
            'Deleted': 'cancelled'
        }
        
        update_data = {
            'thehive_status': case_data.get('status'),
            'status': status_mapping.get(case_data.get('status'), 'active'),
            'resolution': case_data.get('resolutionStatus'),
            'last_sync_date': datetime.now().isoformat(),
            'thehive_owner': case_data.get('owner'),
            'thehive_severity': case_data.get('severity')
        }
        
        # Add case metrics if available
        metrics = case_data.get('stats', {})
        if metrics:
            update_data['case_metrics'] = {
                'tasks_total': metrics.get('tasks', 0),
                'tasks_completed': metrics.get('tasksCompleted', 0),
                'observables': metrics.get('observables', 0)
            }
        
        await self._update_bcm_record('bcm.incident', incident_id, update_data)
        
        # Create activity log entry
        await self._create_activity_log(
            'bcm.incident', incident_id,
            f"TheHive case updated: {case_data.get('status')}",
            case_data
        )
    
    async def _sync_case_update_to_exercise(self, case_data: Dict, exercise_id: str):
        """Sync TheHive case updates to BCM exercise"""
        
        status_mapping = {
            'Open': 'in_progress',
            'Resolved': 'completed',
            'Deleted': 'cancelled'
        }
        
        update_data = {
            'thehive_status': case_data.get('status'),
            'status': status_mapping.get(case_data.get('status'), 'in_progress'),
            'last_sync_date': datetime.now().isoformat()
        }
        
        await self._update_bcm_record('bcm.exercise', exercise_id, update_data)
    
    async def _sync_task_update(self, task_data: Dict, bcm_record: Dict, operation: str):
        """Sync task updates to BCM record"""
        
        # Prepare task update data
        task_update = {
            'thehive_task_id': task_data.get('_id'),
            'title': task_data.get('title'),
            'status': task_data.get('status'),
            'owner': task_data.get('owner'),
            'operation': operation,
            'last_update': datetime.now().isoformat()
        }
        
        model = bcm_record['model']
        record_id = bcm_record['id']
        
        # Update task list in BCM record
        await self._update_task_list(model, record_id, task_update)
        
        # Log task activity
        await self._create_activity_log(
            model, record_id,
            f"Task {operation.lower()}: {task_data.get('title')}",
            task_data
        )
    
    async def _evaluate_alert_for_bcm_incident(self, alert_data: Dict):
        """Evaluate if alert should trigger BCM incident"""
        
        # Check alert criteria for BCM incident creation
        alert_tags = alert_data.get('tags', [])
        alert_severity = alert_data.get('severity', 1)
        alert_type = alert_data.get('type', '')
        
        # Define BCM-relevant criteria
        bcm_triggers = [
            'business-continuity',
            'operational-disruption', 
            'system-outage',
            'data-breach',
            'infrastructure-failure'
        ]
        
        should_create_incident = (
            alert_severity >= 3 or  # High/Critical severity
            any(tag in bcm_triggers for tag in alert_tags) or
            'outage' in alert_type.lower() or
            'disruption' in alert_type.lower()
        )
        
        if should_create_incident:
            await self._create_bcm_incident_from_alert(alert_data)
    
    async def _create_bcm_incident_from_alert(self, alert_data: Dict):
        """Create BCM incident from TheHive alert"""
        
        incident_data = {
            'name': f"Auto-generated from Alert: {alert_data.get('title')}",
            'description': alert_data.get('description'),
            'incident_type': 'security',  # Default type
            'severity': self._map_thehive_severity_to_bcm(alert_data.get('severity', 1)),
            'source': 'thehive_alert',
            'thehive_alert_id': alert_data.get('_id'),
            'detection_time': datetime.now().isoformat(),
            'status': 'new',
            'tags': alert_data.get('tags', [])
        }
        
        # Create incident in BCM platform
        await self._create_bcm_record('bcm.incident', incident_data)
    
    async def _find_bcm_record_by_thehive_case(self, case_id: str) -> Optional[Dict]:
        """Find BCM record associated with TheHive case"""
        
        # Search in incidents
        incident = await self._search_bcm_record('bcm.incident', [
            ('thehive_case_id', '=', case_id)
        ])
        
        if incident:
            return {'model': 'bcm.incident', 'id': incident[0]['id'], 'data': incident[0]}
        
        # Search in exercises
        exercise = await self._search_bcm_record('bcm.exercise', [
            ('thehive_case_id', '=', case_id)
        ])
        
        if exercise:
            return {'model': 'bcm.exercise', 'id': exercise[0]['id'], 'data': exercise[0]}
        
        return None
    
    async def _update_bcm_record(self, model: str, record_id: str, data: Dict):
        """Update BCM record via Odoo API"""
        url = f"{self.odoo_url}/api/v1/{model}/{record_id}"
        
        headers = {
            'Authorization': f'Bearer {self.odoo_api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(url, json=data, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to update {model}:{record_id}: {response.status}")
                    else:
                        logger.info(f"Updated {model}:{record_id}")
                        
        except Exception as e:
            logger.error(f"Error updating BCM record: {e}")
    
    async def _create_bcm_record(self, model: str, data: Dict):
        """Create new BCM record via Odoo API"""
        url = f"{self.odoo_url}/api/v1/{model}"
        
        headers = {
            'Authorization': f'Bearer {self.odoo_api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status not in [200, 201]:
                        logger.error(f"Failed to create {model}: {response.status}")
                    else:
                        result = await response.json()
                        logger.info(f"Created {model}:{result.get('id')}")
                        return result
                        
        except Exception as e:
            logger.error(f"Error creating BCM record: {e}")
    
    async def _search_bcm_record(self, model: str, domain: List) -> List[Dict]:
        """Search BCM records via Odoo API"""
        url = f"{self.odoo_url}/api/v1/{model}/search"
        
        headers = {
            'Authorization': f'Bearer {self.odoo_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {'domain': domain}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Search failed for {model}: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error searching BCM records: {e}")
            return []
    
    async def _update_task_list(self, model: str, record_id: str, task_update: Dict):
        """Update task list in BCM record"""
        
        # Get current record
        current_record = await self._search_bcm_record(model, [('id', '=', record_id)])
        if not current_record:
            return
        
        # Update tasks list
        tasks = current_record[0].get('thehive_tasks', [])
        
        # Find existing task or add new one
        task_found = False
        for i, task in enumerate(tasks):
            if task.get('thehive_task_id') == task_update['thehive_task_id']:
                tasks[i] = task_update
                task_found = True
                break
        
        if not task_found:
            tasks.append(task_update)
        
        # Update record
        await self._update_bcm_record(model, record_id, {'thehive_tasks': tasks})
    
    async def _create_activity_log(self, model: str, record_id: str, 
                                  message: str, details: Dict):
        """Create activity log entry"""
        log_data = {
            'model': model,
            'record_id': record_id,
            'message': message,
            'details': json.dumps(details),
            'source': 'thehive_webhook',
            'timestamp': datetime.now().isoformat()
        }
        
        await self._create_bcm_record('bcm.activity.log', log_data)
    
    def _map_thehive_severity_to_bcm(self, thehive_severity: int) -> str:
        """Map TheHive severity (1-4) to BCM severity"""
        mapping = {1: 'low', 2: 'medium', 3: 'high', 4: 'critical'}
        return mapping.get(thehive_severity, 'medium')

# Factory function to create webhook handler
def create_thehive_webhook_handler(odoo_url: str, odoo_api_key: str, 
                                  webhook_secret: str = None) -> TheHiveWebhookHandler:
    """Create TheHive webhook handler instance"""
    return TheHiveWebhookHandler(odoo_url, odoo_api_key, webhook_secret)
