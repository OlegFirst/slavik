# KQM Quick Start Guide
## Knowledge Quality Manager - Быстрый Старт

**Версия**: 1.0
**Дата**: 2025-10-11
**Время до запуска**: 5 минут ⏱️

---

## 🚀 Быстрый Запуск (5 минут)

### Шаг 1: Установка зависимостей (1 мин)

```bash
cd /Users/MD/AI-Platform-ISO/platform-services/AI-services-management

# Установить пакеты
pip install -r requirements.txt
```

### Шаг 2: Проверка конфигурации (1 мин)

```bash
# Проверить настройки
cat config/settings.py

# Убедиться что указаны:
# - DATABASE_URL (PostgreSQL)
# - REDIS_URL (Redis)
# - ANTHROPIC_API_KEY (Claude)
# - Пути к сценариям
```

### Шаг 3: Запуск сервиса (30 сек)

```bash
# Development режим (с hot reload)
python main.py

# Или production режим
uvicorn main:app --host 0.0.0.0 --port 8090
```

### Шаг 4: Проверка работоспособности (30 сек)

```bash
# Health check
curl http://localhost:8090/health

# Ожидаемый ответ:
{
  "status": "healthy",
  "service": "knowledge-quality-manager",
  "port": 8090,
  "version": "1.0.0"
}
```

### Шаг 5: Первый тест (2 мин)

```bash
# Получить статус системы
curl http://localhost:8090/api/kqm/status

# Получить покрытие знаний
curl http://localhost:8090/api/kqm/knowledge/coverage

# Получить обнаруженные пробелы
curl http://localhost:8090/api/kqm/knowledge/gaps

# Запустить генерацию (первые 5 сценариев)
curl -X POST http://localhost:8090/api/kqm/scenarios/generate
```

✅ **Готово!** KQM запущен и работает.

---

## 📋 API Endpoints

### Health & Status
```bash
GET /health                    # Health check
GET /                          # Service info
GET /api/kqm/status            # Полный статус KQM
```

### Knowledge (Знания)
```bash
GET /api/kqm/knowledge/coverage   # Покрытие знаний
GET /api/kqm/knowledge/gaps       # Обнаруженные пробелы
```

### Scenarios (Сценарии)
```bash
POST /api/kqm/scenarios/generate  # Сгенерировать сценарии
# Body (опционально):
{
  "gap_ids": ["gap_iso_8_2", "gap_cap_bia"]
}
```

### Compliance (Соответствие)
```bash
GET /api/kqm/compliance/status    # Статус соответствия ISO/NIST/WHO
```

### Analytics (Аналитика)
```bash
GET /api/kqm/analytics/metrics    # Полные метрики KQM
```

### Documentation
```bash
GET /docs                         # Swagger UI (интерактивная документация)
GET /redoc                        # ReDoc (альтернативная документация)
```

---

## 🔄 Orchestration Cycle (Автоматический Цикл)

KQM работает в **24-часовом цикле** автоматически:

```
[Старт] →
  1. Оценка состояния знаний (Knowledge Monitor)
  2. Обнаружение пробелов (Gap Detection)
  3. Приоритизация (Top 10)
  4. Генерация сценариев (Scenario Generator)
  5. Валидация (Compliance Controller)
  6. Сохранение (File + RAG + Redis + PostgreSQL)
  7. Отчёт (Metrics Report)
→ [Сон 24 часа] → [Повтор]
```

**Логи цикла**:
```
🔄 Orchestration cycle: Starting...
📊 Cycle: Assessing knowledge state...
   Coverage: 85.0%
   Quality: 88.0%
   Gaps detected: 23
   Prioritized: 10 gaps
🤖 Generating scenarios...
   Generated: 10 scenarios
✅ Validating scenarios...
   Approved: 8/10
   Stored: 8 scenarios
✅ Cycle complete. Sleeping 24 hours...
```

---

## 📁 Структура Проекта

```
/platform-services/AI-services-management/
├── main.py                           # FastAPI сервис
├── models.py                         # Data models (Pydantic)
├── requirements.txt                  # Зависимости
│
├── config/
│   ├── __init__.py
│   └── settings.py                   # Настройки (порт, URLs, API keys)
│
├── tools/                            # ЗНАНИЕ
│   ├── __init__.py
│   └── scenario_generator.py        # Генератор сценариев
│
├── analytics/                        # ЗНАНИЕ + САМОРЕАЛИЗАЦИЯ
│   ├── __init__.py
│   └── knowledge_monitor.py         # Монитор знаний
│
├── validation/                       # ЗАЩИТА
│   ├── __init__.py
│   └── compliance_controller.py     # Контроллер соответствия
│
└── docs/
    ├── KNOWLEDGE_QUALITY_MANAGER_ARCHITECTURE.md   # Архитектура
    ├── TRINITY_PHILOSOPHY.md                       # Философия
    ├── QUICK_START.md                              # Этот файл
    └── KQM_IMPLEMENTATION_SUMMARY.md               # Итоговый отчёт
```

---

## 🎯 Первые Задачи

### Задача 1: Оценить Покрытие ISO 22301
```bash
curl http://localhost:8090/api/kqm/knowledge/coverage

# Проверить:
# - iso_coverage (целевое значение: 85%)
# - iso_clauses_documented / iso_clauses_total
```

