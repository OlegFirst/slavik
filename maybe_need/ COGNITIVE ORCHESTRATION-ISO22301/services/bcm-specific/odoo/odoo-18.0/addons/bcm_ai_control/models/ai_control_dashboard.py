# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
import requests

_logger = logging.getLogger(__name__)

class BCMAIControlDashboard(models.Model):
    """Central AI Control Dashboard for Digital BCM Organism"""
    _name = 'bcm.ai.control.dashboard'
    _description = 'AI Control Dashboard - Digital Organism Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Dashboard Name', required=True, default='Digital BCM Organism Control')

    # Organism Status
    organism_status = fields.Selection([
        ('awakening', '🌅 Awakening - Initializing consciousness'),
        ('learning', '🧠 Learning - Accumulating intelligence'),
        ('active', '✅ Active - Fully operational'),
        ('wise', '🌟 Wise - Advanced intelligence'),
        ('evolving', '🔄 Evolving - Self-improvement active')
    ], string='Organism Status', default='awakening', tracking=True)

    overall_health = fields.Float('Overall Health Score', readonly=True)
    consciousness_level = fields.Float('Consciousness Level', readonly=True)
    total_ai_organs = fields.Integer('Total AI Organs', default=10, readonly=True)

    # Memory System Status
    memory_layer1_status = fields.Selection([
        ('healthy', '✅ Healthy'),
        ('degraded', '⚠️ Degraded'),
        ('critical', '🚨 Critical')
    ], string='Layer 1 Memory (PostgreSQL)', readonly=True)

    memory_layer2_status = fields.Selection([
        ('healthy', '✅ Healthy'),
        ('degraded', '⚠️ Degraded'),
        ('critical', '🚨 Critical')
    ], string='Layer 2 Memory (Redis)', readonly=True)

    memory_layer3_status = fields.Selection([
        ('healthy', '✅ Healthy'),
        ('degraded', '⚠️ Degraded'),
        ('critical', '🚨 Critical')
    ], string='Layer 3 Memory (Supabase)', readonly=True)

    # AI Usage Analytics
    daily_ai_calls = fields.Integer('AI Calls Today', readonly=True)
    anthropic_tokens_used = fields.Integer('Anthropic Tokens Used', readonly=True)
    monthly_ai_cost = fields.Float('Monthly AI Cost ($)', readonly=True)
    ai_efficiency_score = fields.Float('AI Efficiency Score', readonly=True)

    # Learning Analytics
    learning_sessions_today = fields.Integer('Learning Sessions Today', readonly=True)
    wisdom_accumulated = fields.Float('Wisdom Accumulated', readonly=True)
    pattern_recognition_rate = fields.Float('Pattern Recognition Rate', readonly=True)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_refresh_organism_status(self):
        """Refresh organism status from all AI organs"""
        try:
            # Call AI Control Center service
            organism_health = self._get_organism_health()

            self.write({
                'overall_health': organism_health.get('overall_health', 0.5),
                'consciousness_level': organism_health.get('consciousness_level', 0.3),
                'organism_status': self._determine_organism_status(organism_health),
                'memory_layer1_status': 'healthy',  # Would check actual status
                'memory_layer2_status': 'healthy',
                'memory_layer3_status': 'healthy'
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Organism Status Refreshed'),
                    'message': f'Health: {self.overall_health:.1%}, Status: {self.organism_status}',
                    'type': 'success',
                }
            }

        except Exception as e:
            raise UserError(f'Status refresh failed: {str(e)}')

    def action_open_ai_control_center(self):
        """Open professional AI Control Center"""
        return {
            'type': 'ir.actions.act_url',
            'url': 'http://localhost:8200',
            'target': 'new'
        }

    def action_open_mcp_inspector(self):
        """Open MCP Inspector for tool testing"""
        return {
            'type': 'ir.actions.act_url',
            'url': 'http://localhost:8200/mcp-inspector',
            'target': 'new'
        }

    def action_open_prompt_studio(self):
        """Open Prompt Engineering Studio"""
        return {
            'type': 'ir.actions.act_url',
            'url': 'http://localhost:8200/prompt-studio',
            'target': 'new'
        }

    def action_emergency_organism_override(self):
        """Emergency override for organism control"""
        try:
            # Emergency protocols
            override_data = {
                'override_type': 'emergency',
                'initiated_by': self.env.user.name,
                'timestamp': fields.Datetime.now().isoformat(),
                'reason': 'Manual emergency override'
            }

            # Notify all AI organs
            self._broadcast_emergency_override(override_data)

            self.organism_status = 'emergency_override'

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Emergency Override Activated'),
                    'message': 'All AI organs notified of emergency override',
                    'type': 'warning',
                }
            }

        except Exception as e:
            raise UserError(f'Emergency override failed: {str(e)}')

    def _get_organism_health(self):
        """Get organism health from AI Control Center service"""
        try:
            response = requests.get('http://localhost:8200/api/organism/health', timeout=10)
            return response.json() if response.status_code == 200 else {}
        except:
            return {'overall_health': 0.5, 'status': 'unknown'}

    def _determine_organism_status(self, health_data):
        """Determine organism status from health data"""
        health = health_data.get('overall_health', 0.5)

        if health >= 0.9:
            return 'wise'
        elif health >= 0.8:
            return 'active'
        elif health >= 0.6:
            return 'learning'
        else:
            return 'awakening'

    def _broadcast_emergency_override(self, override_data):
        """Broadcast emergency override to all organs"""
        try:
            requests.post(
                'http://eventbus:8001/api/events/emergency',
                json=override_data,
                timeout=5
            )
        except Exception as e:
            _logger.error(f'Emergency broadcast failed: {e}')

