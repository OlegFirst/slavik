# Настройка Claude Desktop для Digital Twin

## Быстрая настройка (2 минуты)

### Шаг 1: Создайте файл конфигурации

Откройте Terminal и выполните:

```bash
# Создайте директорию для конфигурации (если её нет)
mkdir -p ~/Library/Application\ Support/Claude/

# Создайте конфигурационный файл
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "digital-twin": {
      "command": "node",
      "args": [
        "/Users/maksymdemchenko/claude_workspace_files/Development/digital-twin-standalone/mcp-server/digital-twin-mcp-server.js"
      ],
      "env": {
        "SIMPY_ADAPTER_URL": "http://localhost:7001/run",
        "MESA_ADAPTER_URL": "http://localhost:7002/run",
        "EPINOW2_ADAPTER_URL": "http://localhost:7003/run",
        "ANYLOGIC_ADAPTER_URL": "http://localhost:7004/run",
        "SUPABASE_URL": "YOUR_SUPABASE_URL",
        "SUPABASE_ANON_KEY": "YOUR_SUPABASE_KEY"
      }
    }
  }
}
EOF
```

### Шаг 2: Перезапустите Claude Desktop

1. Закройте Claude Desktop полностью (Cmd+Q)
2. Откройте Claude Desktop снова
3. В нижней части интерфейса появится иконка MCP 🔌

### Шаг 3: Проверьте подключение

В чате Claude напишите:
```
Покажи все доступные инструменты Digital Twin
```

Claude должен ответить списком из 8 инструментов.

## Для коллег (упрощенная установка)

### Вариант 1: NPX установка (рекомендуется)

```bash
# Одна команда для полной настройки
npx @nash4/digital-twin-mcp setup

# Выберите режим:
# - Quick Setup (Demo Mode) - для тестирования
# - Organization Setup - для реальной организации
# - Custom Configuration - для своих настроек
```

### Вариант 2: Ручная настройка

```bash
# 1. Клонируйте проект
git clone https://github.com/nash4/digital-twin-standalone.git
cd digital-twin-standalone

# 2. Установите зависимости
npm install

# 3. Запустите сервер
npm start

# 4. В другом терминале настройте MCP
cd mcp-connector
npm install
npm run setup
```

## Примеры команд в Claude Desktop

### Управление организациями
```
"Создай цифрового двойника для благотворительного фонда 'Надежда' с бюджетом $5M"
"Покажи все организации"
"Проанализируй эффективность организации"
```

### Запуск симуляций (30 экспериментов)
```
"Запусти симуляцию кризиса с потерей 30% финансирования"
"Используй SimPy для оптимизации очередей доноров"
"Запусти гибридную симуляцию AnyLogic для всей организации"
"Оптимизируй бюджет с помощью Theory of Change"
```

### Анализ и отчеты
```
"Сгенерируй Impact Passport для организации"
"Спрогнозируй тренды на следующий квартал"
"Проанализируй здоровье организации"
```

### Демо режим
```
"Запусти демо с Hope Foundation International"
"Покажи все 30 возможностей платформы"
```

## Структура проекта для MCP

```
digital-twin-standalone/
├── mcp-server/
│   └── digital-twin-mcp-server.js   # Основной MCP сервер (1185 строк)
├── mcp-connector/
│   ├── package.json                 # NPM пакет для распространения
│   ├── index.js                     # Упрощенный коннектор
│   ├── setup.js                     # Мастер установки
│   └── README.md                    # Документация
└── web-interface/
    └── static/
        └── auth.html                # Страница регистрации
```

## Возможности после подключения

### ✅ Полный функционал через чат:
- **8 MCP инструментов** для управления платформой
- **30 симуляционных экспериментов**
- **4 ресурса** с документацией и шаблонами
- **3 промпта** для частых задач

### 📊 Что можно делать:
1. Создавать и управлять цифровыми двойниками
2. Запускать любой из 30 экспериментов
3. Анализировать организации с помощью AI
4. Прогнозировать тренды и оптимизировать параметры
5. Генерировать отчеты и Impact Passport

## Troubleshooting

### MCP не появляется в Claude Desktop
```bash
# Проверьте конфигурацию
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Проверьте путь к серверу
ls -la /Users/maksymdemchenko/claude_workspace_files/Development/digital-twin-standalone/mcp-server/digital-twin-mcp-server.js

# Перезапустите Claude Desktop
```

### Ошибка "Server not initialized"
```bash
# Запустите основной сервер
cd /Users/maksymdemchenko/claude_workspace_files/Development/digital-twin-standalone
npm start
```

### Проверка работы MCP
В Claude Desktop напишите:
```
list_twins
```

Если все работает, Claude выполнит команду и покажет список организаций.

## Для разработчиков

### Добавление нового инструмента в MCP

Отредактируйте `/mcp-server/digital-twin-mcp-server.js`:

```javascript
// В методе setupHandlers(), строка ~125
tools: [
    // ... существующие инструменты
    {
        name: 'your_new_tool',
        description: 'Description',
        inputSchema: {
            type: 'object',
            properties: {
                // параметры
            }
        }
    }
]
```

### Логи MCP сервера
```bash
# MCP логи идут в stderr
node mcp-server/digital-twin-mcp-server.js 2> mcp.log
```

## Контакты

- **Email**: maksym@nash4.org
- **GitHub**: https://github.com/nash4/digital-twin-standalone
- **Документация**: https://nash4.digital-twin.org

---

**Статус**: ✅ Готово к использованию
**Версия**: 1.0.0
**Дата**: 16 января 2025