-- Supabase Authentication Policies for BCM Platform
-- Advanced security configuration

-- Create custom roles
INSERT INTO auth.roles (name) VALUES ('bcm_admin'), ('bcm_manager'), ('bcm_user'), ('bcm_viewer')
ON CONFLICT (name) DO NOTHING;

-- Email domain restrictions (optional)
CREATE OR REPLACE FUNCTION public.is_valid_email_domain(email TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  -- Allow specific domains or all for now
  RETURN email ~* '@.*\.(com|org|net|edu|gov)$';
END;
$$ LANGUAGE plpgsql;

-- User registration policy
CREATE POLICY "Restrict user registration" ON auth.users
  FOR INSERT
  WITH CHECK (
    -- Allow registration only for valid email domains
    is_valid_email_domain(email)
  );

-- Multi-factor authentication setup
CREATE TABLE public.user_mfa (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES bcm_users(id) ON DELETE CASCADE,

  method TEXT NOT NULL, -- 'totp', 'sms', 'email'
  secret TEXT, -- For TOTP
  phone TEXT, -- For SMS

  is_enabled BOOLEAN DEFAULT false,
  backup_codes TEXT[], -- Array of backup codes

  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_used TIMESTAMPTZ
);

-- Session security
CREATE TABLE public.user_security_events (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES bcm_users(id),

  event_type TEXT NOT NULL, -- 'login', 'logout', 'password_change', etc.
  ip_address INET,
  user_agent TEXT,
  location JSONB, -- GeoIP data

  risk_score INTEGER DEFAULT 0, -- 0-100 risk assessment
  is_suspicious BOOLEAN DEFAULT false,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Rate limiting for API endpoints
CREATE TABLE public.api_rate_limits (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES bcm_users(id),
  endpoint TEXT NOT NULL,

  requests_count INTEGER DEFAULT 0,
  window_start TIMESTAMPTZ DEFAULT NOW(),

  PRIMARY KEY (user_id, endpoint, window_start)
);

-- Password policy enforcement
CREATE OR REPLACE FUNCTION public.validate_password_strength(password TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN (
    LENGTH(password) >= 8 AND
    password ~ '[A-Z]' AND
    password ~ '[a-z]' AND
    password ~ '[0-9]' AND
    password ~ '[^A-Za-z0-9]'
  );
END;
$$ LANGUAGE plpgsql;

-- Company access control
CREATE OR REPLACE FUNCTION public.user_has_company_access(target_company_id INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
  user_company_id INTEGER;
BEGIN
  SELECT company_id INTO user_company_id
  FROM bcm_users
  WHERE id = auth.uid();

  RETURN user_company_id = target_company_id OR
         (SELECT role FROM bcm_users WHERE id = auth.uid()) = 'admin';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Audit logging function
CREATE OR REPLACE FUNCTION public.log_user_activity(
  action_type TEXT,
  resource_name TEXT DEFAULT NULL,
  resource_id TEXT DEFAULT NULL,
  details JSONB DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
  INSERT INTO user_activities (user_id, action, resource, resource_id, details, ip_address)
  VALUES (
    auth.uid(),
    action_type,
    resource_name,
    resource_id,
    details,
    INET(current_setting('request.headers')::json->>'x-forwarded-for')
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- RLS Policies for security tables
ALTER TABLE user_mfa ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_security_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_rate_limits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users own MFA settings" ON user_mfa
  FOR ALL USING (user_id = auth.uid());

CREATE POLICY "Users own security events" ON user_security_events
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users own rate limits" ON api_rate_limits
  FOR ALL USING (user_id = auth.uid());

