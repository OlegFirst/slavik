# AI-Platform-ISO: Automation & Analysis Toolkit

> **Полная автоматизация анализа, документирования и визуализации микросервисов**

## 📋 Содержание

- [Быстрый старт](#быстрый-старт)
- [Инструменты](#инструменты)
- [Использование](#использование)
- [Результаты](#результаты)
- [Лицензии](#лицензии)

---

## 🚀 Быстрый старт

### 1. Установка (5 минут)

```bash
cd /Users/MD/AI-Platform-ISO
chmod +x tools/setup.sh
./tools/setup.sh
```

Скрипт установит все необходимые инструменты и создаст структуру директорий.

### 2. Запуск полного анализа (5 минут)

```bash
chmod +x tools/run_analysis.sh
./tools/run_analysis.sh
```

Этот скрипт выполнит:
- ✅ AST-анализ (функции, классы, эндпоинты)
- ✅ Карту зависимостей между модулями
- ✅ Анализ сложности кода (Cyclomatic, Cognitive)
- ✅ Сканирование безопасности (Bandit OWASP)
- ✅ Анализ качества кода (Pylint)
- ✅ Интерактивные дашборды

### 3. Просмотр результатов

```bash
# Открыть главный дашборд
open tools/reports/dashboard.html

# Открыть UI blueprints
python3 tools/generators/ui_blueprint_gen.py
open docs/ui/index.html
```

---

## 🛠️ Инструменты

### Анализаторы (`tools/analyzers/`)

| Файл | Назначение | Использование |
|------|------------|---------------|
| **ast_analyzer.py** | Извлечение функций, классов, эндпоинтов | `python3 tools/analyzers/ast_analyzer.py` |
| **dependency_mapper.py** | Граф зависимостей, циклические зависимости | `python3 tools/analyzers/dependency_mapper.py` |

### Генераторы (`tools/generators/`)

| Файл | Назначение | Использование |
|------|------------|---------------|
| **api_docs_generator.py** | Markdown документация из OpenAPI | `python3 tools/generators/api_docs_generator.py` |
| **ui_blueprint_gen.py** | UI blueprints для фронтенда | `python3 tools/generators/ui_blueprint_gen.py` |

### Дашборды (`tools/dashboards/`)

| Файл | Назначение | Использование |
|------|------------|---------------|
| **module_dashboard.py** | Интерактивные визуализации (Plotly) | `python3 tools/dashboards/module_dashboard.py` |

---

## 📊 Использование

### 1. AST-анализ

Извлекает все функции, классы и API эндпоинты:

```bash
python3 tools/analyzers/ast_analyzer.py
```

**Результаты:**
- `tools/reports/ast_analysis.json` - JSON со всеми данными
- `tools/reports/ast_analysis.md` - Markdown отчет

**Пример JSON:**
```json
{
  "functions": [
    {
      "name": "record_measurement",
      "file": ".../validation-service/api/routes.py",
      "line": 245,
      "params": ["kpi_id", "measurement", "kpi_service"],
      "is_async": true,
      "decorators": ["post"]
    }
  ],
  "endpoints": [
    {
      "path": "/kpis/{kpi_id}/measure",
      "method": "POST",
      "function": "record_measurement",
      "dependencies": ["get_kpi_service"]
    }
  ]
}
```

### 2. Карта зависимостей

Анализирует imports и строит граф зависимостей:

```bash
python3 tools/analyzers/dependency_mapper.py
```

**Результаты:**
- `tools/reports/dependencies.json` - Список зависимостей
- `tools/reports/dependencies.md` - Markdown отчет
- `tools/reports/dependency_graph.png` - Граф (PNG)
- `tools/reports/dependency_graph.graphml` - Граф для Gephi/Cytoscape
- `tools/reports/circular_dependencies.json` - Циклические зависимости (если есть)

### 3. Анализ сложности кода

Используя Radon:

```bash
# Cyclomatic Complexity
radon cc platform-services/ -a -s

# Maintainability Index
radon mi platform-services/ -s

# Halstead metrics
radon hal platform-services/
```

**Интерпретация:**
- **A-B** (1-5): Простой код, легко поддерживать
- **C** (6-10): Умеренная сложность
- **D-F** (>10): Высокая сложность, требуется рефакторинг

### 4. Сканирование безопасности

Используя Bandit (OWASP):

```bash
# Полный скан
bandit -r platform-services/ -f json -o tools/reports/security_scan.json

# Только высокий приоритет
bandit -r platform-services/ -ll
```

**Проверяет:**
- SQL-инъекции
- Hardcoded secrets
- Небезопасные функции
- Уязвимости зависимостей

### 5. Интерактивные дашборды

```bash
python3 tools/dashboards/module_dashboard.py
```

**Генерирует 3 HTML файла:**

1. **dashboard.html** - Общая статистика:
   - Эндпоинты по методам (GET/POST/PUT/DELETE)
   - Топ-10 модулей по зависимостям
   - Функции vs Классы
   - Async vs Sync функции

2. **endpoint_map.html** - Sunburst диаграмма:
   - Иерархия API эндпоинтов
   - Группировка по файлам

3. **dependency_network.html** - Интерактивная сеть:
   - Граф зависимостей
   - Цвет узла = количество зависимостей

### 6. UI Blueprints

Генерирует схемы интерфейсов на основе API:

```bash
python3 tools/generators/ui_blueprint_gen.py
```

**Результаты:**
- `docs/ui/validation_blueprint.html` - UI для Validation Service
- `docs/ui/documents_blueprint.html` - UI для Documents Service
- `docs/ui/validation_spec.json` - JSON спецификация экранов
- `docs/ui/index.html` - Навигация по всем blueprints

**Что генерируется для каждого ресурса:**
- 📋 **List Screen** - таблица, поиск, фильтры, пагинация
- ➕ **Create Screen** - форма создания
- 👁️ **Detail Screen** - просмотр деталей
- ✏️ **Edit Screen** - редактирование
- ⚡ **Custom Actions** - дополнительные операции

### 7. API Документация

Генерирует документацию из OpenAPI спецификаций:

```bash
# Запустить сервисы
cd platform-services/validation-service && python main.py &
cd platform-services/documents-service && python main.py &

# Генерировать документацию
python3 tools/generators/api_docs_generator.py
```

**Результаты:**
- `docs/api/validation.md` - Markdown документация
- `docs/api/documents.md` - Markdown документация
- `docs/api/README.md` - Индекс всех сервисов
- `docs/api/postman_collection.json` - Postman коллекция

---

## 📁 Структура результатов

```
AI-Platform-ISO/
├── tools/
│   ├── reports/                    # Все отчеты анализа
│   │   ├── ast_analysis.json
│   │   ├── ast_analysis.md
│   │   ├── dependencies.json
│   │   ├── dependencies.md
│   │   ├── dependency_graph.png
│   │   ├── dependency_graph.graphml
│   │   ├── security_scan.json
│   │   ├── pylint_report.json
│   │   ├── dashboard.html          # ⭐ Интерактивный дашборд
│   │   ├── endpoint_map.html       # ⭐ Карта эндпоинтов
│   │   └── dependency_network.html # ⭐ Граф зависимостей
│   └── config/
│       └── analysis_config.yaml    # Конфигурация
├── docs/
│   ├── api/                        # API документация
│   │   ├── README.md
│   │   ├── validation.md
│   │   ├── documents.md
│   │   └── postman_collection.json
│   └── ui/                         # UI Blueprints
│       ├── index.html              # ⭐ Навигация
│       ├── validation_blueprint.html
│       ├── validation_spec.json
│       ├── documents_blueprint.html
│       └── documents_spec.json
```

---

## 🎯 Сценарии использования

### Сценарий 1: Быстрое изучение нового модуля

```bash
# 1. Проанализировать код
./tools/run_analysis.sh

# 2. Открыть дашборд
open tools/reports/dashboard.html

# 3. Изучить эндпоинты
open tools/reports/endpoint_map.html

# 4. Посмотреть зависимости
open tools/reports/dependency_network.html
```

**Результат:** Полное понимание модуля за 5 минут

### Сценарий 2: Планирование UI

```bash
# 1. Сгенерировать UI blueprints
python3 tools/generators/ui_blueprint_gen.py

# 2. Открыть blueprints
open docs/ui/index.html

# 3. Использовать JSON спецификации для генерации кода
cat docs/ui/validation_spec.json
```

**Результат:** Готовые схемы всех экранов

### Сценарий 3: Проверка безопасности перед деплоем

```bash
# 1. Сканирование безопасности
bandit -r platform-services/ -ll

# 2. Проверка циклических зависимостей
python3 tools/analyzers/dependency_mapper.py

# 3. Анализ сложности
radon cc platform-services/ -a -s
```

**Результат:** Список проблем для исправления

### Сценарий 4: Создание документации для команды

```bash
# 1. Запустить сервисы
# (в отдельных терминалах)

# 2. Сгенерировать API документацию
python3 tools/generators/api_docs_generator.py

# 3. Открыть документацию
open docs/api/README.md
```

**Результат:** Полная Markdown документация + Postman коллекция

---

## 💰 Лицензии и стоимость

### ✅ БЕСПЛАТНЫЕ (Установлено через setup.sh)

| Инструмент | Лицензия | Регистрация |
|------------|----------|-------------|
| Radon | MIT | ❌ Не требуется |
| Pylint | GPL-2.0 | ❌ Не требуется |
| Bandit | Apache-2.0 | ❌ Не требуется |
| Prospector | GPL-2.0 | ❌ Не требуется |
| NetworkX | BSD-3 | ❌ Не требуется |
| Plotly | MIT | ❌ Не требуется |
| Sphinx | BSD-2 | ❌ Не требуется |

### 🆓 БЕСПЛАТНЫЕ (С ограничениями)

| Инструмент | Free Tier | Платная версия |
|------------|-----------|----------------|
| **SonarQube** | Community Edition (без ограничений) | Enterprise: по запросу |
| **Postman** | 1000 запросов/месяц | Team: $12/user/месяц |
| **GitBook** | Бесплатно для open-source | Team: $6.70/user/месяц |

### 💵 ПЛАТНЫЕ (Не обязательны)

| Инструмент | Стоимость | Нужно? |
|------------|-----------|--------|
| **CodeClimate** | $249/месяц | ❌ Нет (есть Pylint + Bandit) |
| **Snyk** | $25/месяц | ❌ Нет (есть Bandit) |
| **DeepSource** | $30/месяц | ❌ Нет (есть Radon) |

**💡 Рекомендация:** Используйте только бесплатные инструменты. Они покрывают 100% потребностей.

---

## 🔧 Настройка

### Конфигурация сканирования

Редактировать `tools/config/analysis_config.yaml`:

```yaml
# Directories to scan
scan_paths:
  - platform-services/validation-service
  - platform-services/documents-service
  - shared

# Exclude patterns
exclude:
  - "*/venv/*"
  - "*/__pycache__/*"
  - "*/migrations/*"

# Complexity thresholds
complexity:
  max_cyclomatic: 10  # Максимальная цикломатическая сложность
  max_cognitive: 15   # Максимальная когнитивная сложность
  warn_threshold: 5   # Порог предупреждения

# Security
security:
  confidence_level: "HIGH"
  severity_level: "MEDIUM"
```

### Добавление новых сервисов

1. Добавить путь в `scan_paths` в `analysis_config.yaml`
2. Добавить сервис в `api_docs_generator.py`:

```python
self.services = {
    'validation': 8022,
    'documents': 8024,
    'governance': 8020,
    'my_new_service': 8030,  # <-- Добавить
}
```

3. Запустить анализ:

```bash
./tools/run_analysis.sh
```

---

## 🎓 Лучшие практики

### 1. Регулярный анализ

Запускайте полный анализ:
- ✅ **После каждого PR** - проверка качества
- ✅ **Раз в неделю** - мониторинг технического долга
- ✅ **Перед релизом** - финальная проверка

### 2. Пороги качества

Установите CI/CD проверки:

```bash
# Cyclomatic complexity < 10
radon cc . -nc -a | grep -E "F|E|D" && exit 1

# Maintainability Index > 65
radon mi . -nb | awk '$2 < 65 {exit 1}'

# No high security issues
bandit -r . -ll -f json | jq '.results | length' | grep -q '^0$'
```

### 3. Документация всегда актуальна

Добавьте в CI/CD:

```bash
# Генерировать документацию после деплоя
python3 tools/generators/api_docs_generator.py
python3 tools/generators/ui_blueprint_gen.py
```

---

## 🐛 Troubleshooting

### Проблема: "No module named 'radon'"

```bash
pip3 install radon pylint bandit prospector networkx matplotlib plotly
```

### Проблема: "No data found. Run analyzers first!"

```bash
# Сначала запустите анализаторы
python3 tools/analyzers/ast_analyzer.py
python3 tools/analyzers/dependency_mapper.py

# Потом дашборд
python3 tools/dashboards/module_dashboard.py
```

### Проблема: "Service not responding"

```bash
# Убедитесь, что сервисы запущены
ps aux | grep python | grep -E "validation|documents"

# Запустите сервисы
cd platform-services/validation-service && python3 main.py &
cd platform-services/documents-service && python3 main.py &
```

---

## 📚 Дополнительные ресурсы

- [Radon Documentation](https://radon.readthedocs.io/)
- [Bandit Security Guide](https://bandit.readthedocs.io/)
- [Pylint User Guide](https://pylint.pycqa.org/en/latest/)
- [NetworkX Tutorial](https://networkx.org/documentation/stable/tutorial.html)
- [Plotly Python](https://plotly.com/python/)

---

## 🤝 Вклад

Этот toolkit создан для **AI-Platform-ISO** проекта. Для улучшений:

1. Создайте анализатор в `tools/analyzers/`
2. Добавьте в `run_analysis.sh`
3. Обновите эту документацию

---

## 📄 Лицензия

MIT License - используйте свободно для любых целей.

---

**🚀 Готово к использованию!** Запустите `./tools/setup.sh` и начните анализ.