### Задача 2: Обнаружить Пробелы
```bash
curl http://localhost:8090/api/kqm/knowledge/gaps

# Получить:
# - total_gaps
# - top_priorities (топ 10 пробелов)
```

### Задача 3: Сгенерировать Первые Сценарии
```bash
curl -X POST http://localhost:8090/api/kqm/scenarios/generate

# Результат:
# - generated: количество сгенерированных
# - validated: количество валидированных
# - approved: количество одобренных
# - scenarios: список сценариев
```

### Задача 4: Проверить Compliance
```bash
curl http://localhost:8090/api/kqm/compliance/status

# Проверить:
# - overall_compliance (целевое значение: 90%)
# - critical_gaps (должно быть 0)
```

### Задача 5: Посмотреть Полные Метрики
```bash
curl http://localhost:8090/api/kqm/analytics/metrics

# Получить:
# - knowledge_coverage
# - knowledge_quality
# - generation (сегодня/неделя/месяц)
# - performance (latency, cache hit rate)
# - gaps_detected (по типам)
```

---

## 🔧 Настройка

### Environment Variables

Создайте `.env` файл:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://:password@host:6379

# AI
ANTHROPIC_API_KEY=sk-ant-...

# Paths
SCENARIOS_PATH=/Users/MD/AI-Platform-ISO/platform-services/docs/business-scenarios
GENERATED_PATH=/Users/MD/AI-Platform-ISO/platform-services/docs/business-scenarios/generated

# Thresholds
MIN_CONFIDENCE=0.7
COVERAGE_TARGET=0.85
VALIDATION_PASS_RATE=0.90

# Component URLs
AI_FOUNDATION_URL=http://localhost:8002
EXPERTISE_CENTER_URL=http://localhost:8003
PREDICTIVE_URL=http://localhost:8004
COMMUNITY_INTEL_URL=http://localhost:8005
```

### Настройка Production

```bash
# 1. Создать systemd service
sudo nano /etc/systemd/system/kqm.service

[Unit]
Description=Knowledge Quality Manager
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/AI-services-management
ExecStart=/usr/bin/uvicorn main:app --host 0.0.0.0 --port 8090
Restart=always

[Install]
WantedBy=multi-user.target

# 2. Запустить
sudo systemctl enable kqm
sudo systemctl start kqm
sudo systemctl status kqm
```

---

## 📊 Мониторинг

### Логи

```bash
# Development
# Логи выводятся в консоль

# Production
journalctl -u kqm -f
```

### Метрики (Prometheus)

KQM экспортирует метрики на `/metrics` (если настроен prometheus-fastapi-instrumentator):

```yaml
# Ключевые метрики:
- kqm_knowledge_coverage_iso
- kqm_knowledge_coverage_platform
- kqm_quality_validation_rate
- kqm_scenarios_generated_total
- kqm_gaps_detected_total
```

### Alerts

Рекомендуемые алерты:

```yaml
# ISO Coverage ниже целевого
- alert: LowISOCoverage
  expr: kqm_knowledge_coverage_iso < 0.85

# Критичные пробелы обнаружены
- alert: CriticalGapsDetected
  expr: kqm_gaps_critical_total > 0

# Низкая validation rate
- alert: LowValidationRate
  expr: kqm_quality_validation_rate < 0.90
```

---

## 🐛 Troubleshooting

### Проблема: Сервис не запускается

```bash
# Проверить зависимости
pip list | grep fastapi
pip list | grep anthropic

# Переустановить
pip install -r requirements.txt --force-reinstall
```

### Проблема: Ошибка подключения к БД

```bash
# Проверить DATABASE_URL
echo $DATABASE_URL

# Проверить доступность PostgreSQL
psql $DATABASE_URL -c "SELECT 1"
```

### Проблема: Ошибка Anthropic API

```bash
# Проверить API key
echo $ANTHROPIC_API_KEY

# Проверить лимиты
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

### Проблема: Генерация сценариев не работает

```bash
# Проверить логи
# Возможные причины:
# 1. Нет пробелов для генерации
# 2. Ошибка RAG (AI Foundation недоступен)
# 3. LLM timeout

# Решение: Проверить статус компонентов
curl http://localhost:8002/health  # AI Foundation
curl http://localhost:8003/health  # Expertise Center
```

---

## 📚 Дополнительные Ресурсы

- **Архитектура**: `KNOWLEDGE_QUALITY_MANAGER_ARCHITECTURE.md`
- **Философия Триединства**: `TRINITY_PHILOSOPHY.md`
- **Полный отчёт**: `KQM_IMPLEMENTATION_SUMMARY.md`
- **Swagger UI**: http://localhost:8090/docs
- **ReDoc**: http://localhost:8090/redoc

---

## 🎉 Следующие Шаги

1. ✅ Запустить KQM
2. ⏭️ Загрузить существующие 328 сценариев в RAG
3. ⏭️ Настроить базу данных (PostgreSQL схемы)
4. ⏭️ Интегрировать с AI Foundation
5. ⏭️ Интегрировать с Expertise Center
6. ⏭️ Запустить в production

---

**Статус**: ✅ KQM Готов к Работе
**Порт**: 8090
**Философия**: 🔺 Триединство (Знание → Защита → Самореализация)
**Цикл**: 24 часа непрерывного обучения

**"Познай себя, защити себя, реализуй себя"** 🚀
