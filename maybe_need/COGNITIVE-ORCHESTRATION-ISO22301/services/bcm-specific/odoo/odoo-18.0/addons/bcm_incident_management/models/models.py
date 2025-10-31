from odoo import models, fields

class BcmIncidentManagement(models.Model):
    _name = 'bcm.incident.management'
    _description = 'BCM Incident Management'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    description = fields.Text()
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True, index=True,
        default=lambda self: self.env.company,
    )