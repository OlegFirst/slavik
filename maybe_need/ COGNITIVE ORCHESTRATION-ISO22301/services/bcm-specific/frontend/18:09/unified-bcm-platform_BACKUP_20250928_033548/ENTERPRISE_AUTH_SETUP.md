# 🔐 ENTERPRISE AUTHENTICATION SETUP GUIDE

## **📋 OVERVIEW**

Система аутентификации BCM Platform интегрирует **4 ключевых сервиса**:
- **Keycloak** - Enterprise SSO (Single Sign-On)
- **Odoo PostgreSQL** - Бизнес-данные и permissions
- **Supabase** - AI сервисы и real-time
- **Redis** - Кэширование и связка сервисов

---

## **🏗️ АРХИТЕКТУРА АУТЕНТИФИКАЦИИ**

```typescript
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FRONTEND      │    │    KEYCLOAK     │    │      ODOO       │
│   (Next.js)     │◄──►│  (Master Auth)  │◄──►│  (Business DB)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └─────────────►│    SUPABASE     │◄─────────────┘
                        │  (AI/Real-time) │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │     REDIS       │
                        │ (Cache/Session) │
                        └─────────────────┘
```

---

## **⚡ БЫСТРЫЙ СТАРТ**

### **1. Копирование конфигурации:**
```bash
cd /Users/MD/ISO-22301/frontend/unified-bcm-platform
cp .env.local.example .env.local
```

### **2. Основные настройки (.env.local):**
```bash
# Keycloak SSO
NEXT_PUBLIC_KEYCLOAK_URL=http://localhost:8080
NEXT_PUBLIC_KEYCLOAK_REALM=bcm-platform
NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=bcm-frontend

# Odoo Business Backend
NEXT_PUBLIC_ODOO_URL=http://localhost:8069
NEXT_PUBLIC_ODOO_DB=bcm_production

# Supabase AI/Real-time
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Redis Cache
NEXT_PUBLIC_REDIS_URL=redis://localhost:6379
```

### **3. Запуск платформы:**
```bash
npm run dev  # http://localhost:3002
```

---

## **🔧 ДЕТАЛЬНАЯ НАСТРОЙКА**

### **KEYCLOAK CONFIGURATION**

1. **Создание Realm:**
```bash
# В Keycloak Admin Console:
1. Create new realm: "bcm-platform"
2. Create client: "bcm-frontend"
3. Client settings:
   - Client Protocol: openid-connect
   - Access Type: public
   - Valid Redirect URIs: http://localhost:3002/*
   - Web Origins: http://localhost:3002
```

2. **Пользователи и роли:**
```bash
# Создать роли:
- super_admin (полный доступ)
- org_admin (администратор организации)
- manager (менеджер)
- analyst (аналитик)
- viewer (только просмотр)

# Создать группы:
- BCM_Admins → super_admin role
- Organization_Admins → org_admin role
- BCM_Managers → manager role
- BCM_Analysts → analyst role
- BCM_Viewers → viewer role
```

### **ODOO BACKEND INTEGRATION**

1. **Настройка модулей BCM:**
```python
# В odoo.conf:
[options]
addons_path = /path/to/odoo/addons,/path/to/bcm/addons

# Установить модули:
- bcm_base (основной модуль)
- bcm_authentication (интеграция с Keycloak)
- bcm_api (REST API endpoints)
- bcm_multi_tenant (multi-tenancy)
```

2. **API endpoints для аутентификации:**
```python
# /web/session/authenticate - вход через Keycloak token
# /web/session/check - проверка сессии
# /web/session/logout - выход
# /api/user/permissions - права пользователя
# /api/user/company - данные компании
```

### **SUPABASE AI/REAL-TIME**

1. **Создание проекта:**
```sql
-- Таблицы для AI контекста:
CREATE TABLE user_ai_context (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  keycloak_id TEXT,
  odoo_user_id INTEGER,
  ai_preferences JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Real-time каналы:
CREATE TABLE realtime_channels (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  channel_name TEXT,
  company_id INTEGER,
  user_permissions TEXT[],
  created_at TIMESTAMP DEFAULT NOW()
);
```

2. **Row Level Security (RLS):**
```sql
-- Изоляция по компаниям
ALTER TABLE user_ai_context ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only see their own data" ON user_ai_context
  FOR ALL USING (auth.uid() = user_id);
```

### **REDIS CACHE/SESSION**

1. **Настройка Redis:**
```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

2. **Ключи кэширования:**
```bash
# Формат ключей: {company_id}:{user_id}:{resource}
# Примеры:
1:42:user_profile          # Профиль пользователя
1:42:permissions           # Права доступа
1:42:analytics_dashboard   # Кэш дашборда
1:*:company_data          # Данные компании
```

---

## **🚀 ИСПОЛЬЗОВАНИЕ В КОДЕ**

### **1. Компонент с аутентификацией:**
```typescript
import { useAuth, ProtectedRoute } from '@/components/auth/AuthProvider'

