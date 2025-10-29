# Vercel Environment Variables Setup

## Add these to Vercel Dashboard > Settings > Environment Variables:

### Frontend Variables (Vue CLI format - NO QUOTES!)
```
VUE_APP_EVENTBUS_URL=/api/events
VUE_APP_ORCHESTRATOR_URL=/api
VUE_APP_ENABLE_EVENTS=1
VUE_APP_ENABLE_AUTH=0
VUE_APP_DEMO=0
VUE_APP_DISABLE_AUTH=1
NEXT_PUBLIC_API_URL=https://<iso-22301-service>.up.railway.app
VITE_API_URL=https://<iso-22301-service>.up.railway.app
NEXT_PUBLIC_ODOO_URL=https://<odoo-service>.up.railway.app
VITE_ODOO_URL=https://<odoo-service>.up.railway.app
```

### Upstash Redis KV (Backend - add all to Vercel)
```
KV_URL=rediss://default:AekBAAIncDE2MDAxMzk1NTM1ZGM0MTk1OTYyYWVhMmNjNjIzNmE1Y3AxNTk2NDk@choice-lion-59649.upstash.io:6379
KV_REST_API_URL=https://choice-lion-59649.upstash.io
KV_REST_API_TOKEN=AekBAAIncDE2MDAxMzk1NTM1ZGM0MTk1OTYyYWVhMmNjNjIzNmE1Y3AxNTk2NDk
KV_REST_API_READ_ONLY_TOKEN=AukBAAIgcDGwmNzL_zBlRwYV_K9T_jXtxb6bxH3_CSmAWxo7o8xaQQ
REDIS_URL=rediss://default:AekBAAIncDE2MDAxMzk1NTM1ZGM0MTk1OTYyYWVhMmNjNjIzNmE1Y3AxNTk2NDk@choice-lion-59649.upstash.io:6379
KV_NAMESPACE=events
```

### Optional: Supabase (if you have it)
```
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_KEY=your-service-key
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## Test the API

After adding env vars and redeploying:

```bash
# Test event publishing and history
./frontend/web_portal/test-api.sh

# Or manually:
curl https://iso-22301.vercel.app/api/events/history?tenant_id=default
```

## What works now:
- ✅ Event publishing to Redis
- ✅ Event history from Redis  
- ✅ SSE streaming (with fallback)
- ✅ AI endpoints (mock data for now)

## Redis Data Structure:
- `events:{tenant_id}:history` - List of JSON events (LIFO)
- `events:{tenant_id}` - Pub/sub channel for real-time
