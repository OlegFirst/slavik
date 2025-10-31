# -*- coding: utf-8 -*-

from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)

class BcmExerciseEventBus(models.Model):
    _inherit = 'bcm.exercise'
    
    @api.model
    def handle_exercise_scheduled_event(self, event_data):
        """Handle bcm.exercise.scheduled event from EventBus"""
        try:
            exercise_id = event_data.get('exercise_id')
            if exercise_id:
                exercise = self.browse(exercise_id)
                if exercise.exists():
                    # Update exercise status if needed
                    if exercise.state != 'scheduled':
                        exercise.write({'state': 'scheduled'})
                    
                    # Send additional notifications or perform other actions
                    _logger.info(f"Exercise {exercise.name} has been scheduled via EventBus")
                    
        except Exception as e:
            _logger.error(f"Error handling exercise scheduled event: {e}")
    
    @api.model
    def handle_exercise_completion_event(self, event_data):
        """Handle external system notification about exercise completion"""
        try:
            exercise_id = event_data.get('exercise_id')
            completion_data = event_data.get('completion_data', {})
            
            if exercise_id:
                exercise = self.browse(exercise_id)
                if exercise.exists():
                    # Update exercise status
                    exercise.write({
                        'state': 'completed',
                        'actual_end': completion_data.get('end_time')
                    })
                    
                    # Send completion notification
                    exercise._send_status_notification()
                    
                    _logger.info(f"Exercise {exercise.name} marked as completed via EventBus")
                    
        except Exception as e:
            _logger.error(f"Error handling exercise completion event: {e}")
    
    def action_notify_external_systems(self):
        """Notify external systems about exercise status change"""
        try:
            event_data = {
                'exercise_id': self.id,
                'exercise_name': self.name,
                'exercise_type': self.exercise_type,
                'current_state': self.state,
                'planned_date': self.planned_date.isoformat() if self.planned_date else None,
                'facilitator_id': self.assigned_facilitator.id if self.assigned_facilitator else None,
                'participants': [{'id': p.id, 'name': p.name} for p in self.participant_ids],
                'company_id': self.company_id.id,
                'scenario_summary': self.scenario[:200] + '...' if self.scenario and len(self.scenario) > 200 else self.scenario
            }
            
            # Send to external systems via EventBus
            self.send_event_to_eventbus(f'bcm.exercise.status_changed', event_data)
            
            # Also send specific events for integrations
            if self.state == 'scheduled':
                self.send_event_to_eventbus('moodle.training.schedule', {
                    'training_id': f'bcm_exercise_{self.id}',
                    'title': f'BCM Exercise: {self.name}',
                    'description': self.scenario or 'BCM Exercise Training',
                    'scheduled_date': self.planned_date.isoformat() if self.planned_date else None,
                    'participants': [p.email for p in self.participant_ids if p.email]
                })
            
            if self.state == 'completed':
                self.send_event_to_eventbus('thehive.case.create', {
                    'title': f'Post-Exercise Review: {self.name}',
                    'description': f'Review findings and lessons learned from {self.exercise_type} exercise',
                    'tags': ['bcm', 'exercise', 'review', self.exercise_type],
                    'severity': 'low',
                    'tlp': 'green',
                    'source': 'BCM Portal'
                })
                
        except Exception as e:
            _logger.error(f"Error notifying external systems: {e}")
