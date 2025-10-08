# Infrastructure Tools Integration Guide

## 🎯 Архитектура интеграции

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI PLATFORM INFRASTRUCTURE                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: DISCOVERY & ANALYSIS (tools/)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📊 tools/analyzers/                                             │
│     ├── module_scanner.py          ← Сканирование модулей       │
│     ├── api_mapper.py              ← Поиск API endpoints        │
│     └── dependency_validator.py    ← Граф зависимостей         │
│                                                                   │
│  🔍 tools/infrastructure/                                        │
│     ├── discover_services.py       ← Обнаружение сервисов       │
│     ├── docker_compose_generator.py ← Генерация compose файлов  │
│     └── infrastructure_orchestrator.py ← ГЛАВНЫЙ ОРКЕСТРАТОР    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: AI ORCHESTRATION (intelligent-core/orchestration/)    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  🧠 ai-orchestration/ (Port 8002)                               │
│     ├── orchestrator.py            ← AI-powered orchestration   │
│     ├── core/docker_manager.py     ← Docker управление          │
│     └── control_center/            ← Unified controller         │
│                                                                   │
│  🎯 coordination-center/ (Port 8004)                            │
│     ├── main.py                    ← Coordination hub           │
│     └── core/execution_tracker.py  ← Task tracking             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: DEPLOYMENT (infrastructure/deployment/)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  🐳 docker-management/                                           │
│     └── docker_manager.py          ← Low-level Docker API       │
│                                                                   │
│  📦 generated/                                                   │
│     ├── docker-compose.gateway.yml                              │
│     ├── docker-compose.runtime.yml                              │
│     ├── docker-compose.observability.yml                        │
│     ├── docker-compose.integration.yml                          │
│     ├── docker-compose.full.yml                                 │
│     ├── start_infrastructure.sh    ← Startup скрипт            │
│     └── .env.template               ← Environment template      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: CLI (tools/project-agent/)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  🛠️  project-agent/                                             │
│     ├── agent/cli.py               ← CLI interface              │
│     └── agent/docker_commands.py   ← Docker команды (НОВОЕ)    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Первичная настройка (один раз)

```bash
# Обнаружить все сервисы и сгенерировать конфигурации
python3 tools/infrastructure/infrastructure_orchestrator.py build-and-deploy
```

Это выполнит:
1. ✅ Обнаружение всех сервисов
2. ✅ Генерацию Dockerfile для сервисов без них
3. ✅ Генерацию docker-compose файлов по слоям
4. ✅ Создание startup скриптов
5. ✅ Настройку .env.template
6. ✅ Развёртывание через ai-orchestration (если запущен)

---

## 📋 Основные команды

### Через infrastructure_orchestrator.py

```bash
# 1. Обнаружить все сервисы
python3 tools/infrastructure/infrastructure_orchestrator.py discover

# 2. Сгенерировать docker-compose файлы
python3 tools/infrastructure/infrastructure_orchestrator.py generate

# 3. Развернуть инфраструктуру (через ai-orchestration)
python3 tools/infrastructure/infrastructure_orchestrator.py deploy --layer full

# 4. Развернуть напрямую через docker-compose (без AI)
python3 tools/infrastructure/infrastructure_orchestrator.py deploy --layer full --no-orchestrator

# 5. Полный цикл: discover + generate + deploy
python3 tools/infrastructure/infrastructure_orchestrator.py build-and-deploy

# 6. Проверить статус
python3 tools/infrastructure/infrastructure_orchestrator.py status
```

### Через сгенерированные скрипты

```bash
cd infrastructure/deployment/generated

# Запуск по слоям
./start_infrastructure.sh gateway        # Только Gateway
./start_infrastructure.sh runtime        # Только Runtime
./start_infrastructure.sh observability  # Только Observability
./start_infrastructure.sh full           # Всё сразу

# Остановка
./stop_infrastructure.sh full

# Проверка здоровья
./check_health.sh
```

### Через docker-compose напрямую

```bash
cd infrastructure/deployment/generated

# Запуск конкретного слоя
docker-compose -f docker-compose.gateway.yml up -d

# Остановка
docker-compose -f docker-compose.gateway.yml down

# Логи
docker-compose -f docker-compose.gateway.yml logs -f

# Рестарт сервиса
docker-compose -f docker-compose.gateway.yml restart api-gateway
```

---

## 🔧 Интеграция с project-agent

### Добавление Docker команд в project-agent

```bash
# Интегрировать с project-agent
python3 tools/infrastructure/infrastructure_orchestrator.py integrate-project-agent
```

После интеграции доступны новые команды:

```bash
# Через project-agent CLI
project-agent docker discover         # Обнаружение сервисов
project-agent docker generate         # Генерация конфигов
project-agent docker deploy           # Развёртывание
project-agent docker deploy --layer gateway
project-agent docker build-deploy     # Полный цикл
project-agent docker status           # Статус
```

---

## 🎯 Рабочие процессы

### Workflow 1: Добавление нового сервиса

