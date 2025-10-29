# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class BCMRiskEnhanced(models.Model):
    """Enhanced Risk Management with EventBus Integration"""
    _inherit = 'bcm_risk_management.record'  # Inherit existing risk model

    # EventBus Integration
    def publish_risk_event(self, event_type, risk_data):
        """Publish risk events to ecosystem"""
        try:
            import requests

            event_payload = {
                'source_module': 'bcm_risk_management',
                'event_type': event_type,
                'risk_id': self.id,
                'risk_name': self.name,
                'risk_data': risk_data,
                'timestamp': fields.Datetime.now().isoformat(),
                'company_id': self.company_id.id
            }

            response = requests.post(
                'http://eventbus:8001/api/events/risk',
                json=event_payload,
                timeout=5
            )

            if response.status_code == 200:
                _logger.info(f'Risk event published: {event_type}')
                return True
            else:
                _logger.warning(f'Risk event publish failed: {response.status_code}')
                return False

        except Exception as e:
            _logger.warning(f'EventBus integration failed: {e}')
            return False

    def action_trigger_bia_analysis(self):
        """Trigger BIA analysis from risk assessment"""
        try:
            # Gather risk data for BIA
            risk_data = {
                'risk_assessment': {
                    'risk_id': self.id,
                    'risk_name': self.name,
                    'risk_description': getattr(self, 'notes', ''),
                    'risk_category': 'operational',  # Default
                    'assessment_date': fields.Datetime.now().isoformat()
                },
                'bia_trigger': {
                    'trigger_type': 'risk_assessment_complete',
                    'priority': 'medium',
                    'automated': True
                }
            }

            # Publish risk-to-BIA event
            success = self.publish_risk_event('risk_assessment_complete', risk_data)

            if success:
                # Add message to risk record
                self.message_post(
                    body='🔄 BIA analysis triggered from risk assessment via EventBus',
                    subject='Cross-Module Workflow: Risk → BIA'
                )

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('BIA Analysis Triggered'),
                        'message': 'Risk data sent to BIA module for impact analysis',
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('Failed to trigger BIA analysis - EventBus unavailable'))

        except Exception as e:
            _logger.error(f'BIA trigger failed: {e}')
            raise UserError(f'BIA trigger failed: {str(e)}')

    def action_notify_governance(self):
        """Notify governance of high-risk assessment"""
        try:
            governance_data = {
                'governance_alert': {
                    'alert_type': 'high_risk_identified',
                    'risk_id': self.id,
                    'risk_name': self.name,
                    'severity': 'high',
                    'requires_attention': True
                },
                'recommendation': {
                    'action': 'governance_review_required',
                    'urgency': 'medium',
                    'stakeholders': ['risk_manager', 'governance_board']
                }
            }

            success = self.publish_risk_event('governance_notification', governance_data)

            if success:
                self.message_post(
                    body='🏛️ Governance notified of high-risk assessment',
                    subject='Risk → Governance Alert'
                )

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Governance Notified'),
                        'message': 'High-risk assessment escalated to governance',
                        'type': 'warning',
                    }
                }

        except Exception as e:
            raise UserError(f'Governance notification failed: {str(e)}')

    @api.model
    def handle_ecosystem_event(self, event_data):
        """Handle events from other modules"""
        event_type = event_data.get('event_type')
        source_module = event_data.get('source_module')

        if event_type == 'governance_decision' and source_module == 'bcm_governance':
            # Governance decision affects risk management
            self._handle_governance_decision(event_data)

        elif event_type == 'incident_resolved' and source_module == 'bcm_incident':
            # Incident resolution updates risk assessment
            self._update_risk_from_incident(event_data)

        _logger.info(f'Risk management handled event: {event_type} from {source_module}')

    def _handle_governance_decision(self, governance_data):
        """Handle governance decisions affecting risk management"""
        decision_type = governance_data.get('decision_type')

        if decision_type == 'risk_appetite_change':
            # Update risk appetite settings
            _logger.info('Risk appetite updated from governance decision')

    def _update_risk_from_incident(self, incident_data):
        """Update risk assessment based on incident resolution"""
        incident_category = incident_data.get('incident_category', 'operational')

        # Find related risks to update
        related_risks = self.search([
            ('notes', 'ilike', incident_category),
            ('company_id', '=', self.env.company.id)
        ])

        for risk in related_risks:
            risk.message_post(
                body=f'Risk updated based on incident: {incident_data.get("incident_title", "Unknown")}',
                subject='Risk Update from Incident Resolution'
            )

# Enhanced Risk Register
class BCMRiskWorkflow(models.Model):
    """Risk workflow coordination"""
    _name = 'bcm.risk.workflow'
    _description = 'Risk Workflow Coordination'

    name = fields.Char('Workflow Name', required=True)
    workflow_type = fields.Selection([
        ('risk_to_bia', 'Risk Assessment → BIA Analysis'),
        ('risk_to_governance', 'Risk Alert → Governance Review'),
        ('risk_to_plans', 'Risk → Continuity Plans Update'),
        ('incident_to_risk', 'Incident → Risk Assessment Update')
    ], required=True)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='draft')

    trigger_conditions = fields.Text('Trigger Conditions (JSON)')
    workflow_data = fields.Text('Workflow Data (JSON)')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_execute_workflow(self):
        """Execute cross-module workflow"""
        self.status = 'active'

        if self.workflow_type == 'risk_to_bia':
            return self._execute_risk_to_bia_workflow()
        elif self.workflow_type == 'risk_to_governance':
            return self._execute_risk_to_governance_workflow()

        return {'type': 'ir.actions.act_window_close'}

    def _execute_risk_to_bia_workflow(self):
        """Execute Risk → BIA workflow"""
        try:
            # Get risk data
            risk_records = self.env['bcm_risk_management.record'].search([
                ('company_id', '=', self.company_id.id)
            ], limit=5)  # Test with first 5 risks

            for risk in risk_records:
                # Trigger BIA analysis for each risk
                bia_trigger_result = risk.action_trigger_bia_analysis()

            self.status = 'completed'

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Risk → BIA Workflow Complete'),
                    'message': f'Triggered BIA analysis for {len(risk_records)} risks',
                    'type': 'success',
                }
            }

        except Exception as e:
            self.status = 'failed'
            raise UserError(f'Risk → BIA workflow failed: {str(e)}')