-- Authentication and API Keys Tables
-- Version: 1.0.0
-- Date: 2025-01-15

-- API_KEYS table for organization API access
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    permissions TEXT[] DEFAULT ARRAY['read'],
    description TEXT,
    last_used TIMESTAMPTZ,
    usage_count INTEGER DEFAULT 0,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id)
);

-- Indexes for api_keys
CREATE INDEX idx_api_keys_org ON api_keys(organization_id);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
CREATE INDEX idx_api_keys_expires ON api_keys(expires_at);

-- USER_PROFILES table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id),
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'member',
    avatar_url TEXT,
    phone VARCHAR(50),
    preferences JSONB DEFAULT '{}',
    notifications_enabled BOOLEAN DEFAULT true,
    last_login TIMESTAMPTZ,
    login_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (role IN ('owner', 'admin', 'member', 'viewer'))
);

-- Indexes for user_profiles
CREATE INDEX idx_user_profiles_org ON user_profiles(organization_id);
CREATE INDEX idx_user_profiles_role ON user_profiles(role);

-- INVITATIONS table for inviting team members
CREATE TABLE IF NOT EXISTS invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'member',
    token VARCHAR(255) UNIQUE NOT NULL,
    invited_by UUID REFERENCES auth.users(id),
    accepted_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (role IN ('admin', 'member', 'viewer'))
);

-- Indexes for invitations
CREATE INDEX idx_invitations_org ON invitations(organization_id);
CREATE INDEX idx_invitations_email ON invitations(email);
CREATE INDEX idx_invitations_token ON invitations(token);
CREATE INDEX idx_invitations_expires ON invitations(expires_at);

-- PASSWORD_RESET_TOKENS table (additional to Supabase auth)
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    used BOOLEAN DEFAULT false,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for password_reset_tokens
CREATE INDEX idx_password_reset_user ON password_reset_tokens(user_id);
CREATE INDEX idx_password_reset_token ON password_reset_tokens(token_hash);
CREATE INDEX idx_password_reset_expires ON password_reset_tokens(expires_at);

-- EMAIL_VERIFICATIONS table
CREATE TABLE IF NOT EXISTS email_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    verified BOOLEAN DEFAULT false,
    verified_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for email_verifications
CREATE INDEX idx_email_verif_user ON email_verifications(user_id);
CREATE INDEX idx_email_verif_token ON email_verifications(token_hash);
CREATE INDEX idx_email_verif_expires ON email_verifications(expires_at);

-- LOGIN_ATTEMPTS table for security monitoring
CREATE TABLE IF NOT EXISTS login_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN,
    failure_reason VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for login_attempts
CREATE INDEX idx_login_attempts_email ON login_attempts(email);
CREATE INDEX idx_login_attempts_ip ON login_attempts(ip_address);
CREATE INDEX idx_login_attempts_created ON login_attempts(created_at DESC);

-- ORGANIZATION_SETTINGS table
CREATE TABLE IF NOT EXISTS organization_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE UNIQUE,
    allow_public_profile BOOLEAN DEFAULT false,
    allow_api_access BOOLEAN DEFAULT true,
    max_api_keys INTEGER DEFAULT 5,
    max_team_members INTEGER DEFAULT 10,
    features JSONB DEFAULT '{}',
    billing_info JSONB,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    subscription_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (subscription_tier IN ('free', 'starter', 'professional', 'enterprise'))
);

-- Indexes for organization_settings
CREATE INDEX idx_org_settings_org ON organization_settings(organization_id);
CREATE INDEX idx_org_settings_tier ON organization_settings(subscription_tier);

-- ACTIVITY_LOG table for user activity tracking
CREATE TABLE IF NOT EXISTS activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for activity_log
CREATE INDEX idx_activity_user ON activity_log(user_id);
CREATE INDEX idx_activity_org ON activity_log(organization_id);
CREATE INDEX idx_activity_type ON activity_log(activity_type);
CREATE INDEX idx_activity_created ON activity_log(created_at DESC);

-- Functions for auth management

-- Function to create user profile after signup
CREATE OR REPLACE FUNCTION create_user_profile()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_profiles (id, full_name, role)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
        COALESCE(NEW.raw_user_meta_data->>'role', 'member')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION create_user_profile();

