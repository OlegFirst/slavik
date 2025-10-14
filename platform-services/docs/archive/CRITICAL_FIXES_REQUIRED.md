# КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ ПЕРЕД ЗАПУСКОМ
## Platform Services - Critical Issues & Fix Plan

**Дата**: 2025-10-10
**Приоритет**: 🚨 БЛОКИРУЮЩИЕ ПРОБЛЕМЫ

---

## 🔴 БЛОКИРУЮЩИЕ ПРОБЛЕМЫ (ИСПРАВИТЬ НЕМЕДЛЕННО)

### 1. Governance Service - Port Conflict ⚠️

**Проблема**: Конфликт портов между config и документацией

**Детали**:
- В `config.py`: `SERVICE_PORT = 8020`
- В `PORT_ALLOCATION.md`: должен быть `8013`
- Порт `8020` занят Workflow Intelligence

**Файл**: `/Users/MD/AI-Platform-ISO/platform-services/governance-service/config.py`

**Исправление**:
```python
# Line 17 - изменить с:
SERVICE_PORT: int = 8020

# на:
SERVICE_PORT: int = 8013
```

**Команда**:
```bash
cd /Users/MD/AI-Platform-ISO/platform-services/governance-service
sed -i '' 's/SERVICE_PORT: int = 8020/SERVICE_PORT: int = 8013/' config.py
```

**Проверка**:
```bash
grep "SERVICE_PORT" config.py
# Должно показать: SERVICE_PORT: int = 8013
```

**Воздействие**: БЕЗ ИСПРАВЛЕНИЯ сервис не запустится (порт занят)

---

### 2. Plans Service - Syntax Error ⚠️

**Проблема**: Python syntax error - неверная индентация

**Детали**:
- Line 69: `global` statement имеет неверный отступ
- Python выдаст `IndentationError` при импорте

**Файл**: `/Users/MD/AI-Platform-ISO/platform-services/plans_service/main.py`

**Исправление**:
```python
# Line 69 - текущий код (НЕВЕРНО):
global audit_logger, iso_checker, security_middleware

# Должно быть (добавить 4 пробела):
    global audit_logger, iso_checker, security_middleware
```

**Команда**:
```bash
cd /Users/MD/AI-Platform-ISO/platform-services/plans_service
# Ручное исправление в редакторе - line 69
# Добавить 4 пробела перед "global"
```

**Проверка**:
```bash
python -m py_compile main.py
# Не должно быть ошибок
```

**Воздействие**: БЕЗ ИСПРАВЛЕНИЯ сервис не запустится вообще (syntax error)

---

### 3. Rename /мониторинг Directory 📁

**Проблема**: Кириллическое название создает путаницу с `/monitoring`

**Детали**:
- `/monitoring` = Prometheus/Grafana config files (НЕ сервис)
- `/мониторинг` = 2 активных микросервиса (compliance-monitoring + process-analytics)
- Кириллица в названии неудобна в терминале и git

**Текущая структура**:
```
/мониторинг/
├── compliance-monitoring/  (port 8779)
│   └── main.py
└── process-analytics/      (port 8780)
    └── main.py
```

**Рекомендованное действие** (Option 1 - переименование):
```bash
cd /Users/MD/AI-Platform-ISO/platform-services
mv мониторинг compliance-monitoring-services
```

**ИЛИ** (Option 2 - разделение на 2 сервиса):
```bash
cd /Users/MD/AI-Platform-ISO/platform-services
mkdir compliance-monitoring-service
mkdir process-analytics-service
mv мониторинг/compliance-monitoring/* compliance-monitoring-service/
mv мониторинг/process-analytics/* process-analytics-service/
rm -rf мониторинг
```

**Воздействие**: Не блокирует запуск, но создает путаницу при разработке

---

## 🟡 ВАЖНЫЕ ИСПРАВЛЕНИЯ (ВЫСОКИЙ ПРИОРИТЕТ)

### 4. Shared Library Imports - Portal & Marketplace

**Проблема**: Импорты из `shared.eventbus` не найдут модуль

**Затронутые сервисы**:
- `community-service/portal/main.py` (line 21)
- `community-service/marketplace/main.py` (line 22)
- Оба сервиса: `events/subscribers.py` (line 14)

**Текущий импорт**:
```python
from shared.eventbus import EventBusClient
```

**Проблема**: `shared` находится в project root, не в `platform-services/`

**Fix Option 1** - Установить как package:
```bash
cd /Users/MD/AI-Platform-ISO
pip install -e shared/
```

**Fix Option 2** - sys.path manipulation:
```python
# В начале main.py каждого сервиса:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
```

**Fix Option 3** - Relative imports:
```python
# Изменить импорты на:
from community-service.shared.eventbus import EventBusClient
```

**Воздействие**: Сервисы запустятся, но EventBus интеграция не будет работать

---

### 5. Database Migrations

**Проблема**: Сервисы проверяют наличие schema, но НЕ создают автоматически

