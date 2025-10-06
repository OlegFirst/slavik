# 🗺️ Development Roadmap

**Модуль:** Unified Workflow Engine
**Версия:** 2.0.0
**Дата:** 2025-10-05

---

## 📊 Текущий статус

### ✅ Реализовано (Production-Ready)

- BPMN 2.0 парсинг и выполнение
- XOR/AND Gateway поддержка
- PostgreSQL персистентность
- REST API (10 endpoints)
- AI Recommendations (case-based)
- Case Learning (InMemory)
- Prometheus метрики
- Redis кеширование
- EventBus интеграция
- Multi-tenancy

### ⚠️ Проблемные места

#### 🔴 Критические проблемы

**1. OR Gateway не реализован**
- **Проблема:** Только XOR (выбор одного) и AND (все пути) работают
- **Влияние:** Невозможно моделировать процессы с "хотя бы один путь"
- **Workaround:** Использовать XOR + дополнительные условия
- **Приоритет:** P1
- **Оценка:** 2 дня

**2. Нет Workflow Templates**
- **Проблема:** Каждый раз нужно передавать полный BPMN XML
- **Влияние:** Неудобно для стандартных процессов (BIA, Risk, etc.)
- **Workaround:** Хранить BPMN XML в коде приложения
- **Приоритет:** P1
- **Оценка:** 3 дня

**3. LLM Client отключен**
- **Проблема:** `llm_client=None` в AI Advisor
- **Влияние:** AI рекомендации ограничены case-based поиском, нет NLP анализа
- **Workaround:** Работает case-based поиск похожих кейсов
- **Приоритет:** P1
- **Оценка:** 2 дня (интеграция) + стоимость API

**4. Case Library в памяти**
- **Проблема:** Используется InMemoryStorageAdapter
- **Влияние:** Кейсы теряются при перезапуске, нет долгосрочного обучения
- **Workaround:** Нет (критично для production)
- **Приоритет:** P0 (блокер для production)
- **Оценка:** 5 дней

#### 🟡 Умеренные проблемы

**5. ML Predictor не обучен**
- **Проблема:** `ml_predictor=None`, используется rule-based fallback
- **Влияние:** Предсказания неточные (просто прогресс ÷ время)
- **Workaround:** Rule-based оценка работает, но не AI-powered
- **Приоритет:** P2
- **Оценка:** 10 дней (сбор данных + обучение)

**6. Analytics базовый**
- **Проблема:** Нет process mining, bottleneck detection, performance analytics
- **Влияние:** Невозможно оптимизировать процессы
- **Workaround:** Ручной анализ через Prometheus метрики
- **Приоритет:** P2
- **Оценка:** 7 дней

**7. Тесты 30% coverage**
- **Проблема:** Большая часть кода не покрыта тестами
- **Влияние:** Высокий риск регрессий при изменениях
- **Workaround:** Тщательное ручное тестирование
- **Приоритет:** P2
- **Оценка:** 5 дней

#### 🟢 Минорные проблемы

**8. Frontend компонентов нет**
- **Проблема:** Нет React компонентов для bpmn-js визуализации
- **Влияние:** Frontend команде нужно самим интегрировать bpmn-js
- **Workaround:** API возвращает всё нужное для рендеринга
- **Приоритет:** P3
- **Оценка:** 5 дней

**9. Rate limiting базовый**
- **Проблема:** Простой RateLimiter может не выдержать высокую нагрузку
- **Влияние:** При >1000 RPS возможны проблемы
- **Workaround:** Работает для малых/средних нагрузок
- **Приоритет:** P3
- **Оценка:** 3 дня

**10. Документация неполная**
- **Проблема:** Многие edge cases не описаны
- **Влияние:** Разработчикам нужно читать код
- **Workaround:** Код достаточно читабельный
- **Приоритет:** P3
- **Оценка:** 3 дня

---

## 🎯 Приоритизация

### P0: Блокеры для Production

| # | Проблема | Оценка | Статус |
|---|----------|--------|--------|
| 4 | PostgreSQL Storage для Case Library | 5д | 🔴 TODO |

**Обоснование:** Без персистентности кейсов AI не может обучаться долгосрочно.

### P1: Критические улучшения

| # | Проблема | Оценка | Статус |
|---|----------|--------|--------|
| 1 | OR Gateway | 2д | 🔴 TODO |
| 2 | Workflow Templates | 3д | 🔴 TODO |
| 3 | LLM Client интеграция | 2д | 🔴 TODO |

**Обоснование:** Необходимо для полноценного использования BPMN + AI.

### P2: Важные улучшения

| # | Проблема | Оценка | Статус |
|---|----------|--------|--------|
| 5 | ML Predictor обучение | 10д | 🟡 TODO |
| 6 | Process Mining & Analytics | 7д | 🟡 TODO |
| 7 | Тесты до 80% coverage | 5д | 🟡 TODO |

**Обоснование:** Улучшает качество и надежность системы.

