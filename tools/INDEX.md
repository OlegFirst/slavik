# AI-Platform-ISO Automation Toolkit - Навигация

## 📁 Структура

```
tools/
├── INDEX.md                        # ⭐ ВЫ ЗДЕСЬ - Навигация
├── QUICKSTART_TZ.md               # ⭐ СТАРТ ОТСЮДА - Краткое ТЗ (5 мин)
├── README.md                       # 📖 Полная документация (23 стр)
├── LICENSES_AND_COSTS.md           # 💰 Лицензии и стоимость
│
├── setup.sh                        # 🚀 Установка (запустить первым)
├── run_analysis.sh                 # 🚀 Полный анализ (запустить вторым)
│
├── config/
│   └── analysis_config.yaml        # ⚙️ Конфигурация сканирования
│
├── analyzers/
│   ├── ast_analyzer.py             # 🔍 Функции, классы, эндпоинты
│   └── dependency_mapper.py        # 🔗 Граф зависимостей
│
├── generators/
│   ├── api_docs_generator.py       # 📄 API документация
│   └── ui_blueprint_gen.py         # 🎨 UI схемы
│
├── dashboards/
│   └── module_dashboard.py         # 📊 Интерактивные дашборды
│
└── reports/                        # 📂 Результаты (создается автоматически)
    ├── ast_analysis.json
    ├── dependencies.json
    ├── dashboard.html              # ⭐ Открыть в браузере
    ├── endpoint_map.html           # ⭐ Открыть в браузере
    └── dependency_network.html     # ⭐ Открыть в браузере
```

---

## 🚀 Быстрый старт

### 1️⃣ Первый запуск (10 минут)

```bash
# Установка
chmod +x tools/setup.sh
./tools/setup.sh

# Анализ
chmod +x tools/run_analysis.sh
./tools/run_analysis.sh

# Открыть дашборд
open tools/reports/dashboard.html
```

### 2️⃣ Генерация UI blueprints

```bash
python3 tools/generators/ui_blueprint_gen.py
open docs/ui/index.html
```

### 3️⃣ API документация (опционально)

```bash
# Запустить сервисы
cd platform-services/validation-service && python3 main.py &

# Генерировать документацию
python3 tools/generators/api_docs_generator.py
open docs/api/README.md
```

---

## 📚 Документация

| Файл | Назначение | Время чтения |
|------|------------|--------------|
| **QUICKSTART_TZ.md** | ⭐ ТЗ для быстрого старта | 5 мин |
| **README.md** | Полная документация | 15 мин |
| **LICENSES_AND_COSTS.md** | Лицензии и стоимость инструментов | 5 мин |
| **INDEX.md** | Этот файл - навигация | 2 мин |

---

## 🛠️ Инструменты

### Анализаторы

| Файл | Команда | Результат |
|------|---------|-----------|
| **ast_analyzer.py** | `python3 tools/analyzers/ast_analyzer.py` | Все функции, классы, эндпоинты |
| **dependency_mapper.py** | `python3 tools/analyzers/dependency_mapper.py` | Граф зависимостей |

### Генераторы

| Файл | Команда | Результат |
|------|---------|-----------|
| **api_docs_generator.py** | `python3 tools/generators/api_docs_generator.py` | Markdown + Postman |
| **ui_blueprint_gen.py** | `python3 tools/generators/ui_blueprint_gen.py` | HTML схемы UI |

### Дашборды

| Файл | Команда | Результат |
|------|---------|-----------|
| **module_dashboard.py** | `python3 tools/dashboards/module_dashboard.py` | Интерактивные графики |

---

## 📊 Результаты

### После `run_analysis.sh`

```
tools/reports/
├── ast_analysis.json               # JSON: все функции/классы/эндпоинты
├── ast_analysis.md                 # Markdown отчет
├── dependencies.json               # JSON: зависимости
├── dependencies.md                 # Markdown отчет
├── dependency_graph.png            # PNG: граф
├── security_scan.json              # Bandit: безопасность
├── pylint_report.json              # Pylint: качество
├── dashboard.html                  # ⭐ Интерактивный дашборд
├── endpoint_map.html               # ⭐ Карта эндпоинтов
└── dependency_network.html         # ⭐ Граф зависимостей
```

### После `ui_blueprint_gen.py`

```
docs/ui/
├── index.html                      # ⭐ Навигация
├── validation_blueprint.html       # UI схемы
├── validation_spec.json            # JSON спецификация
├── documents_blueprint.html        # UI схемы
└── documents_spec.json             # JSON спецификация
```

### После `api_docs_generator.py`

```
docs/api/
├── README.md                       # Индекс
├── validation.md                   # Markdown документация
├── documents.md                    # Markdown документация
└── postman_collection.json         # ⭐ Postman коллекция
```

---

## 💡 Частые задачи

### Задача: Изучить новый модуль

```bash
./tools/run_analysis.sh
open tools/reports/dashboard.html
open tools/reports/endpoint_map.html
```

### Задача: Спланировать UI

```bash
python3 tools/generators/ui_blueprint_gen.py
open docs/ui/index.html
cat docs/ui/validation_spec.json | jq
```

### Задача: Проверить безопасность

```bash
./tools/run_analysis.sh
cat tools/reports/security_scan.json | jq '.results[] | select(.issue_severity=="HIGH")'
```

### Задача: Документация для команды

```bash
# Запустить сервисы
cd platform-services/validation-service && python3 main.py &

# Генерировать документацию
python3 tools/generators/api_docs_generator.py
open docs/api/README.md
```

---

## 💰 Стоимость

**Все инструменты бесплатные:**
- ✅ 13 инструментов
- ✅ 0₽ стоимость
- ✅ Без регистрации
- ✅ Без ограничений

Подробнее: [LICENSES_AND_COSTS.md](LICENSES_AND_COSTS.md)

---

## 🆘 Помощь

### Ошибка: "No module named 'radon'"

```bash
./tools/setup.sh
```

### Ошибка: "No data found"

```bash
python3 tools/analyzers/ast_analyzer.py
python3 tools/analyzers/dependency_mapper.py
python3 tools/dashboards/module_dashboard.py
```

### Ошибка: "Service not responding"

```bash
cd platform-services/validation-service && python3 main.py &
cd platform-services/documents-service && python3 main.py &
python3 tools/generators/api_docs_generator.py
```

---

## ✅ Чеклист

- [ ] Прочитать [QUICKSTART_TZ.md](QUICKSTART_TZ.md) (5 мин)
- [ ] Запустить `./tools/setup.sh`
- [ ] Запустить `./tools/run_analysis.sh`
- [ ] Открыть `tools/reports/dashboard.html`
- [ ] Сгенерировать UI blueprints
- [ ] (Опционально) Сгенерировать API документацию

**Время:** 10-15 минут
**Результат:** Полное понимание всех модулей

---

## 📖 Рекомендуемый порядок чтения

1. **INDEX.md** (этот файл) - 2 мин
2. **QUICKSTART_TZ.md** - 5 мин ⭐ НАЧАТЬ ОТСЮДА
3. **README.md** - 15 мин (детальная документация)
4. **LICENSES_AND_COSTS.md** - 5 мин (опционально)

---

🚀 **Начните с [QUICKSTART_TZ.md](QUICKSTART_TZ.md)**
