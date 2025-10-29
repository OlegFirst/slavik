#!/bin/bash

# 🧱 СБОРКА LEGO КОМПОНЕНТОВ
# Собираем все компоненты по названиям в папку lego

echo "================================================"
echo "🧱 СБОРКА LEGO КОМПОНЕНТОВ"
echo "================================================"
echo ""

# Базовая папка для LEGO
LEGO_DIR="/Users/MD/COGNITIVE ORCHESTRATION-ISO22301/BCM-v1/lego"

# Создаем структуру папок
echo "📁 Создаем структуру LEGO папок..."

mkdir -p "$LEGO_DIR"/{orchestrators,event-bus,gateways,auth,notifications,monitoring,document-processors,workflow,ai-services,databases,integrations,bridges,adapters,simulators,digital-twin,tools,bcm-modules}

echo "✅ Структура создана"
echo ""

# ==================================
# СОБИРАЕМ ORCHESTRATORS
# ==================================
echo "🎯 Собираем все orchestrator'ы..."
mkdir -p "$LEGO_DIR/orchestrators"

# Backend orchestrators
[ -d "BCM-v1/backend/orchestrator" ] && cp -r BCM-v1/backend/orchestrator "$LEGO_DIR/orchestrators/backend-orchestrator"
[ -d "BCM-v1/backend/orchestrator_service" ] && cp -r BCM-v1/backend/orchestrator_service "$LEGO_DIR/orchestrators/backend-orchestrator-service"

# Services orchestrators
[ -d "BCM-v1/services/ai_orchestrator" ] && cp -r BCM-v1/services/ai_orchestrator "$LEGO_DIR/orchestrators/ai-orchestrator"
[ -d "BCM-v1/services/scenario_orchestrator" ] && cp -r BCM-v1/services/scenario_orchestrator "$LEGO_DIR/orchestrators/scenario-orchestrator"
[ -d "BCM-v1/services/platform-orchestrator" ] && cp -r BCM-v1/services/platform-orchestrator "$LEGO_DIR/orchestrators/platform-orchestrator"

# Platform-framework orchestrator
[ -d "platform-framework/orchestrator" ] && cp -r platform-framework/orchestrator "$LEGO_DIR/orchestrators/cognitive-orchestrator"

# AI-core orchestrators
[ -d "ai-core/services/ai-consultant" ] && cp -r ai-core/services/ai-consultant "$LEGO_DIR/orchestrators/ai-consultant"

echo "  ✅ Orchestrators собраны"

# ==================================
# СОБИРАЕМ EVENT BUS
# ==================================
echo "🚌 Собираем все event-bus..."
mkdir -p "$LEGO_DIR/event-bus"

[ -d "BCM-v1/backend/eventbus" ] && cp -r BCM-v1/backend/eventbus "$LEGO_DIR/event-bus/backend-eventbus"
[ -d "platform-framework/event-bus" ] && cp -r platform-framework/event-bus "$LEGO_DIR/event-bus/platform-eventbus"
[ -d "core/event-system" ] && cp -r core/event-system "$LEGO_DIR/event-bus/core-event-system"

echo "  ✅ Event Bus собраны"

# ==================================
# СОБИРАЕМ GATEWAYS
# ==================================
echo "🚪 Собираем все gateway..."
mkdir -p "$LEGO_DIR/gateways"

[ -d "BCM-v1/integrations/gateway" ] && cp -r BCM-v1/integrations/gateway "$LEGO_DIR/gateways/integrations-gateway"
[ -d "BCM-v1/services/unified_api_gateway" ] && cp -r BCM-v1/services/unified_api_gateway "$LEGO_DIR/gateways/unified-api-gateway"
[ -d "BCM-v1/services/unified_database_gateway" ] && cp -r BCM-v1/services/unified_database_gateway "$LEGO_DIR/gateways/database-gateway"
[ -d "platform-framework/api-gateway" ] && cp -r platform-framework/api-gateway "$LEGO_DIR/gateways/platform-api-gateway"
[ -d "BCM-v1/api" ] && cp -r BCM-v1/api "$LEGO_DIR/gateways/bcm-api"

echo "  ✅ Gateways собраны"

# ==================================
# СОБИРАЕМ AUTH SERVICES
# ==================================
echo "🔐 Собираем все auth..."
mkdir -p "$LEGO_DIR/auth"

[ -d "BCM-v1/backend/auth_service" ] && cp -r BCM-v1/backend/auth_service "$LEGO_DIR/auth/backend-auth"
[ -d "platform-framework/auth-service" ] && cp -r platform-framework/auth-service "$LEGO_DIR/auth/platform-auth"

echo "  ✅ Auth services собраны"

# ==================================
# СОБИРАЕМ NOTIFICATIONS
# ==================================
echo "📢 Собираем все notifications..."
mkdir -p "$LEGO_DIR/notifications"

[ -d "BCM-v1/backend/notification_service" ] && cp -r BCM-v1/backend/notification_service "$LEGO_DIR/notifications/backend-notification"
[ -d "BCM-v1/services/notification_service" ] && cp -r BCM-v1/services/notification_service "$LEGO_DIR/notifications/services-notification"
[ -d "platform-framework/notification-service" ] && cp -r platform-framework/notification-service "$LEGO_DIR/notifications/platform-notification"

echo "  ✅ Notifications собраны"

# ==================================
# СОБИРАЕМ MONITORING
# ==================================
echo "📊 Собираем все monitoring..."
mkdir -p "$LEGO_DIR/monitoring"

[ -d "BCM-v1/services/monitoring_service" ] && cp -r BCM-v1/services/monitoring_service "$LEGO_DIR/monitoring/services-monitoring"
[ -d "BCM-v1/monitoring" ] && cp -r BCM-v1/monitoring "$LEGO_DIR/monitoring/bcm-monitoring"
[ -d "platform-framework/monitoring" ] && cp -r platform-framework/monitoring "$LEGO_DIR/monitoring/platform-monitoring"
[ -d "platform-framework/monitoring-bcm" ] && cp -r platform-framework/monitoring-bcm "$LEGO_DIR/monitoring/platform-monitoring-bcm"
[ -d "BCM-v1/backend/grafana_adapter" ] && cp -r BCM-v1/backend/grafana_adapter "$LEGO_DIR/monitoring/grafana-adapter"

echo "  ✅ Monitoring собраны"

# ==================================
# СОБИРАЕМ DOCUMENT PROCESSORS
# ==================================
echo "📄 Собираем все document processors..."
mkdir -p "$LEGO_DIR/document-processors"

[ -d "BCM-v1/backend/document_processor" ] && cp -r BCM-v1/backend/document_processor "$LEGO_DIR/document-processors/backend-doc-processor"
[ -d "BCM-v1/services/document_processor" ] && cp -r BCM-v1/services/document_processor "$LEGO_DIR/document-processors/services-doc-processor"
[ -d "BCM-v1/services/document_management" ] && cp -r BCM-v1/services/document_management "$LEGO_DIR/document-processors/doc-management"
[ -d "BCM-v1/adapters/document-processor" ] && cp -r BCM-v1/adapters/document-processor "$LEGO_DIR/document-processors/adapter-doc-processor"
[ -d "platform-framework/document-processor" ] && cp -r platform-framework/document-processor "$LEGO_DIR/document-processors/platform-doc-processor"
[ -d "BCM-v1/services/domain/document-processor" ] && cp -r BCM-v1/services/domain/document-processor "$LEGO_DIR/document-processors/domain-doc-processor"

echo "  ✅ Document processors собраны"

# ==================================
# СОБИРАЕМ WORKFLOW/BPMN
# ==================================
echo "⚙️ Собираем все workflow/bpmn..."
mkdir -p "$LEGO_DIR/workflow"

[ -d "BCM-v1/backend/bpmn_service" ] && cp -r BCM-v1/backend/bpmn_service "$LEGO_DIR/workflow/backend-bpmn"
[ -d "platform-framework/services/bpmn_service" ] && cp -r platform-framework/services/bpmn_service "$LEGO_DIR/workflow/platform-bpmn"
[ -d "core/workflow-engine" ] && cp -r core/workflow-engine "$LEGO_DIR/workflow/core-workflow-engine"

echo "  ✅ Workflow/BPMN собраны"

# ==================================
# СОБИРАЕМ AI SERVICES
# ==================================
echo "🤖 Собираем все AI services..."
mkdir -p "$LEGO_DIR/ai-services"

[ -d "BCM-v1/services/ai_control_center" ] && cp -r BCM-v1/services/ai_control_center "$LEGO_DIR/ai-services/ai-control-center"
[ -d "BCM-v1/services/ai_workflow_optimizer" ] && cp -r BCM-v1/services/ai_workflow_optimizer "$LEGO_DIR/ai-services/ai-workflow-optimizer"
[ -d "BCM-v1/services/ai-consultant" ] && cp -r BCM-v1/services/ai-consultant "$LEGO_DIR/ai-services/ai-consultant"
[ -d "BCM-v1/services/process_mining_service" ] && cp -r BCM-v1/services/process_mining_service "$LEGO_DIR/ai-services/process-mining"
[ -d "ai-core/services" ] && cp -r ai-core/services/* "$LEGO_DIR/ai-services/"

echo "  ✅ AI services собраны"

# ==================================
# СОБИРАЕМ INTEGRATIONS
# ==================================
echo "🔌 Собираем все integrations..."
mkdir -p "$LEGO_DIR/integrations"

[ -d "BCM-v1/integrations/thehive" ] && cp -r BCM-v1/integrations/thehive "$LEGO_DIR/integrations/thehive"
[ -d "BCM-v1/integrations/lms" ] && cp -r BCM-v1/integrations/lms "$LEGO_DIR/integrations/lms"
[ -d "BCM-v1/integrations/moodle" ] && cp -r BCM-v1/integrations/moodle "$LEGO_DIR/integrations/moodle"
[ -d "BCM-v1/integrations/governance" ] && cp -r BCM-v1/integrations/governance "$LEGO_DIR/integrations/governance"
[ -d "BCM-v1/integrations/opengrc_oscal" ] && cp -r BCM-v1/integrations/opengrc_oscal "$LEGO_DIR/integrations/oscal"
[ -d "BCM-v1/integrations/nginx" ] && cp -r BCM-v1/integrations/nginx "$LEGO_DIR/integrations/nginx"

echo "  ✅ Integrations собраны"

# ==================================
# СОБИРАЕМ ADAPTERS
# ==================================
echo "🔄 Собираем все adapters..."
mkdir -p "$LEGO_DIR/adapters"

[ -d "BCM-v1/backend/thehive_adapter" ] && cp -r BCM-v1/backend/thehive_adapter "$LEGO_DIR/adapters/thehive-adapter"
[ -d "BCM-v1/backend/lms_adapter" ] && cp -r BCM-v1/backend/lms_adapter "$LEGO_DIR/adapters/lms-adapter"
[ -d "BCM-v1/adapters" ] && cp -r BCM-v1/adapters/* "$LEGO_DIR/adapters/"

echo "  ✅ Adapters собраны"

# ==================================
# СОБИРАЕМ BRIDGES
# ==================================
echo "🌉 Собираем все bridges..."
mkdir -p "$LEGO_DIR/bridges"

[ -d "BCM-v1/sandbox/golden-pr-26-modules/bcm_ai_bridge" ] && cp -r BCM-v1/sandbox/golden-pr-26-modules/bcm_ai_bridge "$LEGO_DIR/bridges/ai-bridge"
[ -d "BCM-v1/sandbox/golden-pr-26-modules/bcm_microservices_bridge" ] && cp -r BCM-v1/sandbox/golden-pr-26-modules/bcm_microservices_bridge "$LEGO_DIR/bridges/microservices-bridge"
[ -d "BCM-v1/services/bcm_content_training_bridge" ] && cp -r BCM-v1/services/bcm_content_training_bridge "$LEGO_DIR/bridges/training-bridge"
[ -d "BCM-v1/services/crm_bridge" ] && cp -r BCM-v1/services/crm_bridge "$LEGO_DIR/bridges/crm-bridge"

echo "  ✅ Bridges собраны"

# ==================================
# СОБИРАЕМ DIGITAL TWIN
# ==================================
echo "👥 Собираем digital twin..."
mkdir -p "$LEGO_DIR/digital-twin"

[ -d "BCM-v1/services/digital-twin-platform" ] && cp -r BCM-v1/services/digital-twin-platform "$LEGO_DIR/digital-twin/platform"
[ -d "BCM-v1/services/digital-twin-engine" ] && cp -r BCM-v1/services/digital-twin-engine "$LEGO_DIR/digital-twin/engine"

echo "  ✅ Digital twin собраны"

# ==================================
# СОБИРАЕМ BCM MODULES
# ==================================
echo "📦 Собираем BCM modules..."
mkdir -p "$LEGO_DIR/bcm-modules"

[ -d "BCM-v1/services/bia_engine" ] && cp -r BCM-v1/services/bia_engine "$LEGO_DIR/bcm-modules/bia-engine"
[ -d "BCM-v1/services/compliance_checker" ] && cp -r BCM-v1/services/compliance_checker "$LEGO_DIR/bcm-modules/compliance-checker"
[ -d "BCM-v1/services/domain/risk-analyzer" ] && cp -r BCM-v1/services/domain/risk-analyzer "$LEGO_DIR/bcm-modules/risk-analyzer"
[ -d "BCM-v1/services/domain/reporting-engine" ] && cp -r BCM-v1/services/domain/reporting-engine "$LEGO_DIR/bcm-modules/reporting-engine"
[ -d "BCM-v1/services/community" ] && cp -r BCM-v1/services/community "$LEGO_DIR/bcm-modules/community"
[ -d "BCM-v1/sandbox/golden-pr-26-modules/bcm_project_management" ] && cp -r BCM-v1/sandbox/golden-pr-26-modules/bcm_project_management "$LEGO_DIR/bcm-modules/project-management"

echo "  ✅ BCM modules собраны"

# ==================================
# СОБИРАЕМ TOOLS
# ==================================
echo "🛠️ Собираем tools..."
mkdir -p "$LEGO_DIR/tools"

[ -d "BCM-v1/services/deployer" ] && cp -r BCM-v1/services/deployer "$LEGO_DIR/tools/deployer"
[ -d "BCM-v1/services/template_library" ] && cp -r BCM-v1/services/template_library "$LEGO_DIR/tools/template-library"
[ -d "BCM-v1/services/knowledge-base" ] && cp -r BCM-v1/services/knowledge-base "$LEGO_DIR/tools/knowledge-base"
[ -d "BCM-v1/services/unified_control_center" ] && cp -r BCM-v1/services/unified_control_center "$LEGO_DIR/tools/control-center"
[ -d "BCM-v1/services/realtime_websocket" ] && cp -r BCM-v1/services/realtime_websocket "$LEGO_DIR/tools/websocket"
[ -d "platform-framework/config-service" ] && cp -r platform-framework/config-service "$LEGO_DIR/tools/config-service"
[ -d "BCM-v1/integrations/mcp-server" ] && cp -r BCM-v1/integrations/mcp-server "$LEGO_DIR/tools/mcp-server"

echo "  ✅ Tools собраны"

# ==================================
# СОБИРАЕМ SIMULATORS
# ==================================
echo "🎮 Собираем simulators..."
mkdir -p "$LEGO_DIR/simulators"

[ -d "BCM-v1/integrations/exercise_simulators" ] && cp -r BCM-v1/integrations/exercise_simulators "$LEGO_DIR/simulators/exercise-simulators"
[ -d "BCM-v1/integrations/simulation" ] && cp -r BCM-v1/integrations/simulation "$LEGO_DIR/simulators/simulation"
[ -d "BCM-v1/adapters/simulation" ] && cp -r BCM-v1/adapters/simulation "$LEGO_DIR/simulators/simulation-adapter"

echo "  ✅ Simulators собраны"

echo ""
echo "================================================"
echo "✅ ВСЕ LEGO КОМПОНЕНТЫ СОБРАНЫ!"
echo "================================================"
echo ""
echo "📊 Структура LEGO папки:"
echo ""
ls -la "$LEGO_DIR"
echo ""
echo "📝 Количество компонентов в каждой категории:"
echo "  • orchestrators:       $(ls -1 "$LEGO_DIR/orchestrators" 2>/dev/null | wc -l)"
echo "  • event-bus:          $(ls -1 "$LEGO_DIR/event-bus" 2>/dev/null | wc -l)"
echo "  • gateways:           $(ls -1 "$LEGO_DIR/gateways" 2>/dev/null | wc -l)"
echo "  • auth:               $(ls -1 "$LEGO_DIR/auth" 2>/dev/null | wc -l)"
echo "  • notifications:      $(ls -1 "$LEGO_DIR/notifications" 2>/dev/null | wc -l)"
echo "  • monitoring:         $(ls -1 "$LEGO_DIR/monitoring" 2>/dev/null | wc -l)"
echo "  • document-processors: $(ls -1 "$LEGO_DIR/document-processors" 2>/dev/null | wc -l)"
echo "  • workflow:           $(ls -1 "$LEGO_DIR/workflow" 2>/dev/null | wc -l)"
echo "  • ai-services:        $(ls -1 "$LEGO_DIR/ai-services" 2>/dev/null | wc -l)"
echo "  • integrations:       $(ls -1 "$LEGO_DIR/integrations" 2>/dev/null | wc -l)"
echo "  • adapters:           $(ls -1 "$LEGO_DIR/adapters" 2>/dev/null | wc -l)"
echo "  • bridges:            $(ls -1 "$LEGO_DIR/bridges" 2>/dev/null | wc -l)"
echo "  • digital-twin:       $(ls -1 "$LEGO_DIR/digital-twin" 2>/dev/null | wc -l)"
echo "  • bcm-modules:        $(ls -1 "$LEGO_DIR/bcm-modules" 2>/dev/null | wc -l)"
echo "  • tools:              $(ls -1 "$LEGO_DIR/tools" 2>/dev/null | wc -l)"
echo "  • simulators:         $(ls -1 "$LEGO_DIR/simulators" 2>/dev/null | wc -l)"
echo ""
echo "🎯 Теперь можно анализировать и объединять компоненты!"