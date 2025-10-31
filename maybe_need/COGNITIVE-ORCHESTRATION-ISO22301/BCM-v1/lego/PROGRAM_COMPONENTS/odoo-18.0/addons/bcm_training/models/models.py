from odoo import models, fields

class BcmTrainingRecord(models.Model):
    _name = 'bcm.training'
    _description = 'BCM Training Record with Multi-tenancy'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    notes = fields.Text()
    
    # Multi-tenancy field
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company,
        help='Company/tenant isolation'
    )
