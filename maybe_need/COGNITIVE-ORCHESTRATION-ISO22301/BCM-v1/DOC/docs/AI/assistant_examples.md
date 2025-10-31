# Assistant Examples (Dialogues by Workflow)

> Цель: показать готовые шаблоны диалогов ассистента по каждому воркфлоу PDCA.
> Формат краткий, применимый в UI-чат/панели. Все действия инициируются через API (Orchestrator/DocProc) и ждут событий подтверждения.

---

## 1) BIA (Business Impact Analysis)

**User:** Покажи статус и что делать дальше.  
**Assistant:**  
- Контекст: BIA coverage 64% (порог 80%), 2 High-процесса без актуальной BIA > 90 дней.  
- Рекомендации:  
  1) Запустить BIA для процесса *EHR*.  
  2) Запустить BIA для процесса *Pharmacy*.  
- Действия:  
  - `[Compute BIA: process_id=EHR]`  
  - `[Compute BIA: process_id=Pharmacy]`  
- Проверка: ждём `bcm.bia.completed` для каждого процесса.

**System note:** После `bcm.bia.completed` предложить `Generate BCP draft` по High-процессам.

---

## 2) Plan (BCP/DRP)

**User:** Обнови план по EHR.  
**Assistant:**  
- Контекст: План EHR старше 180 дней; прошлое учение было 220 дней назад.  
- Рекомендации:  
  1) Сгенерировать черновик BCP для EHR.  
  2) Запланировать tabletop-учение на 45 минут.  
- Действия:  
  - `[Generate draft BCP: process_id=EHR]`  
  - `[Schedule exercise: process_id=EHR, level=tabletop]`  
- Проверка: ждём `bcm.plan.draft_generated` и `bcm.exercise.scheduled`.

**System note:** После публикации плана → `bcm.plan.versioned`.

---

## 3) Incident Response

**User:** В центре инцидент: EHR недоступен.  
**Assistant:**  
- Контекст: Инцидент *EHR outage*, severity=High, нет чек-листа реагирования.  
- Рекомендации:  
  1) Сформировать AI-чек-лист реагирования (старт/коммы/ресурсы/шаги).  
- Действие:  
  - `[AI draft response: incident_id=TH-9321]`  
- Проверка: ждём `bcm.incident.response_generated`.

**System note:** При подтверждении — отметить 1–2 шага выполненными и предложить коммуникации.

---

## 4) Exercises / Simulation

**User:** Проверь готовность по аптеке.  
**Assistant:**  
- Контекст: Последнее учение по Pharmacy — 200 дней назад, High-критичность.  
- Рекомендации:  
  1) Назначить tabletop-учение на 30–45 минут.  
- Действие:  
  - `[Schedule exercise: process_id=Pharmacy, level=tabletop]`  
- Проверка: ждём `bcm.exercise.scheduled` → после прохождения `bcm.exercise.resulted` с метриками.

---

## 5) Audit & CAPA

**User:** Мы загрузили сертификат и процедуры — что дальше?  
**Assistant:**  
- Контекст: Документы проанализированы (score 0.72; ISO 4.1/5.2/6.1).  
- Рекомендации:  
  1) Summarize evidence (ISO 8.4) и сформировать CAPA по коммуникациям.  
- Действие:  
  - `[Summarize evidence: finding_ids=[…]]`  
- Проверка: ждём `bcm.audit.gap_found` и создание CAPA в Odoo.

---

## 6) KPI / Management Review

**User:** Что в KPI и какие два шага сейчас важны?  
**Assistant:**  
- Контекст: BIA coverage 78% (↓), Plans up-to-date 69% (↓), CAPA on-time 86% (↑).  
- Рекомендации:  
  1) Сгенерировать BCP для EHR (старый).  
  2) Назначить tabletop для Pharmacy (overdue).  
- Действия:  
  - `[Generate draft BCP: process_id=EHR]`  
  - `[Schedule exercise: process_id=Pharmacy, level=tabletop]`  
- Проверка: ждём `bcm.plan.draft_generated`, `bcm.exercise.scheduled`.

---

## 7) Documents / Evidence

**User:** Загрузил policy.pdf — что дальше?  
**Assistant:**  
- Контекст: policy.pdf analyzed, compliance_score=0.72.  
- Рекомендации:  
  - Summarize evidence и сформировать CAPA.  
- Действие:  
  - `[Summarize evidence: finding_ids=[…]]`  
- Проверка: `bcm.audit.gap_found`.

---

## 8) Assistant Activity (пример)
**System publish:**  
```json
{
  "event_type":"assistant.activity",
  "tenant_id":"demo_hospital",
  "data":{
    "intent":"plan_generate_draft",
    "reason":"plan outdated (>180d) & KPI: plans_up_to_date < 70%",
    "actions":[{"type":"plan","process_id":"EHR"}],
    "status":"requested",
    "correlation_id":"corr_abc123"
  }
}
```
