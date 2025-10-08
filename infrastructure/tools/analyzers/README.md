# Infrastructure Automation Tools

Автоматизация обнаружения, конфигурации и развёртывания всех инфраструктурных сервисов.

## 🚀 Quick Start

```bash
# Полная автоматизация в одну команду
python3 tools/infrastructure/infrastructure_orchestrator.py build-and-deploy
```

Это выполнит:
1. ✅ Обнаружение всех сервисов в проекте
2. ✅ Создание Dockerfile для сервисов без них
3. ✅ Генерацию docker-compose файлов по слоям
4. ✅ Создание startup скриптов
5. ✅ Развёртывание инфраструктуры

## 📁 Структура

```
tools/infrastructure/
├── discover_services.py           # Обнаружение сервисов
├── docker_compose_generator.py    # Генерация docker-compose файлов
├── infrastructure_orchestrator.py # ГЛАВНЫЙ ОРКЕСТРАТОР
├── metrics_discovery.py           # Обнаружение метрик
├── INTEGRATION_GUIDE.md           # Полная документация
└── README.md                      # Этот файл
```

## 🎯 Основные команды

### 1. Обнаружение сервисов

```bash
python3 tools/infrastructure/infrastructure_orchestrator.py discover
```

Сканирует проект и находит все сервисы:
- intelligent-core/
- infrastructure/
- platform-services/

Результат: `infrastructure/deployment/generated/service-catalog.json`

### 2. Генерация конфигураций

```bash
python3 tools/infrastructure/infrastructure_orchestrator.py generate
```

Создаёт:
- `docker-compose.gateway.yml` - Gateway слой
- `docker-compose.runtime.yml` - Runtime слой
- `docker-compose.observability.yml` - Observability слой
- `docker-compose.integration.yml` - Integration слой
- `docker-compose.full.yml` - Все сервисы вместе
- `start_infrastructure.sh` - Скрипт запуска
- `stop_infrastructure.sh` - Скрипт остановки
- `.env.template` - Шаблон переменных окружения

### 3. Развёртывание

```bash
# Через ai-orchestration (умное управление)
python3 tools/infrastructure/infrastructure_orchestrator.py deploy --layer full

# Напрямую через docker-compose
python3 tools/infrastructure/infrastructure_orchestrator.py deploy --layer full --no-orchestrator

# Только конкретный слой
python3 tools/infrastructure/infrastructure_orchestrator.py deploy --layer gateway
```

### 4. Проверка статуса

```bash
python3 tools/infrastructure/infrastructure_orchestrator.py status
```

### 5. Полный цикл

```bash
# Обнаружение → Генерация → Развёртывание
python3 tools/infrastructure/infrastructure_orchestrator.py build-and-deploy
```

## 🔧 Интеграция с существующими системами

### С ai-orchestration

```bash
# Запустить ai-orchestration
cd intelligent-core/orchestration
./start_orchestration.sh

# Deploy через ai-orchestration (автоматически используется если запущен)
python3 tools/infrastructure/infrastructure_orchestrator.py deploy --layer full
```

### С project-agent

```bash
# Интегрировать инструменты в project-agent CLI
python3 tools/infrastructure/infrastructure_orchestrator.py integrate-project-agent

# Использовать через project-agent
project-agent docker discover
project-agent docker generate
project-agent docker deploy --layer gateway
project-agent docker status
```

## 📊 Слои инфраструктуры

### Gateway (8000-8099)
- api-gateway (8000)
- unified-database-gateway (8008)
- intelligent-gateway (8005)

### Runtime (8050-8199)
- realtime-websocket (8050)
- eventbus (library)
- message-queue (library)
- service-discovery (library)

### Observability (9000-9199)
- monitoring (8047)
- mio-manager (8046)
- notification-service (8048)
- prometheus (9090)
- grafana (3000)

### Integration (8200-8299)
- github-integration
- process-mining-service
- deployment-service

## 🛠️ Использование сгенерированных скриптов

После генерации конфигураций доступны скрипты:

```bash
cd infrastructure/deployment/generated

# Настроить environment
cp .env.template .env
vim .env  # Установить credentials

# Запуск
./start_infrastructure.sh full        # Все сервисы
./start_infrastructure.sh gateway     # Только Gateway
./start_infrastructure.sh runtime     # Только Runtime

# Проверка
./check_health.sh

# Остановка
./stop_infrastructure.sh full
```

