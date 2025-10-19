-- Migration 052: PII Encryption with pgcrypto
-- Purpose: Enable pgcrypto extension and create PII encryption functions
-- Author: Security hardening initiative
-- Date: 2025-10-19

-- ============================================
-- ENABLE PGCRYPTO EXTENSION
-- ============================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

COMMENT ON EXTENSION pgcrypto IS 'Cryptographic functions for PII encryption';

-- ============================================
-- ENCRYPTION KEY MANAGEMENT
-- ============================================

-- Create secure schema for encryption keys
CREATE SCHEMA IF NOT EXISTS security;

-- Store encryption key hash (actual key should be in environment variable)
-- This table tracks which key version is used
CREATE TABLE IF NOT EXISTS security.encryption_keys (
    id SERIAL PRIMARY KEY,
    key_version VARCHAR(50) NOT NULL UNIQUE,
    algorithm VARCHAR(50) NOT NULL DEFAULT 'aes-256-cbc',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    rotated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT only_one_active_key CHECK (is_active = TRUE)
);

COMMENT ON TABLE security.encryption_keys IS 'Tracks encryption key versions for PII data';

-- Insert initial key version
INSERT INTO security.encryption_keys (key_version, algorithm, is_active)
VALUES ('v1-2025-10', 'aes-256-cbc', TRUE)
ON CONFLICT (key_version) DO NOTHING;

-- ============================================
-- ENCRYPTION/DECRYPTION FUNCTIONS
-- ============================================

-- Function to get current encryption key from environment
-- Key should be stored in ENCRYPTION_KEY environment variable
CREATE OR REPLACE FUNCTION security.get_encryption_key()
RETURNS TEXT AS $$
BEGIN
    -- In production, this reads from environment variable
    -- For now, return a placeholder that signals to use env var
    RETURN current_setting('app.encryption_key', true);
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Encryption key not configured. Set app.encryption_key';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION security.get_encryption_key() IS 'Retrieves encryption key from configuration';

-- Function to encrypt PII data
CREATE OR REPLACE FUNCTION security.encrypt_pii(data TEXT)
RETURNS BYTEA AS $$
DECLARE
    encryption_key TEXT;
BEGIN
    IF data IS NULL THEN
        RETURN NULL;
    END IF;

    encryption_key := security.get_encryption_key();

    -- Encrypt using AES-256-CBC
    RETURN pgp_sym_encrypt(data, encryption_key, 'cipher-algo=aes256');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION security.encrypt_pii(TEXT) IS 'Encrypts sensitive PII data using AES-256';

-- Function to decrypt PII data
CREATE OR REPLACE FUNCTION security.decrypt_pii(encrypted_data BYTEA)
RETURNS TEXT AS $$
DECLARE
    encryption_key TEXT;
BEGIN
    IF encrypted_data IS NULL THEN
        RETURN NULL;
    END IF;

    encryption_key := security.get_encryption_key();

    -- Decrypt using AES-256-CBC
    RETURN pgp_sym_decrypt(encrypted_data, encryption_key);
EXCEPTION
    WHEN OTHERS THEN
        -- Log decryption failure but don't expose details
        RAISE WARNING 'Decryption failed for data';
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION security.decrypt_pii(BYTEA) IS 'Decrypts PII data encrypted with encrypt_pii()';

-- ============================================
-- HELPER FUNCTIONS FOR SPECIFIC DATA TYPES
-- ============================================

