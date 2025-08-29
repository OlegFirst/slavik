# Приклад використання Documentator

## Запуск системи

1. Встановіть залежності: `install.bat`
2. Запустіть MCP сервер: `start.bat`
3. Підключіть до Claude Desktop (див. claude-config.json)

## Використання в Claude Desktop

### 1. Перегляд доступних проектів
```
Покажи мені всі доступні проекти
```

Claude покаже список вбудованих проектів:
- IT-звіти (it-zvity) - 2 шаблони
- Бізнес-плани (biznes-plany) - 1 шаблон  
- Технічна документація (tekhnichna-dokumentatsiya) - 2 шаблони

### 2. Аналіз проекту
```
Проаналізуй проект "it-zvity"
```

Claude покаже детальну інформацію про проект та доступні шаблони.

### 3. Створення тижневого звіту
```
Створи тижневий звіт розробника з проекту "it-zvity" з такими даними:
- developer: "Олексій Іванов" 
- week: "29 січня - 4 лютого 2024"
- project: "CRM система"
- completedTasks: [
  {
    "title": "Розробка API для клієнтів",
    "description": "Створено REST API для роботи з клієнтами",
    "timeSpent": 12,
    "link": "https://github.com/company/crm/pull/123"
  },
  {
    "title": "Налаштування тестування",
    "description": "Додано unit тести для сервісів",
    "timeSpent": 8,
    "link": "https://github.com/company/crm/pull/124"
  }
]
- currentTasks: [
  {
    "title": "Інтеграція з платіжною системою", 
    "description": "Підключення Stripe API",
    "progress": 60,
    "deadline": "10 лютого 2024"
  }
]
- plannedTasks: [
  {
    "title": "Оптимізація запитів до БД",
    "estimatedTime": 16
  }
]
```

### 4. Створення бізнес-плану
```
Створи бізнес-план стартапу з проекту "biznes-plany" для компанії "TechStart" з такими даними:
- companyName: "TechStart"
- businessDescription: "Платформа для автоматизації HR процесів в малих та середніх компаніях"
- mission: "Спростити HR процеси для бізнесу"
- vision: "Стати лідером HR автоматизації в Україні" 
- tam: "$500M"
- sam: "$50M"
- som: "$5M"
- fundingNeed: "$2M"
```

### 5. Створення власного проекту
```
Створи новий проект "Маркетингові звіти" для шаблонів маркетингової звітності
```

Після створення проекту можна завантажувати туди шаблони через API або додавати файли безпосередньо в папку `projects/marketyngovi-zvity/templates/`.

## API використання

### Отримання списку проектів
```bash
curl -X GET "http://localhost:3000/api/embedded-projects" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Завантаження файлу в проект
```bash
curl -X POST "http://localhost:3000/api/embedded-projects/it-zvity/files" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@my-template.md"
```

### Генерація звіту через API
```bash
curl -X POST "http://localhost:3000/api/reports/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "projectPath": "./projects/it-zvity",
    "templateId": "template-id",
    "variables": {
      "developer": "Іван Петров",
      "week": "1-7 лютого 2024"
    }
  }'
```

## Структура шаблону

Приклад простого шаблону:

```markdown
# Звіт: {{title}}

**Автор:** {{author}}
**Дата:** {{date|{{new Date().toLocaleDateString('uk-UA')}}}}

## Виконані завдання

{{#if tasks}}
{{#each tasks as task}}
- ✅ {{task.name}} ({{task.hours}} годин)
{{/each}}
{{#else}}
*Завдань не виконано*
{{/if}}

## Коментарі

{{comments|Додайте ваші коментарі тут}}
```

Цей шаблон використовує:
- Обов'язкові змінні: `title`, `author`
- Змінні з значеннями за замовчуванням: `date`, `comments`
- Умовну логіку: `{{#if tasks}}`
- Цикли: `{{#each tasks as task}}`