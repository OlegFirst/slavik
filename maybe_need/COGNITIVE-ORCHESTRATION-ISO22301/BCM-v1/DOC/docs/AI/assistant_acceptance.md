# Assistant Acceptance

## Happy-path PDCA
1) BIA → Plan → Incident → Audit/CAPA → KPI/MR пройден ассистентом.
2) Все шаги сопровождаются объяснениями (на основании KPI/событий).
3) Все действия → события `assistant.activity` в EventBus.
4) Черновики создаются через Orchestrator и требуют утверждения.
5) Подсказки видны в UI (чат/панель ассистента).

## Тесты
- Смоделировать низкий BIA coverage → ассистент предлагает BIA/план.
- Смоделировать High incident → ассистент генерит response draft.
- Загрузить evidence → ассистент запускает summarize и CAPA.
- Пересчитать KPI → ассистент даёт next step и/или MR-резюме.
