# Digital Office

**Digital Office** - це мультисервісна платформа з інтеграцією Anthropic Claude через Model Context Protocol (MCP), яка дозволяє легко додавати та управляти різними офісними сервісами.

## 🏗️ Архітектура

```
Digital Office Hub
├── ServiceRegistry - управління сервісами
├── DigitalOfficeHub - центральний MCP сервер  
└── Services/
    ├── Documentator - система документообігу
    ├── Calendar - календарний сервіс (planned)
    ├── Tasks - управління завданнями (planned)
    └── Communication - комунікації (planned)
```

## 🚀 Швидкий старт

### Встановлення

```bash
git clone <repository-url>
cd documentator
npm install
npm run build
```

### Запуск Digital Office Hub

```bash
# Запуск тільки MCP Hub
npm run start:hub

# Запуск тільки API сервера
npm run start:api

# Запуск обох (Hub + API)
npm run start:both

# Режим розробки
npm run dev
```

### Управління сервісами через CLI

```bash
# Показати всі сервіси
npm run cli services list

# Статус конкретного сервісу
npm run cli services status documentator

# Увімкнути/вимкнути сервіс
npm run cli services enable documentator
npm run cli services disable documentator

# Запустити/зупинити сервіс
npm run cli services start documentator
npm run cli services stop documentator

# Перевірка здоров'я
npm run cli services health

# Показати конфігурацію
npm run cli config show
```

## ⚙️ Конфігурація

Створіть файл `digital-office-config.json`:

```bash
npm run cli config init
```

Приклад конфігурації:

```json
{
  "services": [
    {
      "name": "documentator",
      "enabled": true,
      "config": {
        "projectsPath": "./projects",
        "templatesPath": "./templates",
        "outputPath": "./output"
      }
    }
  ],
  "globalConfig": {
    "logLevel": "info",
    "apiPort": 3000,
    "mcpServerName": "digital-office"
  }
}
```

## 🔧 Налаштування Claude Desktop

Додайте до вашого `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "digital-office": {
      "command": "node",
      "args": ["C:\\\\path\\\\to\\\\digital-office\\\\dist\\\\index-new.js", "hub"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

## 🛠️ MCP Команди Hub

Digital Office Hub надає наступні команди для Claude:

### Управління сервісами:
- `list_services` - показати всі сервіси та їх статуси
- `service_status <назва>` - детальний статус сервісу
- `enable_service <назва>` - увімкнути сервіс
- `disable_service <назва>` - вимкнути сервіс
- `start_service <назва>` - запустити сервіс
- `stop_service <назва>` - зупинити сервіс
- `health_check` - перевірка здоров'я всіх сервісів

### Команди Documentator сервісу:
- `documentator:analyze_project` - аналіз проекту
- `documentator:list_templates` - список шаблонів
- `documentator:generate_report` - генерація звіту
- `documentator:list_projects` - список проектів
- і інші команди Documentator з префіксом `documentator:`

## 📋 Використання в Claude

```
Покажи мені всі доступні сервіси в Digital Office

Увімкни сервіс documentator

Покажи статус сервісу documentator

Проаналізуй проект "my-reports" використовуючи documentator

Створи звіт з проекту "weekly-docs" з шаблоном "weekly-summary"
```

## 🔌 Додавання нових сервісів

### 1. Створіть новий сервіс

```typescript
// src/services/calendar/CalendarService.ts
import { BaseService } from '../../core/BaseService';

export class CalendarService extends BaseService {
  public metadata = {
    name: 'calendar',
    version: '1.0.0',
    description: 'Календарний сервіс для управління подіями',
    category: 'Продуктивність'
  };

  protected async onInitialize(): Promise<void> {
    // Ініціалізація сервісу
  }

  protected async onShutdown(): Promise<void> {
    // Очищення ресурсів
  }

  public getTools() {
    return [
      {
        name: 'create_event',
        description: 'Створити нову подію в календарі',
        inputSchema: { /* ... */ }
      }
      // інші інструменти
    ];
  }

  public async handleToolCall(toolName: string, args: any) {
    switch (toolName) {
      case 'create_event':
        return this.handleCreateEvent(args);
      // інші обробники
    }
  }
}
```

### 2. Зареєструйте сервіс

```typescript
// src/index-new.ts
import { CalendarService } from './services/calendar/CalendarService';

async function startHub() {
  const hub = new DigitalOfficeHub();
  
  // Реєструємо сервіси
  await hub.registerService(new DocumentatorService());
  await hub.registerService(new CalendarService()); // Новий сервіс
  
  await hub.start();
}
```

### 3. Оновіть конфігурацію

```json
{
  "services": [
    {
      "name": "calendar",
      "enabled": true,
      "config": {
        "defaultCalendar": "work",
        "timezone": "Europe/Kiev"
      }
    }
  ]
}
```

## 🔄 Міграція з Documentator

Старий Documentator продовжує працювати:

```bash
# Запуск старої версії
npm run start:legacy
npm run dev:legacy
```

Команди Claude залишаються без змін, але тепер доступні через новий Hub з префіксом `documentator:`.

## 📂 Структура проекту

```
digital-office/
├── src/
│   ├── core/                    # Основна логіка
│   │   ├── DigitalOfficeHub.ts  # Центральний MCP сервер
│   │   ├── ServiceRegistry.ts   # Реєстр сервісів
│   │   └── BaseService.ts       # Базовий клас сервісу
│   ├── services/                # Сервіси
│   │   └── documentator/        # Documentator сервіс
│   ├── cli/                     # CLI інструменти
│   ├── api/                     # REST API
│   ├── types/                   # TypeScript типи
│   └── utils/                   # Утиліти
├── digital-office-config.json   # Конфігурація сервісів
└── projects/                    # Папка проектів
```

## 🧪 Тестування

```bash
npm run test
npm run lint
npm run typecheck
```

## 📈 Моніторинг

```bash
# CLI моніторинг
npm run cli services list running
npm run cli services health

# Логи у консолі при запуску
npm run dev
```

## 🛣️ Roadmap

- ✅ Базова архітектура Digital Office
- ✅ Інтеграція Documentator як сервіс
- ✅ Система конфігурації сервісів
- ✅ CLI управління сервісами
- 🔄 Calendar сервіс
- 🔄 Tasks сервіс  
- 🔄 Communication сервіс
- 🔄 Веб-інтерфейс управління
- 🔄 Плагін система
- 🔄 Docker контейнеризація

## 📜 Ліцензія

MIT

## 🤝 Підтримка

Створюйте issues в GitHub репозиторії для звітування про баги або пропозицій нових функцій.