### P3: Желательные улучшения

| # | Проблема | Оценка | Статус |
|---|----------|--------|--------|
| 8 | React компоненты | 5д | 🟢 TODO |
| 9 | Advanced Rate Limiting | 3д | 🟢 TODO |
| 10 | Полная документация | 3д | 🟢 TODO |

**Обоснование:** Nice to have, но не блокирует работу.

---

## 🚀 Roadmap по фазам

### Phase 3: Production Hardening (4 недели)

**Цель:** Устранить P0/P1 проблемы

**Week 1:**
- [ ] PostgreSQL Storage Adapter для Case Library (5д)
  - Создать `PostgresStorageAdapter` с векторным поиском
  - Миграция: `039_case_library_storage.sql`
  - Интеграция с UnifiedEngine

**Week 2:**
- [ ] OR Gateway поддержка (2д)
  - Добавить `evaluate_inclusive_gateway()` в GatewayEvaluator
  - Тесты для OR logic
  - Обновить документацию
- [ ] Workflow Templates (3д)
  - Создать `templates/` директорию
  - BPMN шаблоны: `bia_standard.bpmn`, `risk_assessment.bpmn`
  - `start_process_from_template()` метод

**Week 3:**
- [ ] LLM Client интеграция (2д)
  - Добавить Claude API client
  - Интеграция с AI Advisor
  - Настройка API ключей
- [ ] Начать сбор кейсов для ML (ongoing)

**Week 4:**
- [ ] Integration testing
- [ ] Performance testing
- [ ] Documentation update

**Результат:** Production-ready система без критических ограничений

---

### Phase 4: Intelligence & Analytics (3 недели)

**Цель:** Полноценный AI + аналитика

**Week 1-2:**
- [ ] ML Predictor обучение (10д)
  - Собрать 100+ завершенных workflow
  - Обучить модели: duration, success_probability, risk_level
  - Random Forest / XGBoost
  - A/B тестирование vs rule-based

**Week 3:**
- [ ] Process Mining & Analytics (7д)
  - Bottleneck detection
  - Variant analysis (какие пути чаще используются)
  - Performance metrics по задачам
  - Dashboards для Grafana

**Результат:** AI-powered предсказания + глубокая аналитика процессов

---

### Phase 5: Quality & UX (2 недели)

**Цель:** Повысить качество и UX

**Week 1:**
- [ ] Тесты до 80% coverage (5д)
  - Unit tests для всех компонентов
  - Integration tests для API
  - E2E тесты для типовых сценариев
  - CI/CD интеграция

**Week 2:**
- [ ] React компоненты (5д)
  - `<BpmnViewer>` - отображение процесса
  - `<TaskList>` - список задач с AI советами
  - `<ProcessAnalytics>` - графики и метрики
  - Storybook stories

**Результат:** Высокое качество кода + готовые UI компоненты

---

### Phase 6: Scale & Polish (1 неделя)

**Цель:** Готовность к высоким нагрузкам

- [ ] Advanced Rate Limiting (3д)
  - Token bucket алгоритм
  - Distributed rate limiting через Redis
  - Per-tenant quotas
- [ ] Полная документация (3д)
  - Edge cases
  - Troubleshooting guide
  - Performance tuning guide

**Результат:** Enterprise-grade система

---

## 💡 Идеи для будущего развития

### Краткосрочные (3-6 месяцев)

**1. BPMN Events расширение**
- Message Events (связь между процессами)
- Timer Events (отложенные действия, дедлайны)
- Signal Events (broadcast события)
- **Ценность:** Более сложные процессы
- **Сложность:** Средняя (10д)

**2. Sub-Processes**
- Вложенные процессы
- Call Activities (переиспользуемые процессы)
- **Ценность:** DRY принцип для процессов
- **Сложность:** Средняя (7д)

**3. BPMN Versioning**
- Версионирование процессов
- Migration между версиями (старые инстансы → новая версия)
- **Ценность:** Безопасные обновления процессов
- **Сложность:** Высокая (14д)

**4. Visual Process Builder**
- No-code редактор BPMN в браузере
- Интеграция bpmn-js Modeler
- Сохранение и деплой из UI
- **Ценность:** Бизнес-пользователи могут менять процессы
- **Сложность:** Высокая (21д)

### Среднесрочные (6-12 месяцев)

**5. Process Simulation**
- "Что если" симуляции
- Monte Carlo для оценки длительности
- Оптимизация ресурсов
- **Ценность:** Планирование до запуска
- **Сложность:** Высокая (30д)

**6. Human-in-the-Loop AI**
- AI предлагает следующий шаг
- Человек подтверждает/корректирует
- AI учится из фидбека
- **Ценность:** Постепенная автоматизация
- **Сложность:** Средняя (14д)

**7. Multi-instance Tasks**
- Параллельная обработка списка элементов
- Например: "Approve each department" (5 департаментов параллельно)
- **Ценность:** Bulk operations
- **Сложность:** Средняя (10д)

