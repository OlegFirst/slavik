# 📧 Email Digest Agent

Автономний агент для щоденного моніторингу пошти, класифікації листів та створення дайджесту.

## 🎯 Основні можливості

1. **Щоденний моніторинг** - запускається автоматично о 16:00 по Київу
2. **Розумна класифікація** - визначає тип листа (важливий, розсилка, реклама, спам, тощо)
3. **Створення завдань в Asana** - автоматично створює task для важливих листів
4. **Збір підсумків зустрічей** - розпізнає листи від Otter, Read.ai, Fireflies та інших сервісів
5. **Консолідація підсумків** - збирає всі підсумки зустрічей в один MD файл
6. **Email дайджест** - відправляє красивий HTML дайджест на пошту

## 📋 Структура дайджесту

Щоденний дайджест містить:

- 📊 **Статистика** - скільки листів, розподіл за категоріями
- 💡 **Основні моменти** - короткий підсумок найважливіших подій
- ⚠️ **Термінові листи** - що потребує негайної уваги
- 📧 **Важливі листи** - топ важливих листів з запропонованими діями
- 📹 **Підсумки зустрічей** - консолідований файл з усіма зустрічами
- ✅ **Завдання** - список action items, створених в Asana

## 🔧 Налаштування

### 1. Email Credentials

Створіть файл `data/config/email-credentials.json`:

```json
{
  "provider": "gmail",
  "email": "your-email@gmail.com",
  "clientId": "your-google-client-id",
  "clientSecret": "your-google-client-secret",
  "refreshToken": "your-refresh-token"
}
```

**Для Gmail:**
1. Створіть проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Активуйте Gmail API
3. Створіть OAuth 2.0 credentials
4. Отримайте refresh token

**Для Outlook:**
```json
{
  "provider": "outlook",
  "email": "your-email@outlook.com",
  "tenantId": "your-tenant-id",
  "clientId": "your-client-id",
  "clientSecret": "your-client-secret"
}
```

**Для IMAP:**
```json
{
  "provider": "imap",
  "email": "your-email@domain.com",
  "host": "imap.domain.com",
  "port": 993,
  "secure": true,
  "username": "your-username",
  "password": "your-password"
}
```

### 2. Конфігурація агента

Відредагуйте `agent.json`:

```json
{
  "settings": {
    "lookbackHours": 24,
    "digest": {
      "sendTo": "your-email@example.com"
    },
    "filters": {
      "prioritySenders": ["boss@company.com", "client@important.com"],
      "excludeSenders": ["spam@spam.com"]
    }
  }
}
```

### 3. Asana Integration

Налаштуйте IntegrationService в `data/integrations/config.json`:

```json
{
  "taskManagement": {
    "provider": "asana",
    "defaultProject": "Email Tasks",
    "defaultAssignee": "me@company.com"
  }
}
```

## 🚀 Використання

### Автоматичний запуск

Агент запускається автоматично о 16:00 щодня (за київським часом).

### Ручний запуск

Через MCP tools в Claude Desktop:

```
Запусти email digest agent вручну
```

Або через API:

```bash
curl -X POST http://localhost:3000/api/agents/email-digest/execute
```

### Зміна розкладу

В `agent.json` змініть `cronExpression`:

```json
{
  "schedule": {
    "cronExpression": "0 9 * * *"  // 9:00 ранку
  }
}
```

Формат cron:
- `0 16 * * *` - щодня о 16:00
- `0 9,17 * * 1-5` - о 9:00 та 17:00 по робочих днях
- `0 18 * * 5` - щоп'ятниці о 18:00

## 📁 Структура файлів

```
data/agents/email-digest/
├── digests/
│   ├── digest-2024-01-15.json    # JSON дайджест
│   └── digest-2024-01-15.html    # HTML версія
├── meeting-summaries/
│   └── meeting-summaries-2024-01-15.md  # Зведені підсумки
└── attachments/
```

## 🔍 Класифікація листів

### Категорії

- **important** - Важливі робочі листи
- **newsletter** - Розсилки, новини
- **advertisement** - Реклама, промо
- **spam** - Небажана пошта
- **meeting_summary** - Підсумки від Otter, Read.ai, тощо
- **notification** - Сповіщення від систем (GitHub, Jira)
- **personal** - Особисті листи
- **automated** - Автоматичні повідомлення

### Пріоритети

- **urgent** 🔴 - Потребує реакції сьогодні
- **high** 🟠 - Важливо, 1-2 дні
- **medium** 🔵 - Стандартно, до тижня
- **low** ⚪ - Низький пріоритет

## 🤖 Підтримувані сервіси зустрічей

- [Otter.ai](https://otter.ai) - транскрипція зустрічей
- [Read.ai](https://read.ai) - AI підсумки зустрічей
- [Fireflies.ai](https://fireflies.ai) - автоматичні нотатки
- [tldv.io](https://tldv.io) - запис та підсумки
- [Fathom](https://fathom.video) - безкоштовний AI асистент

Агент автоматично розпізнає листи від цих сервісів та збирає їх в окремий файл.

## 📊 Приклад дайджесту

```
ЩОДЕННИЙ ДАЙДЖЕСТ ПОШТИ
15 січня 2024

СТАТИСТИКА:
✉️ Всього листів: 45
⚠️ Важливих: 8
📰 Розсилок: 20
🔔 Сповіщень: 12
👤 Особистих: 5
📹 Підсумків зустрічей: 3

ОСНОВНІ МОМЕНТИ:
> Отримано запит від клієнта X щодо термінів - потребує відповіді сьогодні
> 3 термінових листи від команди про дедлайни проекту
> Підсумки 3 зустрічей зібрано в окремому файлі
> Створено 5 завдань в Asana

ВАЖЛИВІ ЛИСТИ:
[URGENT] Запит звіту до кінця дня
  Від: boss@company.com
  💡 Дія: Підготувати звіт до 18:00

[HIGH] Питання від клієнта
  Від: client@important.com
  💡 Дія: Відповісти протягом доби
```

## 🔐 Безпека

- ✅ Credentials зберігаються локально в `data/config/`
- ✅ Не передаються третім особам
- ✅ OAuth2 для Gmail/Outlook
- ✅ Підтримка App-specific passwords
- ⚠️ НЕ комітьте credentials в git!

## 🐛 Troubleshooting

### Агент не запускається

Перевірте:
1. `agent.json` - `enabled: true`
2. Email credentials налаштовані
3. Логи в `data/agents/email-digest/logs/`

### Листи не класифікуються

- Перевірте що є доступ до пошти
- Переконайтесь що `lookbackHours` правильно налаштований

### Завдання не створюються в Asana

- Перевірте конфігурацію IntegrationService
- Переконайтесь що Asana MCP сервер підключений
- Перевірте `taskCreation.enabled: true`

### Дайджест не відправляється

- Поки що HTML зберігається локально
- Повна інтеграція з email буде додана в наступній версії

## 📝 TODO

- [ ] Інтеграція з Gmail API для реального fetch
- [ ] Інтеграція з Outlook API
- [ ] Підтримка IMAP
- [ ] Відправка email через MCP email server
- [ ] AI класифікація через Claude API
- [ ] Витягування action items через Claude
- [ ] Фільтрація за sentiment analysis
- [ ] Веб інтерфейс для перегляду історії дайджестів

## 🤝 Contribution

Якщо знайшли баг або маєте ідею покращення - створіть issue або PR!

## 📄 Ліцензія

MIT
