# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class BCMKPICalculator(models.Model):
    _name = 'bcm.kpi.calculator'
    _description = 'BCM KPI Calculator'
    _inherit = ['bcm.webhook.mixin', 'bcm.company.mixin']
    
    name = fields.Char('KPI Period', required=True, default=lambda self: datetime.now().strftime('Q%q %Y'))
    date_from = fields.Date('From Date', required=True, default=fields.Date.today)
    date_to = fields.Date('To Date', required=True, default=fields.Date.today)
    
    # KPI Values
    bia_coverage = fields.Float('BIA Coverage (%)', compute='_compute_kpis', store=True)
    plans_up_to_date = fields.Float('Plans Up-to-date (%)', compute='_compute_kpis', store=True)
    capa_on_time = fields.Float('CAPA On-time (%)', compute='_compute_kpis', store=True)
    
    # Additional KPIs
    incident_response_time = fields.Float('Avg Incident Response (hours)', compute='_compute_kpis', store=True)
    exercise_completion = fields.Float('Exercise Completion (%)', compute='_compute_kpis', store=True)
    training_completion = fields.Float('Training Completion (%)', compute='_compute_kpis', store=True)
    
    @api.depends('date_from', 'date_to', 'company_id')
    def _compute_kpis(self):
        for record in self:
            # BIA Coverage
            total_processes = self.env['bcm.process'].search_count([
                ('company_id', '=', record.company_id.id)
            ])
            covered_processes = self.env['bcm.process'].search_count([
                ('company_id', '=', record.company_id.id),
                ('bia_id', '!=', False)
            ])
            record.bia_coverage = (covered_processes / total_processes * 100) if total_processes else 0
            
            # Plans Up-to-date (updated within last 6 months)
            six_months_ago = datetime.now() - timedelta(days=180)
            total_plans = self.env['bcm.plan'].search_count([
                ('company_id', '=', record.company_id.id)
            ])
            current_plans = self.env['bcm.plan'].search_count([
                ('company_id', '=', record.company_id.id),
                ('write_date', '>=', six_months_ago)
            ])
            record.plans_up_to_date = (current_plans / total_plans * 100) if total_plans else 0
            
            # CAPA On-time
            total_capa = self.env['bcm.capa'].search_count([
                ('company_id', '=', record.company_id.id),
                ('create_date', '>=', record.date_from),
                ('create_date', '<=', record.date_to)
            ])
            ontime_capa = self.env['bcm.capa'].search_count([
                ('company_id', '=', record.company_id.id),
                ('create_date', '>=', record.date_from),
                ('create_date', '<=', record.date_to),
                ('state', '=', 'completed'),
                ('completion_date', '<=', 'target_date')
            ])
            record.capa_on_time = (ontime_capa / total_capa * 100) if total_capa else 100
            
            # Incident Response Time
            incidents = self.env['bcm.incident'].search([
                ('company_id', '=', record.company_id.id),
                ('create_date', '>=', record.date_from),
                ('create_date', '<=', record.date_to)
            ])
            if incidents:
                total_response_time = sum([
                    (inc.response_date - inc.create_date).total_seconds() / 3600
                    for inc in incidents if inc.response_date
                ])
                record.incident_response_time = total_response_time / len(incidents)
            else:
                record.incident_response_time = 0
            
            # Exercise Completion
            total_exercises = self.env['bcm.exercise.management'].search_count([
                ('company_id', '=', record.company_id.id),
                ('planned_date', '>=', record.date_from),
                ('planned_date', '<=', record.date_to)
            ])
            completed_exercises = self.env['bcm.exercise.management'].search_count([
                ('company_id', '=', record.company_id.id),
                ('planned_date', '>=', record.date_from),
                ('planned_date', '<=', record.date_to),
                ('state', '=', 'completed')
            ])
            record.exercise_completion = (completed_exercises / total_exercises * 100) if total_exercises else 0
            
            # Training Completion
            total_training = self.env['bcm.training'].search_count([
                ('company_id', '=', record.company_id.id),
                ('scheduled_date', '>=', record.date_from),
                ('scheduled_date', '<=', record.date_to)
            ])
            completed_training = self.env['bcm.training'].search_count([
                ('company_id', '=', record.company_id.id),
                ('scheduled_date', '>=', record.date_from),
                ('scheduled_date', '<=', record.date_to),
                ('state', '=', 'completed')
            ])
            record.training_completion = (completed_training / total_training * 100) if total_training else 0
    
    def action_calculate_kpis(self):
        """Manually trigger KPI calculation"""
        self._compute_kpis()
        
        # Send event to EventBus
        self.send_event_to_eventbus('bcm.kpi.calculated', {
            'period': self.name,
            'bia_coverage': self.bia_coverage,
            'plans_up_to_date': self.plans_up_to_date,
            'capa_on_time': self.capa_on_time,
            'incident_response_time': self.incident_response_time,
            'exercise_completion': self.exercise_completion,
            'training_completion': self.training_completion
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('KPIs Calculated'),
                'message': _(f'BIA Coverage: {self.bia_coverage:.1f}%, Plans Current: {self.plans_up_to_date:.1f}%, CAPA On-time: {self.capa_on_time:.1f}%'),
                'type': 'info',
                'sticky': False,
            }
        }
    
    @api.model
    def get_current_kpis(self):
        """API endpoint for frontend to get current KPIs"""
        current_kpi = self.search([('company_id', '=', self.env.company.id)], limit=1, order='create_date desc')
        if not current_kpi:
            # Create new KPI record for current quarter
            current_kpi = self.create({
                'name': datetime.now().strftime('Q%q %Y'),
                'date_from': datetime.now().replace(day=1),
                'date_to': datetime.now()
            })
        
        return {
            'bia_coverage': current_kpi.bia_coverage,
            'plans_up_to_date': current_kpi.plans_up_to_date,
            'capa_on_time': current_kpi.capa_on_time,
            'incident_response_time': current_kpi.incident_response_time,
            'exercise_completion': current_kpi.exercise_completion,
            'training_completion': current_kpi.training_completion,
            'period': current_kpi.name
        }
