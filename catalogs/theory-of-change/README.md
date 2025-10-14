# Theory of Change - Modeling and Simulation

## Overview

**Theory of Change (ToC)** - это методология планирования и оценки, которая описывает:
- **Как** изменения происходят
- **Почему** определенные действия ведут к желаемым результатам
- **Какие** условия необходимы для успеха

В контексте **Simulation & Modeling Service**, Theory of Change помогает:
1. Понять логику изменений в организации
2. Моделировать причинно-следственные связи
3. Предсказывать результаты вмешательств
4. Планировать изменения с учетом рисков

---

## Структура Theory of Change

### 1. Inputs (Входы)
Ресурсы, вложения, которые мы имеем:
- Человеческие ресурсы
- Финансы
- Технологии
- Знания и экспертиза
- Данные

### 2. Activities (Действия)
Что мы делаем с ресурсами:
- Процессы
- Вмешательства
- Инициативы
- Тренинги
- Внедрения

### 3. Outputs (Выходы)
Прямые результаты действий:
- Обученные сотрудники
- Внедренные системы
- Созданные документы
- Проведенные симуляции

### 4. Outcomes (Результаты)
Изменения в поведении/состоянии:
- Улучшенная готовность
- Повышенная устойчивость
- Изменение культуры
- Снижение рисков

### 5. Impact (Воздействие)
Долгосрочные последствия:
- Организационная устойчивость
- Конкурентное преимущество
- Соответствие стандартам
- Защита бизнеса

---

## Применение в Simulation Service

### Моделирование изменений

```
INPUTS → ACTIVITIES → OUTPUTS → OUTCOMES → IMPACT

Пример 1: Cyber Security Training
Inputs:
- 10 сотрудников IT
- $50,000 бюджет
- 3 месяца времени

Activities:
- Cyber security training
- Ransomware simulation
- Incident response drills

Outputs:
- 10 обученных специалистов
- Протестированный план реагирования
- Идентифицированные пробелы

Outcomes:
- Время реагирования сокращено на 50%
- 90% инцидентов обрабатываются правильно
- Уверенность команды повысилась

Impact:
- Снижение риска кибератак на 40%
- Минимизация простоев
- Соответствие ISO 27001
```

### Assumptions (Предположения)

**Критически важно** моделировать предположения:
- "Обученные сотрудники будут применять знания"
- "Процессы будут соблюдаться"
- "Технология будет работать как ожидается"
- "Внешние факторы останутся стабильными"

### Risks (Риски)

Что может помешать Theory of Change:
- Текучка кадров (потеря обученных людей)
- Бюджетные ограничения
- Изменение приоритетов
- Технологические проблемы
- Сопротивление изменениям

---

## Типы моделей изменений

### 1. Linear Model (Линейная модель)
```
A → B → C → D → E
```
Прямая причинно-следственная цепочка.
**Применение**: Простые вмешательства с предсказуемыми результатами.

### 2. Complex Adaptive Systems (Сложные адаптивные системы)
```
   ↗ B → D ↘
A →   C   → F
   ↘ E ↗
```
Множественные взаимодействия и обратные связи.
**Применение**: Организационные изменения, культурные трансформации.

### 3. Iterative Model (Итеративная модель)
```
A → B → C
 ↑     ↓
 ← D ←
```
Циклические процессы с обучением.
**Применение**: PDCA циклы, continuous improvement.

### 4. Multi-Pathway Model (Множественные пути)
```
A1 → B1 → C
A2 → B2 → C
A3 → B3 → C
```
Различные пути к одному результату.
**Применение**: Комплексные стратегии с альтернативами.

---

## Индикаторы и Метрики

### SMART Indicators
- **Specific**: Конкретные
- **Measurable**: Измеримые
- **Achievable**: Достижимые
- **Relevant**: Релевантные
- **Time-bound**: Ограниченные по времени

### Типы индикаторов:

**1. Input Indicators**
- Количество ресурсов выделено
- Бюджет потрачен
- Время инвестировано

**2. Process Indicators**
- Количество проведенных тренингов
- Число участников
- Завершенные этапы

**3. Output Indicators**
- Документы созданы
- Системы внедрены
- Люди обучены

**4. Outcome Indicators**
- Изменение в поведении (%)
- Улучшение метрик производительности
- Снижение инцидентов

**5. Impact Indicators**
- Долгосрочная устойчивость
- ROI
- Соответствие стандартам

---

## Использование в симуляциях

### Пример: BIA Process Improvement

**Theory of Change:**

