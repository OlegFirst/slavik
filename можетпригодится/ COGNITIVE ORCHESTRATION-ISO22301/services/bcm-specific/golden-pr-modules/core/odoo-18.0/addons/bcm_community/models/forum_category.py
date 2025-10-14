from odoo import models, fields

class BcmForumCategory(models.Model):
    _name = 'bcm.forum.category'
    _description = 'BCM Forum Category'
    _order = 'sequence, name'

    name = fields.Char('Category Name', required=True)
    code = fields.Char('Category Code', required=True)
    description = fields.Text('Description')

    # Visual
    icon = fields.Char('Icon Class', default='fas fa-comments')
    color = fields.Char('Color', default='#6c757d')
    sequence = fields.Integer('Sequence', default=10)

    # Relations
    topic_count = fields.Integer('Topic Count', default=0)

    # Scenario integration
    is_scenario_category = fields.Boolean('Scenario Category', default=False)
    auto_create_for_scenarios = fields.Boolean('Auto Create for Scenarios', default=False)

    # Status
    active = fields.Boolean('Active', default=True)

    # Multi-tenancy
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
