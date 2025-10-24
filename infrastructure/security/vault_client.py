"""
Supabase Vault Client for Secrets Management
Secure retrieval of secrets from Supabase Vault
"""

import os
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class VaultClient:
    """Client for Supabase Vault secrets management"""

    def __init__(self, supabase_url: Optional[str] = None, service_role_key: Optional[str] = None):
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.service_role_key = service_role_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not self.supabase_url or not self.service_role_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

        self._supabase = None
        self._cache: Dict[str, str] = {}

    @property
    def supabase(self):
        """Lazy-load Supabase client"""
        if self._supabase is None:
            try:
                from supabase import create_client
                self._supabase = create_client(self.supabase_url, self.service_role_key)
            except ImportError:
                raise ImportError("supabase-py required: pip install supabase")
        return self._supabase

    def get_secret(self, secret_name: str, use_cache: bool = True) -> str:
        """Retrieve secret from Vault"""
        if use_cache and secret_name in self._cache:
            return self._cache[secret_name]

        try:
            result = self.supabase.rpc("get_secret", {"secret_name": secret_name}).execute()
            if not result.data:
                raise ValueError(f"Secret '{secret_name}' not found")

            secret_value = result.data[0]["decrypted_secret"]
            if use_cache:
                self._cache[secret_name] = secret_value
            return secret_value
        except Exception as e:
            raise ValueError(f"Failed to retrieve secret '{secret_name}': {e}")


def get_secret_or_env(secret_name: str, env_var: str, default: Optional[str] = None) -> str:
    """Try Vault first, fall back to environment variable"""
    try:
        client = VaultClient()
        return client.get_secret(secret_name)
    except:
        return os.getenv(env_var, default)
