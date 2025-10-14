# Business Scenarios Documentation Strategy

**Дата**: 2025-10-11
**Статус**: ✅ Finalized

---

## 🎯 Правильный Подход

### ❌ НЕПРАВИЛЬНО (старый подход):
```
ALL_USAGE_SCENARIOS_CATALOG.md (570+ scenarios)
    ↓
Переписываем в *_DETAILED.md
    ↓
Дублирование, потеря времени
```

### ✅ ПРАВИЛЬНО (новый подход):
```
ALL_USAGE_SCENARIOS_CATALOG.md (570+ scenarios)
    ↓
Загружаем в RAG (Qdrant collection: business_scenarios)
    ↓
AI Assistant может искать и использовать ВСЕ сценарии
    ↓
Детальные примеры (*_DETAILED.md) только для топ-20 самых частых
```

---

## 📊 Текущая Ситуация

### Что у нас есть:

```
/platform-services/docs/business-scenarios/

├── ALL_USAGE_SCENARIOS_CATALOG.md        # ⭐ ОСНОВА (67KB, 570+ scenarios)
│   ├── Краткий формат (Входы/Выходы/События/Компоненты)
│   ├── Все 15 сервисов покрыты
│   └── Готово к загрузке в RAG ✅
│
├── *_DETAILED.md (7 files)                # 📚 ДЕТАЛЬНЫЕ ПРИМЕРЫ
│   ├── BIA_SERVICE_SCENARIOS_DETAILED.md (119KB, 25 scenarios)
│   ├── RISK_SERVICE_SCENARIOS_DETAILED.md (99KB, 22 scenarios)
│   ├── COMPLIANCE_SERVICE_SCENARIOS_DETAILED.md (173KB, 20 scenarios)
│   ├── EXERCISE_SERVICE_SCENARIOS_DETAILED.md (172KB, 16 scenarios)
│   ├── DOCUMENTS_SERVICE_SCENARIOS_DETAILED.md (174KB, 15 scenarios)
│   ├── PLANNING_SERVICE_SCENARIOS_DETAILED.md (96KB, 7/28) ← агент работает
│   └── RESPONSE_SERVICE_SCENARIOS_DETAILED.md (81KB, 9/18) ← агент работает
│
└── ИТОГО: 98/144 детальных (68% complete)
```

---

## 🚀 План Действий

### Phase 1: ✅ Загрузить каталог в RAG (СЕЙЧАС)

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/rag

# 1. Setup Qdrant collection
python setup_collections.py

# 2. Load catalog to RAG
python load_scenarios_to_rag.py

# Результат: 570+ scenarios searchable в Qdrant
```

**Что получим**:
- AI Assistant знает ВСЕ 570+ сценариев
- Можно искать: "How to conduct BIA?" → находит 1.1, 1.3, 1.4
- Можно фильтровать: service="BIA", category="Core"
- Instant knowledge base без переписывания

---

### Phase 2: ✅ Доделать детальные примеры (агенты работают)

**Критерий**: Детальные примеры нужны только для **топ-20 самых частых** сценариев

```
Приоритет 1 (MUST HAVE - уже есть):
✅ BIA: Start BIA, AI RTO suggestion, Generate report
✅ Risk: Risk assessment, Treatment planning
✅ Compliance: Gap analysis, Evidence collection
✅ Exercise: Create exercise, AI scenario generation
✅ Documents: Living documents, Semantic search

Приоритет 2 (агенты делают):
🔄 Planning: ISO Journey (7/28 done)
🔄 Response: Incident response (9/18 done)

Приоритет 3 (НЕ НУЖНО пока):
❌ Governance, Learning, Validation, etc.
   → Их сценарии уже в CATALOG → в RAG → достаточно
```

---

### Phase 3: 🔮 Самообучающаяся система (будущее)

```python
# Автоматическая генерация новых сценариев из реального опыта

Event Bus → Pattern Detection → Domain Analysis → Scenario Generator
    ↓
New scenarios auto-generated
    ↓
Auto-loaded to RAG
    ↓
