# SEH — MCP Server Interface (v1)
**Дата:** 2025-08-16  
**Цель:** Сделать MCP‑сервер «интерфейсом» между нашим диалогом и твоей платформой (Supabase + симуляции + Salesforce).  
**Результат:** ты из чата говоришь «запусти сценарий», я дергаю MCP‑tool → сообщение уходит в Supabase/Edge → заводится job → бэкенд гоняет симуляции → отчёт ложится в твой профиль → ты видишь в веб‑UI/дашборде и кидаешь мне ссылку/ид отчёта.

## Архитектура (упрощённо)
- **MCP Server (Node/TS):** регистрирует набор tools:
  - `create_scenario_job` — создать задачу симуляции/оптимизации.
  - `attach_context` — прикрепить данные/ToC/CSV к задаче.
  - `run_job` — пнуть запуск (или ждать воркер).
  - `get_job` — статус задачи.
  - `get_report` — получить результат (JSON/Signed URL).
- **Supabase (DB + Edge Functions):** хранит `profiles`, `threads`, `jobs`, `reports`, `artifacts`.
- **Worker (Node/TS либо Supabase Function):** слушает `jobs` → вызывает `/api/v1/sim/run` и `/api/v1/impact/optimize` → пишет `reports`.
- **Web‑UI:** стр. профиля и стр. задач/отчётов.
- **Auth:** Bearer JWT в MCP→Edge; RLS в Supabase; Permission Sets по ролям.

## Потоки
1. **Intake:** из чата вызываем `create_scenario_job` с типом (`capacity_sweep|routing_vrp|disbursement|bcm_outage|toc_optimize`) и входами.
2. **Enrich:** `attach_context` — ссылки на CSV/ToC/конфиги, опционально — Salesforce ids.
3. **Run:** `run_job` → воркер берёт задачу, бьёт по API симуляторам/оптимизации.
4. **Report:** воркер кладёт JSON + артефакты (CSV/HTML) → `reports`.
5. **Loop:** `get_report` возвращает краткое резюме (best/frontier), ссылку на полный отчёт. Ты кидаешь мне id — я продолжаю.

## Форматы
### Scenario Job (request)
```json
{
  "profile_id": "uuid",
  "type": "capacity_sweep",
  "inputs": {
    "arrival_rate": 12,
    "service_time": {"dist":"lognormal","mu":"10m","sigma":0.5},
    "capacity_agents": [6,8,10],
    "shift_calendar": {"Mon-Fri":"09:00-17:00"},
    "targets": {"sla_target":0.95},
    "constraints": {"budget_max": 20000}
  },
  "attachments": [{"kind":"toc_yaml","url":"https://.../ToC.yaml"}]
}
```

### Report (резюме)
```json
{
  "job_id":"uuid",
  "status":"succeeded",
  "summary":{"best":{"capacity":8,"sla":0.953,"wait_p50_min":12.4,"cost":18750}},
  "frontier":[{"capacity":6,"sla":0.89},{"capacity":8,"sla":0.95}],
  "artifacts":[{"name":"report.html","signed_url":"https://..."}]
}
```
