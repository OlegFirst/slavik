#!/bin/bash

# 🏗️ РЕОРГАНИЗАЦИЯ СТРУКТУРЫ ПО СЛОЯМ
# Перестройка для понятной архитектуры

echo "================================================"
echo "🏗️ РЕОРГАНИЗАЦИЯ СТРУКТУРЫ ПРОЕКТА"
echo "================================================"
echo ""

# Создаем новую структуру папок
echo "📁 Создаем новую структуру папок..."

mkdir -p 1_NUCLEUS/{orchestrator,event-bus,service-registry,workflow-engine,ai-optimizer,process-mining,infrastructure}
mkdir -p 2_PROTECTION/{api-gateway,load-balancer,auth-service,config-service,rate-limiter,monitoring,notifications,websocket-gateway}
mkdir -p 3_CONTROL/{control-center,data-gateway,deployment-manager}
mkdir -p 4_SERVICES/{document-processor,risk-management,incident-management,audit-service,training-service,bia-service,recovery-planning}
mkdir -p 5_INTEGRATIONS/{thehive-connector,lms-connector,governance-connector,oscal-connector,odoo-modules}
mkdir -p 6_AI_CORE/{models,agents,prompts,training}
mkdir -p docker-compose
mkdir -p scripts
mkdir -p config/{development,staging,production}

echo "✅ Структура папок создана"
echo ""

# ПЕРЕМЕЩАЕМ КОМПОНЕНТЫ ЯДРА (1_NUCLEUS)
echo "🧠 Перемещаем компоненты NUCLEUS..."

