# Prometheus/Grafana Service Registration Analysis

## Текущее состояние (CRITICAL FINDING)

### ❌ Проблема: Полностью ручная конфигурация

**Prometheus:** Все сервисы зарегистрированы вручную в статическом YAML файле
- Файл: `/infrastructure/observability/config/prometheus/prometheus.yml`
- 40+ сервисов hardcoded вручную
- Пример конфигурации:

```yaml
scrape_configs:
  - job_name: 'planning-service'
    static_configs:
      - targets: ['planning-service:8011']

  - job_name: 'ai-event-manager'
    static_configs:
      - targets: ['ai-event-manager:8041']

  # ... еще 38+ сервисов вручную
```

**Grafana:** Настроена читать из Prometheus, но также статическая конфигурация дашбордов.

### 🔍 Что найдено

1. **Статическая конфигурация в prometheus.yml** (388 строк)
   - Все targets прописаны вручную
   - При добавлении нового сервиса нужно вручную редактировать файл
   - При изменении порта нужно вручную обновлять

2. **Попытка auto-generation** (не используется)
   - Файл: `/infrastructure/observability/auto-generated/prometheus-jobs-auto.yml`
   - Генерирует конфиги для intelligent-core сервисов
   - НО: не интегрирован с основным prometheus.yml
   - Не используется в продакшене

3. **Service Discovery директории** (пустые/не используются)
   - `/infrastructure/observability/config/prometheus/sd_configs/`
   - `/infrastructure/observability/config/prometheus/service-discovery/`
   - Есть README с планами, но реализация отсутствует

4. **monitoring-backend** (только читает)
   - Файл: `/infrastructure/observability/monitoring-backend/main.py`
   - Только читает данные из Prometheus API
   - НЕ управляет регистрацией сервисов
   - Предоставляет REST API для фронтенда

5. **Service Discovery сервис** (не используется)
   - Существует: `/infrastructure/runtime/service-discovery/`
   - НЕ интегрирован с Prometheus
   - НЕ управляет регистрацией метрик

---

## ❓ Кто контролирует сейчас?

**Ответ: НИКТО** (Ручная работа DevOps)

Процесс сейчас:
1. Разработчик создает новый сервис
2. Добавляет Prometheus metrics endpoint в код
3. **ВРУЧНУЮ** добавляет конфигурацию в `prometheus.yml`
4. Перезапускает Prometheus
5. **ВРУЧНУЮ** проверяет, что метрики собираются

**Проблемы:**
- ❌ Нет автоматизации
- ❌ Нет проверки, что сервис действительно отчитывается
- ❌ Нет мониторинга coverage (какие сервисы мониторятся, какие нет)
- ❌ Нет уведомлений о пропущенных сервисах
- ❌ При масштабировании нужно вручную добавлять новые инстансы

---

## ✅ Правильная архитектура (Choreography)

### В хореографической модели это задача МиО Manager (ГЛАЗА)

**Почему МиО?**
- МиО = ГЛАЗА системы
- МиО следит, чтобы все собиралось по всей системе
- МиО не командует, но **автоматизирует наблюдение**
- МиО помогает сервисам регистрироваться (automation, not command)

### Архитектурное решение

```
┌─────────────────────────────────────────────────────────────┐
│                     МiО Manager (ГЛАЗА)                      │
│                                                              │
│  1. Service Discovery Observer                              │
│     - Подписывается на: platform.service.registered         │
│     - Наблюдает новые сервисы                               │
│                                                              │
│  2. Metrics Registration Automator (Automation Toolkit)     │
│     - Автоматически создает Prometheus job config           │
│     - Использует file-based service discovery               │
│     - Генерирует /etc/prometheus/sd_configs/services.json   │
│                                                              │
│  3. Metrics Coverage Observer                               │
│     - Проверяет: все ли сервисы отчитываются?              │
│     - Сравнивает Service Discovery vs Prometheus targets    │
│     - Публикует: platform.mio.metrics_coverage_observed     │
│                                                              │
│  4. Metrics Health Checker                                  │
│     - Проверяет доступность metrics endpoints               │
│     - Проверяет актуальность метрик                         │
│     - Публикует: platform.mio.metrics_health_observed       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ publishes observations
                              ▼
                         EventBus
                              │
                              ├─► Brain (может принять решение)
                              ├─► ai-event-manager (координатор events)
                              ├─► DevOps Agent (может исправить проблемы)
                              └─► Analytics (собирает статистику)
```

