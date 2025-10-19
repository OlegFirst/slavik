"""
Security Middleware for FastAPI Services

Provides automatic PII encryption/decryption for FastAPI applications.
Can be used as dependency injection or response middleware.

Usage:
    from infrastructure.security.middleware import encrypt_sensitive_fields

    @app.post("/bia")
    async def create_bia(
        data: BIACreate,
        encryption_service: EncryptionService = Depends(get_encryption_service_dep)
    ):
        # Manually encrypt sensitive fields
        encrypted_patient_data = encryption_service.encrypt_health_data(data.patient_data)
        # Save to DB...

Author: Security hardening initiative
Date: 2025-10-19
"""

from typing import Dict, Any, List, Optional, Callable
from fastapi import Depends, HTTPException, status
import logging

from .encryption import get_encryption_service, EncryptionService, EncryptionError

logger = logging.getLogger(__name__)


# Dependency for FastAPI
def get_encryption_service_dep() -> EncryptionService:
    """
    FastAPI dependency to inject encryption service

    Usage:
        @app.post("/endpoint")
        async def endpoint(
            encryption: EncryptionService = Depends(get_encryption_service_dep)
        ):
            encrypted = encryption.encrypt_pii(data)
    """
    try:
        return get_encryption_service()
    except EncryptionError as e:
        logger.error(f"Failed to initialize encryption service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Encryption service unavailable"
        )


# Field-level encryption helpers
PII_FIELDS = [
    "email",
    "phone",
    "contact_email",
    "contact_phone",
    "patient_name",
    "patient_id",
    "emergency_contact",
    "personal_notes",
]

HEALTH_DATA_FIELDS = [
    "patient_data",
    "health_records",
    "medical_history",
    "diagnosis",
    "treatment_plan",
]


def encrypt_sensitive_fields(
    data: Dict[str, Any],
    pii_fields: Optional[List[str]] = None,
    health_fields: Optional[List[str]] = None,
    encryption_service: Optional[EncryptionService] = None
) -> Dict[str, Any]:
    """
    Encrypt sensitive fields in a dictionary

    Args:
        data: Dictionary containing sensitive fields
        pii_fields: List of PII field names (default: common PII fields)
        health_fields: List of health data field names (default: common health fields)
        encryption_service: Encryption service instance (or uses singleton)

    Returns:
        Dictionary with sensitive fields encrypted (field names get _encrypted suffix)

    Example:
        data = {
            "name": "Hospital A",
            "email": "contact@hospital.com",
            "patient_data": {"id": "P123", "diagnosis": "..."}
        }

        encrypted = encrypt_sensitive_fields(data)
        # Result:
        # {
        #     "name": "Hospital A",
        #     "email_encrypted": b"...",  # encrypted
        #     "patient_data_encrypted": b"..."  # encrypted
        # }
    """
    if not encryption_service:
        encryption_service = get_encryption_service()

    pii_fields = pii_fields or PII_FIELDS
    health_fields = health_fields or HEALTH_DATA_FIELDS

    result = data.copy()

    # Encrypt PII fields
    for field in pii_fields:
        if field in result:
            value = result.pop(field)
            if value:
                try:
                    encrypted = encryption_service.encrypt_pii(value)
                    result[f"{field}_encrypted"] = encrypted
                    logger.debug(f"Encrypted PII field: {field}")
                except EncryptionError as e:
                    logger.error(f"Failed to encrypt {field}: {e}")
                    raise

    # Encrypt health data fields
    for field in health_fields:
        if field in result:
            value = result.pop(field)
            if value:
                try:
                    encrypted = encryption_service.encrypt_health_data(value)
                    result[f"{field}_encrypted"] = encrypted
                    logger.debug(f"Encrypted health field: {field}")
                except EncryptionError as e:
                    logger.error(f"Failed to encrypt {field}: {e}")
                    raise

    return result


