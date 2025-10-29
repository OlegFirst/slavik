# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class BcmDomain(models.Model):
    _name = 'bcm.domain'
    _description = 'BCM Business Domains'
    _order = 'sequence, name asc'
    _rec_name = 'name'
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Domain name must be unique!')
    ]
    
    name = fields.Char(
        string='Domain Name',
        required=True, index=True,
        help='Name of the business domain (e.g., IT, Healthcare, Manufacturing)'
    )
    
    description = fields.Text(
        string='Description',
        help='Description of this business domain'
    )
    
    code = fields.Char(
        string='Domain Code',
        help='Short code for the domain (e.g., IT, HC, MFG)'
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of display'
    )
    
    icon = fields.Char(
        string='Icon Class',
        help='CSS icon class for display'
    )
    
    color = fields.Char(
        string='Color',
        default='#3498db',
        help='Color for domain representation'
    )
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        index=True,
        default=lambda self: self.env.company
    )
    
    # Статистика
    scenario_count = fields.Integer(
        compute='_compute_scenario_count',
        string='Scenario Count',
        help='Number of scenarios in this domain'
    )
    
    # Категоризация
    parent_id = fields.Many2one(
        'bcm.domain',
        string='Parent Domain',
        help='Parent domain for hierarchical organization'
    )
    
    child_ids = fields.One2many(
        'bcm.domain',
        'parent_id',
        string='Child Domains'
    )
    
    # Метаданные
    active = fields.Boolean(default=True)
    
    @api.depends('name')
    def _compute_scenario_count(self):
        for domain in self:
            domain.scenario_count = self.env['bcm.scenario'].search_count([
                ('domains', 'in', [domain.id])
            ])
    
    @api.model
    def get_domain_hierarchy(self):
        """Получить иерархию доменов"""
        root_domains = self.search([('parent_id', '=', False)])
        
        def build_tree(domains):
            result = []
            for domain in domains:
                node = {
                    'id': domain.id,
                    'name': domain.name,
                    'code': domain.code,
                    'scenario_count': domain.scenario_count,
                    'children': build_tree(domain.child_ids)
                }
                result.append(node)
            return result
        
        return build_tree(root_domains)
    
    def action_view_scenarios(self):
        """Показать сценарии этого домена"""
        self.ensure_one()
        
        return {
            'name': _('Scenarios for domain: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.scenario',
            'view_mode': 'list,form',
            'domain': [('domains', 'in', [self.id])],
            'context': {'search_default_published': 1}
        }
