# NASH 4.0 Digital Twin MCP Connector

## Быстрая установка для Claude Desktop (1 команда!)

```bash
npx @nash4/digital-twin-mcp setup
```

Всё! Коннектор автоматически настроит Claude Desktop для работы с Digital Twin платформой.

## Что это?

MCP коннектор позволяет управлять Digital Twin платформой прямо из чата Claude Desktop:
- 30 симуляционных экспериментов
- Создание цифровых двойников организаций  
- AI-анализ и оптимизация
- Генерация Impact Passport

## Установка для коллег

### Вариант 1: Быстрый старт (Demo Mode)

```bash
# Одна команда - всё настроится автоматически
npx @nash4/digital-twin-mcp setup

# Выберите "Quick Setup (Demo Mode)"
# Перезапустите Claude Desktop
# Готово!
```

### Вариант 2: Для организации

```bash
# Запустите setup
npx @nash4/digital-twin-mcp setup

# Выберите "Organization Setup"
# Введите название организации
# Создайте учетную запись
# Готово!
```

### Вариант 3: Локальная установка

```bash
# Клонируйте репозиторий
git clone https://github.com/nash4/digital-twin-standalone.git
cd digital-twin-standalone/mcp-connector

# Установите зависимости
npm install

# Запустите настройку
npm run setup

# Запустите основной сервер (в другом терминале)
cd .. && npm start
```

## Использование в Claude Desktop

После установки просто пишите в чат:

### Демо команды
- "Покажи все 30 экспериментов"
- "Запусти демо с Hope Foundation"
- "Покажи возможности платформы"

### Работа с организацией
- "Создай цифровой двойник моей организации"
- "Запусти симуляцию кризиса"
- "Оптимизируй бюджет на следующий год"
- "Проанализируй эффективность программ"
- "Спрогнозируй поведение доноров"

### Эксперименты
- "Запусти SimPy для оптимизации очередей"
- "Используй Mesa для моделирования доноров"
- "Спрогнозируй спрос с EpiNow2"
- "Запусти гибридную симуляцию AnyLogic"

## Системные требования

- Claude Desktop (последняя версия)
- Node.js 18+ 
- 4GB RAM
- macOS, Windows или Linux

## Проверка установки

```bash
# Проверить статус
npx @nash4/digital-twin-mcp test

# Посмотреть конфигурацию
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json  # macOS
cat %APPDATA%\Claude\claude_desktop_config.json  # Windows
```

## Структура проекта

```
mcp-connector/
├── package.json          # NPM пакет
├── index.js             # Основной MCP сервер
├── setup.js             # Мастер установки
├── bin/
│   └── nash-digital-twin.js  # CLI команды
└── README.md            # Эта документация
```

## Возможности после подключения

### 4 внешних адаптера
1. **SimPy** - Дискретно-событийное моделирование
2. **Mesa** - Агентное моделирование
3. **EpiNow2** - Прогнозирование
4. **AnyLogic** - Гибридное моделирование с ML/AI

### 22 сценария Digital Twin
- Автоматизация процессов
- Антикризисное управление
- Расширение географии
- Цифровая трансформация
- И еще 18 сценариев...

### 4 внутренних движка
- Theory of Change оптимизация
- Capacity sweep анализ
- BCM outage симуляция
- Оптимизация бюджета

## Troubleshooting

### Claude Desktop не видит коннектор
1. Перезапустите Claude Desktop
2. Проверьте конфигурацию: `npx @nash4/digital-twin-mcp test`
3. Переустановите: `npx @nash4/digital-twin-mcp setup`

### Сервер не отвечает
1. Запустите локальный сервер: `npm start`
2. Проверьте порт 3000: `lsof -i :3000`
3. Используйте Demo Mode для тестирования

### Ошибка авторизации
1. Проверьте файл `~/.nash4/auth.json`
2. Перезапустите setup с новыми credentials
3. Используйте Demo Mode без авторизации

## Поддержка

- 📧 Email: support@nash4.org
- 📚 Docs: https://nash4.digital-twin.org
- 💬 Discord: https://discord.gg/nash4
- 🐛 Issues: https://github.com/nash4/digital-twin-mcp/issues

## Лицензия

MIT - свободное использование для НКО

---

**NASH 4.0** - Partnership Excellence in Digital Transformation