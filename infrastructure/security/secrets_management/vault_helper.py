"""
Vault Helper - Utility to easily migrate services to VaultClient

Usage:
    from infrastructure.security.secrets_management.vault_helper import get_secret_safe

    # Will try Vault first, fallback to env var
    api_key = get_secret_safe("anthropic-api-key", env_var="ANTHROPIC_API_KEY")
"""

import os
import sys
import logging

logger = logging.getLogger(__name__)

# Add VaultClient to path
sys.path.insert(0, '/Users/MD/AI-Platform-ISO/infrastructure/security/secrets-management')

def get_secret_safe(secret_name: str, env_var: str = None, default: str = None) -> str:
    """
    Get secret from Vault with fallback to env var

    Args:
        secret_name: Name of secret in Vault (e.g., "anthropic-api-key")
        env_var: Environment variable to use as fallback (e.g., "ANTHROPIC_API_KEY")
        default: Default value if neither Vault nor env var available

    Returns:
        Secret value from Vault, env var, or default

    Raises:
        ValueError: If secret not found and no default provided
    """
    # Try Vault first
    try:
        from vault_client import get_secret
        value = get_secret(secret_name)
        logger.info(f" Loaded {secret_name} from Vault")
        return value
    except ImportError:
        logger.warning("️  VaultClient not available, using env vars")
    except Exception as e:
        logger.debug(f"Vault lookup failed for {secret_name}: {e}")

    # Fallback to env var
    if env_var:
        value = os.getenv(env_var)
        if value:
            logger.warning(f"️  Using {env_var} from .env (migrate to Vault)")
            return value

    # Use default if provided
    if default is not None:
        logger.warning(f"️  Using default value for {secret_name}")
        return default

    # Nothing found
    raise ValueError(
        f"Secret '{secret_name}' not found in Vault or env var '{env_var}'. "
        f"Add to Vault or set {env_var} in .env"
    )


def get_anthropic_api_key() -> str:
    """Get Anthropic API key from Vault or env"""
    return get_secret_safe("anthropic-api-key", env_var="ANTHROPIC_API_KEY")


def get_jwt_secret() -> str:
    """Get JWT secret from Vault or env"""
    return get_secret_safe("jwt-secret", env_var="JWT_SECRET")


def get_redis_password() -> str:
    """Get Redis password from Vault or env"""
    return get_secret_safe("redis-password", env_var="REDIS_PASSWORD")


def get_database_password() -> str:
    """Get Database password from Vault or env"""
    return get_secret_safe("database-password", env_var="DATABASE_PASSWORD")


if __name__ == "__main__":
    # Test all secrets
    import logging
    logging.basicConfig(level=logging.INFO)

    print("\n Testing Vault Helper\n")

    secrets_to_test = [
        ("anthropic-api-key", "ANTHROPIC_API_KEY"),
        ("jwt-secret", "JWT_SECRET"),
        ("redis-password", "REDIS_PASSWORD"),
        ("database-password", "DATABASE_PASSWORD"),
    ]

    for secret_name, env_var in secrets_to_test:
        try:
            value = get_secret_safe(secret_name, env_var=env_var)
            print(f" {secret_name}: {len(value)} chars")
        except Exception as e:
            print(f" {secret_name}: {e}")

    print("\n Test completed!")
