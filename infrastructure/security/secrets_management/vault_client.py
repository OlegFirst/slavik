"""
Supabase Vault Client
Централизованный клиент для работы с секретами из Supabase Vault
"""

import psycopg2
from functools import lru_cache
import os
import logging
from typing import Optional
from urllib.parse import urlparse, unquote

logger = logging.getLogger(__name__)

class SupabaseVaultClient:
    """Клиент для Supabase Vault с кэшированием (использует прямой PostgreSQL доступ)"""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")

        if not self.database_url:
            raise ValueError("DATABASE_URL must be set in environment")

        # Parse DATABASE_URL
        parsed = urlparse(self.database_url)
        self.conn_params = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:],  # Remove leading /
            'user': parsed.username,
            'password': unquote(parsed.password) if parsed.password else None,  # Decode URL-encoded password
            'sslmode': 'require'  # Fix SASL authentication issue with Supabase pooler
        }

        logger.info("✅ Supabase Vault Client initialized")

    def _get_connection(self):
        """Создать подключение к БД"""
        return psycopg2.connect(**self.conn_params)

    @lru_cache(maxsize=100)
    def get_secret(self, secret_name: str) -> str:
        """
        Получить секрет из Vault с кэшированием

        Args:
            secret_name: Имя секрета в Vault (например 'jwt-secret')

        Returns:
            str: Значение секрета

        Raises:
            ValueError: Если секрет не найден
            Exception: При других ошибках
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()

            # Вызываем функцию get_secret
            cur.execute("SELECT public.get_secret(%s)", (secret_name,))
            result = cur.fetchone()

            cur.close()
            conn.close()

            if not result or not result[0]:
                raise ValueError(f"Secret '{secret_name}' not found in Vault")

            logger.debug(f"✅ Retrieved secret: {secret_name}")
            return result[0]

        except Exception as e:
            logger.error(f"❌ Failed to retrieve secret '{secret_name}': {e}")
            raise

    def rotate_secret(self, secret_name: str, new_value: str) -> bool:
        """
        Ротация секрета (обновление значения)

        Args:
            secret_name: Имя секрета
            new_value: Новое значение

        Returns:
            bool: True если успешно
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()

            # Найти ID секрета
            cur.execute(
                "SELECT id FROM vault.secrets WHERE name = %s",
                (secret_name,)
            )
            result = cur.fetchone()

            if not result:
                raise ValueError(f"Secret '{secret_name}' not found")

            secret_id = result[0]

            # Обновить через vault.update_secret
            cur.execute(
                "SELECT vault.update_secret(%s, %s)",
                (secret_id, new_value)
            )

            conn.commit()
            cur.close()
            conn.close()

            # Очистить кэш
            self.get_secret.cache_clear()

            logger.warning(f"🔄 Secret rotated: {secret_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to rotate secret '{secret_name}': {e}")
            raise

    def list_secrets(self) -> list:
        """
        Получить список всех секретов (без значений)

        Returns:
            list: Список словарей с метаданными секретов
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT id, name, description, created_at
                FROM vault.secrets
                ORDER BY created_at DESC
            """)

            secrets = []
            for row in cur.fetchall():
                secrets.append({
                    'id': str(row[0]),
                    'name': row[1],
                    'description': row[2],
                    'created_at': row[3].isoformat() if row[3] else None
                })

            cur.close()
            conn.close()

            return secrets

        except Exception as e:
            logger.error(f"❌ Failed to list secrets: {e}")
            raise


# Singleton instance
_vault_instance: Optional[SupabaseVaultClient] = None

def get_vault_client() -> SupabaseVaultClient:
    """Получить singleton instance Vault client"""
    global _vault_instance
    if _vault_instance is None:
        _vault_instance = SupabaseVaultClient()
    return _vault_instance


# Convenience function
def get_secret(secret_name: str) -> str:
    """
    Удобная функция для получения секрета

    Usage:
        from infrastructure.security.secrets_management.vault_client import get_secret

        JWT_SECRET = get_secret('jwt-secret')
        ANTHROPIC_API_KEY = get_secret('anthropic-api-key')
    """
    vault = get_vault_client()
    return vault.get_secret(secret_name)


if __name__ == "__main__":
    # Тестирование
    logging.basicConfig(level=logging.INFO)

    vault = get_vault_client()

    # Список секретов
    secrets = vault.list_secrets()
    print(f"\n📋 Available secrets: {len(secrets)}")
    for secret in secrets:
        print(f"  - {secret['name']}: {secret['description']}")

    # Тест чтения
    print(f"\n🔑 Testing secret retrieval...")
    jwt_secret = vault.get_secret('jwt-secret')
    print(f"  JWT Secret length: {len(jwt_secret)} chars")

    print(f"\n✅ Vault client test completed!")
