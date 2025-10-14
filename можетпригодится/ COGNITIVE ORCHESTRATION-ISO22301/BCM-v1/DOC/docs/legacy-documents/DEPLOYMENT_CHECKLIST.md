# Deployment Checklist

## ✅ Code Changes Completed

All necessary code changes have been implemented for Railway deployment:

### 1. ISO-22301 EventBus Service
- ✅ `railway.json` disabled (renamed to `railway.json.disabled`)
- ✅ `nixpacks.toml` configured for EventBus-only deployment  
- ✅ Start command: `cd backend/eventbus && uvicorn main:app --host 0.0.0.0 --port $PORT`
- ✅ Health endpoint available at `/health`
- ✅ Ready for Railway deployment with DATABASE_URL and REDIS_URL variables

### 2. Documentation Updated
- ✅ `RAILWAY_DEPLOYMENT.md` - Complete setup guide for all services
- ✅ `VERCEL_ENV_SETUP.md` - Updated with Railway service URLs

## 🚀 Next Steps (Railway Dashboard)

### 1. Deploy Postgres Service
```
POSTGRES_USER=odoo
POSTGRES_PASSWORD=<secure-password>
POSTGRES_DB=odoo
PGDATA=/var/lib/postgresql/data/pgdata
```

### 2. Deploy Odoo Service  
```
DB_HOST=postgres.railway.internal
DB_PORT=5432
DB_USER=odoo
DB_PASSWORD=<same-as-postgres>
DB_NAME=odoo
DATABASE_URL=postgresql://odoo:<password>@postgres.railway.internal:5432/odoo
```
Custom Start Command: `./docker-entrypoint.sh odoo --proxy-mode`

### 3. Deploy ISO-22301 Service
- Repository will auto-use `nixpacks.toml` 
- Set variables:
```
DATABASE_URL=${{ Postgres.DATABASE_PRIVATE_URL }}
REDIS_URL=<redis-connection-string>
```

### 4. Configure Vercel Frontend
Set environment variables in Vercel dashboard:
```
NEXT_PUBLIC_API_URL=https://<iso-22301-service>.up.railway.app
VITE_API_URL=https://<iso-22301-service>.up.railway.app  
NEXT_PUBLIC_ODOO_URL=https://<odoo-service>.up.railway.app
VITE_ODOO_URL=https://<odoo-service>.up.railway.app
```

## 🔧 Configuration Ready

The repository is now properly configured for Railway deployment. The EventBus service will:
- Build using nixpacks (railway.json disabled)
- Install Python dependencies automatically  
- Start with the correct uvicorn command
- Expose health checks at `/health`
- Connect to Postgres and Redis via environment variables

All that's needed now is to create the services in Railway dashboard and set the environment variables as documented.