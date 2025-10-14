"""
Secrets Management - Supabase Vault Integration
"""

from .vault_client import (
    SupabaseVaultClient,
    get_vault_client,
    get_secret
)

__all__ = [
    'SupabaseVaultClient',
    'get_vault_client',
    'get_secret'
]
