# Railway Deployment Configuration

This document outlines the Railway deployment setup for the ISO 22301 BCM Platform.

## Services Setup

### 1. Railway Postgres Service

**Required Environment Variables:**
```
POSTGRES_USER=odoo
POSTGRES_PASSWORD=<your-secure-password>
POSTGRES_DB=odoo
PGDATA=/var/lib/postgresql/data/pgdata
```

**Client Variables:**
```
PGHOST=postgres.railway.internal
PGPORT=5432
PGUSER=${POSTGRES_USER}
PGPASSWORD=${POSTGRES_PASSWORD}
PGDATABASE=${POSTGRES_DB}
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${PGHOST}:${PGPORT}/${POSTGRES_DB}
```

**Note:** If there's a mismatch during deployment:
- Either delete the volume and redeploy
- Or run: `ALTER ROLE odoo WITH PASSWORD '<your-password>';`

### 2. Odoo Service (Railway)

**Environment Variables:**
```
DB_HOST=postgres.railway.internal
DB_PORT=5432
DB_USER=odoo
DB_PASSWORD=<same-as-postgres-password>
DB_NAME=odoo
DATABASE_URL=postgresql://odoo:<password>@postgres.railway.internal:5432/odoo
```

**Custom Start Command:**
```bash
# Wait for DB + enable proxy mode
./docker-entrypoint.sh odoo --proxy-mode
```

**Health Check:** `/web/health`

### 3. ISO-22301 EventBus Service (Railway)

**Configuration:**
- ✅ `railway.json` disabled (renamed to `railway.json.disabled`)
- ✅ `nixpacks.toml` configured for EventBus deployment

**Environment Variables:**
```
DATABASE_URL=${{ Postgres.DATABASE_PRIVATE_URL }}
REDIS_URL=<your-redis-url>
POSTGRES_URL=${{ Postgres.DATABASE_PRIVATE_URL }}
```

**Custom Start Command:**
```bash
cd backend/eventbus && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Health Check:** `/health`

### 4. Vercel Frontend Configuration

**Environment Variables to set in Vercel Dashboard:**
```
NEXT_PUBLIC_API_URL=https://<iso-22301-service>.up.railway.app
VITE_API_URL=https://<iso-22301-service>.up.railway.app
NEXT_PUBLIC_ODOO_URL=https://<odoo-service>.up.railway.app
VITE_ODOO_URL=https://<odoo-service>.up.railway.app
NEXT_PUBLIC_SUPABASE_URL=<your-supabase-url>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-supabase-anon-key>
```

## Deployment Steps

1. **Create Postgres Service:**
   - Add environment variables as listed above
   - Note the DATABASE_PRIVATE_URL for other services

2. **Deploy Odoo Service:**
   - Set database connection variables
   - Configure custom start command with `--proxy-mode`
   - Deploy and get the service URL

3. **Deploy ISO-22301 EventBus:**
   - Repository automatically uses `nixpacks.toml` (railway.json is disabled)
   - Set DATABASE_URL to reference Postgres service
   - Set REDIS_URL to your Redis provider
   - Deploy and get the service URL

4. **Configure Frontend on Vercel:**
   - Set API URLs to point to deployed Railway services
   - Trigger redeploy

## Service Architecture

```
Vercel Frontend → Railway EventBus → Railway Postgres
                     ↓
               Railway Odoo → Railway Postgres
                     ↓
               External Redis
```

## Health Checks

- EventBus: `GET /health`
- Odoo: `GET /web/health`
- Frontend: Standard Vercel health checks

## Notes

- The EventBus service is configured to run on Railway using nixpacks
- railway.json has been disabled to prevent conflicts
- All services share the same Postgres database
- Redis can be external (Upstash) or a separate Railway service