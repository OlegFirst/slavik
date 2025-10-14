#!/bin/bash

# NASH Digital Twin Desktop Extension Builder
# Creates .dxt file for Claude Desktop

echo "========================================="
echo "  Building NASH Digital Twin Extension"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "desktop-extension/manifest.json" ]; then
    echo "Error: manifest.json not found. Please run from module-system/digital-twin-module directory"
    exit 1
fi

echo -e "${YELLOW}Step 1: Preparing build directory...${NC}"
rm -rf build
mkdir -p build/nash-digital-twin
cp -r desktop-extension/* build/nash-digital-twin/

echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"
cd build/nash-digital-twin/server
npm install --production
cd ../../..

echo -e "${YELLOW}Step 3: Creating icon if missing...${NC}"
if [ ! -f "build/nash-digital-twin/assets/icon.png" ]; then
    mkdir -p build/nash-digital-twin/assets
    # Create a simple icon using ImageMagick if available
    if command -v convert &> /dev/null; then
        convert -size 256x256 xc:white \
            -fill '#667eea' \
            -draw "rectangle 0,0 256,256" \
            -fill white \
            -pointsize 120 \
            -gravity center \
            -annotate +0+0 "DT" \
            build/nash-digital-twin/assets/icon.png
        echo "Created icon.png"
    else
        echo "ImageMagick not found, skipping icon creation"
        # Create placeholder
        echo "Icon placeholder" > build/nash-digital-twin/assets/icon.png
    fi
fi

echo -e "${YELLOW}Step 4: Creating CHANGELOG...${NC}"
cat > build/nash-digital-twin/CHANGELOG.md << 'EOF'
# Changelog

## Version 3.0.0 (2024)
- Initial Desktop Extension release
- 30 simulation experiments
- AI-powered analysis
- Full MCP protocol support
- Demo mode available

## Version 2.0.0
- Added external simulation adapters
- Improved performance
- Enhanced reporting

## Version 1.0.0
- Initial release
EOF

echo -e "${YELLOW}Step 5: Creating .dxt package...${NC}"
cd build
# Create the .dxt file (which is actually a ZIP archive)
zip -r nash-digital-twin.dxt nash-digital-twin -x "*.DS_Store" -x "*node_modules/.cache/*"
cd ..

# Move the .dxt file to the main directory
mv build/nash-digital-twin.dxt ./nash-digital-twin.dxt

echo -e "${GREEN}✅ Build complete!${NC}"
echo ""
echo "Desktop Extension created: nash-digital-twin.dxt"
echo "Size: $(du -h nash-digital-twin.dxt | cut -f1)"
echo ""
echo "Installation instructions:"
echo "1. Open Claude Desktop"
echo "2. Drag and drop nash-digital-twin.dxt into Claude Desktop"
echo "3. Follow the configuration prompts"
echo ""
echo "Or distribute to colleagues who can install with:"
echo "- Double-click on nash-digital-twin.dxt"
echo "- Or drag into Claude Desktop"

# Cleanup
read -p "Clean up build directory? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf build
    echo "Build directory cleaned"
fi

echo -e "${GREEN}Done!${NC}"