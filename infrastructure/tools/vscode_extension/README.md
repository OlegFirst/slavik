# BCM AI DevOps VSCode Extension

**Extracted from:** `/intelligent-core/tools/vscode-extension/` (Oct 4, 2025)
**Status:** Development tool (working)
**Lines of code:** 111 (JavaScript)

## What it does
VSCode extension that provides AI-powered DevOps assistance directly in the editor. Integrates with the BCM AI Orchestrator to analyze configurations, provide intelligent suggestions, and enable interactive chat with AI about DevOps tasks.

## Integration points
- **AI Orchestrator:** Connects to `http://localhost:8000` (configurable)
  - Configuration analysis
  - AI-powered suggestions
  - Interactive chat capabilities
- **Supabase:** Stores conversation memory and context
- **VSCode API:** Editor integration and commands
- **Database:** Indirect via AI Orchestrator

## Dependencies
- VSCode Engine: ^1.80.0
- No external npm dependencies (uses VSCode built-ins)

## Key Features
- Context-aware configuration analysis
- AI chat assistant for DevOps tasks
- Docker-compose specific intelligence
- Configuration suggestions and best practices
- Memory-enabled conversations via Supabase
- Right-click context menu integration

## Activation
- Automatically activates in workspaces containing `docker-compose.yml`
- Can be manually triggered via command palette

## Commands
- `BCM AI: Analyze Configuration` - Analyze current config file
- `BCM AI: Chat with AI DevOps` - Open AI chat assistant

## Configuration
```json
{
  "bcm.aiOrchestrator": "http://localhost:8000"
}
```

## How to install
```bash
# Development mode
cd /Users/MD/AI-Platform-ISO/tools/vscode-extension
code --install-extension .

# Or via VSCode
# 1. Open VSCode
# 2. Press F5 to launch Extension Development Host
# 3. Test the extension in the new window
```

## How to package
```bash
# Install vsce
npm install -g @vscode/vsce

# Package extension
vsce package

# This creates bcm-ai-devops-1.0.0.vsix
```

## Future enhancements
- Multi-language support
- More AI-powered DevOps commands
- Real-time deployment monitoring
- Intelligent error detection
- Auto-completion for BCM configurations