# Event Bus
if [ -d "platform-framework/event-bus" ]; then
    echo "  • Перемещаем Event Bus..."
    cp -r platform-framework/event-bus/* 1_NUCLEUS/event-bus/ 2>/dev/null
fi
if [ -d "BCM-v1/backend/eventbus" ]; then
    cp -r BCM-v1/backend/eventbus/* 1_NUCLEUS/event-bus/ 2>/dev/null
fi

# Orchestrator (объединяем все)
if [ -d "platform-framework/orchestrator" ]; then
    echo "  • Перемещаем Orchestrator..."
    cp -r platform-framework/orchestrator/* 1_NUCLEUS/orchestrator/ 2>/dev/null
fi
if [ -d "BCM-v1/backend/orchestrator" ]; then
    cp -r BCM-v1/backend/orchestrator/* 1_NUCLEUS/orchestrator/ 2>/dev/null
fi
if [ -d "BCM-v1/backend/orchestrator_service" ]; then
    cp -r BCM-v1/backend/orchestrator_service/* 1_NUCLEUS/orchestrator/ 2>/dev/null
fi

# Service Registry
if [ -d "platform-framework/service-registry" ]; then
    echo "  • Перемещаем Service Registry..."
    cp -r platform-framework/service-registry/* 1_NUCLEUS/service-registry/ 2>/dev/null
fi

# Workflow Engine (BPMN)
if [ -d "platform-framework/services/bpmn_service" ]; then
    echo "  • Перемещаем Workflow Engine..."
    cp -r platform-framework/services/bpmn_service/* 1_NUCLEUS/workflow-engine/ 2>/dev/null
fi
if [ -d "BCM-v1/backend/bpmn_service" ]; then
    cp -r BCM-v1/backend/bpmn_service/* 1_NUCLEUS/workflow-engine/ 2>/dev/null
fi

# AI Workflow Optimizer
if [ -d "BCM-v1/services/ai_workflow_optimizer" ]; then
    echo "  • Перемещаем AI Optimizer..."
    cp -r BCM-v1/services/ai_workflow_optimizer/* 1_NUCLEUS/ai-optimizer/ 2>/dev/null
fi

# Process Mining
if [ -d "BCM-v1/services/process_mining_service" ]; then
    echo "  • Перемещаем Process Mining..."
    cp -r BCM-v1/services/process_mining_service/* 1_NUCLEUS/process-mining/ 2>/dev/null
fi

echo "✅ NUCLEUS компоненты перемещены"
echo ""

# ПЕРЕМЕЩАЕМ ЗАЩИТНЫЙ СЛОЙ (2_PROTECTION)
echo "🛡️ Перемещаем компоненты PROTECTION..."

# API Gateway (объединяем)
if [ -d "platform-framework/api-gateway" ]; then
    echo "  • Перемещаем API Gateway..."
    cp -r platform-framework/api-gateway/* 2_PROTECTION/api-gateway/ 2>/dev/null
fi
if [ -d "BCM-v1/integrations/gateway" ]; then
    cp -r BCM-v1/integrations/gateway/* 2_PROTECTION/api-gateway/ 2>/dev/null
fi
if [ -d "BCM-v1/services/unified_api_gateway" ]; then
    cp -r BCM-v1/services/unified_api_gateway/* 2_PROTECTION/api-gateway/ 2>/dev/null
fi

# Load Balancer (Nginx)
if [ -d "BCM-v1/integrations/nginx" ]; then
    echo "  • Перемещаем Load Balancer..."
    cp -r BCM-v1/integrations/nginx/* 2_PROTECTION/load-balancer/ 2>/dev/null
fi

# Auth Service
if [ -d "platform-framework/auth-service" ]; then
    echo "  • Перемещаем Auth Service..."
    cp -r platform-framework/auth-service/* 2_PROTECTION/auth-service/ 2>/dev/null
fi
if [ -d "BCM-v1/backend/auth_service" ]; then
    cp -r BCM-v1/backend/auth_service/* 2_PROTECTION/auth-service/ 2>/dev/null
fi

# Config Service
if [ -d "platform-framework/config-service" ]; then
    echo "  • Перемещаем Config Service..."
    cp -r platform-framework/config-service/* 2_PROTECTION/config-service/ 2>/dev/null
fi

# Monitoring
if [ -d "platform-framework/monitoring" ]; then
    echo "  • Перемещаем Monitoring..."
    cp -r platform-framework/monitoring/* 2_PROTECTION/monitoring/ 2>/dev/null
fi
if [ -d "BCM-v1/services/monitoring_service" ]; then
    cp -r BCM-v1/services/monitoring_service/* 2_PROTECTION/monitoring/ 2>/dev/null
fi

# Notifications (объединяем)
if [ -d "platform-framework/notification-service" ]; then
    echo "  • Перемещаем Notifications..."
    cp -r platform-framework/notification-service/* 2_PROTECTION/notifications/ 2>/dev/null
fi
if [ -d "BCM-v1/backend/notification_service" ]; then
    cp -r BCM-v1/backend/notification_service/* 2_PROTECTION/notifications/ 2>/dev/null
fi
if [ -d "BCM-v1/services/notification_service" ]; then
    cp -r BCM-v1/services/notification_service/* 2_PROTECTION/notifications/ 2>/dev/null
fi

# WebSocket Gateway
if [ -d "BCM-v1/services/realtime_websocket" ]; then
    echo "  • Перемещаем WebSocket Gateway..."
    cp -r BCM-v1/services/realtime_websocket/* 2_PROTECTION/websocket-gateway/ 2>/dev/null
fi

echo "✅ PROTECTION компоненты перемещены"
echo ""

# ПЕРЕМЕЩАЕМ УПРАВЛЯЮЩИЙ СЛОЙ (3_CONTROL)
echo "🎛️ Перемещаем компоненты CONTROL..."

if [ -d "BCM-v1/services/unified_control_center" ]; then
    echo "  • Перемещаем Control Center..."
    cp -r BCM-v1/services/unified_control_center/* 3_CONTROL/control-center/ 2>/dev/null
fi

if [ -d "BCM-v1/services/unified_database_gateway" ]; then
    echo "  • Перемещаем Data Gateway..."
    cp -r BCM-v1/services/unified_database_gateway/* 3_CONTROL/data-gateway/ 2>/dev/null
fi

if [ -d "BCM-v1/services/deployer" ]; then
    echo "  • Перемещаем Deployment Manager..."
    cp -r BCM-v1/services/deployer/* 3_CONTROL/deployment-manager/ 2>/dev/null
fi

echo "✅ CONTROL компоненты перемещены"
echo ""

# ПЕРЕМЕЩАЕМ ИНТЕГРАЦИИ (5_INTEGRATIONS)
echo "🔌 Перемещаем компоненты INTEGRATIONS..."

# TheHive (объединяем)
if [ -d "BCM-v1/integrations/thehive" ]; then
    echo "  • Перемещаем TheHive connector..."
    cp -r BCM-v1/integrations/thehive/* 5_INTEGRATIONS/thehive-connector/ 2>/dev/null
fi
if [ -d "BCM-v1/backend/thehive_adapter" ]; then
    cp -r BCM-v1/backend/thehive_adapter/* 5_INTEGRATIONS/thehive-connector/ 2>/dev/null
fi

# LMS (объединяем)
if [ -d "BCM-v1/integrations/lms" ]; then
    echo "  • Перемещаем LMS connector..."
    cp -r BCM-v1/integrations/lms/* 5_INTEGRATIONS/lms-connector/ 2>/dev/null
fi
if [ -d "BCM-v1/backend/lms_adapter" ]; then
    cp -r BCM-v1/backend/lms_adapter/* 5_INTEGRATIONS/lms-connector/ 2>/dev/null
fi

# Governance
if [ -d "BCM-v1/integrations/governance" ]; then
    echo "  • Перемещаем Governance connector..."
    cp -r BCM-v1/integrations/governance/* 5_INTEGRATIONS/governance-connector/ 2>/dev/null
fi

# OSCAL
if [ -d "BCM-v1/integrations/opengrc_oscal" ]; then
    echo "  • Перемещаем OSCAL connector..."
    cp -r BCM-v1/integrations/opengrc_oscal/* 5_INTEGRATIONS/oscal-connector/ 2>/dev/null
fi

echo "✅ INTEGRATIONS компоненты перемещены"
echo ""

# ПЕРЕМЕЩАЕМ AI КОМПОНЕНТЫ (6_AI_CORE)
echo "🤖 Перемещаем AI компоненты..."

if [ -d "ai-core" ]; then
    cp -r ai-core/* 6_AI_CORE/ 2>/dev/null
fi

echo "✅ AI компоненты перемещены"
echo ""

# ПЕРЕМЕЩАЕМ DOCKER КОНФИГУРАЦИИ
echo "🐳 Перемещаем Docker конфигурации..."

mv docker-compose-*.yml docker-compose/ 2>/dev/null

echo "✅ Docker конфигурации перемещены"
echo ""

# ПЕРЕМЕЩАЕМ СКРИПТЫ
echo "📜 Перемещаем скрипты..."

mv start-*.sh scripts/ 2>/dev/null

echo "✅ Скрипты перемещены"
echo ""

# СОЗДАЕМ ГЛАВНЫЙ СКРИПТ ЗАПУСКА
cat > scripts/start-platform.sh << 'EOF'
#!/bin/bash

# 🚀 ЗАПУСК ВСЕЙ ПЛАТФОРМЫ

echo "================================================"
echo "🚀 COGNITIVE ORCHESTRATION PLATFORM"
echo "================================================"
echo ""

# 1. Nucleus (Ядро)
echo "1️⃣ Запускаем NUCLEUS..."
./scripts/start-nucleus.sh

sleep 10

# 2. Protection (Защита)
echo "2️⃣ Запускаем PROTECTION..."
./scripts/start-protection.sh

sleep 10

# 3. Control (Управление)
echo "3️⃣ Запускаем CONTROL..."
./scripts/start-control.sh

sleep 5

# 4. Services (Сервисы)
echo "4️⃣ Запускаем SERVICES..."
./scripts/start-services.sh

sleep 5

# 5. Integrations (Интеграции)
echo "5️⃣ Запускаем INTEGRATIONS..."
./scripts/start-integrations.sh

echo ""
echo "================================================"
echo "✅ ПЛАТФОРМА ПОЛНОСТЬЮ ЗАПУЩЕНА!"
echo "================================================"
EOF

chmod +x scripts/start-platform.sh

echo ""
echo "================================================"
echo "✅ РЕОРГАНИЗАЦИЯ ЗАВЕРШЕНА!"
echo "================================================"
echo ""
echo "📊 Новая структура:"
echo "  • 1_NUCLEUS/       - Ядро системы (мозг)"
echo "  • 2_PROTECTION/    - Защитный слой (череп)"
echo "  • 3_CONTROL/       - Управление (командный центр)"
echo "  • 4_SERVICES/      - Бизнес-сервисы (органы)"
echo "  • 5_INTEGRATIONS/  - Внешние интеграции"
echo "  • 6_AI_CORE/       - AI компоненты"
echo ""
echo "🚀 Для запуска всей платформы:"
echo "  ./scripts/start-platform.sh"
echo ""