### Event Flow (Choreography)

```json
// 1. Новый сервис регистрируется
{
  "event": "platform.service.registered",
  "source": "service-discovery",
  "data": {
    "service_name": "new-service",
    "host": "new-service",
    "port": 8080,
    "metrics_endpoint": "/metrics"
  }
}

// 2. МиО наблюдает регистрацию и автоматически создает Prometheus config
// (через Automation Toolkit)

// 3. МiО публикует наблюдение
{
  "event": "platform.mio.service_monitoring_enabled",
  "source": "mio-manager",
  "data": {
    "service_name": "new-service",
    "prometheus_job": "new-service",
    "status": "enabled"
  }
}

// 4. МiО периодически проверяет coverage
{
  "event": "platform.mio.metrics_coverage_observed",
  "source": "mio-manager",
  "data": {
    "total_services": 45,
    "monitored_services": 43,
    "missing_services": ["legacy-service", "test-service"],
    "coverage_percentage": 95.5,
    "timestamp": "2025-10-11T10:30:00Z"
  }
}

// 5. Если обнаружена проблема
{
  "event": "platform.mio.metrics_health_issue_observed",
  "source": "mio-manager",
  "data": {
    "service_name": "failing-service",
    "issue": "metrics_endpoint_unreachable",
    "details": "Connection refused on failing-service:8080/metrics",
    "recommendation": "Check if service is running and metrics endpoint is configured"
  }
}
```

### Сервисы в хореографии (кто что делает)

1. **Service Discovery** (coordinator of service registry sector)
   - Регистрирует новые сервисы
   - Публикует: `platform.service.registered`
   - Отслеживает health checks

2. **МiО Manager** (ГЛАЗА - Observatory)
   - Наблюдает регистрацию сервисов
   - Автоматизирует создание Prometheus configs
   - Наблюдает metrics coverage
   - Наблюдает metrics health
   - Публикует наблюдения в EventBus
   - НЕ принимает решения, НЕ командует

3. **Brain/Predictive** (МОЗГ - Decision maker)
   - Получает наблюдения от МiО
   - Принимает решения на основе observations
   - Может решить: нужно масштабировать мониторинг
   - Публикует: `platform.brain.decision_made`

4. **DevOps Agent** (coordinator of DevOps sector)
   - Подписывается на observations от МiО
   - Может автоматически исправлять проблемы регистрации
   - Может перезапускать Prometheus при изменениях
   - Публикует: `platform.devops.action_completed`

5. **Analytics Specialist** (АНАЛИТИК)
   - Собирает статистику coverage
   - Анализирует trends в метриках
   - Передает insights в Brain
   - Публикует: `platform.analytics.insights_ready`

6. **ai-event-manager** (coordinator of events sector)
   - Координирует event flow
   - Может escalate критичные проблемы
   - Публикует: `platform.events.alert_triggered`

---

## 🔧 Техническое решение

### Prometheus File-Based Service Discovery

Вместо статического `prometheus.yml`, использовать file-based service discovery:

**prometheus.yml** (новая версия):
```yaml
scrape_configs:
  - job_name: 'dynamic-services'
    file_sd_configs:
      - files:
          - '/etc/prometheus/sd_configs/services.json'
        refresh_interval: 30s
```

