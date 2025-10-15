# Automated Service Registration System

**Дата создания**: 15 октября 2025
**Версия**: 1.0.0
**Статус**: ✅ Production Ready

---

## 📋 Обзор

Автоматическая система регистрации сервисов для AI Platform ISO. Обеспечивает:

- ✅ **Автоматическая регистрация** новых сервисов в каталоге
- ✅ **Управление портами** с проверкой конфликтов
- ✅ **Генерация шаблонов** кода для новых сервисов
- ✅ **Git pre-commit hook** для автоматической проверки
- ✅ **Отчеты по использованию портов**

---

## 🚀 Быстрый старт

### 1. Установка Git Hook

```bash
# Перейти в корень репозитория
cd /Users/MD/AI-Platform-ISO

# Скопировать hook в git hooks
cp .git-hooks/pre-commit-service-check.sh .git/hooks/pre-commit

# Сделать исполняемым
chmod +x .git/hooks/pre-commit

# Проверить установку
ls -la .git/hooks/pre-commit
```

### 2. Сделать скрипт регистрации исполняемым

```bash
chmod +x scripts/service-registry/auto_register_service.py
```

### 3. Первое использование

```bash
# Посмотреть использование портов
python3 scripts/service-registry/auto_register_service.py ports

# Зарегистрировать новый сервис
python3 scripts/service-registry/auto_register_service.py register
```

---

## 📖 Использование

### Команда: Port Usage Report

Показывает использование портов по всем сервисам:

```bash
python3 scripts/service-registry/auto_register_service.py ports
```

**Пример вывода**:
```
======================================================================
📊 PORT USAGE REPORT
======================================================================

PLATFORM_SERVICES
  Range: 8000-8099
  Used: 5/100 (5.0%)
  Available: 95
  Used ports: 8060, 8061, 8062, 8063, 8064

INTELLIGENT_CORE
  Range: 8100-8199
  Used: 0/100 (0.0%)
  Available: 100
  Used ports:

INFRASTRUCTURE
  Range: 8200-8299
  Used: 3/100 (3.0%)
  Available: 97
  Used ports: 8200, 8201, 8202

======================================================================
```

### Команда: Interactive Registration

Интерактивная регистрация нового сервиса:

```bash
python3 scripts/service-registry/auto_register_service.py register
```

**Процесс**:

1. **Service Name**: Имя сервиса (например, `my_awesome_service`)
2. **Service Type**: Тип сервиса (learning_infrastructure/ai_core/platform/integration)
3. **Description**: Описание сервиса
4. **Component**: Компонент (platform_services/intelligent_core/infrastructure)
5. **Port Selection**: Выбор порта из предложенных или ввод своего
6. **Location**: Расположение в проекте (по умолчанию: infrastructure/{service_name})
7. **Create Template**: Создать ли шаблон кода (y/n)

**Что создается**:

1. ✅ `/catalogs/platform-services/{service_name}.yaml` - запись в каталоге
2. ✅ Обновляется `SERVICE_CATALOG_DETAILED.yaml`
3. ✅ (Опционально) Шаблон сервиса:
   - `{location}/main.py` - FastAPI сервис
   - `{location}/requirements.txt` - зависимости
   - `{location}/README.md` - документация

---

## 🔧 Git Pre-Commit Hook

Автоматически проверяет новые сервисы при коммите.

### Что проверяет

1. **Новые сервисы**: Обнаруживает новые файлы `main.py` в:
   - `/infrastructure/*/main.py`
   - `/intelligent_core/*/main.py`
   - `/platform_services/*/main.py`

2. **Регистрация в каталоге**: Проверяет наличие записи в `/catalogs/platform-services/{service_name}.yaml`

3. **Hardcoded порты**: Предупреждает о хардкоде портов в коде

### Пример работы

```bash
git add infrastructure/my_new_service/main.py
git commit -m "Add new service"

# Hook запустится автоматически:
🔍 Checking for new services...
📦 Found new service: my_new_service (infrastructure/my_new_service)
❌ Service NOT registered in catalog: my_new_service

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ UNREGISTERED SERVICES DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The following services are not registered in the catalog:
  - my_new_service (infrastructure/my_new_service)

To register a service, run:
  python scripts/service-registry/auto_register_service.py register

Or skip this check (not recommended):
  git commit --no-verify

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Register services now? (y/n):
```

