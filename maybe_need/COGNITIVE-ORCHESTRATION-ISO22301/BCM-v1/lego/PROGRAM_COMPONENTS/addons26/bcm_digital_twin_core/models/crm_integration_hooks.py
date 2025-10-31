# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
import logging

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    """
    CRM Integration Hooks for res.users

    This model extends res.users to provide hooks that drive the entire
    Digital Twin ecosystem through CRM lifecycle management.
    """
    _inherit = 'res.users'

    # Digital Twin Integration Fields
    digital_twin_id = fields.Many2one(
        'bcm.personal.digital.twin',
        string='Digital Twin',
        help="Associated personal digital twin",
        readonly=True
    )

    digital_twin_status = fields.Selection(
        related='digital_twin_id.sync_status',
        string='Twin Status',
        readonly=True
    )

    digital_twin_health = fields.Float(
        related='digital_twin_id.twin_health_score',
        string='Twin Health Score',
        readonly=True
    )

    # CRM Lifecycle Hooks

    @api.model_create_multi
    def create(self, vals_list):
        """Hook into user creation to trigger Digital Twin lifecycle"""
        users = super().create(vals_list)

        # Get lifecycle manager
        lifecycle_manager = self.env['bcm.digital.twin.lifecycle.manager'].get_singleton()

        for user in users:
            try:
                # Trigger Digital Twin creation
                lifecycle_manager.api_user_created(user.id, {
                    'name': user.name,
                    'email': user.email,
                    'company': user.company_id.name if user.company_id else None,
                    'groups': user.groups_id.mapped('name'),
                    'language': user.lang,
                    'timezone': user.tz
                })

                _logger.info(f"Digital Twin lifecycle triggered for new user: {user.name}")

            except Exception as e:
                _logger.error(f"Failed to trigger Digital Twin lifecycle for user {user.name}: {str(e)}")

        return users

    def write(self, vals):
        """Hook into user updates to sync with Digital Twin"""
        # Capture old values for comparison
        old_values = {}
        changed_fields = list(vals.keys())

        for record in self:
            old_values[record.id] = {}
            for field in changed_fields:
                if hasattr(record, field):
                    old_value = getattr(record, field)
                    if hasattr(old_value, 'id'):  # Many2one
                        old_values[record.id][field] = old_value.id
                    elif hasattr(old_value, 'ids'):  # Many2many/One2many
                        old_values[record.id][field] = old_value.ids
                    else:
                        old_values[record.id][field] = old_value

        # Perform the update
        result = super().write(vals)

        # Trigger Digital Twin sync
        lifecycle_manager = self.env['bcm.digital.twin.lifecycle.manager'].get_singleton()

        for record in self:
            try:
                lifecycle_manager.api_user_updated(
                    record.id,
                    changed_fields,
                    old_values.get(record.id, {})
                )

                # Also queue for data sync
                sync_engine = self.env['bcm.data.sync.engine'].get_singleton()
                sync_engine.queue_sync_operation(
                    'update',
                    'res.users',
                    record.id,
                    {
                        'changed_fields': changed_fields,
                        'old_values': old_values.get(record.id, {}),
                        'new_values': vals
                    },
                    priority='high'
                )

            except Exception as e:
                _logger.error(f"Failed to sync user update for {record.name}: {str(e)}")

        return result

    def action_archive(self):
        """Hook into user archiving to deactivate Digital Twin"""
        lifecycle_manager = self.env['bcm.digital.twin.lifecycle.manager'].get_singleton()

        for record in self:
            try:
                lifecycle_manager.api_user_deactivated(record.id)
                _logger.info(f"Digital Twin deactivated for archived user: {record.name}")
            except Exception as e:
                _logger.error(f"Failed to deactivate Digital Twin for {record.name}: {str(e)}")

        return super().action_archive()

    def action_unarchive(self):
        """Hook into user unarchiving to reactivate Digital Twin"""
        result = super().action_unarchive()

        lifecycle_manager = self.env['bcm.digital.twin.lifecycle.manager'].get_singleton()

        for record in self:
            try:
                # Reactivate by creating/updating Digital Twin
                lifecycle_manager.api_user_created(record.id, {
                    'name': record.name,
                    'email': record.email,
                    'reactivation': True
                })
                _logger.info(f"Digital Twin reactivated for unarchived user: {record.name}")
            except Exception as e:
                _logger.error(f"Failed to reactivate Digital Twin for {record.name}: {str(e)}")

        return result

    # Login/Logout Hooks

    def _update_last_login(self):
        """Hook into login to trigger Digital Twin activity tracking"""
        result = super()._update_last_login()

        lifecycle_manager = self.env['bcm.digital.twin.lifecycle.manager'].get_singleton()

        try:
            login_info = {
                'timestamp': fields.Datetime.now().isoformat(),
                'ip_address': self.env.context.get('ip_address', ''),
                'user_agent': self.env.context.get('user_agent', ''),
                'session_id': self.env.context.get('session_id', '')
            }

            lifecycle_manager.api_user_login(self.id, login_info)

        except Exception as e:
            _logger.error(f"Failed to process login for Digital Twin: {str(e)}")

        return result

    # Role Management Hooks

    def set_groups_id(self, groups_id):
        """Hook into role changes to update Digital Twin permissions"""
        # Get current groups for comparison
        old_groups = self.groups_id.mapped('name')

        # Perform the group change
        result = super().set_groups_id(groups_id)

        # Get new groups
        new_groups = self.groups_id.mapped('name')

        # Calculate changes
        added_groups = list(set(new_groups) - set(old_groups))
        removed_groups = list(set(old_groups) - set(new_groups))

        if added_groups or removed_groups:
            lifecycle_manager = self.env['bcm.digital.twin.lifecycle.manager'].get_singleton()

            try:
                role_changes = {
                    'added': added_groups,
                    'removed': removed_groups
                }

                lifecycle_manager.api_role_changed(self.id, role_changes)

            except Exception as e:
                _logger.error(f"Failed to process role change for Digital Twin: {str(e)}")

        return result

    # Digital Twin Management Actions

    def action_view_digital_twin(self):
        """Action to view user's Digital Twin"""
        self.ensure_one()

        if not self.digital_twin_id:
            # Create Digital Twin if it doesn't exist
            twin_model = self.env['bcm.personal.digital.twin']
            twin = twin_model.create_for_user(self.id)
            self.digital_twin_id = twin.id

        return {
            'name': _('Personal Digital Twin'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.personal.digital.twin',
            'res_id': self.digital_twin_id.id,
            'view_mode': 'form',
            'target': 'current'
        }

    def action_sync_digital_twin(self):
        """Action to manually sync Digital Twin"""
        self.ensure_one()

        if self.digital_twin_id:
            try:
                self.digital_twin_id.action_sync_personal_data()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Success"),
                        'message': _("Digital Twin synchronized successfully"),
                        'type': 'success'
                    }
                }
            except Exception as e:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Error"),
                        'message': f"Failed to sync Digital Twin: {str(e)}",
                        'type': 'danger'
                    }
                }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Warning"),
                    'message': _("No Digital Twin found for this user"),
                    'type': 'warning'
                }
            }


