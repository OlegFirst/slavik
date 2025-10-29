# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
import json
import logging
import threading
import time
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict, OrderedDict
import queue

_logger = logging.getLogger(__name__)

class DataSyncEngine(models.Model):
    _name = 'bcm.data.sync.engine'
    _description = 'Data Synchronization Engine'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # Core Information
    name = fields.Char(
        string='Engine Name',
        default='BCM Data Synchronization Engine',
        required=True
    )

    description = fields.Text(
        string='Description',
        help="Description of the synchronization engine"
    )

    # Configuration
    sync_mode = fields.Selection([
        ('real_time', 'Real-time'),
        ('batch', 'Batch'),
        ('hybrid', 'Hybrid (Real-time + Batch)')
    ], string='Sync Mode', default='hybrid',
       help="Synchronization mode")

    batch_size = fields.Integer(
        string='Batch Size',
        default=100,
        help="Number of records to process in each batch"
    )

    batch_interval = fields.Integer(
        string='Batch Interval (minutes)',
        default=15,
        help="Interval between batch synchronizations"
    )

    max_retry_attempts = fields.Integer(
        string='Max Retry Attempts',
        default=3,
        help="Maximum number of retry attempts for failed syncs"
    )

    conflict_resolution = fields.Selection([
        ('latest_wins', 'Latest Timestamp Wins'),
        ('source_priority', 'Source Priority'),
        ('manual_review', 'Manual Review Required'),
        ('merge_strategy', 'Intelligent Merge')
    ], string='Conflict Resolution', default='latest_wins',
       help="Strategy for resolving data conflicts")

    # Status and Monitoring
    status = fields.Selection([
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('syncing', 'Syncing'),
        ('error', 'Error'),
        ('maintenance', 'Maintenance')
    ], string='Status', default='active', tracking=True)

    last_sync = fields.Datetime(
        string='Last Synchronization',
        help="Timestamp of last synchronization"
    )

    next_sync = fields.Datetime(
        string='Next Scheduled Sync',
        compute='_compute_next_sync',
        help="Next scheduled synchronization time"
    )

    # Performance Metrics
    total_records_synced = fields.Integer(
        string='Total Records Synced',
        default=0,
        help="Total number of records synchronized"
    )

    sync_success_rate = fields.Float(
        string='Success Rate (%)',
        compute='_compute_sync_metrics',
        help="Synchronization success rate percentage"
    )

    avg_sync_time = fields.Float(
        string='Average Sync Time (seconds)',
        compute='_compute_sync_metrics',
        help="Average time for synchronization operations"
    )

    pending_sync_count = fields.Integer(
        string='Pending Sync Count',
        compute='_compute_sync_metrics',
        help="Number of records pending synchronization"
    )

    # Sync Configuration
    enabled_modules = fields.Text(
        string='Enabled Modules',
        default='bcm_core,bcm_incident,bcm_risk_management,bcm_bia,bcm_governance,bcm_audit,bcm_training,bcm_templates,bcm_scenario_hub,bcm_reporting',
        help="Comma-separated list of modules to synchronize"
    )

    sync_triggers = fields.Json(
        string='Sync Triggers',
        help="Configuration for synchronization triggers",
        default=lambda self: self._default_sync_triggers()
    )

    data_validation_rules = fields.Json(
        string='Data Validation Rules',
        help="Rules for validating data during synchronization",
        default=lambda self: self._default_validation_rules()
    )

    # Sync Queue and Logs
    sync_queue = fields.Json(
        string='Synchronization Queue',
        help="Queue of pending synchronization operations",
        default=lambda self: []
    )

    sync_log = fields.Json(
        string='Synchronization Log',
        help="Log of synchronization operations",
        default=lambda self: []
    )

    conflict_log = fields.Json(
        string='Conflict Log',
        help="Log of data conflicts and resolutions",
        default=lambda self: []
    )

    error_log = fields.Json(
        string='Error Log',
        help="Log of synchronization errors",
        default=lambda self: []
    )

    # Data Mapping and Transformation
    field_mappings = fields.Json(
        string='Field Mappings',
        help="Mappings between different data sources",
        default=lambda self: {}
    )

    transformation_rules = fields.Json(
        string='Transformation Rules',
        help="Rules for transforming data during sync",
        default=lambda self: {}
    )

    # Company
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )

    # Computed Fields
    @api.depends('last_sync', 'batch_interval')
    def _compute_next_sync(self):
        for record in self:
            if record.last_sync and record.sync_mode in ['batch', 'hybrid']:
                record.next_sync = record.last_sync + timedelta(minutes=record.batch_interval)
            else:
                record.next_sync = False

    @api.depends('sync_log', 'sync_queue')
    def _compute_sync_metrics(self):
        for record in self:
            logs = record.sync_log or []
            queue_items = record.sync_queue or []

            # Calculate success rate
            if logs:
                successful_syncs = len([log for log in logs if log.get('status') == 'success'])
                record.sync_success_rate = (successful_syncs / len(logs)) * 100
            else:
                record.sync_success_rate = 0.0

            # Calculate average sync time
            sync_times = [log.get('duration', 0) for log in logs if log.get('duration')]
            record.avg_sync_time = sum(sync_times) / len(sync_times) if sync_times else 0.0

            # Pending sync count
            record.pending_sync_count = len(queue_items)

    # Default Configurations
    def _default_sync_triggers(self):
        return {
            'model_create': True,
            'model_write': True,
            'model_unlink': False,  # Usually don't sync deletions immediately
            'user_login': True,
            'user_logout': False,
            'cron_batch': True,
            'manual_trigger': True,
            'eventbus_events': True
        }

    def _default_validation_rules(self):
        return {
            'required_fields': {
                'bcm.personal.digital.twin': ['user_id'],
                'bcm.incident': ['name', 'priority'],
                'bcm.risk.assessment': ['name', 'risk_level']
            },
            'data_types': {
                'dates': 'validate_datetime_format',
                'emails': 'validate_email_format',
                'json_fields': 'validate_json_structure'
            },
            'referential_integrity': {
                'check_foreign_keys': True,
                'auto_create_missing_references': False
            }
        }

    # Core Synchronization Methods

    @api.model
    def get_singleton(self):
        """Get or create the singleton sync engine"""
        engine = self.search([], limit=1)
        if not engine:
            engine = self.create({
                'name': 'BCM Data Synchronization Engine'
            })
        return engine

    def queue_sync_operation(self, operation_type, model_name, record_id, data=None, priority='medium'):
        """Queue a synchronization operation"""
        try:
            if self.status not in ['active', 'syncing']:
                return False

            sync_queue = self.sync_queue or []

            # Check if operation already exists in queue
            existing_op = None
            for i, op in enumerate(sync_queue):
                if (op.get('model_name') == model_name and
                    op.get('record_id') == record_id and
                    op.get('operation_type') == operation_type):
                    existing_op = i
                    break

            operation = {
                'id': f"{model_name}_{record_id}_{operation_type}_{int(time.time())}",
                'operation_type': operation_type,  # create, update, delete, bulk_sync
                'model_name': model_name,
                'record_id': record_id,
                'data': data or {},
                'priority': priority,
                'queued_at': fields.Datetime.now().isoformat(),
                'retry_count': 0,
                'status': 'pending'
            }

            if existing_op is not None:
                # Update existing operation
                sync_queue[existing_op] = operation
            else:
                # Add new operation
                sync_queue.append(operation)

            # Sort by priority and timestamp
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            sync_queue.sort(key=lambda x: (
                priority_order.get(x.get('priority', 'medium'), 2),
                x.get('queued_at', '')
            ))

            self.sync_queue = sync_queue

            # Trigger immediate sync for real-time operations
            if self.sync_mode in ['real_time', 'hybrid'] and priority in ['critical', 'high']:
                self._process_sync_queue_immediate()

            return True

        except Exception as e:
            _logger.error(f"Failed to queue sync operation: {str(e)}")
            return False

    def process_sync_queue(self):
        """Process the synchronization queue"""
        try:
            if self.status != 'active':
                return False

            self.status = 'syncing'
            sync_queue = self.sync_queue or []

            if not sync_queue:
                self.status = 'active'
                return True

            processed_count = 0
            successful_count = 0
            errors = []

            start_time = time.time()

            # Process operations in batches
            for i in range(0, len(sync_queue), self.batch_size):
                batch = sync_queue[i:i + self.batch_size]

                for operation in batch:
                    try:
                        success = self._process_sync_operation(operation)
                        if success:
                            successful_count += 1
                            operation['status'] = 'completed'
                        else:
                            operation['status'] = 'failed'
                            operation['retry_count'] += 1

                        processed_count += 1

                    except Exception as e:
                        error_msg = f"Sync operation failed: {str(e)}"
                        errors.append(error_msg)
                        operation['status'] = 'error'
                        operation['error'] = str(e)
                        operation['retry_count'] += 1

            # Remove completed operations and prepare retry operations
            remaining_queue = []
            for operation in sync_queue:
                if operation['status'] == 'completed':
                    continue
                elif operation['status'] in ['failed', 'error'] and operation['retry_count'] >= self.max_retry_attempts:
                    # Move to error log
                    self._log_sync_error(operation)
                    continue
                else:
                    # Keep for retry
                    remaining_queue.append(operation)

            self.sync_queue = remaining_queue

            # Update metrics
            self.total_records_synced += successful_count
            self.last_sync = fields.Datetime.now()

            # Log sync operation
            duration = time.time() - start_time
            self._log_sync_operation({
                'operation': 'batch_sync',
                'processed': processed_count,
                'successful': successful_count,
                'errors': len(errors),
                'duration': duration,
                'status': 'success' if len(errors) == 0 else 'partial_success'
            })

            self.status = 'active'

            # Send EventBus notification
            self._send_sync_event('sync_completed', {
                'processed': processed_count,
                'successful': successful_count,
                'errors': len(errors),
                'remaining_queue': len(remaining_queue)
            })

            return True

        except Exception as e:
            self.status = 'error'
            _logger.error(f"Sync queue processing failed: {str(e)}")
            return False

    def _process_sync_operation(self, operation):
        """Process a single synchronization operation"""
        try:
            operation_type = operation.get('operation_type')
            model_name = operation.get('model_name')
            record_id = operation.get('record_id')
            data = operation.get('data', {})

            if operation_type == 'create':
                return self._sync_record_create(model_name, record_id, data)
            elif operation_type == 'update':
                return self._sync_record_update(model_name, record_id, data)
            elif operation_type == 'delete':
                return self._sync_record_delete(model_name, record_id, data)
            elif operation_type == 'bulk_sync':
                return self._sync_bulk_operation(model_name, data)
            else:
                _logger.warning(f"Unknown sync operation type: {operation_type}")
                return False

        except Exception as e:
            _logger.error(f"Failed to process sync operation: {str(e)}")
            return False

    def _sync_record_create(self, model_name, record_id, data):
        """Synchronize record creation across modules"""
        try:
            # Get the record
            if model_name not in self.env:
                return False

            record = self.env[model_name].browse(record_id)
            if not record.exists():
                return False

            # Determine which modules need to be notified
            target_modules = self._get_dependent_modules(model_name)

            # Sync to Digital Twins if user-related
            if self._is_user_related_model(model_name):
                self._sync_to_digital_twins(model_name, record, 'create')

            # Sync to other BCM modules
            for target_module in target_modules:
                self._sync_to_module(target_module, model_name, record, 'create', data)

            # Send EventBus notification
            self._send_sync_event('record_synced', {
                'operation': 'create',
                'model': model_name,
                'record_id': record_id,
                'synced_to': target_modules
            })

            return True

        except Exception as e:
            _logger.error(f"Record create sync failed: {str(e)}")
            return False

    def _sync_record_update(self, model_name, record_id, data):
        """Synchronize record updates across modules"""
        try:
            if model_name not in self.env:
                return False

            record = self.env[model_name].browse(record_id)
            if not record.exists():
                return False

            changed_fields = data.get('changed_fields', [])
            old_values = data.get('old_values', {})

            # Check for conflicts
            conflicts = self._detect_conflicts(model_name, record_id, changed_fields, old_values)
            if conflicts:
                resolved_data = self._resolve_conflicts(conflicts, data)
                if not resolved_data:
                    return False
                data = resolved_data

            # Determine which modules need to be notified
            target_modules = self._get_dependent_modules(model_name)

            # Sync to Digital Twins if user-related
            if self._is_user_related_model(model_name):
                self._sync_to_digital_twins(model_name, record, 'update', changed_fields)

            # Sync to other BCM modules
            for target_module in target_modules:
                self._sync_to_module(target_module, model_name, record, 'update', data)

            # Send EventBus notification
            self._send_sync_event('record_synced', {
                'operation': 'update',
                'model': model_name,
                'record_id': record_id,
                'changed_fields': changed_fields,
                'synced_to': target_modules
            })

            return True

        except Exception as e:
            _logger.error(f"Record update sync failed: {str(e)}")
            return False

    def _sync_record_delete(self, model_name, record_id, data):
        """Synchronize record deletion across modules"""
        try:
            # Usually deletions are handled carefully
            # May need to mark as inactive instead of actual deletion

            target_modules = self._get_dependent_modules(model_name)

            # Notify Digital Twins if user-related
            if self._is_user_related_model(model_name):
                self._sync_deletion_to_digital_twins(model_name, record_id, data)

            # Send EventBus notification
            self._send_sync_event('record_deleted', {
                'model': model_name,
                'record_id': record_id,
                'notified_modules': target_modules
            })

            return True

        except Exception as e:
            _logger.error(f"Record delete sync failed: {str(e)}")
            return False

    # Module Integration Methods

    def _get_dependent_modules(self, model_name):
        """Get modules that depend on changes to this model"""
        dependencies = {
            'res.users': ['bcm_digital_twin_core', 'bcm_core', 'bcm_portal'],
            'bcm.personal.digital.twin': ['bcm_core', 'bcm_portal', 'bcm_reporting'],
            'bcm.incident': ['bcm_core', 'bcm_risk_management', 'bcm_reporting', 'bcm_digital_twin_core'],
            'bcm.risk.assessment': ['bcm_core', 'bcm_incident', 'bcm_governance', 'bcm_digital_twin_core'],
            'bcm.business.process': ['bcm_core', 'bcm_bia', 'bcm_incident', 'bcm_digital_twin_core'],
            'bcm.plan': ['bcm_core', 'bcm_incident', 'bcm_exercise', 'bcm_digital_twin_core']
        }

        return dependencies.get(model_name, [])

    def _is_user_related_model(self, model_name):
        """Check if model is related to users and should sync to Digital Twins"""
        user_related_models = [
            'res.users',
            'bcm.incident',
            'bcm.risk.assessment',
            'bcm.training.assignment',
            'bcm.exercise.participation'
        ]
        return model_name in user_related_models

    def _sync_to_digital_twins(self, model_name, record, operation, changed_fields=None):
        """Sync changes to Digital Twins"""
        try:
            if model_name == 'res.users':
                # User changes
                twin_model = self.env['bcm.personal.digital.twin']
                lifecycle_manager = self.env['bcm.digital.twin.lifecycle.manager'].get_singleton()

                if operation == 'create':
                    lifecycle_manager.process_user_creation(record.id)
                elif operation == 'update':
                    lifecycle_manager.process_user_update(record.id, changed_fields or [])

            elif model_name in ['bcm.incident', 'bcm.risk.assessment']:
                # Find affected users
                affected_users = self._get_affected_users(record)
                for user_id in affected_users:
                    twin = self.env['bcm.personal.digital.twin'].search([
                        ('user_id', '=', user_id)
                    ], limit=1)
                    if twin:
                        # Update personal metrics
                        twin.action_sync_personal_data()

        except Exception as e:
            _logger.error(f"Digital Twin sync failed: {str(e)}")

    def _sync_to_module(self, target_module, model_name, record, operation, data):
        """Sync to a specific BCM module"""
        try:
            # This would implement specific sync logic for each module
            # For now, we'll log the sync operation
            _logger.info(f"Syncing {model_name} record {record.id} to {target_module} (operation: {operation})")

            # Send module-specific EventBus events
            self._send_sync_event('module_sync', {
                'target_module': target_module,
                'source_model': model_name,
                'record_id': record.id,
                'operation': operation,
                'data': data
            })

        except Exception as e:
            _logger.error(f"Module sync failed for {target_module}: {str(e)}")

    def _get_affected_users(self, record):
        """Get users affected by a record change"""
        affected_users = []

        try:
            # Common patterns for finding affected users
            if hasattr(record, 'user_id') and record.user_id:
                affected_users.append(record.user_id.id)

            if hasattr(record, 'assigned_user_ids'):
                affected_users.extend(record.assigned_user_ids.ids)

            if hasattr(record, 'responsible_user_id') and record.responsible_user_id:
                affected_users.append(record.responsible_user_id.id)

            if hasattr(record, 'create_uid') and record.create_uid:
                affected_users.append(record.create_uid.id)

        except Exception as e:
            _logger.error(f"Failed to get affected users: {str(e)}")

        return list(set(affected_users))  # Remove duplicates

    # Conflict Resolution

    def _detect_conflicts(self, model_name, record_id, changed_fields, old_values):
        """Detect data conflicts during synchronization"""
        try:
            conflicts = []

            if model_name not in self.env:
                return conflicts

            current_record = self.env[model_name].browse(record_id)
            if not current_record.exists():
                return conflicts

            # Check for concurrent modifications
            for field_name in changed_fields:
                if hasattr(current_record, field_name):
                    current_value = getattr(current_record, field_name)
                    old_value = old_values.get(field_name)

                    # Convert values for comparison
                    if hasattr(current_value, 'id'):  # Many2one field
                        current_value = current_value.id
                    elif hasattr(current_value, 'ids'):  # Many2many/One2many field
                        current_value = sorted(current_value.ids)

                    # Check if current value differs from old value
                    if current_value != old_value:
                        conflicts.append({
                            'field': field_name,
                            'old_value': old_value,
                            'current_value': current_value,
                            'conflict_type': 'concurrent_modification'
                        })

            return conflicts

        except Exception as e:
            _logger.error(f"Conflict detection failed: {str(e)}")
            return []

    def _resolve_conflicts(self, conflicts, data):
        """Resolve data conflicts based on configured strategy"""
        try:
            if not conflicts:
                return data

            resolved_data = data.copy()
            resolution_strategy = self.conflict_resolution

            for conflict in conflicts:
                field_name = conflict['field']

                if resolution_strategy == 'latest_wins':
                    # Keep the current value (do nothing)
                    if field_name in resolved_data.get('values', {}):
                        del resolved_data['values'][field_name]

                elif resolution_strategy == 'source_priority':
                    # Use source priority logic (implementation specific)
                    # For now, keep the incoming change
                    pass

                elif resolution_strategy == 'manual_review':
                    # Log conflict for manual review
                    self._log_conflict(conflict, data)
                    # Don't sync this field
                    if field_name in resolved_data.get('values', {}):
                        del resolved_data['values'][field_name]

                elif resolution_strategy == 'merge_strategy':
                    # Implement intelligent merge (model-specific)
                    merged_value = self._merge_field_values(conflict)
                    if merged_value is not None:
                        resolved_data.setdefault('values', {})[field_name] = merged_value

            return resolved_data

        except Exception as e:
            _logger.error(f"Conflict resolution failed: {str(e)}")
            return None

    def _merge_field_values(self, conflict):
        """Merge conflicting field values intelligently"""
        try:
            field_name = conflict['field']
            old_value = conflict['old_value']
            current_value = conflict['current_value']

            # Simple merge strategies based on field type
            if isinstance(current_value, (list, tuple)) and isinstance(old_value, (list, tuple)):
                # For list fields, merge unique values
                merged = list(set(list(current_value) + list(old_value)))
                return merged

            elif isinstance(current_value, dict) and isinstance(old_value, dict):
                # For dict fields, merge dictionaries
                merged = old_value.copy()
                merged.update(current_value)
                return merged

            else:
                # For simple fields, keep current value
                return current_value

        except Exception as e:
            _logger.error(f"Field merge failed: {str(e)}")
            return None

    # Validation Methods

    def _validate_sync_data(self, model_name, data):
        """Validate data before synchronization"""
        try:
            validation_rules = self.data_validation_rules or {}

            # Check required fields
            required_fields = validation_rules.get('required_fields', {}).get(model_name, [])
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValidationError(f"Required field '{field}' is missing for {model_name}")

            # Check data types
            data_type_rules = validation_rules.get('data_types', {})
            for field_name, field_value in data.items():
                if field_name.endswith('_date') and field_value:
                    # Validate date format
                    if not self._validate_datetime_format(field_value):
                        raise ValidationError(f"Invalid date format for field '{field_name}'")

                elif field_name.endswith('_email') and field_value:
                    # Validate email format
                    if not self._validate_email_format(field_value):
                        raise ValidationError(f"Invalid email format for field '{field_name}'")

            return True

        except Exception as e:
            _logger.error(f"Data validation failed: {str(e)}")
            return False

    def _validate_datetime_format(self, value):
        """Validate datetime format"""
        try:
            if isinstance(value, str):
                datetime.fromisoformat(value.replace('Z', '+00:00'))
            return True
        except:
            return False

    def _validate_email_format(self, value):
        """Validate email format"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, value) is not None

    # Logging Methods

    def _log_sync_operation(self, operation_data):
        """Log synchronization operation"""
        logs = self.sync_log or []

        log_entry = {
            'timestamp': fields.Datetime.now().isoformat(),
            'operation': operation_data.get('operation', 'unknown'),
            'status': operation_data.get('status', 'unknown'),
            'duration': operation_data.get('duration', 0),
            'details': operation_data
        }

        logs.append(log_entry)

        # Keep only last 1000 log entries
        if len(logs) > 1000:
            logs = logs[-1000:]

        self.sync_log = logs

    def _log_conflict(self, conflict, data):
        """Log data conflict"""
        conflicts = self.conflict_log or []

        conflict_entry = {
            'timestamp': fields.Datetime.now().isoformat(),
            'conflict': conflict,
            'data': data,
            'resolution': 'pending'
        }

        conflicts.append(conflict_entry)

        # Keep only last 500 conflict entries
        if len(conflicts) > 500:
            conflicts = conflicts[-500:]

        self.conflict_log = conflicts

    def _log_sync_error(self, operation):
        """Log synchronization error"""
        errors = self.error_log or []

        error_entry = {
            'timestamp': fields.Datetime.now().isoformat(),
            'operation': operation,
            'retry_count': operation.get('retry_count', 0)
        }

        errors.append(error_entry)

        # Keep only last 200 error entries
        if len(errors) > 200:
            errors = errors[-200:]

        self.error_log = errors

    def _send_sync_event(self, event_type, data):
        """Send synchronization event to EventBus"""
        try:
            eventbus = self.env['bcm.eventbus.integration'].get_singleton()
            eventbus.send_message(event_type, {
                'sync_engine_id': self.id,
                'timestamp': fields.Datetime.now().isoformat(),
                'data': data
            })

        except Exception as e:
            _logger.error(f"Failed to send sync event: {str(e)}")

    # Immediate Processing

    def _process_sync_queue_immediate(self):
        """Process high-priority items immediately"""
        def process_immediate():
            try:
                sync_queue = self.sync_queue or []
                immediate_items = [
                    item for item in sync_queue
                    if item.get('priority') in ['critical', 'high'] and item.get('status') == 'pending'
                ]

                for item in immediate_items:
                    self._process_sync_operation(item)
                    item['status'] = 'completed'

                # Update queue
                self.sync_queue = sync_queue

            except Exception as e:
                _logger.error(f"Immediate sync processing failed: {str(e)}")

        # Run in background thread
        thread = threading.Thread(target=process_immediate)
        thread.daemon = True
        thread.start()

    # Action Methods

    def action_process_queue(self):
        """Action to manually process sync queue"""
        self.ensure_one()
        success = self.process_sync_queue()

        if success:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': f"Sync queue processed. {self.pending_sync_count} items remaining",
                    'type': 'success'
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error"),
                    'message': _("Failed to process sync queue"),
                    'type': 'danger'
                }
            }

    def action_clear_queue(self):
        """Action to clear sync queue"""
        self.ensure_one()
        self.sync_queue = []

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Sync queue cleared"),
                'type': 'info'
            }
        }

    def action_view_sync_logs(self):
        """Action to view sync logs"""
        self.ensure_one()

        return {
            'name': _('Synchronization Logs'),
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.data.sync.logs.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_engine_id': self.id,
                'sync_logs': self.sync_log,
                'conflict_logs': self.conflict_log,
                'error_logs': self.error_log
            }
        }

    # Cron Methods

    @api.model
    def cron_process_sync_queue(self):
        """Cron job to process sync queue"""
        engine = self.get_singleton()
        if engine.status == 'active' and engine.sync_mode in ['batch', 'hybrid']:
            engine.process_sync_queue()

    @api.model
    def cron_cleanup_logs(self):
        """Cron job to clean up old logs"""
        engine = self.get_singleton()

        try:
            # Clean up old sync logs (keep last 30 days)
            cutoff_date = (fields.Datetime.now() - timedelta(days=30)).isoformat()

            logs = engine.sync_log or []
            filtered_logs = [
                log for log in logs
                if log.get('timestamp', '') >= cutoff_date
            ]
            engine.sync_log = filtered_logs

            # Clean up old conflict logs (keep last 14 days)
            conflict_cutoff = (fields.Datetime.now() - timedelta(days=14)).isoformat()

            conflicts = engine.conflict_log or []
            filtered_conflicts = [
                conflict for conflict in conflicts
                if conflict.get('timestamp', '') >= conflict_cutoff
            ]
            engine.conflict_log = filtered_conflicts

            # Clean up old error logs (keep last 7 days)
            error_cutoff = (fields.Datetime.now() - timedelta(days=7)).isoformat()

            errors = engine.error_log or []
            filtered_errors = [
                error for error in errors
                if error.get('timestamp', '') >= error_cutoff
            ]
            engine.error_log = filtered_errors

        except Exception as e:
            _logger.error(f"Log cleanup failed: {str(e)}")

    # API Methods

    @api.model
    def api_queue_sync(self, operation_type, model_name, record_id, data=None, priority='medium'):
        """API endpoint to queue sync operation"""
        engine = self.get_singleton()
        return engine.queue_sync_operation(operation_type, model_name, record_id, data, priority)

    @api.model
    def api_trigger_sync(self, model_name=None, record_ids=None):
        """API endpoint to trigger immediate sync"""
        engine = self.get_singleton()

        if model_name and record_ids:
            # Queue specific records for sync
            for record_id in record_ids:
                engine.queue_sync_operation('update', model_name, record_id, priority='high')

        return engine.process_sync_queue()

    @api.model
    def api_get_sync_status(self):
        """API endpoint to get sync status"""
        engine = self.get_singleton()
        return {
            'status': engine.status,
            'pending_count': engine.pending_sync_count,
            'success_rate': engine.sync_success_rate,
            'last_sync': engine.last_sync.isoformat() if engine.last_sync else None
        }