**Затронутые сервисы**: ВСЕ (кроме portal/marketplace с Supabase)

**Действие**:
```bash
# Для каждого сервиса проверить наличие migrations/
cd /Users/MD/AI-Platform-ISO/platform-services

# Пример для BIA Service:
psql -h localhost -U bcm -d bcm_platform << EOF
CREATE SCHEMA IF NOT EXISTS bia;
CREATE TABLE IF NOT EXISTS bia.bia_processes (...);
-- И т.д.
EOF
```

**ИЛИ использовать Alembic**:
```bash
# Если есть alembic/
alembic upgrade head
```

**Воздействие**: Сервисы запустятся, но выдадут warnings и не будут работать корректно

---

### 6. Environment Variables Configuration

**Проблема**: Каждый сервис требует свои env vars, нет централизованного .env

**Создать**: `/Users/MD/AI-Platform-ISO/platform-services/.env`

**Минимально необходимые переменные**:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://bcm:bcm_password@localhost:5432/bcm_platform

# Supabase (for Portal/Marketplace)
SUPABASE_URL=https://tpdkhddtbhpoqzzgxfni.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ / EventBus
EVENTBUS_URL=amqp://guest:guest@localhost:5672
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
JWT_ALGORITHM=HS256

# Service URLs (для интеграций)
ORCHESTRATOR_URL=http://localhost:8002
CLIENTS_SERVICE_URL=http://localhost:8030
AI_ORCHESTRATION_URL=http://localhost:8002

# Optional AI Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Logging
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

**Применить для всех сервисов**:
```bash
# В каждом main.py добавить:
from dotenv import load_dotenv
load_dotenv("../.env")  # или platform-services/.env
```

**Воздействие**: Сервисы могут не запуститься из-за отсутствия обязательных переменных

---

## 🟢 РЕКОМЕНДАЦИИ (СРЕДНИЙ ПРИОРИТЕТ)

### 7. Workflow Intelligence Package Installation

**Проблема**: Локальная зависимость от `../../intelligent-core/workflow-intelligence`

**Затронуто**: Почти ВСЕ ISO сервисы

**Решение**:
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/workflow-intelligence
pip install -e .
```

**ИЛИ добавить в requirements.txt**:
```
workflow-intelligence @ file:///Users/MD/AI-Platform-ISO/intelligent-core/workflow-intelligence
```

---

### 8. Redis для Validation Service

**Проблема**: Validation Service ТРЕБУЕТ Redis для Celery tasks

**Celery использование**:
- Auto-collection KPIs (каждые 24 часа)
- Alert checking (каждый час)
- Background task processing

**Установка Redis**:
```bash
# macOS:
brew install redis
brew services start redis

# Docker:
docker run -d -p 6379:6379 redis:7-alpine

# Проверка:
redis-cli ping
# Должно вернуть: PONG
```

**Запуск Celery workers**:
```bash
cd /Users/MD/AI-Platform-ISO/platform-services/validation-service
celery -A tasks.celery_app worker --loglevel=info &
celery -A tasks.celery_app beat --loglevel=info &
```

---

### 9. Update PORT_ALLOCATION.md

**Проблема**: Документация портов может быть устаревшей после исправлений

**Действие**: Обновить `/Users/MD/AI-Platform-ISO/platform-services/docs/PORT_ALLOCATION.md`

**Проверить соответствие**:
```
BIA Service: 8012 ✓
Governance Service: 8013 ✓ (ПОСЛЕ ИСПРАВЛЕНИЯ)
Compliance Service: 8014 ✓
Planning Service: 8011 ✓
Plans Service: 8023 ✓
Learning Service: 8021 ✓
Response Service: 8041 ✓
Risk Service: 8040 ✓
Validation Service: 8022 ✓
Documents Service: 8024 ✓
Portal: 8033 ✓
Marketplace: 8032 ✓
Living Docs: 8034 ✓
Compliance Monitoring: 8779 ✓
Process Analytics: 8780 ✓
```

---

## ✅ CHECKLIST ПЕРЕД ПЕРВЫМ ЗАПУСКОМ

### Инфраструктура:
- [ ] PostgreSQL запущен и доступен
- [ ] Redis запущен (для Validation Service)
- [ ] RabbitMQ запущен (для EventBus)
- [ ] Созданы databases и schemas

### Исправления кода:
- [ ] ✅ Governance Service port изменен на 8013
- [ ] ✅ Plans Service syntax error исправлен (line 69)
- [ ] ✅ `/мониторинг` переименован в `/compliance-monitoring-services`
- [ ] ✅ Shared library установлен или sys.path настроен

### Конфигурация:
- [ ] `.env` файл создан с всеми необходимыми переменными
- [ ] JWT_SECRET установлен (минимум 32 символа)
- [ ] Database migrations выполнены
- [ ] Workflow Intelligence package установлен

### Проверка перед запуском каждого сервиса:
```bash
# Проверка Python syntax:
python -m py_compile main.py

