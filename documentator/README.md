# Documentator

Система автоматизації створення звітної документації з аналізом проектних папок та інтеграцією з Anthropic через MCP (Model Context Protocol).

## Функціональність

- 📁 **Вбудовані проекти**: Система управління проектами з папкою `projects/` - кожна підпапка є окремим проектом
- 📝 **Аналіз проектів**: Автоматичний пошук та аналіз шаблонів документації в проектних папках  
- 📊 **Генерація звітів**: Створення звітів на основі знайдених шаблонів з підтримкою змінних та логіки
- 🔌 **MCP інтеграція**: Підключення до Anthropic Claude через Model Context Protocol з 8 командами
- 🔐 **Система авторизації**: JWT authentication з ролями користувачів та API ключами
- 🌐 **REST API**: Повноцінний API для управління проектами, шаблонами та звітами
- 📤 **Завантаження файлів**: Можливість завантажувати шаблони та документи через API
- 🎯 **Приклади проектів**: Готові проекти з шаблонами для IT звітів, бізнес-планів та технічної документації

## Встановлення

### Передумови

- Node.js 18+
- npm або yarn

### Кроки встановлення

1. **Клонуйте репозиторій**
   ```bash
   git clone <repository-url>
   cd documentator
   ```

2. **Встановіть залежності**
   ```bash
   npm install
   ```

3. **Налаштуйте середовище**
   ```bash
   cp .env.example .env
   # Відредагуйте .env файл під ваші потреби
   ```

4. **Скомпілюйте проект**
   ```bash
   npm run build
   ```

## Використання

### Запуск MCP сервера

Для використання з Anthropic Claude:

```bash
npm start
# або
npm run dev
```

### Запуск API сервера

Для використання через REST API:

```bash
npm start api
```

### Запуск обох серверів

```bash
npm start both
```

## Налаштування MCP в Claude Desktop

Додайте до вашого `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "documentator": {
      "command": "node",
      "args": ["C:\\\\path\\\\to\\\\documentator\\\\dist\\\\index.js"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

## API Документація

### Аутентифікація

**POST** `/api/auth/login`
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**POST** `/api/auth/register`
```json
{
  "username": "user",
  "email": "user@example.com",
  "password": "password123"
}
```

### Аналіз проектів

**POST** `/api/projects/analyze`
```json
{
  "projectPath": "C:\\\\path\\\\to\\\\project",
  "forceRefresh": false
}
```

### Генерація звітів

**POST** `/api/reports/generate`
```json
{
  "projectPath": "C:\\\\path\\\\to\\\\project",
  "templateId": "template-id",
  "variables": {
    "projectName": "Мій проект",
    "author": "Іван Іванов",
    "date": "2024-01-01"
  },
  "format": "markdown"
}
```

## Формат шаблонів

### Базовий синтаксис змінних

```markdown
# {{title}}

Автор: {{author}}
Дата: {{date|2024-01-01}}

## Опис

{{description:string|Опис проекту}}
```

### Умовна логіка

```markdown
{{#if hasTests}}
## Тестування
Проект містить тести.
{{/if}}
```

### Цикли

```markdown
{{#each features as feature}}
- {{feature.name}}: {{feature.description}}
{{/each}}
```

## Структура проектів

Система працює з папкою `projects/`, де кожна підпапка є окремим проектом:

```
projects/
├── my-project/            # Ваш проект
│   ├── template1.md       # Шаблони в корені проекту  
│   ├── template2.md       # або
│   └── templates/         # в підпапці templates/
│       └── report.md
└── another-project/       # Інший проект
    └── weekly-report.md
```

**Як створити проект:**
1. Створіть папку в `projects/` з назвою вашого проекту
2. Додайте файли .md з шаблонами
3. Використайте MCP команди в Claude для роботи з проектом

## MCP Команди

Доступні команди для Anthropic Claude:

**Для зовнішніх проектів:**
- `analyze_project` - Аналіз проекту за повним шляхом
- `list_templates` - Отримання списку шаблонів проекту
- `get_template_variables` - Отримання змінних шаблону
- `generate_report` - Генерація звіту

**Для проектів з папки projects/:**
- `list_projects` - Список всіх проектів в папці projects/
- `analyze_project_by_id` - Аналіз проекту за ID (назвою папки)
- `generate_report_by_id` - Генерація звіту з проекту

### Приклади використання в Claude

**Робота з проектами з папки projects/:**
```
Покажи мені всі проекти в папці projects/

Проаналізуй проект "my-reports" та покажи доступні шаблони

Створи звіт з проекту "my-reports" використовуючи шаблон "weekly-report" з такими даними:
- title: "Тижневий звіт"
- author: "Іван Петров"
- week: "22-28 січня 2024"
```

**Робота з зовнішніми проектами:**
```
Проаналізуй проект в папці C:\\MyProject

Створи звіт на основі шаблону з папки C:\\MyProject з даними:
- title: "Звіт по проекту"
- author: "Команда розробки"
```

## Структура проекту

```
documentator/
├── src/
│   ├── api/          # REST API
│   ├── auth/         # Система авторизації
│   ├── core/         # Основна логіка
│   ├── mcp/          # MCP сервер
│   ├── types/        # TypeScript типи
│   └── utils/        # Утиліти
├── dist/             # Скомпільовані файли
├── data/             # Дані користувачів
└── tests/            # Тести
```

## Розробка

### Скрипти розробки

```bash
npm run dev          # Запуск в режимі розробки
npm run build        # Компіляція TypeScript
npm run test         # Запуск тестів
npm run lint         # Лінтинг коду
npm run typecheck    # Перевірка типів
```

### Додавання нових типів шаблонів

1. Розширте `ProjectAnalyzer.ts` для підтримки нового формату
2. Додайте логіку обробки в `ReportGenerator.ts`
3. Оновіть типи в `types/index.ts`

## Безпека

- JWT токени для API авторизації
- Bcrypt для хешування паролів
- Helmet для безпеки HTTP заголовків
- Валідація всіх вхідних даних
- Обмеження розміру файлів

## Логування

Логи зберігаються у файлі `logs/documentator.log` або виводяться в консоль залежно від налаштувань.

## Ліцензія

MIT

## Підтримка

Створюйте issues в GitHub репозиторії для звітування про баги або пропозицій нових функцій.