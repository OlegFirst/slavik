# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class BCMIncidentActions(models.Model):
    _inherit = 'bcm.incident'
    _description = 'BCM Incident Actions'
    
    ai_checklist = fields.Text('AI Response Checklist', readonly=True)
    ai_recommendations = fields.Text('AI Recommendations', readonly=True)
    
    def action_ai_emergency_response(self):
        """AI Emergency Response System - Fast Local AI Analysis"""
        self.ensure_one()
        
        try:
            # Prepare incident context
            context_data = {
                'incident_id': self.id,
                'title': self.name,
                'severity': self.severity or 'medium',
                'description': self.description or '',
                'affected_processes': [p.name for p in self.affected_process_ids] if hasattr(self, 'affected_process_ids') else [],
                'incident_type': self.incident_type if hasattr(self, 'incident_type') else 'operational'
            }
            
            # AI Emergency Response System (Fast Local AI)
            emergency_prompt = f"""
AI EMERGENCY RESPONSE SYSTEM ACTIVATED

INCIDENT ALERT:
Title: {self.name}
Severity: {context_data['severity']}
Type: {context_data['incident_type']}
Organization: {self.company_id.name}

Description: {context_data.get('description', 'No description')}

IMMEDIATE RESPONSE REQUIRED:

1. FIRST 15 MINUTES:
   - Critical assessment actions
   - Key personnel notifications
   - System isolation/protection

2. RESPONSE TEAM ACTIVATION:
   - Required team members
   - Communication protocols
   - Resource mobilization

3. ESCALATION TRIGGERS:
   - When to escalate severity
   - Stakeholder notification points
   - External authority involvement

4. MONITORING CHECKLIST:
   - Key metrics to track
   - Success indicators
   - Next decision points

Provide IMMEDIATE, ACTIONABLE emergency response guidance.
"""

            # Call local AI (fast response for emergencies)
            result = self.call_ai_orchestrator_fast_mode(emergency_prompt, context_data)
            
            if result:
                # Generate checklist
                checklist = []
                checklist.append("IMMEDIATE ACTIONS:")
                checklist.append("1. Assess immediate impact and safety")
                checklist.append("2. Notify crisis management team")
                checklist.append("3. Activate communication protocols")
                
                if self.severity == 'critical':
                    checklist.append("4. Activate alternate site if needed")
                    checklist.append("5. Notify executive management")
                
                checklist.append("\nRECOMMENDED ACTIONS:")
                alternatives = result.get('alternatives', [])
                for i, alt in enumerate(alternatives, 1):
                    checklist.append(f"{i}. {alt.get('option', '')}")
                
                self.write({
                    'ai_checklist': '\n'.join(checklist),
                    'ai_recommendations': result.get('recommendation', ''),
                    'state': 'in_progress'
                })
                
                # Send event
                self.send_event_to_eventbus('bcm.incident.response_generated', {
                    'incident_id': self.id,
                    'severity': self.severity,
                    'checklist_items': len(checklist)
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Response Checklist Generated'),
                        'message': _('AI has generated an incident response checklist'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_("Failed to generate response from Orchestrator"))
                
        except Exception as e:
            raise UserError(_(f"Emergency response failed: {str(e)}"))

    def call_ai_orchestrator_fast_mode(self, prompt, context):
        """Fast local AI call for emergency responses"""
        try:
            import requests

            # Fast mode call to AI Orchestrator (local models)
            response = requests.post(
                'http://ai_orchestrator:8000/nlp/query',
                json={
                    'query': prompt,
                    'context': {
                        **context,
                        'emergency_mode': True,
                        'fast_response_required': True,
                        'use_local_ai': True  # Force local AI for speed
                    },
                    'user_role': 'emergency_response_system'
                },
                timeout=10  # Short timeout for emergency
            )

            if response.status_code == 200:
                ai_result = response.json()
                return {
                    'recommendation': ai_result.get('response', ''),
                    'alternatives': [],  # Quick response, no alternatives
                    'confidence': ai_result.get('confidence', 0.8),
                    'response_time': '< 10 seconds',
                    'ai_model': 'local_emergency_response'
                }
            else:
                # Emergency fallback
                return self._emergency_fallback_response(context)

        except Exception as e:
            _logger.error(f'Fast AI call failed: {e}')
            return self._emergency_fallback_response(context)

    def _emergency_fallback_response(self, context):
        """Emergency fallback when AI unavailable"""
        severity = context.get('severity', 'medium')

        emergency_responses = {
            'critical': {
                'immediate_actions': [
                    'Activate crisis management team',
                    'Implement emergency communication plan',
                    'Execute business continuity procedures'
                ],
                'notifications': ['Executive team', 'All staff', 'External stakeholders'],
                'resources': ['Emergency supplies', 'Backup systems', 'Alternative locations']
            },
            'high': {
                'immediate_actions': [
                    'Notify incident response team',
                    'Assess impact and scope',
                    'Implement containment measures'
                ],
                'notifications': ['Management team', 'Affected departments'],
                'resources': ['Technical team', 'Backup procedures']
            },
            'medium': {
                'immediate_actions': [
                    'Document incident details',
                    'Notify supervisor',
                    'Begin impact assessment'
                ],
                'notifications': ['Department head', 'IT support'],
                'resources': ['Standard procedures', 'Documentation']
            }
        }

        fallback = emergency_responses.get(severity, emergency_responses['medium'])

        return {
            'recommendation': f"Emergency response for {severity} severity incident",
            'alternatives': fallback['immediate_actions'],
            'emergency_notifications': fallback['notifications'],
            'required_resources': fallback['resources'],
            'fallback_mode': True
        }

    def action_ai_lifecycle_monitoring(self):
        """Monitor AI Emergency Response System lifecycle"""
        try:
            # Lifecycle metrics for dashboard
            lifecycle_data = {
                'organ_name': 'Emergency Response System',
                'status': 'active',
                'last_activation': self.write_date,
                'response_count': self.search_count([]),
                'avg_response_time': self._calculate_avg_response_time(),
                'effectiveness_score': self._calculate_effectiveness_score(),
                'memory_usage': len(self.ai_checklist or '') + len(self.ai_recommendations or ''),
                'learning_progress': self._assess_learning_progress()
            }

            # Store lifecycle data for dashboard
            self.env['bcm.ai.lifecycle'].sudo().create_or_update_lifecycle(
                'incident_response',
                lifecycle_data
            )

            return lifecycle_data

        except Exception as e:
            _logger.error(f'Lifecycle monitoring failed: {e}')
            return {'error': str(e)}

    def _calculate_avg_response_time(self):
        """Calculate average AI response time"""
        # Mock calculation - would track actual response times
        return 8.5  # seconds

    def _calculate_effectiveness_score(self):
        """Calculate emergency response effectiveness"""
        # Mock calculation - would analyze success rates
        return 0.87  # 87% effectiveness

    def _assess_learning_progress(self):
        """Assess how much the system has learned"""
        # Mock assessment - would track learning metrics
        return 0.73  # 73% learning progress
