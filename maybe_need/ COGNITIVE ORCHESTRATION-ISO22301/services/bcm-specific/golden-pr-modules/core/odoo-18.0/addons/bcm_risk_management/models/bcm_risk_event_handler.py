# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import json

_logger = logging.getLogger(__name__)

class BCMRiskEventHandler(models.Model):
    """Risk Management as Living Organ of BCM Organism

    This transforms Risk Management from isolated module
    into reactive organ that communicates with other organs
    through the central nervous system (BCM Event Bus).
    """

    _inherit = 'bcm_risk_management.record'

    # Living Organ Properties
    organ_health_status = fields.Selection([
        ('healthy', 'Healthy'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('error', 'Error')
    ], default='healthy', string='Organ Health')

    last_event_processed = fields.Datetime('Last Event Processed')
    events_processed_count = fields.Integer('Events Processed', default=0)

    @api.model_create_multi
    def create(self, vals_list):
        """Create with organism integration"""
        risks = super().create(vals_list)

        for risk in risks:
            # Publish to organism about new risk
            risk._publish_integration_event('risk_identified', {
                'risk_id': risk.id,
                'risk_name': risk.name,
                'severity': getattr(risk, 'severity', 'medium'),
                'category': getattr(risk, 'category', 'operational'),
                'description': getattr(risk, 'notes', ''),
                'assessment_date': fields.Datetime.now().isoformat(),
                'requires_bia': True,
                'requires_plans_review': True
            })

            _logger.info(f'Risk organ published: risk_identified for {risk.name}')

        return risks

    def write(self, vals):
        """Write with organism integration"""
        result = super().write(vals)

        # Check if significant changes happened
        significant_fields = ['severity', 'status', 'notes']
        if any(field in vals for field in significant_fields):
            self._publish_integration_event('risk_updated', {
                'risk_id': self.id,
                'risk_name': self.name,
                'changes': {k: v for k, v in vals.items() if k in significant_fields},
                'update_timestamp': fields.Datetime.now().isoformat(),
                'requires_review': True
            })

            # Update health status
            self._update_organ_health()

        return result

    def _publish_integration_event(self, event_type, event_data):
        """Publish event to BCM Event Bus (Central Nervous System)"""
        try:
            # Get Event Bus (Central Nervous System)
            event_bus = self.env['bcm.event.bus']

            # Publish event to organism
            success = event_bus.publish_event(
                event_type=event_type,
                source_module='bcm_risk_management',
                event_data=event_data,
                priority='high' if 'critical' in str(event_data) else 'normal'
            )

            if success:
                self.events_processed_count += 1
                self.last_event_processed = fields.Datetime.now()

                # Add message to chatter
                self.message_post(
                    body=f'🧬 Organism Event Published: {event_type}',
                    subject=f'Living Organ Communication: {event_type}'
                )

            return success

        except Exception as e:
            _logger.error(f'Organism communication failed: {e}')
            self.organ_health_status = 'error'
            return False

    @api.model
    def handle_event(self, event_type, event_data, source_module):
        """Handle events from other organs in the organism

        This method makes Risk Management reactive to events from:
        - Project Management: project health issues
        - Incident Management: new incidents
        - Audit: audit findings
        - Governance: policy changes
        """

        try:
            _logger.info(f'Risk organ received event: {event_type} from {source_module}')

            if event_type == 'project_critical_health' and source_module == 'bcm_project_management':
                return self._handle_project_critical_event(event_data)

            elif event_type == 'incident_created' and source_module == 'bcm_incident_management':
                return self._handle_incident_event(event_data)

            elif event_type == 'audit_finding_created' and source_module == 'bcm_audit':
                return self._handle_audit_finding_event(event_data)

            elif event_type == 'governance_policy_changed' and source_module == 'bcm_governance':
                return self._handle_governance_change_event(event_data)

            else:
                _logger.info(f'Risk organ: No handler for event {event_type} from {source_module}')
                return {'status': 'ignored', 'reason': 'no_handler'}

        except Exception as e:
            _logger.error(f'Risk organ event handling failed: {e}')
            self.organ_health_status = 'error'
            return {'status': 'error', 'message': str(e)}

    def _handle_project_critical_event(self, event_data):
        """React to critical project health issues"""
        try:
            project_name = event_data.get('project_name', 'Unknown Project')
            health_issues = event_data.get('health_issues', [])

            # Create or update risk related to project issues
            risk_name = f'Project Risk: {project_name}'

            existing_risk = self.search([
                ('name', 'ilike', project_name),
                ('company_id', '=', self.env.company.id)
            ], limit=1)

            if existing_risk:
                # Update existing risk
                existing_risk.write({
                    'notes': f"Updated from project critical health event: {', '.join(health_issues)}"
                })
                risk_record = existing_risk
            else:
                # Create new risk
                risk_record = self.create({
                    'name': risk_name,
                    'notes': f"Risk identified from project health issues: {', '.join(health_issues)}",
                    'active': True
                })

            # Add chatter message
            risk_record.message_post(
                body=f'🚨 Risk updated from project critical health: {project_name}',
                subject='Living Organ Reaction: Project → Risk'
            )

            # Trigger further analysis
            risk_record._trigger_bia_analysis()

            return {'status': 'success', 'risk_id': risk_record.id}

        except Exception as e:
            _logger.error(f'Project critical event handling failed: {e}')
            return {'status': 'error', 'message': str(e)}

    def _handle_incident_event(self, event_data):
        """React to new incidents"""
        try:
            incident_title = event_data.get('incident_title', 'Unknown Incident')
            incident_category = event_data.get('category', 'operational')

            # Find related risks to update
            related_risks = self.search([
                ('notes', 'ilike', incident_category),
                ('company_id', '=', self.env.company.id)
            ])

            for risk in related_risks:
                risk.message_post(
                    body=f'📋 Risk assessment updated based on incident: {incident_title}',
                    subject='Living Organ Reaction: Incident → Risk Update'
                )

            return {'status': 'success', 'updated_risks': len(related_risks)}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _handle_audit_finding_event(self, event_data):
        """React to audit findings"""
        try:
            finding = event_data.get('finding', 'Unknown Finding')
            severity = event_data.get('severity', 'medium')

            # Create risk from audit finding if severe
            if severity in ['high', 'critical']:
                risk_record = self.create({
                    'name': f'Audit Risk: {finding}',
                    'notes': f'Risk identified from audit finding: {finding}',
                    'active': True
                })

                return {'status': 'success', 'risk_created': risk_record.id}

            return {'status': 'success', 'action': 'monitored'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _handle_governance_change_event(self, event_data):
        """React to governance policy changes"""
        try:
            policy_change = event_data.get('policy_change', 'Unknown Change')

            # Update risk appetite or assessment criteria
            self.message_post(
                body=f'🏛️ Risk assessment criteria updated due to governance change: {policy_change}',
                subject='Living Organ Reaction: Governance → Risk Criteria Update'
            )

            return {'status': 'success', 'action': 'criteria_updated'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _trigger_bia_analysis(self):
        """Trigger BIA analysis using organism architecture"""
        try:
            # Publish event to BIA organ through Event Bus
            bia_data = {
                'risk_id': self.id,
                'risk_name': self.name,
                'risk_description': getattr(self, 'notes', ''),
                'assessment_date': fields.Datetime.now().isoformat(),
                'trigger_type': 'risk_assessment_complete',
                'priority': 'medium',
                'automated': True
            }

            success = self._publish_integration_event('risk_to_bia_trigger', bia_data)

            if success:
                self.message_post(
                    body='🔄 BIA analysis triggered through organism Event Bus',
                    subject='Chain Reaction: Risk → BIA'
                )

                return True
            else:
                _logger.warning('BIA trigger failed - Event Bus unavailable')
                return False

        except Exception as e:
            _logger.error(f'BIA trigger failed: {e}')
            return False

    def _update_organ_health(self):
        """Update organ health status based on activity"""
        try:
            # Calculate health based on recent activity
            recent_events = self.events_processed_count

            if recent_events > 10:
                self.organ_health_status = 'healthy'
            elif recent_events > 5:
                self.organ_health_status = 'warning'
            else:
                self.organ_health_status = 'critical'

        except Exception as e:
            self.organ_health_status = 'error'

    @api.model
    def get_organ_health_status(self):
        """Get health status for organism monitoring"""
        try:
            total_risks = self.search_count([('company_id', '=', self.env.company.id)])
            active_risks = self.search_count([
                ('active', '=', True),
                ('company_id', '=', self.env.company.id)
            ])

            recent_activity = self.search_count([
                ('last_event_processed', '>=', fields.Datetime.now() - fields.timedelta(hours=24)),
                ('company_id', '=', self.env.company.id)
            ])

            return {
                'organ_name': 'bcm_risk_management',
                'health_status': 'healthy' if recent_activity > 0 else 'warning',
                'total_records': total_risks,
                'active_records': active_risks,
                'recent_activity': recent_activity,
                'last_active': fields.Datetime.now().isoformat(),
                'capabilities': [
                    'risk_identification',
                    'risk_assessment',
                    'bia_triggering',
                    'incident_reaction',
                    'governance_compliance'
                ]
            }

        except Exception as e:
            return {
                'organ_name': 'bcm_risk_management',
                'health_status': 'error',
                'error': str(e)
            }

    def action_test_organism_integration(self):
        """Test organism integration"""
        try:
            # Test event publishing
            test_success = self._publish_integration_event('test_event', {
                'test_data': 'Risk organ health check',
                'timestamp': fields.Datetime.now().isoformat()
            })

            if test_success:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Organism Integration Test'),
                        'message': 'Risk organ successfully communicated with organism Event Bus',
                        'type': 'success',
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Integration Test Failed'),
                        'message': 'Risk organ cannot communicate with organism Event Bus',
                        'type': 'danger',
                    }
                }

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Test Error'),
                    'message': f'Integration test failed: {str(e)}',
                    'type': 'danger',
                }
            }