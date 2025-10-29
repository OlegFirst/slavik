# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, ValidationError
import logging
import json

_logger = logging.getLogger(__name__)

class BcmWebPortalMain(CustomerPortal):
    """
    Unified Web Portal Controller
    Объединяет функциональность bcm_portal + admin_website
    """
    
    def _prepare_home_portal_values(self, counters):
        """Prepare portal home page values with BCM data"""
        values = super()._prepare_home_portal_values(counters)
        
        # Get portal configuration for current user
        portal_config = self._get_portal_config()
        if portal_config:
            values['portal_config'] = portal_config
            
            # Add BCM-specific counters if enabled
            if portal_config.enable_dashboard:
                client = self._get_user_client()
                if client:
                    bcm_data = self._prepare_bcm_counters(client, counters)
                    values.update(bcm_data)
        
        return values
    
    def _get_portal_config(self):
        """Get portal configuration for current user"""
        user = request.env.user
        
        # Find appropriate portal based on user access
        portals = request.env['bcm.web.portal'].search([
            ('active', '=', True)
        ])
        
        for portal in portals:
            if portal.check_portal_access(user):
                return portal
        
        return None
    
    def _get_user_client(self):
        """Get client for current user"""
        if not request.env.user.has_group('base.group_portal'):
            return None
            
        contact = request.env['bcm.client.contact'].search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        return contact.client_id if contact else None
    
    def _prepare_bcm_counters(self, client, counters):
        """Prepare BCM-specific counters for dashboard"""
        bcm_data = {}
        
        try:
            if 'bcm_processes' in counters:
                bcm_data['bcm_process_count'] = request.env['bcm.process'].search_count([
                    ('company_id', '=', client.company_id.id)
                ])
            
            if 'bcm_plans' in counters:
                bcm_data['bcm_plan_count'] = request.env['bcm.plan'].search_count([
                    ('company_id', '=', client.company_id.id)
                ])
            
            if 'bcm_incidents' in counters:
                bcm_data['bcm_incident_count'] = request.env['bcm.incident'].search_count([
                    ('company_id', '=', client.company_id.id),
                    ('status', 'not in', ['closed', 'resolved'])
                ])
            
            if 'bcm_exercises' in counters:
                bcm_data['bcm_exercise_count'] = request.env['bcm.exercise'].search_count([
                    ('company_id', '=', client.company_id.id)
                ])
                
        except Exception as e:
            _logger.warning(f"Error preparing BCM counters: {e}")
            
        return bcm_data
    
    # === MAIN PORTAL ROUTES ===
    
    @http.route('/portal', type='http', auth='public', website=True)
    def portal_home(self, **kwargs):
        """Main portal entry point with automatic routing"""
        user = request.env.user
        portal_config = self._get_portal_config()
        
        if not portal_config:
            return request.render('bcm_web_portal.no_portal_access', {
                'error_message': _('No portal access configured for your account.')
            })
        
        # Log portal access
        request_info = {
            'ip_address': request.httprequest.environ.get('REMOTE_ADDR'),
            'user_agent': request.httprequest.headers.get('User-Agent'),
            'request_path': request.httprequest.path,
        }
        portal_config.log_portal_access(user, request_info)
        
        # Route based on portal type and user permissions
        if portal_config.portal_type == 'admin' and user.has_group('bcm_web_portal.group_portal_admin'):
            return self._redirect_to_admin_interface()
        elif portal_config.portal_type == 'client' and user.has_group('base.group_portal'):
            return self._redirect_to_client_portal()
        elif portal_config.portal_type == 'public':
            return self._redirect_to_public_portal()
        else:
            # Default behavior - show portal selector or main dashboard
            return self._show_portal_dashboard(portal_config)
    
    @http.route('/portal/<int:portal_id>', type='http', auth='public', website=True)
    def portal_specific(self, portal_id, **kwargs):
        """Access specific portal by ID"""
        portal = request.env['bcm.web.portal'].browse(portal_id)
        
        if not portal.exists() or not portal.active:
            return request.not_found()
        
        if not portal.check_portal_access(request.env.user):
            return request.render('bcm_web_portal.access_denied', {
                'portal_name': portal.name
            })
        
        # Route to appropriate interface
        if portal.portal_type == 'admin':
            return self._show_admin_interface(portal)
        elif portal.portal_type == 'client':
            return self._show_client_portal(portal)
        else:
            return self._show_public_portal(portal)
    
    # === DASHBOARD ROUTES ===
    
    @http.route('/my/bcm', type='http', auth='user', website=True)
    def bcm_dashboard(self, **kwargs):
        """Main BCM dashboard"""
        portal_config = self._get_portal_config()
        client = self._get_user_client()
        
        if not portal_config or not portal_config.enable_dashboard:
            return request.redirect('/my')
        
        if not client:
            return request.render('bcm_web_portal.no_client_access', {
                'error_message': _('You do not have access to any BCM client data.')
            })
        
        # Prepare dashboard data
        dashboard_data = self._prepare_dashboard_data(client, portal_config)
        
        values = {
            'page_name': 'bcm_dashboard',
            'portal_config': portal_config,
            'client': client,
            'dashboard_data': dashboard_data,
        }
        
        return request.render('bcm_web_portal.bcm_dashboard', values)
    
    def _prepare_dashboard_data(self, client, portal_config):
        """Prepare comprehensive dashboard data"""
        try:
            data = {}
            
            # BIA Coverage
            if portal_config.enable_bia_access:
                total_processes = request.env['bcm.process'].search_count([
                    ('company_id', '=', client.company_id.id)
                ])
                analyzed_processes = request.env['bcm.bia.result'].search_count([
                    ('company_id', '=', client.company_id.id)
                ])
                data['bia_coverage'] = (analyzed_processes / total_processes * 100) if total_processes > 0 else 0
                data['total_processes'] = total_processes
                data['analyzed_processes'] = analyzed_processes
            
            # Plans Status
            if portal_config.enable_plans_access:
                plans = request.env['bcm.plan'].search([
                    ('company_id', '=', client.company_id.id),
                    ('status', '=', 'active')
                ])
                data['active_plans'] = len(plans)
                
                # Calculate average plan age
                if plans:
                    from datetime import datetime
                    ages = [(datetime.now().date() - plan.last_updated.date()).days 
                           for plan in plans if plan.last_updated]
                    data['avg_plan_age'] = sum(ages) / len(ages) if ages else 0
                else:
                    data['avg_plan_age'] = 0
            
            # Incidents
            if portal_config.enable_incident_reporting:
                data['open_incidents'] = request.env['bcm.incident'].search_count([
                    ('company_id', '=', client.company_id.id),
                    ('status', 'not in', ['closed', 'resolved'])
                ])
                
                data['recent_incidents'] = request.env['bcm.incident'].search([
                    ('company_id', '=', client.company_id.id)
                ], limit=5, order='create_date desc')
            
            # Exercises
            if portal_config.enable_exercise_participation:
                data['upcoming_exercises'] = request.env['bcm.exercise'].search([
                    ('company_id', '=', client.company_id.id),
                    ('status', 'in', ['planned', 'scheduled']),
                    ('scheduled_date', '>', request.env.cr.now())
                ], limit=5, order='scheduled_date asc')
            
            # Training
            if portal_config.enable_training_access:
                training_completion = request.env['bcm.training.status'].search_count([
                    ('company_id', '=', client.company_id.id),
                    ('status', '=', 'completed')
                ])
                
                total_training = request.env['bcm.training.status'].search_count([
                    ('company_id', '=', client.company_id.id)
                ])
                
                data['training_percentage'] = (training_completion / total_training * 100) if total_training > 0 else 0
            
            # Findings
            data['open_findings'] = request.env['bcm.finding'].search_count([
                ('company_id', '=', client.company_id.id),
                ('status', 'not in', ['closed', 'resolved'])
            ])
            
            return data
            
        except Exception as e:
            _logger.error(f"Error preparing dashboard data: {e}")
            return {}
    
    # === SECTION ROUTES ===
    
    @http.route('/my/bcm/bia', type='http', auth='user', website=True)
    def bcm_bia_section(self, **kwargs):
        """BIA section"""
        portal_config = self._get_portal_config()
        client = self._get_user_client()
        
        if not portal_config or not portal_config.enable_bia_access:
            return request.redirect('/my')
        
        if not client:
            return self._redirect_no_access()
        
        # Get BIA data
        bia_surveys = request.env['bcm.bia.survey'].search([
            ('company_id', '=', client.company_id.id)
        ])
        
        bia_results = request.env['bcm.bia.result'].search([
            ('company_id', '=', client.company_id.id)
        ])
        
        values = {
            'page_name': 'bia',
            'portal_config': portal_config,
            'client': client,
            'bia_surveys': bia_surveys,
            'bia_results': bia_results,
        }
        
        return request.render('bcm_web_portal.bcm_bia_section', values)
    
    @http.route('/my/bcm/plans', type='http', auth='user', website=True)
    def bcm_plans_section(self, **kwargs):
        """Plans section"""
        portal_config = self._get_portal_config()
        client = self._get_user_client()
        
        if not portal_config or not portal_config.enable_plans_access:
            return request.redirect('/my')
        
        if not client:
            return self._redirect_no_access()
        
        plans = request.env['bcm.plan'].search([
            ('company_id', '=', client.company_id.id)
        ])
        
        values = {
            'page_name': 'plans',
            'portal_config': portal_config,
            'client': client,
            'plans': plans,
        }
        
        return request.render('bcm_web_portal.bcm_plans_section', values)
    
    @http.route('/my/bcm/incidents', type='http', auth='user', website=True)
    def bcm_incidents_section(self, **kwargs):
        """Incidents section"""
        portal_config = self._get_portal_config()
        client = self._get_user_client()
        
        if not portal_config or not portal_config.enable_incident_reporting:
            return request.redirect('/my')
        
        if not client:
            return self._redirect_no_access()
        
        incidents = request.env['bcm.incident'].search([
            ('company_id', '=', client.company_id.id)
        ])
        
        values = {
            'page_name': 'incidents',
            'portal_config': portal_config,
            'client': client,
            'incidents': incidents,
        }
        
        return request.render('bcm_web_portal.bcm_incidents_section', values)
    
    @http.route('/my/bcm/exercises', type='http', auth='user', website=True)
    def bcm_exercises_section(self, **kwargs):
        """Exercises section"""
        portal_config = self._get_portal_config()
        client = self._get_user_client()
        
        if not portal_config or not portal_config.enable_exercise_participation:
            return request.redirect('/my')
        
        if not client:
            return self._redirect_no_access()
        
        exercises = request.env['bcm.exercise'].search([
            ('company_id', '=', client.company_id.id)
        ])
        
        values = {
            'page_name': 'exercises',
            'portal_config': portal_config,
            'client': client,
            'exercises': exercises,
        }
        
        return request.render('bcm_web_portal.bcm_exercises_section', values)
    
    @http.route('/my/bcm/training', type='http', auth='user', website=True)
    def bcm_training_section(self, **kwargs):
        """Training section"""
        portal_config = self._get_portal_config()
        client = self._get_user_client()
        
        if not portal_config or not portal_config.enable_training_access:
            return request.redirect('/my')
        
        if not client:
            return self._redirect_no_access()
        
        trainings = request.env['bcm.training'].search([
            ('company_id', '=', client.company_id.id)
        ])
        
        training_status = request.env['bcm.training.status'].search([
            ('company_id', '=', client.company_id.id),
            ('user_id', '=', request.env.user.id)
        ])
        
        values = {
            'page_name': 'training',
            'portal_config': portal_config,
            'client': client,
            'trainings': trainings,
            'training_status': training_status,
        }
        
        return request.render('bcm_web_portal.bcm_training_section', values)
    
    # === AI ASSISTANT ROUTES ===
    
    @http.route('/portal/ai/chat', type='json', auth='user')
    def ai_assistant_chat(self, message, **kwargs):
        """AI assistant chat endpoint"""
        portal_config = self._get_portal_config()
        
        if not portal_config or not portal_config.enable_ai_assistant:
            return {'error': 'AI assistant not available'}
        
        try:
            # TODO: Integrate with AI service
            response = self._process_ai_message(message, portal_config)
            return {
                'response': response,
                'timestamp': fields.Datetime.now().isoformat()
            }
        except Exception as e:
            _logger.error(f"AI assistant error: {e}")
            return {'error': 'AI assistant temporarily unavailable'}
    
    def _process_ai_message(self, message, portal_config):
        """Process AI assistant message"""
        # Placeholder for AI integration
        return f"AI Response to: {message}"
    
    # === UTILITY METHODS ===
    
    def _redirect_to_admin_interface(self):
        """Redirect to admin interface"""
        return request.redirect('/portal/admin')
    
    def _redirect_to_client_portal(self):
        """Redirect to client portal"""
        return request.redirect('/my/bcm')
    
    def _redirect_to_public_portal(self):
        """Redirect to public portal"""
        return request.redirect('/')
    
    def _show_portal_dashboard(self, portal_config):
        """Show portal dashboard"""
        values = {
            'portal_config': portal_config,
        }
        return request.render('bcm_web_portal.portal_dashboard', values)
    
    def _show_admin_interface(self, portal):
        """Show admin interface"""
        values = {
            'portal_config': portal,
        }
        return request.render('bcm_web_portal.admin_interface', values)
    
    def _show_client_portal(self, portal):
        """Show client portal"""
        return request.redirect('/my/bcm')
    
    def _show_public_portal(self, portal):
        """Show public portal"""
        values = {
            'portal_config': portal,
        }
        return request.render('bcm_web_portal.public_portal', values)
    
    def _redirect_no_access(self):
        """Redirect when no access"""
        return request.render('bcm_web_portal.no_client_access', {
            'error_message': _('Access denied: You do not have permission to view this BCM data.')
        })
