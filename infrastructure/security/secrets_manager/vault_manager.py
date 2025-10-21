"""
HashiCorp Vault Manager
Безопасное управление секретами, токенами, паролями

Features:
- Key-Value Secrets Engine (KV v2)
- Dynamic Secrets (database credentials)
- Encryption as a Service (transit engine)
- Token management
- Audit logging
- Auto-renewal of leases
"""

import os
import logging
from typing import Dict, Any, Optional, List
import hvac
from hvac.exceptions import InvalidPath, Forbidden, VaultError

logger = logging.getLogger(__name__)


class VaultManager:
    """
    HashiCorp Vault Manager для безопасного хранения секретов

    Usage:
        vault = VaultManager("http://localhost:8200", token="root-token")

        # Сохранить секрет
        vault.write_secret("database/postgres", {
            "username": "admin",
            "password": "super-secret"
        })

        # Получить секрет
        secret = vault.read_secret("database/postgres")
        print(secret["password"])

        # Зашифровать данные
        ciphertext = vault.encrypt("my-key", "sensitive data")
        plaintext = vault.decrypt("my-key", ciphertext)
    """

    def __init__(
        self,
        url: str = "http://localhost:8200",
        token: Optional[str] = None,
        namespace: Optional[str] = None,
        mount_point: str = "secret"
    ):
        """
        Args:
            url: URL Vault сервера
            token: Root token или app token
            namespace: Vault namespace (Enterprise feature)
            mount_point: Mount point для KV engine (по умолчанию "secret")
        """
        self.url = url
        self.token = token or os.getenv("VAULT_TOKEN")
        self.namespace = namespace
        self.mount_point = mount_point

        if not self.token:
            raise ValueError("Vault token is required (set VAULT_TOKEN env var)")

        # Создаем клиент
        self.client = hvac.Client(
            url=self.url,
            token=self.token,
            namespace=self.namespace
        )

        # Проверяем подключение
        if not self.client.is_authenticated():
            raise VaultError("Failed to authenticate with Vault")

        logger.info(f" Connected to Vault: {self.url}")

    # ============================================
    # KV Secrets (Static Secrets)
    # ============================================

    def write_secret(
        self,
        path: str,
        secret: Dict[str, Any],
        mount_point: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Сохранить секрет в KV v2 engine

        Args:
            path: Путь к секрету (например: "database/postgres")
            secret: Данные секрета
            mount_point: Mount point (по умолчанию self.mount_point)

        Returns:
            Metadata о созданном секрете (version, created_time, etc.)
        """
        mount = mount_point or self.mount_point

        try:
            response = self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secret,
                mount_point=mount
            )

            logger.info(f" Secret written to '{mount}/{path}' (version {response['data']['version']})")
            return response['data']

        except Exception as e:
            logger.error(f" Failed to write secret '{path}': {e}")
            raise

    def read_secret(
        self,
        path: str,
        version: Optional[int] = None,
        mount_point: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Прочитать секрет из KV v2 engine

        Args:
            path: Путь к секрету
            version: Версия секрета (None = latest)
            mount_point: Mount point

        Returns:
            Данные секрета
        """
        mount = mount_point or self.mount_point

        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                version=version,
                mount_point=mount
            )

            logger.debug(f" Secret read from '{mount}/{path}' (version {response['data']['metadata']['version']})")
            return response['data']['data']

        except InvalidPath:
            logger.warning(f"️  Secret not found: '{path}'")
            return {}

        except Exception as e:
            logger.error(f" Failed to read secret '{path}': {e}")
            raise

    def delete_secret(
        self,
        path: str,
        versions: Optional[List[int]] = None,
        mount_point: Optional[str] = None
    ):
        """
        Удалить версии секрета (soft delete)

        Args:
            path: Путь к секрету
            versions: Список версий для удаления (None = latest)
            mount_point: Mount point
        """
        mount = mount_point or self.mount_point

        try:
            if versions:
                self.client.secrets.kv.v2.delete_secret_versions(
                    path=path,
                    versions=versions,
                    mount_point=mount
                )
            else:
                self.client.secrets.kv.v2.delete_latest_version_of_secret(
                    path=path,
                    mount_point=mount
                )

            logger.info(f"️  Secret deleted: '{mount}/{path}' (versions: {versions or 'latest'})")

        except Exception as e:
            logger.error(f" Failed to delete secret '{path}': {e}")
            raise

    def list_secrets(
        self,
        path: str = "",
        mount_point: Optional[str] = None
    ) -> List[str]:
        """
        Список секретов в директории

        Args:
            path: Путь директории (пустая строка = корень)
            mount_point: Mount point

        Returns:
            Список имен секретов
        """
        mount = mount_point or self.mount_point

        try:
            response = self.client.secrets.kv.v2.list_secrets(
                path=path,
                mount_point=mount
            )

            secrets = response['data']['keys']
            logger.debug(f" Listed {len(secrets)} secrets in '{mount}/{path}'")
            return secrets

        except InvalidPath:
            return []

        except Exception as e:
            logger.error(f" Failed to list secrets in '{path}': {e}")
            raise

    # ============================================
    # Transit Engine (Encryption as a Service)
    # ============================================

    def create_encryption_key(
        self,
        name: str,
        key_type: str = "aes256-gcm96"
    ):
        """
        Создать ключ шифрования в Transit engine

        Args:
            name: Имя ключа
            key_type: Тип ключа (aes256-gcm96, chacha20-poly1305, rsa-2048, etc.)
        """
        try:
            self.client.secrets.transit.create_key(
                name=name,
                key_type=key_type
            )

            logger.info(f" Encryption key created: '{name}' (type: {key_type})")

        except Exception as e:
            logger.error(f" Failed to create encryption key '{name}': {e}")
            raise

    def encrypt(
        self,
        key_name: str,
        plaintext: str,
        context: Optional[str] = None
    ) -> str:
        """
        Зашифровать данные с помощью Transit engine

        Args:
            key_name: Имя ключа шифрования
            plaintext: Данные для шифрования
            context: Контекст (для AEAD)

        Returns:
            Зашифрованный текст (vault:v1:...)
        """
        import base64

        try:
            # Кодируем plaintext в base64
            plaintext_b64 = base64.b64encode(plaintext.encode()).decode()

            # Шифруем
            response = self.client.secrets.transit.encrypt_data(
                name=key_name,
                plaintext=plaintext_b64,
                context=context
            )

            ciphertext = response['data']['ciphertext']
            logger.debug(f" Data encrypted with key '{key_name}'")
            return ciphertext

        except Exception as e:
            logger.error(f" Encryption failed: {e}")
            raise

    def decrypt(
        self,
        key_name: str,
        ciphertext: str,
        context: Optional[str] = None
    ) -> str:
        """
        Расшифровать данные с помощью Transit engine

        Args:
            key_name: Имя ключа шифрования
            ciphertext: Зашифрованный текст
            context: Контекст (должен совпадать с encrypt)

        Returns:
            Расшифрованный текст
        """
        import base64

        try:
            # Расшифровываем
            response = self.client.secrets.transit.decrypt_data(
                name=key_name,
                ciphertext=ciphertext,
                context=context
            )

            # Декодируем из base64
            plaintext_b64 = response['data']['plaintext']
            plaintext = base64.b64decode(plaintext_b64).decode()

            logger.debug(f" Data decrypted with key '{key_name}'")
            return plaintext

        except Exception as e:
            logger.error(f" Decryption failed: {e}")
            raise

    # ============================================
    # Database Secrets (Dynamic Secrets)
    # ============================================

    def configure_database(
        self,
        name: str,
        plugin_name: str,
        connection_url: str,
        allowed_roles: List[str],
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Настроить Database Secrets Engine

        Args:
            name: Имя connection
            plugin_name: postgresql-database-plugin, mysql-database-plugin, etc.
            connection_url: Connection string (можно с {{username}} и {{password}})
            allowed_roles: Список разрешенных ролей
            username: Username для подключения
            password: Password для подключения
        """
        try:
            self.client.secrets.database.configure(
                name=name,
                plugin_name=plugin_name,
                connection_url=connection_url,
                allowed_roles=allowed_roles,
                username=username,
                password=password
            )

            logger.info(f" Database connection configured: '{name}'")

        except Exception as e:
            logger.error(f" Failed to configure database '{name}': {e}")
            raise

    def create_database_role(
        self,
        name: str,
        db_name: str,
        creation_statements: List[str],
        default_ttl: str = "1h",
        max_ttl: str = "24h"
    ):
        """
        Создать роль для Database Secrets

        Args:
            name: Имя роли
            db_name: Имя database connection
            creation_statements: SQL statements для создания user
            default_ttl: Время жизни credentials по умолчанию
            max_ttl: Максимальное время жизни
        """
        try:
            self.client.secrets.database.create_role(
                name=name,
                db_name=db_name,
                creation_statements=creation_statements,
                default_ttl=default_ttl,
                max_ttl=max_ttl
            )

            logger.info(f" Database role created: '{name}' (TTL: {default_ttl})")

        except Exception as e:
            logger.error(f" Failed to create database role '{name}': {e}")
            raise

    def get_database_credentials(
        self,
        role_name: str
    ) -> Dict[str, str]:
        """
        Получить динамические credentials для database role

        Args:
            role_name: Имя роли

        Returns:
            {"username": "v-root-...", "password": "..."}
        """
        try:
            response = self.client.secrets.database.generate_credentials(
                name=role_name
            )

            creds = response['data']
            logger.info(f" Generated database credentials for role '{role_name}' (lease: {response['lease_duration']}s)")
            return creds

        except Exception as e:
            logger.error(f" Failed to generate credentials for '{role_name}': {e}")
            raise

    # ============================================
    # Token Management
    # ============================================

    def create_token(
        self,
        policies: List[str],
        ttl: str = "1h",
        renewable: bool = True,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Создать новый Vault token

        Args:
            policies: Список policies для token
            ttl: Время жизни token
            renewable: Можно ли продлевать
            metadata: Метаданные

        Returns:
            Token info (client_token, accessor, etc.)
        """
        try:
            response = self.client.auth.token.create(
                policies=policies,
                ttl=ttl,
                renewable=renewable,
                meta=metadata
            )

            token_info = response['auth']
            logger.info(f"️  Token created (policies: {policies}, TTL: {ttl})")
            return token_info

        except Exception as e:
            logger.error(f" Failed to create token: {e}")
            raise

    def renew_token(
        self,
        token: Optional[str] = None,
        increment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Продлить token

        Args:
            token: Token для продления (None = self token)
            increment: На сколько продлить (None = default TTL)

        Returns:
            Обновленная информация о token
        """
        try:
            if token:
                response = self.client.auth.token.renew(
                    token=token,
                    increment=increment
                )
            else:
                response = self.client.auth.token.renew_self(
                    increment=increment
                )

            logger.info(f"️  Token renewed (new TTL: {response['auth']['lease_duration']}s)")
            return response['auth']

        except Exception as e:
            logger.error(f" Failed to renew token: {e}")
            raise

    def revoke_token(self, token: str):
        """Отозвать token"""
        try:
            self.client.auth.token.revoke(token=token)
            logger.info(f" Token revoked")

        except Exception as e:
            logger.error(f" Failed to revoke token: {e}")
            raise

    # ============================================
    # Utility Methods
    # ============================================

    def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья Vault сервера"""
        try:
            health = self.client.sys.read_health_status()
            logger.debug(f" Vault health: initialized={health.initialized}, sealed={health.sealed}")
            return {
                "initialized": health.initialized,
                "sealed": health.sealed,
                "standby": health.standby,
                "version": health.version
            }
        except Exception as e:
            logger.error(f" Health check failed: {e}")
            raise

    def is_sealed(self) -> bool:
        """Проверка, запечатан ли Vault"""
        return self.client.sys.is_sealed()


# Singleton instance
_vault_manager: Optional[VaultManager] = None


def get_vault_manager(
    url: str = None,
    token: str = None
) -> VaultManager:
    """Получить singleton instance Vault Manager"""
    global _vault_manager

    if _vault_manager is None:
        url = url or os.getenv("VAULT_ADDR", "http://localhost:8200")
        token = token or os.getenv("VAULT_TOKEN")
        _vault_manager = VaultManager(url, token)

    return _vault_manager


# Example usage
if __name__ == "__main__":
    # Создаем менеджер
    vault = VaultManager(
        url="http://localhost:8200",
        token="root-token"
    )

    # 1. Работа с секретами
    print("\n=== KV Secrets ===")

    # Сохранить секрет
    vault.write_secret("database/postgres", {
        "host": "localhost",
        "port": 5432,
        "username": "admin",
        "password": "super-secret-password"
    })

    # Прочитать секрет
    db_creds = vault.read_secret("database/postgres")
    print(f"Database password: {db_creds['password']}")

    # Список секретов
    secrets = vault.list_secrets("database")
    print(f"Secrets in 'database/': {secrets}")

    # 2. Шифрование данных
    print("\n=== Encryption ===")

    # Создать ключ
    vault.create_encryption_key("my-app-key")

    # Зашифровать
    plaintext = "sensitive customer data"
    ciphertext = vault.encrypt("my-app-key", plaintext)
    print(f"Encrypted: {ciphertext}")

    # Расшифровать
    decrypted = vault.decrypt("my-app-key", ciphertext)
    print(f"Decrypted: {decrypted}")

    # 3. Динамические credentials для БД
    print("\n=== Dynamic Database Credentials ===")

    # Настроить подключение
    vault.configure_database(
        name="my-postgres",
        plugin_name="postgresql-database-plugin",
        connection_url="postgresql://{{username}}:{{password}}@localhost:5432/mydb",
        allowed_roles=["readonly", "readwrite"],
        username="vault",
        password="vault-password"
    )

    # Создать роль
    vault.create_database_role(
        name="readonly",
        db_name="my-postgres",
        creation_statements=[
            "CREATE USER '{{name}}' WITH PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';",
            "GRANT SELECT ON ALL TABLES IN SCHEMA public TO '{{name}}';"
        ],
        default_ttl="1h",
        max_ttl="24h"
    )

    # Получить credentials
    creds = vault.get_database_credentials("readonly")
    print(f"Dynamic credentials: {creds['username']} / {creds['password']}")

    # 4. Token management
    print("\n=== Tokens ===")

    # Создать token для приложения
    app_token = vault.create_token(
        policies=["app-policy"],
        ttl="24h",
        metadata={"app": "bcm-platform"}
    )
    print(f"App token: {app_token['client_token'][:20]}...")

    # 5. Health check
    print("\n=== Health ===")
    health = vault.health_check()
    print(f"Vault status: {health}")
