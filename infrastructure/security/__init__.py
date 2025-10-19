"""
Security Infrastructure Module

Exports:
- EncryptionService: PII/health data encryption service
- get_encryption_service: Singleton accessor
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

__all__ = [
    "EncryptionService",
    "EncryptionError",
    "get_encryption_service",
    "encrypt_health_data",
    "decrypt_health_data",
    "encrypt_pii",
    "decrypt_pii",
]
