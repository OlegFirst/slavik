# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class BCMBase(models.AbstractModel):
    """Abstract base model for all BCM modules providing common functionality"""
    _name = 'bcm.base'
    _description = 'BCM Base Abstract Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # Common fields for all BCM models
    active = fields.Boolean(default=True, tracking=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        index=True,
        default=lambda self: self.env.company
    )
    
    # ISO 22301 compliance tracking
    iso_clause = fields.Char(
        string='ISO 22301 Clause',
        help='Related ISO 22301 clause number'
    )
    compliance_status = fields.Selection([
        ('compliant', 'Compliant'),
        ('partial', 'Partially Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('not_applicable', 'Not Applicable')
    ], string='Compliance Status', default='partial', tracking=True)
    
    # Audit trail
    created_by = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )
    last_review_date = fields.Datetime(
        string='Last Review Date',
        tracking=True
    )
    next_review_date = fields.Date(
        string='Next Review Date',
        tracking=True
    )
    
    # Risk level for all BCM components
    risk_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Risk Level', default='medium', tracking=True)
    
    # Tags for categorization
    tag_ids = fields.Many2many(
        'bcm.tag',
        string='Tags',
        help='Tags for categorization and filtering'
    )
    
    @api.model
    def _check_multitenancy(self):
        """Ensure data isolation between companies"""
        if self.env['ir.config_parameter'].sudo().get_param('bcm.multitenancy.enabled') == 'True':
            domain = [('company_id', '=', self.env.company.id)]
            return domain
        return []
    
    @api.model
    def create(self, vals):
        """Override create to add audit logging"""
        res = super().create(vals)
        _logger.info(f"BCM Record created: {self._name} ID: {res.id} by User: {self.env.user.name}")
        return res
    
    def write(self, vals):
        """Override write to add audit logging"""
        res = super().write(vals)
        for record in self:
            _logger.info(f"BCM Record updated: {self._name} ID: {record.id} by User: {self.env.user.name}")
        return res
    
    def unlink(self):
        """Override unlink to add audit logging"""
        for record in self:
            _logger.warning(f"BCM Record deleted: {self._name} ID: {record.id} by User: {self.env.user.name}")
        return super().unlink()
    
    @api.constrains('next_review_date', 'last_review_date')
    def _check_review_dates(self):
        """Ensure next review date is after last review date"""
        for record in self:
            if record.next_review_date and record.last_review_date:
                if fields.Date.to_date(record.next_review_date) <= fields.Date.to_date(record.last_review_date):
                    raise ValidationError(_("Next review date must be after last review date"))
    
    def action_mark_reviewed(self):
        """Mark record as reviewed and set next review date"""
        for record in self:
            record.last_review_date = fields.Datetime.now()
            # Set next review date to 1 year from now by default
            from datetime import timedelta
            record.next_review_date = fields.Date.today() + timedelta(days=365)
        return True


class BCMTag(models.Model):
    """Tags for categorizing BCM records"""
    _name = 'bcm.tag'
    _description = 'BCM Tag'
    _order = 'name'
    
    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color Index')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Tag name must be unique!')
    ]
