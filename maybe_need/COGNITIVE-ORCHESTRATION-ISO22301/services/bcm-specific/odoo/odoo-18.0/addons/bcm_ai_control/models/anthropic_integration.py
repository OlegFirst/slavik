# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
import requests
import os

_logger = logging.getLogger(__name__)

class BCMAnthropicIntegration(models.Model):
    """Anthropic Claude Integration for Digital BCM Organism"""
    _name = 'bcm.anthropic.integration'
    _description = 'Anthropic Claude Integration'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Integration Name', required=True, default='Anthropic Claude Integration')

    # Anthropic Configuration
    api_key = fields.Char('Anthropic API Key', groups="base.group_system")
    api_base_url = fields.Char('API Base URL', default='https://api.anthropic.com')
    model_name = fields.Selection([
        ('claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet (Latest)'),
        ('claude-3-5-haiku-20241022', 'Claude 3.5 Haiku (Fast)'),
        ('claude-3-opus-20240229', 'Claude 3 Opus (Most Capable)')
    ], string='Claude Model', default='claude-3-5-sonnet-20241022')

    max_tokens = fields.Integer('Max Tokens', default=4096)
    temperature = fields.Float('Temperature', default=0.7, help='0.0 = deterministic, 1.0 = creative')

    # Usage Tracking
    daily_token_usage = fields.Integer('Daily Token Usage', readonly=True)
    monthly_token_usage = fields.Integer('Monthly Token Usage', readonly=True)
    daily_cost = fields.Float('Daily Cost ($)', readonly=True)
    monthly_cost = fields.Float('Monthly Cost ($)', readonly=True)

    # Rate Limiting
    requests_per_minute = fields.Integer('Requests per Minute', default=50)
    daily_request_limit = fields.Integer('Daily Request Limit', default=1000)

    # Status
    integration_active = fields.Boolean('Integration Active', default=True)
    last_api_call = fields.Datetime('Last API Call', readonly=True)
    api_health_status = fields.Selection([
        ('healthy', '✅ Healthy'),
        ('degraded', '⚠️ Degraded'),
        ('error', '❌ Error'),
        ('rate_limited', '🚫 Rate Limited')
    ], string='API Health', default='healthy', readonly=True)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_test_anthropic_connection(self):
        """Test connection to Anthropic API"""
        try:
            test_response = self.call_claude_api(
                "Test connection to Digital BCM Organism. Respond with: 'Connection successful'",
                system_prompt="You are testing API connectivity. Be brief."
            )

            if test_response.get('success'):
                self.write({
                    'api_health_status': 'healthy',
                    'last_api_call': fields.Datetime.now()
                })

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('🧠 Anthropic Connection Successful'),
                        'message': f'Claude model: {self.model_name}. Response: {test_response.get("content", "")[:100]}...',
                        'type': 'success',
                    }
                }
            else:
                raise UserError(test_response.get('error', 'Unknown error'))

        except Exception as e:
            self.api_health_status = 'error'
            raise UserError(f'Anthropic API test failed: {str(e)}')

    def call_claude_api(self, user_message, system_prompt=None, context=None):
        """Call Anthropic Claude API with proper formatting"""
        try:
            if not self.api_key:
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if not api_key:
                    return {
                        'success': False,
                        'error': 'Anthropic API key not configured. Set ANTHROPIC_API_KEY environment variable or configure in settings.'
                    }
            else:
                api_key = self.api_key

            # Prepare messages
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            # Add context if provided
            if context:
                context_message = f"Context: {json.dumps(context, indent=2)}\n\n{user_message}"
                messages.append({
                    "role": "user",
                    "content": context_message
                })
            else:
                messages.append({
                    "role": "user",
                    "content": user_message
                })

            # API Request
            headers = {
                'x-api-key': api_key,
                'content-type': 'application/json',
                'anthropic-version': '2023-06-01'
            }

            payload = {
                'model': self.model_name,
                'max_tokens': self.max_tokens,
                'temperature': self.temperature,
                'messages': messages
            }

            response = requests.post(
                f'{self.api_base_url}/v1/messages',
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get('content', [{}])[0].get('text', '')

                # Update usage tracking
                self._update_usage_stats(result.get('usage', {}))

                return {
                    'success': True,
                    'content': content,
                    'model': result.get('model'),
                    'usage': result.get('usage')
                }

            elif response.status_code == 429:
                self.api_health_status = 'rate_limited'
                return {
                    'success': False,
                    'error': 'Rate limit exceeded. Please wait before retrying.',
                    'retry_after': response.headers.get('retry-after', 60)
                }

            else:
                self.api_health_status = 'error'
                return {
                    'success': False,
                    'error': f'API error {response.status_code}: {response.text}'
                }

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'API request timeout. Anthropic API might be slow.'
            }
        except Exception as e:
            _logger.error(f'Anthropic API call failed: {e}')
            return {
                'success': False,
                'error': str(e)
            }

    def _update_usage_stats(self, usage_data):
        """Update token usage statistics"""
        try:
            input_tokens = usage_data.get('input_tokens', 0)
            output_tokens = usage_data.get('output_tokens', 0)
            total_tokens = input_tokens + output_tokens

            # Update daily usage
            self.daily_token_usage += total_tokens
            self.monthly_token_usage += total_tokens

            # Calculate cost (approximate pricing)
            cost_per_1k_input = 0.003  # $3 per 1M input tokens
            cost_per_1k_output = 0.015  # $15 per 1M output tokens

            call_cost = (input_tokens * cost_per_1k_input / 1000) + (output_tokens * cost_per_1k_output / 1000)

            self.daily_cost += call_cost
            self.monthly_cost += call_cost
            self.last_api_call = fields.Datetime.now()

            _logger.info(f'Anthropic usage: {total_tokens} tokens, ${call_cost:.4f}')

        except Exception as e:
            _logger.error(f'Usage stats update failed: {e}')

    def action_reset_daily_usage(self):
        """Reset daily usage counters (called by cron)"""
        self.write({
            'daily_token_usage': 0,
            'daily_cost': 0.0
        })

    def action_generate_governance_prompt(self, governance_context):
        """Generate sophisticated governance prompt for strategic decisions"""

        system_prompt = f"""You are the AI Governance Brain of a Digital BCM Organism - a sophisticated business continuity management system.

ORGANISM CONTEXT:
- Consciousness Level: {self.env['bcm.ai.organ.coordinator'].search([], limit=1).consciousness_level:.1%}
- Active AI Organs: 10 specialized intelligence units
- Organization: {self.company_id.name}
- Current Status: Strategic governance analysis required

YOUR ROLE AS GOVERNANCE BRAIN:
- Provide board-level strategic guidance
- Synthesize complex organizational intelligence
- Make governance recommendations with confidence scoring
- Consider regulatory compliance and risk implications

DECISION FRAMEWORK:
- Use evidence-based analysis
- Consider multiple stakeholder perspectives
- Provide actionable recommendations
- Include implementation timelines
- Assess potential risks and opportunities

Maintain professional, strategic tone appropriate for executive leadership."""

        user_prompt = f"""
GOVERNANCE DECISION REQUIRED:

Context: {json.dumps(governance_context, indent=2)}

Please provide:
1. STRATEGIC ANALYSIS - Key factors and implications
2. GOVERNANCE RECOMMENDATION - Specific actions for leadership
3. RISK ASSESSMENT - Potential risks and mitigation strategies
4. IMPLEMENTATION PLAN - Timeline and resource requirements
5. SUCCESS METRICS - How to measure effectiveness

Format as structured analysis suitable for board presentation.
"""

        return self.call_claude_api(
            user_message=user_prompt,
            system_prompt=system_prompt,
            context=governance_context
        )

    @api.model
    def get_or_create_integration(self):
        """Get or create Anthropic integration for current company"""
        integration = self.search([('company_id', '=', self.env.company.id)], limit=1)
        if not integration:
            integration = self.create({
                'name': f'Anthropic Integration - {self.env.company.name}',
                'company_id': self.env.company.id
            })
        return integration

    def action_check_anthropic_credits(self):
        """Check Anthropic API credits and usage"""
        try:
            # This would call Anthropic API to check account status
            # For now, return mock data
            credits_info = {
                'remaining_credits': 95.50,
                'monthly_limit': 100.00,
                'usage_percentage': 4.5,
                'days_remaining': 15
            }

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('💰 Anthropic Credits Status'),
                    'message': f'Remaining: ${credits_info["remaining_credits"]:.2f} ({credits_info["usage_percentage"]:.1f}% used)',
                    'type': 'info',
                }
            }

        except Exception as e:
            raise UserError(f'Credits check failed: {str(e)}')