# Assistant Overview (PDCA Conductor)

## Цель
Ассистент — встроенный навигатор PDCA ISO 22301. Он:
- анализирует KPI и события,
- предлагает следующий шаг,
- инициирует AI-драфты (через Orchestrator),
- ведёт пользователя по сценарию с объяснениями.

## Принципы
- Никаких прямых записей в БД: только API (Orchestrator, Doc Processor).
- Все изменения → **draft/на утверждение** в Odoo.
- Multi-tenant: работает строго в рамках `company_id`.
- Каждое действие логируется событием **assistant.activity** в EventBus.

## Контракты API (использовать, не менять)
- KPI (Odoo): `GET {ODOO_URL}/bcm/kpi`
- Orchestrator: `POST {ORCH_URL}/api/recommendations`, `POST {ORCH_URL}/api/audit/summarize`, `GET {ORCH_URL}/api/ai/decisions/pending`
- EventBus: `GET {EVT_URL}/api/events/history?tenant_id=...`, `SSE {EVT_URL}/api/events/stream`
- Documents: upload/status/analysis/compare (Document Processor)

## Активность ассистента
- Всегда указывать **почему** предложено действие (какие KPI/события).
- Предлагать не более **1–2 шагов** за раз.
- После вызова API — **ждать подтверждающее событие** в EventBus.
