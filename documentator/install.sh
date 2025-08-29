#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo " ____                                   _        _             "
echo "| _ \  ___   ___ _   _ _ __ ___   ___ _ | |_ __ _| |_ ___  _ __ "
echo "| |_) |/ _ \ / __| | | | '_ \` _ \ / _ \| | __/ _\` | __/ _ \| '__|"
echo "| _ <| (_) | (__| |_| | | | | | |  __/ | | || (_| | || (_) | |   "
echo "|_| \_\\___/ \___|\__,_|_| |_| |_|\___|_| |\__\__,_|\__\___/|_|   "
echo ""
echo "One-Click Installer for Claude Desktop"
echo "====================================="
echo -e "${NC}"

# Check if Node.js is installed
echo "Checking for Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed!${NC}"
    echo ""
    echo "Please install Node.js first:"
    echo "https://nodejs.org/en/download/"
    echo ""
    
    # Try to help with installation
    if command -v brew &> /dev/null; then
        echo "On macOS with Homebrew:"
        echo "  brew install node"
    elif command -v apt-get &> /dev/null; then
        echo "On Ubuntu/Debian:"
        echo "  sudo apt-get install nodejs npm"
    elif command -v yum &> /dev/null; then
        echo "On CentOS/RHEL:"
        echo "  sudo yum install nodejs npm"
    fi
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Node.js found: $(node --version)${NC}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# First build the project
echo "Building Documentator..."
cd "$SCRIPT_DIR"

npm install
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to build project${NC}"
    exit 1
fi

# Run the simple installer
echo ""
echo "Starting installation..."
echo ""

node "$SCRIPT_DIR/simple-install.js"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 SUCCESS! Documentator is ready to use${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Installation encountered issues${NC}"
    echo "Check the output above for details"
    echo ""
fi

# On macOS/Linux, don't pause automatically
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Press any key to continue..."
    read -n 1 -s
fi