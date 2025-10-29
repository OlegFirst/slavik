# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class BCMPlanActions(models.Model):
    _inherit = 'bcm.plan'  
    _description = 'BCM Plan Actions'
    
    draft_steps = fields.Text('Draft Steps', readonly=True)
    ai_generated = fields.Boolean('AI Generated', default=False)
    
    def action_generate_draft(self):
        """Generate draft plan using AI Orchestrator"""
        self.ensure_one()
        
        try:
            # Prepare context for Orchestrator
            context_data = {
                'plan_type': self.plan_type or 'BCP',
                'based_on_bia': bool(self.bia_id),
                'bia_data': {
                    'rto': self.bia_id.computed_rto if self.bia_id else 0,
                    'rpo': self.bia_id.computed_rpo if self.bia_id else 0,
                    'critical_processes': [p.name for p in self.bia_id.process_ids] if self.bia_id else []
                } if self.bia_id else {},
                'scope': self.scope or ''
            }
            
            # Call Orchestrator
            result = self.call_orchestrator('/api/recommendations', {
                'context': f'Generate {self.plan_type or "BCP"} plan draft',
                'data': context_data,
                'tenant_id': self.company_id.id
            })
            
            if result:
                # Extract draft steps
                draft_content = result.get('recommendation', '')
                alternatives = result.get('alternatives', [])
                
                # Create draft steps
                steps = []
                for i, alt in enumerate(alternatives, 1):
                    steps.append(f"{i}. {alt.get('option', '')}")
                
                self.write({
                    'draft_steps': draft_content + '\n\nRecommended Steps:\n' + '\n'.join(steps),
                    'ai_generated': True,
                    'state': 'draft'
                })
                
                # Send event
                self.send_event_to_eventbus('bcm.plan.draft_generated', {
                    'plan_id': self.id,
                    'plan_type': self.plan_type,
                    'ai_generated': True
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Draft Plan Generated'),
                        'message': _('AI has generated a draft plan successfully'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_("Failed to generate draft from Orchestrator"))
                
        except Exception as e:
            raise UserError(_(f"Error generating draft: {str(e)}"))