```yaml
goal: "Improve BIA process effectiveness by 50% within 6 months"

inputs:
  - resources:
      - 5 BIA specialists
      - BIA software tool
      - Historical data
  - budget: $100,000
  - time: 6 months

activities:
  - Training on new BIA methodology
  - Pilot BIA with 3 departments
  - Simulation of disruption scenarios
  - Process refinement based on findings
  - Full rollout

outputs:
  - 3 completed pilot BIAs
  - Refined BIA process documentation
  - 15 trained staff
  - 10 simulation scenarios tested

outcomes:
  - Short-term (1-3 months):
      - BIA completion time reduced 30%
      - Data quality improved
      - Staff confidence increased

  - Medium-term (3-6 months):
      - All critical processes analyzed
      - RTO/RPO targets defined
      - Recovery strategies documented

  - Long-term (6+ months):
      - BCM plans updated
      - Organization resilience improved
      - Compliance achieved

impact:
  - Organizational resilience increased
  - Business continuity ensured
  - ISO 22301 compliance
  - Reduced business disruption risk

assumptions:
  - Management support continues
  - Staff remain engaged
  - Budget remains available
  - No major organizational changes

risks:
  - Staff turnover
  - Competing priorities
  - Budget cuts
  - Resistance to change

mitigation:
  - Regular stakeholder engagement
  - Quick wins to maintain momentum
  - Flexible timeline
  - Change management program

indicators:
  - BIA completion time (hours)
  - Data accuracy (%)
  - Staff satisfaction (1-10)
  - Process maturity level (1-5)
  - Critical process coverage (%)
```

---

## Моделирование в Simulation Service

### Как использовать ToC в симуляциях:

**1. Pre-Simulation: Planning**
- Определить Theory of Change для инициативы
- Выявить предположения и риски
- Установить индикаторы успеха

**2. During Simulation: Testing**
- Тестировать предположения
- Проверять причинно-следственные связи
- Идентифицировать точки отказа

**3. Post-Simulation: Learning**
- Анализировать какие пути сработали
- Корректировать Theory of Change
- Обновлять предположения

**4. Knowledge Storage**
- Сохранять подтвержденные ToC модели
- Делиться знаниями с сообществом
- Использовать для будущих симуляций

---

## Инструменты моделирования

### 1. Logic Models
Визуальное представление ToC:
```
[Inputs] → [Activities] → [Outputs] → [Outcomes] → [Impact]
```

### 2. Causal Loop Diagrams
Показывают обратные связи:
```
Training → Skills ↑
    ↑         ↓
    ← Performance ↑
```

### 3. Systems Dynamics
Количественное моделирование потоков и запасов.

### 4. Agent-Based Models
Моделирование поведения отдельных агентов.

---

## Интеграция с платформой

### Автоматическое извлечение ToC

Simulation Service может автоматически извлекать Theory of Change из:
- Спецификаций симуляций
- Результатов выполнения
- Исторических данных
- Документов организации

### Визуализация

- Диаграммы ToC
- Интерактивные модели
- Прогрессия изменений
- Дерево решений

### Предсказания

Используя ML и AI:
- Предсказать вероятность успеха
- Идентифицировать критические предположения
- Рекомендовать митигации
- Оптимизировать путь к цели

---

## Примеры ToC шаблонов

См. файлы в этой директории:
- `toc-cyber-resilience.yaml` - Кибербезопасность
- `toc-bcm-implementation.yaml` - Внедрение BCM
- `toc-pandemic-response.yaml` - Ответ на пандемию
- `toc-digital-transformation.yaml` - Цифровая трансформация

---

## Ссылки и ресурсы

### Методологии:
- Theory of Change (TOC)
- Logical Framework Approach (LFA)
- Results-Based Management (RBM)
- Systems Thinking
- Causal Inference

### Стандарты:
- ISO 22301 (BCM)
- ISO 31000 (Risk Management)
- ISO 9001 (Quality Management)

### Инструменты:
- ToC Builder
- Kumu (systems mapping)
- Vensim (system dynamics)
- NetLogo (agent-based)

---

## Заключение

Theory of Change - это **не просто план**, это:
- Гипотеза о том, как работают изменения
- Инструмент для тестирования предположений
- Основа для обучения и адаптации
- Способ коммуникации стратегии

В **Simulation Service**, ToC позволяет:
✅ Моделировать комплексные изменения
✅ Тестировать стратегии безопасно
✅ Обучаться на симуляциях
✅ Оптимизировать инвестиции в изменения
