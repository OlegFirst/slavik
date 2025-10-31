from odoo import models, fields, api, _

class BcmRiskManagement(models.Model):
    _name = 'bcm.risk.management'
    _description = 'BCM Risk Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    description = fields.Text('Description', tracking=True)
    active = fields.Boolean(default=True)
    risk_score = fields.Float('Risk Score', default=0.0, tracking=True)
    ai_analysis = fields.Text('AI Analysis Result')

    # Risk assessment fields
    risk_category = fields.Selection([
        ('operational', 'Operational'),
        ('financial', 'Financial'),
        ('strategic', 'Strategic'),
        ('compliance', 'Compliance'),
        ('reputational', 'Reputational'),
    ], string='Risk Category', default='operational', tracking=True)

    likelihood = fields.Selection([
        ('rare', 'Rare'),
        ('unlikely', 'Unlikely'),
        ('possible', 'Possible'),
        ('likely', 'Likely'),
        ('almost_certain', 'Almost Certain'),
    ], string='Likelihood', default='possible', tracking=True)

    impact = fields.Selection([
        ('insignificant', 'Insignificant'),
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('catastrophic', 'Catastrophic'),
    ], string='Impact', default='moderate', tracking=True)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_ai_risk_analysis(self):
        """Perform AI risk analysis"""
        self.ensure_one()
        # Placeholder for AI risk analysis functionality
        self.risk_score = 75.0  # Demo value
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('AI Risk Analysis'),
                'message': _('Risk analysis completed. Score: %.1f') % self.risk_score,
                'type': 'success',
                'sticky': False,
            }
        }