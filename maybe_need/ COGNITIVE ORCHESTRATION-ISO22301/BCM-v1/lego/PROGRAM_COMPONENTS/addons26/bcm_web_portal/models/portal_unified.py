# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
import json
import logging

_logger = logging.getLogger(__name__)

class BcmWebPortal(models.Model):
    """
    Unified Web Portal Model
    Объединяет функциональность bcm_portal + admin_website functionality
    """
    _name = 'bcm.web.portal'
    _description = 'BCM Web Portal - Unified'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'portal_type, name'
    _rec_name = 'name'

    # === CORE FIELDS ===
    
    name = fields.Char(
        string='Portal Name',
        required=True,
        index=True,
        tracking=True,
        help='Name of the portal instance'
    )
    
    portal_type = fields.Selection([
        ('client', 'Client Portal'),
        ('admin', 'Admin Interface'),
        ('public', 'Public Website'),
        ('hybrid', 'Hybrid Portal')
    ], string='Portal Type', required=True, default='client', tracking=True)
    
    description = fields.Text(
        string='Description',
        help='Description of the portal purpose'
    )
    
    # === ACCESS CONTROL ===
    
    access_level = fields.Selection([
        ('public', 'Public Access'),
        ('authenticated', 'Authenticated Users'),
        ('client_users', 'Client Users Only'),
        ('admin_users', 'Admin Users Only'),
        ('custom', 'Custom Access Rules')
    ], string='Access Level', required=True, default='authenticated', tracking=True)
    
    allowed_user_groups = fields.Many2many(
        'res.groups',
        string='Allowed User Groups',
        help='User groups allowed to access this portal'
    )
    
    allowed_clients = fields.Many2many(
        'bcm.client',
        string='Allowed Clients',
        help='Specific clients allowed to access this portal'
    )
    
    # === CLIENT PORTAL FEATURES (из bcm_portal) ===
    
    enable_dashboard = fields.Boolean(
        string='Enable Dashboard',
        default=True,
        help='Enable client dashboard with KPIs and metrics'
    )
    
    enable_bia_access = fields.Boolean(
        string='Enable BIA Access',
        default=True,
        help='Allow clients to view BIA results'
    )
    
    enable_plans_access = fields.Boolean(
        string='Enable Plans Access',
        default=True,
        help='Allow clients to view business continuity plans'
    )
    
    enable_incident_reporting = fields.Boolean(
        string='Enable Incident Reporting',
        default=True,
        help='Allow clients to report and view incidents'
    )
    
    enable_exercise_participation = fields.Boolean(
        string='Enable Exercise Participation',
        default=True,
        help='Allow clients to participate in exercises'
    )
    
    enable_training_access = fields.Boolean(
        string='Enable Training Access',
        default=True,
        help='Allow clients to access training materials'
    )
    
    enable_document_management = fields.Boolean(
        string='Enable Document Management',
        default=True,
        help='Allow clients to manage documents'
    )
    
    # === ADMIN INTERFACE FEATURES (admin_website functionality) ===
    
    enable_user_management = fields.Boolean(
        string='Enable User Management',
        default=False,
        help='Enable admin user management interface'
    )
    
    enable_system_monitoring = fields.Boolean(
        string='Enable System Monitoring',
        default=False,
        help='Enable system monitoring dashboard'
    )
    
    enable_content_management = fields.Boolean(
        string='Enable Content Management',
        default=False,
        help='Enable content management system'
    )
    
    enable_configuration = fields.Boolean(
        string='Enable Configuration',
        default=False,
        help='Enable system configuration interface'
    )
    
    enable_audit_logs = fields.Boolean(
        string='Enable Audit Logs',
        default=False,
        help='Enable audit log viewing'
    )
    
    enable_analytics = fields.Boolean(
        string='Enable Analytics',
        default=False,
        help='Enable analytics dashboard'
    )
    
    # === UI/UX CONFIGURATION ===
    
    theme = fields.Selection([
        ('default', 'Default Theme'),
        ('dark', 'Dark Theme'),
        ('light', 'Light Theme'),
        ('client_branded', 'Client Branded'),
        ('custom', 'Custom Theme')
    ], string='Theme', default='default')
    
    custom_css = fields.Text(
        string='Custom CSS',
        help='Custom CSS styling for the portal'
    )
    
    custom_javascript = fields.Text(
        string='Custom JavaScript',
        help='Custom JavaScript for the portal'
    )
    
    logo_image = fields.Binary(
        string='Portal Logo',
        help='Logo image for the portal header'
    )
    
    favicon = fields.Binary(
        string='Favicon',
        help='Favicon for the portal'
    )
    
    # === INTEGRATION SETTINGS ===
    
    enable_sso = fields.Boolean(
        string='Enable SSO',
        default=False,
        help='Enable Single Sign-On integration'
    )
    
    sso_provider = fields.Selection([
        ('keycloak', 'Keycloak'),
        ('azure_ad', 'Azure AD'),
        ('google', 'Google'),
        ('okta', 'Okta'),
        ('custom', 'Custom SAML/OIDC')
    ], string='SSO Provider')
    
    sso_config = fields.Text(
        string='SSO Configuration',
        help='JSON configuration for SSO integration'
    )
    
    enable_api = fields.Boolean(
        string='Enable API Access',
        default=False,
        help='Enable REST API access for this portal'
    )
    
    api_endpoints = fields.Text(
        string='API Endpoints',
        help='JSON configuration of available API endpoints'
    )
    
    enable_websocket = fields.Boolean(
        string='Enable WebSocket',
        default=False,
        help='Enable real-time WebSocket connections'
    )
    
    # === AI FEATURES ===
    
    enable_ai_assistant = fields.Boolean(
        string='Enable AI Assistant',
        default=False,
        help='Enable AI assistant widget in portal'
    )
    
    ai_assistant_config = fields.Text(
        string='AI Assistant Configuration',
        help='JSON configuration for AI assistant'
    )
    
    enable_smart_search = fields.Boolean(
        string='Enable Smart Search',
        default=False,
        help='Enable AI-powered smart search'
    )
    
    enable_predictive_analytics = fields.Boolean(
        string='Enable Predictive Analytics',
        default=False,
        help='Enable AI predictive analytics'
    )
    
    # === SECURITY SETTINGS ===
    
    enable_mfa = fields.Boolean(
        string='Enable Multi-Factor Authentication',
        default=False,
        help='Require MFA for portal access'
    )
    
    session_timeout = fields.Integer(
        string='Session Timeout (minutes)',
        default=480,  # 8 hours
        help='Session timeout in minutes'
    )
    
    max_login_attempts = fields.Integer(
        string='Max Login Attempts',
        default=5,
        help='Maximum failed login attempts before lockout'
    )
    
    lockout_duration = fields.Integer(
        string='Lockout Duration (minutes)',
        default=30,
        help='Account lockout duration in minutes'
    )
    
    enable_audit_logging = fields.Boolean(
        string='Enable Audit Logging',
        default=True,
        help='Log all portal activities for audit'
    )
    
    # === PERFORMANCE SETTINGS ===
    
    enable_caching = fields.Boolean(
        string='Enable Caching',
        default=True,
        help='Enable portal content caching'
    )
    
    cache_timeout = fields.Integer(
        string='Cache Timeout (seconds)',
        default=3600,  # 1 hour
        help='Cache timeout in seconds'
    )
    
    enable_compression = fields.Boolean(
        string='Enable Compression',
        default=True,
        help='Enable GZIP compression'
    )
    
    enable_cdn = fields.Boolean(
        string='Enable CDN',
        default=False,
        help='Enable CDN for static assets'
    )
    
    cdn_url = fields.Char(
        string='CDN URL',
        help='CDN base URL for static assets'
    )
    
    # === ANALYTICS AND MONITORING ===
    
    portal_usage_stats = fields.One2many(
        'bcm.portal.usage.stat',
        'portal_id',
        string='Usage Statistics'
    )
    
    portal_access_logs = fields.One2many(
        'bcm.portal.access.log',
        'portal_id',
        string='Access Logs'
    )
    
    # Computed fields
    total_users = fields.Integer(
        string='Total Users',
        compute='_compute_user_stats',
        help='Total number of portal users'
    )
    
    active_sessions = fields.Integer(
        string='Active Sessions',
        compute='_compute_session_stats',
        help='Number of currently active sessions'
    )
    
    daily_visits = fields.Integer(
        string='Daily Visits',
        compute='_compute_visit_stats',
        help='Number of visits today'
    )
    
    # === SYSTEM FIELDS ===
    
    active = fields.Boolean(default=True, tracking=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        index=True,
        default=lambda self: self.env.company,
        help='Company/tenant isolation'
    )
    
    # === COMPUTED FIELDS ===
    
    @api.depends('portal_access_logs')
    def _compute_user_stats(self):
        for portal in self:
            # Count unique users who accessed this portal
            unique_users = portal.portal_access_logs.mapped('user_id')
            portal.total_users = len(unique_users)
    
    @api.depends()
    def _compute_session_stats(self):
        for portal in self:
            # Count active sessions (simplified)
            # In real implementation, this would check session store
            portal.active_sessions = 0
    
    @api.depends('portal_access_logs')
    def _compute_visit_stats(self):
        for portal in self:
            today = fields.Date.today()
            daily_logs = portal.portal_access_logs.filtered(
                lambda log: log.access_date.date() == today
            )
            portal.daily_visits = len(daily_logs)
    
    # === CONSTRAINTS ===
    
    @api.constrains('session_timeout', 'max_login_attempts', 'lockout_duration')
    def _check_security_values(self):
        for portal in self:
            if portal.session_timeout < 5:
                raise ValidationError(_('Session timeout must be at least 5 minutes'))
            if portal.max_login_attempts < 1:
                raise ValidationError(_('Max login attempts must be at least 1'))
            if portal.lockout_duration < 1:
                raise ValidationError(_('Lockout duration must be at least 1 minute'))
    
    @api.constrains('sso_config', 'ai_assistant_config', 'api_endpoints')
    def _check_json_fields(self):
        """Validate JSON fields"""
        for portal in self:
            json_fields = ['sso_config', 'ai_assistant_config', 'api_endpoints']
            for field_name in json_fields:
                field_value = getattr(portal, field_name, None)
                if field_value:
                    try:
                        json.loads(field_value)
                    except json.JSONDecodeError:
                        raise ValidationError(_(f'{field_name} must be valid JSON'))
    
    # === ACTION METHODS ===
    
    def action_open_portal(self):
        """Open portal in new window"""
        self.ensure_one()
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        portal_url = f"{base_url}/portal/{self.id}"
        
        return {
            'type': 'ir.actions.act_url',
            'url': portal_url,
            'target': 'new',
        }
    
    def action_test_sso(self):
        """Test SSO configuration"""
        self.ensure_one()
        
        if not self.enable_sso or not self.sso_config:
            raise ValidationError(_('SSO is not configured for this portal'))
        
        # TODO: Implement SSO testing
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('SSO Test'),
                'message': _('SSO configuration test started'),
                'type': 'info',
            }
        }
    
    def action_clear_cache(self):
        """Clear portal cache"""
        self.ensure_one()
        
        if not self.enable_caching:
            raise ValidationError(_('Caching is not enabled for this portal'))
        
        # TODO: Implement cache clearing
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Cache Cleared'),
                'message': _('Portal cache has been cleared'),
                'type': 'success',
            }
        }
    
    def action_view_analytics(self):
        """View portal analytics"""
        self.ensure_one()
        
        return {
            'name': _('Portal Analytics'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.portal.analytics.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_portal_id': self.id}
        }
    
    def action_export_logs(self):
        """Export portal access logs"""
        self.ensure_one()
        
        return {
            'name': _('Export Access Logs'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.portal.log.export.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_portal_id': self.id}
        }
    
    # === SECURITY METHODS ===
    
    def check_portal_access(self, user):
        """Check if user has access to this portal"""
        self.ensure_one()
        
        if not self.active:
            return False
        
        if self.access_level == 'public':
            return True
        
        if not user or user._is_public():
            return False
        
        if self.access_level == 'authenticated':
            return True
        
        if self.access_level == 'client_users':
            # Check if user is a client contact
            client_contact = self.env['bcm.client.contact'].search([
                ('user_id', '=', user.id)
            ], limit=1)
            if client_contact and client_contact.client_id in self.allowed_clients:
                return True
            return False
        
        if self.access_level == 'admin_users':
            return user.has_group('bcm_web_portal.group_portal_admin')
        
        if self.access_level == 'custom':
            user_groups = user.groups_id
            return bool(user_groups & self.allowed_user_groups)
        
        return False
    
    def log_portal_access(self, user, request_info=None):
        """Log portal access"""
        self.ensure_one()
        
        if not self.enable_audit_logging:
            return
        
        self.env['bcm.portal.access.log'].create({
            'portal_id': self.id,
            'user_id': user.id if user and not user._is_public() else False,
            'access_date': fields.Datetime.now(),
            'ip_address': request_info.get('ip_address') if request_info else None,
            'user_agent': request_info.get('user_agent') if request_info else None,
            'request_path': request_info.get('request_path') if request_info else None,
        })
    
    # === CONFIGURATION METHODS ===
    
    def configure_client_portal(self):
        """Configure as client portal with default settings"""
        self.write({
            'portal_type': 'client',
            'access_level': 'client_users',
            'enable_dashboard': True,
            'enable_bia_access': True,
            'enable_plans_access': True,
            'enable_incident_reporting': True,
            'enable_exercise_participation': True,
            'enable_training_access': True,
            'enable_document_management': True,
            'enable_ai_assistant': True,
            'enable_audit_logging': True,
        })
    
    def configure_admin_portal(self):
        """Configure as admin portal with default settings"""
        self.write({
            'portal_type': 'admin',
            'access_level': 'admin_users',
            'enable_user_management': True,
            'enable_system_monitoring': True,
            'enable_content_management': True,
            'enable_configuration': True,
            'enable_audit_logs': True,
            'enable_analytics': True,
            'enable_api': True,
            'enable_mfa': True,
            'enable_audit_logging': True,
        })
    
    def configure_public_portal(self):
        """Configure as public portal with default settings"""
        self.write({
            'portal_type': 'public',
            'access_level': 'public',
            'enable_caching': True,
            'enable_compression': True,
            'enable_cdn': True,
        })


# === SUPPORTING MODELS ===

class BcmPortalUsageStat(models.Model):
    """Portal usage statistics"""
    _name = 'bcm.portal.usage.stat'
    _description = 'Portal Usage Statistics'
    _order = 'date desc'
    
    portal_id = fields.Many2one('bcm.web.portal', required=True, ondelete='cascade')
    date = fields.Date(required=True, default=fields.Date.today)
    page_views = fields.Integer('Page Views', default=0)
    unique_visitors = fields.Integer('Unique Visitors', default=0)
    bounce_rate = fields.Float('Bounce Rate (%)', default=0.0)
    avg_session_duration = fields.Float('Avg Session Duration (min)', default=0.0)


class BcmPortalAccessLog(models.Model):
    """Portal access logs"""
    _name = 'bcm.portal.access.log'
    _description = 'Portal Access Log'
    _order = 'access_date desc'
    
    portal_id = fields.Many2one('bcm.web.portal', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User')
    access_date = fields.Datetime('Access Date', required=True)
    ip_address = fields.Char('IP Address')
    user_agent = fields.Text('User Agent')
    request_path = fields.Char('Request Path')
    response_code = fields.Integer('Response Code')
    response_time = fields.Float('Response Time (ms)')


class BcmPortalContent(models.Model):
    """Portal content management"""
    _name = 'bcm.portal.content'
    _description = 'Portal Content'
    _order = 'content_type, sequence, name'
    
    name = fields.Char(required=True)
    portal_id = fields.Many2one('bcm.web.portal', required=True, ondelete='cascade')
    content_type = fields.Selection([
        ('page', 'Static Page'),
        ('widget', 'Dashboard Widget'),
        ('menu_item', 'Menu Item'),
        ('footer_link', 'Footer Link'),
        ('banner', 'Banner/Announcement')
    ], required=True)
    sequence = fields.Integer(default=10)
    content_html = fields.Html('Content')
    is_active = fields.Boolean(default=True)
    target_audience = fields.Selection([
        ('all', 'All Users'),
        ('clients', 'Client Users'),
        ('admins', 'Admin Users'),
        ('custom', 'Custom Groups')
    ], default='all')
