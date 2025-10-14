# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BCMIntelligentBase(models.AbstractModel):
    """Base model for BCM intelligent features"""
    _name = 'bcm.intelligent.base'
    _description = 'BCM Intelligent Base'
    
    ai_enabled = fields.Boolean('AI Enabled', default=False)
    ai_score = fields.Float('AI Score', digits=(16, 2))
    ai_recommendations = fields.Text('AI Recommendations')
    ai_last_analysis = fields.Datetime('Last AI Analysis')
    
    @api.model
    def ai_analyze(self):
        """Base method for AI analysis"""
        return True