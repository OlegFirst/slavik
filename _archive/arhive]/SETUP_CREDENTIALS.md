# Setup Credentials - Пошаговая инструкция

## Что уже настроено ✅

1. ✅ **Supabase** - PostgreSQL database
2. ✅ **ngrok** - Tunneling token

## Что НУЖНО добавить в `.env`

### 1. 🔴 Redis Password (КРИТИЧНО)

**Где взять:**
1. Зайди на https://redis.cloud
2. Databases → `redis-10023` (твой database)
3. Configuration → Default user password
4. Скопируй password

**Что обновить в `.env`:**
```bash
REDIS_PASSWORD=YOUR_REDIS_PASSWORD_HERE   # ← Замени на реальный пароль
```

---

### 2. 🔴 OpenAI API Key (КРИТИЧНО для AI)

**Где взять:**
1. Зайди на https://platform.openai.com/api-keys
2. Create new secret key
3. ⚠️ Скопируй СРАЗУ (показывается только раз!)

**Что обновить в `.env`:**
```bash
OPENAI_API_KEY=sk-...   # ← Вставь свой ключ
```

---

### 3. 🟡 Anthropic API Key (ОПЦИОНАЛЬНО)

Если хочешь использовать Claude вместо GPT-4:

**Где взять:**
1. Зайди на https://console.anthropic.com/settings/keys
2. Create Key
3. Скопируй

**Что обновить в `.env`:**
```bash
ANTHROPIC_API_KEY=sk-ant-...   # ← Вставь если нужен Claude
```

---

### 4. 🟡 Resend API Key (ОПЦИОНАЛЬНО - для email)

Для отправки email уведомлений:

**Где взять:**
1. Зайди на https://resend.com/api-keys
2. Create API Key
3. Скопируй

**Что обновить в `.env`:**
```bash
RESEND_API_KEY=re_...   # ← Вставь если нужны email уведомления
```

---

## Что НЕ НУЖНО (пока)

- ❌ **MongoDB** - не используем (есть PostgreSQL)
- ❌ **Sentry** - добавим позже для error tracking
- ❌ **Cloudflare Tunnel** - есть ngrok

---

## Проверка после добавления credentials

После того как добавишь **Redis Password** и **OpenAI API Key**, запусти:

```bash
cd /Users/MD/AI-Platform-ISO
python3 infrastructure/test_connections.py
```

Должно показать:
```
✅ Supabase: PASSED
✅ Redis: PASSED
```

---

## Если не работает

### Supabase не подключается
- Проверь что `DATABASE_URL` правильный
- В Supabase Dashboard → Settings → Database проверь Connection String

### Redis не подключается
- Проверь пароль в Redis Cloud dashboard
- Проверь что endpoint правильный: `redis-10023.c8.us-east-1-4.ec2.redns.redis-cloud.com:10023`

### OpenAI не работает
- Проверь что API key начинается с `sk-`
- Проверь что у тебя есть credits на аккаунте
- В OpenAI Dashboard → Usage проверь лимиты

---

## Следующие шаги (после настройки credentials)

1. ✅ Протестировать подключения
2. ✅ Применить SQL migrations к Supabase
3. ✅ Создать тестовые данные
4. ✅ Запустить первый сервис (Participants)

---

**Готов?** Добавь Redis Password и OpenAI API Key, и я запущу тесты!
