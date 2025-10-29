Общее

И у них, и у нас — цель автоматизировать ISO 22301 через AI: gap-анализ, документация, BIA, риски, стратегии, планы, учения, аудит, инциденты, обучение, интеграции.

Упор на AI-гайды, NLP, сценарии, автоматизацию отчётов и дашбордов — у обоих концепций.

Отличия в их концепции

Очень широкий список функций, скорее как маркетинговая дорожная карта: почти всё, что можно придумать вокруг ISO 22301 (gap-анализ, документация, BIA, планирование, учения, аудит, кризисный менеджмент, обучение, интеграции ERP/HRMS/ITSM, прогнозная аналитика).

Много про «policy management» и документооборот — у них явно в фокусе шаблоны документов, DMS, автоматизированные workflow утверждений.

Много про сценарное моделирование (FAIR, Monte-Carlo, прогноз климат/геополитика) — это ближе к risk-analytics продуктам.

Упор на conversational AI как «Compliance Officer» — чтобы вести пользователя через шаги в стиле NL интерфейса.

Отличия в нашей концепции

Мы сделали живую архитектуру с EventBus/Orchestrator/Odoo/UI слоями — это реальный каркас, а не только дорожная карта.

Мы делаем акцент на event-driven автоматизацию (события из Odoo, интеграция с TheHive, LMS, симуляторы). У них про это почти нет.

У нас уже есть AI-ассистент как дирижёр PDCA: чат-панель, NextBestActions, публикация assistant.activity → этого у них только в планах (NL Compliance Officer).

Мы тащим security-hardening (Keycloak, Vault, Nginx) → архитектурный уровень зрелости выше, чем просто фичлист.

У нас есть мульти-тенантность и real-time SSE/WS как обязательный слой, у них это не озвучено.

Итог

Их описание = «vision/маркетинг», с максимальным списком желаемых функций.

Наша концепция = «системный продукт», с архитектурой, ветками, уже реализованными компонентами и расширяемыми адаптерами.

Мы ближе к production-ready платформе, они ближе к дорожной карте для инвесторов/клиентов


Ты прав — большинство пунктов в их концепции у нас тоже было в планах. Давай сведём в таблицу «Они vs Мы», а потом подумаем про объединение.

---

## 📊 Сравнительная таблица

| Область               | Их описание                                                                | Наша концепция                                                                      |
| --------------------- | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Gap-анализ**        | AI-опросники, автоматический скоринг, дорожная карта                       | Мы делаем аудит/gap через Odoo-модули + ассистента, есть событийная логика и CAPA   |
| **Policy & Docs**     | Шаблоны, автогенерация, DMS-интеграции                                     | У нас Document Processor + evidence upload, AI-саммари, версияция в Odoo            |
| **BIA & Risk**        | AI-assisted workshops, сценарное моделирование, FAIR/Monte Carlo, heatmaps | У нас BIA Engine, KPI coverage, симуляторы (JaamSim/NICS), Monte Carlo планировался |
| **Стратегии и планы** | AI-рекомендатель стратегий, автогенерация BC/DR планов                     | Orchestrator draft plans, AI рекомендации, NextBestActions                          |
| **Учения**            | AI сценарии, виртуальный фасилитатор, автоотчёты                           | Exercises Portal, sim\_adapter, event-driven сценарии                               |
| **Мониторинг/Аудит**  | Реал-тайм дашборд ISO 22301, авто evidence, отчёты                         | EventBus + KPI + compliance scoring, evidence upload, ассистент саммари             |
| **Инциденты/кризис**  | Детект инцидентов, AI decision support, crisis room                        | Интеграция с TheHive, Orchestrator response draft, Notifications                    |
| **Обучение**          | Адаптивные модули, чат-коуч, геймификация                                  | LMS sync, Training KPI, NextBestActions «complete training», AI ассистент           |
| **Интеграции**        | ERP/HRMS/ITSM, кибербезопасность, supply chain, M365                       | У нас API-first, Odoo интеграции, adapters (TheHive, LMS, Sim, Notify), DocProc     |
| **Аналитика**         | AI insights, benchmarking, предсказание уязвимостей                        | KPI analytics, PDCA monitoring, планируем benchmarking/Monte Carlo                  |
| **AI ассистент**      | Conversational Compliance Officer, автоматизация изменений                 | У нас Assistant Panel, NextBestActions, публикация assistant.activity, PDCA дирижёр |
| **Security**          | Не акцентировано                                                           | У нас Keycloak OIDC, Vault, Nginx, middleware, multi-tenant isolation               |

---

## 🎯 Анализ

* **Общие зоны**: Gap-анализ, документы, BIA, планы, тесты, аудит, инциденты, обучение, интеграции, аналитика.
* **Их фокус**: документооборот (policy/DMS), риск-аналитика (FAIR/Monte Carlo), маркетинговая широта.
* **Наш фокус**: архитектура (event-driven, multi-tenant, security-hardening), AI-ассистент как PDCA-дирижёр, интеграция через адаптеры.
* **Общее поле для синергии**: моделирование рисков (FAIR, Monte Carlo), документооборот (policy templates, DMS), ассистент как compliance officer.