### Обход проверки (не рекомендуется)

```bash
git commit --no-verify -m "Skip hook check"
```

---

## 🎯 Port Ranges

Система автоматически назначает порты из диапазонов:

| Service Type | Port Range | Назначение |
|--------------|------------|------------|
| **platform_services** | 8000-8099 | Платформенные сервисы (ACE, etc.) |
| **intelligent_core** | 8100-8199 | AI модули (Orchestration, Predictive) |
| **infrastructure** | 8200-8299 | Инфраструктурные сервисы (Gateway, Discovery) |
| **integration** | 8300-8399 | Интеграционные сервисы (GitHub, MCP) |
| **monitoring** | 9000-9099 | Мониторинг (Prometheus, Grafana) |
| **databases** | 5000-5099 | База данных сервисы |

### Port Conflict Detection

Система проверяет порты:
1. ✅ В YAML каталогах (`/catalogs/**/*.yaml`)
2. ✅ В системе (через `lsof -i :PORT`)

---

## 📂 Структура создаваемых файлов

### Catalog Entry (`/catalogs/platform-services/{service_name}.yaml`)

```yaml
{service_name}:
  name: {service_name}
  display_name: {Service Name}
  registration:
    type: {service_type}
    status: development
    port: {assigned_port}
    version: 1.0.0
    environment: development
    created_date: '2025-10-15'

  description: |
    {service_description}

  purpose:
    - Purpose 1
    - Purpose 2

  capabilities:
    - Capability 1
    - Capability 2

  runtime:
    port: {assigned_port}
    protocol: HTTP/REST
    framework: FastAPI
    language: Python 3.11+
    health_endpoint: /health
    metrics_endpoint: /metrics

  dependencies:
    required: []
    optional: []

  deployment:
    location: /{location}/
    startup:
      command: python main.py
      environment_vars: []

  kpis: []

  monitoring:
    health_check: curl http://localhost:{port}/health
    metrics: curl http://localhost:{port}/metrics
    prometheus_job: {service_name}
```

### Service Template (`{location}/main.py`)

```python
"""
{Service Name} Service

Auto-generated service template
Port: {port}
"""

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import logging
import os
import uvicorn

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PORT = {port}
HOST = "0.0.0.0"

# Create FastAPI app
app = FastAPI(
    title="{Service Name} Service",
    description="Auto-generated service",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "{service_name}",
        "version": "1.0.0",
        "port": PORT
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "{Service Name}",
        "version": "1.0.0",
        "port": PORT,
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    logger.info(f"🚀 Starting {service_name} on port {PORT}")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
```

---

## 🔍 Примеры использования

### Пример 1: Регистрация простого сервиса

```bash
$ python3 scripts/service-registry/auto_register_service.py register

======================================================================
🎯 INTERACTIVE SERVICE REGISTRATION
======================================================================

Service name (e.g., my_service): analytics_service
Service type (learning_infrastructure/ai_core/platform/integration): platform
Description: Analytics and reporting service
Component (platform_services/intelligent_core/infrastructure): platform_services

📍 Suggested ports for platform_services:
  1. Port 8065
  2. Port 8066
  3. Port 8067
  4. Port 8068
  5. Port 8069

Select port (1-5) or enter custom: 1

Service location (default: infrastructure/analytics_service):

Create service code template? (y/n): y

🔄 Registering service...

======================================================================
📝 REGISTERING SERVICE: analytics_service
======================================================================

✅ Service registered: /Users/MD/AI-Platform-ISO/catalogs/platform-services/analytics_service.yaml
📍 Port assigned: 8065
🔗 Health check: http://localhost:8065/health

======================================================================

✅ Updated main catalog: /Users/MD/AI-Platform-ISO/catalogs/platform-services/SERVICE_CATALOG_DETAILED.yaml
✅ Created service template: /Users/MD/AI-Platform-ISO/infrastructure/analytics_service
   - main.py
   - requirements.txt
   - README.md

✅ Registration complete!

📝 Catalog entry: /Users/MD/AI-Platform-ISO/catalogs/platform-services/analytics_service.yaml
🔗 Health check: http://localhost:8065/health

Next steps:
  1. cd /Users/MD/AI-Platform-ISO/infrastructure/analytics_service
  2. pip install -r requirements.txt
  3. python main.py
```

