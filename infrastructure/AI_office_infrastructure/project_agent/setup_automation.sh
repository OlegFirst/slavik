#!/bin/bash
# Setup script for Project Agent automation
# This script configures all automation components

set -e  # Exit on error

PROJECT_ROOT="/Users/MD/AI-Platform-ISO"
PROJECT_AGENT_DIR="$PROJECT_ROOT/infrastructure/AI-office-infrastructure/project-agent"

echo "=================================================="
echo "🚀 Project Agent Automation Setup"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Step 1: Install project-agent
echo ""
print_info "Step 1: Installing Project Agent..."
cd "$PROJECT_AGENT_DIR"

if pip install -e . > /dev/null 2>&1; then
    print_success "Project Agent installed"
else
    print_error "Failed to install Project Agent"
    exit 1
fi

# Step 2: Install dependencies
echo ""
print_info "Step 2: Installing dependencies..."
if pip install -r requirements.txt > /dev/null 2>&1; then
    print_success "Dependencies installed"
else
    print_warning "Some dependencies failed to install"
fi

# Step 3: Install pre-commit
echo ""
print_info "Step 3: Installing pre-commit..."
if pip install pre-commit > /dev/null 2>&1; then
    print_success "Pre-commit installed"
else
    print_error "Failed to install pre-commit"
    exit 1
fi

# Step 4: Setup pre-commit hooks
echo ""
print_info "Step 4: Setting up pre-commit hooks..."
cd "$PROJECT_ROOT"

if pre-commit install; then
    print_success "Pre-commit hooks installed"
else
    print_error "Failed to install pre-commit hooks"
    exit 1
fi

# Step 5: Create secrets baseline for detect-secrets
echo ""
print_info "Step 5: Creating secrets baseline..."
if detect-secrets scan --baseline .secrets.baseline > /dev/null 2>&1; then
    print_success "Secrets baseline created"
else
    print_warning "Secrets baseline creation skipped (detect-secrets not installed)"
fi

# Step 6: Create systemd service for code watcher (Linux only)
echo ""
print_info "Step 6: Setting up code watcher service..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    SERVICE_FILE="/etc/systemd/system/project-agent-watcher.service"

    sudo bash -c "cat > $SERVICE_FILE" << EOF
[Unit]
Description=Project Agent Code Watcher
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_AGENT_DIR
ExecStart=/usr/bin/python3 $PROJECT_AGENT_DIR/code_watcher.py --project-root $PROJECT_ROOT
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    print_success "Systemd service created: $SERVICE_FILE"
    print_info "To start: sudo systemctl start project-agent-watcher"
    print_info "To enable on boot: sudo systemctl enable project-agent-watcher"

elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS LaunchAgent
    PLIST_FILE="$HOME/Library/LaunchAgents/com.ai-platform.project-agent-watcher.plist"
    mkdir -p "$HOME/Library/LaunchAgents"

    cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ai-platform.project-agent-watcher</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$PROJECT_AGENT_DIR/code_watcher.py</string>
        <string>--project-root</string>
        <string>$PROJECT_ROOT</string>
        <string>--config</string>
        <string>$PROJECT_AGENT_DIR/watcher_config.json</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$PROJECT_AGENT_DIR/watcher.log</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_AGENT_DIR/watcher.error.log</string>
</dict>
</plist>
EOF

    print_success "LaunchAgent created: $PLIST_FILE"
    print_info "To start: launchctl load $PLIST_FILE"
    print_info "To stop: launchctl unload $PLIST_FILE"
else
    print_warning "Automatic service setup not supported on this OS"
    print_info "Run manually: python $PROJECT_AGENT_DIR/code_watcher.py"
fi

# Step 7: Create helper scripts
echo ""
print_info "Step 7: Creating helper scripts..."

# Start watcher script
cat > "$PROJECT_AGENT_DIR/start_watcher.sh" << 'EOF'
#!/bin/bash
# Start the code watcher service

PROJECT_AGENT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_AGENT_DIR"

echo "🚀 Starting Project Agent Code Watcher..."
python3 code_watcher.py --project-root /Users/MD/AI-Platform-ISO --config watcher_config.json
EOF

chmod +x "$PROJECT_AGENT_DIR/start_watcher.sh"
print_success "Created: start_watcher.sh"

# Stop watcher script (for macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    cat > "$PROJECT_AGENT_DIR/stop_watcher.sh" << EOF
#!/bin/bash
# Stop the code watcher service (macOS)

PLIST_FILE="$HOME/Library/LaunchAgents/com.ai-platform.project-agent-watcher.plist"

if launchctl list | grep -q "com.ai-platform.project-agent-watcher"; then
    launchctl unload "\$PLIST_FILE"
    echo "✅ Code watcher stopped"
else
    echo "⚠️  Code watcher is not running"
fi
EOF

    chmod +x "$PROJECT_AGENT_DIR/stop_watcher.sh"
    print_success "Created: stop_watcher.sh"
fi

# Manual test generation script
cat > "$PROJECT_AGENT_DIR/generate_tests.sh" << 'EOF'
#!/bin/bash
# Manually generate tests for specific file or directory

if [ -z "$1" ]; then
    echo "Usage: ./generate_tests.sh <file_or_directory>"
    exit 1
fi

python3 -m agent.test_generator --file "$1"
EOF

chmod +x "$PROJECT_AGENT_DIR/generate_tests.sh"
print_success "Created: generate_tests.sh"

# Step 8: Test the setup
echo ""
print_info "Step 8: Testing setup..."

# Test project-agent CLI
if python -m agent.cli --help > /dev/null 2>&1; then
    print_success "Project Agent CLI is working"
else
    print_warning "Project Agent CLI test failed"
fi

# Test pre-commit
if pre-commit run --all-files --show-diff-on-failure > /dev/null 2>&1; then
    print_success "Pre-commit hooks are working"
else
    print_warning "Pre-commit hooks need configuration"
fi

# Final summary
echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Start the code watcher:"
echo "   $PROJECT_AGENT_DIR/start_watcher.sh"
echo ""
echo "2. Or load as LaunchAgent (macOS):"
echo "   launchctl load ~/Library/LaunchAgents/com.ai-platform.project-agent-watcher.plist"
echo ""
echo "3. Pre-commit hooks are installed and will run automatically"
echo "   Test with: pre-commit run --all-files"
echo ""
echo "4. GitHub Actions workflow is configured in:"
echo "   .github/workflows/project-agent-automation.yml"
echo ""
echo "5. Configuration file:"
echo "   $PROJECT_AGENT_DIR/watcher_config.json"
echo ""
echo "=================================================="
