# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class BCMAPIController(http.Controller):
    
    @http.route('/bcm/plan/update', type='json', auth='user', methods=['POST'], cors='*')
    def update_plan(self, **kwargs):
        """Update a BCM plan"""
        try:
            data = kwargs
            plan_id = data.get('plan_id') or data.get('id')
            
            if not plan_id:
                return {
                    'status': 'error',
                    'message': 'Plan ID is required'
                }
            
            # Find the plan
            plan = request.env['bcm.plan'].search([('id', '=', plan_id)], limit=1)
            if not plan:
                return {
                    'status': 'error',
                    'message': f'Plan with ID {plan_id} not found'
                }
            
            # Update plan with provided data
            update_data = {}
            if 'name' in data:
                update_data['name'] = data['name']
            if 'description' in data:
                update_data['description'] = data['description']
            if 'plan_type' in data:
                update_data['plan_type'] = data['plan_type']
            if 'status' in data:
                update_data['status'] = data['status']
            if 'recovery_procedures' in data:
                update_data['recovery_procedures'] = data['recovery_procedures']
            if 'activation_criteria' in data:
                update_data['activation_criteria'] = data['activation_criteria']
            
            if update_data:
                plan.write(update_data)
            
            # Send event to EventBus if available
            try:
                plan.send_event_to_eventbus('bcm.plan.updated', {
                    'plan_id': plan.id,
                    'plan_name': plan.name,
                    'updated_fields': list(update_data.keys()),
                    'company_id': plan.company_id.id
                })
            except Exception as e:
                _logger.warning(f"Could not send event to EventBus: {e}")
            
            return {
                'status': 'success',
                'message': 'Plan updated successfully',
                'plan_id': plan.id,
                'updated_fields': list(update_data.keys())
            }
            
        except Exception as e:
            _logger.error(f"Error updating plan: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @http.route('/bcm/incident/update', type='json', auth='user', methods=['POST'], cors='*')
    def update_incident(self, **kwargs):
        """Update a BCM incident"""
        try:
            data = kwargs
            incident_id = data.get('incident_id') or data.get('id')
            
            if not incident_id:
                return {
                    'status': 'error',
                    'message': 'Incident ID is required'
                }
            
            # Find the incident
            incident = request.env['bcm.incident'].search([('id', '=', incident_id)], limit=1)
            if not incident:
                return {
                    'status': 'error',
                    'message': f'Incident with ID {incident_id} not found'
                }
            
            # Update incident with provided data
            update_data = {}
            if 'name' in data:
                update_data['name'] = data['name']
            if 'description' in data:
                update_data['description'] = data['description']
            if 'severity' in data:
                update_data['severity'] = data['severity']
            if 'status' in data:
                update_data['status'] = data['status']
            if 'category' in data:
                update_data['category'] = data['category']
            if 'resolution_notes' in data:
                update_data['resolution_notes'] = data['resolution_notes']
            
            if update_data:
                incident.write(update_data)
            
            # Send event to EventBus if available
            try:
                incident.send_event_to_eventbus('bcm.incident.updated', {
                    'incident_id': incident.id,
                    'incident_name': incident.name,
                    'severity': incident.severity,
                    'status': incident.status,
                    'updated_fields': list(update_data.keys()),
                    'company_id': incident.company_id.id
                })
            except Exception as e:
                _logger.warning(f"Could not send event to EventBus: {e}")
            
            return {
                'status': 'success',
                'message': 'Incident updated successfully',
                'incident_id': incident.id,
                'updated_fields': list(update_data.keys())
            }
            
        except Exception as e:
            _logger.error(f"Error updating incident: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @http.route('/bcm/incident/update_checklist', type='json', auth='user', methods=['POST'], cors='*')
    def update_incident_checklist(self, **kwargs):
        """Update incident response checklist"""
        try:
            data = kwargs
            incident_id = data.get('incident_id')
            checklist = data.get('checklist', [])
            ai_generated = data.get('ai_generated', False)
            
            if not incident_id:
                return {
                    'status': 'error',
                    'message': 'Incident ID is required'
                }
            
            # Find the incident
            incident = request.env['bcm.incident'].search([('id', '=', incident_id)], limit=1)
            if not incident:
                return {
                    'status': 'error',
                    'message': f'Incident with ID {incident_id} not found'
                }
            
            # Update incident checklist
            update_data = {
                'response_checklist': json.dumps(checklist) if isinstance(checklist, list) else checklist,
                'ai_generated_checklist': ai_generated
            }
            
            incident.write(update_data)
            
            # Send event to EventBus if available
            try:
                incident.send_event_to_eventbus('bcm.incident.checklist_updated', {
                    'incident_id': incident.id,
                    'incident_name': incident.name,
                    'checklist_items': len(checklist) if isinstance(checklist, list) else 0,
                    'ai_generated': ai_generated,
                    'company_id': incident.company_id.id
                })
            except Exception as e:
                _logger.warning(f"Could not send event to EventBus: {e}")
            
            return {
                'status': 'success',
                'message': 'Incident checklist updated successfully',
                'incident_id': incident.id,
                'checklist_items': len(checklist) if isinstance(checklist, list) else 0,
                'ai_generated': ai_generated
            }
            
        except Exception as e:
            _logger.error(f"Error updating incident checklist: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @http.route('/bcm/plan/create', type='json', auth='user', methods=['POST'], cors='*')
    def create_plan(self, **kwargs):
        """Create a new BCM plan"""
        try:
            data = kwargs
            
            # Required fields
            if not data.get('name'):
                return {
                    'status': 'error',
                    'message': 'Plan name is required'
                }
            
            # Create plan
            plan_data = {
                'name': data['name'],
                'description': data.get('description', ''),
                'plan_type': data.get('plan_type', 'recovery'),
                'company_id': request.env.company.id,
                'status': data.get('status', 'draft'),
                'recovery_procedures': data.get('recovery_procedures', ''),
                'activation_criteria': data.get('activation_criteria', '')
            }
            
            plan = request.env['bcm.plan'].create(plan_data)
            
            # Send event to EventBus if available
            try:
                plan.send_event_to_eventbus('bcm.plan.created', {
                    'plan_id': plan.id,
                    'plan_name': plan.name,
                    'plan_type': plan.plan_type,
                    'company_id': plan.company_id.id
                })
            except Exception as e:
                _logger.warning(f"Could not send event to EventBus: {e}")
            
            return {
                'status': 'success',
                'message': 'Plan created successfully',
                'plan_id': plan.id,
                'plan_name': plan.name
            }
            
        except Exception as e:
            _logger.error(f"Error creating plan: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @http.route('/bcm/incident/create', type='json', auth='user', methods=['POST'], cors='*')
    def create_incident(self, **kwargs):
        """Create a new BCM incident"""
        try:
            data = kwargs
            
            # Required fields
            if not data.get('name'):
                return {
                    'status': 'error',
                    'message': 'Incident name is required'
                }
            
            # Create incident
            incident_data = {
                'name': data['name'],
                'description': data.get('description', ''),
                'severity': data.get('severity', 'medium'),
                'category': data.get('category', 'operational'),
                'company_id': request.env.company.id,
                'status': data.get('status', 'draft'),
                'assigned_user_id': data.get('assigned_user_id') or request.env.user.id
            }
            
            incident = request.env['bcm.incident'].create(incident_data)
            
            # Send event to EventBus if available
            try:
                incident.send_event_to_eventbus('bcm.incident.created', {
                    'incident_id': incident.id,
                    'incident_name': incident.name,
                    'severity': incident.severity,
                    'category': incident.category,
                    'company_id': incident.company_id.id
                })
            except Exception as e:
                _logger.warning(f"Could not send event to EventBus: {e}")
            
            return {
                'status': 'success',
                'message': 'Incident created successfully',
                'incident_id': incident.id,
                'incident_name': incident.name
            }
            
        except Exception as e:
            _logger.error(f"Error creating incident: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }