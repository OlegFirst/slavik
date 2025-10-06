#!/bin/bash
# AI-Platform-ISO: Automated Analysis Toolkit Setup
# Время выполнения: ~5 минут

set -e

echo "🚀 AI-Platform-ISO Analysis Toolkit Setup"
echo "========================================="

# 1. Создать структуру папок
echo "📁 Creating directory structure..."
mkdir -p tools/{analyzers,generators,dashboards,reports,config}
mkdir -p docs/{api,scenarios,architecture}

# 2. Установить все инструменты
echo "📦 Installing analysis tools..."
pip3 install --upgrade pip

# Static analysis
pip3 install radon pylint bandit prospector

# Dependency mapping
pip3 install pipdeptree networkx matplotlib

# Visualization
pip3 install plotly kaleido

# Documentation
pip3 install sphinx sphinx-rtd-theme pydoc-markdown

# API testing
pip3 install tavern[pytest] httpx

# Additional utilities
pip3 install pyyaml jinja2 graphviz

echo "✅ All tools installed!"

# 3. Проверить установку
echo ""
echo "🔍 Verifying installations..."
python3 -c "import radon; import pylint; import bandit; import networkx; import plotly; print('✅ All imports successful!')"

# 4. Создать конфигурацию
echo ""
echo "⚙️  Creating default configuration..."
cat > tools/config/analysis_config.yaml << 'EOF'
# AI-Platform-ISO Analysis Configuration

# Directories to scan
scan_paths:
  - platform-services/validation-service
  - platform-services/documents-service
  - platform-services/governance-service
  - platform-services/incident-service
  - shared

# Exclude patterns
exclude:
  - "*/venv/*"
  - "*/__pycache__/*"
  - "*/migrations/*"
  - "*/.pytest_cache/*"

# Analysis settings
complexity:
  max_cyclomatic: 10
  max_cognitive: 15
  warn_threshold: 5

security:
  confidence_level: "HIGH"
  severity_level: "MEDIUM"

# Output formats
reports:
  formats: ["json", "html", "markdown"]
  output_dir: "tools/reports"

# Documentation
docs:
  api_format: "openapi"
  include_examples: true
  auto_generate_ui: true
EOF

echo "✅ Configuration created: tools/config/analysis_config.yaml"

# 5. Готово
echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Next steps:"
echo "  1. Run full analysis: ./tools/run_analysis.sh"
echo "  2. View dashboard: python tools/dashboards/module_dashboard.py"
echo "  3. Generate docs: python tools/generators/api_docs_generator.py"
echo ""
