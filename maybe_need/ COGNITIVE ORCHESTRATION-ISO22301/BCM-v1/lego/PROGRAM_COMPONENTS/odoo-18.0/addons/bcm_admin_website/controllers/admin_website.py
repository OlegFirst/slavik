# -*- coding: utf-8 -*-

import json
from odoo import http, fields
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.portal.controllers.portal import CustomerPortal


class BCMAdminWebsite(Website):
    """BCM Admin Website Controller - Full Management Interface"""

    @http.route('/bcm/admin', type='http', auth='user', website=True)
    def bcm_admin_dashboard(self, **kwargs):
        """Main BCM Admin Dashboard"""
        if not request.env.user.has_group('base.group_system'):
            return request.redirect('/web/login?redirect=/bcm/admin')

        # Get dashboard statistics
        stats = self._get_admin_stats()

        # Get recent activities
        activities = self._get_recent_activities()

        # Get system health
        health = self._get_system_health()

        values = {
            'page_name': 'bcm_admin_dashboard',
            'stats': stats,
            'activities': activities,
            'health': health,
            'user': request.env.user,
        }

        return request.render('bcm_portal.admin_dashboard_template', values)

    @http.route('/bcm/admin/modules', type='http', auth='user', website=True)
    def bcm_admin_modules(self, **kwargs):
        """BCM Modules Management"""
        if not request.env.user.has_group('base.group_system'):
            return request.redirect('/web/login?redirect=/bcm/admin')

        # Get all BCM modules
        modules = self._get_bcm_modules()

        values = {
            'page_name': 'bcm_admin_modules',
            'modules': modules,
            'user': request.env.user,
        }

        return request.render('bcm_portal.admin_modules_template', values)

    @http.route('/bcm/admin/module/<string:module_name>', type='http', auth='user', website=True)
    def bcm_admin_module_detail(self, module_name, **kwargs):
        """Individual BCM Module Management"""
        if not request.env.user.has_group('base.group_system'):
            return request.redirect('/web/login?redirect=/bcm/admin')

        module_info = self._get_module_info(module_name)
        module_data = self._get_module_data(module_name)

        values = {
            'page_name': f'bcm_admin_module_{module_name}',
            'module_name': module_name,
            'module_info': module_info,
            'module_data': module_data,
            'user': request.env.user,
        }

        return request.render('bcm_portal.admin_module_detail_template', values)

    @http.route('/bcm/admin/ai', type='http', auth='user', website=True)
    def bcm_admin_ai(self, **kwargs):
        """AI Organs Management"""
        if not request.env.user.has_group('base.group_system'):
            return request.redirect('/web/login?redirect=/bcm/admin')

        # Get AI organs status
        ai_organs = self._get_ai_organs_status()

        values = {
            'page_name': 'bcm_admin_ai',
            'ai_organs': ai_organs,
            'user': request.env.user,
        }

        return request.render('bcm_portal.admin_ai_template', values)

    @http.route('/bcm/admin/users', type='http', auth='user', website=True)
    def bcm_admin_users(self, **kwargs):
        """Users & Permissions Management"""
        if not request.env.user.has_group('base.group_system'):
            return request.redirect('/web/login?redirect=/bcm/admin')

        # Get users and groups
        users = request.env['res.users'].sudo().search([])
        groups = request.env['res.groups'].sudo().search([('name', 'ilike', 'BCM')])

        values = {
            'page_name': 'bcm_admin_users',
            'users': users,
            'groups': groups,
            'user': request.env.user,
        }

        return request.render('bcm_portal.admin_users_template', values)

    @http.route('/bcm/admin/reports', type='http', auth='user', website=True)
    def bcm_admin_reports(self, **kwargs):
        """Reports & Analytics Management"""
        if not request.env.user.has_group('base.group_system'):
            return request.redirect('/web/login?redirect=/bcm/admin')

        # Get reports data
        reports_data = self._get_reports_data()

        values = {
            'page_name': 'bcm_admin_reports',
            'reports_data': reports_data,
            'user': request.env.user,
        }

        return request.render('bcm_portal.admin_reports_template', values)

    @http.route('/bcm/admin/settings', type='http', auth='user', website=True)
    def bcm_admin_settings(self, **kwargs):
        """System Settings Management"""
        if not request.env.user.has_group('base.group_system'):
            return request.redirect('/web/login?redirect=/bcm/admin')

        # Get system settings
        settings = self._get_system_settings()

        values = {
            'page_name': 'bcm_admin_settings',
            'settings': settings,
            'user': request.env.user,
        }

        return request.render('bcm_portal.admin_settings_template', values)

    # API Endpoints for AJAX calls
    @http.route('/bcm/admin/api/module/<string:module_name>/data', type='json', auth='user')
    def get_module_data_api(self, module_name, **kwargs):
        """Get module data via API"""
        if not request.env.user.has_group('base.group_system'):
            return {'error': 'Access denied'}

        return self._get_module_data(module_name)

    @http.route('/bcm/admin/api/stats', type='json', auth='user')
    def get_admin_stats_api(self, **kwargs):
        """Get admin stats via API"""
        if not request.env.user.has_group('base.group_system'):
            return {'error': 'Access denied'}

        return self._get_admin_stats()

    @http.route('/bcm/admin/api/ai/status', type='json', auth='user')
    def get_ai_status_api(self, **kwargs):
        """Get AI organs status via API"""
        if not request.env.user.has_group('base.group_system'):
            return {'error': 'Access denied'}

        return self._get_ai_organs_status()

    # Helper methods
    def _get_admin_stats(self):
        """Get admin dashboard statistics"""
        env = request.env

        stats = {
            'total_users': env['res.users'].sudo().search_count([]),
            'active_sessions': len(env.registry._Registry__cache),
            'total_incidents': env['bcm.incident'].sudo().search_count([]),
            'open_incidents': env['bcm.incident'].sudo().search_count([('state', '=', 'open')]),
            'total_risks': env['bcm.risk.management'].sudo().search_count([]),
            'high_risks': env['bcm.risk.management'].sudo().search_count([('risk_level', '=', 'high')]),
            'total_plans': env['bcm.plans'].sudo().search_count([]),
            'active_plans': env['bcm.plans'].sudo().search_count([('state', '=', 'active')]),
            'total_trainings': env['bcm.training'].sudo().search_count([]),
            'completed_trainings': env['bcm.training'].sudo().search_count([('status', '=', 'completed')]),
            'total_exercises': env['bcm.exercise'].sudo().search_count([]),
            'pending_exercises': env['bcm.exercise'].sudo().search_count([('status', '=', 'planned')]),
        }

        return stats

    def _get_recent_activities(self):
        """Get recent system activities"""
        # This would get recent activities from various modules
        activities = [
            {
                'id': 1,
                'type': 'incident',
                'message': 'New critical incident reported',
                'user': 'John Doe',
                'date': fields.Datetime.now(),
                'icon': 'fa-exclamation-triangle',
                'color': 'danger'
            },
            {
                'id': 2,
                'type': 'training',
                'message': 'Training module completed by 15 users',
                'user': 'System',
                'date': fields.Datetime.now(),
                'icon': 'fa-graduation-cap',
                'color': 'success'
            },
            {
                'id': 3,
                'type': 'risk',
                'message': 'Risk assessment updated',
                'user': 'Jane Smith',
                'date': fields.Datetime.now(),
                'icon': 'fa-shield-alt',
                'color': 'warning'
            }
        ]

        return activities

    def _get_system_health(self):
        """Get system health status"""
        health = {
            'database': 'healthy',
            'redis': 'healthy',
            'ai_services': 'healthy',
            'storage': 'healthy',
            'memory_usage': 45,
            'cpu_usage': 32,
            'disk_usage': 68,
        }

        return health

    def _get_bcm_modules(self):
        """Get all BCM modules information"""
        bcm_modules = [
            {
                'name': 'bcm_core',
                'title': 'BCM Core',
                'description': 'Core BCM functionality and organization context',
                'icon': 'fa-shield-alt',
                'status': 'active',
                'records_count': request.env['bcm.core'].sudo().search_count([]) if 'bcm.core' in request.env else 0,
                'color': 'primary'
            },
            {
                'name': 'bcm_bia',
                'title': 'Business Impact Analysis',
                'description': 'Business impact analysis and critical functions',
                'icon': 'fa-chart-bar',
                'status': 'active',
                'records_count': request.env['bcm.bia'].sudo().search_count([]) if 'bcm.bia' in request.env else 0,
                'color': 'info'
            },
            {
                'name': 'bcm_risk_management',
                'title': 'Risk Management',
                'description': 'Risk assessment and mitigation strategies',
                'icon': 'fa-exclamation-triangle',
                'status': 'active',
                'records_count': request.env['bcm.risk.management'].sudo().search_count([]) if 'bcm.risk.management' in request.env else 0,
                'color': 'warning'
            },
            {
                'name': 'bcm_incident',
                'title': 'Incident Management',
                'description': 'Incident response and crisis management',
                'icon': 'fa-fire',
                'status': 'active',
                'records_count': request.env['bcm.incident'].sudo().search_count([]) if 'bcm.incident' in request.env else 0,
                'color': 'danger'
            },
            {
                'name': 'bcm_plans',
                'title': 'BCM Plans',
                'description': 'Business continuity and recovery plans',
                'icon': 'fa-file-alt',
                'status': 'active',
                'records_count': request.env['bcm.plans'].sudo().search_count([]) if 'bcm.plans' in request.env else 0,
                'color': 'success'
            },
            {
                'name': 'bcm_training',
                'title': 'Training Management',
                'description': 'Staff training and competency management',
                'icon': 'fa-graduation-cap',
                'status': 'active',
                'records_count': request.env['bcm.training'].sudo().search_count([]) if 'bcm.training' in request.env else 0,
                'color': 'info'
            },
            {
                'name': 'bcm_exercise',
                'title': 'Exercise Management',
                'description': 'BCM exercises and drills management',
                'icon': 'fa-play-circle',
                'status': 'active',
                'records_count': request.env['bcm.exercise'].sudo().search_count([]) if 'bcm.exercise' in request.env else 0,
                'color': 'secondary'
            },
            {
                'name': 'bcm_reporting',
                'title': 'Reporting & Analytics',
                'description': 'Reports, dashboards and compliance analytics',
                'icon': 'fa-chart-pie',
                'status': 'active',
                'records_count': request.env['bcm.reporting'].sudo().search_count([]) if 'bcm.reporting' in request.env else 0,
                'color': 'primary'
            },
            {
                'name': 'bcm_ai_control',
                'title': 'AI Control Center',
                'description': 'AI organs management and monitoring',
                'icon': 'fa-robot',
                'status': 'active',
                'records_count': 10,  # AI organs count
                'color': 'dark'
            },
            {
                'name': 'bcm_community',
                'title': 'Community & Knowledge',
                'description': 'Community forum and knowledge management',
                'icon': 'fa-users',
                'status': 'active',
                'records_count': request.env['bcm.community'].sudo().search_count([]) if 'bcm.community' in request.env else 0,
                'color': 'info'
            }
        ]

        return bcm_modules

    def _get_module_info(self, module_name):
        """Get specific module information"""
        module_map = {
            'bcm_core': {
                'title': 'BCM Core',
                'model': 'bcm.core',
                'description': 'Core BCM functionality and organization context',
                'fields': ['name', 'organization_id', 'context_type', 'description']
            },
            'bcm_bia': {
                'title': 'Business Impact Analysis',
                'model': 'bcm.bia',
                'description': 'Business impact analysis and critical functions',
                'fields': ['name', 'business_function', 'impact_level', 'rto', 'rpo']
            },
            'bcm_risk_management': {
                'title': 'Risk Management',
                'model': 'bcm.risk.management',
                'description': 'Risk assessment and mitigation strategies',
                'fields': ['name', 'risk_level', 'impact', 'probability', 'mitigation_strategy']
            },
            'bcm_incident': {
                'title': 'Incident Management',
                'model': 'bcm.incident',
                'description': 'Incident response and crisis management',
                'fields': ['name', 'severity', 'status', 'reported_date', 'resolved_date']
            },
            'bcm_plans': {
                'title': 'BCM Plans',
                'model': 'bcm.plans',
                'description': 'Business continuity and recovery plans',
                'fields': ['name', 'plan_type', 'status', 'last_review', 'next_review']
            }
        }

        return module_map.get(module_name, {})

    def _get_module_data(self, module_name):
        """Get module records data"""
        module_info = self._get_module_info(module_name)
        if not module_info or 'model' not in module_info:
            return []

        model_name = module_info['model']
        if model_name not in request.env:
            return []

        records = request.env[model_name].sudo().search([], limit=50)
        return [{
            'id': record.id,
            'name': record.name if hasattr(record, 'name') else f'Record {record.id}',
            'data': {field: getattr(record, field, '') for field in module_info.get('fields', [])}
        } for record in records]

    def _get_ai_organs_status(self):
        """Get AI organs status"""
        ai_organs = [
            {
                'name': 'Governance Brain',
                'type': 'strategic',
                'status': 'active',
                'health': 95,
                'last_activity': fields.Datetime.now(),
                'provider': 'Anthropic Claude',
                'icon': 'fa-brain'
            },
            {
                'name': 'Emergency Response',
                'type': 'operational',
                'status': 'active',
                'health': 92,
                'last_activity': fields.Datetime.now(),
                'provider': 'Local LLM',
                'icon': 'fa-ambulance'
            },
            {
                'name': 'Impact Oracle',
                'type': 'analytical',
                'status': 'active',
                'health': 88,
                'last_activity': fields.Datetime.now(),
                'provider': 'Local LLM',
                'icon': 'fa-crystal-ball'
            },
            {
                'name': 'Scenario Creator',
                'type': 'creative',
                'status': 'active',
                'health': 94,
                'last_activity': fields.Datetime.now(),
                'provider': 'Local LLM',
                'icon': 'fa-theater-masks'
            },
            {
                'name': 'Risk Advisor',
                'type': 'analytical',
                'status': 'active',
                'health': 91,
                'last_activity': fields.Datetime.now(),
                'provider': 'Local LLM',
                'icon': 'fa-shield-alt'
            }
        ]

        return ai_organs

    def _get_reports_data(self):
        """Get reports and analytics data"""
        return {
            'total_reports': 45,
            'generated_today': 3,
            'scheduled_reports': 12,
            'report_categories': [
                {'name': 'Compliance', 'count': 15},
                {'name': 'Performance', 'count': 18},
                {'name': 'Operational', 'count': 12}
            ]
        }

    def _get_system_settings(self):
        """Get system settings"""
        return {
            'ai_enabled': True,
            'notifications_enabled': True,
            'auto_backup': True,
            'maintenance_mode': False,
            'debug_mode': False,
            'max_users': 100,
            'current_users': 25,
            'storage_used': '2.3 GB',
            'storage_limit': '10 GB'
        }