# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import json
from datetime import datetime

class BCMPortalController(CustomerPortal):
    
    @http.route('/portal/exercises', type='http', auth='user', website=True)
    def portal_exercises(self, **kwargs):
        """Portal page for exercises"""
        # Get current user's exercises
        exercises = request.env['bcm.exercise.management'].sudo().search([
            ('company_id', '=', request.env.company.id)
        ])
        
        values = {
            'exercises': exercises,
            'page_name': 'exercises'
        }
        return request.render('bcm_portal.portal_exercises', values)
    
    @http.route('/portal/exercise/request', type='http', auth='user', website=True)
    def portal_exercise_request_form(self, **kwargs):
        """Display exercise request form"""
        # Get available users for participants selection
        company_users = request.env['res.users'].sudo().search([
            ('company_id', '=', request.env.company.id),
            ('active', '=', True)
        ])
        
        values = {
            'page_name': 'exercise_request',
            'company_users': company_users,
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
                pass
            
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
                pass
            
            # Redirect to exercise status page
            return request.redirect(f'/portal/exercise/status')
            
        except Exception as e:
            # Return to form with error message
            request.session['exercise_request_error'] = str(e)
            return request.redirect('/portal/exercise/request')
    
    @http.route('/portal/training', type='http', auth='user', website=True)
    def portal_training(self, **kwargs):
        """Portal page for training"""
        # Get current user's training
        training = request.env['bcm.training'].sudo().search([
            ('company_id', '=', request.env.company.id)
        ])
        
        values = {
            'training': training,
            'page_name': 'training'
        }
        return request.render('bcm_portal.portal_training', values)
    
    @http.route('/portal/training/request', type='json', auth='user', methods=['POST'], csrf=False)
    def request_training(self, **kwargs):
        """Request new training"""
        try:
            training_type = kwargs.get('training_type', 'awareness')
            topic = kwargs.get('topic', '')
            preferred_date = kwargs.get('preferred_date')
            attendees = kwargs.get('attendees', [])
            
            # Create training request
            training = request.env['bcm.training'].sudo().create({
                'name': f"Training Request - {topic}",
                'training_type': training_type,
                'topic': topic,
                'scheduled_date': preferred_date,
                'state': 'requested',
                'company_id': request.env.company.id,
                'requested_by': request.env.user.id,
                'attendee_ids': [(6, 0, attendees)] if attendees else []
            })
            
            # Send event to EventBus
            training.send_event_to_eventbus('bcm.training.requested', {
                'training_id': training.id,
                'training_type': training_type,
                'topic': topic,
                'scheduled_date': preferred_date,
                'attendees_count': len(attendees)
            })
            
            return {
                'status': 'success',
                'training_id': training.id,
                'message': 'Training request submitted successfully'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @http.route('/portal/bcm/dashboard', type='http', auth='user', website=True)
    def portal_bcm_dashboard(self, **kwargs):
        """BCM Portal Dashboard"""
        # Get user's BCM data
        company = request.env.company
        
        # Recent exercises
        recent_exercises = request.env['bcm.exercise.management'].sudo().search([
            ('company_id', '=', company.id)
        ], limit=5, order='create_date desc')
        
        # Recent training
        recent_training = request.env['bcm.training'].sudo().search([
            ('company_id', '=', company.id)
        ], limit=5, order='create_date desc')
        
        # KPIs
        kpi_calculator = request.env['bcm.kpi.calculator'].sudo().search([
            ('company_id', '=', company.id)
        ], limit=1, order='create_date desc')
        
        # Incidents
        recent_incidents = request.env['bcm.incident'].sudo().search([
            ('company_id', '=', company.id)
        ], limit=3, order='create_date desc')
        
        values = {
            'recent_exercises': recent_exercises,
            'recent_training': recent_training,
            'kpi_data': kpi_calculator,
            'recent_incidents': recent_incidents,
            'page_name': 'bcm_dashboard'
        }
        return request.render('bcm_portal.portal_bcm_dashboard', values)
    
    @http.route('/portal/exercise/<int:exercise_id>/scenario', type='json', auth='user', methods=['GET'])
    def get_exercise_scenario(self, exercise_id, **kwargs):
        """Get AI-generated exercise scenario"""
        try:
            exercise = request.env['bcm.exercise.management'].sudo().browse(exercise_id)
            if not exercise.exists():
                return {'status': 'error', 'message': 'Exercise not found'}
            
            if exercise.company_id.id != request.env.company.id:
                return {'status': 'error', 'message': 'Access denied'}
            
            return {
                'status': 'success',
                'scenario': exercise.scenario,
                'exercise_type': exercise.exercise_type,
                'planned_date': exercise.planned_date.isoformat() if exercise.planned_date else None,
                'state': exercise.state
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @http.route('/portal/api/stats', type='json', auth='user', methods=['GET'])
    def get_portal_stats(self, **kwargs):
        """Get portal statistics"""
        try:
            company = request.env.company
            
            stats = {
                'exercises': {
                    'total': request.env['bcm.exercise.management'].sudo().search_count([
                        ('company_id', '=', company.id)
                    ]),
                    'completed': request.env['bcm.exercise.management'].sudo().search_count([
                        ('company_id', '=', company.id),
                        ('state', '=', 'completed')
                    ]),
                    'scheduled': request.env['bcm.exercise.management'].sudo().search_count([
                        ('company_id', '=', company.id),
                        ('state', '=', 'scheduled')
                    ])
                },
                'training': {
                    'total': request.env['bcm.training'].sudo().search_count([
                        ('company_id', '=', company.id)
                    ]),
                    'completed': request.env['bcm.training'].sudo().search_count([
                        ('company_id', '=', company.id),
                        ('state', '=', 'completed')
                    ]),
                    'scheduled': request.env['bcm.training'].sudo().search_count([
                        ('company_id', '=', company.id),
                        ('state', '=', 'scheduled')
                    ])
                },
                'incidents': {
                    'total': request.env['bcm.incident'].sudo().search_count([
                        ('company_id', '=', company.id)
                    ]),
                    'open': request.env['bcm.incident'].sudo().search_count([
                        ('company_id', '=', company.id),
                        ('state', 'in', ['draft', 'in_progress'])
                    ]),
                    'critical': request.env['bcm.incident'].sudo().search_count([
                        ('company_id', '=', company.id),
                        ('severity', '=', 'critical')
                    ])
                }
            }
            
            # Get KPI data
            kpi_calculator = request.env['bcm.kpi.calculator'].sudo().search([
                ('company_id', '=', company.id)
            ], limit=1, order='create_date desc')
            
            if kpi_calculator:
                stats['kpis'] = {
                    'bia_coverage': kpi_calculator.bia_coverage,
                    'plans_up_to_date': kpi_calculator.plans_up_to_date,
                    'capa_on_time': kpi_calculator.capa_on_time,
                    'exercise_completion': kpi_calculator.exercise_completion,
                    'training_completion': kpi_calculator.training_completion
                }
            
            return {
                'status': 'success',
                'data': stats
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
