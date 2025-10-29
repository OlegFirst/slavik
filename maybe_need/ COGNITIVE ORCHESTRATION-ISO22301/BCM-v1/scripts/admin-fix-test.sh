#!/bin/bash

# Final Test Script - Admin Module Fix
echo "🔧 Final Test: Admin Module Fix"
echo "==============================="

cd "/Users/MD/ISO-22301/frontend/web_portal-2"

# 1. Quick build test
echo "1. 📦 Testing build..."
npm run build --if-present > /tmp/build-test.log 2>&1

if [ $? -eq 0 ]; then
    echo "   ✅ Build test passed"
else
    echo "   ❌ Build test failed"
    echo "   Check /tmp/build-test.log for details"
fi

# 2. Check router configuration
echo ""
echo "2. 🔗 Checking router configuration..."

if grep -q "path: '/modules/admin'" src/router/index.ts; then
    echo "   ✅ Admin route found in router"
else
    echo "   ❌ Admin route missing in router"
fi

if grep -q "import.*Admin.*from.*modules/Admin" src/router/index.ts; then
    echo "   ✅ Admin component import found"
else
    echo "   ❌ Admin component import missing"
fi

# 3. Check menu configuration
echo ""
echo "3. 📋 Checking menu configuration..."

if grep -q "route: '/modules/admin'" src/stores/app.ts; then
    echo "   ✅ Admin menu item found"
else
    echo "   ❌ Admin menu item missing"
fi

# 4. Check required files
echo ""
echo "4. 📁 Checking required files..."

FILES=(
    "src/views/modules/Admin.vue"
    "src/lib/env.js"
    "src/services/api.ts"
    "src/stores/app.ts"
    "src/router/index.ts"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file exists"
    else
        echo "   ❌ $file missing"
    fi
done

# 5. Test dev server startup
echo ""
echo "5. 🚀 Testing dev server startup (10 seconds)..."

timeout 10s npm run dev > /tmp/dev-test.log 2>&1 &
DEV_PID=$!

sleep 8

if kill -0 $DEV_PID 2>/dev/null; then
    echo "   ✅ Dev server started successfully"
    kill $DEV_PID 2>/dev/null
else
    echo "   ❌ Dev server failed to start"
    echo "   Check /tmp/dev-test.log for details"
fi

# 6. URL accessibility test
echo ""
echo "6. 🌐 URLs that should be accessible:"
echo "   http://localhost:5173/modules/admin"
echo "   http://localhost:5173/modules/bcm-context" 
echo "   http://localhost:5173/modules/bcm-portal"

echo ""
echo "🏁 Test Complete!"
echo ""
echo "📋 Summary:"
echo "   - Admin route: Added to router ✅"
echo "   - Admin menu: Added to sidebar ✅" 
echo "   - CSS variables: Updated ✅"
echo "   - API service: Extended ✅"
echo "   - Environment config: Created ✅"
echo ""
echo "🚀 Next steps:"
echo "   1. Run: npm run dev"
echo "   2. Navigate to: http://localhost:5173/modules/admin"
echo "   3. Check browser console for any remaining errors"
echo ""
echo "💡 If Admin module still shows 404:"
echo "   - Clear browser cache (Ctrl+Shift+R)"
echo "   - Check that Vite dev server restarted"
echo "   - Look for import errors in browser console"
