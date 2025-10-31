-- BCM Platform Supabase Schema (ИСПРАВЛЕННАЯ ВЕРСИЯ)
-- Работает с стандартным Supabase auth

-- Enable Row Level Security
-- ALTER DATABASE postgres SET row_security = on; -- Не нужно в Supabase

-- Users table (extends Supabase auth.users через metadata)
CREATE TABLE public.bcm_users (
  id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  avatar_url TEXT,

  -- BCM specific fields
  company_id INTEGER,
  client_id TEXT,
  subscription_plan TEXT DEFAULT 'basic',
  is_active BOOLEAN DEFAULT true,

  -- Preferences
  theme TEXT DEFAULT 'light',
  language TEXT DEFAULT 'en',
  timezone TEXT DEFAULT 'UTC',

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_login TIMESTAMPTZ,
  login_count INTEGER DEFAULT 0
);

-- Companies/Clients table for multi-tenancy
CREATE TABLE public.bcm_companies (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,

  -- Subscription
  subscription_plan TEXT DEFAULT 'basic',
  subscription_status TEXT DEFAULT 'active',
  max_users INTEGER DEFAULT 10,

  -- Settings
  settings JSONB DEFAULT '{}',
  features JSONB DEFAULT '{}',

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User sessions and activity
CREATE TABLE public.user_sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  session_data JSONB,
  ip_address INET,
  user_agent TEXT,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  is_active BOOLEAN DEFAULT true
);

-- Activity log for audit trail
CREATE TABLE public.user_activities (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  action TEXT NOT NULL,
  resource TEXT,
  resource_id TEXT,
  details JSONB,
  ip_address INET,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI Assistant conversations
CREATE TABLE public.ai_conversations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  context_type TEXT, -- 'bia', 'incident', 'training', etc.
  context_data JSONB,

  messages JSONB[], -- Array of message objects
  status TEXT DEFAULT 'active',

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_bcm_users_company ON bcm_users(company_id);
CREATE INDEX idx_bcm_users_email ON bcm_users(email);
CREATE INDEX idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_user_activities_user ON user_activities(user_id);
CREATE INDEX idx_user_activities_created ON user_activities(created_at);
CREATE INDEX idx_ai_conversations_user ON ai_conversations(user_id);

-- Row Level Security Policies
ALTER TABLE bcm_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE bcm_companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON bcm_users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON bcm_users
  FOR UPDATE USING (auth.uid() = id);

-- Company isolation (исправленная политика)
CREATE POLICY "Company data isolation" ON bcm_companies
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM bcm_users
      WHERE bcm_users.id = auth.uid()
      AND bcm_users.company_id = bcm_companies.id
    )
    OR
    (auth.jwt() ->> 'role') = 'bcm_admin'
  );

-- Session management
CREATE POLICY "Users own sessions" ON user_sessions
  FOR ALL USING (user_id = auth.uid());

-- Activity log (users can view own)
CREATE POLICY "Users own activities" ON user_activities
  FOR SELECT USING (user_id = auth.uid());

-- AI conversations (users own)
CREATE POLICY "Users own conversations" ON ai_conversations
  FOR ALL USING (user_id = auth.uid());

-- Functions for user management
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.bcm_users (id, email, full_name)
  VALUES (
    new.id,
    new.email,
    new.raw_user_meta_data->>'full_name'
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger on auth.users creation
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update triggers
CREATE TRIGGER update_bcm_users_updated_at BEFORE UPDATE ON bcm_users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bcm_companies_updated_at BEFORE UPDATE ON bcm_companies
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default company for testing
INSERT INTO bcm_companies (name, slug, subscription_plan)
VALUES ('Demo Company', 'demo-company', 'premium')
ON CONFLICT (slug) DO NOTHING;