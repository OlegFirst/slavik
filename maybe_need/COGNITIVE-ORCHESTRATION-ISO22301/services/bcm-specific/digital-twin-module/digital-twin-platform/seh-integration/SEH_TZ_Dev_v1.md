
# SEH — ТЗ для разработчиков (Standalone)
**Версия:** 1.0  
**Дата:** 2025-08-16  
**Назначение:** Чёткое задание на реализацию системы данных, симуляций и ИИ‑оркестрации для фонда SEH. ТЗ само‑достаточно и не требует чтения других документов (но ссылается на приложения/шаблоны).

---

## 1. Цели и рамки
**Что хотим:** операционная система данных для программ и грантов, способная автоматически собирать данные, оценивать влияние (Theory‑of‑Change), запускать симуляции/оптимизацию и выдавать управленческие решения.  
**Ключевые результаты:**
- Единая каноническая модель данных (Programs, Services, Outcomes, Grants, BCM и т.д.).
- Интеграция с Salesforce Nonprofit Cloud (PMM, Outcome, Grantmaking, кастом BCM).
- Data Lake + ETL (CSV/Sheets/API) + события CDC/Webhooks.
- Модуль симуляций (AnyLogic) + оптимизация (capacity, routing, disbursement, BCM).
- ToC‑движок: причинный граф, Монте‑Карло, расчёт прогноза/риска, подбор «политики».
- ИИ‑оркестратор: набор агентов, workflow, guardrails, журналы действий.
- BI‑дашборды и Open API для агрегированных метрик.
**Вне рамок v1:** мобильная разработка, сложные порталы для внешней публики, 3D/DT визуализация.

## 2. Пользовательские роли
- **Оператор/Аналитик:** грузит данные, запускает симуляции, получает планы.
- **Менеджер программ:** утверждает решения/расписания/транши.
- **Data Engineer:** поддержка ETL/качества/схем.
- **Админ:** IAM, политики, мониторинг.
- **Исследователь (read‑only):** доступ к анонимизированным наборам и API.

## 3. Архитектура (высокоуровнево)
- **Data Lake + DWH:** сырые, очищенные и витрины. Хранилище объектов для Evidence.
- **CRM Salesforce:** PMM (Program/Service/ServiceDelivery), Outcome Mgmt, Grantmaking, BCM custom.
- **Eventing:** Platform Events/CDC → шина событий → Data Lake; наши доменные топики (`indicator.measured`, `service.delivery.recorded`, `grant.disbursement.made`, `bcm.test.completed`, `poi.claim.submitted`).
- **Simulation Engine:** AnyLogic Cloud/API. Пакет сценариев: capacity, routing, KPI↔disbursement, BCM.
- **ToC Engine:** YAML граф причинности + конфиг оптимизации → генерация входов для симулятора → Монте‑Карло + policy search.
- **AI Orchestrator:** агенты (ETL/CRM/Sim/BI/Alert), state‑машина, guardrails, журналы.
- **BI и Open API:** 3 дашборда v1 + REST/JSON (агрегаты).

## 4. Источники и схемы данных
Опорные CSV‑шаблоны (поставляются): **SEH_CSV_Templates.zip**. Поля: Program, Service, Participant, ServiceDelivery, Outcome, Indicator, Target, Measurement, Evidence, FundingProgram, Application, GrantAward, Disbursement, ReportingRequirement, BCMScenario, BCMTest, Consent, Location.  
**Требования к данным:** даты ISO‑8601, UUID, словари дисагрегаций, гео (ISO/GeoJSON).

## 5. Интеграция с Salesforce
**Объекты v1:**  
- PMM: Program, Service, Program Engagement/Contact, Service Delivery.  
- Outcome Mgmt: Outcome, Indicator, Target, Measurement.  
- Grantmaking: Funding Program, Application, Award, Disbursement, Reporting Requirement.  
- Custom: BCM_Scenario__c, BCM_Test__c, Consent__c (или Consent Mgmt).  
**Синхронизация:**  
- Импорт → Bulk API (до 100k записей/батч), upsert по внешним id.  
- Экспорт → Platform Events/Change Data Capture → подписчик в Data Lake/ETL.  
**Нефункциональные:** SSO, MFA, профили/permission sets, аудит.

## 6. Доменные события (Kafka/NATS)
Примеры JSON Schema (фрагменты):
```json
{
  "$id": "indicator.measured", "type": "object",
  "properties": {
    "measurement_id": {"type":"string","format":"uuid"},
    "indicator_id": {"type":"string"},
    "period_start": {"type":"string","format":"date"},
    "period_end": {"type":"string","format":"date"},
    "value": {"type":"number"},
    "confidence": {"type":"number","minimum":0,"maximum":1}
  },
  "required": ["measurement_id","indicator_id","period_start","period_end","value"]
}
```
```json
{ "$id":"grant.disbursement.made", "type":"object",
  "properties":{"disbursement_id":{"type":"string","format":"uuid"},"grant_id":{"type":"string"},"amount":{"type":"number"},"date":{"type":"string","format":"date"}},
  "required":["disbursement_id","grant_id","amount","date"]
}
```

## 7. API (черновик OpenAPI v1)
- `POST /api/v1/measurements:batch` — пакетная загрузка измерений (idempotency‑key).  
- `GET /api/v1/indicators/{id}/measurements?from=&to=` — выборка фактов.  
- `POST /api/v1/sim/run` — запуск эксперимента (см. §9 форматы).  
- `POST /api/v1/impact/optimize` — поиск политики ToC (см. §10 входы/выходы).  
- `GET /api/v1/grants/{id}/disbursements` — агрегаты.  
- `GET /api/v1/dashboards/{name}` — JSON для BI.  
**Требования:** OAuth2/OIDC, scopes, rate limiting, подробный аудит запросов/ответов.