class BCMModelBase(models.AbstractModel):
    """
    Base model for all BCM models to integrate with Digital Twin ecosystem
    """
    _name = 'bcm.model.base'
    _description = 'BCM Model Base for Digital Twin Integration'

    @api.model_create_multi
    def create(self, vals_list):
        """Hook into BCM model creation for Digital Twin sync"""
        records = super().create(vals_list)

        # Queue for synchronization
        sync_engine = self.env['bcm.data.sync.engine'].get_singleton()

        for record in records:
            try:
                sync_engine.queue_sync_operation(
                    'create',
                    record._name,
                    record.id,
                    {'created_data': vals_list},
                    priority='medium'
                )
            except Exception as e:
                _logger.error(f"Failed to queue sync for {record._name} creation: {str(e)}")

        return records

    def write(self, vals):
        """Hook into BCM model updates for Digital Twin sync"""
        # Capture changed fields
        changed_fields = list(vals.keys())

        # Perform the update
        result = super().write(vals)

        # Queue for synchronization
        sync_engine = self.env['bcm.data.sync.engine'].get_singleton()

        for record in self:
            try:
                sync_engine.queue_sync_operation(
                    'update',
                    record._name,
                    record.id,
                    {
                        'changed_fields': changed_fields,
                        'updated_data': vals
                    },
                    priority='medium'
                )
            except Exception as e:
                _logger.error(f"Failed to queue sync for {record._name} update: {str(e)}")

        return result

    def unlink(self):
        """Hook into BCM model deletion for Digital Twin sync"""
        # Capture record info before deletion
        records_info = []
        for record in self:
            records_info.append({
                'id': record.id,
                'name': getattr(record, 'name', str(record.id)),
                'model': record._name
            })

        # Perform deletion
        result = super().unlink()

        # Queue deletion sync
        sync_engine = self.env['bcm.data.sync.engine'].get_singleton()

        for record_info in records_info:
            try:
                sync_engine.queue_sync_operation(
                    'delete',
                    record_info['model'],
                    record_info['id'],
                    {'deleted_record': record_info},
                    priority='high'
                )
            except Exception as e:
                _logger.error(f"Failed to queue sync for {record_info['model']} deletion: {str(e)}")

        return result


