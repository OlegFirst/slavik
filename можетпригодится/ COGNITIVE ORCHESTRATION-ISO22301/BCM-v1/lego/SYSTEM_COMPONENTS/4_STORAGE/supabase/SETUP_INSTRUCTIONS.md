# Supabase Setup Instructions for BCM Platform

## 1. Database Setup

### Run Schema
```sql
-- In Supabase SQL Editor:
-- 1. Copy and run schema.sql
-- 2. Copy and run auth-policies.sql
```

### Verify Tables
- bcm_users
- bcm_companies
- user_sessions
- user_activities
- ai_conversations
- api_keys

## 2. Authentication Configuration

### Enable Providers
- Email/Password: ✅ Enable
- Google OAuth: Optional
- GitHub OAuth: Optional

### Email Templates
Update confirmation email template in:
`Authentication > Email Templates`

### Security Settings
- Enable email confirmations
- Set password requirements
- Configure session timeout

## 3. Row Level Security

### Policies Created:
- Users can only see own data
- Company data isolation
- Admin override permissions
- Audit log protection

### Test RLS:
```sql
SELECT auth.uid(); -- Should return user ID
SELECT * FROM bcm_users; -- Should return only current user
```

## 4. Edge Functions (Optional)

### Deploy Function:
```bash
supabase functions deploy bcm-sync
```

### Environment Variables:
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY

## 5. API Keys Setup

### Add to GitHub Secrets:
- SUPABASE_URL: https://mvzlkpzakzlmmxyjjtvr.supabase.co
- SUPABASE_ANON_KEY: (public key)
- SUPABASE_SERVICE_KEY: (service role key)

### Local Development:
```bash
# Create .env in web_portal-2:
VITE_SUPABASE_URL=https://mvzlkpzakzlmmxyjjtvr.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

## 6. Integration Test

### Test Authentication:
1. Open Web Portal v2
2. Register new user
3. Check bcm_users table
4. Test login/logout
5. Verify RLS policies

### Test API:
```javascript
import { supabase } from './lib/supabase'

// Test connection
const { data, error } = await supabase.auth.getSession()
console.log('Session:', data.session)
```

## 7. Multi-tenancy Setup

### Company Creation:
```sql
INSERT INTO bcm_companies (name, slug, subscription_plan)
VALUES ('Test Company', 'test-company', 'premium');
```

### Assign User to Company:
```sql
UPDATE bcm_users
SET company_id = 1, role = 'admin'
WHERE email = 'your@email.com';
```

## Ready for Production!

After setup, your BCM Platform will have:
- ✅ Secure multi-tenant authentication
- ✅ User profile management
- ✅ Activity auditing
- ✅ AI conversation tracking
- ✅ Company isolation
- ✅ API key management