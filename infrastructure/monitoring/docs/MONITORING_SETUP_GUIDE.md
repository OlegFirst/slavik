# 📊 Monitoring Setup Guide - Простая Структура

**Дата:** 2025-10-03
**Статус:** ✅ ФИНАЛЬНАЯ СТРУКТУРА

---

## 🎯 ПРОСТОЕ ПРАВИЛО: Где Что Настраивать

### 📂 Структура (3 директории - РАЗНОЕ НАЗНАЧЕНИЕ):

```
/Users/MD/AI-Platform-ISO/
│
├── infrastructure/
│   │
│   ├── observability/              # 🐳 DOCKER STACK - Production Monitoring
│   │   ├── docker-compose.monitoring.yml  # ← Запуск Prometheus/Grafana/Loki
│   │   ├── prometheus.yml          # ← ГЛАВНЫЙ Prometheus config
│   │   ├── grafana/                # ← Grafana dashboards
│   │   └── config/                 # ← Alert rules, Loki config
│   │
│   └── monitoring/                 # 🔧 DEV DASHBOARD - Development Tool
│       ├── main.py                 # ← FastAPI сервис (Port 8045)
│       ├── Dockerfile              # ← Container для dev dashboard
│       └── dashboards/             # ← Custom dashboards
│
└── platform-services/
    └── monitoring/                 # ❌ УДАЛИТЬ или объединить
        ├── prometheus.yml          # ← Дубликат! (содержимое → observability)
        └── grafana/                # ← Дубликат dashboards
```

---

## ✅ РЕШЕНИЕ: Правильная Структура

### 1️⃣ `/infrastructure/observability/` - **ГЛАВНЫЙ Production Stack**

**Назначение:** Production мониторинг (Prometheus + Grafana + Loki + Exporters)

**Что здесь:**
- ✅ `docker-compose.monitoring.yml` - Запуск всего стека
- ✅ `prometheus.yml` - **MASTER CONFIG** для scraping метрик
- ✅ `grafana/` - Production dashboards
- ✅ `config/` - Alert rules, Loki config, Alertmanager
- ✅ `loki/` - Log aggregation config

**Когда использовать:** Production deployment, долгосрочное хранение метрик

**Как запустить:**
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/observability
docker-compose -f docker-compose.monitoring.yml up -d
```

**Порты:**
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (admin/admin123)
- Loki: `http://localhost:3100`
- Alertmanager: `http://localhost:9093`

**Что настраивать:**
- ✏️ Добавление сервисов → `prometheus.yml`
- ✏️ Dashboards → `config/grafana/dashboards/`
- ✏️ Alert rules → `config/prometheus/rules/`

---

### 2️⃣ `/infrastructure/monitoring/` - **Development Dashboard**

**Назначение:** Легкий dev-инструмент для быстрой проверки

**Что здесь:**
- ✅ `main.py` - FastAPI сервис (Port 8045)
- ✅ Health checks всех сервисов (каждые 30s)
- ✅ WebSocket real-time streaming
- ✅ In-memory logs/metrics (24h)
- ✅ HTML dashboard

**Когда использовать:** Development, debugging, быстрый overview

**Как запустить:**
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/monitoring
python main.py
# или
docker build -t monitoring-service . && docker run -p 8045:8045 monitoring-service
```

**Порт:**
- Dashboard: `http://localhost:8045/dashboard`
- API: `http://localhost:8045/docs`

**Что настраивать:**
- ✏️ Список сервисов → `main.py` (Config.MONITORED_SERVICES)

**⚠️ Ограничения:**
- In-memory storage (данные теряются при рестарте)
- Retention 24 часа
- НЕ для production долгосрочного хранения

---

### 3️⃣ `/platform-services/monitoring/` - **❌ УДАЛИТЬ**

**Проблема:** Дубликат `prometheus.yml` и `grafana/` dashboards

**Решение:**

**Option A: УДАЛИТЬ (рекомендуется)**
```bash
# Backup на всякий случай
mv /Users/MD/AI-Platform-ISO/platform-services/monitoring \
   /Users/MD/AI-Platform-ISO/_archive/platform-services-monitoring-backup-$(date +%Y%m%d)

# Проверить что ничего не сломалось
```

**Option B: Символическая ссылка**
```bash
# Если docker-compose ссылается на platform-services/monitoring
rm -rf /Users/MD/AI-Platform-ISO/platform-services/monitoring
ln -s /Users/MD/AI-Platform-ISO/infrastructure/observability/prometheus.yml \
      /Users/MD/AI-Platform-ISO/platform-services/monitoring/prometheus.yml
```

**Причина удаления:**
- ❌ Содержит тот же `prometheus.yml` что и `/infrastructure/observability/`
- ❌ Dashboards дублируют `/infrastructure/observability/grafana/`
- ❌ Создает путаницу - где настраивать?

---

## 🔧 Где Что Настраивать (Quick Reference)

### Добавить Новый Сервис в Мониторинг:

**1. Production Stack (Prometheus scraping):**
```bash
# Редактируем ГЛАВНЫЙ config
nano /Users/MD/AI-Platform-ISO/infrastructure/observability/prometheus.yml

# Добавляем:
  - job_name: 'new-service'
    scrape_interval: 10s
    static_configs:
      - targets: ['new-service:8050']
        labels:
          service: 'new-service'
          iso_clause: '8.x'

# Reload Prometheus
docker-compose -f /Users/MD/AI-Platform-ISO/infrastructure/observability/docker-compose.monitoring.yml restart prometheus
```

