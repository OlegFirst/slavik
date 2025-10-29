# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class BCMBIAEventBusIntegration(models.Model):
    """BIA EventBus Integration for Cross-Module Workflows"""
    _inherit = 'bcm_bia.record'  # Inherit existing BIA model

    @api.model
    def handle_risk_assessment_event(self, risk_data):
        """Handle risk assessment completion event"""
        try:
            risk_id = risk_data.get('risk_id')
            risk_name = risk_data.get('risk_name', 'Unknown Risk')

            _logger.info(f'BIA module received risk assessment event: {risk_name}')

            # Create or update BIA analysis based on risk data
            bia_record = self.search([
                ('name', 'ilike', risk_name),
                ('company_id', '=', self.env.company.id)
            ], limit=1)

            if not bia_record:
                # Create new BIA record triggered by risk
                bia_record = self.create({
                    'name': f'BIA Analysis: {risk_name}',
                    'notes': f'Triggered by risk assessment ID: {risk_id}',
                    'active': True
                })

            # Add chatter message about risk-triggered analysis
            bia_record.message_post(
                body=f'🔄 BIA analysis triggered by risk assessment: {risk_name}',
                subject='Cross-Module Trigger: Risk → BIA'
            )

            # Trigger next workflow step: BIA → Plans
            self._trigger_plans_update(bia_record, risk_data)

            return True

        except Exception as e:
            _logger.error(f'Risk assessment event handling failed: {e}')
            return False

    def _trigger_plans_update(self, bia_record, source_risk_data):
        """Trigger continuity plans update from BIA analysis"""
        try:
            import requests

            plans_data = {
                'bia_trigger': {
                    'bia_id': bia_record.id,
                    'bia_name': bia_record.name,
                    'source_risk': source_risk_data.get('risk_name'),
                    'trigger_type': 'bia_analysis_complete'
                },
                'update_requirements': {
                    'plan_review_required': True,
                    'risk_mitigation_update': True,
                    'procedure_enhancement': True
                }
            }

            # Publish BIA-to-Plans event
            event_payload = {
                'source_module': 'bcm_bia',
                'event_type': 'bia_analysis_complete',
                'target_module': 'bcm_plans',
                'plans_data': plans_data,
                'timestamp': fields.Datetime.now().isoformat(),
                'company_id': self.env.company.id
            }

            response = requests.post(
                'http://eventbus:8001/api/events/plans',
                json=event_payload,
                timeout=5
            )

            if response.status_code == 200:
                bia_record.message_post(
                    body='📋 Continuity plans update triggered from BIA analysis',
                    subject='Cross-Module Workflow: BIA → Plans'
                )
                return True

        except Exception as e:
            _logger.warning(f'Plans trigger failed: {e}')
            return False

    def action_manual_cross_module_trigger(self):
        """Manual trigger for testing cross-module workflows"""
        # Simulate risk assessment completion
        test_risk_data = {
            'risk_id': 999,
            'risk_name': 'Test Risk for Cross-Module Workflow',
            'risk_category': 'operational',
            'test_mode': True
        }

        success = self.handle_risk_assessment_event(test_risk_data)

        if success:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Cross-Module Workflow Test'),
                    'message': 'Risk → BIA → Plans workflow triggered successfully',
                    'type': 'success',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Workflow Test Failed'),
                    'message': 'Cross-module workflow could not be triggered',
                    'type': 'danger',
                }
            }