# Apply BCM integration to key models
class BCMIncident(models.Model):
    _inherit = ['bcm.incident', 'bcm.model.base']
    _name = 'bcm.incident'


class BCMRiskAssessment(models.Model):
    _inherit = ['bcm.risk.assessment', 'bcm.model.base']
    _name = 'bcm.risk.assessment'


class BCMBusinessProcess(models.Model):
    _inherit = ['bcm.business.process', 'bcm.model.base']
    _name = 'bcm.business.process'


class BCMPlan(models.Model):
    _inherit = ['bcm.plan', 'bcm.model.base']
    _name = 'bcm.plan'


# Session Management for Digital Twin Activity Tracking
class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _authenticate(cls, endpoint):
        """Hook into authentication to track user activity"""
        result = super()._authenticate(endpoint)

        try:
            request = cls._get_request()
            if hasattr(request, 'env') and hasattr(request, 'session'):
                user_id = request.session.get('uid')

                if user_id:
                    # Track user activity in Digital Twin
                    lifecycle_manager = request.env['bcm.digital.twin.lifecycle.manager'].get_singleton()

                    # Set context for tracking
                    request.env = request.env.with_context(
                        ip_address=request.httprequest.environ.get('REMOTE_ADDR', ''),
                        user_agent=request.httprequest.headers.get('User-Agent', ''),
                        session_id=request.session.sid
                    )

        except Exception as e:
            _logger.error(f"Failed to track authentication activity: {str(e)}")

        return result


