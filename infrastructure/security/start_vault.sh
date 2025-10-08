#!/bin/bash

# HashiCorp Vault Startup Script
# Port: 8200

set -e

echo "🔐 Starting HashiCorp Vault..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop first"
    exit 1
fi

# Check if Vault container exists
if docker ps -a | grep -q "vault-bcm"; then
    echo "📦 Vault container exists"

    # Check if running
    if docker ps | grep -q "vault-bcm"; then
        echo "✅ Vault is already running"
        echo "Vault UI: http://localhost:8200/ui"
        exit 0
    else
        echo "🔄 Starting existing container..."
        docker start vault-bcm
    fi
else
    echo "📦 Creating new Vault container..."

    # Create vault data directory
    VAULT_DATA_DIR="/Users/MD/AI-Platform-ISO/infrastructure/security/vault-data"
    mkdir -p "$VAULT_DATA_DIR"

    # Run Vault in dev mode (for testing)
    docker run -d \
        --name vault-bcm \
        -p 8200:8200 \
        -e VAULT_DEV_ROOT_TOKEN_ID=bcm-root-token \
        -e VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200 \
        -v "$VAULT_DATA_DIR:/vault/data" \
        --cap-add=IPC_LOCK \
        hashicorp/vault:1.15 server -dev

    echo "⏳ Waiting for Vault to start..."
    sleep 5
fi

# Check Vault health
echo "🔍 Checking Vault health..."
curl -s http://localhost:8200/v1/sys/health | python3 -m json.tool || {
    echo "⚠️  Vault health check failed"
}

echo ""
echo "✅ Vault is running!"
echo ""
echo "╔═══════════════════════════════════════╗"
echo "║  Vault Dev Mode Configuration        ║"
echo "╠═══════════════════════════════════════╣"
echo "║  URL:   http://localhost:8200        ║"
echo "║  UI:    http://localhost:8200/ui     ║"
echo "║  Token: bcm-root-token               ║"
echo "╚═══════════════════════════════════════╝"
echo ""
echo "🔧 Set environment variables:"
echo "export VAULT_ADDR=http://localhost:8200"
echo "export VAULT_TOKEN=bcm-root-token"
echo ""
echo "📚 Test connection:"
echo "vault status"
echo "vault kv put secret/test message='Hello from Vault'"
echo "vault kv get secret/test"
