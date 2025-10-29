# 🧱 АНАЛИЗ LEGO КОМПОНЕНТОВ

## Что собралось:

### Orchestrators (2):
- `cognitive-orchestrator` - из platform-framework
- `ai-consultant` - из ai-core

### Event-bus (2):
- backend версия
- platform версия

### AI Services (7):
- Много AI компонентов

### Monitoring (2):
- BCM monitoring
- Platform monitoring

### Workflow (2):
- Backend BPMN
- Platform BPMN

---

## 🎯 КОНЦЕПТУАЛЬНОЕ РАЗДЕЛЕНИЕ:

### 1️⃣ **СИСТЕМНЫЕ КОМПОНЕНТЫ** (инфраструктура платформы):
```
Это универсальные компоненты, которые работают для любой системы:

- event-bus/             → Система событий
- orchestrators/         → Координация
- workflow/              → Процессы
- auth/                  → Аутентификация
- gateways/              → API входы
- monitoring/            → Мониторинг
- notifications/         → Уведомления
- tools/                 → Инструменты
- ai-services/           → AI сервисы
```

### 2️⃣ **ПРОГРАММНЫЕ КОМПОНЕНТЫ BCM** (специфика BCM):
```
Это все что связано с BCM и ISO 22301:

- bcm-modules/           → BCM модули (пока пустые)
- document-processors/   → Обработка BCM документов
- simulators/            → Симуляторы учений
- bridges/               → Мосты к BCM системам
- integrations/          → Интеграции с BCM инструментами
```

### 3️⃣ **ДУБЛИКАТЫ ДЛЯ ОБЪЕДИНЕНИЯ**:
```
orchestrators/:
  - cognitive-orchestrator (новый)
  - ai-consultant (старый)
  → ОБЪЕДИНИТЬ в один

event-bus/:
  - backend версия
  - platform версия
  → ОБЪЕДИНИТЬ в один

workflow/:
  - backend BPMN
  - platform BPMN
  → ОБЪЕДИНИТЬ в один

monitoring/:
  - BCM monitoring
  - Platform monitoring
  → ОБЪЕДИНИТЬ в один
```

---

## 📊 СЛЕДУЮЩИЕ ШАГИ:

1. **Создать папки по категориям:**
   - `SYSTEM_COMPONENTS/` - системные универсальные
   - `BCM_COMPONENTS/` - BCM специфичные

2. **Объединить дубликаты:**
   - Взять лучшее из каждой версии
   - Создать единую конфигурацию

3. **Построить иерархию:**
   ```
   ORGANISM/
   ├── 1_CORE_SYSTEM/        (системные компоненты)
   │   ├── brain/            (orchestrators)
   │   ├── nervous/          (event-bus)
   │   ├── circulation/      (workflow)
   │   └── senses/           (monitoring)
   │
   └── 2_BCM_ORGANS/         (BCM компоненты)
       ├── risk-management/
       ├── incident-response/
       ├── business-continuity/
       └── compliance/
   ```

---

## 🔍 ЧТО НЕ ХВАТАЕТ:

Многие папки пустые, значит компоненты не нашлись:
- bcm-modules (0) - не нашли BCM модули
- integrations (0) - не нашли интеграции
- adapters (0) - не нашли адаптеры
- bridges (0) - не нашли мосты
- digital-twin (0) - не нашли цифровых двойников
- simulators (0) - не нашли симуляторы

Нужно поискать их в других местах!