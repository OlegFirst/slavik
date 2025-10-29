#!/bin/bash

echo "Making scripts executable..."

# Make launch script executable
chmod +x /Users/MD/ISO-22301/launch-bcm-platform.sh
echo "✅ Main launch script ready"

# Make user platform script executable  
chmod +x /Users/MD/ISO-22301/frontend/web_portal_enhanced/start-user-platform.sh
echo "✅ User platform script ready"

# Make admin panel check script executable
chmod +x /Users/MD/ISO-22301/frontend/admin_panel/check-services.sh
echo "✅ Admin panel service check ready"

echo ""
echo "🎉 BCM Platform Setup Complete!"
echo ""
echo "📋 What's ready:"
echo "   ✅ Admin Panel (React + TypeScript) - System monitoring & AI organisms"  
echo "   ✅ User Platform (Vue.js + TypeScript) - Business BCM interface"
echo "   ✅ Real API integrations - Connects to your running services"
echo "   ✅ Enhanced mock data - Works offline for development"  
echo "   ✅ Launch scripts - Easy startup options"
echo ""
echo "🚀 To start the platform:"
echo "   cd /Users/MD/ISO-22301"
echo "   ./launch-bcm-platform.sh"
echo ""
echo "🌐 Platform URLs (when running):"
echo "   • User Platform:  http://localhost:5173"
echo "   • Admin Panel:    http://localhost:3001"
echo ""
echo "💡 The platform adapts automatically:"
echo "   • Full integration when backend services are running"
echo "   • Enhanced mock data when services are offline"
echo "   • Real-time updates via WebSocket when available"
echo ""
