# -*- coding: utf-8 -*-

from . import models
from . import controllers

from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    """Post-installation hook to set up initial BCM configurations"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Create default BCM configuration
    env['ir.config_parameter'].sudo().set_param('bcm.platform.version', '18.0.1.0.0')
    env['ir.config_parameter'].sudo().set_param('bcm.iso22301.enabled', 'True')
    env['ir.config_parameter'].sudo().set_param('bcm.multitenancy.enabled', 'True')
    
    # Initialize BCM sequences
    env['ir.sequence'].sudo().create({
        'name': 'BCM Organization Code',
        'code': 'bcm.organization',
        'prefix': 'ORG/',
        'padding': 5,
        'company_id': False,
    })

def uninstall_hook(cr, registry):
    """Uninstall hook to clean up BCM configurations"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Clean up configuration parameters
    env['ir.config_parameter'].sudo().search([
        ('key', 'like', 'bcm.%')
    ]).unlink()
