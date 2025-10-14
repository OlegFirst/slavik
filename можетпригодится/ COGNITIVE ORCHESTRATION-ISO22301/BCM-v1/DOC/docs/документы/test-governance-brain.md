# Test AI Governance Brain - Console Command

## 🧠 **ПРОМТ ДЛЯ КОНСОЛИ:**

Используй этот промт в Claude Code консоли для тестирования нашего AI Governance Brain:

```
Ты - AI Governance Brain для BCM Platform. Сейчас мы тестируем твою интеграцию через консоль.

ЗАДАЧА: Протестировать Anthropic integration для bcm_governance модуля

КОНТЕКСТ:
- У нас есть bcm_governance модуль с AI integration
- Anthropic API key настроен в .env файле
- AI Orchestrator должен роутить governance запросы в Anthropic
- Нужно протестировать полную цепочку через console commands

ТЕСТИРОВАНИЕ:

1. ПРОВЕРЬ ANTHROPIC API KEY:
   - Прочитай .env файл
   - Убедись что ANTHROPIC_API_KEY настроен
   - Проверь что AI Orchestrator видит ключ

2. ПРОТЕСТИРУЙ AI ORCHESTRATOR ANTHROPIC ROUTING:
   Выполни POST запрос:
   ```bash
   curl -X POST http://localhost:8000/nlp/query \
     -H "Content-Type: application/json" \
     -d '{
       "query": "Analyze ISO 22301 compliance strategy for healthcare organization",
       "context": {
         "module": "bcm_governance",
         "domain": "iso_22301",
         "priority": "high",
         "company": "Test Healthcare Corp",
         "use_anthropic": true
       },
       "user_role": "governance_brain"
     }'
   ```

3. ПРОВЕРЬ РЕЗУЛЬТАТ:
   - Response должен содержать sophisticated analysis
   - model_used должен показывать "anthropic_claude_sonnet"
   - confidence должен быть 0.95
   - content должен быть executive-level quality

4. ПРОТЕСТИРУЙ EMERGENCY MODE:
   ```bash
   curl -X POST http://localhost:8000/nlp/query \
     -H "Content-Type: application/json" \
     -d '{
       "query": "EMERGENCY: Major data breach detected, need immediate governance response",
       "context": {
         "module": "bcm_governance",
         "priority": "emergency",
         "use_anthropic": true
       },
       "user_role": "governance_brain"
     }'
   ```

5. ЕСЛИ ANTHROPIC НЕ РАБОТАЕТ:
   - Проверь API key format
   - Проверь network connectivity
   - Fallback должен сработать на local AI

ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:
- Sophisticated strategic analysis от Anthropic
- Executive-quality governance recommendations
- Emergency response protocols
- Board-ready strategic insights

КРИТЕРИИ УСПЕХА:
✅ AI Orchestrator routes governance requests to Anthropic
✅ Anthropic returns high-quality strategic analysis
✅ Emergency mode works for crisis governance
✅ Fallback works if Anthropic unavailable
✅ Integration stable и production-ready

Проведи полное тестирование и доложи о результатах!
```

## 🔧 **Альтернативный промт если нужна помощь с debugging:**

```
Помоги мне отладить AI Governance Brain integration с Anthropic API.

ПРОБЛЕМА:
Нужно протестировать что bcm_governance модуль корректно использует Anthropic для strategic analysis.

ЧТО СДЕЛАНО:
- Anthropic API key добавлен в .env
- bcm_governance модуль enhanced с AI integration
- AI Orchestrator должен роутить governance запросы

ЧТО ПРОТЕСТИРОВАТЬ:
1. API key configuration
2. AI Orchestrator Anthropic routing
3. Governance brain functionality
4. Emergency mode testing
5. Fallback mechanisms

Используй все доступные tools (Bash, Read, Edit, etc.) для:
- Проверки configuration
- Тестирования API endpoints
- Debugging integration issues
- Validating response quality

Цель: Убедиться что Governance Brain работает как sophisticated AI advisor для strategic BCM decisions.
```

## 🎯 **КАКОЙ ПРОМТ ПРЕДПОЧИТАЕШЬ?**

1. **Первый** - для independent testing
2. **Второй** - для debugging assistance

**Или хочешь чтобы я сам протестировал через console прямо сейчас?** 🧠⚡