# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Post-migration script for BCM Digital Twin Core"""
    env = api.Environment(cr, SUPERUSER_ID, {})

    _logger.info("Starting BCM Digital Twin post-migration...")

    # 1. Ensure all BCM models are properly linked
    _ensure_bcm_links(env)

    # 2. Initialize default configurations
    _initialize_configs(env)

    # 3. Set up AI organs mapping
    _setup_ai_organs(env)

    # 4. Update existing records with BCM prefixes
    _update_model_prefixes(env)

    _logger.info("BCM Digital Twin post-migration completed successfully")

def _ensure_bcm_links(env):
    """Ensure all BCM models have Digital Twin extensions"""
    _logger.info("Checking BCM model links...")

    # Check if BCM modules are installed
    bcm_modules = [
        'bcm_clients', 'bcm_context', 'bcm_bia',
        'bcm_risk_management', 'bcm_incident'
    ]

    for module_name in bcm_modules:
        module = env['ir.module.module'].search([('name', '=', module_name)])
        if module and module.state == 'installed':
            _logger.info(f"BCM module {module_name} is installed and ready for integration")
        else:
            _logger.warning(f"BCM module {module_name} not found or not installed")

def _initialize_configs(env):
    """Initialize default configurations"""
    _logger.info("Initializing Digital Twin configurations...")

    # Check if default config exists
    Config = env['bcm.digital.twin.config']
    default_config = Config.search([('name', '=', 'Default BCM Digital Twin Configuration')])

    if not default_config:
        # Create default configuration
        Config.create({
            'name': 'Default BCM Digital Twin Configuration',
            'active': True,
            'service_url': 'http://localhost:3001',
            'timeout': 30,
            'retry_count': 3,
            'default_simulation_mode': 'standard',
            'enable_caching': True,
            'cache_duration': 24,
            'enable_ai_analysis': True,
            'ai_confidence_threshold': 70.0,
            'max_concurrent_simulations': 5,
            'batch_processing_enabled': True,
            'batch_size': 10
        })
        _logger.info("Default configuration created")

def _setup_ai_organs(env):
    """Set up AI organs mapping"""
    _logger.info("Setting up AI organs mapping...")

    # Define AI organs configuration
    ai_organs = {
        'governance_brain': {
            'name': 'Governance Brain',
            'description': 'Strategic governance and compliance AI',
            'bcm_module': 'bcm_ai_control',
            'priority': 1
        },
        'emergency_response': {
            'name': 'Emergency Response System',
            'description': 'Crisis and emergency management AI',
            'bcm_module': 'bcm_incident',
            'priority': 2
        },
        'impact_oracle': {
            'name': 'Impact Oracle',
            'description': 'Business impact prediction AI',
            'bcm_module': 'bcm_bia',
            'priority': 3
        },
        'scenario_creator': {
            'name': 'Scenario Creator',
            'description': 'Scenario generation and simulation AI',
            'bcm_module': 'bcm_scenario',
            'priority': 4
        },
        'risk_advisor': {
            'name': 'Risk Advisor',
            'description': 'Risk assessment and mitigation AI',
            'bcm_module': 'bcm_risk_management',
            'priority': 5
        },
        'compliance_guardian': {
            'name': 'Compliance Guardian',
            'description': 'Regulatory compliance monitoring AI',
            'bcm_module': 'bcm_audit',
            'priority': 6
        },
        'performance_analyst': {
            'name': 'Performance Analyst',
            'description': 'Performance metrics and KPI analysis AI',
            'bcm_module': 'bcm_metrics',
            'priority': 7
        },
        'learning_coach': {
            'name': 'Learning Coach',
            'description': 'Training and skill development AI',
            'bcm_module': 'bcm_training',
            'priority': 8
        },
        'plan_generator': {
            'name': 'Plan Generator',
            'description': 'Continuity plan generation AI',
            'bcm_module': 'bcm_plan',
            'priority': 9
        },
        'lifecycle_monitor': {
            'name': 'Lifecycle Monitor',
            'description': 'System lifecycle monitoring AI',
            'bcm_module': 'bcm_lifecycle',
            'priority': 10
        }
    }

    # Store configuration in system parameters
    IrConfig = env['ir.config_parameter'].sudo()
    for organ_id, organ_data in ai_organs.items():
        param_key = f'bcm.ai_organ.{organ_id}'
        IrConfig.set_param(param_key, str(organ_data))
        _logger.info(f"Configured AI organ: {organ_data['name']}")

def _update_model_prefixes(env):
    """Update existing records with BCM prefixes"""
    _logger.info("Updating model prefixes...")

    # Map old model names to new BCM-prefixed names
    model_mapping = {
        'digital.twin.organization': 'bcm.digital.twin.organization',
        'digital.twin.simulation': 'bcm.digital.twin.simulation',
        'digital.twin.config': 'bcm.digital.twin.config',
        'ai.twin.orchestrator': 'bcm.ai.twin.orchestrator'
    }

    # Update ir.model records
    for old_name, new_name in model_mapping.items():
        cr.execute("""
            UPDATE ir_model
            SET model = %s
            WHERE model = %s
        """, (new_name, old_name))

        cr.execute("""
            UPDATE ir_model_fields
            SET model = %s
            WHERE model = %s
        """, (new_name, old_name))

        _logger.info(f"Updated model {old_name} to {new_name}")

    # Update references in XML IDs
    cr.execute("""
        UPDATE ir_model_data
        SET model = REPLACE(model, 'digital.twin.', 'bcm.digital.twin.')
        WHERE model LIKE 'digital.twin.%'
    """)

    cr.execute("""
        UPDATE ir_model_data
        SET model = REPLACE(model, 'ai.twin.', 'bcm.ai.twin.')
        WHERE model LIKE 'ai.twin.%'
    """)

    _logger.info("Model prefix update completed")