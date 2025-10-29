# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

class CorporateFinancialModel(models.Model):
    """Financial modeling for corporate digital twin"""
    _name = 'bcm.corporate.financial'
    _description = 'Corporate Financial Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char('Model Name', required=True)
    corporate_twin_id = fields.Many2one('bcm.corporate.twin', 'Corporate Twin', required=True)
    active = fields.Boolean('Active', default=True)

    # Cash Flow Analysis
    cash_flow_type = fields.Selection([
        ('operational', 'Operational'),
        ('investment', 'Investment'),
        ('financing', 'Financing'),
        ('emergency', 'Emergency Reserve')
    ], string='Cash Flow Type', default='operational')

    current_cash_position = fields.Monetary('Current Cash Position', currency_field='currency_id')
    projected_cash_flow = fields.Monetary('Projected Cash Flow (30 days)', currency_field='currency_id')
    minimum_cash_requirement = fields.Monetary('Minimum Cash Requirement', currency_field='currency_id')
    emergency_fund = fields.Monetary('Emergency Fund', currency_field='currency_id')

    # Revenue Impact
    revenue_baseline = fields.Monetary('Revenue Baseline', currency_field='currency_id')
    revenue_at_risk = fields.Monetary('Revenue at Risk', currency_field='currency_id')
    recovery_time_days = fields.Integer('Recovery Time (Days)')

    # Budget Allocation
    bcm_budget = fields.Monetary('BCM Budget', currency_field='currency_id')
    insurance_coverage = fields.Monetary('Insurance Coverage', currency_field='currency_id')
    contingency_budget = fields.Monetary('Contingency Budget', currency_field='currency_id')

    # Financial Metrics
    rto_cost_per_hour = fields.Monetary('RTO Cost per Hour', currency_field='currency_id')
    rpo_data_value = fields.Monetary('RPO Data Value', currency_field='currency_id')
    downtime_cost_per_hour = fields.Monetary('Downtime Cost per Hour', currency_field='currency_id')

    # Stress Testing
    stress_test_scenario = fields.Selection([
        ('mild', 'Mild Disruption (1-3 days)'),
        ('moderate', 'Moderate Disruption (3-7 days)'),
        ('severe', 'Severe Disruption (7-30 days)'),
        ('extreme', 'Extreme Disruption (30+ days)')
    ], string='Stress Test Scenario')

    stress_test_result = fields.Text('Stress Test Results')
    financial_resilience_score = fields.Float('Financial Resilience Score', compute='_compute_resilience_score')

    # Currency
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company)

    @api.depends('cash_flow_type', 'current_cash_position', 'minimum_cash_requirement')
    def _compute_resilience_score(self):
        for record in self:
            score = 50.0  # Base score
            if record.current_cash_position and record.minimum_cash_requirement:
                ratio = record.current_cash_position / record.minimum_cash_requirement
                if ratio > 2:
                    score += 30
                elif ratio > 1.5:
                    score += 20
                elif ratio > 1:
                    score += 10

            if record.emergency_fund:
                score += 10

            if record.insurance_coverage:
                score += 10

            record.financial_resilience_score = min(score, 100.0)

    def action_run_stress_test(self):
        """Run financial stress test simulation"""
        self.ensure_one()

        # Simple stress test logic
        scenarios = {
            'mild': 0.95,
            'moderate': 0.85,
            'severe': 0.70,
            'extreme': 0.50
        }

        impact_factor = scenarios.get(self.stress_test_scenario, 1.0)
        projected_revenue = self.revenue_baseline * impact_factor
        revenue_loss = self.revenue_baseline - projected_revenue

        result = f"""Stress Test Results for {self.stress_test_scenario} scenario:
        - Projected Revenue: {projected_revenue:,.2f}
        - Expected Revenue Loss: {revenue_loss:,.2f}
        - Recovery Time: {self.recovery_time_days} days
        - Cash Flow Impact: {self.projected_cash_flow * impact_factor:,.2f}
        - Financial Resilience Score: {self.financial_resilience_score:.1f}/100
        """

        self.stress_test_result = result

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Stress Test Complete',
                'message': f'Financial stress test completed for {self.name}',
                'type': 'success',
            }
        }

    def action_optimize_budget(self):
        """Optimize BCM budget allocation"""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Budget Optimization',
                'message': 'Budget optimization analysis started',
                'type': 'info',
            }
        }