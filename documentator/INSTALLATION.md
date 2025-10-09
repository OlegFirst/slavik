# 🚀 Digital Office - Інструкція зі встановлення

## Швидке встановлення (рекомендовано)

### Варіант 1: Автоматичний інсталятор

1. **Подвійний клік на `INSTALL.bat`**
   - Інсталятор автоматично встановить Digital Office
   - Встановить всі залежності
   - Зберає проект
   - Створить ярлики на робочому столі

2. **Після встановлення:**
   - Подвійний клік на ярлик **"Digital Office Setup"** на робочому столі
   - Налаштуйте Email (Gmail/Outlook/IMAP)
   - Налаштуйте Asana
   - Готово!

3. **Запуск:**
   - Подвійний клік на ярлик **"Digital Office Hub"** на робочому столі

---

## Системні вимоги

- **Node.js 18+** ([Завантажити](https://nodejs.org/))
- **Windows 10/11** (64-bit)
- **4 GB RAM** (мінімум)
- **500 MB** вільного місця на диску

---

## Варіант 2: Ручне встановлення

Якщо автоматичний інсталятор не працює:

### Крок 1: Встановлення залежностей

```bash
npm install
```

### Крок 2: Збірка проекту

```bash
npm run build
```

### Крок 3: Налаштування

```bash
npm run setup
```

Оберіть:
- ✅ Email (Gmail/Outlook/IMAP)
- ✅ Asana

Слідуйте інструкціям на екрані.

### Крок 4: Запуск

```bash
npm run start:hub
```

---

## Що встановлюється?

### Папки:
- `%LOCALAPPDATA%\DigitalOffice\` - Основна папка програми
- `%LOCALAPPDATA%\DigitalOffice\data\` - Конфігурації та дані

### Ярлики на робочому столі:
- **Digital Office Setup** - Налаштування Email та Asana
- **Digital Office Hub** - Запуск основної програми

---

## Налаштування Email Digest Agent

Email Digest Agent автоматично:
- **Аналізує пошту** щодня о 16:00 по Києву
- **Класифікує листи**: важливі, розсилки, реклама, спам
- **Створює завдання в Asana** для важливих листів
- **Збирає підсумки зустрічей** з Otter.ai, Read.ai, Fireflies.ai
- **Надсилає щоденний дайджест** на пошту

### Підтримувані провайдери Email:

#### Gmail (OAuth2)
1. Google Cloud Console → Create OAuth Client
2. Enable Gmail API
3. Get Client ID, Secret, Refresh Token
4. Вставте у Setup Wizard

#### Outlook / Office 365
1. Azure Portal → Register App
2. Get Tenant ID, Client ID, Secret
3. Add Mail.Read permissions
4. Вставте у Setup Wizard

#### Інший провайдер (IMAP)
1. Отримайте IMAP host та port
2. Створіть App Password (якщо використовується 2FA)
3. Вставте у Setup Wizard

---

## Налаштування Asana

1. **Personal Access Token:**
   - https://app.asana.com/ → My Settings → Apps
   - Create new token
   - Скопіюйте токен

2. **Workspace GID:**
   - Відкрийте Asana у браузері
   - Перейдіть до Workspace
   - URL: `https://app.asana.com/0/WORKSPACE_GID/...`
   - WORKSPACE_GID - довге число після `0/`

3. **Project GID:**
   - Відкрийте проект в Asana
   - URL: `https://app.asana.com/0/PROJECT_GID/...`
   - PROJECT_GID - друге довге число

4. **Вставте у Setup Wizard**

---

## Запуск

### Через ярлик:
Подвійний клік на **"Digital Office Hub"** на робочому столі

### Через командний рядок:
```bash
cd %LOCALAPPDATA%\DigitalOffice
node dist\index-new.js hub
```

### Налаштування змінити:
Подвійний клік на **"Digital Office Setup"**

---

## Перевірка роботи Email Digest Agent

Після налаштування:
1. Email Digest Agent запуститься о **16:00 по Києву**
2. Перевірте файл `data/agents/email-digest/digests/`
3. Перевірте Asana - повинні з'явитися завдання
4. Перевірте пошту - повинен прийти дайджест

### Ручний запуск (для тестування):
```bash
# У Claude Desktop використайте MCP tool "trigger_digest"
```

---

## Видалення

### Автоматичне:
1. Видаліть папку `%LOCALAPPDATA%\DigitalOffice`
2. Видаліть ярлики з робочого столу

### Ручне:
```bash
rmdir /s /q "%LOCALAPPDATA%\DigitalOffice"
```

---

## Часті питання

**Q: Де зберігаються конфігурації?**
A: `%LOCALAPPDATA%\DigitalOffice\data\config\`

**Q: Як змінити час запуску Email Digest?**
A: Відредагуйте `src/agents/monitoring/email-digest/agent.json` → `schedule.cronExpression`

**Q: Чому не приходить дайджест?**
A: Перевірте:
- Email credentials у `data/config/email-credentials.json`
- Логи у `data/agents/email-digest/`
- Чи запущений Digital Office Hub

**Q: Як оновити програму?**
A: Запустіть `INSTALL.bat` знову - він перезапише файли

---

## Підтримка

- GitHub Issues: [Створити issue](https://github.com/anthropics/documentator/issues)
- Email: support@digital-office.local

---

## Ліцензія

MIT License

---

**Дякуємо що використовуєте Digital Office! 🎉**
