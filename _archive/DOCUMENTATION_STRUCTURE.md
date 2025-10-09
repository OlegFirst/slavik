# Структура документации AI-Platform-ISO

**Дата**: 2025-10-09
**Версия**: 2.0.0

---

## 📁 Текущая структура

### Корень проекта `/`

**4 файла - точки входа:**

| Файл | Размер | Назначение |
|------|--------|------------|
| **README.md** | 17 KB | Главный README проекта - первая точка входа |
| **PROJECT_INDEX.md** | 7.6 KB | Мастер-индекс всего проекта - навигация по всем разделам |
| **QUICK_SPECS_REFERENCE.md** | 4.9 KB | Быстрая справка - ТОП-10 спецификаций + навигация по ролям |
| **PHASE1_QUICK_START.md** | 6.1 KB | Quick start для Phase 1 (System BCM) |

> ✅ **Корень организован правильно** - только главные индексы и README

---

### `/docs/` - Основная документация платформы

**14 MD файлов + 16 подпапок**

#### Главные файлы в `/docs/`:

| Файл | Размер | Описание |
|------|--------|----------|
| **INDEX.md** | 14 KB | Главный индекс документации |
| **README.md** | 15 KB | README документации |
| **ARCHITECTURE.md** | 73 KB | ⭐ Детальная архитектура платформы |
| **API_REFERENCE.md** | 40 KB | ⭐ API Reference (150+ endpoints) |
| **DEPLOYMENT_GUIDE.md** | 27 KB | ⭐ Руководство по развертыванию |
| **STANDARDS_COMPLIANCE.md** | 28 KB | ⭐ ISO 22301, NIST compliance |
| **EXECUTIVE_SUMMARY.md** | 16 KB | Executive summary |
| **GETTING_STARTED.md** | 20 KB | Руководство начала работы |
| **PLATFORM_ARCHITECTURE_MAP.md** | 5 KB | Карта архитектуры |
| **COMPLETE_DOCUMENTATION_MAP.md** | 19 KB | Полная карта документации |
| **ARCHIVE_INVENTORY.md** | 4 KB | Инвентаризация архива |
| **SYSTEM_BCM_INTEGRATION.md** | 13 KB | Интеграция System BCM |
| **00_INDEX_BY_SECTIONS.md** | 10 KB | Индекс по 13 секциям |

#### Подпапки в `/docs/`:

```
docs/
├── ai-capabilities/         # AI возможности (7 файлов)
├── analysis/                # Системный анализ
├── api/                     # AsyncAPI/OpenAPI спецификации
├── architecture/            # Архитектурные документы (15 файлов)
├── business-analysis/       # Бизнес-анализ
├── deployment/              # Deployment документация
├── executive/               # Executive документы
├── glossary/                # Глоссарий терминов
├── guides/                  # Руководства пользователя
├── integration/             # Интеграционные гайды
├── knowledge-library/       # База знаний (8 файлов)
├── modules/                 # Документация по модулям
├── reports/                 # Отчёты
├── scenarios/               # Сценарии использования
├── testing/                 # Тестирование
└── ui/                      # ⚠️ UI спецификации (HTML/JSON)
```

> ⚠️ **Проблема**: `/docs/ui/` содержит старые HTML/JSON файлы спецификаций

---

### `/doc-project/` - Проектная документация

**83 MD файла в корне + подпапки**

#### Главные ТЗ в `/doc-project/`:

| Файл | Размер | Описание |
|------|--------|----------|
| **TZ_AI_BCM_PLATFORM.md** | 63 KB | ⭐⭐⭐ Главное ТЗ платформы |
| **TZ_USER_INTERFACE.md** | 35 KB | ⭐⭐⭐ Полное ТЗ UI/UX |
| **SPECIFICATIONS_CATALOG.md** | - | Каталог всех 108 спецификаций |

#### Подпапки в `/doc-project/`:

```
doc-project/
├── architecture/            # 35 архитектурных файлов
├── integration/             # 20 интеграционных файлов
├── documentation/           # Файлы о документации
├── phases/                  # Документы по фазам
├── tasks/                   # Задачи и планы
├── reports/                 # 24 отчёта
├── system-bcm/              # 3 файла System BCM
├── ai-analysis/             # AI анализы
├── old-numbered/            # Архив старых файлов (123.md и т.д.)
├── diagrams/                # ⭐ 36 Mermaid диаграмм
│   ├── architecture/        # 24 диаграммы
│   ├── user-scenarios/      # 4 диаграммы
│   ├── dependencies/        # 1 диаграмма
│   ├── flows/               # 3 диаграммы
│   ├── integration/         # 4 диаграммы
│   └── business-processes/  # 1 диаграмма
└── _archived_docs/          # Архив старых версий
```

> ✅ **doc-project организован хорошо** - проектная документация и ТЗ

---

## 🎯 Рекомендуемая навигация

### Для новых пользователей:

