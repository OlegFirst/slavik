# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json


class PersonalTwinPrivacyWizard(models.TransientModel):
    _name = 'bcm.personal.twin.privacy.wizard'
    _description = 'Personal Digital Twin Privacy Settings Wizard'

    twin_id = fields.Many2one(
        'bcm.personal.digital.twin',
        string='Digital Twin',
        required=True
    )

    # Profile Visibility
    profile_visibility = fields.Selection([
        ('private', 'Private - Only visible to me'),
        ('organization', 'Organization - Visible to organization members'),
        ('public', 'Public - Visible to all users')
    ], string='Profile Visibility', default='private', required=True)

    # Activity Tracking
    activity_tracking = fields.Boolean(
        string='Enable Activity Tracking',
        default=True,
        help="Allow the system to track your activities for insights"
    )

    analytics_consent = fields.Boolean(
        string='Analytics Consent',
        default=True,
        help="Consent to analytics data collection for improving services"
    )

    # Data Sharing Preferences
    data_share_organization = fields.Boolean(
        string='Share with Organization',
        default=True,
        help="Share anonymized data with your organization for insights"
    )

    data_share_platform = fields.Boolean(
        string='Share with Platform',
        default=False,
        help="Share anonymized data with the platform for improvements"
    )

    data_share_third_party = fields.Boolean(
        string='Share with Third Parties',
        default=False,
        help="Allow sharing anonymized data with third-party services"
    )

    # Data Retention Settings
    activity_logs_retention = fields.Integer(
        string='Activity Logs Retention (days)',
        default=365,
        help="Number of days to retain activity logs"
    )

    metrics_history_retention = fields.Integer(
        string='Metrics History Retention (days)',
        default=730,
        help="Number of days to retain metrics history"
    )

    patterns_analysis_retention = fields.Integer(
        string='Pattern Analysis Retention (days)',
        default=90,
        help="Number of days to retain pattern analysis data"
    )

    # Advanced Privacy Settings
    pseudonymization = fields.Boolean(
        string='Enable Pseudonymization',
        default=False,
        help="Replace personal identifiers with pseudonyms in analytics"
    )

    encrypt_sensitive_data = fields.Boolean(
        string='Encrypt Sensitive Data',
        default=True,
        help="Encrypt sensitive personal data at rest"
    )

    audit_access = fields.Boolean(
        string='Audit Data Access',
        default=True,
        help="Keep audit logs of who accesses your personal data"
    )

    # Notification Preferences for Privacy
    privacy_notifications = fields.Boolean(
        string='Privacy Notifications',
        default=True,
        help="Receive notifications about privacy policy changes"
    )

    data_breach_notifications = fields.Boolean(
        string='Data Breach Notifications',
        default=True,
        help="Receive immediate notifications about data breaches"
    )

    @api.model
    def default_get(self, fields_list):
        """Load current privacy settings from the digital twin"""
        res = super().default_get(fields_list)

        twin_id = self.env.context.get('default_twin_id')
        if twin_id:
            twin = self.env['bcm.personal.digital.twin'].browse(twin_id)
            if twin.privacy_settings:
                settings = twin.privacy_settings

                # Map settings to wizard fields
                res.update({
                    'twin_id': twin_id,
                    'profile_visibility': settings.get('profile_visibility', 'private'),
                    'activity_tracking': settings.get('activity_tracking', True),
                    'analytics_consent': settings.get('analytics_consent', True),
                    'data_share_organization': settings.get('data_sharing', {}).get('organization', True),
                    'data_share_platform': settings.get('data_sharing', {}).get('platform', False),
                    'data_share_third_party': settings.get('data_sharing', {}).get('third_party', False),
                    'activity_logs_retention': settings.get('retention_policy', {}).get('activity_logs', 365),
                    'metrics_history_retention': settings.get('retention_policy', {}).get('metrics_history', 730),
                    'patterns_analysis_retention': settings.get('retention_policy', {}).get('patterns_analysis', 90),
                    'pseudonymization': settings.get('advanced', {}).get('pseudonymization', False),
                    'encrypt_sensitive_data': settings.get('advanced', {}).get('encrypt_sensitive_data', True),
                    'audit_access': settings.get('advanced', {}).get('audit_access', True),
                    'privacy_notifications': settings.get('notifications', {}).get('privacy_notifications', True),
                    'data_breach_notifications': settings.get('notifications', {}).get('data_breach_notifications', True),
                })

        return res

    @api.constrains('activity_logs_retention', 'metrics_history_retention', 'patterns_analysis_retention')
    def _check_retention_periods(self):
        """Validate retention periods"""
        for record in self:
            if record.activity_logs_retention < 1 or record.activity_logs_retention > 3650:
                raise UserError(_("Activity logs retention must be between 1 and 3650 days"))
            if record.metrics_history_retention < 1 or record.metrics_history_retention > 3650:
                raise UserError(_("Metrics history retention must be between 1 and 3650 days"))
            if record.patterns_analysis_retention < 1 or record.patterns_analysis_retention > 365:
                raise UserError(_("Pattern analysis retention must be between 1 and 365 days"))

    def action_save_privacy_settings(self):
        """Save privacy settings to the digital twin"""
        self.ensure_one()

        if not self.twin_id:
            raise UserError(_("No digital twin specified"))

        # Build privacy settings dictionary
        privacy_settings = {
            'profile_visibility': self.profile_visibility,
            'activity_tracking': self.activity_tracking,
            'analytics_consent': self.analytics_consent,
            'data_sharing': {
                'organization': self.data_share_organization,
                'platform': self.data_share_platform,
                'third_party': self.data_share_third_party
            },
            'retention_policy': {
                'activity_logs': self.activity_logs_retention,
                'metrics_history': self.metrics_history_retention,
                'patterns_analysis': self.patterns_analysis_retention
            },
            'advanced': {
                'pseudonymization': self.pseudonymization,
                'encrypt_sensitive_data': self.encrypt_sensitive_data,
                'audit_access': self.audit_access
            },
            'notifications': {
                'privacy_notifications': self.privacy_notifications,
                'data_breach_notifications': self.data_breach_notifications
            },
            'last_updated': fields.Datetime.to_string(fields.Datetime.now()),
            'updated_by': self.env.user.id
        }

        # Update the digital twin
        self.twin_id.privacy_settings = privacy_settings

        # Update is_public field based on profile visibility
        self.twin_id.is_public = (self.profile_visibility == 'public')

        # If analytics consent is revoked, stop AI insights
        if not self.analytics_consent:
            self.twin_id.ai_insights_enabled = False

        # Log the privacy settings change
        self.twin_id.message_post(
            body=_("Privacy settings updated"),
            message_type='notification'
        )

        # Create audit log for privacy changes
        self._create_privacy_audit_log()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Privacy settings saved successfully"),
                'type': 'success'
            }
        }

    def action_delete_personal_data(self):
        """Delete personal data (GDPR right to be forgotten)"""
        self.ensure_one()

        return {
            'name': _('Delete Personal Data'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.personal.twin.data.deletion.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_twin_id': self.twin_id.id
            }
        }

    def action_export_personal_data(self):
        """Export personal data (GDPR right to data portability)"""
        self.ensure_one()

        return {
            'name': _('Export Personal Data'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.personal.twin.data.export.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_twin_id': self.twin_id.id
            }
        }

    def action_reset_to_strict(self):
        """Reset to most strict privacy settings"""
        self.ensure_one()

        self.write({
            'profile_visibility': 'private',
            'activity_tracking': False,
            'analytics_consent': False,
            'data_share_organization': False,
            'data_share_platform': False,
            'data_share_third_party': False,
            'activity_logs_retention': 30,  # Minimum required
            'metrics_history_retention': 30,
            'patterns_analysis_retention': 30,
            'pseudonymization': True,
            'encrypt_sensitive_data': True,
            'audit_access': True,
            'privacy_notifications': True,
            'data_breach_notifications': True,
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Privacy Settings"),
                'message': _("Reset to most strict privacy settings"),
                'type': 'info'
            }
        }

    def _create_privacy_audit_log(self):
        """Create audit log for privacy settings changes"""
        audit_data = {
            'user_id': self.env.user.id,
            'twin_id': self.twin_id.id,
            'timestamp': fields.Datetime.now(),
            'action': 'privacy_settings_updated',
            'settings_snapshot': self.twin_id.privacy_settings,
            'ip_address': self.env.context.get('client_ip', 'unknown')
        }

        # In a real implementation, this would create an audit log record
        # For now, just log to the twin's message thread
        self.twin_id.message_post(
            body=_("Privacy settings audit log: %s") % json.dumps(audit_data, default=str),
            message_type='comment',
            subtype_id=self.env.ref('mail.mt_note').id
        )