**2. Dev Dashboard (Health checks):**
```bash
# Редактируем
nano /Users/MD/AI-Platform-ISO/infrastructure/monitoring/main.py

# Добавляем в Config.MONITORED_SERVICES:
"new_service": {
    "url": "http://localhost:8050",
    "health": "/health",
    "metrics": "/metrics",
    "type": "bcm",
    "description": "ISO 22301 Clause X.X - Description"
}
```

---

### Добавить Grafana Dashboard:

```bash
# Положить dashboard JSON в:
/Users/MD/AI-Platform-ISO/infrastructure/observability/config/grafana/dashboards/my-dashboard.json

# Grafana автоматически загрузит его при следующем запуске
docker-compose -f /Users/MD/AI-Platform-ISO/infrastructure/observability/docker-compose.monitoring.yml restart grafana
```

---

### Настроить Alert Rules:

```bash
# Добавить правила в:
/Users/MD/AI-Platform-ISO/infrastructure/observability/config/prometheus/rules/alerts.yml

groups:
  - name: bcm_alerts
    rules:
      - alert: HighLatency
        expr: http_request_duration_seconds{quantile="0.95"} > 1
        for: 5m
        annotations:
          summary: "High latency on {{ $labels.service }}"

# Reload Prometheus
curl -X POST http://localhost:9090/-/reload
```

---

## 📋 Action Plan (Что Делать Сейчас)

### Шаг 1: Удалить Дубликат (5 минут)

```bash
# 1. Backup platform-services/monitoring
mv /Users/MD/AI-Platform-ISO/platform-services/monitoring \
   /Users/MD/AI-Platform-ISO/_archive/platform-services-monitoring-$(date +%Y%m%d)

# 2. Проверить что docker-compose НЕ ссылается на platform-services/monitoring
grep -r "platform-services/monitoring" /Users/MD/AI-Platform-ISO/platform-services/docker-compose*.yml

# Если есть ссылки - заменить на infrastructure/observability
```

---

### Шаг 2: Проверить Main Config (2 минуты)

```bash
# Открыть ГЛАВНЫЙ Prometheus config
cat /Users/MD/AI-Platform-ISO/infrastructure/observability/prometheus.yml

# Должны быть ВСЕ 12+ сервисов:
# - planning, plans, bia, compliance
# - learning, governance
# - community-portal, community-marketplace
# - validation, documents, risk, response
```

---

### Шаг 3: Запустить Production Stack (3 минуты)

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/observability

# Запустить Prometheus + Grafana + Loki
docker-compose -f docker-compose.monitoring.yml up -d

# Проверить что все поднялось
docker-compose -f docker-compose.monitoring.yml ps

# Открыть Prometheus
open http://localhost:9090/targets
# Все сервисы должны быть UP (или DOWN если не запущены)
```

---

### Шаг 4: Опционально - Запустить Dev Dashboard (2 минуты)

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/monitoring

# Установить зависимости (если еще не установлены)
pip install -r requirements.txt

# Запустить FastAPI dashboard
python main.py

# Открыть dashboard
open http://localhost:8045/dashboard
```

---

## ✅ Финальная Структура (После Cleanup)

```
/Users/MD/AI-Platform-ISO/
│
├── infrastructure/
│   │
│   ├── observability/              # ✅ PRODUCTION STACK
│   │   ├── docker-compose.monitoring.yml
│   │   ├── prometheus.yml          # ← ЕДИНСТВЕННЫЙ source of truth
│   │   ├── grafana/
│   │   └── config/
│   │       ├── prometheus/rules/
│   │       ├── grafana/dashboards/
│   │       ├── loki/
│   │       └── alertmanager/
│   │
│   └── monitoring/                 # ✅ DEV DASHBOARD (опционально)
│       ├── main.py
│       ├── Dockerfile
│       └── dashboards/
│
└── platform-services/
    └── monitoring/                 # ❌ УДАЛЕНО (archived)
```

---

## 🎓 Когда Что Использовать

| Сценарий | Использовать | Причина |
|----------|--------------|---------|
| Production deployment | `/infrastructure/observability/` | Долгосрочное хранение, Grafana dashboards, Alerting |
| Development/Debugging | `/infrastructure/monitoring/` | Быстрый overview, real-time WebSocket, легкий запуск |
| Добавить новый сервис | Оба (observability + monitoring) | Prometheus scraping + health checks |
| Настроить dashboards | `/infrastructure/observability/grafana/` | Production dashboards |
| Alert rules | `/infrastructure/observability/config/prometheus/rules/` | Alertmanager integration |

---

## 🔍 Проверка (Checklist)

### После Cleanup:

- [ ] `/platform-services/monitoring/` удалена или архивирована
- [ ] `/infrastructure/observability/prometheus.yml` содержит ВСЕ сервисы
- [ ] Prometheus запущен и scraping работает (`http://localhost:9090/targets`)
- [ ] Grafana показывает dashboards (`http://localhost:3000`)
- [ ] Dev dashboard запущен (опционально) (`http://localhost:8045`)
- [ ] Нет дубликатов конфигов

---

## 📝 Summary

**ОДНО ПРАВИЛО:**

- **Production (долгосрочно)** → `/infrastructure/observability/`
- **Development (временно)** → `/infrastructure/monitoring/`
- **~~Старые дубликаты~~** → ❌ УДАЛИТЬ

**ОДИН CONFIG:**

- Prometheus scraping → `/infrastructure/observability/prometheus.yml`

**ПРОСТО И ПОНЯТНО!** ✅
