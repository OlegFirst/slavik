"""
Security Infrastructure Module

Exports:
- EncryptionService: PII/health data encryption service
- get_encryption_service: Singleton accessor
- SupabaseVaultClient: Secrets management via Supabase Vault
- get_vault_client: Vault client singleton
- Convenience functions: encrypt_health_data, decrypt_health_data, encrypt_pii, decrypt_pii
"""

from .encryption import (
    EncryptionService,
    EncryptionError,
    get_encryption_service,
    encrypt_health_data,
    decrypt_health_data,
    encrypt_pii,
    decrypt_pii,
)

from .vault_client import (
    SupabaseVaultClient,
    VaultSecret,
    get_vault_client,
    get_secret,
    get_secret_with_fallback,
)

from .vault_helpers import (
    get_temporal_config,
    get_qdrant_config,
    get_rabbitmq_config,
    get_all_vault_secrets,
    test_vault_connection,
)

__all__ = [
    # Encryption
    "EncryptionService",
    "EncryptionError",
    "get_encryption_service",
    "encrypt_health_data",
    "decrypt_health_data",
    "encrypt_pii",
    "decrypt_pii",
    # Vault
    "SupabaseVaultClient",
    "VaultSecret",
    "get_vault_client",
    "get_secret",
    "get_secret_with_fallback",
    # Vault Helpers
    "get_temporal_config",
    "get_qdrant_config",
    "get_rabbitmq_config",
    "get_all_vault_secrets",
    "test_vault_connection",
]