## 8. BI‑дашборды v1 (минимум)
- **Grant Burn‑rate:** транши vs расходы, прогноз cash‑flow, риск задержек.
- **Outcome vs Target:** три индикатора, таргеты, факт, доверие/качество.
- **BCM Readiness:** RTO/RPO, сценарии, последнее тестирование, узкие места.

## 9. Симуляции (AnyLogic) — форматы I/O
**Запуск эксперимента:**
```json
{
  "experiment": "capacity_sweep",
  "params": {
    "arrival_rate": 12,
    "service_time": {"dist":"lognormal","mu":"10m","sigma":0.5},
    "capacity_agents": [6,8,10],
    "shift_calendar": {"Mon-Fri":"09:00-17:00"},
    "targets": {"sla_target":0.95},
    "constraints": {"budget_max": 20000}
  },
  "monte_carlo_runs": 200
}
```
**Ответ:**
```json
{
  "run_id":"...", "experiment":"capacity_sweep",
  "best": {"capacity": 8, "sla":0.953, "wait_p50_min": 12.4, "cost": 18750},
  "frontier":[{"capacity":6,"sla":0.89},{"capacity":8,"sla":0.95}],
  "explain":"Узкое место — регистрация; рекомендуем 1 плавающую ставку в часы пик"
}
```

## 10. ToC — конфиг и оптимизация
**ToC YAML:** поставляется как `ToC_template.yaml` (узлы, связи, интервенции, индикаторы, приоры).  
**Конфиг оптимизации:** `ImpactSimulator_Config.json`.  
**Запрос оптимизации:**
```json
{
  "objective":"maximize_outcome_cov_per_cost",
  "budget_cap": 50000,
  "decision_variables":[
    {"id":"outreach_sms_intensity","min":0,"max":3,"step":0.1},
    {"id":"transport_vouchers_intensity","min":0,"max":2,"step":0.1},
    {"id":"counseling_intensity","min":0,"max":2,"step":0.1}
  ],
  "monte_carlo_runs": 1000
}
```
**Ответ:**
```json
{
  "policy": {"outreach_sms":1.6,"transport_vouchers":0.8,"counseling":1.1},
  "coverage_forecast": {"mean":0.71,"p10":0.66,"p90":0.75},
  "cost": 49800,
  "nmb": 0.42,
  "assumptions":["эластичности как в приорах"]
}
```

## 11. ИИ‑оркестратор
**Workflow:** `intake → enrich → simulate/optimize → explain → commit (CRM/BI) → notify → learn`  
**Агенты/инструменты:** ETL, CRM, Simulation, BI, Alerts.  
**Guardrails:** роли и лимиты, RAG по политике/мастер‑доку, журнал команд, песочницы.  
**Логи:** все действия с метаданными (user, tool, входы/выходы, время).

## 12. Безопасность и соответствие
- OIDC/MFA, RBAC/ABAC, шифрование in‑transit и at‑rest (KMS), ротация ключей.
- PII‑изоляция: псевдонимизация Participant↔Identity; Vault для ключей линковки.
- DPIA/Privacy by Design, Retention (Measurements 7y, Evidence 5y, Consent revoke+5y).
- Аудит интеграций и событий, алерты аномалий доступа.

## 13. Окружения и DevOps
- **Envs:** dev / test / prod, изолированные аккаунты/ключи.
- **CI/CD:** линтеры схем, контракты API (schema tests), smoke‑тесты.
- **Observability:** метрики API/ETL/симуляций, логи, трассировки; алерты по SLO.
- **Backups/DR:** ежедневные снепшоты; учёт RPO/RTO для критичных сервисов.

## 14. Тестирование и качество
- **Data QA:** валидация CSV/ETL, completeness/consistency/valid ranges.
- **Контракты:** JSON Schema для событий и API; pact‑тесты с AnyLogic API mock.
- **Модели:** backtesting (MAPE/R^2), Монте‑Карло стабильность, сенситивити анализ.
- **Безопасность:** SAST/DAST, периодический pentest.

## 15. План поставки (минимум)
- **M1 (2 недели):** Data Lake+ETL, мэппинг CSV→Salesforce, 3 дашборда каркас.
- **M2 (2 недели):** AnyLogic интеграция: capacity и BCM; API `/sim/run`.
- **M3 (2 недели):** ToC Engine + `/impact/optimize`; оркестратор v1.
- **M4 (1 неделя):** стабилизация, документация, передача.

## 16. Приёмочные критерии (DoD)
- Импорт ≥200 ServiceDelivery, ≥3 индикатора с Target+Measurements.
- Один Grant с Disbursements и отчётностью.
- Запуск симуляции `capacity_sweep` и `bcm_outage` через API → валидный JSON выход.
- `/impact/optimize` возвращает политику и прогноз с доверительными интервалами.
- Три дашборда отдают корректные данные.
- Логи действий и аудит включены, базовые алерты настроены.

## 17. Приложения
- CSV‑шаблоны: `SEH_CSV_Templates.zip`
- Mermaid‑схемы: `SEH_iso_scenarios_ai_orchestration_min.html`
- ToC: `ToC_template.yaml`
- Impact Simulator: `ImpactSimulator_Config.json`

---

**Контакты:** SEH Architecture • arh@seh.example • Slack: #seh-data-sim