**services.json** (автоматически генерируется МiО):
```json
[
  {
    "targets": ["ai-event-manager:8041"],
    "labels": {
      "job": "ai-event-manager",
      "env": "production",
      "sector": "events"
    }
  },
  {
    "targets": ["balancer-service:8043"],
    "labels": {
      "job": "balancer-service",
      "env": "production",
      "sector": "balancing"
    }
  }
  // ... автоматически добавляются новые сервисы
]
```

### МiО Manager - Metrics Registration Automator

```python
# /infrastructure/AI-office-infrastructure/mio-manager/automation/metrics_registration_automator.py

class MetricsRegistrationAutomator:
    """
    Автоматическая регистрация сервисов в Prometheus

    Часть МiО Manager Automation Toolkit
    Хореография: реагирует на events, не командует
    """

    def __init__(self, eventbus, prometheus_sd_file: str):
        self.eventbus = eventbus
        self.prometheus_sd_file = prometheus_sd_file
        self.registered_services = {}

    async def start(self):
        """Start listening to service registration events"""
        await self.eventbus.subscribe_to_service_events(
            self.handle_service_registered
        )

    async def handle_service_registered(self, event: dict):
        """
        Реагирует на platform.service.registered
        Автоматически добавляет сервис в Prometheus SD
        """
        service_name = event['data']['service_name']
        host = event['data']['host']
        port = event['data']['port']
        metrics_endpoint = event['data'].get('metrics_endpoint', '/metrics')

        # Add to Prometheus service discovery
        await self._add_to_prometheus_sd(
            service_name, host, port, metrics_endpoint
        )

        # Publish observation
        await self.eventbus.publish(
            'platform.mio.service_monitoring_enabled',
            {
                'service_name': service_name,
                'prometheus_job': service_name,
                'target': f"{host}:{port}",
                'status': 'enabled'
            }
        )

    async def _add_to_prometheus_sd(self, service_name, host, port, endpoint):
        """Update Prometheus file-based service discovery JSON"""
        # Read current config
        with open(self.prometheus_sd_file, 'r') as f:
            services = json.load(f)

        # Add new service
        services.append({
            'targets': [f"{host}:{port}"],
            'labels': {
                'job': service_name,
                'env': 'production',
                'metrics_path': endpoint
            }
        })

        # Write updated config
        with open(self.prometheus_sd_file, 'w') as f:
            json.dump(services, f, indent=2)

        logger.info(f"✅ Added {service_name} to Prometheus SD")
```

### МiО Manager - Metrics Coverage Observer

```python
# /infrastructure/AI-office-infrastructure/mio-manager/monitoring/metrics_coverage_observer.py

class MetricsCoverageObserver:
    """
    Наблюдает за coverage метрик

    Проверяет:
    - Все ли сервисы из Service Discovery мониторятся?
    - Все ли Prometheus targets отчитываются?
    """

    def __init__(self, eventbus, service_discovery_client, prometheus_client):
        self.eventbus = eventbus
        self.service_discovery = service_discovery_client
        self.prometheus = prometheus_client

    async def observe_coverage(self):
        """
        Периодически проверяет coverage
        Публикует наблюдения в EventBus
        """
        # Get all registered services
        all_services = await self.service_discovery.get_all_services()

        # Get all Prometheus targets
        prometheus_targets = await self.prometheus.get_targets()

        # Compare
        monitored = set(t['job'] for t in prometheus_targets if t['health'] == 'up')
        registered = set(s['name'] for s in all_services)

        missing = registered - monitored
        coverage_pct = (len(monitored) / len(registered) * 100) if registered else 0

        # Publish observation
        await self.eventbus.publish(
            'platform.mio.metrics_coverage_observed',
            {
                'total_services': len(registered),
                'monitored_services': len(monitored),
                'missing_services': list(missing),
                'coverage_percentage': coverage_pct,
                'timestamp': datetime.utcnow().isoformat()
            },
            priority='normal'
        )

        # If coverage is low, publish health issue
        if coverage_pct < 90:
            await self.eventbus.publish(
                'platform.mio.metrics_coverage_issue_observed',
                {
                    'coverage_percentage': coverage_pct,
                    'missing_count': len(missing),
                    'missing_services': list(missing),
                    'severity': 'high' if coverage_pct < 80 else 'medium',
                    'recommendation': 'Check service registration and Prometheus configuration'
                },
                priority='high'
            )
```