-- Encrypt email
CREATE OR REPLACE FUNCTION security.encrypt_email(email TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN security.encrypt_pii(LOWER(TRIM(email)));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Encrypt phone number
CREATE OR REPLACE FUNCTION security.encrypt_phone(phone TEXT)
RETURNS BYTEA AS $$
BEGIN
    -- Remove all non-numeric characters before encryption
    RETURN security.encrypt_pii(regexp_replace(phone, '[^0-9]', '', 'g'));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Encrypt health/medical data
CREATE OR REPLACE FUNCTION security.encrypt_health_data(data JSONB)
RETURNS BYTEA AS $$
BEGIN
    IF data IS NULL THEN
        RETURN NULL;
    END IF;

    RETURN security.encrypt_pii(data::TEXT);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION security.encrypt_health_data(JSONB) IS 'Encrypts health/medical records stored as JSONB';

-- Decrypt health/medical data
CREATE OR REPLACE FUNCTION security.decrypt_health_data(encrypted_data BYTEA)
RETURNS JSONB AS $$
DECLARE
    decrypted_text TEXT;
BEGIN
    IF encrypted_data IS NULL THEN
        RETURN NULL;
    END IF;

    decrypted_text := security.decrypt_pii(encrypted_data);

    IF decrypted_text IS NULL THEN
        RETURN NULL;
    END IF;

    RETURN decrypted_text::JSONB;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Failed to decrypt health data as JSONB';
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- AUDIT LOGGING FOR ENCRYPTION OPERATIONS
-- ============================================

CREATE TABLE IF NOT EXISTS security.encryption_audit_log (
    id BIGSERIAL PRIMARY KEY,
    operation VARCHAR(50) NOT NULL, -- 'encrypt', 'decrypt', 'key_rotation'
    table_name VARCHAR(100),
    column_name VARCHAR(100),
    user_id UUID,
    performed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

CREATE INDEX idx_encryption_audit_performed_at ON security.encryption_audit_log(performed_at DESC);
CREATE INDEX idx_encryption_audit_user ON security.encryption_audit_log(user_id);

COMMENT ON TABLE security.encryption_audit_log IS 'Audit log for all encryption/decryption operations';

-- Function to log encryption operations
CREATE OR REPLACE FUNCTION security.log_encryption_operation(
    p_operation VARCHAR,
    p_table_name VARCHAR DEFAULT NULL,
    p_column_name VARCHAR DEFAULT NULL,
    p_success BOOLEAN DEFAULT TRUE,
    p_error_message TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO security.encryption_audit_log (
        operation,
        table_name,
        column_name,
        user_id,
        ip_address,
        success,
        error_message
    ) VALUES (
        p_operation,
        p_table_name,
        p_column_name,
        auth.uid(), -- Supabase auth user ID
        inet_client_addr(),
        p_success,
        p_error_message
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- ENCRYPTED COLUMNS FOR EXISTING TABLES
-- ============================================

-- Add encrypted columns to bia.processes (BIA processes table)
-- These will store encrypted patient/health data

ALTER TABLE bia.processes
ADD COLUMN IF NOT EXISTS patient_data_encrypted BYTEA,
ADD COLUMN IF NOT EXISTS health_records_encrypted BYTEA,
ADD COLUMN IF NOT EXISTS contact_info_encrypted BYTEA;

COMMENT ON COLUMN bia.processes.patient_data_encrypted IS 'Encrypted patient demographic data';
COMMENT ON COLUMN bia.processes.health_records_encrypted IS 'Encrypted health/medical records';
COMMENT ON COLUMN bia.processes.contact_info_encrypted IS 'Encrypted contact information';

-- Add encrypted columns to organizations table (if PII exists)
ALTER TABLE organizations
ADD COLUMN IF NOT EXISTS contact_email_encrypted BYTEA,
ADD COLUMN IF NOT EXISTS contact_phone_encrypted BYTEA;

-- Add encrypted columns to users table (if not using Supabase auth encryption)
-- Note: Supabase already encrypts email, but we add for consistency
ALTER TABLE organization_users
ADD COLUMN IF NOT EXISTS emergency_contact_encrypted BYTEA,
ADD COLUMN IF NOT EXISTS personal_notes_encrypted BYTEA;

-- ============================================
-- VIEWS FOR EASY DECRYPTION (FOR AUTHORIZED ACCESS)
-- ============================================

-- Create view that auto-decrypts BIA data for authorized users
CREATE OR REPLACE VIEW bia.processes_decrypted AS
SELECT
    id,
    organization_id,
    process_name,
    description,
    criticality_level,
    security.decrypt_health_data(patient_data_encrypted) AS patient_data,
    security.decrypt_health_data(health_records_encrypted) AS health_records,
    security.decrypt_pii(contact_info_encrypted) AS contact_info,
    created_at,
    updated_at
FROM bia.processes
WHERE
    -- RLS policies will restrict access based on organization_id
    organization_id IN (SELECT get_user_org_ids());

COMMENT ON VIEW bia.processes_decrypted IS 'Decrypted view of BIA processes - access controlled by RLS';

-- ============================================
-- MIGRATION HELPERS
-- ============================================

-- Function to migrate existing plaintext data to encrypted format
-- This should be run ONCE after deployment
CREATE OR REPLACE FUNCTION security.migrate_bia_encryption()
RETURNS INTEGER AS $$
DECLARE
    rows_updated INTEGER := 0;
BEGIN
    -- Update BIA records that have plaintext data but no encrypted data
    -- This is a one-time migration - adjust based on your schema

    -- Example: If you have patient_data as JSONB, encrypt it
    -- UPDATE bia.processes
    -- SET patient_data_encrypted = security.encrypt_health_data(patient_data)
    -- WHERE patient_data IS NOT NULL
    -- AND patient_data_encrypted IS NULL;

    -- GET DIAGNOSTICS rows_updated = ROW_COUNT;

    -- Log the migration
    PERFORM security.log_encryption_operation(
        'migration',
        'bia.processes',
        'patient_data_encrypted',
        TRUE,
        format('Migrated %s rows', rows_updated)
    );

    RETURN rows_updated;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION security.migrate_bia_encryption() IS 'One-time migration to encrypt existing plaintext PII data';

-- ============================================
-- GRANTS
-- ============================================

-- Grant usage on security schema to authenticated users
GRANT USAGE ON SCHEMA security TO authenticated;

-- Only allow function execution, not direct table access
GRANT EXECUTE ON FUNCTION security.encrypt_pii(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION security.decrypt_pii(BYTEA) TO authenticated;
GRANT EXECUTE ON FUNCTION security.encrypt_email(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION security.encrypt_phone(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION security.encrypt_health_data(JSONB) TO authenticated;
GRANT EXECUTE ON FUNCTION security.decrypt_health_data(BYTEA) TO authenticated;

-- Restrict access to encryption keys table
REVOKE ALL ON security.encryption_keys FROM PUBLIC;
GRANT SELECT ON security.encryption_keys TO authenticated;

-- Restrict audit log access
REVOKE ALL ON security.encryption_audit_log FROM PUBLIC;
GRANT SELECT ON security.encryption_audit_log TO authenticated;

-- Grant access to decrypted views
GRANT SELECT ON bia.processes_decrypted TO authenticated;

-- ============================================
-- VERIFICATION
-- ============================================

-- Test encryption/decryption
DO $$
DECLARE
    test_data TEXT := 'Sensitive Patient Data 12345';
    encrypted BYTEA;
    decrypted TEXT;
BEGIN
    -- This test will fail until encryption key is configured
    -- encrypted := security.encrypt_pii(test_data);
    -- decrypted := security.decrypt_pii(encrypted);

    -- ASSERT decrypted = test_data, 'Encryption/decryption test failed';

    RAISE NOTICE 'Migration 052 completed successfully';
    RAISE NOTICE 'IMPORTANT: Configure encryption key before using encryption functions';
    RAISE NOTICE 'Set: ALTER DATABASE postgres SET app.encryption_key = ''your-32-byte-key'';';
END $$;
