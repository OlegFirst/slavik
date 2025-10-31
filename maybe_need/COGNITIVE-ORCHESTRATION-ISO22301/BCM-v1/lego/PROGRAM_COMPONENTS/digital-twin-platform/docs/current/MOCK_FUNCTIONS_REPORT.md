# Mock Functions Report

Дата: 2025-08-16T06:49:03.574Z

## Найдено 10 модулей с mock функциями

### src/demo-mode.js
- ⚠️ **КРИТИЧЕСКОЕ**: Содержит mock/demo функции в production коде
- **Рекомендация**: Вынести в отдельные test-only модули

### src/mcp-integration.js
- ⚠️ **КРИТИЧЕСКОЕ**: Содержит mock/demo функции в production коде
- **Рекомендация**: Вынести в отдельные test-only модули

### src/organization-data-collector.js
- ⚠️ **КРИТИЧЕСКОЕ**: Содержит mock/demo функции в production коде
- **Рекомендация**: Вынести в отдельные test-only модули

### src/simulation-router.js
- ⚠️ **КРИТИЧЕСКОЕ**: Содержит mock/demo функции в production коде
- **Рекомендация**: Вынести в отдельные test-only модули

### core/ai/ai-orchestrator.js
- ⚠️ **КРИТИЧЕСКОЕ**: Содержит mock/demo функции в production коде
- **Рекомендация**: Вынести в отдельные test-only модули

### core/context-manager.js
- ⚠️ **КРИТИЧЕСКОЕ**: Содержит mock/demo функции в production коде
- **Рекомендация**: Вынести в отдельные test-only модули

### core/organization-context.js
- ⚠️ **КРИТИЧЕСКОЕ**: Содержит mock/demo функции в production коде
- **Рекомендация**: Вынести в отдельные test-only модули

### core/security/security-manager.js
- ⚠️ **КРИТИЧЕСКОЕ**: Содержит mock/demo функции в production коде
- **Рекомендация**: Вынести в отдельные test-only модули

### core/security/security-orchestrator.js
- ⚠️ **КРИТИЧЕСКОЕ**: Содержит mock/demo функции в production коде
- **Рекомендация**: Вынести в отдельные test-only модули

### core/tenant-manager.js
- ⚠️ **КРИТИЧЕСКОЕ**: Содержит mock/demo функции в production коде
- **Рекомендация**: Вынести в отдельные test-only модули

## Рекомендации

1. Создать отдельную папку `src/mocks/` для mock функций
2. Использовать environment variables для переключения между production и mock режимами
3. Добавить lint правила для предотвращения mock функций в production
