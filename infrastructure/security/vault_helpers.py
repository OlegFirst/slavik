"""
Vault Helper Functions
Удобные функции для работы с Supabase Vault
"""

from typing import Optional
from .vault_client import get_vault_client

def get_temporal_config() -> dict:
    """
    Get Temporal Cloud configuration from Vault
    
    Returns:
        dict with temporal_api_key, namespace, address
    """
    vault = get_vault_client()
    
    return {
        'api_key': vault.get_secret_with_fallback('temporal_api_key', 'TEMPORAL_API_KEY'),
        'namespace': os.getenv('TEMPORAL_NAMESPACE', 'ai-platform-iso-22301.r3gxp'),
        'address': os.getenv('TEMPORAL_ADDRESS', 'europe-west3.gcp.api.temporal.io:7233')
    }

def get_qdrant_config() -> dict:
    """
    Get Qdrant configuration from Vault
    
    Returns:
        dict with api_key, url
    """
    vault = get_vault_client()
    
    return {
        'api_key': vault.get_secret_with_fallback('qdrant_api_key', 'QDRANT_API_KEY'),
        'url': os.getenv('QDRANT_URL', 'https://fa9f6acd-aef9-4ebe-a3f5-f89c62bce378.eu-west-1-0.aws.cloud.qdrant.io:6333')
    }

def get_rabbitmq_config() -> dict:
    """
    Get RabbitMQ configuration from Vault
    
    Returns:
        dict with password, host, port, user
    """
    vault = get_vault_client()
    
    return {
        'password': vault.get_secret_with_fallback('rabbitmq_password', 'RABBITMQ_PASSWORD', 'guest'),
        'host': os.getenv('RABBITMQ_HOST', 'localhost'),
        'port': int(os.getenv('RABBITMQ_PORT', '5672')),
        'user': os.getenv('RABBITMQ_USER', 'guest')
    }

def get_all_vault_secrets() -> list:
    """
    List all secrets in Vault
    
    Returns:
        List of secret names
    """
    vault = get_vault_client()
    return vault.list_secrets()

def test_vault_connection() -> bool:
    """
    Test Vault connection
    
    Returns:
        True if connection successful
    """
    try:
        vault = get_vault_client()
        secrets = vault.list_secrets()
        print(f" Vault connection OK: {len(secrets)} secrets available")
        return True
    except Exception as e:
        print(f" Vault connection failed: {e}")
        return False

# Add missing import
import os
