# Fixing Vercel Integration

## Problem
The GitHub repository is connected to the wrong Vercel account (@superman32432432) instead of the correct one (maxdemchenko-6220).

## Solution Steps

### 1. Remove Wrong Integration from GitHub
1. Go to https://github.com/SEH-foundation/ISO-22301/settings/installations
2. Find the Vercel app installation for @superman32432432
3. Click "Configure" and then "Uninstall" or "Revoke access"

### 2. Remove Project from Wrong Vercel Account (if accessible)
If you have access to @superman32432432's Vercel account:
1. Go to https://vercel.com/dashboard
2. Find the ISO-22301 project
3. Go to Settings → Git
4. Disconnect the GitHub repository

### 3. Connect to Correct Vercel Account
1. Log in to Vercel with the correct account: https://vercel.com/maxdemchenko-6220
2. Go to https://vercel.com/new
3. Import the GitHub repository: SEH-foundation/ISO-22301
4. Select the correct project: maxs-projects-386ddd54
5. Use project ID: prj_IVdgUJ1I9ZADYwr7XUsfYzrNvZwe

### 4. Configure Deployment Settings
1. Framework Preset: Vue.js
2. Build Command: `npm run build`
3. Output Directory: `dist`
4. Install Command: `npm ci`
5. Root Directory: `frontend/web_portal`

### 5. Environment Variables
Add these environment variables in Vercel:
```
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
VITE_API_BASE_URL=your-api-base-url
```

### 6. Verify GitHub Integration
After connecting:
1. Go to GitHub repository settings
2. Check "Webhooks" section for Vercel webhook
3. Verify it's from the correct Vercel account

## Alternative: Using Vercel CLI
If UI method doesn't work:
```bash
# Install Vercel CLI
npm i -g vercel

# Login with correct account
vercel login

# Link project
cd frontend/web_portal
vercel link --project=prj_IVdgUJ1I9ZADYwr7XUsfYzrNvZwe

# Deploy
vercel --prod
```

## Notes
- The @superman32432432 account is not referenced in the codebase
- The integration is at the GitHub repository level, not in code
- CI/CD will fail until the correct account is connected