```bash
# 1. Создать новый сервис в infrastructure/
mkdir infrastructure/my-new-service
cd infrastructure/my-new-service
# ... создать main.py, requirements.txt ...

# 2. Переобнаружить сервисы и пересоздать конфиги
python3 tools/infrastructure/infrastructure_orchestrator.py discover
python3 tools/infrastructure/infrastructure_orchestrator.py generate

# 3. Запустить обновлённую инфраструктуру
cd infrastructure/deployment/generated
./start_infrastructure.sh full
```

### Workflow 2: Разработка с hot-reload

```bash
# 1. Запустить только нужный слой
cd infrastructure/deployment/generated
./start_infrastructure.sh gateway

# 2. Для локальной разработки - использовать volumes
# В docker-compose.*.yml добавить volumes для hot-reload:
#   volumes:
#     - ../../gateway/api-gateway:/app

# 3. При изменении кода контейнер автоматически перезапустится
```

### Workflow 3: Production deployment

```bash
# 1. Обновить .env с production credentials
cd infrastructure/deployment/generated
vim .env

# 2. Запустить через ai-orchestration (умное управление)
python3 tools/infrastructure/infrastructure_orchestrator.py deploy --layer full

# 3. Мониторить через observability
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
```

---

## 📊 Слои инфраструктуры

### Gateway Layer (Ports 8000-8099)

Сервисы:
- `api-gateway` (8000) - Главный API Gateway
- `unified-database-gateway` (8008) - Database Gateway
- `intelligent-gateway` (8005) - AI-powered Gateway

Docker Compose: `docker-compose.gateway.yml`

### Runtime Layer (Ports 8100-8199)

Сервисы:
- `realtime-websocket` (8050) - WebSocket сервис
- `eventbus` - Event Bus (library)
- `message-queue` - RabbitMQ wrapper
- `service-discovery` - Service Registry

Docker Compose: `docker-compose.runtime.yml`

### Observability Layer (Ports 9000-9199)

Сервисы:
- `monitoring` (8047) - Monitoring service
- `mio-manager` (8046) - AI MIO Manager
- `notification-service` (8048) - Notification service
- `prometheus` (9090) - Metrics collection
- `grafana` (3000) - Visualization

Docker Compose: `docker-compose.observability.yml`

### Integration Layer (Ports 8200-8299)

Сервисы:
- `github-integration` - GitHub integration
- `process-mining-service` - Process mining
- `deployment-service` - Deployment automation

Docker Compose: `docker-compose.integration.yml`

---

## 🔄 Автоматизация с CI/CD

### GitHub Actions Integration

Создать `.github/workflows/infrastructure.yml`:

```yaml
name: Infrastructure Build & Deploy

on:
  push:
    paths:
      - 'infrastructure/**'
      - 'tools/infrastructure/**'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd tools
          pip install -r requirements.txt

      - name: Discover services
        run: |
          python3 tools/infrastructure/infrastructure_orchestrator.py discover

      - name: Generate configurations
        run: |
          python3 tools/infrastructure/infrastructure_orchestrator.py generate

      - name: Validate configurations
        run: |
          cd infrastructure/deployment/generated
          for f in docker-compose.*.yml; do
            docker-compose -f $f config
          done

      - name: Deploy to staging
        if: github.ref == 'refs/heads/develop'
        run: |
          python3 tools/infrastructure/infrastructure_orchestrator.py deploy --layer full --no-orchestrator
```

---

## 🛠️ Расширение системы

### Добавление нового слоя

Отредактировать `tools/infrastructure/docker_compose_generator.py`:

```python
LAYERS = {
    # ... существующие слои ...
    'ml-platform': {
        'services': ['ml-training', 'ml-inference', 'feature-store'],
        'network': 'ml-network',
        'port_range': '8300-8399'
    }
}
```

### Добавление нового анализатора

Создать в `tools/analyzers/`:

```python
# tools/analyzers/my_custom_analyzer.py

class MyCustomAnalyzer:
    def analyze(self, service_path):
        # Ваша логика анализа
        pass
```

Интегрировать в `discover_services.py`:

```python
from analyzers.my_custom_analyzer import MyCustomAnalyzer

analyzer = MyCustomAnalyzer()
custom_data = analyzer.analyze(service_path)
```

---

## 📚 API Reference

### ServiceDiscovery

```python
from infrastructure.discover_services import ServiceDiscovery

discovery = ServiceDiscovery(project_root)
services = discovery.discover_all()

# services = [
#   {
#     'name': 'api-gateway',
#     'port': 8000,
#     'path': '/path/to/service',
#     'endpoints': [...],
#     'dependencies': [...],
#     'environment': [...]
#   },
#   ...
# ]
```

### DockerComposeGenerator

```python
from infrastructure.docker_compose_generator import DockerComposeGenerator

generator = DockerComposeGenerator(project_root, output_dir)

# Генерация одного слоя
generator.generate_layer('gateway')

# Генерация всех слоёв
generator.generate_all()
```

### InfrastructureOrchestrator

