# Модульные Docker Compose конфигурации

## 🎯 Модульный запуск сервисов

### 📦 Доступные модули:

#### 1. 🏗️ Инфраструктура
```bash
docker-compose -f compose/docker-compose.infrastructure.yml up -d
```
**Включает**: PostgreSQL, Redis, RabbitMQ, Keycloak

#### 2. 🔧 Backend сервисы
```bash
docker-compose -f compose/docker-compose.backend.yml up -d
```
**Включает**: EventBus, BPMN Service, Adapters (LMS, TheHive, Grafana)

#### 3. 🤖 AI сервисы
```bash
docker-compose -f compose/docker-compose.ai.yml up -d
```
**Включает**: AI Orchestrator, BIA Engine, Document Processor, Compliance Checker, PDCA Assistant, Docker-AI-PoC, Scenario Orchestrator, MCP Server

#### 4. 🌐 Odoo Platform
```bash
docker-compose -f compose/docker-compose.odoo.yml up -d
```
**Включает**: Odoo BCM Platform с 20+ модулями

#### 5. 💻 Frontend
```bash
docker-compose -f compose/docker-compose.frontend.yml up -d
```
**Включает**: Web Portal, Admin Panel

#### 6. 📊 Мониторинг
```bash
docker-compose -f compose/docker-compose.monitoring.yml up -d
```
**Включает**: Grafana, MailHog, Traefik

## 🚀 Сценарии запуска:

### Полная платформа
```bash
# 1. Инфраструктура
docker-compose -f compose/docker-compose.infrastructure.yml up -d

# 2. Backend
docker-compose -f compose/docker-compose.backend.yml up -d

# 3. AI сервисы
docker-compose -f compose/docker-compose.ai.yml up -d

# 4. Odoo
docker-compose -f compose/docker-compose.odoo.yml up -d

# 5. Frontend
docker-compose -f compose/docker-compose.frontend.yml up -d

# 6. Мониторинг
docker-compose -f compose/docker-compose.monitoring.yml up -d
```

### Только для разработки AI
```bash
docker-compose -f compose/docker-compose.infrastructure.yml up -d
docker-compose -f compose/docker-compose.ai.yml up -d
```

### Только BCM Platform
```bash
docker-compose -f compose/docker-compose.infrastructure.yml up -d
docker-compose -f compose/docker-compose.odoo.yml up -d
docker-compose -f compose/docker-compose.frontend.yml up -d
```

## 📋 Архивные конфигурации:

В папке `compose/` также находятся:
- `docker-compose-current.yml` - предыдущая версия
- `docker-compose.ai-agents.yml` - эксперимент с AI агентами
- `docker-compose.docker-ai.yml` - Docker AI native версия
- `docker-compose.production.yml` - production конфигурация

## 🎯 Основной файл:

**`/docker-compose.yml`** - полная конфигурация всех сервисов для быстрого запуска всей платформы одной командой.