**8. Collaboration (Multi-tenant workflows)**
- Процессы между организациями
- Shared workflow instances
- **Ценность:** B2B процессы
- **Сложность:** Очень высокая (60д)

### Долгосрочные (12+ месяцев)

**9. AI Auto-Optimization**
- AI автоматически предлагает изменения процесса
- "Task X is bottleneck → add parallel path?"
- A/B тестирование процессов
- **Ценность:** Self-improving процессы
- **Сложность:** Очень высокая (90д)

**10. Natural Language Process Definition**
- Описать процесс текстом → AI генерирует BPMN
- "When user submits BIA, assign to analyst. If approved, create report..."
- **Ценность:** Нетехнические пользователи создают процессы
- **Сложность:** Очень высокая (60д)

**11. Blockchain Audit Trail**
- Неизменяемый лог всех действий в процессе
- Криптографическое подтверждение
- **Ценность:** Regulatory compliance
- **Сложность:** Высокая (45д)

---

## 🔬 Исследовательские направления

### 1. Federated Learning для Case Library
- **Проблема:** Компании не хотят делиться данными
- **Решение:** Обучение моделей локально, обмен только весами
- **Ценность:** Коллективное обучение без утечки данных
- **Риски:** Технически сложно, нужна инфраструктура

### 2. Process Mining Integration
- **Проблема:** Нужно анализировать реальные процессы (не только BPMN)
- **Решение:** Интеграция с PM4Py, Celonis
- **Ценность:** Discover процессы из логов
- **Риски:** Дублирование функциональности

### 3. Graph Neural Networks для Process Prediction
- **Проблема:** Процессы - это графы, обычный ML не учитывает структуру
- **Решение:** GNN для предсказаний на основе топологии процесса
- **Ценность:** Более точные предсказания
- **Риски:** Требует большого количества данных

---

## 📈 Метрики успеха

### Technical Metrics

- **Test Coverage:** 30% → 80%
- **API Response Time (p95):** <200ms
- **Database Query Time (p95):** <50ms
- **Cache Hit Rate:** >70%
- **Uptime:** 99.9%

### Business Metrics

- **Time to Complete Workflow:** -30% (с AI рекомендациями)
- **Decision Quality Score:** +25% (правильность выбора)
- **User Satisfaction:** >4.5/5
- **AI Recommendation Acceptance Rate:** >60%
- **Case Library Growth:** +50 cases/месяц

### AI Metrics

- **Recommendation Relevance:** >0.8 (user feedback)
- **ML Prediction Accuracy:** >85% (duration), >90% (success)
- **Case Search Precision:** >0.7
- **LLM Response Quality:** >4/5 (human evaluation)

---

## 🛠️ Технический долг

### Код

1. **Дублирование логики** - `_process_next_elements()` ~200 строк, нужен рефакторинг
2. **Слабая типизация** - много `Dict[str, Any]`, нужно больше Pydantic моделей
3. **Circular imports** - некоторые модули взаимозависимы
4. **Error handling** - много `try/except` без специфичных исключений

### Инфраструктура

5. **Connection pooling** - нет настройки пула соединений для PostgreSQL
6. **Caching strategy** - простой TTL, нужна invalidation по событиям
7. **Observability** - нет distributed tracing (OpenTelemetry)
8. **Security** - нет audit trail для изменений процессов

### Документация

9. **API docs** - нет OpenAPI/Swagger UI
10. **Architecture Decision Records** - нужно документировать ключевые решения

---

## 🎬 Следующие шаги

### Немедленно (эта неделя)

1. ✅ Консолидировать документацию (DONE)
2. 🔴 Создать PostgresStorageAdapter для Case Library (P0)
3. 🔴 Добавить OR Gateway поддержку (P1)

### Ближайший месяц

4. Создать Workflow Templates (BIA, Risk, Compliance)
5. Интегрировать LLM Client (Claude API)
6. Начать сбор кейсов для ML обучения
7. Написать integration tests

### Квартал (3 месяца)

8. Обучить ML Predictor
9. Добавить Process Mining & Analytics
10. React компоненты для фронтенда
11. Довести test coverage до 80%

---

## 📞 Контакты

**Вопросы по roadmap:**
- Tech Lead: MD
- AI Integration: Claude
- Platform Architecture: См. COMPLETE_PLATFORM_ARCHITECTURE.md

**Документы:**
- [README.md](README.md) - Основная документация
- [WORKFLOW_INTELLIGENCE_INTEGRATED.md](WORKFLOW_INTELLIGENCE_INTEGRATED.md) - AI интеграция
- [REST_API_IMPLEMENTED.md](REST_API_IMPLEMENTED.md) - API спецификация
- [GATEWAY_SUPPORT_IMPLEMENTED.md](GATEWAY_SUPPORT_IMPLEMENTED.md) - Gateway документация

---

**Последнее обновление:** 2025-10-05
**Версия roadmap:** 1.0
