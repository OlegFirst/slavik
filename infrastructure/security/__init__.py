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
]