def decrypt_sensitive_fields(
    data: Dict[str, Any],
    pii_fields: Optional[List[str]] = None,
    health_fields: Optional[List[str]] = None,
    encryption_service: Optional[EncryptionService] = None
) -> Dict[str, Any]:
    """
    Decrypt sensitive fields in a dictionary

    Args:
        data: Dictionary containing encrypted fields (with _encrypted suffix)
        pii_fields: List of PII field names (default: common PII fields)
        health_fields: List of health data field names (default: common health fields)
        encryption_service: Encryption service instance (or uses singleton)

    Returns:
        Dictionary with encrypted fields decrypted (removes _encrypted suffix)

    Example:
        encrypted_data = {
            "name": "Hospital A",
            "email_encrypted": b"...",
            "patient_data_encrypted": b"..."
        }

        decrypted = decrypt_sensitive_fields(encrypted_data)
        # Result:
        # {
        #     "name": "Hospital A",
        #     "email": "contact@hospital.com",
        #     "patient_data": {"id": "P123", "diagnosis": "..."}
        # }
    """
    if not encryption_service:
        encryption_service = get_encryption_service()

    pii_fields = pii_fields or PII_FIELDS
    health_fields = health_fields or HEALTH_DATA_FIELDS

    result = data.copy()

    # Decrypt PII fields
    for field in pii_fields:
        encrypted_field = f"{field}_encrypted"
        if encrypted_field in result:
            encrypted_value = result.pop(encrypted_field)
            if encrypted_value:
                try:
                    decrypted = encryption_service.decrypt_pii(encrypted_value, return_type="str")
                    result[field] = decrypted
                    logger.debug(f"Decrypted PII field: {field}")
                except EncryptionError as e:
                    logger.error(f"Failed to decrypt {field}: {e}")
                    # Don't fail, just skip
                    result[field] = None

    # Decrypt health data fields
    for field in health_fields:
        encrypted_field = f"{field}_encrypted"
        if encrypted_field in result:
            encrypted_value = result.pop(encrypted_field)
            if encrypted_value:
                try:
                    decrypted = encryption_service.decrypt_health_data(encrypted_value)
                    result[field] = decrypted
                    logger.debug(f"Decrypted health field: {field}")
                except EncryptionError as e:
                    logger.error(f"Failed to decrypt {field}: {e}")
                    # Don't fail, just skip
                    result[field] = None

    return result


# Decorator for automatic encryption
def auto_encrypt_response(
    pii_fields: Optional[List[str]] = None,
    health_fields: Optional[List[str]] = None
):
    """
    Decorator to automatically encrypt sensitive fields in response

    Usage:
        @app.get("/bia/{id}")
        @auto_encrypt_response(health_fields=["patient_data"])
        async def get_bia(id: str):
            # Return unencrypted data
            return {"id": id, "patient_data": {...}}
            # Response will have patient_data_encrypted automatically

    Note: This is a simplified decorator. For production, consider
    using FastAPI response models with custom serializers.
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if isinstance(result, dict):
                return encrypt_sensitive_fields(result, pii_fields, health_fields)
            return result
        return wrapper
    return decorator


# Model mixin for encrypted fields
class EncryptedFieldsMixin:
    """
    Mixin for Pydantic models to handle encrypted fields

    Usage:
        class BIAModel(BaseModel, EncryptedFieldsMixin):
            id: str
            patient_data: Optional[Dict] = None
            patient_data_encrypted: Optional[bytes] = None

            def encrypt_fields(self):
                if self.patient_data:
                    self.patient_data_encrypted = encrypt_health_data(self.patient_data)
                    self.patient_data = None
    """

    def encrypt_fields(
        self,
        pii_fields: Optional[List[str]] = None,
        health_fields: Optional[List[str]] = None
    ):
        """Encrypt all sensitive fields in the model"""
        data = self.dict()
        encrypted_data = encrypt_sensitive_fields(data, pii_fields, health_fields)

        # Update model with encrypted fields
        for key, value in encrypted_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def decrypt_fields(
        self,
        pii_fields: Optional[List[str]] = None,
        health_fields: Optional[List[str]] = None
    ):
        """Decrypt all encrypted fields in the model"""
        data = self.dict()
        decrypted_data = decrypt_sensitive_fields(data, pii_fields, health_fields)

        # Update model with decrypted fields
        for key, value in decrypted_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
