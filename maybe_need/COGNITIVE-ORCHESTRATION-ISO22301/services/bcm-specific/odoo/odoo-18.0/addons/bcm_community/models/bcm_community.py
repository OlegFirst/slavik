from odoo import models, fields, api

class BcmCommunity(models.Model):
    _name = 'bcm.community'
    _description = 'BCM Community Base Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True, tracking=True)
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)

    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company
    )