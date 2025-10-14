# -*- coding: utf-8 -*-

from . import models
from . import controllers

def post_init_hook(env):
    """Post-installation hook для настройки мультитенантности"""
    
    # Создать базовые роли безопасности если их нет
    bcm_client_model = env['ir.model'].search([('model', '=', 'bcm.client')])
    if bcm_client_model:
        env['ir.model.access'].create({
            'name': 'BCM Client Multi-tenant Access',
            'model_id': bcm_client_model.id,
            'perm_read': True,
            'perm_write': True,
            'perm_create': True,
            'perm_unlink': False,
        })
