from odoo import models, fields

class BcmExpertBadge(models.Model):
    _name = 'bcm.expert.badge'
    _description = 'Expert Badge'

    name = fields.Char('Badge Name', required=True)
    code = fields.Char('Badge Code', required=True)
    description = fields.Text('Description')

    # Visual
    icon = fields.Char('Icon Class', default='fas fa-star')
    color = fields.Char('Color', default='#6c757d')

    # Requirements
    points_required = fields.Integer('Points Required', default=0)

    # Status
    active = fields.Boolean('Active', default=True)

    # Multi-tenancy
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)