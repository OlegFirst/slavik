"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProjectInitializer = void 0;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
const ProjectManager_1 = require("../core/ProjectManager");
class ProjectInitializer {
    constructor(baseDir = './') {
        this.projectManager = new ProjectManager_1.ProjectManager(baseDir);
        this.projectsDir = path.join(baseDir, 'projects');
    }
    async initializeDefaultProjects() {
        console.log('Ініціалізація прикладів проектів...');
        try {
            // Проект для IT звітів
            await this.createItReportsProject();
            // Проект для бізнес планів
            await this.createBusinessPlansProject();
            // Проект для технічної документації
            await this.createTechDocsProject();
            console.log('Приклади проектів успішно створено!');
        }
        catch (error) {
            console.error('Помилка створення прикладів проектів:', error);
        }
    }
    async createItReportsProject() {
        const projectName = 'IT-звіти';
        const projectId = 'it-zvity';
        if (await this.projectExists(projectId)) {
            return;
        }
        await this.projectManager.createProject({
            name: projectName,
            description: 'Шаблони для IT звітів: тижневі, місячні, проектні звіти'
        });
        const projectPath = this.projectManager.getProjectPath(projectId);
        // Тижневий звіт розробника
        await this.createFile(projectPath, 'templates/weekly-developer-report.md', `# Тижневий звіт розробника

**Розробник:** {{developer|Ім'я розробника}}  
**Тиждень:** {{week|1-7 січня 2024}}  
**Проект:** {{project|Назва проекту}}

---

## Виконані завдання

{{#if completedTasks}}
{{#each completedTasks as task}}
### {{task.title}}
- **Опис:** {{task.description}}
- **Час:** {{task.timeSpent}} годин
- **Статус:** ✅ Завершено
- **Посилання:** {{task.link|#}}

{{/each}}
{{#else}}
*Немає завершених завдань*
{{/if}}

---

## Поточні завдання

{{#if currentTasks}}
{{#each currentTasks as task}}
### {{task.title}}
- **Опис:** {{task.description}}
- **Прогрес:** {{task.progress|0}}%
- **Очікувана дата завершення:** {{task.deadline}}
- **Блокери:** {{task.blockers|Немає}}

{{/each}}
{{#else}}
*Немає поточних завдань*
{{/if}}

---

## Заплановані завдання на наступний тиждень

{{#if plannedTasks}}
{{#each plannedTasks as task}}
- {{task.title}} ({{task.estimatedTime}} годин)
{{/each}}
{{#else}}
*Завдання на наступний тиждень ще не заплановані*
{{/if}}

---

## Проблеми та ризики

{{#if issues}}
{{#each issues as issue}}
**{{issue.severity}}**: {{issue.title}}
- Опис: {{issue.description}}
- Вплив: {{issue.impact}}
- Запропоноване рішення: {{issue.solution}}

{{/each}}
{{#else}}
*Проблем не виявлено*
{{/if}}

---

## Навчання та розвиток

{{learningActivities|Опишіть активності з навчання цього тижня}}

---

## Коментарі

{{comments|Додаткові коментарі та зауваження}}

---

*Звіт створено: {{generatedDate|{{new Date().toLocaleDateString('uk-UA')}}}}*`);
        // Місячний звіт по проекту
        await this.createFile(projectPath, 'templates/monthly-project-report.md', `# Місячний звіт по проекту

**Проект:** {{projectName}}  
**Місяць:** {{month|Січень 2024}}  
**Менеджер проекту:** {{projectManager}}  
**Команда:** {{teamSize|5}} осіб

---

## Резюме проекту

{{projectSummary|Короткий опис проекту та його поточного стану}}

### Ключові досягнення

{{#if achievements}}
{{#each achievements as achievement}}
- ✅ {{achievement}}
{{/each}}
{{#else}}
- Досягнення будуть додані пізніше
{{/if}}

---

## Метрики продуктивності

| Метрика | Поточне значення | Ціль | Статус |
|---------|------------------|------|--------|
| Завершено задач | {{completedTasks|0}} | {{targetTasks|50}} | {{tasksStatus|В процесі}} |
| Покриття тестами | {{testCoverage|75}}% | {{targetCoverage|80}}% | {{coverageStatus|Майже досягнуто}} |
| Відкритих багів | {{openBugs|3}} | {{maxBugs|5}} | {{bugsStatus|Норма}} |
| Velocity (SP) | {{velocity|25}} | {{targetVelocity|30}} | {{velocityStatus|Нижче цілі}} |

---

## Прогрес по віхах

{{#if milestones}}
{{#each milestones as milestone}}
### {{milestone.name}}
- **Заплановано:** {{milestone.planned}}
- **Фактично:** {{milestone.actual|В процесі}}
- **Статус:** {{milestone.status}}
- **Коментар:** {{milestone.comment}}

{{/each}}
{{#else}}
*Віхи проекту не визначені*
{{/if}}

---

## Команда

### Розподіл навантаження

{{#if teamMembers}}
| Член команди | Роль | Завантаженість | Продуктивність |
|--------------|------|----------------|----------------|
{{#each teamMembers as member}}
| {{member.name}} | {{member.role}} | {{member.workload|100}}% | {{member.performance|Нормальна}} |
{{/each}}
{{#else}}
*Інформація про команду не надана*
{{/if}}

---

## Бюджет

| Категорія | Заплановано | Витрачено | Залишок |
|-----------|-------------|-----------|---------|
| Розробка | ${{ plannedDev } | 50000}} | ${{ spentDev } | 35000}} | ${{ remainingDev } | 15000}} |
| Тестування | ${{ plannedTest } | 15000}} | ${{ spentTest } | 12000}} | ${{ remainingTest } | 3000}} |
| Інфраструктура | ${{ plannedInfra } | 10000}} | ${{ spentInfra } | 8000}} | ${{ remainingInfra } | 2000}} |
| **Всього** | **${{ totalPlanned } | 75000}}** | **${{ totalSpent } | 55000}}** | **${{ totalRemaining } | 20000}}** |

---

## Ризики та проблеми

{{#if risks}}
### Ризики
{{#each risks as risk}}
**{{risk.level}}**: {{risk.title}}
- Опис: {{risk.description}}
- Ймовірність: {{risk.probability}}
- Вплив: {{risk.impact}}
- Мітигація: {{risk.mitigation}}

{{/each}}
{{/if}}

{{#if issues}}
### Поточні проблеми
{{#each issues as issue}}
**{{issue.severity}}**: {{issue.title}}
- Опис: {{issue.description}}
- Відповідальний: {{issue.assignee}}
- Дедлайн: {{issue.deadline}}

{{/each}}
{{/if}}

---

## План на наступний місяць

{{#if nextMonthPlan}}
{{#each nextMonthPlan as item}}
- {{item}}
{{/each}}
{{#else}}
*План на наступний місяць буде сформовано пізніше*
{{/if}}

---

## Висновки

{{conclusions|Основні висновки та рекомендації на основі результатів місяця}}

---

*Звіт підготовлено: {{reportDate|{{new Date().toLocaleDateString('uk-UA')}}}}*  
*Наступний звіт: {{nextReportDate}}*`);
        console.log(`✓ Створено проект "${projectName}"`);
    }
    async createBusinessPlansProject() {
        const projectName = 'Бізнес-плани';
        const projectId = 'biznes-plany';
        if (await this.projectExists(projectId)) {
            return;
        }
        await this.projectManager.createProject({
            name: projectName,
            description: 'Шаблони бізнес-планів, презентацій та фінансових звітів'
        });
        const projectPath = this.projectManager.getProjectPath(projectId);
        // Бізнес-план стартапу
        await this.createFile(projectPath, 'templates/startup-business-plan.md', `# Бізнес-план: {{companyName}}

**Дата:** {{date|{{new Date().toLocaleDateString('uk-UA')}}}}  
**Версія:** {{version|1.0}}  
**Підготувано:** {{preparedBy}}

---

## 1. Резюме проекту

### Опис бізнесу
{{businessDescription|Короткий опис бізнес-ідеї та її унікальності}}

### Місія компанії
{{mission|Місія вашої компанії}}

### Бачення
{{vision|Бачення розвитку компанії на 5-10 років}}

### Ключові фактори успіху
{{#if successFactors}}
{{#each successFactors as factor}}
- {{factor}}
{{/each}}
{{#else}}
- Інноваційний продукт
- Досвідчена команда
- Великий ринок
{{/if}}

---

## 2. Опис продукту/послуги

### Продукт
{{productDescription|Детальний опис продукту або послуги}}

### Унікальна цінність
{{uniqueValue|Що робить ваш продукт унікальним}}

### Стадія розвитку
{{developmentStage|Концепція/Прототип/MVP/Готовий продукт}}

---

## 3. Аналіз ринку

### Розмір ринку
- **TAM (Total Addressable Market):** {{tam|$100M}}
- **SAM (Service Addressable Market):** {{sam|$20M}}
- **SOM (Service Obtainable Market):** {{som|$2M}}

### Цільова аудиторія
{{#if targetAudience}}
{{#each targetAudience as segment}}
**{{segment.name}}:**
- Розмір: {{segment.size}}
- Характеристики: {{segment.characteristics}}
- Потреби: {{segment.needs}}

{{/each}}
{{#else}}
*Цільова аудиторія буде визначена*
{{/if}}

### Конкуренти
{{#if competitors}}
| Конкурент | Сильні сторони | Слабкі сторони | Частка ринку |
|-----------|----------------|----------------|--------------|
{{#each competitors as competitor}}
| {{competitor.name}} | {{competitor.strengths}} | {{competitor.weaknesses}} | {{competitor.marketShare}} |
{{/each}}
{{#else}}
*Аналіз конкурентів буде проведено*
{{/if}}

---

## 4. Маркетингова стратегія

### Позиціонування
{{positioning|Як ви позиціонуєте свій продукт на ринку}}

### Маркетинговий мікс (4P)
- **Product (Продукт):** {{product4p}}
- **Price (Ціна):** {{price4p}}
- **Place (Місце):** {{place4p}}
- **Promotion (Просування):** {{promotion4p}}

### Канали залучення клієнтів
{{#if acquisitionChannels}}
{{#each acquisitionChannels as channel}}
- **{{channel.name}}:** {{channel.description}} ({{channel.cost}})
{{/each}}
{{#else}}
- Цифровий маркетинг
- Соціальні мережі
- Partnerships
{{/if}}

---

## 5. Операційний план

### Команда
{{#if team}}
{{#each team as member}}
**{{member.name}}** - {{member.position}}
- Досвід: {{member.experience}}
- Відповідальності: {{member.responsibilities}}

{{/each}}
{{#else}}
*Склад команди буде визначено*
{{/if}}

### Операційна модель
{{operationalModel|Опис того, як працюватиме ваш бізнес щодня}}

### Необхідні ресурси
{{#if resources}}
{{#each resources as resource}}
- {{resource.name}}: {{resource.description}} ({{resource.cost}})
{{/each}}
{{/if}}

---

## 6. Фінансовий план

### Стартові витрати
{{#if startupCosts}}
| Категорія | Сума |
|-----------|------|
{{#each startupCosts as cost}}
| {{cost.category}} | ${{ cost, : .amount }} |
{{/each}}
| **Всього** | **${{ totalStartupCosts }}** |
{{#else}}
*Стартові витрати будуть розраховані*
{{/if}}

### Прогноз доходів (3 роки)
{{#if revenueProjection}}
| Рік | Дохід | Витрати | Прибуток |
|-----|-------|---------|----------|
{{#each revenueProjection as year}}
| {{year.year}} | ${{ year, : .revenue }} | ${{ year, : .expenses }} | ${{ year, : .profit }} |
{{/each}}
{{#else}}
*Прогноз буде підготовлено*
{{/if}}

### Точка беззбитковості
{{breakEvenPoint|Місяць/рік досягнення точки беззбитковості}}

---

## 7. Фінансування

### Потреба в інвестиціях
{{fundingNeed|Сума необхідного фінансування}}

### Використання коштів
{{#if fundingUse}}
{{#each fundingUse as use}}
- {{use.purpose}}: {{use.percentage}}% ({{use.amount}})
{{/each}}
{{#else}}
- Розробка продукту: 40%
- Маркетинг: 30%
- Операційні витрати: 20%
- Резерв: 10%
{{/if}}

### Пропозиція для інвесторів
{{investorProposal|Що ви пропонуєте інвесторам в обмін на інвестиції}}

---

## 8. Ризики

{{#if risks}}
{{#each risks as risk}}
**{{risk.type}}**: {{risk.description}}
- Ймовірність: {{risk.probability}}
- Вплив: {{risk.impact}}
- Мітигація: {{risk.mitigation}}

{{/each}}
{{#else}}
*Аналіз ризиків буде проведено*
{{/if}}

---

## 9. Додатки

{{appendices|Посилання на додаткові матеріали, дослідження, презентації}}

---

*Бізнес-план підготовлено: {{preparedDate|{{new Date().toLocaleDateString('uk-UA')}}}}*`);
        console.log(`✓ Створено проект "${projectName}"`);
    }
    async createTechDocsProject() {
        const projectName = 'Технічна документація';
        const projectId = 'tekhnichna-dokumentatsiya';
        if (await this.projectExists(projectId)) {
            return;
        }
        await this.projectManager.createProject({
            name: projectName,
            description: 'Шаблони технічної документації: API, архітектури, посібники'
        });
        const projectPath = this.projectManager.getProjectPath(projectId);
        // API документація
        await this.createFile(projectPath, 'templates/api-documentation.md', `# API Documentation: {{apiName}}

**Version:** {{version|1.0.0}}  
**Base URL:** {{baseUrl|https://api.example.com/v1}}  
**Last Updated:** {{lastUpdated|{{new Date().toLocaleDateString('uk-UA')}}}}

---

## Overview

{{apiDescription|Short description of what this API does}}

### Authentication

{{#if authType}}
This API uses {{authType}} authentication.

{{#if authType === 'Bearer Token'}}
Include the authorization header in your requests:
\`\`\`
Authorization: Bearer YOUR_TOKEN_HERE
\`\`\`
{{/if}}

{{#if authType === 'API Key'}}
Include the API key in your requests:
\`\`\`
X-API-Key: YOUR_API_KEY_HERE
\`\`\`
{{/if}}

{{#else}}
Authentication method: To be defined
{{/if}}

### Rate Limiting

{{rateLimiting|Rate limiting information will be specified}}

---

## Base Response Format

All API responses follow this structure:

\`\`\`json
{
  "success": boolean,
  "data": object | array,
  "error": {
    "code": string,
    "message": string
  },
  "meta": {
    "timestamp": string,
    "version": string
  }
}
\`\`\`

---

## Endpoints

{{#if endpoints}}
{{#each endpoints as endpoint}}
### {{endpoint.method}} {{endpoint.path}}

{{endpoint.description}}

**Parameters:**

{{#if endpoint.parameters}}
{{#each endpoint.parameters as param}}
- \`{{param.name}}\` ({{param.type}}) - {{param.description}} {{#if param.required}}*required*{{/if}}
{{/each}}
{{#else}}
No parameters required.
{{/if}}

**Example Request:**

\`\`\`{{endpoint.requestLang|bash}}
{{endpoint.exampleRequest|curl -X GET "https://api.example.com/v1/endpoint"}}
\`\`\`

**Example Response:**

\`\`\`json
{{endpoint.exampleResponse|{"success": true, "data": {}}}}
\`\`\`

**Error Responses:**

{{#if endpoint.errors}}
{{#each endpoint.errors as error}}
- \`{{error.code}}\` - {{error.description}}
{{/each}}
{{#else}}
Standard HTTP error codes apply.
{{/if}}

---

{{/each}}
{{#else}}
API endpoints will be documented here.
{{/if}}

## Error Codes

{{#if errorCodes}}
| Code | Description |
|------|-------------|
{{#each errorCodes as error}}
| {{error.code}} | {{error.description}} |
{{/each}}
{{#else}}
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |
{{/if}}

---

## SDK Examples

{{#if sdkExamples}}
{{#each sdkExamples as example}}
### {{example.language}}

\`\`\`{{example.language}}
{{example.code}}
\`\`\`

{{/each}}
{{#else}}
SDK examples will be provided.
{{/if}}

---

## Changelog

{{#if changelog}}
{{#each changelog as change}}
### {{change.version}} - {{change.date}}

{{change.description}}

{{#if change.breaking}}
**Breaking Changes:**
{{#each change.breaking as breaking}}
- {{breaking}}
{{/each}}
{{/if}}

{{/each}}
{{#else}}
Version history will be maintained here.
{{/if}}

---

*Documentation generated on {{generatedDate|{{new Date().toISOString()}}}}*`);
        // Архітектурна документація
        await this.createFile(projectPath, 'templates/architecture-document.md', `# System Architecture: {{systemName}}

**Version:** {{version|1.0}}  
**Date:** {{date|{{new Date().toLocaleDateString('uk-UA')}}}}  
**Architect:** {{architect|System Architect}}

---

## 1. System Overview

### Purpose
{{systemPurpose|Describe the main purpose and goals of the system}}

### Scope
{{systemScope|Define what is included and excluded from this system}}

### Stakeholders
{{#if stakeholders}}
{{#each stakeholders as stakeholder}}
- **{{stakeholder.role}}:** {{stakeholder.responsibilities}}
{{/each}}
{{#else}}
- Business Users
- Development Team
- Operations Team
- Security Team
{{/if}}

---

## 2. Business Requirements

### Functional Requirements
{{#if functionalRequirements}}
{{#each functionalRequirements as req}}
- **{{req.id}}:** {{req.description}}
  - Priority: {{req.priority}}
  - Status: {{req.status}}
{{/each}}
{{#else}}
Functional requirements to be defined.
{{/if}}

### Non-Functional Requirements
{{#if nonFunctionalRequirements}}
{{#each nonFunctionalRequirements as req}}
- **{{req.category}}:** {{req.description}}
  - Target: {{req.target}}
  - Measurement: {{req.measurement}}
{{/each}}
{{#else}}
- Performance: Response time < 2 seconds
- Availability: 99.9% uptime
- Scalability: Support 10,000 concurrent users
- Security: Enterprise-grade security standards
{{/if}}

---

## 3. High-Level Architecture

### Architecture Style
{{architectureStyle|Microservices/Monolithic/Serverless/Hybrid}}

### Key Architectural Principles
{{#if architecturePrinciples}}
{{#each architecturePrinciples as principle}}
- {{principle}}
{{/each}}
{{#else}}
- Separation of Concerns
- Single Responsibility
- Loose Coupling
- High Cohesion
- Scalability First
{{/if}}

### System Context Diagram

\`\`\`
{{contextDiagram|[System Context Diagram will be included here]}}
\`\`\`

---

## 4. Component Architecture

### Core Components

{{#if components}}
{{#each components as component}}
#### {{component.name}}

**Purpose:** {{component.purpose}}
**Responsibilities:** {{component.responsibilities}}
**Technologies:** {{component.technologies}}
**Interfaces:** {{component.interfaces}}

{{/each}}
{{#else}}
System components will be detailed here.
{{/if}}

### Component Diagram

\`\`\`
{{componentDiagram|[Component Diagram will be included here]}}
\`\`\`

---

## 5. Data Architecture

### Data Model
{{dataModel|Description of the data model and key entities}}

### Database Design
{{#if databases}}
{{#each databases as db}}
#### {{db.name}} ({{db.type}})

- **Purpose:** {{db.purpose}}
- **Schema:** {{db.schema}}
- **Backup Strategy:** {{db.backup}}
- **Performance Requirements:** {{db.performance}}

{{/each}}
{{#else}}
Database specifications will be provided.
{{/if}}

### Data Flow Diagram

\`\`\`
{{dataFlowDiagram|[Data Flow Diagram will be included here]}}
\`\`\`

---

## 6. Technology Stack

### Languages & Frameworks
{{#if techStack}}
{{#each techStack as tech}}
- **{{tech.category}}:** {{tech.technology}} ({{tech.version}})
  - Rationale: {{tech.rationale}}
{{/each}}
{{#else}}
Technology choices will be specified.
{{/if}}

### Infrastructure
{{#if infrastructure}}
- **Cloud Provider:** {{infrastructure.cloud}}
- **Container Platform:** {{infrastructure.containers}}
- **CI/CD:** {{infrastructure.cicd}}
- **Monitoring:** {{infrastructure.monitoring}}
- **Security:** {{infrastructure.security}}
{{#else}}
Infrastructure specifications will be provided.
{{/if}}

---

## 7. Security Architecture

### Security Requirements
{{#if securityRequirements}}
{{#each securityRequirements as req}}
- {{req}}
{{/each}}
{{#else}}
- Authentication and Authorization
- Data Encryption (in transit and at rest)
- Input Validation
- Audit Logging
- Secure Communication
{{/if}}

### Security Controls
{{#if securityControls}}
{{#each securityControls as control}}
#### {{control.name}}

**Description:** {{control.description}}
**Implementation:** {{control.implementation}}
**Validation:** {{control.validation}}

{{/each}}
{{#else}}
Security controls will be detailed.
{{/if}}

---

## 8. Performance & Scalability

### Performance Targets
{{#if performanceTargets}}
{{#each performanceTargets as target}}
- **{{target.metric}}:** {{target.value}}
{{/each}}
{{#else}}
- Response Time: < 2 seconds
- Throughput: 1000 requests/second
- Concurrent Users: 10,000
- Data Volume: 10TB
{{/if}}

### Scalability Strategy
{{scalabilityStrategy|Horizontal/Vertical scaling approach and implementation}}

### Caching Strategy
{{cachingStrategy|Description of caching layers and strategies}}

---

## 9. Deployment Architecture

### Environment Strategy
{{#if environments}}
{{#each environments as env}}
- **{{env.name}}:** {{env.purpose}}
  - Infrastructure: {{env.infrastructure}}
  - Data: {{env.data}}
  - Access: {{env.access}}
{{/each}}
{{#else}}
- Development: For active development
- Testing: For QA and integration testing  
- Staging: Pre-production environment
- Production: Live system
{{/if}}

### Deployment Diagram

\`\`\`
{{deploymentDiagram|[Deployment Diagram will be included here]}}
\`\`\`

---

## 10. Monitoring & Operations

### Monitoring Strategy
{{monitoringStrategy|Description of monitoring approach and tools}}

### Key Metrics
{{#if keyMetrics}}
{{#each keyMetrics as metric}}
- **{{metric.name}}:** {{metric.description}}
  - Target: {{metric.target}}
  - Alert Threshold: {{metric.alert}}
{{/each}}
{{#else}}
Key operational metrics will be defined.
{{/if}}

### Disaster Recovery
{{disasterRecovery|Backup and recovery procedures}}

---

## 11. Migration Strategy

{{migrationStrategy|If applicable, describe migration from existing systems}}

---

## 12. Risks & Mitigation

{{#if risks}}
{{#each risks as risk}}
### {{risk.title}}

**Description:** {{risk.description}}
**Impact:** {{risk.impact}}
**Probability:** {{risk.probability}}
**Mitigation:** {{risk.mitigation}}

{{/each}}
{{#else}}
Project risks will be identified and documented.
{{/if}}

---

## 13. Future Considerations

{{futureconsiderations|Plans for future enhancements and evolution}}

---

*Document Version: {{docVersion|1.0}}*  
*Last Updated: {{lastUpdated|{{new Date().toLocaleDateString('uk-UA')}}}}*  
*Next Review: {{nextReview}}*`);
        console.log(`✓ Створено проект "${projectName}"`);
    }
    async createFile(projectPath, filePath, content) {
        const fullPath = path.join(projectPath, filePath);
        await fs.ensureDir(path.dirname(fullPath));
        await fs.writeFile(fullPath, content, 'utf-8');
    }
    async projectExists(projectId) {
        const projectPath = path.join(this.projectsDir, projectId);
        return await fs.pathExists(projectPath);
    }
}
exports.ProjectInitializer = ProjectInitializer;
//# sourceMappingURL=ProjectInitializer.js.map