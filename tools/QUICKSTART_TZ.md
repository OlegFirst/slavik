# ТЗ: Automation Toolkit - Быстрый старт

> **Цель:** Автоматизация анализа, документирования и визуализации всех микросервисов AI-Platform-ISO

---

## 📋 ТЗ в 3 шагах

### Шаг 1: Установка (5 минут)

```bash
cd /Users/MD/AI-Platform-ISO
chmod +x tools/setup.sh
./tools/setup.sh
```

**Что установится:**
- 13 бесплатных инструментов анализа
- Структура директорий для отчетов
- Конфигурация по умолчанию

**Стоимость:** 0₽
**Регистрация:** Не требуется

---

### Шаг 2: Анализ (5 минут)

```bash
./tools/run_analysis.sh
```

**Что будет выполнено:**

| Этап | Инструмент | Результат | Файл |
|------|------------|-----------|------|
| 1. AST анализ | ast_analyzer.py | Все функции, классы, эндпоинты | `tools/reports/ast_analysis.json` |
| 2. Зависимости | dependency_mapper.py | Граф зависимостей, циклы | `tools/reports/dependencies.json` |
| 3. Сложность | radon | Cyclomatic, Maintainability Index | Консоль |
| 4. Безопасность | bandit | OWASP Top 10 проблемы | `tools/reports/security_scan.json` |
| 5. Качество | pylint | Ошибки стиля, потенциальные баги | `tools/reports/pylint_report.json` |
| 6. Дашборды | module_dashboard.py | Интерактивные графики | `tools/reports/dashboard.html` |

**Общее время:** ~5 минут

---

### Шаг 3: Результаты

#### A. Интерактивные дашборды

```bash
# Главный дашборд
open tools/reports/dashboard.html

# Карта эндпоинтов (Sunburst)
open tools/reports/endpoint_map.html

# Граф зависимостей
open tools/reports/dependency_network.html
```

**Что увидите:**
- 📊 Статистика по методам (GET/POST/PUT/DELETE)
- 🔗 Граф зависимостей между модулями
- 📈 Метрики сложности
- ⚡ Async vs Sync функции

#### B. UI Blueprints (схемы интерфейсов)

```bash
python3 tools/generators/ui_blueprint_gen.py
open docs/ui/index.html
```

**Что увидите:**
- Схемы экранов для каждого сервиса (List, Create, Detail, Edit)
- JSON спецификации для генерации кода
- Карта компонентов UI

#### C. API Документация

```bash
# Сначала запустить сервисы
cd platform-services/validation-service && python3 main.py &
cd platform-services/documents-service && python3 main.py &

# Генерировать документацию
python3 tools/generators/api_docs_generator.py
open docs/api/README.md
```

**Что увидите:**
- Markdown документация всех эндпоинтов
- Postman коллекция для импорта
- Схемы запросов/ответов

---

## 🎯 Основные файлы

### Созданные инструменты

```
tools/
├── setup.sh                        # ⭐ Установка всех инструментов
├── run_analysis.sh                 # ⭐ Полный анализ проекта
├── config/
│   └── analysis_config.yaml        # Конфигурация сканирования
├── analyzers/
│   ├── ast_analyzer.py             # Извлечение функций/классов/эндпоинтов
│   └── dependency_mapper.py        # Граф зависимостей
├── generators/
│   ├── api_docs_generator.py       # Генерация API документации
│   └── ui_blueprint_gen.py         # Генерация UI схем
├── dashboards/
│   └── module_dashboard.py         # Интерактивные дашборды
└── reports/                        # Все отчеты (создается автоматически)
```

### Документация

```
tools/
├── README.md                       # ⭐ Полная документация (23 страницы)
├── LICENSES_AND_COSTS.md           # ⭐ Лицензии и стоимость
└── QUICKSTART_TZ.md               # ⭐ Этот файл (краткое ТЗ)
```

---

## 📊 Результаты анализа

### После запуска `run_analysis.sh`

