# Migration Guide: Services to Supabase Vault

## ✅ Completed

### Phase 1: Vault Infrastructure
- [x] Supabase Vault extension enabled
- [x] 4 secrets created in Vault:
  - `jwt-secret` - JWT signing key (86 chars)
  - `anthropic-api-key` - Claude API key
  - `redis-password` - Upstash Redis password
  - `database-password` - PostgreSQL password
- [x] `public.get_secret()` function created
- [x] VaultClient Python library created (`vault_client.py`)
- [x] Secrets Management Service (HTTP API) created on port 8062

## 🔄 Migration Steps for Each Service

### Step 1: Add VaultClient to Service

```python
# Add to requirements.txt
psycopg2-binary>=2.9.0

# In your main.py or config.py
import os
import sys

# Add vault_client to path (or install as package)
sys.path.insert(0, '/Users/MD/AI-Platform-ISO/infrastructure/security/secrets-management')
from vault_client import get_secret

# Replace hardcoded secrets
# OLD:
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# NEW:
ANTHROPIC_API_KEY = get_secret("anthropic-api-key")
```

### Step 2: Update .env File

Remove secrets from .env, keep only non-sensitive config:

```bash
# .env - REMOVE these:
# ANTHROPIC_API_KEY=sk-ant-...  ❌ DELETE
# JWT_SECRET=...                ❌ DELETE
# REDIS_PASSWORD=...            ❌ DELETE

# .env - KEEP these:
DATABASE_URL=postgresql://...    ✅ KEEP (used by VaultClient)
SERVICE_PORT=8080                ✅ KEEP
DEBUG=false                      ✅ KEEP
```

### Step 3: Test Secret Retrieval

```python
# Test script
from vault_client import get_vault_client

vault = get_vault_client()

# List available secrets
secrets = vault.list_secrets()
print(f"Available secrets: {[s['name'] for s in secrets]}")

# Get specific secret
jwt_secret = vault.get_secret('jwt-secret')
print(f"JWT Secret length: {len(jwt_secret)} chars")
```

### Step 4: Update Service Startup

```python
# main.py
import logging
from vault_client import get_secret

logger = logging.getLogger(__name__)

# Load secrets at startup
try:
    ANTHROPIC_API_KEY = get_secret("anthropic-api-key")
    JWT_SECRET = get_secret("jwt-secret")
    logger.info("✅ Secrets loaded from Vault")
except Exception as e:
    logger.error(f"❌ Failed to load secrets: {e}")
    raise
```

## 📋 Services to Migrate

### Priority 1: Core Services (Use Anthropic API or JWT)
1. **AI Orchestrator** (`intelligent-core/orchestration/ai-orchestration/`)
   - Needs: `anthropic-api-key`, `jwt-secret`
   - Files: `orchestrator.py`, `config.py`

2. **Learning & Knowledge** (`intelligent-core/ai-foundation/learning-knowledge/`)
   - Needs: `anthropic-api-key`
   - Files: `main.py`

3. **Analytics Specialist** (`infrastructure/AI-office-infrastructure/analytics-specialist/`)
   - Needs: `anthropic-api-key`, `redis-password`
   - Files: `main.py`, `config/settings.py`

### Priority 2: AI Office Infrastructure
4. **AI Event Manager** (`infrastructure/AI-office-infrastructure/ai-event-manager/`)
   - Needs: `redis-password`
   - Files: `main.py`

5. **MIO Manager** (`infrastructure/AI-office-infrastructure/mio-manager/`)
   - Needs: `redis-password`, `database-password`
   - Files: `main.py`

6. **Agent Router** (`infrastructure/AI-office-infrastructure/agent-router/`)
   - Needs: `anthropic-api-key`
   - Files: `main.py`

### Priority 3: Platform Services
7. **BIA Service** (`platform-services/bia_service/`)
   - Needs: `database-password`, `anthropic-api-key`
   - Files: `main.py`

8. **Governance Service** (`platform-services/governance-service/`)
   - Needs: `database-password`
   - Files: `main.py`, `config.py`

9. **Plans Service** (`platform-services/plans_service/`)
   - Needs: `database-password`
   - Files: `main.py`

### Priority 4: Infrastructure Services
10. **Auth Service** (`infrastructure/security/auth/`)
    - Needs: `jwt-secret`, `database-password`
    - Files: `main.py`

11. **Message Queue** (`infrastructure/runtime/message-queue/`)
    - Needs: `redis-password`
    - Files: `main.py`

12. **EventBus** (`infrastructure/eventbus/`)
    - Needs: `redis-password`
    - Files: `eventbus.py`

13. **Service Discovery** (`infrastructure/runtime/service-discovery/`)
    - Needs: `redis-password`
    - Files: `main.py`

14. **Realtime WebSocket** (`infrastructure/runtime/realtime-websocket/`)
    - Needs: `redis-password`, `jwt-secret`
    - Files: `main.py`

15. **Balancer Service** (`infrastructure/balancer-service/`)
    - Needs: `redis-password`
    - Files: `main.py`

## 🔒 Security Best Practices

### DO ✅
- Use `get_secret()` for all sensitive data
- Keep `DATABASE_URL` in .env (needed by VaultClient)
- Log secret retrieval (not values!)
- Handle `ValueError` when secret not found
- Test locally before deploying

### DON'T ❌
- Don't commit `.env` files with secrets
- Don't log secret values
- Don't cache secrets in global variables (VaultClient has LRU cache)
- Don't use hardcoded fallback secrets in production

## 🧪 Testing

### Test VaultClient Locally
```bash
# Set DATABASE_URL
export DATABASE_URL="postgresql://postgres.tpdkhddtbhpoqzzgxfni:K%40x3ta9V8GK5rnW@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

# Test VaultClient
python3 infrastructure/security/secrets-management/vault_client.py
```

### Test Service with VaultClient
```bash
# Update service to use VaultClient
# Run service
python3 main.py

# Check logs for "✅ Secrets loaded from Vault"
```

## 📊 Migration Progress

- [ ] AI Orchestrator
- [ ] Learning & Knowledge
- [ ] Analytics Specialist
- [ ] AI Event Manager
- [ ] MIO Manager
- [ ] Agent Router
- [ ] BIA Service
- [ ] Governance Service
- [ ] Plans Service
- [ ] Auth Service
- [ ] Message Queue
- [ ] EventBus
- [ ] Service Discovery
- [ ] Realtime WebSocket
- [ ] Balancer Service

## 🆘 Troubleshooting

### Error: `Secret 'xxx' not found in Vault`
**Solution**: Check available secrets:
```bash
PGPASSWORD='K@x3ta9V8GK5rnW' psql -h aws-1-eu-north-1.pooler.supabase.com -U postgres.tpdkhddtbhpoqzzgxfni -d postgres -p 5432 -c "SELECT name, description FROM vault.decrypted_secrets;"
```

### Error: `connection to server failed: password authentication failed`
**Solution**: Check DATABASE_URL is set correctly with URL-encoded password (`@` = `%40`)

### Error: `ModuleNotFoundError: No module named 'psycopg2'`
**Solution**: Install psycopg2:
```bash
pip3 install psycopg2-binary
```

## 📝 Notes

- VaultClient uses LRU cache (maxsize=100) for performance
- Secrets are decrypted on-the-fly by `public.get_secret()` function
- Database password in DATABASE_URL is used to connect to Vault
- All secrets are encrypted at rest in Supabase Vault