AI knows even MORE scenarios (without manual work)
```

---

## 🎯 Зачем Детальные Примеры?

### Когда нужны *_DETAILED.md:

1. **Onboarding новых разработчиков**
   - Полные JSON примеры
   - Step-by-step процессы
   - Копируй-вставляй код

2. **API Documentation**
   - Swagger/OpenAPI недостаточно
   - Нужны реальные business flows
   - Error handling examples

3. **Customer demos**
   - Показать возможности
   - Бизнес-ценность ($50K-$500K)
   - Real-world use cases

### Когда НЕ нужны:

1. **Редкие сценарии** (< 5% usage)
   - Краткого описания в CATALOG достаточно
   - RAG найдёт при необходимости

2. **Вариации базовых** (те же endpoints, разные параметры)
   - 1 детальный пример + вариации в CATALOG

3. **Будущие features** (ещё не реализованы)
   - Зачем документировать то чего нет?

---

## 📈 Метрики Успеха

### До (старый подход):
```
- 570 scenarios в CATALOG
- 98 detailed (68%)
- AI НЕ ЗНАЕТ о 472 сценариях (не в RAG)
- Search: manual grep по markdown
```

### После (новый подход):
```
- 570 scenarios в CATALOG → в RAG ✅
- 20-30 detailed (топ сценарии)
- AI ЗНАЕТ ВСЕ 570 сценариев
- Search: semantic search (Qdrant)
```

**ROI**:
- Экономия времени: ~80% (не переписываем 472 сценария)
- AI capabilities: +500% (знает в 5 раз больше)
- Search quality: semantic vs grep

---

## 🔧 Техническая Реализация

### 1. RAG Collection Structure

```python
Collection: "business_scenarios"
Vector size: 384 (all-MiniLM-L6-v2)
Distance: COSINE

Point = {
    "id": 123,
    "vector": [0.1, 0.2, ...],  # 384-dim embedding
    "payload": {
        "title": "1.1 Start New BIA",
        "service": "BIA Service",
        "category": "Core",
        "inputs": "org_id, scope, method",
        "outputs": "bia_id, workflow_created",
        "events": "bia.workflow.started",
        "components": "BIA Service → Orchestrator → Task Queue",
        "full_text": "..."  # for display
    }
}
```

### 2. Search API

```python
from load_scenarios_to_rag import ScenarioLoader

loader = ScenarioLoader()

# Semantic search
results = loader.search_scenarios(
    query="How to conduct BIA with AI assistance?",
    top_k=5
)

# Filtered search
results = loader.search_scenarios(
    query="risk assessment",
    filters={"service": "Risk Service", "category": "Core"}
)
```

### 3. Integration with AI Assistant

```python
# In AI Assistant / LLM Router
async def answer_question(question: str):
    # 1. Search scenarios
    scenarios = rag_pipeline.search(
        query=question,
        collection="business_scenarios",
        top_k=3
    )

    # 2. Use as context for LLM
    context = "\n".join([s['full_text'] for s in scenarios])

    prompt = f"""
    User question: {question}

    Relevant scenarios from our platform:
    {context}

    Answer the question using these scenarios.
    """

    answer = await llm.generate(prompt)
    return answer
```

---

## ✅ Следующие Шаги

### Immediate (Сейчас):

1. ✅ Создать `load_scenarios_to_rag.py` ← DONE
2. ✅ Обновить `setup_collections.py` ← DONE
3. ⏭️ Запустить загрузку:
   ```bash
   python load_scenarios_to_rag.py
   ```
4. ⏭️ Проверить поиск:
   ```python
   loader.search_scenarios("How to do BIA?")
   ```

### Short-term (Эта неделя):

1. Доделать Planning scenarios (агент работает)
2. Доделать Response scenarios (агент работает)
3. Интегрировать RAG search в AI Assistant
4. Тестировать semantic search

### Long-term (Следующий месяц):

1. Self-Learning Scenario System
2. Auto-generation from real usage
3. Evolution tracking
4. Community Intelligence sharing

---

## 🎓 Lessons Learned

### Ошибка:
"Давайте перепишем все 570 сценариев в детальном формате с JSON примерами!"

### Правильно:
1. **Основа** (CATALOG) → в RAG → AI знает всё
2. **Детали** (DETAILED) → только топ-20 → для людей
3. **Будущее** (Self-Learning) → автогенерация → без работы

### Принцип:
**"Don't Repeat Yourself"** применим к документации тоже!

---

**Статус**: ✅ Стратегия утверждена
**Next**: Загрузить CATALOG в RAG
**ETA**: 30 минут (парсинг + embedding + upload)
