# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CorporateTwin(models.Model):
    """Corporate Digital Twin - Virtual representation of organization"""
    _name = 'bcm.corporate.twin'
    _description = 'Corporate Digital Twin'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Organization Name', required=True)
    code = fields.Char('Organization Code', required=True)
    active = fields.Boolean('Active', default=True)

    # Organization Structure
    parent_id = fields.Many2one('bcm.corporate.twin', 'Parent Organization')
    child_ids = fields.One2many('bcm.corporate.twin', 'parent_id', 'Subsidiaries')

    # Digital Twin Configuration
    twin_type = fields.Selection([
        ('headquarters', 'Headquarters'),
        ('subsidiary', 'Subsidiary'),
        ('branch', 'Branch'),
        ('department', 'Department'),
        ('business_unit', 'Business Unit')
    ], string='Organization Type', default='headquarters')

    # Simulation Parameters
    simulation_enabled = fields.Boolean('Enable Simulation', default=True)
    real_time_sync = fields.Boolean('Real-time Synchronization', default=False)
    last_sync = fields.Datetime('Last Synchronization')

    # KPIs and Metrics
    resilience_score = fields.Float('Resilience Score', compute='_compute_resilience_score')
    maturity_level = fields.Selection([
        ('initial', 'Initial'),
        ('developing', 'Developing'),
        ('established', 'Established'),
        ('predictive', 'Predictive'),
        ('optimizing', 'Optimizing')
    ], string='BCM Maturity Level', default='initial')

    # Integration Points
    digital_twin_core_id = fields.Many2one('digital.twin.organization', 'Digital Twin Core')

    @api.depends('name')
    def _compute_resilience_score(self):
        for record in self:
            # Simple calculation for now
            record.resilience_score = 75.0

    def action_sync_twin(self):
        """Synchronize with digital twin core"""
        self.last_sync = fields.Datetime.now()
        return True

    def action_run_simulation(self):
        """Run corporate simulation"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Simulation Started',
                'message': f'Running simulation for {self.name}',
                'type': 'success',
            }
        }