# 🤖 ТЕХНИЧЕСКОЕ ЗАДАНИЕ ДЛЯ АНАЛИЗА BCM ПЛАТФОРМЫ

## 🎯 ЗАДАЧА: Провести ПОЛНЫЙ профессиональный анализ BCM Platform

### 📋 ТРЕБОВАНИЯ К АНАЛИЗУ

#### 🔍 **ДЛЯ КАЖДОГО ИЗ 23 BCM МОДУЛЕЙ выполнить:**

**1. СТРУКТУРНЫЙ АНАЛИЗ:**
```bash
# Подсчитать файлы
find /path/to/module -name "*.py" | wc -l
find /path/to/module -name "*.xml" | wc -l
find /path/to/module -name "*.js" | wc -l

# Подсчитать строки кода
wc -l /path/to/module/models/*.py
wc -l /path/to/module/controllers/*.py
wc -l /path/to/module/views/*.xml
```

**2. АНАЛИЗ МОДЕЛЕЙ - ПРОЧИТАТЬ КАЖДЫЙ ФАЙЛ:**
```python
# Для каждого файла в models/ определить:
- Имена всех классов моделей
- Количество полей в каждой модели
- Computed fields и их сложность
- @api.depends зависимости
- Constraints и validations
- Methods и их назначение
- Inherit от других моделей
- Связи Many2one, One2many, Many2many
```

**3. АНАЛИЗ КОНТРОЛЛЕРОВ - ПРОЧИТАТЬ КАЖДЫЙ ФАЙЛ:**
```python
# Для каждого файла в controllers/ определить:
- Все @http.route endpoints
- HTTP методы (GET, POST, PUT, DELETE)
- Auth requirements ('user', 'public', 'none')
- CORS настройки
- JSON/HTTP type routes
- Параметры и return форматы
```

**4. АНАЛИЗ VIEWS - ПРОЧИТАТЬ КАЖДЫЙ XML:**
```xml
<!-- Для каждого файла в views/ определить: -->
- Типы view (tree, form, kanban, search, etc.)
- Actions и их конфигурация
- Menu items и их иерархия
- Wizard views
- Website templates
- Assets (CSS/JS)
```

**5. АНАЛИЗ AI ИНТЕГРАЦИИ:**
```python
# Искать в коде:
- Наследование от 'bcm.intelligent.base'
- Импорты AI библиотек (requests, numpy, pandas, etc.)
- Методы с 'ai_' в названии
- Вызовы AI сервисов
- Machine Learning алгоритмы
- Vector embeddings
- AI-generated контент
```

**6. АНАЛИЗ ВНЕШНИХ ИНТЕГРАЦИЙ:**
```python
# Искать в коде:
- external_dependencies в __manifest__.py
- import requests, httpx, websocket
- URL endpoints к внешним системам
- API ключи и аутентификация
- Webhook обработчики
- Event Bus интеграции
```

**7. АНАЛИЗ БИЗНЕС-ЛОГИКИ:**
```python
# Для каждой модели определить:
- Бизнес-процессы (workflows)
- State transitions
- Validation rules
- Computed business metrics
- Report generation
- Email notifications
- Cron jobs
```

### 📊 ТРЕБУЕМЫЙ РЕЗУЛЬТАТ

Для каждого модуля создать таблицу:

| Параметр | Значение | Детали |
|----------|----------|--------|
| **Размер кода** | X строк Python + Y строк XML | Точные цифры |
| **Модели** | [список классов] | Имена всех моделей |
| **Endpoints** | [список @http.route] | Все API endpoints |
| **AI компоненты** | [список AI классов/методов] | Все AI функции |
| **Внешние интеграции** | [список систем] | К каким системам подключен |
| **Views** | [типы views] | tree/form/kanban/search/etc |
| **Complexity Score** | 1-5 звезд | Объективная оценка |
| **Readiness** | X% | Процент готовности |
| **Dependencies** | [список зависимостей] | Все зависимости |
| **Key Features** | [список функций] | Основной функционал |

### 🎯 ПРИМЕР ПРАВИЛЬНОГО АНАЛИЗА:

**bcm_clients:**
- **Размер:** 367+259+294+198 = 1118 строк Python + 266+200+150+120 = 736 строк XML
- **Модели:** BcmClient, BcmClientVault, BcmClientAppkey, BcmClientContact, BcmScope
- **Endpoints:** /api/clients, /api/clients/<id> (из bcm_modules_api.py)
- **AI:** Vector embeddings (pgvector), AI Orchestrator webhooks, context reindexing
- **Интеграции:** AI Orchestrator, PostgreSQL pgvector, Keycloak portal users
- **Views:** tree, form, kanban, search + 3 sub-model views
- **Complexity:** ⭐⭐⭐⭐⭐ (Enterprise CRM система)
- **Readiness:** 95% (production ready)
- **Dependencies:** bcm_intelligent_base, portal, hr
- **Features:** Multi-tenant CRM, API key management, Vector search, Smart metrics

### 🎯 КРИТЕРИИ КАЧЕСТВА АНАЛИЗА:

**✅ ХОРОШО:** Прочитаны ВСЕ файлы, найдены ВСЕ функции, точные цифры
**❌ ПЛОХО:** Поверхностный анализ, догадки, неточные оценки

### 📝 ИНСТРУКЦИИ ДЛЯ АГЕНТА:

1. **Читай ВСЕ файлы полностью** - не ограничивайся первыми строками
2. **Считай точно** - используй wc -l, grep -c, find
3. **Ищи скрытые функции** - методы в конце файлов, комментированный код
4. **Проверяй __init__.py** - какие модели реально импортированы
5. **Анализируй external_dependencies** - какие библиотеки используются
6. **Изучай computed fields** - там часто скрыта сложная логика
7. **Ищи TODO комментарии** - показывают планируемый функционал

### 🚨 ОШИБКИ, КОТОРЫХ ИЗБЕГАТЬ:

❌ **Не делать:**
- Анализировать только __manifest__.py
- Читать только первые 30 строк файлов
- Догадываться о функционале по названиям
- Пропускать controllers и views
- Игнорировать external_dependencies

✅ **Делать:**
- Читать каждый файл полностью
- Считать точные метрики
- Проверять реальную сложность кода
- Искать скрытые интеграции
- Анализировать бизнес-логику