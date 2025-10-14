# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError
import json
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class BCMExercisePortal(CustomerPortal):
    """Controller for BCM Exercise Portal functionality"""
    
    @http.route('/portal/exercise/request', type='http', auth='user', website=True)
    def portal_exercise_request_form(self, **kwargs):
        """Display exercise request form"""
        # Get available users for participants selection
        company_users = request.env['res.users'].sudo().search([
            ('company_id', '=', request.env.company.id),
            ('active', '=', True)
        ])
        
        # Check for error messages from session
        error_message = request.session.pop('exercise_request_error', None)
        success_message = request.session.pop('exercise_request_success', None)
        
        values = {
            'page_name': 'exercise_request',
            'company_users': company_users,
            'error_message': error_message,
            'success_message': success_message,
        }
        return request.render('bcm_portal.portal_exercise_request_form', values)
    
    @http.route('/portal/exercise/submit', type='http', auth='user', methods=['POST'], csrf=False)
    def submit_exercise_request(self, **kwargs):
        """Submit new exercise request from form"""
        try:
            # Extract form data
            exercise_type = kwargs.get('exercise_type', 'tabletop')
            scenario_description = kwargs.get('scenario_description', '')
            participants = kwargs.get('participants', '').split(',') if kwargs.get('participants') else []
            preferred_datetime = kwargs.get('preferred_datetime')
            
            # Convert participant IDs to integers
            participant_ids = []
            for pid in participants:
                if pid.strip():
                    try:
                        participant_ids.append(int(pid.strip()))
                    except ValueError:
                        continue
            
            # Create exercise request
            exercise = request.env['bcm.exercise.management'].sudo().create({
                'name': f"Exercise Request - {exercise_type.title()} - {datetime.now().strftime('%Y-%m-%d')}",
                'exercise_type': exercise_type,
                'scenario': scenario_description,
                'planned_date': preferred_datetime if preferred_datetime else False,
                'state': 'requested',
                'company_id': request.env.company.id,
                'requested_by': request.env.user.id,
                'participant_ids': [(6, 0, participant_ids)] if participant_ids else []
            })
            
            # Generate scenario using Orchestrator if available
            try:
                orchestrator_result = exercise.call_orchestrator('/api/recommendations', {
                    'context': f'Generate {exercise_type} exercise scenario for BCM training',
                    'data': {
                        'exercise_type': exercise_type,
                        'scenario_base': scenario_description,
                        'participants_count': len(participant_ids),
                        'company_name': request.env.company.name
                    },
                    'tenant_id': request.env.company.id
                })
                
                if orchestrator_result:
                    enhanced_scenario = orchestrator_result.get('recommendation', scenario_description)
                    exercise.write({
                        'scenario': enhanced_scenario,
                        'ai_generated': True
                    })
            except Exception as e:
                # Continue even if orchestrator fails
                _logger.warning(f"Orchestrator call failed: {e}")
            
            # Send event to EventBus
            try:
                exercise.send_event_to_eventbus('bcm.exercise.requested', {
                    'exercise_id': exercise.id,
                    'exercise_name': exercise.name,
                    'exercise_type': exercise_type,
                    'requested_date': preferred_datetime,
                    'requested_by': request.env.user.name,
                    'participants_count': len(participant_ids),
                    'company_id': request.env.company.id
                })
            except Exception as e:
                # Continue even if event bus fails
                _logger.warning(f"EventBus call failed: {e}")
            
            # Set success message and redirect to status page
            request.session['exercise_request_success'] = f'Exercise request submitted successfully! Request ID: {exercise.id}'
            return request.redirect(f'/portal/exercise/status')
            
        except Exception as e:
            # Return to form with error message
            request.session['exercise_request_error'] = str(e)
            return request.redirect('/portal/exercise/request')
    
    @http.route('/portal/exercise/status', type='http', auth='user', website=True)
    def portal_exercise_status(self, **kwargs):
        """Display exercise status tracking page"""
        # Get user's exercise requests
        exercises = request.env['bcm.exercise.management'].sudo().search([
            ('company_id', '=', request.env.company.id),
            ('requested_by', '=', request.env.user.id)
        ], order='create_date desc')
        
        # Get all company exercises for admin view
        all_exercises = request.env['bcm.exercise.management'].sudo().search([
            ('company_id', '=', request.env.company.id)
        ], order='create_date desc')
        
        # Check for success messages
        success_message = request.session.pop('exercise_request_success', None)
        
        values = {
            'page_name': 'exercise_status',
            'exercises': exercises,
            'all_exercises': all_exercises,
            'can_view_all': request.env.user.has_group('base.group_system') or request.env.user.has_group('bcm_core.group_bcm_manager'),
            'success_message': success_message,
        }
        return request.render('bcm_portal.portal_exercise_status', values)
    
    @http.route('/portal/exercise/<int:exercise_id>/download', type='http', auth='user', website=True)
    def download_exercise_materials(self, exercise_id, **kwargs):
        """Download exercise materials"""
        try:
            exercise = request.env['bcm.exercise.management'].sudo().browse(exercise_id)
            if not exercise.exists():
                return request.not_found()
            
            # Check access
            if exercise.company_id.id != request.env.company.id:
                return request.not_found()
            
            # Create exercise materials content
            content = f"""Exercise Materials - {exercise.name}
===============================================

Exercise Details:
- Name: {exercise.name}
- Type: {exercise.exercise_type}
- Status: {exercise.state}
- Requested by: {exercise.requested_by.name if exercise.requested_by else 'Unknown'}
- Requested date: {exercise.create_date}
- Planned date: {exercise.planned_date or 'Not scheduled yet'}
- Participants: {len(exercise.participant_ids)} users

Scenario:
---------
{exercise.scenario or 'No scenario available yet.'}

Participants:
-------------
{chr(10).join([f"- {p.name}" for p in exercise.participant_ids]) if exercise.participant_ids else "No participants assigned yet."}

Status Information:
------------------
Current Status: {dict(exercise._fields['state'].selection).get(exercise.state, exercise.state)}

Exercise Materials:
------------------
This document contains the basic exercise information. In a full implementation, 
this would include:
- Detailed exercise procedures
- Role-playing instructions
- Scenario injects and timeline
- Evaluation criteria
- Resource requirements
- Safety procedures
- Post-exercise evaluation forms

---
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
BCM Portal - Exercise Materials
"""
            
            # Create response
            response = request.make_response(
                content,
                headers=[
                    ('Content-Type', 'text/plain; charset=utf-8'),
                    ('Content-Disposition', f'attachment; filename=exercise_{exercise.id}_materials.txt')
                ]
            )
            return response
            
        except Exception as e:
            _logger.error(f"Error downloading exercise materials: {e}")
            return request.not_found()
    
    @http.route('/portal/exercise/<int:exercise_id>/feedback', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def exercise_feedback(self, exercise_id, **kwargs):
        """Submit post-exercise feedback"""
        try:
            exercise = request.env['bcm.exercise.management'].sudo().browse(exercise_id)
            if not exercise.exists():
                return request.not_found()
            
            # Check access
            if exercise.company_id.id != request.env.company.id:
                return request.not_found()
            
            # Only allow feedback for completed exercises
            if exercise.state != 'completed':
                return request.redirect('/portal/exercise/status')
            
            if request.httprequest.method == 'POST':
                # Process feedback submission
                feedback_data = {
                    'exercise_rating': int(kwargs.get('exercise_rating', 0)),
                    'scenario_realism': int(kwargs.get('scenario_realism', 0)),
                    'facilitator_rating': int(kwargs.get('facilitator_rating', 0)),
                    'learning_objectives': kwargs.get('learning_objectives', ''),
                    'improvements': kwargs.get('improvements', ''),
                    'additional_comments': kwargs.get('additional_comments', ''),
                    'submitted_by': request.env.user.name,
                    'submitted_date': datetime.now().isoformat()
                }
                
                # Store feedback in exercise record
                exercise.write({
                    'feedback_data': json.dumps(feedback_data),
                    'feedback_submitted': True,
                    'feedback_date': datetime.now()
                })
                
                # Send feedback event
                try:
                    exercise.send_event_to_eventbus('bcm.exercise.feedback_submitted', {
                        'exercise_id': exercise.id,
                        'exercise_name': exercise.name,
                        'feedback_by': request.env.user.name,
                        'ratings': {
                            'exercise_rating': feedback_data.get('exercise_rating', 0),
                            'scenario_realism': feedback_data.get('scenario_realism', 0),
                            'facilitator_rating': feedback_data.get('facilitator_rating', 0)
                        },
                        'company_id': request.env.company.id
                    })
                except Exception as e:
                    _logger.warning(f"EventBus feedback call failed: {e}")
                
                # Set success message and redirect
                request.session['feedback_success'] = 'Thank you for your feedback! Your input helps us improve future exercises.'
                return request.redirect('/portal/exercise/status')
            
            # Display feedback form
            values = {
                'page_name': 'exercise_feedback',
                'exercise': exercise,
            }
            return request.render('bcm_portal.portal_exercise_feedback', values)
            
        except Exception as e:
            _logger.error(f"Error in exercise feedback: {e}")
            return request.not_found()
    
    @http.route('/portal/exercise/history', type='http', auth='user', website=True)
    def exercise_history(self, **kwargs):
        """Display exercise history"""
        # Get user's completed exercises
        completed_exercises = request.env['bcm.exercise.management'].sudo().search([
            ('company_id', '=', request.env.company.id),
            ('state', '=', 'completed')
        ], order='write_date desc')
        
        # Filter by user participation if not admin
        if not (request.env.user.has_group('base.group_system') or request.env.user.has_group('bcm_core.group_bcm_manager')):
            completed_exercises = completed_exercises.filtered(
                lambda e: request.env.user in e.participant_ids or e.requested_by == request.env.user
            )
        
        values = {
            'page_name': 'exercise_history',
            'completed_exercises': completed_exercises,
        }
        return request.render('bcm_portal.portal_exercise_history', values)
