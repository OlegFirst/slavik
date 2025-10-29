#!/bin/bash

echo "🚀 Запуск обновленной админ панели с 28 BCM модулями..."
echo "================================"

cd /Users/MD/ISO-22301/frontend/admin_panel

# Проверяем что все зависимости установлены
echo "📦 Проверка зависимостей..."
npm list --depth=0 > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  Устанавливаем зависимости..."
    npm install
fi

echo "✅ Зависимости готовы"

# Запускаем dev server
echo "🔥 Запуск development server..."
echo "URL: http://localhost:5173"
echo "Tab: ISO 22301 (6-й таб)"
echo ""
echo "🎯 Что проверить:"
echo "1. ✅ Показывает 28 модулей вместо 10"
echo "2. ✅ Реальные проценты соответствия (не все 0%)"
echo "3. ✅ Кнопки 'Open in Odoo' работают"
echo "4. ✅ Overall compliance ~59%"
echo "5. ✅ Critical gaps показывают реальные модули"
echo ""

npm run dev
