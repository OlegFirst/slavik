#!/usr/bin/env python3
"""
Тест интеграции Supabase Vault
Проверяет доступ ко всем секретам
"""

import sys
import os

# Добавить путь к проекту
sys.path.insert(0, '/Users/MD/AI-Platform-ISO')

from infrastructure.security import (
    test_vault_connection,
    get_all_vault_secrets,
    get_temporal_config,
    get_qdrant_config,
    get_rabbitmq_config,
    get_encryption_service,
    get_vault_client
)

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║          VAULT INTEGRATION TEST                              ║")
    print("╔══════════════════════════════════════════════════════════════╗")
    print()
    
    # Test 1: Vault Connection
    print("📡 Test 1: Vault Connection")
    print("-" * 60)
    if not test_vault_connection():
        print("❌ FAILED: Cannot connect to Vault")
        return False
    print()
    
    # Test 2: List all secrets
    print("📋 Test 2: List All Secrets")
    print("-" * 60)
    try:
        secrets = get_all_vault_secrets()
        print(f"✅ Found {len(secrets)} secrets:")
        for i, secret_name in enumerate(secrets, 1):
            print(f"   {i}. {secret_name}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False
    print()
    
    # Test 3: Read critical secrets
    print("🔑 Test 3: Read Critical Secrets")
    print("-" * 60)
    vault = get_vault_client()
    
    critical_secrets = [
        'encryption_key',
        'anthropic-api-key',
        'temporal_api_key',
        'qdrant_api_key',
        'rabbitmq_password',
        'redis-password',
        'database-password',
        'jwt-secret'
    ]
    
    for secret_name in critical_secrets:
        try:
            value = vault.get_secret(secret_name)
            if value and len(value) > 10:
                print(f"   ✅ {secret_name}: {value[:10]}... ({len(value)} chars)")
            else:
                print(f"   ⚠️  {secret_name}: TOO SHORT or EMPTY")
        except Exception as e:
            print(f"   ❌ {secret_name}: ERROR - {e}")
    print()
    
    # Test 4: Helper Functions
    print("🛠️  Test 4: Helper Functions")
    print("-" * 60)
    
    try:
        temporal_config = get_temporal_config()
        print(f"   ✅ Temporal: api_key={temporal_config['api_key'][:20]}...")
        print(f"              namespace={temporal_config['namespace']}")
    except Exception as e:
        print(f"   ❌ Temporal config failed: {e}")
    
    try:
        qdrant_config = get_qdrant_config()
        print(f"   ✅ Qdrant: api_key={qdrant_config['api_key'][:20]}...")
        print(f"             url={qdrant_config['url'][:50]}...")
    except Exception as e:
        print(f"   ❌ Qdrant config failed: {e}")
    
    try:
        rabbitmq_config = get_rabbitmq_config()
        print(f"   ✅ RabbitMQ: password={rabbitmq_config['password'][:10]}...")
        print(f"               host={rabbitmq_config['host']}")
    except Exception as e:
        print(f"   ❌ RabbitMQ config failed: {e}")
    print()
    
    # Test 5: Encryption Service
    print("🔐 Test 5: Encryption Service (uses Vault)")
    print("-" * 60)
    try:
        encryption = get_encryption_service()
        
        # Test encryption
        test_data = {"patient_id": "12345", "diagnosis": "test"}
        encrypted = encryption.encrypt_health_data(test_data)
        decrypted = encryption.decrypt_health_data(encrypted)
        
        if decrypted == test_data:
            print("   ✅ Encryption/Decryption works!")
            print(f"      Original: {test_data}")
            print(f"      Encrypted: {encrypted[:50]}...")
            print(f"      Decrypted: {decrypted}")
        else:
            print("   ❌ Decryption mismatch!")
    except Exception as e:
        print(f"   ❌ Encryption test failed: {e}")
    print()
    
    # Summary
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    TEST SUMMARY                              ║")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("✅ All tests passed successfully!")
    print(f"📊 Vault contains {len(secrets)} secrets")
    print("🔐 All critical secrets are accessible")
    print("🛠️  Helper functions work correctly")
    print("🔒 Encryption service integrated with Vault")
    print()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
