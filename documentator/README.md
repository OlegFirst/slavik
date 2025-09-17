# Digital Office Hub

Потужна платформа для автоматизації бізнес-процесів та управління проектами з інтелектуальними AI-агентами.

## Основні можливості

- **Інтелектуальні агенти** - автоматизація задач через спеціалізовані AI-агенти
- **API сервер** - RESTful API для інтеграції з зовнішніми системами
- **MCP інтеграція** - підтримка Model Context Protocol для роботи з AI моделями
- **Аутентифікація** - JWT-based система з ролями (admin/user)
- **Генерація контенту** - автоматичне створення документації та текстів
- **Web scraping** - збір та аналіз даних з веб-ресурсів

## Швидкий старт

### Вимоги

- Node.js 18+
- npm або yarn

### Встановлення

```bash
# Клонувати репозиторій
git clone <your-repo-url>
cd documentator

# Встановити залежності
npm install

# Створити папку для даних
mkdir data
```

### Налаштування

1. Створіть файл `.env`:

```env
# JWT секрет для аутентифікації
JWT_SECRET=your-secret-key-change-in-production

# Порт API сервера
API_PORT=4000

# Порт MCP сервера
MCP_PORT=3000
```

2. За замовчуванням створюється адміністратор:
   - Логін: `admin`
   - Пароль: `admin123`

### Запуск

```bash
# Збірка TypeScript
npm run build

# Запуск Digital Office Hub (API + MCP сервери)
npm start

# Або для розробки з автоматичною перезбіркою
npm run dev
```

## API Endpoints

### Аутентифікація

- `POST /auth/login` - вхід (username, password)
- `POST /auth/register` - реєстрація нового користувача
- `GET /auth/me` - профіль поточного користувача [потребує токен]
- `POST /auth/change-password` - зміна пароля [потребує токен]
- `POST /auth/api-key` - генерація API ключа [потребує токен]
- `PUT /auth/users/:userId/role` - зміна ролі користувача [тільки admin]

### Агенти

- `GET /agents` - список доступних агентів
- `GET /agents/:id` - інформація про агента
- `POST /agents/:id/execute` - виконати задачу агента [потребує токен]
- `GET /agents/:id/status/:taskId` - статус виконання задачі

### Документи

- `POST /documents/generate` - генерація документа за шаблоном [потребує токен]
- `GET /documents/templates` - список доступних шаблонів

### Проекти

- `GET /projects` - список проектів [потребує токен]
- `POST /projects` - створити проект [потребує токен]
- `GET /projects/:id` - деталі проекту [потребує токен]
- `PUT /projects/:id` - оновити проект [потребує токен]

## Структура проекту

```
documentator/
├── src/
│   ├── agents/           # Інтелектуальні агенти
│   │   ├── automation/   # Агенти автоматизації
│   │   └── content/      # Агенти генерації контенту
│   ├── api/              # API сервер та маршрути
│   │   ├── routes/       # Express маршрути
│   │   └── server.ts     # Налаштування сервера
│   ├── auth/             # Система аутентифікації
│   │   ├── AuthService.ts
│   │   └── middleware.ts
│   ├── core/             # Основні модулі системи
│   │   ├── DigitalOfficeHub.ts  # Головний хаб
│   │   ├── BaseAgent.ts         # Базовий клас агентів
│   │   └── EventBus.ts          # Система подій
│   ├── services/         # Бізнес-логіка
│   ├── templates/        # Шаблони документів
│   └── types/            # TypeScript типи
├── data/                 # Дані додатку (користувачі, проекти)
├── dist/                 # Скомпільований код
└── tests/                # Тести
```

## Архітектура агентів

Система підтримує інтелектуальні агенти через модульну архітектуру. Агенти можуть бути додані в категорії:

### Категорії агентів
- **Automation** - агенти автоматизації
- **Analytics** - агенти аналізу даних
- **Integration** - агенти інтеграції
- **Monitoring** - агенти моніторингу
- **Custom** - кастомні агенти

### Поточний стан
Система готова до додавання нових агентів. Структура директорій підготовлена для розширення функціональності.

## Розробка

### Додавання нового агента

1. Створіть папку агента в `src/agents/<category>/<agent-name>/`
2. Додайте файли:
   - `agent.json` - конфігурація агента
   - `index.ts` - логіка агента (extends BaseAgent)
3. Агент автоматично буде доступний через API

### Структура агента

```typescript
// src/agents/automation/my-agent/index.ts
import { BaseAgent } from '../../../core/BaseAgent';

export class MyAgent extends BaseAgent {
  async execute(task: any): Promise<any> {
    // Логіка виконання задачі
    return result;
  }
}
```

```json
// src/agents/automation/my-agent/agent.json
{
  "id": "my-agent",
  "name": "My Agent",
  "description": "Опис агента",
  "category": "automation",
  "capabilities": ["task1", "task2"]
}
```

## MCP Команди

Доступні команди для Claude Desktop:

- `analyze_project` - Аналіз проекту
- `list_templates` - Список шаблонів
- `get_template_variables` - Отримання змінних шаблону
- `generate_report` - Генерація звіту
- `list_projects` - Список проектів
- `analyze_project_by_id` - Аналіз проекту за ID
- `generate_report_by_id` - Генерація звіту за ID

## Налаштування MCP в Claude Desktop

Додайте до `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "digital-office": {
      "command": "node",
      "args": ["/absolute/path/to/your/documentator/dist/index-new.js"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

**Для Windows:**
```json
{
  "mcpServers": {
    "digital-office": {
      "command": "node",
      "args": ["C:\\Users\\YourUsername\\documentator\\dist\\index-new.js"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

**Для macOS/Linux:**
```json
{
  "mcpServers": {
    "digital-office": {
      "command": "node",
      "args": ["/home/username/documentator/dist/index-new.js"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

## Скрипти

- `npm start` - запуск продакшн версії
- `npm run dev` - запуск в режимі розробки
- `npm run build` - збірка TypeScript
- `npm test` - запуск тестів
- `npm run lint` - перевірка коду ESLint
- `npm run format` - форматування коду Prettier
- `npm run typecheck` - перевірка типів TypeScript

## Безпека

⚠️ **Важливо для продакшн:**

1. Змініть `JWT_SECRET` на унікальний ключ
2. Змініть пароль адміністратора після першого входу
3. Використовуйте HTTPS для API
4. Налаштуйте CORS для вашого домену
5. Регулярно оновлюйте залежності

## Логування

Логи зберігаються у файлі `logs/documentator.log` або виводяться в консоль залежно від налаштувань.

## Ліцензія

MIT

## Підтримка

Для питань та пропозицій створюйте issue на GitHub.