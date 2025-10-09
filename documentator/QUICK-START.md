# 🚀 Digital Office - Швидкий старт

## Для користувачів (найпростіший спосіб)

### Крок 1: Подвійний клік на `INSTALL.bat`
Інсталятор автоматично:
- ✅ Встановить Digital Office у `%LOCALAPPDATA%\DigitalOffice`
- ✅ Встановить всі залежності
- ✅ Зберає проект
- ✅ Створить ярлики на робочому столі

### Крок 2: Налаштування
Подвійний клік на ярлик **"Digital Office Setup"** на робочому столі

Оберіть що налаштовуємо:
- ☑️ Email (Gmail/Outlook/IMAP)
- ☑️ Asana

Слідуйте інструкціям на екрані - wizard все покаже!

### Крок 3: Запуск
Подвійний клік на ярлик **"Digital Office Hub"** на робочому столі

**Готово!** 🎉

---

## Що робить Email Digest Agent?

Автоматично **щодня о 16:00** по Києву:

📧 **Аналізує пошту:**
- Важливі листи
- Розсилки (newsletters)
- Реклама
- Спам
- Підсумки зустрічей
- Сповіщення

📋 **Створює завдання в Asana:**
- Автоматично для важливих листів
- З пріоритетом та дедлайном
- З посиланням на оригінальний лист

📊 **Надсилає щоденний дайджест:**
- Статистика по категоріях
- Найважливіші листи
- Рекомендовані дії

📄 **Збирає підсумки зустрічей:**
- Otter.ai
- Read.ai
- Fireflies.ai
- Fathom
- Всі підсумки в одному MD файлі

---

## Системні вимоги

- **Node.js 18+** - [Завантажити](https://nodejs.org/)
- **Windows 10/11** (64-bit)
- **4 GB RAM**
- **500 MB** вільного місця

---

## Портативна версія (для розповсюдження)

### Для розробників:

Створити ZIP для розповсюдження:
```
Подвійний клік на CREATE-PORTABLE.bat
```

Отримаєте: `DigitalOffice-Portable-v1.0.zip`

### Для користувачів портативної версії:

1. Розпакуйте ZIP в будь-яку папку
2. Подвійний клік на `FIRST-RUN.bat`
3. Подвійний клік на `Setup-Wizard.bat`
4. Подвійний клік на `Start-Hub.bat`

---

## Файли та папки

### Після встановлення:

```
%LOCALAPPDATA%\DigitalOffice\
├── data\
│   ├── config\
│   │   └── email-credentials.json       ← Ваші email налаштування
│   ├── integrations\
│   │   └── config.json                  ← Asana налаштування
│   └── agents\
│       └── email-digest\
│           ├── digests\                 ← Щоденні дайджести
│           └── meeting-summaries\       ← Підсумки зустрічей
├── dist\                                ← Зібраний код
└── Setup-Wizard.bat                     ← Повторне налаштування
```

### На робочому столі:

- **Digital Office Setup.lnk** - Налаштування
- **Digital Office Hub.lnk** - Запуск

---

## Налаштування Email

### Gmail:
1. Google Cloud Console → Create Project
2. Enable Gmail API
3. Create OAuth Client (Desktop app)
4. Get Client ID + Secret
5. OAuth Playground → Get Refresh Token
6. Вставте у Setup Wizard ✅

### Outlook:
1. Azure Portal → Register App
2. Get Tenant ID + Client ID
3. Create Client Secret
4. Add Mail.Read permission
5. Вставте у Setup Wizard ✅

### IMAP (будь-який провайдер):
1. Host: `imap.gmail.com` (або ваш)
2. Port: `993`
3. Email + App Password
4. Вставте у Setup Wizard ✅

---

## Налаштування Asana

1. **Personal Access Token:**
   - https://app.asana.com/
   - My Settings → Apps → Create token
   - Скопіюйте токен

2. **Workspace GID:**
   - URL: `https://app.asana.com/0/WORKSPACE_GID/...`
   - Скопіюйте довге число після `0/`

3. **Project GID:**
   - URL: `https://app.asana.com/0/PROJECT_GID/...`
   - Скопіюйте друге довге число

4. **Вставте у Setup Wizard** ✅

---

## Зміна налаштувань

Подвійний клік на **"Digital Office Setup"** на робочому столі

або

```
cd %LOCALAPPDATA%\DigitalOffice
node dist\cli\setup-wizard.js
```

---

## Видалення

1. Видаліть папку `%LOCALAPPDATA%\DigitalOffice`
2. Видаліть ярлики з робочого столу

або

```
rmdir /s /q "%LOCALAPPDATA%\DigitalOffice"
```

---

## Питання?

📖 Детальна документація: `INSTALLATION.md`

💡 Не працює? Перевірте:
- Чи встановлено Node.js?
- Чи правильні email credentials?
- Чи запущений Digital Office Hub?

---

**Digital Office v1.0**
*Ваш автоматизований офісний помічник* 🤖
