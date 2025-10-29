# Может Пригодиться - Полезный Код

Здесь хранится код который был убран из основной кодовой базы, но может пригодиться в будущем.

## llm_clients/

**Источник**: `orchestration/ai-orchestration/muscles/llm_clients/`

**Что**: Старый Anthropic client специально для governance анализа

**Файлы**:
- `anthropic_client.py` - AnthropicGovernanceBrain класс

**Почему сохранили**:
- Использует claude-3-sonnet-20240229 (старая модель)
- Специализированные governance prompts
- Может пригодиться для легаси интеграций
- НЕ ДУБЛИКАТ ai-foundation/llm/llm_router.py (это другое!)

**Когда использовать**:
- Если нужен специфичный governance-анализ
- Если нужна конкретная версия Claude модели
- Для миграции старого кода

**Также доступен в**: `workflow_intelligence/integration/legacy_anthropic_client.py`

---

**Дата**: 2025-10-06
**Команда**: Claude + MD
