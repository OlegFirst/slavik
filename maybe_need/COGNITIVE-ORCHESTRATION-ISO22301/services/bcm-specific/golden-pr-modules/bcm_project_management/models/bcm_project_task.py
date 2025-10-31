# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class BCMProjectTask(models.Model):
    _inherit = 'project.task'
    _description = 'BCM Enhanced Task'

    # BCM specific fields
    bcm_task_type = fields.Selection([
        ('assessment', 'Assessment'),
        ('implementation', 'Implementation'),
        ('testing', 'Testing'),
        ('documentation', 'Documentation'),
        ('training', 'Training'),
        ('review', 'Review'),
    ], string='BCM Task Type')

    criticality = fields.Selection([
        ('immediate', 'Immediate Action'),
        ('urgent', 'Urgent'),
        ('normal', 'Normal'),
        ('low', 'Low Priority'),
    ], string='Criticality', default='normal')

    # Recovery specific
    recovery_sequence = fields.Integer('Recovery Sequence',
        help='Order in which this task should be executed during recovery')

    dependency_ids = fields.Many2many(
        'project.task',
        'bcm_task_dependencies',
        'task_id',
        'depends_on_id',
        string='Dependencies',
        help='Tasks that must be completed before this one'
    )

    # AI fields
    ai_complexity_score = fields.Float('AI Complexity Score', readonly=True)
    ai_estimated_hours = fields.Float('AI Estimated Hours')
    smart_assignee_id = fields.Many2one('res.users', 'AI Suggested Assignee',
        compute='_compute_smart_assignee')

    # Risk association
    risk_ids = fields.Many2many('bcm.risk', string='Associated Risks')

    # Automation
    auto_escalate = fields.Boolean('Auto Escalate', default=True)
    escalation_level = fields.Integer('Escalation Level', default=0)

    @api.depends('name', 'project_id.user_id', 'planned_hours')
    def _compute_smart_assignee(self):
        """AI-powered assignee suggestion"""
        for task in self:
            # Simple logic for now - would use AI in production
            if task.project_id.auto_assign:
                task.smart_assignee_id = task.project_id._find_best_assignee_for_task(task.name)
            else:
                task.smart_assignee_id = False

    @api.model
    def create(self, vals):
        """Enhanced task creation with BCM logic"""
        task = super().create(vals)

        # Auto-assign if enabled
        if task.project_id.auto_assign and not task.user_ids:
            if task.smart_assignee_id:
                task.user_ids = [(4, task.smart_assignee_id.id)]

        return task

    def action_start_task(self):
        """Quick action to start working on task"""
        self.ensure_one()
        self.write({
            'stage_id': self._get_in_progress_stage().id,
            'date_begin': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Task Started'),
                'message': _('Task "%s" is now in progress') % self.name,
                'type': 'success',
            }
        }

    def _get_in_progress_stage(self):
        """Get the 'In Progress' stage"""
        return self.env['project.task.type'].search([
            ('project_ids', 'in', self.project_id.id),
            ('name', 'ilike', 'progress'),
        ], limit=1) or self.env['project.task.type'].search([
            ('project_ids', 'in', self.project_id.id),
        ], limit=1)