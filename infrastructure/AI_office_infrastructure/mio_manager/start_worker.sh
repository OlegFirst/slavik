#!/bin/bash
#
# Start Temporal Worker for MIO Manager v2.0
# ==========================================
#
# This script starts the Temporal Worker that executes MIO Manager workflows.
#
# Prerequisites:
# - Temporal Cloud configured (or local Temporal server running)
# - Environment variables in /Users/MD/AI-Platform-ISO/.env
# - Python dependencies installed
#
# Usage:
#   ./start_worker.sh
#

set -e

echo "🚀 Starting MIO Manager Temporal Worker..."

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if .env exists
if [ ! -f "/Users/MD/AI-Platform-ISO/.env" ]; then
    echo "❌ Error: /Users/MD/AI-Platform-ISO/.env not found"
    exit 1
fi

# Check if Temporal variables are set
source /Users/MD/AI-Platform-ISO/.env

if [ -z "$TEMPORAL_ADDRESS" ] || [ -z "$TEMPORAL_NAMESPACE" ]; then
    echo "❌ Error: TEMPORAL_ADDRESS or TEMPORAL_NAMESPACE not set in .env"
    exit 1
fi

echo "✅ Temporal configuration loaded"
echo "   Address: $TEMPORAL_ADDRESS"
echo "   Namespace: $TEMPORAL_NAMESPACE"

# Check Python dependencies
if ! python3 -c "import temporalio" 2>/dev/null; then
    echo "❌ Error: temporalio not installed"
    echo "   Run: pip3 install temporalio"
    exit 1
fi

# Run worker
echo ""
echo "🏃 Starting worker..."
python3 run_worker.py
