# Workflow Intelligence - Integration Layer

Интеграции workflow_intelligence с другими компонентами платформы.

## Текущие интеграции:

### ai_context_builder.py
Построение AI контекста для workflow анализа

### bia_adapter.py
Адаптер для BIA service интеграции

### eventbus_publisher.py
Публикация workflow events в EventBus

### legacy_anthropic_client.py ✅ NEW
**Источник**: `orchestration/ai-orchestration/muscles/llm_clients/`

Старый Anthropic client для governance анализа.

**Использование**:
- Легаси governance интеграции
- Специфичные governance prompts
- Фоллбэк для старых workflow

**Замечание**: Для новых интеграций используй `ai-foundation/llm/llm_router.py`!

---

**Обновлено**: 2025-10-06
