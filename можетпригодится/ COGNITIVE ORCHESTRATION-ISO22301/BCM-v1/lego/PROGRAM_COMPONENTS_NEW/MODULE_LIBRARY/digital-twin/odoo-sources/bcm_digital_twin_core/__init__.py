# -*- coding: utf-8 -*-

from . import models
from . import controllers
from . import wizard

import logging
_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """Post-initialization hook"""

    _logger.info("Initializing BCM Digital Twin Core module...")

    # Check BCM dependencies
    _check_bcm_dependencies(env)

    # Initialize Digital Twin service
    _initialize_service(env)

    # Set up default data
    _setup_default_data(env)

    _logger.info("BCM Digital Twin Core module initialized successfully")

def uninstall_hook(env):
    """Uninstall hook"""

    _logger.info("Uninstalling BCM Digital Twin Core module...")

    # Clean up system parameters
    params = env['ir.config_parameter'].sudo()
    params.search([('key', 'like', 'bcm.digital_twin.%')]).unlink()
    params.search([('key', 'like', 'bcm.ai_organ.%')]).unlink()

    _logger.info("BCM Digital Twin Core module uninstalled")

def _check_bcm_dependencies(env):
    """Check if required BCM modules are installed"""
    required_modules = [
        'bcm_core',
        'bcm_base',
        'bcm_clients'
    ]

    missing_modules = []
    for module_name in required_modules:
        module = env['ir.module.module'].search([
            ('name', '=', module_name),
            ('state', '=', 'installed')
        ])
        if not module:
            missing_modules.append(module_name)

    if missing_modules:
        _logger.warning(
            f"The following BCM modules are not installed but recommended: {', '.join(missing_modules)}"
        )

def _initialize_service(env):
    """Initialize Digital Twin service connection"""
    _logger.info("Digital Twin service initialization skipped - will be implemented later")

def _setup_default_data(env):
    """Set up default configuration if not exists"""
    Config = env['bcm.digital.twin.config']
    if not Config.search([]):
        # Default config will be created from XML data
        _logger.info("Default configuration will be loaded from data files")