---

## 📋 План внедрения

### Phase 1: МiО становится наблюдателем (1-2 дня)

1. **Создать Metrics Coverage Observer в МiО**
   - Сравнивает Service Discovery vs Prometheus
   - Публикует observations в EventBus
   - Файл: `/mio-manager/monitoring/metrics_coverage_observer.py`

2. **Добавить Metrics Health Checker в МiО**
   - Проверяет доступность endpoints
   - Проверяет актуальность метрик
   - Файл: `/mio-manager/monitoring/metrics_health_checker.py`

3. **Интегрировать в SmartScheduler**
   - Добавить Metrics Coverage Cycle (каждые 5 минут)
   - Добавить Metrics Health Cycle (каждую минуту)

### Phase 2: Автоматизация регистрации (2-3 дня)

4. **Создать Metrics Registration Automator**
   - Слушает `platform.service.registered`
   - Автоматически обновляет Prometheus SD JSON
   - Файл: `/mio-manager/automation/metrics_registration_automator.py`

5. **Перевести Prometheus на file-based SD**
   - Изменить `prometheus.yml` на file_sd_configs
   - Создать `/etc/prometheus/sd_configs/services.json`
   - Мигрировать существующие сервисы

6. **Обновить Service Discovery**
   - Публиковать `platform.service.registered` при регистрации
   - Интеграция с EventBus

### Phase 3: Реакция на проблемы (1-2 дня)

7. **DevOps Agent слушает observations**
   - Подписывается на `platform.mio.metrics_coverage_issue_observed`
   - Автоматически пытается исправить проблемы регистрации

8. **Brain анализирует trends**
   - Получает observations от МiО
   - Может принять решение о масштабировании мониторинга

9. **Analytics собирает статистику**
   - Анализирует coverage trends
   - Передает insights в Brain

---

## 🎯 Результат

После внедрения:

✅ **Автоматическая регистрация**
- Новый сервис → автоматически появляется в Prometheus
- Нет ручной работы DevOps

✅ **Постоянное наблюдение**
- МiО следит за coverage 24/7
- Немедленное обнаружение проблем

✅ **Хореографическая архитектура**
- МiО = ГЛАЗА (наблюдает и автоматизирует)
- Brain = МОЗГ (принимает решения)
- DevOps Agent = РУКИ (исправляет проблемы)
- Analytics = АНАЛИТИК (анализирует trends)

✅ **Масштабируемость**
- Динамическая регистрация
- Автоматическое обнаружение новых инстансов

✅ **Надежность**
- Постоянная проверка health
- Автоматическое восстановление

---

## 📊 Метрики успеха

После внедрения отслеживаем:

1. **Metrics Coverage**: >= 95% сервисов мониторятся
2. **Time to Monitor**: < 1 минута от регистрации до сбора метрик
3. **Manual Interventions**: 0 (полная автоматизация)
4. **Issue Detection Time**: < 1 минута
5. **Issue Resolution Time**: < 5 минут (с DevOps Agent)

---

## 🚀 Следующие шаги

1. ✅ Документировать текущее состояние (этот документ)
2. ⏭️ Создать Metrics Coverage Observer
3. ⏭️ Создать Metrics Health Checker
4. ⏭️ Создать Metrics Registration Automator
5. ⏭️ Мигрировать Prometheus на file-based SD
6. ⏭️ Интегрировать с DevOps Agent для автоматических исправлений
