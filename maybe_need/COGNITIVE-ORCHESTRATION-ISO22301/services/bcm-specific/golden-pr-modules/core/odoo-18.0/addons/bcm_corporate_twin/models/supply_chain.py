# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CorporateSupplyChain(models.Model):
    """Supply chain analysis for corporate digital twin"""
    _name = 'bcm.corporate.supply_chain'
    _description = 'Corporate Supply Chain Analysis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char('Supply Chain Name', required=True)
    corporate_twin_id = fields.Many2one('bcm.corporate.twin', 'Corporate Twin', required=True)
    active = fields.Boolean('Active', default=True)

    # Supplier Information
    supplier_name = fields.Char('Supplier Name')
    supplier_category = fields.Selection([
        ('critical', 'Critical'),
        ('important', 'Important'),
        ('standard', 'Standard'),
        ('backup', 'Backup')
    ], string='Supplier Category', default='standard')

    supplier_location = fields.Char('Supplier Location')
    supplier_country_id = fields.Many2one('res.country', 'Supplier Country')

    # Dependencies
    dependency_level = fields.Selection([
        ('high', 'High Dependency'),
        ('medium', 'Medium Dependency'),
        ('low', 'Low Dependency')
    ], string='Dependency Level', default='medium')

    single_point_failure = fields.Boolean('Single Point of Failure')
    alternative_suppliers = fields.Integer('Number of Alternatives')
    switching_time_days = fields.Integer('Switching Time (Days)')

    # Inventory
    inventory_type = fields.Selection([
        ('raw_material', 'Raw Materials'),
        ('work_in_progress', 'Work in Progress'),
        ('finished_goods', 'Finished Goods'),
        ('spare_parts', 'Spare Parts')
    ], string='Inventory Type')

    current_stock_level = fields.Float('Current Stock Level')
    minimum_stock_level = fields.Float('Minimum Stock Level')
    maximum_stock_level = fields.Float('Maximum Stock Level')
    stock_coverage_days = fields.Integer('Stock Coverage (Days)')

    # Logistics
    transport_mode = fields.Selection([
        ('air', 'Air Freight'),
        ('sea', 'Sea Freight'),
        ('road', 'Road Transport'),
        ('rail', 'Rail Transport'),
        ('multimodal', 'Multimodal')
    ], string='Primary Transport Mode')

    lead_time_days = fields.Integer('Lead Time (Days)')
    transit_time_days = fields.Integer('Transit Time (Days)')
    customs_clearance_days = fields.Integer('Customs Clearance (Days)')

    # Risk Assessment
    disruption_probability = fields.Selection([
        ('very_low', 'Very Low (< 5%)'),
        ('low', 'Low (5-20%)'),
        ('medium', 'Medium (20-50%)'),
        ('high', 'High (50-80%)'),
        ('very_high', 'Very High (> 80%)')
    ], string='Disruption Probability')

    impact_severity = fields.Selection([
        ('negligible', 'Negligible'),
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('catastrophic', 'Catastrophic')
    ], string='Impact Severity')

    # Resilience Metrics
    supply_chain_resilience_score = fields.Float('Resilience Score', compute='_compute_resilience_score')
    recovery_strategy = fields.Text('Recovery Strategy')
    contingency_plan_id = fields.Many2one('bcm.plans', 'Contingency Plan')

    # Simulation Results
    last_simulation_date = fields.Datetime('Last Simulation')
    simulation_result = fields.Text('Simulation Results')

    @api.depends('dependency_level', 'alternative_suppliers', 'single_point_failure')
    def _compute_resilience_score(self):
        for record in self:
            score = 50.0  # Base score

            # Dependency factor
            if record.dependency_level == 'low':
                score += 20
            elif record.dependency_level == 'medium':
                score += 10
            elif record.dependency_level == 'high':
                score -= 10

            # Alternative suppliers factor
            if record.alternative_suppliers > 3:
                score += 20
            elif record.alternative_suppliers > 1:
                score += 10
            elif record.alternative_suppliers == 1:
                score += 5

            # Single point of failure factor
            if record.single_point_failure:
                score -= 20
            else:
                score += 10

            # Stock coverage factor
            if record.stock_coverage_days > 30:
                score += 10
            elif record.stock_coverage_days > 14:
                score += 5

            record.supply_chain_resilience_score = max(0, min(score, 100))

    def action_simulate_disruption(self):
        """Simulate supply chain disruption"""
        self.ensure_one()

        # Simple simulation logic
        impact_levels = {
            'negligible': 0.95,
            'minor': 0.85,
            'moderate': 0.70,
            'major': 0.50,
            'catastrophic': 0.20
        }

        impact_factor = impact_levels.get(self.impact_severity, 1.0)

        result = f"""Supply Chain Disruption Simulation:
        Supplier: {self.supplier_name}
        Category: {self.supplier_category}
        Dependency Level: {self.dependency_level}

        Disruption Impact:
        - Stock Coverage: {self.stock_coverage_days * impact_factor:.0f} days
        - Alternative Suppliers: {self.alternative_suppliers}
        - Switching Time: {self.switching_time_days} days
        - Recovery Time Estimate: {self.lead_time_days + self.switching_time_days} days

        Resilience Score: {self.supply_chain_resilience_score:.1f}/100

        Recommendations:
        - {"Add alternative suppliers" if self.alternative_suppliers < 2 else "Alternative suppliers available"}
        - {"Increase stock levels" if self.stock_coverage_days < 14 else "Stock levels adequate"}
        - {"Develop contingency plan" if not self.contingency_plan_id else "Contingency plan in place"}
        """

        self.simulation_result = result
        self.last_simulation_date = fields.Datetime.now()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Disruption Simulation Complete',
                'message': f'Supply chain simulation completed for {self.name}',
                'type': 'success',
            }
        }

    def action_analyze_alternatives(self):
        """Analyze alternative suppliers"""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Alternative Analysis',
                'message': 'Analyzing alternative suppliers and routes',
                'type': 'info',
            }
        }