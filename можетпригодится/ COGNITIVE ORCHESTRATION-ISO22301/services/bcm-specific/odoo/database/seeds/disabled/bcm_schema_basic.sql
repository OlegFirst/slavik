-- =====================================================
-- BCM Platform - Basic Database Schema
-- ISO 22301:2019 Compatible (Basic Setup)
-- PostgreSQL 15+ Compatible
-- =====================================================

-- Create BCM database extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- BCM Core Tables (Floor 1) - Basic structure only
-- =====================================================

-- Organization Context (bcm_context module)
CREATE TABLE IF NOT EXISTS bcm_context (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sequence INTEGER DEFAULT 10,
    active BOOLEAN DEFAULT TRUE,
    context_type VARCHAR(50) NOT NULL CHECK (context_type IN ('internal', 'external', 'stakeholder', 'regulatory', 'strategic')),
    description TEXT,
    impact_on_bcms TEXT,
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    opportunity_level VARCHAR(20) CHECK (opportunity_level IN ('low', 'medium', 'high')),
    review_frequency VARCHAR(20) DEFAULT 'quarterly' CHECK (review_frequency IN ('monthly', 'quarterly', 'semiannually', 'annually')),
    last_review_date DATE,
    next_review_date DATE,
    responsible_user_id INTEGER,
    department_id INTEGER,
    company_id INTEGER NOT NULL,
    create_uid INTEGER,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    write_uid INTEGER,
    write_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Log table for successful initialization
CREATE TABLE IF NOT EXISTS bcm_init_log (
    id SERIAL PRIMARY KEY,
    message VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO bcm_init_log (message) VALUES ('BCM Basic Schema initialized successfully');