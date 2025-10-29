#!/bin/bash

echo "🔧 Quick Node.js Setup for BCM Project"
echo "====================================="

# Try to fix Homebrew PATH first
echo "📝 Setting up Homebrew PATH..."
export PATH="/opt/homebrew/bin:$PATH"

if command -v brew &> /dev/null; then
    echo "✅ Homebrew found, installing Node.js..."
    brew install node
    
    if [ $? -eq 0 ]; then
        echo "✅ Node.js installed via Homebrew!"
        export PATH="/opt/homebrew/bin:$PATH"
        node --version
        npm --version
    else
        echo "❌ Homebrew installation failed"
    fi
else
    echo "❌ Homebrew still not working"
    echo ""
    echo "🌐 Please install Node.js manually:"
    echo "1. Go to: https://nodejs.org/"
    echo "2. Download 'LTS' version for macOS"
    echo "3. Open the downloaded .pkg file"
    echo "4. Follow installation wizard"
    echo "5. Restart Terminal"
    echo ""
    echo "🐳 OR use Docker alternative:"
    echo "docker --version"
    if command -v docker &> /dev/null; then
        echo "✅ Docker found! You can use Docker instead:"
        echo ""
        echo "Run these commands:"
        echo "cd /Users/MD/ISO-22301/frontend/web_portal-2"
        echo "docker run -it --rm -v \"\$(pwd)\":/app -w /app -p 5173:5173 node:18-alpine sh"
        echo "# Then inside container:"
        echo "npm install"
        echo "npm run dev -- --host 0.0.0.0"
        echo "# Open: http://localhost:5173"
    else
        echo "❌ Docker not found either"
    fi
fi

echo ""
echo "🎯 After Node.js is working, run:"
echo "cd /Users/MD/ISO-22301/frontend/web_portal-2"
echo "npm install"
echo "npm run dev"
echo "# Then open: http://localhost:5173/modules/admin"
