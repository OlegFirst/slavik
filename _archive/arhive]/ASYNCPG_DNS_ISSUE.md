# asyncpg DNS Resolution Issue

## Problem
`asyncpg` cannot resolve Supabase Session pooler hostname, while `psycopg2` works fine.

## Symptoms
```
Error: [Errno 8] nodename nor servname provided, or not known
Host: aws-1-eu-north-1.pooler.supabase.com:5432
```

## Evidence
✅ **DNS resolves correctly:**
```bash
nslookup aws-1-eu-north-1.pooler.supabase.com
# Returns: 51.21.18.29, 13.60.102.132
```

✅ **psycopg2 works:**
```python
# All 18 migrations applied successfully via psycopg2
conn = psycopg2.connect(
    host='aws-1-eu-north-1.pooler.supabase.com',
    port=5432,
    user='postgres.tpdkhddtbhpoqzzgxfni',
    password='K@x3ta9V8GK5rnW',
    sslmode='require'
)
# ✅ SUCCESS
```

❌ **asyncpg fails:**
```python
from sqlalchemy.ext.asyncio import create_async_engine
url = 'postgresql+asyncpg://postgres.tpdkhddtbhpoqzzgxfni:K@x3ta9V8GK5rnW@aws-1-eu-north-1.pooler.supabase.com:5432/postgres'
engine = create_async_engine(url)
# ❌ [Errno 8] nodename nor servname provided, or not known
```

## Possible Causes
1. **asyncpg DNS resolution bug** on macOS Darwin 23.6.0
2. **asyncpg IPv6/IPv4 preference** issue (ELB returns both)
3. **asyncio event loop DNS cache** issue

## Solutions to Try
1. **Use IP address directly** instead of hostname
2. **Force IPv4** in asyncpg connection
3. **Try alternative async driver** (psycopg3 async mode)
4. **Use psycopg2 with threading** instead of asyncpg
5. **Check asyncpg version** and update to latest

## Impact
- ⚠️ Blocks production services using async SQLAlchemy
- ✅ Migrations work (using psycopg2)
- ✅ Can use psycopg2 for services as fallback

## Environment
- OS: macOS Darwin 23.6.0
- Database: Supabase PostgreSQL (Session pooler)
- Working: psycopg2
- Failing: asyncpg + SQLAlchemy async

## Next Steps
Local agent should investigate and fix asyncpg DNS resolution issue.
