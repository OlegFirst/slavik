# Assistant Activity Event — Payload Schema

## Event Type
`assistant.activity`

## Purpose
Фиксировать действия ассистента: что рекомендовал, почему, что вызвал, чего ждёт, чем завершилось.

## JSON Schema (пример)
```json
{
  "event_type": "assistant.activity",
  "tenant_id": "string",
  "data": {
    "intent": "check_status | plan_generate_draft | incident_draft_response | audit_summarize | documents_analyze | schedule_exercise | show_next_step",
    "reason": "string (какие KPI/события привели к решению)",
    "context": {
      "kpi": {
        "bia_coverage": 0.78,
        "plans_up_to_date": 0.69,
        "capa_on_time": 0.86
      },
      "recent_events": [
        {"event_type":"bcm.plan.versioned","ts":"..."},
        {"event_type":"bcm.incident.opened","ts":"..."}
      ]
    },
    "actions": [
      {"type":"plan","process_id":"EHR","params":{"priority":"high"}},
      {"type":"exercise","process_id":"Pharmacy","params":{"level":"tabletop","duration_min":45}}
    ],
    "status": "requested | approved | rejected | completed | failed",
    "error": null,
    "correlation_id": "string",
    "sources": ["kpi","history","user_prompt"]
  },
  "user_id": "optional",
  "metadata": {"ui":"web_portal","version":"x.y.z"},
  "event_id": "optional (idempotency)",
  "created_at": "iso-datetime"
}
```

## Required Fields
- `tenant_id`
- `data.intent`
- `data.reason`
- `data.actions` (минимум 1)  
- `data.status`

## Status Transitions
- `requested` → опубликовано ассистентом при старте действия
- `approved/rejected` → пользователь утвердил/отклонил (по кнопке)
- `completed` → подтверждающее событие получено (например, `bcm.plan.draft_generated`)
- `failed` → ошибка API/валидации (с заполнением `data.error`)

## Correlation
- `correlation_id` обязателен для связывания assistant.activity с подтверждающими событиями (plan/incident/audit).

## Security
- Публиковать только в каналы `bcm.{tenant_id}` + `bcm.event.assistant.activity`
- Не включать чувствительные данные (PII/PHI) в payload. Использовать идентификаторы вместо содержимого документов.
