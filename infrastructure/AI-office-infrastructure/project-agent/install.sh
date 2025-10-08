#!/bin/bash
# Project Agent — Quick Install Script

set -e

echo "🚀 Project Agent — Installation"
echo "================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
echo "✓ Python $PYTHON_VERSION found"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Project Agent
echo ""
echo "Installing Project Agent..."
pip install -e .

# Verify installation
echo ""
echo "Verifying installation..."
if command -v project-agent &> /dev/null; then
    echo "✓ Project Agent installed successfully"
    project-agent --help | head -5
else
    echo "❌ Installation failed"
    exit 1
fi

echo ""
echo "================================"
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Activate environment: source .venv/bin/activate"
echo "  2. Go to your project: cd /path/to/your/project"
echo "  3. Initialize: export REPO_PATH=\$(pwd) && project-agent init"
echo "  4. Scan: project-agent scan"
echo ""
echo "Or try the test project:"
echo "  cd test-project"
echo "  export REPO_PATH=\$(pwd)"
echo "  project-agent scan"
echo ""
echo "For more info: cat QUICKSTART.md"