```python
from infrastructure.infrastructure_orchestrator import InfrastructureOrchestrator

orchestrator = InfrastructureOrchestrator(project_root)

# Полный цикл
orchestrator.build_and_deploy(layer='full', use_orchestrator=True)

# Отдельные шаги
services = orchestrator.discover_services()
orchestrator.generate_configs(services)
orchestrator.deploy_infrastructure('gateway')
orchestrator.status()
```

---

## 🐛 Troubleshooting

### Проблема: Сервис не обнаруживается

**Причина:** Нет main.py или app.py в корне сервиса

**Решение:**
```bash
# Убедиться что есть entry point
ls infrastructure/my-service/main.py

# Или переименовать
mv infrastructure/my-service/app.py infrastructure/my-service/main.py
```

### Проблема: Docker Compose не запускается

**Причина:** Отсутствует .env файл

**Решение:**
```bash
cd infrastructure/deployment/generated
cp .env.template .env
# Отредактировать .env с реальными значениями
vim .env
```

### Проблема: ai-orchestration не подключается

**Причина:** Сервис не запущен

**Решение:**
```bash
# Запустить ai-orchestration
cd intelligent-core/orchestration
./start_orchestration.sh

# Проверить
curl http://localhost:8002/health
```

### Проблема: Конфликт портов

**Причина:** Порт уже занят другим процессом

**Решение:**
```bash
# Найти процесс
lsof -i :8000

# Убить процесс
kill -9 <PID>

# Или изменить порт в service config
```

---

## 📖 Best Practices

### 1. Environment Variables

- ✅ Всегда использовать `.env` файл для credentials
- ✅ Никогда не коммитить `.env` в git
- ✅ Использовать `.env.template` как документацию

### 2. Service Discovery

- ✅ Запускать `discover` после добавления новых сервисов
- ✅ Проверять `service-catalog.json` на корректность
- ✅ Использовать стандартные имена файлов (`main.py`, `Dockerfile`)

### 3. Deployment

- ✅ Тестировать локально перед production
- ✅ Использовать слои для изолированного тестирования
- ✅ Мониторить через Grafana после deploy

### 4. Development

- ✅ Использовать volumes для hot-reload в разработке
- ✅ Логи в stdout/stderr для Docker
- ✅ Health checks для всех сервисов

---

## 🎓 Примеры использования

### Пример 1: Новый проект

```bash
# 1. Setup
cd /path/to/new/project
python3 tools/infrastructure/infrastructure_orchestrator.py build-and-deploy

# 2. Configure
cd infrastructure/deployment/generated
cp .env.template .env
vim .env  # Установить credentials

# 3. Start
./start_infrastructure.sh full

# 4. Verify
./check_health.sh
```

### Пример 2: Добавление сервиса в существующий проект

```bash
# 1. Создать новый сервис
mkdir infrastructure/my-service
cd infrastructure/my-service

# 2. Создать файлы
cat > main.py << 'EOF'
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
EOF

cat > requirements.txt << 'EOF'
fastapi
uvicorn
EOF

# 3. Обновить конфиги
python3 ../../tools/infrastructure/infrastructure_orchestrator.py discover
python3 ../../tools/infrastructure/infrastructure_orchestrator.py generate

# 4. Запустить
cd ../deployment/generated
docker-compose -f docker-compose.full.yml up -d my-service

# 5. Проверить
curl http://localhost:8100/health
```

### Пример 3: Production deployment

```bash
# 1. Подготовить production .env
cd infrastructure/deployment/generated
cat > .env << 'EOF'
# Production credentials
DATABASE_URL=postgresql://prod_user:secure_password@prod-db.example.com:5432/prod_db
REDIS_URL=redis://prod-redis.example.com:6379/0
QDRANT_URL=https://prod-qdrant.example.com
ANTHROPIC_API_KEY=sk-ant-prod-xxxxx
JWT_SECRET=super-secret-production-key
EOF

# 2. Deploy через ai-orchestration (intelligent deployment)
python3 ../../tools/infrastructure/infrastructure_orchestrator.py deploy --layer full

# 3. Monitor
# Открыть Grafana: http://prod-grafana.example.com:3000
# Проверить Prometheus: http://prod-prometheus.example.com:9090

# 4. Health checks
./check_health.sh
```

---

## 🔗 Связанные документы

- [Infrastructure Complete Status](../../infrastructure/INFRASTRUCTURE_COMPLETE_STATUS.md)
- [Professional Setup Strategy](../../infrastructure/PROFESSIONAL_SETUP_STRATEGY.md)
- [AI Orchestration Architecture](../../intelligent-core/orchestration/ai-orchestration/ARCHITECTURE.md)
- [Project Agent README](../project-agent/README.md)

---

## 📞 Поддержка

Если возникли вопросы или проблемы:

1. Проверить [Troubleshooting](#-troubleshooting)
2. Проверить логи: `docker-compose logs -f <service>`
3. Проверить статус: `python3 tools/infrastructure/infrastructure_orchestrator.py status`

---

*Auto-generated integration guide*
*Last updated: 2025-10-07*