function MyComponent() {
  const { user, hasPermission, executeOdooQuery } = useAuth()

  return (
    <ProtectedRoute requiredPermission="bcm.read_bia">
      <div>Привет, {user?.firstName}!</div>
    </ProtectedRoute>
  )
}
```

### **2. API запросы с multi-tenancy:**
```typescript
import { unifiedApi } from '@/lib/api/unified-api-client'

// Автоматически добавляется company_id фильтр
const biaData = await unifiedApi.getBcmData('bia', 'search_read')

// Odoo запрос с компанией
const risks = await unifiedApi.odoo('bcm.risk_assessment', 'search_read')

// Supabase с изоляцией пользователей
const aiAnalysis = await unifiedApi.supabase('ai_analysis', 'select')
```

### **3. Real-time подписки:**
```typescript
// Подписка на updates по компании
const subscription = await unifiedApi.subscribeToUpdates(
  'incident_alerts',
  (data) => {
    console.log('Новый инцидент:', data)
  },
  { severity: 'high' }
)
```

---

## **🔒 БЕЗОПАСНОСТЬ**

### **Multi-Tenant Isolation:**
```typescript
// Каждый запрос автоматически фильтруется:
const userCompanyId = getCurrentUser().companyId

// Odoo queries:
domain.push(['company_id', '=', userCompanyId])

// Supabase RLS:
WHERE company_id = current_user_company_id()

// Redis keys:
const key = `${companyId}:${userId}:${resource}`
```

### **Role-Based Access Control:**
```typescript
// Проверка permissions:
if (!hasPermission('bcm.write_risk_assessment')) {
  throw new Error('Access denied')
}

// UI guards:
<RoleGuard roles={['org_admin', 'manager']}>
  <AdminPanel />
</RoleGuard>

<PermissionGuard permissions={['bcm.read_incidents']}>
  <IncidentList />
</PermissionGuard>
```

### **Session Management:**
```typescript
// Автоматическое обновление токенов
// Timeout sessions после неактивности
// Logout из всех сервисов одновременно
await unifiedAuth.logout() // Keycloak + Supabase + Redis
```

---

## **📊 МОНИТОРИНГ**

### **Health Checks:**
```typescript
// Проверка всех сервисов:
const health = await Promise.all([
  fetch('/api/keycloak/health'),
  fetch('/api/odoo/health'),
  fetch('/api/supabase/health'),
  fetch('/api/redis/health')
])
```

### **Audit Logging:**
```typescript
// Все действия логируются:
- Who: user_id, keycloak_id
- What: action, resource, changes
- When: timestamp
- Where: IP, user_agent
- Company: company_id (isolation)
```

---

## **🚨 TROUBLESHOOTING**

### **Частые проблемы:**

1. **Keycloak не отвечает:**
```bash
# Проверить статус:
curl http://localhost:8080/auth/realms/bcm-platform

# Логи:
docker logs keycloak_container
```

2. **Odoo session expired:**
```typescript
// Автоматический refresh в коде:
try {
  await odooQuery()
} catch (error) {
  if (error.code === 'session_expired') {
    await refreshSession()
    return odooQuery() // retry
  }
}
```

3. **Supabase RLS блокирует:**
```sql
-- Проверить политики:
SELECT * FROM pg_policies WHERE tablename = 'your_table';

-- Отладка:
SET rls.debug_level = 'debug';
```

4. **Redis connection issues:**
```bash
# Проверить подключение:
redis-cli ping

# Мониторинг:
redis-cli monitor
```

---

## **📈 PERFORMANCE OPTIMIZATION**

### **Кэширование:**
```typescript
// User profile - 1 час
await cache('user_profile', 'set', userData, 3600)

// Permissions - 15 минут
await cache('user_permissions', 'set', permissions, 900)

// Analytics - 5 минут
await cache('dashboard_data', 'set', analytics, 300)
```

### **Connection Pooling:**
```bash
# PostgreSQL (Odoo):
max_connections = 100
shared_buffers = 256MB

# Redis:
tcp-keepalive = 300
timeout = 300
```

---

## **🎯 PRODUCTION CHECKLIST**

### **Security:**
- [ ] HTTPS включен для всех сервисов
- [ ] JWT secrets сгенерированы криптографически
- [ ] Database credentials защищены
- [ ] Rate limiting настроен
- [ ] Audit logging включен

### **Performance:**
- [ ] Redis cache настроен
- [ ] Database indexes созданы
- [ ] Connection pooling настроен
- [ ] CDN для статики

### **Monitoring:**
- [ ] Health checks работают
- [ ] Logs централизованы
- [ ] Alerts настроены
- [ ] Backup процедуры работают

### **Compliance:**
- [ ] GDPR соответствие
- [ ] SOX audit trail
- [ ] Data retention policies
- [ ] Access reviews process

---

**🎉 ГОТОВО! ENTERPRISE AUTHENTICATION НАСТРОЕН!**

Теперь у вас есть полноценная enterprise система аутентификации с:
- ✅ Single Sign-On через Keycloak
- ✅ Multi-tenant изоляция данных
- ✅ Role-based access control
- ✅ Real-time capabilities
- ✅ Comprehensive audit trail
- ✅ Production-ready security