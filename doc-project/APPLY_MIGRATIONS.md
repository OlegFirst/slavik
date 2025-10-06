# 🗄️ Apply Migrations - Quick Guide

## Миграции для применения

### 1️⃣ Community Intelligence (Migration 037)

**Файл миграции:**
```
/Users/MD/AI-Platform-ISO/infrastructure/database/migrations_source/037_community_intelligence.sql
```

**Создаёт:**
- ✅ 6 таблиц (case_contributions, peer_reviews, user_reputation, etc)
- ✅ Row Level Security policies
- ✅ Indexes и constraints
- ✅ Triggers

---

## 🚀 Способы применения

### Способ 1: Bash скрипт (Fastest)

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/database

# Set DATABASE_URL (если ещё не установлен)
export DATABASE_URL='postgresql://postgres:[YOUR-PASSWORD]@[HOST]:5432/postgres'

# Apply migration
./apply_community_intelligence.sh
```

---

### Способ 2: Python скрипт

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/database

# Set DATABASE_URL (или создай .env файл)
export DATABASE_URL='postgresql://postgres:[YOUR-PASSWORD]@[HOST]:5432/postgres'

# Apply migration
python apply_community_migration.py
```

---

### Способ 3: Прямо через psql

```bash
cd /Users/MD/AI-Platform-ISO

# Set DATABASE_URL
export DATABASE_URL='postgresql://postgres:[YOUR-PASSWORD]@[HOST]:5432/postgres'

# Apply
psql $DATABASE_URL -f infrastructure/database/migrations_source/037_community_intelligence.sql
```

---

### Способ 4: Через Supabase CLI (если используешь Supabase)

```bash
cd /Users/MD/AI-Platform-ISO

# Login to Supabase
supabase login

# Link project (если ещё не linked)
supabase link --project-ref [YOUR-PROJECT-REF]

# Push migration
supabase db push

# ИЛИ apply specific migration
supabase db push --include-all --schema public
```

---

## 📋 Проверка после применения

### Проверить таблицы

```bash
psql $DATABASE_URL -c "\dt case_contributions"
psql $DATABASE_URL -c "\dt peer_reviews"
psql $DATABASE_URL -c "\dt user_reputation"
psql $DATABASE_URL -c "\dt community_annotations"
psql $DATABASE_URL -c "\dt synthesized_guidance"
```

### Проверить RLS policies

```bash
psql $DATABASE_URL -c "SELECT schemaname, tablename, policyname FROM pg_policies WHERE tablename LIKE '%contribution%' OR tablename LIKE '%reputation%';"
```

### Проверить indexes

```bash
psql $DATABASE_URL -c "SELECT tablename, indexname FROM pg_indexes WHERE tablename IN ('case_contributions', 'peer_reviews', 'user_reputation');"
```

---

## 🔧 Troubleshooting

### Ошибка: "relation already exists"

Таблица уже существует. Два варианта:

**1. Drop и пересоздать (ОСТОРОЖНО! Удалит данные):**
```sql
DROP TABLE IF EXISTS case_contributions CASCADE;
DROP TABLE IF EXISTS peer_reviews CASCADE;
DROP TABLE IF EXISTS user_reputation CASCADE;
DROP TABLE IF EXISTS reputation_transactions CASCADE;
DROP TABLE IF EXISTS community_annotations CASCADE;
DROP TABLE IF EXISTS synthesized_guidance CASCADE;

-- Затем apply migration снова
```

**2. Пропустить (если структура совпадает):**
Просто проигнорировать ошибку, если таблицы уже созданы правильно.

---

### Ошибка: "permission denied"

Убедитесь что пользователь имеет права CREATE:

```sql
GRANT CREATE ON DATABASE your_database TO your_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO your_user;
```

---

### Ошибка: "DATABASE_URL not set"

Установите переменную окружения:

```bash
# Для текущей сессии
export DATABASE_URL='postgresql://user:pass@host:5432/db'

# ИЛИ создайте .env файл
echo "DATABASE_URL=postgresql://user:pass@host:5432/db" > .env
```

---

## 📁 Созданные файлы для применения

1. **Bash скрипт:**
   ```
   /Users/MD/AI-Platform-ISO/infrastructure/database/apply_community_intelligence.sh
   ```

2. **Python скрипт:**
   ```
   /Users/MD/AI-Platform-ISO/infrastructure/database/apply_community_migration.py
   ```

3. **SQL миграция:**
   ```
   /Users/MD/AI-Platform-ISO/infrastructure/database/migrations_source/037_community_intelligence.sql
   ```

---

## ✅ После успешного применения

Вы увидите:

```
✅ Migration applied successfully!

Created tables:
  - case_contributions
  - peer_reviews
  - user_reputation
  - reputation_transactions
  - community_annotations
  - synthesized_guidance
```

**Модуль Community Intelligence готов к использованию!** 🎉

---

## 🎯 Следующие шаги

После применения миграции:

1. **Verify** - Проверьте таблицы
2. **Test** - Запустите тесты
   ```bash
   pytest intelligent-core/community_intelligence/tests/
   ```
3. **Integrate** - Начните использовать API
4. **Monitor** - Настройте мониторинг

---

**Готово! Миграция ждёт применения! 🚀**