```
tools/reports/
├── ast_analysis.json               # JSON: все функции, классы, эндпоинты
├── ast_analysis.md                 # Markdown отчет
├── dependencies.json               # JSON: зависимости между модулями
├── dependencies.md                 # Markdown отчет
├── dependency_graph.png            # PNG: граф зависимостей
├── dependency_graph.graphml        # GraphML: для Gephi/Cytoscape
├── circular_dependencies.json      # Циклические зависимости (если есть)
├── security_scan.json              # Bandit: проблемы безопасности
├── pylint_report.json              # Pylint: качество кода
├── dashboard.html                  # ⭐ Интерактивный дашборд
├── endpoint_map.html               # ⭐ Sunburst карта эндпоинтов
└── dependency_network.html         # ⭐ Интерактивный граф
```

### После генерации UI blueprints

```
docs/ui/
├── index.html                      # ⭐ Навигация по всем сервисам
├── validation_blueprint.html       # UI схемы для Validation Service
├── validation_spec.json            # JSON спецификация экранов
├── documents_blueprint.html        # UI схемы для Documents Service
└── documents_spec.json             # JSON спецификация экранов
```

### После генерации API документации

```
docs/api/
├── README.md                       # Индекс всех сервисов
├── validation.md                   # Markdown документация
├── documents.md                    # Markdown документация
└── postman_collection.json         # ⭐ Postman коллекция
```

---

## 💡 Примеры использования

### Пример 1: Изучить новый модуль

```bash
# 1. Проанализировать
./tools/run_analysis.sh

# 2. Открыть дашборд
open tools/reports/dashboard.html

# 3. Посмотреть эндпоинты
open tools/reports/endpoint_map.html
```

**Результат:** Полное понимание модуля за 5 минут

---

### Пример 2: Спланировать UI

```bash
# 1. Сгенерировать UI blueprints
python3 tools/generators/ui_blueprint_gen.py

# 2. Открыть схемы
open docs/ui/validation_blueprint.html

# 3. Использовать JSON для генерации кода
cat docs/ui/validation_spec.json | jq '.resources.kpis.screens'
```

**Результат:** Готовые схемы всех экранов с компонентами

---

### Пример 3: Найти проблемы перед деплоем

```bash
# 1. Полный анализ
./tools/run_analysis.sh

# 2. Проверить безопасность
cat tools/reports/security_scan.json | jq '.results[] | select(.issue_severity=="HIGH")'

# 3. Найти циклические зависимости
cat tools/reports/circular_dependencies.json

# 4. Проверить сложность
radon cc platform-services/ -a -s | grep -E "F|E|D"
```

**Результат:** Список всех проблем для исправления

---

### Пример 4: Документация для команды

```bash
# 1. Запустить сервисы
cd platform-services/validation-service && python3 main.py &
cd platform-services/documents-service && python3 main.py &

# 2. Генерировать документацию
python3 tools/generators/api_docs_generator.py

# 3. Открыть Markdown
open docs/api/validation.md

# 4. Импортировать в Postman
# File → Import → docs/api/postman_collection.json
```

**Результат:** Полная документация + Postman коллекция

---

## 🔧 Кастомизация

### Изменить пути сканирования

Редактировать `tools/config/analysis_config.yaml`:

```yaml
scan_paths:
  - platform-services/validation-service
  - platform-services/documents-service
  - platform-services/governance-service  # <-- Добавить новый сервис
  - shared
```

### Изменить пороги сложности

```yaml
complexity:
  max_cyclomatic: 10   # Максимальная цикломатическая сложность
  max_cognitive: 15    # Максимальная когнитивная сложность
  warn_threshold: 5    # Порог предупреждения
```

### Добавить новый сервис в API документацию

Редактировать `tools/generators/api_docs_generator.py`:

```python
self.services = {
    'validation': 8022,
    'documents': 8024,
    'governance': 8020,
    'incident': 8025,
    'my_new_service': 8030,  # <-- Добавить
}
```

---

## 📈 Метрики качества

### Cyclomatic Complexity (Radon)