-- Function to log login attempts
CREATE OR REPLACE FUNCTION log_login_attempt(
    p_email VARCHAR,
    p_ip_address INET,
    p_user_agent TEXT,
    p_success BOOLEAN,
    p_failure_reason VARCHAR DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO login_attempts (email, ip_address, user_agent, success, failure_reason)
    VALUES (p_email, p_ip_address, p_user_agent, p_success, p_failure_reason);
    
    -- Check for suspicious activity (too many failed attempts)
    IF NOT p_success THEN
        DECLARE
            v_failed_count INTEGER;
        BEGIN
            SELECT COUNT(*) INTO v_failed_count
            FROM login_attempts
            WHERE email = p_email
            AND success = false
            AND created_at > NOW() - INTERVAL '15 minutes';
            
            IF v_failed_count > 5 THEN
                -- Log suspicious activity
                INSERT INTO audit_logs (
                    actor_email,
                    action,
                    resource_type,
                    ip_address,
                    user_agent,
                    success,
                    error_message
                ) VALUES (
                    p_email,
                    'suspicious_login_attempts',
                    'authentication',
                    p_ip_address,
                    p_user_agent,
                    false,
                    'Multiple failed login attempts detected'
                );
            END IF;
        END;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to validate API key
CREATE OR REPLACE FUNCTION validate_api_key(p_key_hash VARCHAR)
RETURNS TABLE (
    organization_id UUID,
    permissions TEXT[],
    is_valid BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ak.organization_id,
        ak.permissions,
        (ak.is_active AND (ak.expires_at IS NULL OR ak.expires_at > NOW())) as is_valid
    FROM api_keys ak
    WHERE ak.key_hash = p_key_hash
    LIMIT 1;
    
    -- Update last used timestamp
    UPDATE api_keys 
    SET 
        last_used = NOW(),
        usage_count = usage_count + 1
    WHERE key_hash = p_key_hash;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired tokens
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS INTEGER AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    -- Delete expired password reset tokens
    DELETE FROM password_reset_tokens
    WHERE expires_at < NOW() AND used = false;
    
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    
    -- Delete expired email verifications
    DELETE FROM email_verifications
    WHERE expires_at < NOW() AND verified = false;
    
    -- Delete expired invitations
    DELETE FROM invitations
    WHERE expires_at < NOW() AND accepted_at IS NULL;
    
    -- Delete expired sessions
    DELETE FROM sessions
    WHERE expires_at < NOW();
    
    -- Archive old login attempts (keep last 30 days)
    DELETE FROM login_attempts
    WHERE created_at < NOW() - INTERVAL '30 days';
    
    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get organization statistics
CREATE OR REPLACE FUNCTION get_organization_stats(p_org_id UUID)
RETURNS TABLE (
    total_users INTEGER,
    total_twins INTEGER,
    total_simulations INTEGER,
    total_api_keys INTEGER,
    active_sessions INTEGER,
    last_activity TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM user_profiles WHERE organization_id = p_org_id)::INTEGER as total_users,
        (SELECT COUNT(*) FROM digital_twins WHERE organization_id = p_org_id)::INTEGER as total_twins,
        (SELECT COUNT(*) FROM simulations s 
         JOIN digital_twins dt ON s.twin_id = dt.id 
         WHERE dt.organization_id = p_org_id)::INTEGER as total_simulations,
        (SELECT COUNT(*) FROM api_keys WHERE organization_id = p_org_id AND is_active = true)::INTEGER as total_api_keys,
        (SELECT COUNT(*) FROM sessions s 
         JOIN user_profiles up ON s.user_id = up.id 
         WHERE up.organization_id = p_org_id 
         AND s.expires_at > NOW())::INTEGER as active_sessions,
        (SELECT MAX(created_at) FROM activity_log WHERE organization_id = p_org_id) as last_activity;
END;
$$ LANGUAGE plpgsql;

-- RLS Policies for new tables

-- API Keys policies
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Organizations manage their API keys"
    ON api_keys FOR ALL
    USING (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    )
    WITH CHECK (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    );

-- User profiles policies
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile"
    ON user_profiles FOR SELECT
    USING (id = auth.uid());

CREATE POLICY "Users can update their own profile"
    ON user_profiles FOR UPDATE
    USING (id = auth.uid())
    WITH CHECK (id = auth.uid());

CREATE POLICY "Organization owners can view member profiles"
    ON user_profiles FOR SELECT
    USING (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    );

-- Organization settings policies
ALTER TABLE organization_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Organizations manage their settings"
    ON organization_settings FOR ALL
    USING (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    )
    WITH CHECK (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    );

-- Activity log policies
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own activity"
    ON activity_log FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Organizations can view their activity"
    ON activity_log FOR SELECT
    USING (
        organization_id IN (
            SELECT id FROM organizations 
            WHERE created_by = auth.uid()
        )
    );

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON api_keys TO authenticated;
GRANT SELECT, INSERT, UPDATE ON user_profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE ON organization_settings TO authenticated;
GRANT SELECT ON activity_log TO authenticated;
GRANT INSERT ON activity_log TO authenticated;

-- Comments
COMMENT ON TABLE api_keys IS 'API keys for programmatic access to organization resources';
COMMENT ON TABLE user_profiles IS 'Extended user profiles linked to Supabase auth';
COMMENT ON TABLE invitations IS 'Pending invitations to join organizations';
COMMENT ON TABLE organization_settings IS 'Organization-specific settings and preferences';
COMMENT ON TABLE activity_log IS 'User activity tracking for analytics and security';