## 📖 Примеры

### Пример 1: Первое использование

```bash
# 1. Обнаружить и сгенерировать конфиги
python3 tools/infrastructure/infrastructure_orchestrator.py build-and-deploy

# 2. Настроить environment
cd infrastructure/deployment/generated
cp .env.template .env
vim .env

# 3. Запустить
./start_infrastructure.sh full

# 4. Проверить
./check_health.sh
```

### Пример 2: Добавление нового сервиса

```bash
# 1. Создать новый сервис
mkdir infrastructure/my-new-service
cd infrastructure/my-new-service
# ... создать main.py, requirements.txt ...

# 2. Обновить конфиги
python3 tools/infrastructure/infrastructure_orchestrator.py discover
python3 tools/infrastructure/infrastructure_orchestrator.py generate

# 3. Запустить обновлённую инфраструктуру
cd infrastructure/deployment/generated
./start_infrastructure.sh full
```

### Пример 3: Разработка с hot-reload

```bash
# 1. Запустить только нужный слой
cd infrastructure/deployment/generated
./start_infrastructure.sh gateway

# 2. Логи в реальном времени
docker-compose -f docker-compose.gateway.yml logs -f api-gateway

# 3. Рестарт после изменений
docker-compose -f docker-compose.gateway.yml restart api-gateway
```

## 🏗️ Архитектура

```
┌─────────────────────────────────────┐
│  tools/infrastructure/              │
│  (Service Discovery & Generation)   │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  intelligent-core/orchestration/    │
│  ai-orchestration (AI Management)   │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│  infrastructure/deployment/         │
│  (Docker Compose Execution)         │
└─────────────────────────────────────┘
```

**Преимущества этого подхода:**

1. ✅ **Автоматизация** - нет ручной настройки
2. ✅ **Интеграция** - использует существующие инструменты
3. ✅ **Гибкость** - можно использовать AI или напрямую
4. ✅ **Масштабируемость** - легко добавлять новые сервисы
5. ✅ **Best Practices** - следует industry standards

## 🔗 Документация

Полная документация: [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)

Включает:
- Детальная архитектура
- Все команды и параметры
- Workflow для разных сценариев
- Troubleshooting
- API Reference
- Best Practices

## 🎓 Best Practices

### Environment Variables
```bash
# ✅ Всегда использовать .env файл
cp .env.template .env

# ❌ Не коммитить credentials
echo ".env" >> .gitignore
```

### Service Discovery
```bash
# ✅ Запускать после добавления сервисов
python3 tools/infrastructure/infrastructure_orchestrator.py discover

# ✅ Проверять каталог
cat infrastructure/deployment/generated/service-catalog.json
```

### Deployment
```bash
# ✅ Тестировать локально перед production
./start_infrastructure.sh gateway  # Тестируем один слой

# ✅ Использовать слои для изоляции
./start_infrastructure.sh runtime

# ✅ Мониторить после deploy
./check_health.sh
```

## 🐛 Troubleshooting

### Сервис не обнаружен

```bash
# Проверить структуру
ls infrastructure/my-service/main.py

# Должен быть main.py или app.py
```

### Docker Compose не запускается

```bash
# Проверить .env
cat infrastructure/deployment/generated/.env

# Валидировать compose файл
docker-compose -f docker-compose.full.yml config
```

### ai-orchestration не доступен

```bash
# Запустить ai-orchestration
cd intelligent-core/orchestration
./start_orchestration.sh

# Проверить
curl http://localhost:8002/health
```

## 📞 Поддержка

- Полная документация: [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)
- Infrastructure Status: [../../infrastructure/INFRASTRUCTURE_COMPLETE_STATUS.md](../../infrastructure/INFRASTRUCTURE_COMPLETE_STATUS.md)
- AI Orchestration: [../../intelligent-core/orchestration/ai-orchestration/ARCHITECTURE.md](../../intelligent-core/orchestration/ai-orchestration/ARCHITECTURE.md)

---

*Created: 2025-10-07*
*Version: 1.0.0*
