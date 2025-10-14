"""
Database Initialization Script for KQM

Создаёт все необходимые таблицы в PostgreSQL
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ psycopg2 не установлен. Установите: pip3 install psycopg2-binary")
    sys.exit(1)

from config.settings import settings


def init_database():
    """Инициализация базы данных"""

    print("=" * 60)
    print("🗄️  KQM DATABASE INITIALIZATION")
    print("=" * 60)

    # Parse DATABASE_URL
    db_url = settings.DATABASE_URL
    print(f"\n📍 Database URL: {db_url[:50]}...")

    try:
        # Connect to PostgreSQL
        print("\n🔌 Подключение к PostgreSQL...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()

        print("✅ Подключение установлено")

        # Read schema file
        schema_file = Path(__file__).parent / "schema.sql"
        print(f"\n📄 Читаем schema: {schema_file}")

        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Execute schema
        print("\n🔨 Создаём таблицы...")
        cursor.execute(schema_sql)

        print("✅ Таблицы созданы")

        # Verify tables
        print("\n📊 Проверка созданных таблиц...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name LIKE 'kqm_%'
            ORDER BY table_name
        """)

        tables = cursor.fetchall()

        print(f"\n✅ Создано {len(tables)} таблиц:")
        for table in tables:
            print(f"   - {table[0]}")

        # Count rows
        print("\n📊 Статистика:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   {table_name}: {count} строк")

        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("✅ БАЗА ДАННЫХ ГОТОВА!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
