# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import json

_logger = logging.getLogger(__name__)

class BCMEventBusIntegration(models.AbstractModel):
    """EventBus integration pattern для всех BCM modules"""
    _name = 'bcm.eventbus.integration'
    _description = 'EventBus Integration Pattern'

    def publish_module_event(self, event_type, event_data, priority='normal'):
        """Publish module events to ecosystem"""
        try:
            import requests

            event_payload = {
                'source_module': self._name,
                'event_type': event_type,
                'event_data': event_data,
                'priority': priority,
                'timestamp': fields.Datetime.now().isoformat(),
                'company_id': getattr(self, 'company_id', self.env.company).id,
                'user_id': self.env.user.id
            }

            response = requests.post(
                'http://eventbus:8001/api/events/publish',
                json=event_payload,
                timeout=5
            )

            if response.status_code == 200:
                _logger.info(f'Event published: {event_type} from {self._name}')
                return True
            else:
                _logger.warning(f'Event publish failed: {response.status_code}')
                return False

        except Exception as e:
            _logger.warning(f'EventBus integration failed: {e}')
            return False

    @api.model
    def handle_ecosystem_event(self, event_data):
        """Handle events from other modules - override в каждом module"""
        event_type = event_data.get('event_type')
        source_module = event_data.get('source_module')

        _logger.info(f'{self._name} received event: {event_type} from {source_module}')

        # Базовая обработка - override в specific modules
        return True

    def trigger_cross_module_workflow(self, workflow_type, workflow_data):
        """Trigger cross-module workflows"""

        workflow_triggers = {
            'risk_to_bia': {
                'target_module': 'bcm.bia',
                'event_type': 'risk_assessment_complete',
                'priority': 'high'
            },
            'bia_to_plans': {
                'target_module': 'bcm.plans',
                'event_type': 'bia_analysis_complete',
                'priority': 'high'
            },
            'plans_to_exercise': {
                'target_module': 'bcm.exercise',
                'event_type': 'plans_updated',
                'priority': 'medium'
            },
            'incident_to_scenario': {
                'target_module': 'bcm.scenario',
                'event_type': 'incident_lessons_available',
                'priority': 'medium'
            },
            'governance_to_all': {
                'target_module': 'all',
                'event_type': 'governance_decision',
                'priority': 'critical'
            }
        }

        trigger = workflow_triggers.get(workflow_type)
        if trigger:
            return self.publish_module_event(
                trigger['event_type'],
                workflow_data,
                trigger['priority']
            )

        return False