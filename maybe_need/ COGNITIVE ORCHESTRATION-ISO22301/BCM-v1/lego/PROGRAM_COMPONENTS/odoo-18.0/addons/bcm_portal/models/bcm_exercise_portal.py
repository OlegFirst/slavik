# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class BCMExercise(models.Model):
    _inherit = 'bcm.exercise'
    
    # Portal-specific fields
    requested_by = fields.Many2one('res.users', string='Requested By')
    participant_ids = fields.Many2many('res.users', string='Participants')
    scenario = fields.Text('Exercise Scenario')
    ai_generated = fields.Boolean('AI Generated Scenario', default=False)
    exercise_type = fields.Selection([
        ('tabletop', 'Tabletop Exercise'),
        ('walkthrough', 'Walkthrough'),
        ('simulation', 'Simulation'),
        ('fullscale', 'Full-Scale Exercise')
    ], string='Exercise Type', default='tabletop')
    
    def action_generate_scenario(self):
        """Generate exercise scenario using AI Orchestrator"""
        self.ensure_one()
        
        try:
            # Prepare context for Orchestrator
            context_data = {
                'exercise_type': self.exercise_type,
                'current_scenario': self.scenario or '',
                'participants_count': len(self.participant_ids),
                'company_processes': [p.name for p in self.env['bcm.process'].search([
                    ('company_id', '=', self.company_id.id)
                ], limit=5)]
            }
            
            # Call Orchestrator
            result = self.call_orchestrator('/api/recommendations', {
                'context': f'Generate {self.exercise_type} BCM exercise scenario',
                'data': context_data,
                'tenant_id': self.company_id.id
            })
            
            if result:
                scenario = result.get('recommendation', '')
                alternatives = result.get('alternatives', [])
                
                # Build comprehensive scenario
                full_scenario = scenario
                if alternatives:
                    full_scenario += "\n\nAlternative Scenarios:\n"
                    for i, alt in enumerate(alternatives, 1):
                        full_scenario += f"{i}. {alt.get('option', '')}\n"
                
                self.write({
                    'scenario': full_scenario,
                    'ai_generated': True,
                    'state': 'planned'
                })
                
                # Send event
                self.send_event_to_eventbus('bcm.exercise.scenario_generated', {
                    'exercise_id': self.id,
                    'exercise_type': self.exercise_type,
                    'ai_generated': True
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Scenario Generated'),
                        'message': _('AI has generated an exercise scenario successfully'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise Exception(_("Failed to generate scenario from Orchestrator"))
                
        except Exception as e:
            raise Exception(_(f"Error generating scenario: {str(e)}"))
    
    def action_schedule_exercise(self):
        """Schedule the exercise"""
        self.ensure_one()
        
        if not self.scenario:
            self.action_generate_scenario()
        
        self.write({'state': 'scheduled'})
        
        # Send event
        self.send_event_to_eventbus('bcm.exercise.scheduled', {
            'exercise_id': self.id,
            'exercise_type': self.exercise_type,
            'planned_date': self.planned_date.isoformat() if self.planned_date else None,
            'participants_count': len(self.participant_ids)
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Exercise Scheduled'),
                'message': _('Exercise has been scheduled successfully'),
                'type': 'success',
                'sticky': False,
            }
        }

class BCMTraining(models.Model):
    _inherit = 'bcm.training'
    
    # Portal-specific fields
    requested_by = fields.Many2one('res.users', string='Requested By')
    attendee_ids = fields.Many2many('res.users', string='Attendees')
    training_type = fields.Selection([
        ('awareness', 'Awareness Training'),
        ('technical', 'Technical Training'),
        ('leadership', 'Leadership Training'),
        ('tabletop', 'Tabletop Exercise Training')
    ], string='Training Type', default='awareness')
    topic = fields.Char('Training Topic')
    materials = fields.Text('Training Materials')
    
    def action_generate_materials(self):
        """Generate training materials using AI Orchestrator"""
        self.ensure_one()
        
        try:
            # Call Orchestrator for training materials
            result = self.call_orchestrator('/api/recommendations', {
                'context': f'Generate {self.training_type} training materials for BCM',
                'data': {
                    'training_type': self.training_type,
                    'topic': self.topic or 'Business Continuity Management',
                    'attendees_count': len(self.attendee_ids),
                    'company_context': self.company_id.name
                },
                'tenant_id': self.company_id.id
            })
            
            if result:
                materials = result.get('recommendation', '')
                
                self.write({
                    'materials': materials,
                    'state': 'planned'
                })
                
                # Send event
                self.send_event_to_eventbus('bcm.training.materials_generated', {
                    'training_id': self.id,
                    'training_type': self.training_type,
                    'topic': self.topic
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Materials Generated'),
                        'message': _('Training materials have been generated successfully'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise Exception(_("Failed to generate materials from Orchestrator"))
                
        except Exception as e:
            raise Exception(_(f"Error generating materials: {str(e)}"))
    
    def action_schedule_training(self):
        """Schedule the training"""
        self.ensure_one()
        
        if not self.materials:
            self.action_generate_materials()
        
        self.write({'state': 'scheduled'})
        
        # Send event
        self.send_event_to_eventbus('bcm.training.scheduled', {
            'training_id': self.id,
            'training_type': self.training_type,
            'topic': self.topic,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'attendees_count': len(self.attendee_ids)
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Training Scheduled'),
                'message': _('Training has been scheduled successfully'),
                'type': 'success',
                'sticky': False,
            }
        }