| Оценка | Значение | Интерпретация |
|--------|----------|---------------|
| **A** | 1-5 | ✅ Простой код, легко тестировать |
| **B** | 6-10 | ✅ Нормальная сложность |
| **C** | 11-20 | ⚠️ Умеренная сложность |
| **D** | 21-30 | ❌ Высокая сложность, рефакторить |
| **E** | 31-40 | ❌ Очень высокая сложность |
| **F** | 41+ | 🚨 Критическая сложность |

**Цель:** Все функции должны быть A-B (≤10)

### Maintainability Index (Radon)

| Оценка | Значение | Интерпретация |
|--------|----------|---------------|
| **A** | 100-20 | ✅ Легко поддерживать |
| **B** | 19-10 | ⚠️ Умеренно сложно |
| **C** | 9-0 | ❌ Сложно поддерживать |

**Цель:** MI > 65 (оценка A-B)

### Security Issues (Bandit)

| Уровень | Действие |
|---------|----------|
| **HIGH** | 🚨 Исправить немедленно |
| **MEDIUM** | ⚠️ Исправить перед релизом |
| **LOW** | ℹ️ Исправить когда возможно |

**Цель:** 0 HIGH issues

---

## 🎓 Лучшие практики

### 1. Регулярный анализ

```bash
# Еженедельно
./tools/run_analysis.sh

# Перед каждым PR
radon cc . -nc -a && bandit -r . -ll
```

### 2. CI/CD интеграция

```yaml
# .github/workflows/quality.yml
- name: Code Quality
  run: |
    radon cc . -nc -a | grep -E "F|E|D" && exit 1
    bandit -r . -ll -f json | jq '.results | length' | grep -q '^0$'
```

### 3. Автоматическая документация

```bash
# После деплоя каждого сервиса
python3 tools/generators/api_docs_generator.py
python3 tools/generators/ui_blueprint_gen.py
```

---

## 💰 Стоимость

| Категория | Инструментов | Стоимость |
|-----------|--------------|-----------|
| **Анализаторы** | 4 | 0₽ |
| **Визуализация** | 3 | 0₽ |
| **Документация** | 2 | 0₽ |
| **Тестирование** | 2 | 0₽ |
| **Вспомогательные** | 2 | 0₽ |
| **ИТОГО** | **13** | **0₽/месяц** |

**Регистрация:** ❌ Не требуется
**Ограничения:** ❌ Нет

Подробнее: [LICENSES_AND_COSTS.md](LICENSES_AND_COSTS.md)

---

## 🆘 Troubleshooting

### Ошибка: "No module named 'radon'"

```bash
pip3 install radon pylint bandit prospector networkx matplotlib plotly sphinx
```

### Ошибка: "No data found"

```bash
# Сначала запустить анализаторы
python3 tools/analyzers/ast_analyzer.py
python3 tools/analyzers/dependency_mapper.py

# Потом дашборды
python3 tools/dashboards/module_dashboard.py
```

### Ошибка: "Service not responding"

```bash
# Проверить, запущены ли сервисы
ps aux | grep python | grep -E "validation|documents"

# Запустить сервисы
cd platform-services/validation-service && python3 main.py &
```

---

## 📚 Документация

- **Полная документация:** [README.md](README.md)
- **Лицензии и стоимость:** [LICENSES_AND_COSTS.md](LICENSES_AND_COSTS.md)
- **Этот документ:** Краткое ТЗ для быстрого старта

---

## ✅ Чеклист выполнения ТЗ

- [ ] Установка: `./tools/setup.sh`
- [ ] Анализ: `./tools/run_analysis.sh`
- [ ] Открыть дашборд: `open tools/reports/dashboard.html`
- [ ] Сгенерировать UI blueprints: `python3 tools/generators/ui_blueprint_gen.py`
- [ ] Открыть UI blueprints: `open docs/ui/index.html`
- [ ] (Опционально) Сгенерировать API документацию: `python3 tools/generators/api_docs_generator.py`

**Время выполнения:** 10-15 минут
**Стоимость:** 0₽
**Результат:** Полное понимание всех модулей + готовые схемы UI + документация

---

🚀 **Готово к использованию!** Запускайте `./tools/setup.sh`
