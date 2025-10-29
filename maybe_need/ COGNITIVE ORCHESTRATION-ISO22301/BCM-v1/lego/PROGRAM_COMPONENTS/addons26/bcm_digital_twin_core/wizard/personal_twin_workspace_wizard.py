# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json


class PersonalTwinWorkspaceWizard(models.TransientModel):
    _name = 'bcm.personal.twin.workspace.wizard'
    _description = 'Personal Digital Twin Workspace Configuration Wizard'

    twin_id = fields.Many2one(
        'bcm.personal.digital.twin',
        string='Digital Twin',
        required=True
    )

    # Workspace Configuration Fields
    theme = fields.Selection([
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
        ('auto', 'Auto (System Preference)')
    ], string='Theme', default='light')

    language = fields.Selection(
        string='Language',
        selection='_get_language_selection',
        default='en_US'
    )

    timezone = fields.Selection(
        string='Timezone',
        selection='_get_timezone_selection',
        default='UTC'
    )

    dashboard_layout = fields.Selection([
        ('default', 'Default Layout'),
        ('compact', 'Compact Layout'),
        ('detailed', 'Detailed Layout'),
        ('custom', 'Custom Layout')
    ], string='Dashboard Layout', default='default')

    # Notification Settings
    email_notifications = fields.Boolean(
        string='Email Notifications',
        default=True
    )

    browser_notifications = fields.Boolean(
        string='Browser Notifications',
        default=True
    )

    mobile_notifications = fields.Boolean(
        string='Mobile Push Notifications',
        default=False
    )

    # Widget Settings
    activity_feed_widget = fields.Boolean(
        string='Activity Feed Widget',
        default=True
    )

    kpi_overview_widget = fields.Boolean(
        string='KPI Overview Widget',
        default=True
    )

    quick_actions_widget = fields.Boolean(
        string='Quick Actions Widget',
        default=True
    )

    recent_documents_widget = fields.Boolean(
        string='Recent Documents Widget',
        default=True
    )

    # Preferences
    auto_save = fields.Boolean(
        string='Auto Save',
        default=True,
        help="Automatically save changes without confirmation"
    )

    compact_view = fields.Boolean(
        string='Compact View',
        default=False,
        help="Use compact view for tables and lists"
    )

    show_hints = fields.Boolean(
        string='Show Hints',
        default=True,
        help="Show helpful hints and tooltips"
    )

    def _get_language_selection(self):
        """Get available languages"""
        langs = self.env['res.lang'].search([('active', '=', True)])
        return [(lang.code, lang.name) for lang in langs]

    def _get_timezone_selection(self):
        """Get available timezones"""
        # This is a simplified list - in production, you'd want a more comprehensive list
        return [
            ('UTC', 'UTC'),
            ('America/New_York', 'Eastern Time (US & Canada)'),
            ('America/Chicago', 'Central Time (US & Canada)'),
            ('America/Denver', 'Mountain Time (US & Canada)'),
            ('America/Los_Angeles', 'Pacific Time (US & Canada)'),
            ('Europe/London', 'London'),
            ('Europe/Paris', 'Paris'),
            ('Europe/Berlin', 'Berlin'),
            ('Asia/Tokyo', 'Tokyo'),
            ('Asia/Shanghai', 'Shanghai'),
            ('Australia/Sydney', 'Sydney')
        ]

    @api.model
    def default_get(self, fields_list):
        """Load current configuration from the digital twin"""
        res = super().default_get(fields_list)

        twin_id = self.env.context.get('default_twin_id')
        if twin_id:
            twin = self.env['bcm.personal.digital.twin'].browse(twin_id)
            if twin.workspace_config:
                config = twin.workspace_config

                # Map configuration to wizard fields
                res.update({
                    'twin_id': twin_id,
                    'theme': config.get('theme', 'light'),
                    'language': config.get('language', 'en_US'),
                    'timezone': config.get('timezone', 'UTC'),
                    'dashboard_layout': config.get('dashboard_layout', 'default'),
                    'email_notifications': config.get('notifications', {}).get('email', True),
                    'browser_notifications': config.get('notifications', {}).get('browser', True),
                    'mobile_notifications': config.get('notifications', {}).get('mobile', False),
                    'activity_feed_widget': config.get('widgets', {}).get('activity_feed', True),
                    'kpi_overview_widget': config.get('widgets', {}).get('kpi_overview', True),
                    'quick_actions_widget': config.get('widgets', {}).get('quick_actions', True),
                    'recent_documents_widget': config.get('widgets', {}).get('recent_documents', True),
                    'auto_save': config.get('preferences', {}).get('auto_save', True),
                    'compact_view': config.get('preferences', {}).get('compact_view', False),
                    'show_hints': config.get('preferences', {}).get('show_hints', True),
                })

        return res

    def action_save_configuration(self):
        """Save the workspace configuration to the digital twin"""
        self.ensure_one()

        if not self.twin_id:
            raise UserError(_("No digital twin specified"))

        # Build configuration dictionary
        config = {
            'theme': self.theme,
            'language': self.language,
            'timezone': self.timezone,
            'dashboard_layout': self.dashboard_layout,
            'notifications': {
                'email': self.email_notifications,
                'browser': self.browser_notifications,
                'mobile': self.mobile_notifications
            },
            'widgets': {
                'activity_feed': self.activity_feed_widget,
                'kpi_overview': self.kpi_overview_widget,
                'quick_actions': self.quick_actions_widget,
                'recent_documents': self.recent_documents_widget
            },
            'preferences': {
                'auto_save': self.auto_save,
                'compact_view': self.compact_view,
                'show_hints': self.show_hints
            },
            'last_updated': fields.Datetime.to_string(fields.Datetime.now())
        }

        # Update the digital twin
        self.twin_id.workspace_config = config

        # Log the change
        self.twin_id.message_post(
            body=_("Workspace configuration updated"),
            message_type='notification'
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Workspace configuration saved successfully"),
                'type': 'success'
            }
        }

    def action_reset_to_default(self):
        """Reset configuration to default values"""
        self.ensure_one()

        default_config = self.twin_id._default_workspace_config()

        # Update wizard fields with defaults
        self.write({
            'theme': default_config.get('theme', 'light'),
            'language': default_config.get('language', 'en_US'),
            'timezone': default_config.get('timezone', 'UTC'),
            'dashboard_layout': default_config.get('dashboard_layout', 'default'),
            'email_notifications': default_config.get('notifications', {}).get('email', True),
            'browser_notifications': default_config.get('notifications', {}).get('browser', True),
            'mobile_notifications': default_config.get('notifications', {}).get('mobile', False),
            'activity_feed_widget': default_config.get('widgets', {}).get('activity_feed', True),
            'kpi_overview_widget': default_config.get('widgets', {}).get('kpi_overview', True),
            'quick_actions_widget': default_config.get('widgets', {}).get('quick_actions', True),
            'recent_documents_widget': default_config.get('widgets', {}).get('recent_documents', True),
            'auto_save': default_config.get('preferences', {}).get('auto_save', True),
            'compact_view': default_config.get('preferences', {}).get('compact_view', False),
            'show_hints': default_config.get('preferences', {}).get('show_hints', True),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Reset"),
                'message': _("Configuration reset to default values"),
                'type': 'info'
            }
        }