# Проверка импортов:
python -c "import sys; sys.path.insert(0, '..'); from main import app; print('OK')"

# Проверка database connection:
psql -h localhost -U bcm -d bcm_platform -c "SELECT 1;"

# Проверка Redis:
redis-cli ping

# Проверка RabbitMQ:
curl -u guest:guest http://localhost:15672/api/overview
```

---

## 🚀 QUICK FIX SCRIPT

Создай и выполни этот скрипт для автоматического исправления:

```bash
#!/bin/bash
# quick_fix_platform_services.sh

set -e

echo "🔧 Platform Services Quick Fix Script"
echo "======================================"

# 1. Fix Governance Service Port
echo "1️⃣ Fixing Governance Service port conflict..."
cd /Users/MD/AI-Platform-ISO/platform-services/governance-service
sed -i '' 's/SERVICE_PORT: int = 8020/SERVICE_PORT: int = 8013/' config.py
echo "   ✅ Governance port fixed (8013)"

# 2. Fix Plans Service Syntax (manual step - показать где)
echo "2️⃣ Plans Service syntax error - MANUAL FIX REQUIRED:"
echo "   📝 File: /Users/MD/AI-Platform-ISO/platform-services/plans_service/main.py"
echo "   📝 Line 69: Add 4 spaces before 'global audit_logger...'"
echo "   Press Enter when fixed..."
read

# 3. Rename мониторинг
echo "3️⃣ Renaming /мониторинг to /compliance-monitoring-services..."
cd /Users/MD/AI-Platform-ISO/platform-services
if [ -d "мониторинг" ]; then
    mv мониторинг compliance-monitoring-services
    echo "   ✅ Renamed successfully"
else
    echo "   ⚠️ Directory not found or already renamed"
fi

# 4. Install Workflow Intelligence
echo "4️⃣ Installing Workflow Intelligence package..."
cd /Users/MD/AI-Platform-ISO/intelligent-core/workflow-intelligence
pip install -e .
echo "   ✅ Workflow Intelligence installed"

# 5. Create .env template
echo "5️⃣ Creating .env template..."
cd /Users/MD/AI-Platform-ISO/platform-services
cat > .env.template << 'EOF'
# Database
DATABASE_URL=postgresql+asyncpg://bcm:PASSWORD@localhost:5432/bcm_platform

# Supabase
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=YOUR_ANON_KEY

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
EVENTBUS_URL=amqp://guest:guest@localhost:5672

# JWT
JWT_SECRET_KEY=CHANGE_THIS_TO_STRONG_SECRET_MIN_32_CHARS

# Service URLs
ORCHESTRATOR_URL=http://localhost:8002
CLIENTS_SERVICE_URL=http://localhost:8030

# Logging
LOG_LEVEL=INFO
EOF
echo "   ✅ .env.template created - CONFIGURE IT!"

echo ""
echo "======================================"
echo "✅ Quick fixes applied!"
echo ""
echo "⚠️  MANUAL STEPS REMAINING:"
echo "   1. Fix Plans Service syntax (line 69)"
echo "   2. Configure .env from .env.template"
echo "   3. Run database migrations"
echo "   4. Start infrastructure (PostgreSQL, Redis, RabbitMQ)"
echo ""
echo "Then run: bash check_services.sh"
```

**Запуск**:
```bash
chmod +x quick_fix_platform_services.sh
./quick_fix_platform_services.sh
```

---

## 📊 СТАТУС ИСПРАВЛЕНИЙ

| Проблема | Приоритет | Автофикс | Время |
|----------|-----------|----------|-------|
| Governance port conflict | 🔴 Блокирующая | ✅ Да | 1 мин |
| Plans syntax error | 🔴 Блокирующая | ⚠️ Ручное | 1 мин |
| Rename /мониторинг | 🔴 Блокирующая | ✅ Да | 1 мин |
| Shared library imports | 🟡 Важная | ✅ Да | 2 мин |
| Database migrations | 🟡 Важная | ⚠️ Ручное | 10 мин |
| .env configuration | 🟡 Важная | ✅ Template | 5 мин |
| Workflow Intelligence | 🟢 Рекомендация | ✅ Да | 2 мин |
| Redis setup | 🟢 Рекомендация | ⚠️ Brew/Docker | 5 мин |

**Общее время на исправления**: ~30 минут

---

## 📝 NOTES

- Все блокирующие проблемы можно исправить за 3 минуты
- База данных и environment variables требуют ручной настройки
- После исправлений все сервисы готовы к запуску
- Рекомендуется запускать сервисы последовательно для отладки

**Следующий документ**: `STARTUP_GUIDE.md` - детальная инструкция по запуску

---

**Создано**: 2025-10-10
**Приоритет**: 🚨 КРИТИЧЕСКИЙ
**Статус**: ТРЕБУЕТ ДЕЙСТВИЙ