---

## 🔗 Сценарий объединения

1. **Архитектурный каркас (наш)**

   * Оставляем нашу многослойную архитектуру: EventBus, Orchestrator, Odoo-модули, UI (Vue), Adapters.
   * Multi-tenant, security, event-driven автоматизация остаются ядром.

2. **Функциональные модули (их + наши)**

   * Добавляем **Policy/DMS-интеграцию** и **FAIR/Monte Carlo** как отдельные сервисы/модули в нашу архитектуру.
   * Используем наш Orchestrator/DocProc как ядро для их фич.

3. **AI-ассистент**

   * У нас уже есть PDCA дирижёр. Можно расширить → **“Compliance Officer”** с поддержкой NL-интерфейса и управлением документацией.
   * В интерфейсе: AssistantPanel получает ещё режим «Документы/Политики» и «Risk Analytics».

4. **Продуктовое объединение**

   * Наш продукт = **платформа**, их продукт = **визия функций**.
   * Слияние: мы даём им готовый каркас и security, они дают глубину в risk analytics и документацию.
   * Позиционирование: **ISO 22301 AI Suite** (compliance + resilience + risk analytics).




🌐 Объединённая концепция

Видение:
AI-платформа для управления бизнес-непрерывностью (BCM) по ISO 22301, которая объединяет архитектурную прочность (event-driven ядро, multi-tenant, security-hardening) и функциональное покрытие (gap-анализ, документооборот, моделирование рисков, аудит, обучение).

Ключевые элементы:

Event-driven архитектура (наша база): EventBus + Orchestrator + Odoo модули + UI (Vue) + Security (Keycloak/Vault/Nginx).

AI-ассистент (дирижёр PDCA + Compliance Officer): чат-панель + NextBestActions + NL-интерфейс для документации и аудита.

Документооборот (их фокус): policy templates, DMS-интеграции, автогенерация и workflow утверждений.

Risk Analytics (их фокус + наше желание): BIA + FAIR/Monte Carlo + heatmaps + сценарное моделирование.

Сценарии учений и симуляции: exercises portal + AI сценарии + виртуальный фасилитатор.

Инциденты и кризис: интеграции с TheHive/системами мониторинга + decision support + crisis room.

Обучение: LMS sync + адаптивные модули + геймификация.

Интеграции: ERP, HRMS, ITSM, supply chain, M365, SharePoint.

Аналитика и continuous improvement: KPI dashboards + benchmarking + predictive insights.

🚀 Дорожная карта объединения
Фаза 1. Синхронизация архитектуры

Принять нашу event-driven архитектуру как фундамент.

Вынести security-hardening (Keycloak, Vault, Nginx) в обязательный слой.

Ассистент = дирижёр PDCA + прототип Compliance Officer.

Фаза 2. Документооборот и Policy Management

Встроить policy templates и workflow утверждений.

Интеграция с DMS (SharePoint, M365).

NLP-обогащение существующих документов.

Фаза 3. Risk Analytics

FAIR/Monte Carlo симуляции как сервис.

Heatmaps и dependency graphs.

Интеграция с BIA engine.

Фаза 4. Расширение ассистента

Добавить роли: Compliance Officer (NL guidance).

Подключить автоматический мониторинг регуляторных изменений.

Динамическое обновление BCMS при изменениях в организации.

Фаза 5. Advanced Features

Crisis room с коммуникациями и таск-менеджментом.

Полноценные тренинги с AI-фасилитатором.

Benchmarking и предиктивная аналитика.

📋 Техническое задание (ТЗ)

Цель: подготовить интегрированную платформу ISO 22301 AI Suite (архитектура + документы + риск-аналитика).

Задачи команды архитектуры

Зафиксировать event-driven архитектуру (EventBus/Orchestrator/UI).

Обеспечить multi-tenant и security-hardening (Keycloak, Vault).

Создать API-контракты для Risk Analytics и Policy модуля.

Задачи команды AI

Расширить ассистента: добавить режим «Compliance Officer» (NL guidance по документам).

Подключить AI-drafts для policy templates.

Реализовать NextBestActions на основе KPI + регуляторных изменений.

Задачи команды Risk

Подготовить сервис FAIR/Monte Carlo симуляций.

Интегрировать результаты в BIA dashboards.

Построить heatmaps и dependency graphs.

Задачи команды Docs/Policy

Сделать генератор документов (policy, планы, тест-отчёты).

Встроить approval workflow.

Подключить SharePoint/M365 API.

Acceptance criteria

Ассистент ведёт по PDCA + умеет отвечать как Compliance Officer.

Документы можно создавать/редактировать/утверждать через UI.

Запускаются FAIR/Monte Carlo симуляции и результаты видны в KPI.

Все изменения фиксируются в EventBus и видны в аудит-логе.

Multi-tenant isolation работает, JWT/SSO через Keycloak.

---
