# {{projectName|Звіт по проекту}}

**Автор:** {{author}}  
**Дата:** {{date|{{new Date().toLocaleDateString('uk-UA')}}}}  
**Версія:** {{version|1.0}}

---

## Огляд проекту

{{description|Опис проекту}}

### Основні характеристики

{{#if features}}
{{#each features as feature}}
- **{{feature.name}}**: {{feature.description}}
{{/each}}
{{/if}}

---

## Технічні деталі

### Технологічний стек

{{#if technologies}}
| Технологія | Версія | Призначення |
|------------|--------|-------------|
{{#each technologies as tech}}
| {{tech.name}} | {{tech.version}} | {{tech.purpose}} |
{{/each}}
{{/if}}

### Архітектура

{{architecture|Опис архітектури системи}}

---

## Прогрес виконання

### Завершені завдання

{{#if completedTasks}}
{{#each completedTasks as task}}
- [x] {{task}}
{{/each}}
{{/if}}

### Поточні завдання

{{#if currentTasks}}
{{#each currentTasks as task}}
- [ ] {{task}}
{{/each}}
{{/if}}

### Заплановані завдання

{{#if plannedTasks}}
{{#each plannedTasks as task}}
- [ ] {{task}}
{{/each}}
{{/if}}

---

## Метрики

| Метрика | Значення |
|---------|----------|
| Рядків коду | {{linesOfCode|0}} |
| Тестів | {{testsCount|0}} |
| Покриття тестами | {{testCoverage|0}}% |
| Відкритих багів | {{openBugs|0}} |

---

## Ризики та проблеми

{{#if risks}}
### Поточні ризики

{{#each risks as risk}}
**{{risk.level}}**: {{risk.description}}
- **Вплив**: {{risk.impact}}
- **Ймовірність**: {{risk.probability}}
- **План мітигації**: {{risk.mitigation}}

{{/each}}
{{/if}}

{{#if issues}}
### Відомі проблеми

{{#each issues as issue}}
- **{{issue.severity}}**: {{issue.title}}
  - Опис: {{issue.description}}
  - Статус: {{issue.status}}
  {{#if issue.assignee}}
  - Відповідальний: {{issue.assignee}}
  {{/if}}

{{/each}}
{{/if}}

---

## Висновки

{{conclusions|Основні висновки та рекомендації}}

### Наступні кроки

{{#if nextSteps}}
{{#each nextSteps as step}}
1. {{step}}
{{/each}}
{{/if}}

---

*Звіт згенеровано автоматично системою Documentator*
*{{generatedAt|{{new Date().toISOString()}}}}*