# Automated System Integration
class BCMDigitalTwinSystemIntegration(models.Model):
    """
    System integration model that orchestrates the entire Digital Twin ecosystem
    """
    _name = 'bcm.digital.twin.system.integration'
    _description = 'Digital Twin System Integration Orchestrator'
    _rec_name = 'name'

    name = fields.Char(
        string='Integration Name',
        default='BCM Digital Twin System Integration',
        readonly=True
    )

    # Integration Status
    lifecycle_manager_status = fields.Selection(
        related='lifecycle_manager_id.status',
        string='Lifecycle Manager Status'
    )

    eventbus_status = fields.Selection(
        related='eventbus_integration_id.status',
        string='EventBus Status'
    )

    service_registry_status = fields.Selection(
        related='service_registry_id.status',
        string='Service Registry Status'
    )

    sync_engine_status = fields.Selection(
        related='sync_engine_id.status',
        string='Sync Engine Status'
    )

    # Component References
    lifecycle_manager_id = fields.Many2one(
        'bcm.digital.twin.lifecycle.manager',
        string='Lifecycle Manager',
        compute='_compute_components',
        store=True
    )

    eventbus_integration_id = fields.Many2one(
        'bcm.eventbus.integration',
        string='EventBus Integration',
        compute='_compute_components',
        store=True
    )

    service_registry_id = fields.Many2one(
        'bcm.service.registry',
        string='Service Registry',
        compute='_compute_components',
        store=True
    )

    sync_engine_id = fields.Many2one(
        'bcm.data.sync.engine',
        string='Sync Engine',
        compute='_compute_components',
        store=True
    )

    # System Health
    overall_health = fields.Selection([
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('unhealthy', 'Unhealthy')
    ], string='Overall System Health', compute='_compute_overall_health')

    active_twins_count = fields.Integer(
        string='Active Digital Twins',
        compute='_compute_system_metrics'
    )

    total_services_count = fields.Integer(
        string='Total Registered Services',
        compute='_compute_system_metrics'
    )

    pending_sync_count = fields.Integer(
        string='Pending Sync Operations',
        compute='_compute_system_metrics'
    )

    @api.depends()
    def _compute_components(self):
        for record in self:
            record.lifecycle_manager_id = self.env['bcm.digital.twin.lifecycle.manager'].get_singleton()
            record.eventbus_integration_id = self.env['bcm.eventbus.integration'].get_singleton()
            record.service_registry_id = self.env['bcm.service.registry'].get_singleton()
            record.sync_engine_id = self.env['bcm.data.sync.engine'].get_singleton()

    @api.depends('lifecycle_manager_status', 'eventbus_status', 'service_registry_status', 'sync_engine_status')
    def _compute_overall_health(self):
        for record in self:
            statuses = [
                record.lifecycle_manager_status,
                record.eventbus_status,
                record.service_registry_status,
                record.sync_engine_status
            ]

            if all(status == 'active' for status in statuses):
                record.overall_health = 'healthy'
            elif any(status == 'error' for status in statuses):
                record.overall_health = 'unhealthy'
            else:
                record.overall_health = 'degraded'

    @api.depends()
    def _compute_system_metrics(self):
        for record in self:
            record.active_twins_count = self.env['bcm.personal.digital.twin'].search_count([
                ('sync_status', '=', 'active')
            ])

            registry = self.env['bcm.service.registry'].get_singleton()
            record.total_services_count = registry.total_services

            sync_engine = self.env['bcm.data.sync.engine'].get_singleton()
            record.pending_sync_count = sync_engine.pending_sync_count

    @api.model
    def get_singleton(self):
        """Get or create the singleton system integration"""
        integration = self.search([], limit=1)
        if not integration:
            integration = self.create({
                'name': 'BCM Digital Twin System Integration'
            })
        return integration

    def action_initialize_system(self):
        """Initialize the entire Digital Twin system"""
        self.ensure_one()

        try:
            # Initialize all components
            self.lifecycle_manager_id.action_start_manager()
            self.eventbus_integration_id.action_connect()
            self.service_registry_id.action_discover_services()
            self.sync_engine_id.action_process_queue()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("Digital Twin system initialized successfully"),
                    'type': 'success'
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error"),
                    'message': f"Failed to initialize system: {str(e)}",
                    'type': 'danger'
                }
            }

    def action_system_health_check(self):
        """Perform comprehensive system health check"""
        self.ensure_one()

        try:
            # Trigger health checks on all components
            self.service_registry_id.action_health_check()

            health_report = {
                'overall_health': self.overall_health,
                'active_twins': self.active_twins_count,
                'total_services': self.total_services_count,
                'pending_syncs': self.pending_sync_count,
                'component_status': {
                    'lifecycle_manager': self.lifecycle_manager_status,
                    'eventbus': self.eventbus_status,
                    'service_registry': self.service_registry_status,
                    'sync_engine': self.sync_engine_status
                }
            }

            return {
                'name': _('System Health Report'),
                'type': 'ir.actions.act_window',
                'res_model': 'bcm.digital.twin.health.report.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_integration_id': self.id,
                    'health_report': health_report
                }
            }

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error"),
                    'message': f"Health check failed: {str(e)}",
                    'type': 'danger'
                }
            }