### Пример 2: Только регистрация без шаблона

```bash
$ python3 scripts/service-registry/auto_register_service.py register

Service name: existing_service
Service type: platform
Description: Already existing service that needs catalog entry
Component: platform_services
Select port: 8070
Service location: infrastructure/existing_service

Create service code template? (y/n): n

✅ Registration complete!
```

### Пример 3: Port Usage Report

```bash
$ python3 scripts/service-registry/auto_register_service.py ports

======================================================================
📊 PORT USAGE REPORT
======================================================================

PLATFORM_SERVICES
  Range: 8000-8099
  Used: 6/100 (6.0%)
  Available: 94
  Used ports: 8060, 8061, 8062, 8063, 8064, 8065

INTELLIGENT_CORE
  Range: 8100-8199
  Used: 0/100 (0.0%)
  Available: 100

INFRASTRUCTURE
  Range: 8200-8299
  Used: 0/100 (0.0%)
  Available: 100

INTEGRATION
  Range: 8300-8399
  Used: 0/100 (0.0%)
  Available: 100

MONITORING
  Range: 9000-9099
  Used: 0/100 (0.0%)
  Available: 100

DATABASES
  Range: 5000-5099
  Used: 0/100 (0.0%)
  Available: 100

======================================================================
```

---

## 🛠️ Troubleshooting

### Проблема: "Port already in use"

**Решение**: Используйте команду `ports` чтобы найти свободный порт:

```bash
python3 scripts/service-registry/auto_register_service.py ports
```

### Проблема: Git hook не срабатывает

**Решение**: Проверьте установку hook:

```bash
# Проверить наличие
ls -la .git/hooks/pre-commit

# Переустановить
cp .git-hooks/pre-commit-service-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Проблема: "No module named 'yaml'"

**Решение**: Установите PyYAML:

```bash
pip3 install pyyaml
```

### Проблема: lsof команда не найдена (macOS/Linux)

**Решение**: Система автоматически fallback на проверку только каталогов. Это нормально.

---

## 📚 Дополнительная информация

### Files Created by This System

1. **`auto_register_service.py`** - Основной скрипт регистрации
2. **`pre-commit-service-check.sh`** - Git hook для проверки
3. **`README.md`** (этот файл) - Документация

### Dependencies

- Python 3.11+
- PyYAML
- Git
- (Опционально) lsof для проверки портов в системе

### Future Enhancements

- [ ] Support for batch registration (multiple services)
- [ ] Export/import catalog entries
- [ ] Validate YAML schema
- [ ] Check for duplicate service names
- [ ] Generate Docker Compose entries
- [ ] Integration with service discovery (Consul)
- [ ] Web UI for service registration

---

## 🎯 Best Practices

1. **Always register services** - Don't skip the catalog
2. **Use suggested ports** - They're conflict-free
3. **Create templates** - Start with working code
4. **Document your services** - Update generated README
5. **Don't bypass git hook** - It catches issues early

---

## 📞 Support

Если возникли проблемы:

1. Проверьте логи: `tail -f *.log`
2. Проверьте каталоги: `ls -la catalogs/platform-services/`
3. Проверьте порты: `python3 scripts/service-registry/auto_register_service.py ports`
4. Создайте issue в репозитории

---

## 🎉 Summary

**Automated Service Registration System** обеспечивает:

- ✅ **Автоматическая регистрация** всех новых сервисов
- ✅ **Нет конфликтов портов** - автоматическое управление
- ✅ **Стандартные шаблоны** - быстрый старт
- ✅ **Git integration** - проверка при коммите
- ✅ **Полная документация** - catalog + README

**Результат**: Быстрое и безопасное добавление новых сервисов в платформу! 🚀

---

**Created**: 2025-10-15
**Version**: 1.0.0
**Status**: ✅ Production Ready
**Location**: `/Users/MD/AI-Platform-ISO/scripts/service-registry/`
