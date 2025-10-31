# -*- coding: utf-8 -*-

from . import models

def _pre_init_hook(env):
    """Pre-initialization hook"""
    # Initialize bridge infrastructure
    pass

def _post_init_hook(env):
    """Post-initialization hook"""
    # Register all BCM modules with the bridge
    env['bcm.ai.bridge']._discover_and_register_modules()