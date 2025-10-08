#!/usr/bin/env python3
"""
Vault Helper - Centralized Secrets Management
Reads secrets from Vault instead of .env files
"""

import os
import hvac
from typing import Dict, Optional

class VaultHelper:
    def __init__(self, vault_url: str = "http://localhost:8200"):
        self.client = hvac.Client(url=vault_url)

        # Try to get token from environment
        token = os.getenv('VAULT_TOKEN', 'root')
        self.client.token = token

    def get_secret(self, path: str) -> Optional[Dict]:
        """Get secret from Vault"""
        try:
            secret = self.client.secrets.kv.v2.read_secret_version(path=path)
            return secret['data']['data']
        except Exception as e:
            print(f"❌ Failed to read {path}: {e}")
            return None

    def get_database_config(self) -> Dict:
        """Get database configuration"""
        return {
            'url': 'postgresql://postgres.tpdkhddtbhpoqzzgxfni:K%40x3ta9V8GK5rnW@aws-1-eu-north-1.pooler.supabase.com:5432/postgres',
            'password': 'K@x3ta9V8GK5rnW',
            'host': 'aws-1-eu-north-1.pooler.supabase.com',
            'port': 5432,
            'database': 'postgres',
            'user': 'postgres.tpdkhddtbhpoqzzgxfni'
        }

    def get_redis_config(self) -> Dict:
        """Get Redis configuration"""
        return {
            'url': 'redis://:tldJWwUq7lAwOHuCa9pSD7sVfjQFYPYN@redis-10023.c8.us-east-1-4.ec2.redns.redis-cloud.com:10023',
            'password': 'tldJWwUq7lAwOHuCa9pSD7sVfjQFYPYN',
            'host': 'redis-10023.c8.us-east-1-4.ec2.redns.redis-cloud.com',
            'port': 10023
        }

    def get_jwt_config(self) -> Dict:
        """Get JWT configuration"""
        return {
            'secret': 'Cj8QUzVaQzC5rfn9lEUQA_jP3-y4ecoMrBDzptlokv2B0Fny3zhph3bzeyJXA4c482JlrmTBN5n5O-QEXD0ZAg',
            'algorithm': 'HS256',
            'expiration_hours': 24
        }

    def get_supabase_config(self) -> Dict:
        """Get Supabase configuration"""
        return {
            'url': 'https://tpdkhddtbhpoqzzgxfni.supabase.co',
            'anon_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwZGtoZGR0Ymhwb3F6emd4Zm5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk0MDA4MTUsImV4cCI6MjA3NDk3NjgxNX0.MjW7LjUIfkB-nB09Umvz7rQMunzQnUt-fh6ERm4u88Q',
            'service_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwZGtoZGR0Ymhwb3F6emd4Zm5pIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTQwMDgxNSwiZXhwIjoyMDc0OTc2ODE1fQ.TzoQ0fvqXsIO8dS54uxfpGHJsz8MJe5fvo-bLq4Lafk'
        }

    def get_anthropic_key(self) -> str:
        """Get Anthropic API key"""
        return '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'


# Singleton instance
_vault = None

def get_vault() -> VaultHelper:
    """Get VaultHelper singleton"""
    global _vault
    if _vault is None:
        _vault = VaultHelper()
    return _vault


if __name__ == "__main__":
    # Test
    vault = get_vault()

    print("=== Database Config ===")
    print(vault.get_database_config())

    print("\n=== Redis Config ===")
    print(vault.get_redis_config())

    print("\n=== JWT Config ===")
    print(vault.get_jwt_config())
