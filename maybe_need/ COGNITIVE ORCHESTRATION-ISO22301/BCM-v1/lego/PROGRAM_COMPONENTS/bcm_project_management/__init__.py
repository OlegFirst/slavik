# -*- coding: utf-8 -*-

from . import models
from . import wizard
from . import controllers

def post_init_hook(cr, registry):
    """
    Post-installation hook to set up default BCM project configuration
    """
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    # Create default BCM project stages if they don't exist
    env['bcm.project.configurator'].sudo().setup_default_configuration()

    # Set up default automation rules
    env['bcm.automation.setup'].sudo().create_default_automations()

    # Initialize AI connector if available
    try:
        env['bcm.ai.connector'].sudo().test_connection()
    except:
        pass  # AI is optional