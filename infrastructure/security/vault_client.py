"""
Supabase Vault Client for Python Services

Provides access to secrets stored in Supabase Vault.
Replaces environment variables with secure Vault storage.

Usage:
    from infrastructure.security.vault_client import get_vault_client

    vault = get_vault_client()
    encryption_key = vault.get_secret('encryption_key')
    smtp_password = vault.get_secret('smtp_password')

Author: Security hardening initiative
Date: 2025-10-19
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


@dataclass
class VaultSecret:
    """Vault secret with metadata"""
    id: str
    name: str
    value: str
    description: Optional[str] = None
    created_at: Optional[str] = None


class SupabaseVaultClient:
    """
    Client for accessing Supabase Vault secrets

    Reads secrets from vault.decrypted_secrets view via Supabase REST API.
    Caches secrets in memory for performance.

    Configuration via environment:
    - SUPABASE_URL: Supabase project URL
    - SUPABASE_SERVICE_KEY: Service role key (has vault access)
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        service_key: Optional[str] = None,
        cache_enabled: bool = True
    ):
        """
        Initialize Vault client

        Args:
            supabase_url: Supabase project URL (defaults to env SUPABASE_URL)
            service_key: Service role key (defaults to env SUPABASE_SERVICE_KEY)
            cache_enabled: Enable in-memory caching of secrets
        """
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.service_key = service_key or os.getenv('SUPABASE_SERVICE_KEY')

        if not self.supabase_url:
            raise ValueError("SUPABASE_URL environment variable not set")
        if not self.service_key:
            raise ValueError("SUPABASE_SERVICE_KEY environment variable not set")

        self.cache_enabled = cache_enabled
        self._cache: Dict[str, VaultSecret] = {}

        # Build API endpoint
        self.vault_url = f"{self.supabase_url}/rest/v1/decrypted_secrets"

        logger.info(f"Vault client initialized (cache: {cache_enabled})")

    def get_secret(self, name: str, use_cache: bool = True) -> str:
        """
        Get secret value by name

        Args:
            name: Secret name (e.g., 'encryption_key', 'smtp_password')
            use_cache: Use cached value if available

        Returns:
            Secret value as string

        Raises:
            ValueError: If secret not found
            httpx.HTTPError: If API request fails
        """
        # Check cache
        if use_cache and self.cache_enabled and name in self._cache:
            logger.debug(f"Retrieved secret '{name}' from cache")
            return self._cache[name].value

        # Fetch from Vault
        try:
            with httpx.Client() as client:
                response = client.get(
                    self.vault_url,
                    headers={
                        'apikey': self.service_key,
                        'Authorization': f'Bearer {self.service_key}',
                        'Content-Type': 'application/json'
                    },
                    params={'name': f'eq.{name}', 'select': 'id,name,decrypted_secret,description,created_at'}
                )
                response.raise_for_status()

            data = response.json()

            if not data:
                raise ValueError(f"Secret '{name}' not found in Vault")

            secret_data = data[0]
            secret = VaultSecret(
                id=secret_data['id'],
                name=secret_data['name'],
                value=secret_data['decrypted_secret'],
                description=secret_data.get('description'),
                created_at=secret_data.get('created_at')
            )

            # Cache
            if self.cache_enabled:
                self._cache[name] = secret

            logger.info(f"Retrieved secret '{name}' from Vault")
            return secret.value

        except httpx.HTTPError as e:
            logger.error(f"Failed to retrieve secret '{name}': {e}")
            raise

    def get_secret_with_fallback(self, name: str, env_var: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret with fallback to environment variable

        Args:
            name: Secret name in Vault
            env_var: Environment variable name
            default: Default value if neither Vault nor env var available

        Returns:
            Secret value, env var, or default

        Example:
            # Try Vault, fall back to env var, default to None
            smtp_password = vault.get_secret_with_fallback(
                'smtp_password',
                'SMTP_PASSWORD',
                None
            )
        """
        try:
            return self.get_secret(name)
        except (ValueError, httpx.HTTPError) as e:
            logger.warning(f"Vault secret '{name}' not available: {e}")

            # Try environment variable
            env_value = os.getenv(env_var)
            if env_value:
                logger.info(f"Using environment variable {env_var} instead of Vault")
                return env_value

            # Use default
            if default is not None:
                logger.info(f"Using default value for '{name}'")
                return default

            return None

    def create_secret(self, name: str, value: str, description: str = "") -> str:
        """
        Create new secret in Vault

        Args:
            name: Secret name
            value: Secret value
            description: Secret description

        Returns:
            Secret ID (UUID)

        Note: This requires database access. For production, use Supabase dashboard
        or SQL client to create secrets.
        """
        raise NotImplementedError(
            "Creating secrets via API is not supported. "
            "Use SQL: SELECT vault.create_secret('value', 'name', 'description');"
        )

    def update_secret(self, name: str, new_value: str) -> None:
        """
        Update existing secret

        Args:
            name: Secret name
            new_value: New secret value

        Note: This requires database access. For production, use SQL client.
        """
        raise NotImplementedError(
            "Updating secrets via API is not supported. "
            "Use SQL: SELECT vault.update_secret(id, 'new_value');"
        )

    def list_secrets(self) -> list[str]:
        """
        List all available secret names

        Returns:
            List of secret names
        """
        try:
            with httpx.Client() as client:
                response = client.get(
                    self.vault_url,
                    headers={
                        'apikey': self.service_key,
                        'Authorization': f'Bearer {self.service_key}',
                        'Content-Type': 'application/json'
                    },
                    params={'select': 'name'}
                )
                response.raise_for_status()

            data = response.json()
            return [item['name'] for item in data if item.get('name')]

        except httpx.HTTPError as e:
            logger.error(f"Failed to list secrets: {e}")
            return []

    def clear_cache(self) -> None:
        """Clear cached secrets"""
        self._cache.clear()
        logger.info("Vault cache cleared")


# Global singleton
_vault_client: Optional[SupabaseVaultClient] = None


def get_vault_client(
    supabase_url: Optional[str] = None,
    service_key: Optional[str] = None,
    cache_enabled: bool = True
) -> SupabaseVaultClient:
    """
    Get global Vault client instance (singleton)

    Args:
        supabase_url: Supabase project URL
        service_key: Service role key
        cache_enabled: Enable caching

    Returns:
        SupabaseVaultClient instance
    """
    global _vault_client

    if _vault_client is None:
        _vault_client = SupabaseVaultClient(
            supabase_url=supabase_url,
            service_key=service_key,
            cache_enabled=cache_enabled
        )

    return _vault_client


# Convenience functions
def get_secret(name: str) -> str:
    """Get secret from Vault (convenience function)"""
    return get_vault_client().get_secret(name)


def get_secret_with_fallback(name: str, env_var: str, default: Optional[str] = None) -> Optional[str]:
    """Get secret with fallback to env var (convenience function)"""
    return get_vault_client().get_secret_with_fallback(name, env_var, default)
