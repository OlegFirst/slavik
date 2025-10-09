# 🚀 Quick Start - AI Platform Web UI

**Быстрый запуск единого интерфейса для всей платформы**

---

## ⚡ За 3 шага

### 1. Установить зависимости

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/web-ui
pip3 install -r requirements.txt
```

### 2. Запустить платформу

```bash
./start-platform.sh
```

Этот скрипт автоматически запустит:
- ✅ Prometheus (port 9090)
- ✅ Grafana (port 3000)
- ✅ Alert Manager (port 9093)
- ✅ Web UI (port 8888)

### 3. Открыть в браузере

```
http://localhost:8888
```

**Готово!** 🎉

---

## 📱 Что доступно?

### Main Dashboard
```
http://localhost:8888/
```

- Статус всех сервисов платформы
- Real-time health checks
- Quick actions
- Platform overview

### Tools Management
```
http://localhost:8888/tools
```

- Все 7 инструментов анализа
- Запуск вручную одной кнопкой
- Просмотр результатов
- Competency levels

### Monitoring
```
http://localhost:8888/monitoring
```

- Embedded Grafana dashboards
- Embedded Prometheus metrics
- Alert Manager
- Platform metrics

---

## 🛑 Остановить платформу

```bash
./stop-platform.sh
```

Остановит все компоненты gracefully.

---

## 🔧 Ручной запуск (альтернатива)

Если хочешь запустить только Web UI без observability stack:

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/web-ui
python3 main.py
```

Затем открой http://localhost:8888

---

## 📊 Интеграция с другими сервисами

### Analytics Specialist (если запущен)

```bash
# В другом терминале
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/analytics-specialist
python3 -m uvicorn main:app --host 0.0.0.0 --port 8051
```

Тогда в Web UI появятся все 7 инструментов на странице /tools

### Workflow Intelligence (если запущен)

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence
python3 -m uvicorn main:app --host 0.0.0.0 --port 8030
```

Тогда в Dashboard появится статус Workflow Intelligence

---

## 🎯 Минимальная конфигурация

Для работы Web UI достаточно:

**ОБЯЗАТЕЛЬНО:**
- Python 3.11+
- pip

**ОПЦИОНАЛЬНО (для полного функционала):**
- Docker (для Prometheus/Grafana)
- Analytics Specialist running (для tools management)
- Other platform services (для полного dashboard)

**Даже без других сервисов Web UI запустится и покажет, что недоступно.**

---

## 🐛 Troubleshooting

### Проблема: Port 8888 already in use

```bash
# Найти процесс
lsof -i :8888

# Убить процесс
kill -9 <PID>

# Или изменить порт в main.py
uvicorn.run("main:app", host="0.0.0.0", port=8889)  # Другой порт
```

### Проблема: Module not found

```bash
# Переустановить зависимости
pip3 install -r requirements.txt --force-reinstall
```

### Проблема: Docker not running

```bash
# Запустить Docker Desktop
open -a Docker

# Или установить Docker
brew install --cask docker
```

---

## 🎨 Скриншоты

### Dashboard
```
┌─────────────────────────────────────────────────────┐
│ 🎯 Platform Dashboard                              │
│ Real-time monitoring of AI Platform ISO            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Total Services: 12    Healthy: 10    Issues: 2   │
│                                                     │
│  🚀 Platform Services                              │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────┐│
│  │ Analytics    │ │ Workflow     │ │ Prometheus  ││
│  │ Specialist   │ │ Intelligence │ │             ││
│  │ ● Healthy    │ │ ● Healthy    │ │ ● Healthy   ││
│  └──────────────┘ └──────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────┘
```

### Tools
```
┌─────────────────────────────────────────────────────┐
│ 🔧 Analysis Tools                                   │
├─────────────────────────────────────────────────────┤
│  ┌───────────────────┐ ┌───────────────────┐       │
│  │ AST Analyzer      │ │ Security Scanner  │       │
│  │ [JUNIOR]          │ │ [SENIOR]          │       │
│  │ ● Available       │ │ ● Available       │       │
│  │ [▶ Run Now]       │ │ [▶ Run Now]       │       │
│  └───────────────────┘ └───────────────────┘       │
└─────────────────────────────────────────────────────┘
```

### Monitoring
```
┌─────────────────────────────────────────────────────┐
│ 📊 Platform Monitoring                              │
├─────────────────────────────────────────────────────┤
│ [Overview] [Grafana] [Prometheus] [Alerts]         │
│                                                     │
│  ┌────────────────────────────────────────────────┐│
│  │                                                ││
│  │         Grafana Dashboard Embedded             ││
│  │                                                ││
│  └────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Production Deployment

### С Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  web-ui:
    build: .
    ports:
      - "8888:8888"
    environment:
      - PLATFORM_ROOT=/app
    volumes:
      - ./logs:/app/logs
    restart: always
```

```bash
docker-compose up -d
```

### С systemd

```bash
sudo cp start-platform.sh /opt/ai-platform/
sudo systemctl enable ai-platform-ui
sudo systemctl start ai-platform-ui
```

---

## 📞 Поддержка

- Issues: GitHub Issues
- Docs: README.md
- Architecture: main.py

---

**Enjoy! 🎉**
