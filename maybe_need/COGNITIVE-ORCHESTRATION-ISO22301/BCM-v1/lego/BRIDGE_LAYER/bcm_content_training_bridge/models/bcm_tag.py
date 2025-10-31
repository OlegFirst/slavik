# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class BcmTag(models.Model):
    _name = 'bcm.tag'
    _description = 'BCM Scenario Tags'
    _order = 'name asc'
    _rec_name = 'name'
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Tag name must be unique!')
    ]
    
    name = fields.Char(
        string='Tag Name',
        required=True, index=True,
        help='Name of the tag'
    )
    
    description = fields.Text(
        string='Description',
        help='Description of what this tag represents'
    )
    
    color = fields.Integer(
        string='Color',
        default=0,
        help='Color for tag display'
    )
    
    # Multi-tenancy
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        index=True,
        default=lambda self: self.env.company
    )
    
    # Статистика использования
    scenario_count = fields.Integer(
        compute='_compute_scenario_count',
        string='Scenario Count',
        help='Number of scenarios using this tag'
    )
    
    # Метаданные
    active = fields.Boolean(default=True)
    
    create_uid = fields.Many2one('res.users', string='Created by')
    create_date = fields.Datetime(string='Created on')
    
    @api.depends('name')
    def _compute_scenario_count(self):
        for tag in self:
            tag.scenario_count = self.env['bcm.scenario'].search_count([
                ('tags', 'in', [tag.id])
            ])
    
    @api.model
    def get_popular_tags(self, limit=20):
        """Получить популярные теги"""
        # Получить теги отсортированные по количеству использований
        tags = self.search([])
        
        # Подсчитать использование и отсортировать
        tag_usage = []
        for tag in tags:
            count = self.env['bcm.scenario'].search_count([
                ('tags', 'in', [tag.id]),
                ('status', '=', 'published')
            ])
            if count > 0:
                tag_usage.append((tag, count))
        
        # Сортировать по количеству использований
        tag_usage.sort(key=lambda x: x[1], reverse=True)
        
        return [tag for tag, count in tag_usage[:limit]]
    
    @api.model
    def create_if_not_exists(self, tag_names):
        """Создать теги если они не существуют"""
        if isinstance(tag_names, str):
            tag_names = [tag_names]
        
        existing_tags = self.search([('name', 'in', tag_names)])
        existing_names = existing_tags.mapped('name')
        
        new_tags = []
        for name in tag_names:
            if name not in existing_names:
                new_tag = self.create({'name': name})
                new_tags.append(new_tag)
        
        return existing_tags + self.browse([tag.id for tag in new_tags])
    
    def action_view_scenarios(self):
        """Показать сценарии с этим тегом"""
        self.ensure_one()
        
        return {
            'name': _('Scenarios with tag: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'bcm.scenario',
            'view_mode': 'list,form',
            'domain': [('tags', 'in', [self.id])],
            'context': {'search_default_published': 1}
        }
