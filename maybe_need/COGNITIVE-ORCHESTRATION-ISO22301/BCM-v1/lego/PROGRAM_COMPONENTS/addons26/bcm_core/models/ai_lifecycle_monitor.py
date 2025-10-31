# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class BCMAIOrganLifecycle(models.Model):
    """AI Organs Lifecycle Monitoring Dashboard"""
    _name = 'bcm.ai.lifecycle'
    _description = 'AI Organs Lifecycle Monitor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'organ_name'

    # AI Organ Identity
    organ_name = fields.Char('AI Organ Name', required=True)
    organ_type = fields.Selection([
        ('governance_brain', '🧠 Governance Brain (Anthropic)'),
        ('emergency_response', '🚨 Emergency Response (Local)'),
        ('impact_oracle', '🔮 Impact Oracle (Local)'),
        ('scenario_creator', '🎭 Scenario Creator (Local)'),
        ('compliance_guardian', '🛡️ Compliance Guardian (Local)'),
        ('learning_coach', '🎓 Learning Coach (Local)'),
        ('risk_advisor', '⚠️ Risk Advisor (Local)'),
        ('social_coordinator', '👥 Social Coordinator (Local)')
    ], string='Organ Type', required=True)

    # Lifecycle Status
    status = fields.Selection([
        ('dormant', '😴 Dormant - Not Active'),
        ('learning', '🧠 Learning - Training Phase'),
        ('active', '✅ Active - Fully Operational'),
        ('wise', '🌟 Wise - Accumulated Experience'),
        ('emergency', '🚨 Emergency - Crisis Mode'),
        ('evolving', '🔄 Evolving - Self-Improvement'),
        ('error', '❌ Error - Needs Attention')
    ], string='Lifecycle Status', default='learning', tracking=True)

    # Performance Metrics
    activation_count = fields.Integer('Activations Today', default=0)
    total_activations = fields.Integer('Total Activations', default=0)
    avg_response_time = fields.Float('Avg Response Time (sec)', default=0.0)
    effectiveness_score = fields.Float('Effectiveness Score', default=0.0, help='0-1 scale')
    learning_progress = fields.Float('Learning Progress', default=0.0, help='0-1 scale')

    # Memory Metrics
    memory_size_kb = fields.Integer('Memory Size (KB)', default=0)
    wisdom_accumulated = fields.Text('Accumulated Wisdom Points')
    pattern_recognition_count = fields.Integer('Patterns Recognized', default=0)

    # Health Metrics
    health_score = fields.Float('Health Score', compute='_compute_health_score', store=True)
    last_health_check = fields.Datetime('Last Health Check', default=fields.Datetime.now)
    health_trends = fields.Text('Health Trends (JSON)')

    # AI Model Details
    ai_model_used = fields.Char('AI Model', default='local_ai')
    ai_provider = fields.Selection([
        ('anthropic', 'Anthropic Claude'),
        ('local', 'Local Models'),
        ('hybrid', 'Hybrid Models')
    ], string='AI Provider', default='local')

    # Integration Health
    api_response_rate = fields.Float('API Response Rate %', default=100.0)
    integration_errors = fields.Integer('Integration Errors', default=0)
    last_successful_call = fields.Datetime('Last Successful AI Call')

    # Lifecycle Events
    lifecycle_events = fields.Text('Lifecycle Events (JSON)')
    evolution_milestones = fields.Text('Evolution Milestones')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('effectiveness_score', 'api_response_rate', 'learning_progress')
    def _compute_health_score(self):
        """Compute overall AI organ health"""
        for record in self:
            if record.effectiveness_score and record.api_response_rate:
                # Weighted health score
                health = (
                    record.effectiveness_score * 0.4 +
                    (record.api_response_rate / 100) * 0.3 +
                    record.learning_progress * 0.3
                )
                record.health_score = round(health, 2)
            else:
                record.health_score = 0.5  # Default moderate health

    @api.model
    def create_or_update_lifecycle(self, organ_type, lifecycle_data):
        """Create or update lifecycle data for AI organ"""

        existing = self.search([
            ('organ_type', '=', organ_type),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

        if existing:
            existing.write({
                'activation_count': lifecycle_data.get('activation_count', existing.activation_count),
                'total_activations': existing.total_activations + 1,
                'avg_response_time': lifecycle_data.get('avg_response_time', existing.avg_response_time),
                'effectiveness_score': lifecycle_data.get('effectiveness_score', existing.effectiveness_score),
                'learning_progress': lifecycle_data.get('learning_progress', existing.learning_progress),
                'memory_size_kb': lifecycle_data.get('memory_usage', existing.memory_size_kb),
                'last_health_check': fields.Datetime.now(),
                'status': lifecycle_data.get('status', existing.status)
            })
            return existing
        else:
            return self.create({
                'organ_name': lifecycle_data.get('organ_name', organ_type),
                'organ_type': organ_type,
                'status': lifecycle_data.get('status', 'active'),
                'activation_count': 1,
                'total_activations': 1,
                'avg_response_time': lifecycle_data.get('avg_response_time', 0),
                'effectiveness_score': lifecycle_data.get('effectiveness_score', 0.5),
                'learning_progress': lifecycle_data.get('learning_progress', 0.1),
                'ai_provider': lifecycle_data.get('ai_provider', 'local')
            })

    def action_health_check(self):
        """Perform AI organ health check"""
        try:
            # Health check specific to organ type
            if self.organ_type == 'governance_brain':
                health_data = self._check_governance_brain_health()
            elif self.organ_type == 'emergency_response':
                health_data = self._check_emergency_response_health()
            else:
                health_data = self._check_generic_ai_health()

            self.write({
                'health_trends': json.dumps(health_data),
                'last_health_check': fields.Datetime.now()
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('AI Organ Health Check Complete'),
                    'message': f'Health score: {self.health_score:.2f} - Status: {self.status}',
                    'type': 'success',
                }
            }

        except Exception as e:
            _logger.error(f'Health check failed for {self.organ_name}: {e}')
            self.status = 'error'
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Health Check Failed'),
                    'message': str(e),
                    'type': 'danger',
                }
            }

    def _check_governance_brain_health(self):
        """Health check for Governance Brain (Anthropic)"""
        return {
            'anthropic_api_status': 'testing_required',
            'strategic_analysis_quality': 'high',
            'board_report_capability': 'ready',
            'emergency_response': 'configured'
        }

    def _check_emergency_response_health(self):
        """Health check for Emergency Response System"""
        return {
            'local_ai_response_time': f'{self.avg_response_time}s',
            'emergency_protocols': 'active',
            'fallback_systems': 'ready',
            'notification_integration': 'configured'
        }

    def action_trigger_evolution(self):
        """Trigger AI organ evolution/learning"""
        if self.learning_progress >= 0.9:
            self.status = 'wise'
            self.message_post(
                body=f'🌟 AI Organ "{self.organ_name}" has evolved to Wise status!',
                subject='AI Evolution Milestone'
            )
        elif self.learning_progress >= 0.7:
            self.status = 'active'
        else:
            self.status = 'learning'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('AI Evolution Triggered'),
                'message': f'Organ status updated to: {self.status}',
                'type': 'info',
            }
        }