class BCMAIOrganStatus(models.Model):
    """Individual AI Organ Status Tracking"""
    _name = 'bcm.ai.organ.status'
    _description = 'AI Organ Status'

    name = fields.Char('Organ Name', required=True)
    organ_type = fields.Selection([
        ('governance_brain', '🧠 Governance Brain'),
        ('emergency_response', '🚨 Emergency Response'),
        ('impact_oracle', '🔮 Impact Oracle'),
        ('scenario_creator', '🎭 Scenario Creator'),
        ('risk_advisor', '⚠️ Risk Advisor'),
        ('compliance_guardian', '🛡️ Compliance Guardian'),
        ('performance_analyst', '📈 Performance Analyst'),
        ('learning_coach', '🎓 Learning Coach'),
        ('plan_generator', '📋 Plan Generator'),
        ('lifecycle_monitor', '📊 Lifecycle Monitor')
    ], required=True)

    # Status
    status = fields.Selection([
        ('dormant', '😴 Dormant'),
        ('learning', '🧠 Learning'),
        ('active', '✅ Active'),
        ('wise', '🌟 Wise'),
        ('emergency', '🚨 Emergency'),
        ('error', '❌ Error')
    ], default='learning')

    health_score = fields.Float('Health Score', default=0.5)
    last_activation = fields.Datetime('Last Activation')
    ai_provider = fields.Char('AI Provider')
    personality = fields.Char('AI Personality')

    # Performance
    activation_count = fields.Integer('Activations', default=0)
    avg_response_time = fields.Float('Avg Response Time (sec)')
    success_rate = fields.Float('Success Rate (%)')

    # dashboard_id = fields.Many2one('bcm.ai.control.dashboard', 'Dashboard')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_activate_organ(self):
        """Activate specific AI organ"""
        self.status = 'active'
        self.last_activation = fields.Datetime.now()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('AI Organ Activated'),
                'message': f'{self.name} is now active',
                'type': 'success',
            }
        }

    def action_put_organ_to_sleep(self):
        """Put AI organ to dormant state"""
        self.status = 'dormant'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('AI Organ Dormant'),
                'message': f'{self.name} is now dormant',
                'type': 'info',
            }
        }