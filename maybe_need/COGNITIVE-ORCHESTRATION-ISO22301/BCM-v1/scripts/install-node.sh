#!/bin/bash

# Node.js Installation Helper for macOS
echo "🚀 Node.js Installation Helper"
echo "============================="

# Check if Node.js is already installed
if command -v node &> /dev/null; then
    echo "✅ Node.js is already installed:"
    echo "   Node version: $(node --version)"
    echo "   npm version: $(npm --version)"
    echo ""
    echo "You can now run:"
    echo "   cd /Users/MD/ISO-22301/frontend/web_portal-2"
    echo "   npm install"
    echo "   npm run dev"
    exit 0
fi

echo "❌ Node.js not found. Installing..."
echo ""

# Check if Homebrew is installed
if command -v brew &> /dev/null; then
    echo "📦 Installing Node.js via Homebrew..."
    brew install node
    
    if [ $? -eq 0 ]; then
        echo "✅ Node.js installed successfully!"
        echo "   Node version: $(node --version)"
        echo "   npm version: $(npm --version)"
    else
        echo "❌ Homebrew installation failed"
    fi
else
    echo "❌ Homebrew not found"
    echo ""
    echo "📋 Manual installation options:"
    echo ""
    echo "1. 🌐 Download from official website:"
    echo "   - Go to: https://nodejs.org/"
    echo "   - Download LTS version for macOS"
    echo "   - Install the .pkg file"
    echo ""
    echo "2. 📦 Install Homebrew first, then Node.js:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo "   brew install node"
    echo ""
    echo "3. 🐳 Use Docker (if you have Docker installed):"
    echo "   docker run -it --rm -v \"\$(pwd)\":/app -w /app -p 5173:5173 node:18 bash"
    echo "   npm install"
    echo "   npm run dev -- --host 0.0.0.0"
fi

echo ""
echo "🏁 After Node.js installation, run:"
echo "   cd /Users/MD/ISO-22301/frontend/web_portal-2"
echo "   npm install"
echo "   npm run dev"
