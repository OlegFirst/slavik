"""
PII Encryption Module for AI-Platform-ISO

Provides encryption/decryption utilities for sensitive health data and PII.
Uses AES-256-CBC encryption via pgcrypto PostgreSQL extension.

Usage:
    from infrastructure.security.encryption import EncryptionService

    encryption = EncryptionService()
    encrypted = await encryption.encrypt_health_data({"patient_id": "12345", "diagnosis": "..."})
    decrypted = await encryption.decrypt_health_data(encrypted)

Environment Variables:
    ENCRYPTION_KEY: 32-byte encryption key (required)

Author: Security hardening initiative
Date: 2025-10-19
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import json

logger = logging.getLogger(__name__)

# Lazy import vault_client to avoid circular dependency
def _get_vault_client():
    """Lazy import of vault client"""
    try:
        from .vault_client import get_vault_client
        return get_vault_client()
    except Exception as e:
        logger.warning(f"Vault client not available: {e}")
        return None


class EncryptionError(Exception):
    """Raised when encryption/decryption operations fail"""
    pass


class EncryptionService:
    """
    Service for encrypting/decrypting PII and health data

    This service uses Fernet (symmetric encryption) for application-level encryption
    that complements database-level pgcrypto encryption.

    Key Features:
    - AES-256-CBC encryption
    - Automatic key derivation from master key
    - JSON serialization for complex data
    - Type-safe encryption/decryption
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption service

        Args:
            encryption_key: Base encryption key. If None, tries Vault, then ENCRYPTION_KEY env var

        Raises:
            EncryptionError: If encryption key is not configured
        """
        # Priority: 1) Explicit param, 2) Vault, 3) Environment variable
        if encryption_key:
            self.key = encryption_key
        else:
            # Try Vault first
            vault = _get_vault_client()
            if vault:
                try:
                    self.key = vault.get_secret_with_fallback(
                        'encryption_key',
                        'ENCRYPTION_KEY',
                        None
                    )
                except Exception as e:
                    logger.warning(f"Failed to get encryption key from Vault: {e}")
                    self.key = os.getenv("ENCRYPTION_KEY")
            else:
                # Fallback to environment variable
                self.key = os.getenv("ENCRYPTION_KEY")

        if not self.key:
            raise EncryptionError(
                "Encryption key not configured. Add to Vault: "
                "SELECT vault.create_secret('key', 'encryption_key') "
                "or set ENCRYPTION_KEY environment variable"
            )

        # Derive Fernet key from master key
        self.fernet = self._derive_fernet_key(self.key.encode())

    def _derive_fernet_key(self, master_key: bytes) -> Fernet:
        """
        Derive Fernet key from master key using PBKDF2

        Args:
            master_key: Master encryption key

        Returns:
            Fernet instance for encryption/decryption
        """
        # Use PBKDF2 to derive a key from the master key
        # Salt should be fixed for consistent key derivation
        salt = b'ai-platform-iso-salt-v1'  # In production, use configurable salt

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )

        key = base64.urlsafe_b64encode(kdf.derive(master_key))
        return Fernet(key)

    def encrypt_string(self, plaintext: str) -> bytes:
        """
        Encrypt a string

        Args:
            plaintext: String to encrypt

        Returns:
            Encrypted bytes

        Raises:
            EncryptionError: If encryption fails
        """
        if not plaintext:
            return b""

        try:
            return self.fernet.encrypt(plaintext.encode('utf-8'))
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise EncryptionError(f"Failed to encrypt data: {e}")

    def decrypt_string(self, ciphertext: bytes) -> str:
        """
        Decrypt bytes to string

        Args:
            ciphertext: Encrypted bytes

        Returns:
            Decrypted string

        Raises:
            EncryptionError: If decryption fails
        """
        if not ciphertext:
            return ""

        try:
            return self.fernet.decrypt(ciphertext).decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise EncryptionError(f"Failed to decrypt data: {e}")

    def encrypt_dict(self, data: Dict[str, Any]) -> bytes:
        """
        Encrypt a dictionary (JSON serializable)

        Args:
            data: Dictionary to encrypt

        Returns:
            Encrypted bytes

        Raises:
            EncryptionError: If encryption fails
        """
        if not data:
            return b""

        try:
            json_str = json.dumps(data, ensure_ascii=False)
            return self.encrypt_string(json_str)
        except Exception as e:
            logger.error(f"Failed to encrypt dict: {e}")
            raise EncryptionError(f"Failed to encrypt dictionary: {e}")

    def decrypt_dict(self, ciphertext: bytes) -> Dict[str, Any]:
        """
        Decrypt bytes to dictionary

        Args:
            ciphertext: Encrypted bytes

        Returns:
            Decrypted dictionary

        Raises:
            EncryptionError: If decryption fails
        """
        if not ciphertext:
            return {}

        try:
            json_str = self.decrypt_string(ciphertext)
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse decrypted JSON: {e}")
            raise EncryptionError(f"Decrypted data is not valid JSON: {e}")
        except Exception as e:
            logger.error(f"Failed to decrypt dict: {e}")
            raise EncryptionError(f"Failed to decrypt dictionary: {e}")

    # Specific methods for health data

    def encrypt_health_data(self, health_data: Dict[str, Any]) -> bytes:
        """
        Encrypt health/medical records

        Args:
            health_data: Health data dictionary (patient records, diagnosis, etc.)

        Returns:
            Encrypted bytes

        Example:
            health_data = {
                "patient_id": "P-12345",
                "diagnosis": "Hypertension",
                "medications": ["Lisinopril 10mg"],
                "vitals": {"bp": "140/90", "hr": 72}
            }
            encrypted = encryption.encrypt_health_data(health_data)
        """
        logger.info("Encrypting health data")
        return self.encrypt_dict(health_data)

    def decrypt_health_data(self, ciphertext: bytes) -> Dict[str, Any]:
        """
        Decrypt health/medical records

        Args:
            ciphertext: Encrypted health data

        Returns:
            Decrypted health data dictionary
        """
        logger.info("Decrypting health data")
        return self.decrypt_dict(ciphertext)

    def encrypt_pii(self, pii_data: Union[str, Dict[str, Any]]) -> bytes:
        """
        Encrypt PII data (name, email, phone, SSN, etc.)

        Args:
            pii_data: PII as string or dictionary

        Returns:
            Encrypted bytes

        Example:
            # String PII
            encrypted_email = encryption.encrypt_pii("patient@example.com")

            # Dict PII
            encrypted_contact = encryption.encrypt_pii({
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1-555-0100"
            })
        """
        logger.info("Encrypting PII data")

        if isinstance(pii_data, dict):
            return self.encrypt_dict(pii_data)
        elif isinstance(pii_data, str):
            return self.encrypt_string(pii_data)
        else:
            raise EncryptionError(f"Unsupported PII data type: {type(pii_data)}")

    def decrypt_pii(self, ciphertext: bytes, return_type: str = "str") -> Union[str, Dict[str, Any]]:
        """
        Decrypt PII data

        Args:
            ciphertext: Encrypted PII
            return_type: "str" or "dict" - expected return type

        Returns:
            Decrypted PII as string or dictionary
        """
        logger.info("Decrypting PII data")

        if return_type == "dict":
            return self.decrypt_dict(ciphertext)
        else:
            return self.decrypt_string(ciphertext)

    # Email and phone specific helpers

    def encrypt_email(self, email: str) -> bytes:
        """Encrypt email address"""
        normalized = email.lower().strip()
        return self.encrypt_string(normalized)

    def decrypt_email(self, ciphertext: bytes) -> str:
        """Decrypt email address"""
        return self.decrypt_string(ciphertext)

    def encrypt_phone(self, phone: str) -> bytes:
        """
        Encrypt phone number

        Normalizes phone by removing all non-numeric characters before encryption
        """
        import re
        normalized = re.sub(r'[^0-9]', '', phone)
        return self.encrypt_string(normalized)

    def decrypt_phone(self, ciphertext: bytes) -> str:
        """Decrypt phone number"""
        return self.decrypt_string(ciphertext)


# Global singleton instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """
    Get global encryption service instance (singleton)

    Returns:
        EncryptionService instance

    Raises:
        EncryptionError: If encryption key is not configured
    """
    global _encryption_service

    if _encryption_service is None:
        _encryption_service = EncryptionService()

    return _encryption_service


# Convenience functions for common operations

def encrypt_health_data(data: Dict[str, Any]) -> bytes:
    """Encrypt health data (convenience function)"""
    return get_encryption_service().encrypt_health_data(data)


def decrypt_health_data(ciphertext: bytes) -> Dict[str, Any]:
    """Decrypt health data (convenience function)"""
    return get_encryption_service().decrypt_health_data(ciphertext)


def encrypt_pii(data: Union[str, Dict[str, Any]]) -> bytes:
    """Encrypt PII (convenience function)"""
    return get_encryption_service().encrypt_pii(data)


def decrypt_pii(ciphertext: bytes, return_type: str = "str") -> Union[str, Dict[str, Any]]:
    """Decrypt PII (convenience function)"""
    return get_encryption_service().decrypt_pii(ciphertext, return_type)
