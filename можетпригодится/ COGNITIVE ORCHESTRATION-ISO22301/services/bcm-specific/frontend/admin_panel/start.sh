#!/bin/bash

# BCM Admin Control Center - Quick Start Script

set -e

echo "🎛️  BCM Admin Control Center - Quick Start"
echo "=========================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm 9+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version is $NODE_VERSION. Please upgrade to Node.js 18 or higher."
    exit 1
fi

echo "✅ Node.js $(node -v) detected"
echo "✅ npm $(npm -v) detected"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo "✅ Dependencies installed"
fi

# Start development server
echo ""
echo "🚀 Starting BCM Admin Control Center..."
echo ""
echo "🌐 Access Points:"
echo "   Admin Dashboard: http://localhost:3001"
echo "   BCM Platform:    http://localhost:8069 (if running)"
echo "   AI Orchestrator: http://localhost:8000 (if running)"
echo "   Grafana:         http://localhost:3000 (if running)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the development server
npm run dev

echo ""
echo "👋 BCM Admin Control Center stopped"
