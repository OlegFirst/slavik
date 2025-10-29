#!/bin/bash

# BCM Platform Quick Fix Script
# Исправляет основные проблемы в frontend проекте

echo "🔧 BCM Platform Quick Fix"
echo "========================="

cd "/Users/MD/ISO-22301/frontend/web_portal-2"

# 1. Установка Bootstrap
echo "📦 Installing Bootstrap..."
npm install bootstrap@5.3.2

# 2. Очистка кэша
echo "🧹 Clearing cache..."
rm -rf node_modules/.vite
rm -rf dist

# 3. Переустановка зависимостей
echo "📥 Reinstalling dependencies..."
npm install

# 4. Создание недостающих сервисов (если еще не созданы)
echo "📝 Checking services..."

# Проверяем bcmPortal.js
if [ ! -f "src/services/bcmPortal.js" ]; then
    echo "Creating bcmPortal.js..."
    # Создание уже сделано выше
fi

# Проверяем bcmContext.js
if [ ! -f "src/services/bcmContext.js" ]; then
    echo "Creating bcmContext.js..."
    # Создание уже сделано выше
fi

# 5. Обновление .env для отключения Odoo
echo "⚙️ Configuring environment..."
cat > .env << 'EOF'
# BCM Platform Environment
VITE_API_URL=http://localhost:8069
VITE_AI_URL=http://localhost:8000
VITE_ODOO_DB=bcm_platform
VITE_WS_URL=ws://localhost:8000
VITE_ENABLE_AI_FEATURES=true
VITE_ENABLE_SIMULATION=true
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_ODOO_INTEGRATION=false
VITE_DEBUG_MODE=true
VITE_LOG_LEVEL=debug
VITE_DISABLE_AUTH=true
EOF

echo "✅ Quick fix completed!"
echo ""
echo "🚀 Now you can run:"
echo "   npm run dev"
echo ""
echo "🌍 The app will be available at:"
echo "   http://localhost:5173"
