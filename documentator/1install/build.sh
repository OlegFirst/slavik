#!/bin/bash
# Digital Office Hub Installer Build Script (Linux/macOS)
# Builds the installer exe from source

echo "Digital Office Hub - Installer Build"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js is not installed${NC}"
    echo "Please install Node.js from https://nodejs.org"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}ERROR: npm is not installed${NC}"
    exit 1
fi

echo -e "${BLUE}[1/4] Installing dependencies...${NC}"
npm install
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to install dependencies${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}[2/4] Copying main project files...${NC}"
# Copy necessary files from main project
mkdir -p temp-build
cp -r ../src temp-build/
cp ../package.json temp-build/
cp ../tsconfig.json temp-build/
if [ -f "../README.md" ]; then
    cp ../README.md temp-build/
fi

echo ""
echo -e "${BLUE}[3/4] Building installer executable...${NC}"
npm run build:installer
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to build installer${NC}"
    echo "Check the error messages above"
    exit 1
fi

echo ""
echo -e "${BLUE}[4/4] Cleaning up temporary files...${NC}"
if [ -d "temp-build" ]; then
    rm -rf temp-build
fi

echo ""
echo -e "${GREEN}✅ Build completed successfully!${NC}"
echo ""
echo "The installer executable has been created in the 'dist' folder."
echo "You can distribute this file to install Digital Office Hub on other computers."
echo ""

if [ -f "dist/Digital Office Hub Setup.exe" ]; then
    echo "Installer location: dist/Digital Office Hub Setup.exe"
    echo "File size: $(du -h "dist/Digital Office Hub Setup.exe" | cut -f1)"
else
    echo -e "${RED}WARNING: Installer file not found in expected location${NC}"
fi

echo ""