1. Начать с **[README.md](../README.md)** в корне
2. Изучить **[PROJECT_INDEX.md](../PROJECT_INDEX.md)** для понимания структуры
3. Выбрать путь:
   - **Product/Business** → [docs/EXECUTIVE_SUMMARY.md](../docs/EXECUTIVE_SUMMARY.md)
   - **Technical** → [QUICK_SPECS_REFERENCE.md](../QUICK_SPECS_REFERENCE.md)
   - **Quick Start** → [PHASE1_QUICK_START.md](../PHASE1_QUICK_START.md)

### Для разработчиков:

1. **[QUICK_SPECS_REFERENCE.md](../QUICK_SPECS_REFERENCE.md)** - быстрая справка
2. **[docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)** - архитектура
3. **[docs/API_REFERENCE.md](../docs/API_REFERENCE.md)** - API
4. **[doc-project/diagrams/](../doc-project/diagrams/)** - визуализации

### Для UI/UX дизайнеров:

1. **[doc-project/TZ_USER_INTERFACE.md](../doc-project/TZ_USER_INTERFACE.md)** - полное ТЗ UI
2. **[doc-project/diagrams/user-scenarios/](../doc-project/diagrams/user-scenarios/)** - сценарии
3. Frontend спецификации сервисов

---

## ✅ Что организовано:

1. ✅ **Корень** - только 4 главных индекса
2. ✅ **`/docs/`** - основная документация платформы (125+ файлов)
3. ✅ **`/doc-project/`** - проектная документация (277 файлов)
4. ✅ **`/doc-project/diagrams/`** - все диаграммы (36 штук)
5. ✅ **`/doc-project/SPECIFICATIONS_CATALOG.md`** - каталог 108 спецификаций
6. ✅ Все ТЗ в `/doc-project/`

---

## ⚠️ Что нужно улучшить:

### 1. Папка `/docs/ui/` содержит старые файлы

**Текущее содержимое**:
- `documents_blueprint.html` (16 KB)
- `documents_spec.json` (9 KB)
- `governance_blueprint.html` (32 KB)
- `governance_spec.json` (21 KB)
- `other_blueprint.html` (159 KB)
- `other_spec.json` (97 KB)
- `validation_blueprint.html` (26 KB)
- `validation_spec.json` (17 KB)
- `index.html` (4 KB)

**Решение**:
- Переместить в `/_archive/old-ui-specs/`
- ~~Удалить папку `/docs/ui/`~~ Папка пустая после перемещения TZ
- Актуальное ТЗ UI теперь в `/doc-project/TZ_USER_INTERFACE.md`

### 2. Создать единый справочник UI спецификаций

**Локация**: `/doc-project/UI_SPECIFICATIONS_INDEX.md`

**Содержание**:
- Главное ТЗ: `TZ_USER_INTERFACE.md`
- Frontend спецификации сервисов:
  - Learning Service (59 KB)
  - Digital Twin (44 KB)
  - Community Service (20 KB)
- User scenario диаграммы (4 шт)
- Ссылки на все UI-related документы

---

## 📊 Статистика

| Категория | Файлов | Размер |
|-----------|--------|--------|
| Корень | 4 MD | ~36 KB |
| `/docs/` | 125+ MD | ~500 KB |
| `/doc-project/` | 277 MD | ~2 MB |
| Диаграммы | 36 .mmd | ~100 KB |
| Спецификации | 108 | ~1.67 MB |
| **ВСЕГО** | **~550** | **~4.3 MB** |

---

## 🗺️ Ключевые индексы (точки входа)

| Файл | Уровень | Что охватывает |
|------|---------|----------------|
| **[README.md](../README.md)** | L1 | Главная страница проекта |
| **[PROJECT_INDEX.md](../PROJECT_INDEX.md)** | L1 | Мастер-индекс всех разделов |
| **[QUICK_SPECS_REFERENCE.md](../QUICK_SPECS_REFERENCE.md)** | L1 | ТОП-10 спецификаций |
| **[docs/INDEX.md](../docs/INDEX.md)** | L2 | Индекс основной документации |
| **[docs/00_INDEX_BY_SECTIONS.md](../docs/00_INDEX_BY_SECTIONS.md)** | L2 | Индекс по 13 секциям |
| **[doc-project/SPECIFICATIONS_CATALOG.md](../doc-project/SPECIFICATIONS_CATALOG.md)** | L2 | Каталог 108 спецификаций |
| **[doc-project/diagrams/README.md](../doc-project/diagrams/README.md)** | L3 | Каталог 36 диаграмм |

---

## 🎯 Итого

### ✅ Хорошо организовано:

- Корень - только главные индексы
- `/docs/` - основная платформенная документация
- `/doc-project/` - проектная документация с ТЗ
- Диаграммы собраны в одном месте
- Спецификации каталогизированы
- Множество индексов для навигации

### ⚠️ Требует внимания:

- Старые UI спецификации в `/docs/ui/` (HTML/JSON) → переместить в архив
- Создать единый UI Specifications Index

---

**Вывод**: Документация **НЕ разбросана**! Она **структурирована** на 3 уровня:
1. **Корень** (4 файла) - точки входа
2. **`/docs/`** (125+ файлов) - основная документация
3. **`/doc-project/`** (277 файлов) - проектная документация

Навигация обеспечена через **7 индексов** на разных уровнях.

**Последнее обновление**: 2025-10-09
