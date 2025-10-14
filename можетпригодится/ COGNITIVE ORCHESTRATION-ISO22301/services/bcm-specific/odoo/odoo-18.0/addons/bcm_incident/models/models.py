from odoo import models, fields

class BcmIncident(models.Model):
    _name = 'bcm.incident'
    _description = 'BCM Incident'

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

class BcmIncidentRecord(models.Model):
    _name = 'bcm_incident.record'
    _description = 'BCM Incident Record with Multi-tenancy'

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
