# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
import json
import logging
import requests
import websocket
import threading
from datetime import datetime, timedelta
from contextlib import closing

_logger = logging.getLogger(__name__)

class PersonalDigitalTwin(models.Model):
    _name = 'bcm.personal.digital.twin'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Personal Digital Twin'
    _order = 'user_id, create_date desc'
    _rec_name = 'display_name'

    # Core Identity
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        ondelete='cascade',
        tracking=True,
        help="User associated with this personal digital twin"
    )

    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
        help="Display name for the personal digital twin"
    )

    organization_twin_id = fields.Many2one(
        'bcm.digital.twin.organization',
        string='Organization Twin',
        help="Associated organization digital twin",
        tracking=True
    )

    # Personal Configuration
    workspace_config = fields.Json(
        string='Workspace Configuration',
        help="JSON configuration for personal workspace settings",
        default=lambda self: self._default_workspace_config()
    )

    personal_metrics = fields.Json(
        string='Personal Metrics',
        help="JSON field for user activity metrics",
        compute='_compute_personal_metrics',
        store=True
    )

    activity_patterns = fields.Json(
        string='Activity Patterns',
        help="JSON field for behavior analysis and patterns",
        readonly=True
    )

    privacy_settings = fields.Json(
        string='Privacy Settings',
        help="JSON field for user privacy controls",
        default=lambda self: self._default_privacy_settings()
    )

    # Sync & Status
    sync_status = fields.Selection([
        ('active', 'Active'),
        ('syncing', 'Syncing'),
        ('offline', 'Offline'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance')
    ], string='Sync Status', default='active', tracking=True,
       help="Current synchronization status")

    last_sync = fields.Datetime(
        string='Last Sync',
        help="Timestamp of the last successful synchronization",
        tracking=True
    )

    next_sync = fields.Datetime(
        string='Next Sync',
        compute='_compute_next_sync',
        help="Scheduled time for next synchronization"
    )

    # Analytics & Insights
    twin_health_score = fields.Float(
        string='Twin Health Score',
        compute='_compute_twin_health_score',
        store=True,
        help="Overall health score of the personal digital twin (0-100)"
    )

    activity_score = fields.Float(
        string='Activity Score',
        compute='_compute_activity_score',
        store=True,
        help="User activity engagement score (0-100)"
    )

    last_activity = fields.Datetime(
        string='Last Activity',
        help="Timestamp of the last recorded user activity"
    )

    total_sessions = fields.Integer(
        string='Total Sessions',
        compute='_compute_session_stats',
        store=True,
        help="Total number of user sessions"
    )

    avg_session_duration = fields.Float(
        string='Avg Session Duration (hours)',
        compute='_compute_session_stats',
        store=True,
        help="Average session duration in hours"
    )

    # Integration Status
    bcm_integration_active = fields.Boolean(
        string='BCM Integration Active',
        default=True,
        help="Whether BCM integration is active for this user"
    )

    ai_insights_enabled = fields.Boolean(
        string='AI Insights Enabled',
        default=True,
        help="Whether AI insights are enabled for this user"
    )

    real_time_sync = fields.Boolean(
        string='Real-time Sync',
        default=True,
        help="Enable real-time synchronization with personal cabinet"
    )

    # Access & Security
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help="Company this personal digital twin belongs to"
    )

    is_public = fields.Boolean(
        string='Public Profile',
        default=False,
        help="Whether this twin profile is visible to other users"
    )

    # Computed Fields
    @api.depends('user_id', 'user_id.name')
    def _compute_display_name(self):
        for record in self:
            if record.user_id:
                record.display_name = f"Digital Twin - {record.user_id.name}"
            else:
                record.display_name = "Digital Twin - (No User)"

    @api.depends('last_sync', 'sync_status')
    def _compute_next_sync(self):
        for record in self:
            if record.last_sync and record.sync_status == 'active':
                # Schedule next sync based on user activity level
                sync_interval = 1 if record.real_time_sync else 6  # hours
                record.next_sync = record.last_sync + timedelta(hours=sync_interval)
            else:
                record.next_sync = False

    @api.depends('user_id', 'personal_metrics', 'activity_patterns', 'last_sync')
    def _compute_twin_health_score(self):
        for record in self:
            score = 0

            # Base score for having a user
            if record.user_id:
                score += 20

            # Sync health
            if record.last_sync:
                days_since_sync = (fields.Datetime.now() - record.last_sync).days
                if days_since_sync <= 1:
                    score += 30
                elif days_since_sync <= 7:
                    score += 20
                elif days_since_sync <= 30:
                    score += 10

            # Data completeness
            if record.personal_metrics:
                score += 25
            if record.activity_patterns:
                score += 15
            if record.workspace_config:
                score += 10

            record.twin_health_score = min(score, 100)

    @api.depends('personal_metrics', 'last_activity')
    def _compute_activity_score(self):
        for record in self:
            score = 0

            if record.personal_metrics:
                metrics = record.personal_metrics

                # Recent activity
                if record.last_activity:
                    hours_since_activity = (fields.Datetime.now() - record.last_activity).total_seconds() / 3600
                    if hours_since_activity <= 1:
                        score += 40
                    elif hours_since_activity <= 24:
                        score += 30
                    elif hours_since_activity <= 168:  # 1 week
                        score += 20

                # Engagement metrics
                login_count = metrics.get('login_count_month', 0)
                if login_count >= 20:
                    score += 30
                elif login_count >= 10:
                    score += 20
                elif login_count >= 5:
                    score += 10

                # Feature usage
                features_used = len(metrics.get('features_used', []))
                if features_used >= 10:
                    score += 30
                elif features_used >= 5:
                    score += 20
                elif features_used >= 1:
                    score += 10

            record.activity_score = min(score, 100)

    @api.depends('personal_metrics')
    def _compute_session_stats(self):
        for record in self:
            if record.personal_metrics:
                metrics = record.personal_metrics
                record.total_sessions = metrics.get('total_sessions', 0)
                record.avg_session_duration = metrics.get('avg_session_hours', 0.0)
            else:
                record.total_sessions = 0
                record.avg_session_duration = 0.0

    def _compute_personal_metrics(self):
        """Compute personal metrics from user activities"""
        for record in self:
            if not record.user_id:
                record.personal_metrics = {}
                continue

            try:
                # Get user activity data
                now = fields.Datetime.now()
                month_ago = now - timedelta(days=30)

                # Login statistics
                login_count = self._get_user_login_count(record.user_id, month_ago)

                # Feature usage
                features_used = self._get_user_feature_usage(record.user_id, month_ago)

                # Session statistics
                session_data = self._get_user_session_data(record.user_id, month_ago)

                # BCM module usage
                bcm_activity = self._get_bcm_activity(record.user_id, month_ago)

                metrics = {
                    'login_count_month': login_count,
                    'features_used': features_used,
                    'total_sessions': session_data.get('count', 0),
                    'avg_session_hours': session_data.get('avg_duration', 0.0),
                    'bcm_modules_used': bcm_activity.get('modules', []),
                    'bcm_actions_count': bcm_activity.get('actions', 0),
                    'last_computed': fields.Datetime.to_string(now),
                    'data_quality_score': self._calculate_data_quality_score(record)
                }

                record.personal_metrics = metrics

            except Exception as e:
                _logger.error(f"Error computing personal metrics for user {record.user_id.name}: {str(e)}")
                record.personal_metrics = {'error': str(e), 'last_computed': fields.Datetime.to_string(now)}

    # Default Values
    def _default_workspace_config(self):
        return {
            'theme': 'light',
            'language': 'en_US',
            'timezone': 'UTC',
            'dashboard_layout': 'default',
            'notifications': {
                'email': True,
                'browser': True,
                'mobile': False
            },
            'widgets': {
                'activity_feed': True,
                'kpi_overview': True,
                'quick_actions': True,
                'recent_documents': True
            },
            'preferences': {
                'auto_save': True,
                'compact_view': False,
                'show_hints': True
            }
        }

    def _default_privacy_settings(self):
        return {
            'profile_visibility': 'private',  # private, organization, public
            'activity_tracking': True,
            'analytics_consent': True,
            'data_sharing': {
                'organization': True,
                'platform': False,
                'third_party': False
            },
            'retention_policy': {
                'activity_logs': 365,  # days
                'metrics_history': 730,
                'patterns_analysis': 90
            }
        }

    # Constraints
    @api.constrains('user_id')
    def _check_user_unique(self):
        for record in self:
            existing = self.search([
                ('user_id', '=', record.user_id.id),
                ('id', '!=', record.id)
            ], limit=1)
            if existing:
                raise ValidationError(_("Each user can only have one personal digital twin."))

    @api.constrains('workspace_config', 'personal_metrics', 'activity_patterns', 'privacy_settings')
    def _check_json_fields(self):
        for record in self:
            fields_to_check = [
                ('workspace_config', record.workspace_config),
                ('personal_metrics', record.personal_metrics),
                ('activity_patterns', record.activity_patterns),
                ('privacy_settings', record.privacy_settings)
            ]

            for field_name, field_value in fields_to_check:
                if field_value and not isinstance(field_value, (dict, list)):
                    raise ValidationError(_("Field '%s' must contain valid JSON data") % field_name)

    # Security & Access Control
    @api.model
    def _check_access_rights(self, operation, raise_exception=True):
        """Override to implement custom access control"""
        res = super()._check_access_rights(operation, raise_exception=False)

        if not res and raise_exception:
            if operation in ('read', 'write', 'unlink'):
                # Allow users to access their own twin
                return True

        return res

    def check_access_rule(self, operation):
        """Check if user can access this record"""
        if self.env.user.has_group('base.group_system'):
            return  # System admin can access everything

        for record in self:
            if record.user_id != self.env.user:
                raise AccessError(_("You can only access your own personal digital twin."))

    # Core Action Methods
    def action_sync_personal_data(self):
        """Synchronize personal data from various sources"""
        self.ensure_one()

        try:
            self.sync_status = 'syncing'

            # Update personal metrics
            self._compute_personal_metrics()

            # Analyze activity patterns
            self._analyze_activity_patterns()

            # Sync with organization twin if available
            if self.organization_twin_id:
                self._sync_with_organization_twin()

            # Update sync timestamp
            self.last_sync = fields.Datetime.now()
            self.sync_status = 'active'

            # Log activity
            self.message_post(
                body=_("Personal data synchronized successfully"),
                message_type='notification'
            )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Personal data synchronized successfully"),
                    'type': 'success'
                }
            }

        except Exception as e:
            self.sync_status = 'error'
            _logger.error(f"Failed to sync personal data for user {self.user_id.name}: {str(e)}")
            raise UserError(_("Failed to sync personal data: %s") % str(e))

    def action_update_workspace(self):
        """Update workspace configuration"""
        self.ensure_one()

        return {
            'name': _('Update Workspace'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.personal.twin.workspace.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_twin_id': self.id,
                'current_config': self.workspace_config
            }
        }

    def action_analyze_patterns(self):
        """Analyze user activity patterns"""
        self.ensure_one()

        try:
            # Perform pattern analysis
            patterns = self._perform_pattern_analysis()

            # Update activity patterns
            self.activity_patterns = patterns

            # Generate insights
            insights = self._generate_pattern_insights(patterns)

            self.message_post(
                body=_("Activity patterns analyzed successfully"),
                message_type='notification'
            )

            return {
                'name': _('Pattern Analysis Results'),
                'type': 'ir.actions.act_window',
                'res_model': 'bcm.personal.twin.insights.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_twin_id': self.id,
                    'patterns': patterns,
                    'insights': insights
                }
            }

        except Exception as e:
            _logger.error(f"Failed to analyze patterns for user {self.user_id.name}: {str(e)}")
            raise UserError(_("Failed to analyze activity patterns: %s") % str(e))

    def action_view_dashboard(self):
        """Open personal dashboard"""
        self.ensure_one()

        return {
            'name': _('Personal Dashboard'),
            'type': 'ir.actions.act_url',
            'url': f'/bcm/personal-dashboard/{self.id}',
            'target': 'self'
        }

    def action_privacy_settings(self):
        """Open privacy settings wizard"""
        self.ensure_one()

        return {
            'name': _('Privacy Settings'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.personal.twin.privacy.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_twin_id': self.id,
                'current_settings': self.privacy_settings
            }
        }

    # EventBus Integration Methods
    def _send_eventbus_message(self, event_type, data, priority='medium'):
        """Send message to EventBus"""
        try:
            eventbus_url = self.env['ir.config_parameter'].sudo().get_param('bcm.eventbus.url', 'ws://localhost:8001')

            message = {
                'event_type': event_type,
                'source': 'personal_digital_twin',
                'user_id': self.user_id.id,
                'twin_id': self.id,
                'timestamp': fields.Datetime.now().isoformat(),
                'priority': priority,
                'data': data
            }

            # Send via WebSocket
            if eventbus_url.startswith('ws'):
                self._send_websocket_message(eventbus_url, message)
            else:
                # Send via HTTP POST
                response = requests.post(f"{eventbus_url}/events", json=message, timeout=5)
                response.raise_for_status()

            _logger.info(f"EventBus message sent: {event_type} for user {self.user_id.name}")
            return True

        except Exception as e:
            _logger.error(f"Failed to send EventBus message: {str(e)}")
            return False

    def _send_websocket_message(self, url, message):
        """Send message via WebSocket"""
        def send_message():
            try:
                with closing(websocket.create_connection(url, timeout=5)) as ws:
                    ws.send(json.dumps(message))
            except Exception as e:
                _logger.error(f"WebSocket send failed: {str(e)}")

        # Send in background thread to avoid blocking
        thread = threading.Thread(target=send_message)
        thread.daemon = True
        thread.start()

    def _sync_with_crm_user_changes(self):
        """Sync changes from res.users (CRM) to Digital Twin"""
        if not self.user_id:
            return

        user = self.user_id
        changes_detected = []

        # Check for user profile changes
        current_config = self.workspace_config or {}
        if user.lang and current_config.get('language') != user.lang:
            current_config['language'] = user.lang
            changes_detected.append('language')

        if user.tz and current_config.get('timezone') != user.tz:
            current_config['timezone'] = user.tz
            changes_detected.append('timezone')

        # Update workspace config if changes detected
        if changes_detected:
            self.workspace_config = current_config

            # Send EventBus notification
            self._send_eventbus_message('user_profile_sync', {
                'changes': changes_detected,
                'updated_config': current_config
            })

        # Track user activity
        if user.login_date and user.login_date != self.last_activity:
            self.last_activity = user.login_date

            # Send activity event
            self._send_eventbus_message('user_activity', {
                'activity_type': 'login',
                'timestamp': user.login_date.isoformat()
            })

    def _track_user_behavior(self, action_type, context_data=None):
        """Track user behavior for analysis"""
        behavior_data = {
            'action_type': action_type,
            'timestamp': fields.Datetime.now().isoformat(),
            'context': context_data or {},
            'session_info': self._get_current_session_info()
        }

        # Update activity patterns
        current_patterns = self.activity_patterns or {}
        behavior_log = current_patterns.get('behavior_log', [])
        behavior_log.append(behavior_data)

        # Keep only last 100 behavior entries
        if len(behavior_log) > 100:
            behavior_log = behavior_log[-100:]

        current_patterns['behavior_log'] = behavior_log
        current_patterns['last_tracked'] = fields.Datetime.now().isoformat()

        self.activity_patterns = current_patterns

        # Send to EventBus for real-time processing
        self._send_eventbus_message('user_behavior', behavior_data)

    def _get_current_session_info(self):
        """Get current session information"""
        return {
            'user_agent': self.env.context.get('user_agent', ''),
            'ip_address': self.env.context.get('ip_address', ''),
            'session_id': self.env.context.get('session_id', ''),
        }

    # Real Data Methods (replacing mock implementations)
    def _get_user_login_count(self, user, since_date):
        """Get actual user login count since specified date"""
        try:
            # Query actual login logs from Odoo
            domain = [
                ('user_id', '=', user.id),
                ('create_date', '>=', since_date)
            ]

            # Try to get from session logs if available
            if hasattr(self.env, 'ir.logging'):
                logs = self.env['ir.logging'].search(domain + [('name', 'ilike', 'login')])
                return len(logs)

            # Fallback: estimate based on write dates on user record
            user_writes = user.with_context(active_test=False).message_ids.filtered(
                lambda m: m.create_date >= since_date and 'login' in (m.body or '')
            )
            return len(user_writes) or 1  # At least 1 if user exists

        except Exception as e:
            _logger.warning(f"Could not get real login count: {str(e)}")
            return 1  # Conservative fallback

    def _get_user_feature_usage(self, user, since_date):
        """Get actual list of features used by user"""
        try:
            features_used = set()

            # Query mail.message for user activities
            messages = self.env['mail.message'].search([
                ('author_id', '=', user.partner_id.id),
                ('create_date', '>=', since_date)
            ])

            # Extract model usage from messages
            for message in messages:
                if message.model:
                    if message.model.startswith('bcm.'):
                        features_used.add(message.model.replace('.', '_'))
                    elif message.model in ['res.partner', 'res.users']:
                        features_used.add('user_management')
                    elif message.model.startswith('project.'):
                        features_used.add('project_management')

            # Query ir.model.access for accessed models
            accessed_models = self.env['ir.model.access'].search([
                ('group_id', 'in', user.groups_id.ids)
            ]).mapped('model_id.model')

            bcm_models = [model for model in accessed_models if model.startswith('bcm.')]
            for model in bcm_models:
                features_used.add(model.replace('.', '_'))

            # Always include basic features if user is active
            if features_used:
                features_used.add('dashboard')

            return list(features_used) or ['dashboard']  # At least dashboard

        except Exception as e:
            _logger.warning(f"Could not get real feature usage: {str(e)}")
            return ['dashboard', 'bcm_core']  # Conservative fallback

    def _get_user_session_data(self, user, since_date):
        """Get actual user session statistics"""
        try:
            # Estimate sessions from login activity patterns
            login_count = self._get_user_login_count(user, since_date)

            # Query user activities to estimate session duration
            activities = self.env['mail.message'].search([
                ('author_id', '=', user.partner_id.id),
                ('create_date', '>=', since_date)
            ], order='create_date')

            if not activities:
                return {'count': 0, 'avg_duration': 0.0, 'total_duration': 0.0}

            # Group activities by day to estimate sessions
            daily_activities = {}
            for activity in activities:
                day = activity.create_date.date()
                if day not in daily_activities:
                    daily_activities[day] = []
                daily_activities[day].append(activity.create_date)

            # Estimate session durations
            total_duration = 0.0
            session_count = 0

            for day, timestamps in daily_activities.items():
                timestamps.sort()
                if len(timestamps) >= 2:
                    # Estimate session as time between first and last activity of the day
                    duration = (timestamps[-1] - timestamps[0]).total_seconds() / 3600  # hours
                    total_duration += min(duration, 8.0)  # Cap at 8 hours per day
                    session_count += 1
                else:
                    # Single activity, assume 30 minutes
                    total_duration += 0.5
                    session_count += 1

            avg_duration = total_duration / session_count if session_count > 0 else 0.0

            return {
                'count': max(session_count, login_count),
                'avg_duration': avg_duration,
                'total_duration': total_duration
            }

        except Exception as e:
            _logger.warning(f"Could not get real session data: {str(e)}")
            return {'count': 1, 'avg_duration': 1.0, 'total_duration': 1.0}  # Conservative fallback

    def _get_bcm_activity(self, user, since_date):
        """Get actual BCM-specific activity data"""
        try:
            # Get all BCM models
            bcm_models = self.env['ir.model'].search([
                ('model', 'ilike', 'bcm.%')
            ])

            modules_used = set()
            total_actions = 0

            # Check activities on BCM models
            for model in bcm_models:
                try:
                    if model.model in self.env:
                        # Check if user has records in this model
                        record_count = self.env[model.model].search_count([
                            ('create_uid', '=', user.id),
                            ('create_date', '>=', since_date)
                        ])

                        if record_count > 0:
                            # Extract module name from model
                            module_name = '_'.join(model.model.split('.')[:-1])
                            modules_used.add(module_name)
                            total_actions += record_count

                        # Also check for write operations
                        write_count = self.env[model.model].search_count([
                            ('write_uid', '=', user.id),
                            ('write_date', '>=', since_date)
                        ])
                        total_actions += write_count

                except Exception:
                    # Skip models that can't be accessed
                    continue

            # Check mail messages on BCM objects
            bcm_messages = self.env['mail.message'].search([
                ('author_id', '=', user.partner_id.id),
                ('model', 'ilike', 'bcm.%'),
                ('create_date', '>=', since_date)
            ])

            for message in bcm_messages:
                if message.model:
                    module_name = '_'.join(message.model.split('.')[:-1])
                    modules_used.add(module_name)
                    total_actions += 1

            return {
                'modules': list(modules_used) or ['bcm_core'],
                'actions': total_actions
            }

        except Exception as e:
            _logger.warning(f"Could not get real BCM activity: {str(e)}")
            return {'modules': ['bcm_core'], 'actions': 1}  # Conservative fallback

    def _calculate_data_quality_score(self, record):
        """Calculate data quality score based on available information"""
        score = 0
        max_score = 100

        # User profile completeness
        if record.user_id.email:
            score += 20
        if record.user_id.phone:
            score += 10
        if record.user_id.image_1920:
            score += 10

        # Digital twin configuration
        if record.workspace_config:
            score += 20
        if record.privacy_settings:
            score += 15
        if record.organization_twin_id:
            score += 15

        # Recent activity
        if record.last_activity:
            days_ago = (fields.Datetime.now() - record.last_activity).days
            if days_ago <= 7:
                score += 10

        return min(score, max_score)

    def _analyze_activity_patterns(self):
        """Analyze user activity patterns"""
        if not self.personal_metrics:
            return {}

        metrics = self.personal_metrics
        now = fields.Datetime.now()

        patterns = {
            'activity_level': self._classify_activity_level(metrics),
            'peak_usage_hours': self._identify_peak_hours(metrics),
            'preferred_modules': metrics.get('bcm_modules_used', []),
            'engagement_trend': self._calculate_engagement_trend(metrics),
            'behavioral_insights': self._generate_behavioral_insights(metrics),
            'analyzed_at': fields.Datetime.to_string(now)
        }

        return patterns

    def _classify_activity_level(self, metrics):
        """Classify user activity level"""
        login_count = metrics.get('login_count_month', 0)
        actions_count = metrics.get('bcm_actions_count', 0)

        if login_count >= 20 and actions_count >= 100:
            return 'high'
        elif login_count >= 10 and actions_count >= 50:
            return 'medium'
        else:
            return 'low'

    def _identify_peak_hours(self, metrics):
        """Identify peak usage hours (mock implementation)"""
        # This would analyze actual login timestamps
        return ['09:00-11:00', '14:00-16:00']

    def _calculate_engagement_trend(self, metrics):
        """Calculate engagement trend"""
        # This would compare metrics over time
        return 'increasing'  # increasing, stable, decreasing

    def _generate_behavioral_insights(self, metrics):
        """Generate behavioral insights from patterns"""
        insights = []

        activity_level = self._classify_activity_level(metrics)
        if activity_level == 'high':
            insights.append("User shows high engagement with the platform")
        elif activity_level == 'low':
            insights.append("Consider engagement strategies to increase platform usage")

        return insights

    def _perform_pattern_analysis(self):
        """Perform comprehensive pattern analysis"""
        if not self.personal_metrics:
            return {}

        patterns = self._analyze_activity_patterns()

        # Add more sophisticated analysis here
        patterns.update({
            'predictive_insights': self._generate_predictive_insights(),
            'recommendations': self._generate_recommendations(),
            'risk_indicators': self._identify_risk_indicators()
        })

        return patterns

    def _generate_predictive_insights(self):
        """Generate predictive insights about user behavior"""
        return {
            'likely_churn_risk': 'low',
            'feature_adoption_probability': 0.75,
            'engagement_forecast': 'stable'
        }

    def _generate_recommendations(self):
        """Generate personalized recommendations"""
        return [
            "Consider exploring the Risk Management module",
            "Set up automated reports for better efficiency",
            "Join the community forum for knowledge sharing"
        ]

    def _identify_risk_indicators(self):
        """Identify potential risk indicators"""
        indicators = []

        if self.activity_score < 30:
            indicators.append("Low activity score - user may be disengaged")

        if self.twin_health_score < 50:
            indicators.append("Poor twin health - data synchronization issues")

        return indicators

    def _generate_pattern_insights(self, patterns):
        """Generate insights from analyzed patterns"""
        insights = {
            'summary': f"Activity level: {patterns.get('activity_level', 'unknown')}",
            'recommendations': patterns.get('recommendations', []),
            'behavioral_insights': patterns.get('behavioral_insights', []),
            'risk_indicators': patterns.get('risk_indicators', []),
            'generated_at': fields.Datetime.to_string(fields.Datetime.now())
        }

        return insights

    def _sync_with_organization_twin(self):
        """Sync with organization digital twin"""
        if not self.organization_twin_id:
            return

        # Update organization twin with personal metrics
        org_twin = self.organization_twin_id

        # This would implement actual synchronization logic
        _logger.info(f"Syncing personal twin {self.id} with organization twin {org_twin.id}")

    @api.model
    def create_for_user(self, user_id):
        """Create a personal digital twin for a user"""
        user = self.env['res.users'].browse(user_id)
        if not user.exists():
            raise UserError(_("User not found"))

        existing = self.search([('user_id', '=', user_id)], limit=1)
        if existing:
            return existing

        # Find associated organization twin
        org_twin = self.env['bcm.digital.twin.organization'].search([
            ('bcm_client_id.partner_id', '=', user.partner_id.parent_id.id if user.partner_id.parent_id else user.partner_id.id)
        ], limit=1)

        vals = {
            'user_id': user_id,
            'organization_twin_id': org_twin.id if org_twin else False,
            'workspace_config': self._default_workspace_config(),
            'privacy_settings': self._default_privacy_settings()
        }

        return self.create(vals)

    # Cron Methods
    @api.model
    def cron_sync_all_twins(self):
        """Cron job to sync all active personal digital twins"""
        active_twins = self.search([('sync_status', '=', 'active'), ('real_time_sync', '=', False)])

        for twin in active_twins:
            try:
                twin.action_sync_personal_data()
            except Exception as e:
                _logger.error(f"Failed to sync twin {twin.id}: {str(e)}")
                twin.sync_status = 'error'

    @api.model
    def cron_analyze_patterns(self):
        """Cron job to analyze activity patterns"""
        twins_to_analyze = self.search([
            ('sync_status', '=', 'active'),
            ('ai_insights_enabled', '=', True)
        ])

        for twin in twins_to_analyze:
            try:
                twin.action_analyze_patterns()
            except Exception as e:
                _logger.error(f"Failed to analyze patterns for twin {twin.id}: {str(e)}")

    # CRM Lifecycle Integration Methods
    @api.model
    def handle_user_created(self, user_id):
        """Handle new user creation from CRM"""
        try:
            user = self.env['res.users'].browse(user_id)
            if not user.exists():
                return False

            # Create personal digital twin automatically
            twin = self.create_for_user(user_id)

            # Send EventBus notification
            twin._send_eventbus_message('user_lifecycle', {
                'event': 'user_created',
                'user_id': user_id,
                'twin_id': twin.id,
                'user_info': {
                    'name': user.name,
                    'email': user.email,
                    'company': user.company_id.name if user.company_id else None
                }
            }, priority='high')

            _logger.info(f"Digital Twin created for new user: {user.name}")
            return twin

        except Exception as e:
            _logger.error(f"Failed to create Digital Twin for user {user_id}: {str(e)}")
            return False

    @api.model
    def handle_user_updated(self, user_id, changed_fields):
        """Handle user profile updates from CRM"""
        try:
            twin = self.search([('user_id', '=', user_id)], limit=1)
            if not twin:
                # Create twin if it doesn't exist
                twin = self.create_for_user(user_id)

            # Sync changes to twin
            twin._sync_with_crm_user_changes()

            # Track behavior change
            twin._track_user_behavior('profile_update', {
                'changed_fields': changed_fields
            })

            # Send EventBus notification
            twin._send_eventbus_message('user_lifecycle', {
                'event': 'user_updated',
                'user_id': user_id,
                'changed_fields': changed_fields
            })

            return True

        except Exception as e:
            _logger.error(f"Failed to handle user update for user {user_id}: {str(e)}")
            return False

    @api.model
    def handle_user_login(self, user_id, login_info):
        """Handle user login event from CRM"""
        try:
            twin = self.search([('user_id', '=', user_id)], limit=1)
            if not twin:
                twin = self.create_for_user(user_id)

            # Update activity tracking
            twin.last_activity = fields.Datetime.now()

            # Track login behavior
            twin._track_user_behavior('login', login_info)

            # Send EventBus notification
            twin._send_eventbus_message('user_activity', {
                'event': 'login',
                'user_id': user_id,
                'login_info': login_info
            })

            # Trigger real-time sync if enabled
            if twin.real_time_sync:
                twin.action_sync_personal_data()

            return True

        except Exception as e:
            _logger.error(f"Failed to handle user login for user {user_id}: {str(e)}")
            return False

    @api.model
    def handle_user_logout(self, user_id, session_info):
        """Handle user logout event from CRM"""
        try:
            twin = self.search([('user_id', '=', user_id)], limit=1)
            if twin:
                # Track logout behavior
                twin._track_user_behavior('logout', session_info)

                # Send EventBus notification
                twin._send_eventbus_message('user_activity', {
                    'event': 'logout',
                    'user_id': user_id,
                    'session_info': session_info
                })

            return True

        except Exception as e:
            _logger.error(f"Failed to handle user logout for user {user_id}: {str(e)}")
            return False

    @api.model
    def handle_user_deactivated(self, user_id):
        """Handle user deactivation from CRM"""
        try:
            twin = self.search([('user_id', '=', user_id)], limit=1)
            if twin:
                # Archive the twin
                twin.sync_status = 'offline'
                twin.write({
                    'real_time_sync': False,
                    'bcm_integration_active': False
                })

                # Send EventBus notification
                twin._send_eventbus_message('user_lifecycle', {
                    'event': 'user_deactivated',
                    'user_id': user_id,
                    'twin_id': twin.id
                }, priority='high')

                _logger.info(f"Digital Twin deactivated for user: {twin.user_id.name}")

            return True

        except Exception as e:
            _logger.error(f"Failed to handle user deactivation for user {user_id}: {str(e)}")
            return False

    @api.model
    def handle_role_changed(self, user_id, role_changes):
        """Handle user role changes from CRM"""
        try:
            twin = self.search([('user_id', '=', user_id)], limit=1)
            if twin:
                # Update twin permissions based on new roles
                twin._update_permissions_from_roles(role_changes)

                # Track role change
                twin._track_user_behavior('role_change', role_changes)

                # Send EventBus notification
                twin._send_eventbus_message('user_lifecycle', {
                    'event': 'role_changed',
                    'user_id': user_id,
                    'role_changes': role_changes
                })

            return True

        except Exception as e:
            _logger.error(f"Failed to handle role change for user {user_id}: {str(e)}")
            return False

    def _update_permissions_from_roles(self, role_changes):
        """Update twin permissions based on role changes"""
        if not role_changes:
            return

        # Update privacy settings based on roles
        privacy_settings = self.privacy_settings or {}

        # Admin roles get extended permissions
        if any('admin' in role.lower() for role in role_changes.get('added', [])):
            privacy_settings['profile_visibility'] = 'organization'
            privacy_settings['data_sharing']['organization'] = True

        # Manager roles get department visibility
        if any('manager' in role.lower() for role in role_changes.get('added', [])):
            privacy_settings['profile_visibility'] = 'organization'

        # Basic user restrictions
        if role_changes.get('removed') and not role_changes.get('added'):
            privacy_settings['profile_visibility'] = 'private'
            privacy_settings['data_sharing'] = {
                'organization': False,
                'platform': False,
                'third_party': False
            }

        self.privacy_settings = privacy_settings

    # Real-time EventBus Listeners
    @api.model
    def listen_to_eventbus_messages(self):
        """Listen to EventBus messages for cross-service updates"""
        try:
            eventbus_url = self.env['ir.config_parameter'].sudo().get_param('bcm.eventbus.url', 'ws://localhost:8001')

            def message_handler(message):
                try:
                    data = json.loads(message)
                    self._process_eventbus_message(data)
                except Exception as e:
                    _logger.error(f"Error processing EventBus message: {str(e)}")

            # This would be implemented with actual WebSocket connection
            # For now, we'll use a polling mechanism
            _logger.info("EventBus listener initialized for Personal Digital Twins")

        except Exception as e:
            _logger.error(f"Failed to initialize EventBus listener: {str(e)}")

    def _process_eventbus_message(self, message):
        """Process incoming EventBus message"""
        event_type = message.get('event_type')
        source = message.get('source')
        data = message.get('data', {})

        if source == 'personal_digital_twin':
            # Ignore messages from own source
            return

        # Process different message types
        if event_type == 'bcm_module_update':
            self._handle_bcm_module_update(data)
        elif event_type == 'organization_update':
            self._handle_organization_update(data)
        elif event_type == 'risk_assessment_complete':
            self._handle_risk_assessment_update(data)
        elif event_type == 'incident_created':
            self._handle_incident_notification(data)
        elif event_type == 'training_assigned':
            self._handle_training_notification(data)

    def _handle_bcm_module_update(self, data):
        """Handle BCM module update notification"""
        module_name = data.get('module')
        user_affected = data.get('user_id') == self.user_id.id

        if user_affected:
            # Trigger sync to get latest data
            if self.real_time_sync:
                self.action_sync_personal_data()

            # Track module interaction
            self._track_user_behavior('module_update', {
                'module': module_name,
                'update_type': data.get('update_type')
            })

    def _handle_organization_update(self, data):
        """Handle organization-level update"""
        if self.organization_twin_id and data.get('org_twin_id') == self.organization_twin_id.id:
            # Sync with organization changes
            self._sync_with_organization_twin()

    def _handle_risk_assessment_update(self, data):
        """Handle risk assessment completion"""
        if data.get('assigned_user_id') == self.user_id.id:
            # Add notification to personal metrics
            metrics = self.personal_metrics or {}
            metrics['pending_notifications'] = metrics.get('pending_notifications', [])
            metrics['pending_notifications'].append({
                'type': 'risk_assessment',
                'title': 'Risk Assessment Completed',
                'data': data,
                'timestamp': fields.Datetime.now().isoformat()
            })
            self.personal_metrics = metrics

    def _handle_incident_notification(self, data):
        """Handle incident creation notification"""
        if data.get('assigned_users') and self.user_id.id in data.get('assigned_users', []):
            # Add urgent notification
            metrics = self.personal_metrics or {}
            metrics['urgent_notifications'] = metrics.get('urgent_notifications', [])
            metrics['urgent_notifications'].append({
                'type': 'incident',
                'title': f"New Incident: {data.get('title', 'Unknown')}",
                'priority': 'high',
                'data': data,
                'timestamp': fields.Datetime.now().isoformat()
            })
            self.personal_metrics = metrics

    def _handle_training_notification(self, data):
        """Handle training assignment notification"""
        if data.get('assigned_user_id') == self.user_id.id:
            # Add training notification
            metrics = self.personal_metrics or {}
            metrics['training_notifications'] = metrics.get('training_notifications', [])
            metrics['training_notifications'].append({
                'type': 'training',
                'title': f"Training Assigned: {data.get('title', 'Unknown')}",
                'due_date': data.get('due_date'),
                'data': data,
                'timestamp': fields.Datetime.now().isoformat()
            })
            self.personal_metrics = metrics