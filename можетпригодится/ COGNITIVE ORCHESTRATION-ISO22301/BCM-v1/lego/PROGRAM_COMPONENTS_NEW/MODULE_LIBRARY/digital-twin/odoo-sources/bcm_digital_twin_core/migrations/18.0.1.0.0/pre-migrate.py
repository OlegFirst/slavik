# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Pre-migration script for BCM Digital Twin Core"""

    _logger.info("Starting BCM Digital Twin pre-migration...")

    # Create tables if they don't exist
    _create_tables(cr)

    # Add missing columns
    _add_missing_columns(cr)

    # Create indexes for performance
    _create_indexes(cr)

    _logger.info("BCM Digital Twin pre-migration completed")

def _create_tables(cr):
    """Create Digital Twin tables if they don't exist"""

    # BCM Digital Twin Organization table
    cr.execute("""
        CREATE TABLE IF NOT EXISTS bcm_digital_twin_organization (
            id SERIAL PRIMARY KEY,
            create_uid INTEGER,
            write_uid INTEGER,
            create_date TIMESTAMP,
            write_date TIMESTAMP,
            name VARCHAR(255) NOT NULL,
            code VARCHAR(50),
            domain_type VARCHAR(50),
            bcm_client_id INTEGER,
            twin_status VARCHAR(50),
            twin_health_score FLOAT,
            twin_config TEXT,
            ai_insights TEXT,
            simulation_results TEXT,
            last_simulation_date TIMESTAMP,
            execution_mode VARCHAR(50),
            service_endpoint VARCHAR(255),
            api_key VARCHAR(255),
            connection_status VARCHAR(50),
            last_sync_date TIMESTAMP,
            sync_frequency INTEGER,
            enable_auto_sync BOOLEAN DEFAULT FALSE,
            data_retention_days INTEGER DEFAULT 90,
            notes TEXT,
            active BOOLEAN DEFAULT TRUE
        );
    """)
    _logger.info("Created/verified bcm_digital_twin_organization table")

    # BCM Digital Twin Simulation table
    cr.execute("""
        CREATE TABLE IF NOT EXISTS bcm_digital_twin_simulation (
            id SERIAL PRIMARY KEY,
            create_uid INTEGER,
            write_uid INTEGER,
            create_date TIMESTAMP,
            write_date TIMESTAMP,
            name VARCHAR(255) NOT NULL,
            organization_id INTEGER REFERENCES bcm_digital_twin_organization(id),
            scenario_type VARCHAR(50),
            scenario_description TEXT,
            parameters TEXT,
            state VARCHAR(50),
            progress FLOAT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration FLOAT,
            results TEXT,
            insights TEXT,
            recommendations TEXT,
            confidence_score FLOAT,
            impact_score FLOAT,
            risk_score FLOAT,
            related_incident INTEGER,
            related_risk INTEGER,
            related_bia INTEGER,
            notes TEXT
        );
    """)
    _logger.info("Created/verified bcm_digital_twin_simulation table")

    # BCM AI Twin Orchestrator table
    cr.execute("""
        CREATE TABLE IF NOT EXISTS bcm_ai_twin_orchestrator (
            id SERIAL PRIMARY KEY,
            create_uid INTEGER,
            write_uid INTEGER,
            create_date TIMESTAMP,
            write_date TIMESTAMP,
            name VARCHAR(255) NOT NULL,
            organization_id INTEGER REFERENCES bcm_digital_twin_organization(id),
            simulation_id INTEGER REFERENCES bcm_digital_twin_simulation(id),
            analysis_type VARCHAR(50),
            priority VARCHAR(20),
            state VARCHAR(50),
            organs_status TEXT,
            ai_results TEXT,
            synthesized_insights TEXT,
            recommendations TEXT,
            confidence_score FLOAT,
            execution_time FLOAT,
            start_time TIMESTAMP,
            completion_time TIMESTAMP
        );
    """)
    _logger.info("Created/verified bcm_ai_twin_orchestrator table")

    # BCM Digital Twin Config table
    cr.execute("""
        CREATE TABLE IF NOT EXISTS bcm_digital_twin_config (
            id SERIAL PRIMARY KEY,
            create_uid INTEGER,
            write_uid INTEGER,
            create_date TIMESTAMP,
            write_date TIMESTAMP,
            name VARCHAR(255) NOT NULL,
            active BOOLEAN DEFAULT TRUE,
            service_url VARCHAR(255),
            timeout INTEGER DEFAULT 30,
            retry_count INTEGER DEFAULT 3,
            default_simulation_mode VARCHAR(50),
            enable_caching BOOLEAN DEFAULT TRUE,
            cache_duration INTEGER DEFAULT 24,
            enable_ai_analysis BOOLEAN DEFAULT TRUE,
            ai_confidence_threshold FLOAT DEFAULT 70.0,
            max_concurrent_simulations INTEGER DEFAULT 5,
            batch_processing_enabled BOOLEAN DEFAULT FALSE,
            batch_size INTEGER DEFAULT 10,
            log_level VARCHAR(20) DEFAULT 'INFO',
            enable_notifications BOOLEAN DEFAULT TRUE
        );
    """)
    _logger.info("Created/verified bcm_digital_twin_config table")

def _add_missing_columns(cr):
    """Add missing columns to existing tables"""

    # Check and add columns for integration with BCM modules
    columns_to_add = [
        ('bcm_digital_twin_organization', 'bcm_context_id', 'INTEGER'),
        ('bcm_digital_twin_organization', 'bcm_strategy_id', 'INTEGER'),
        ('bcm_digital_twin_simulation', 'bcm_plan_id', 'INTEGER'),
        ('bcm_digital_twin_simulation', 'bcm_exercise_id', 'INTEGER'),
        ('bcm_ai_twin_orchestrator', 'bcm_ai_control_id', 'INTEGER')
    ]

    for table, column, col_type in columns_to_add:
        # Check if column exists
        cr.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
        """, (table, column))

        if not cr.fetchone():
            cr.execute(f"""
                ALTER TABLE {table}
                ADD COLUMN IF NOT EXISTS {column} {col_type}
            """)
            _logger.info(f"Added column {column} to {table}")

def _create_indexes(cr):
    """Create indexes for performance optimization"""

    indexes = [
        ('idx_dt_org_client', 'bcm_digital_twin_organization', 'bcm_client_id'),
        ('idx_dt_org_status', 'bcm_digital_twin_organization', 'twin_status'),
        ('idx_dt_sim_org', 'bcm_digital_twin_simulation', 'organization_id'),
        ('idx_dt_sim_state', 'bcm_digital_twin_simulation', 'state'),
        ('idx_dt_sim_type', 'bcm_digital_twin_simulation', 'scenario_type'),
        ('idx_ai_orch_org', 'bcm_ai_twin_orchestrator', 'organization_id'),
        ('idx_ai_orch_sim', 'bcm_ai_twin_orchestrator', 'simulation_id'),
        ('idx_ai_orch_state', 'bcm_ai_twin_orchestrator', 'state')
    ]

    for index_name, table_name, column_name in indexes:
        cr.execute(f"""
            CREATE INDEX IF NOT EXISTS {index_name}
            ON {table_name} ({column_name})
        """)
        _logger.info(f"Created index {index_name} on {table_name}.{column_name}")