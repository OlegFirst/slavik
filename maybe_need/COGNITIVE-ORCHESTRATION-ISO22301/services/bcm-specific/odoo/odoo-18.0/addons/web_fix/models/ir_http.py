# -*- coding: utf-8 -*-
from odoo import models

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def get_frontend_session_info(self):
        """Compatibility method for Odoo 18.0 templates"""
        return {
            'is_admin': self.env.user._is_admin(),
            'is_system': self.env.user._is_system(),
            'is_public': self.env.user._is_public(),
            'is_employee': self.env.user.has_group('base.group_user'),
            'user_id': self.env.user.id,
            'bundle_params': {
                'lang': self.env.lang,
                'debug': self.env.context.get('debug', ''),
            },
        }