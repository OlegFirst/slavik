#!/bin/bash

# BCM Platform Startup Script
# Запуск полной платформы Business Continuity Management

set -e

echo "🚀 Starting BCM Platform (ISO 22301 Compliance System)"
echo "======================================================"

# Проверка Docker и Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Создание .env файла если не существует
if [ ! -f .env ]; then
    echo "📝 Creating .env file with default configuration..."
    cat > .env << EOF
# BCM Platform Environment Configuration

# Database Configuration
POSTGRES_DB=bcm_platform
POSTGRES_USER=odoo
POSTGRES_PASSWORD=odoo_password

# Keycloak Configuration
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123
KC_DB_PASSWORD=keycloak_password

# BCM Platform Configuration
BCM_VERSION=18.0.1.0.0
BCM_MODE=development
BCM_MULTITENANCY=true
BCM_AI_ENABLED=true

# Email Configuration
SMTP_HOST=mailhog
SMTP_PORT=1025
EMAIL_FROM=bcm-platform@localhost

# External URLs (for production)
# EXTERNAL_URL=https://bcm-platform.your-domain.com
# KEYCLOAK_EXTERNAL_URL=https://auth.your-domain.com
EOF
    echo "✅ Created .env file. Please review and customize if needed."
fi

# Создание hosts записей
echo "📝 Adding hosts entries for local development..."
if ! grep -q "bcm-platform.local" /etc/hosts; then
    echo "127.0.0.1 bcm-platform.local mail.bcm-platform.local auth.bcm-platform.local" | sudo tee -a /etc/hosts
    echo "✅ Added local hosts entries"
fi

# Проверка портов
echo "🔍 Checking port availability..."
ports_to_check=(80 443 5432 6379 8069 8080 8082 8083 8084 8025 8888)
for port in "${ports_to_check[@]}"; do
    if lsof -i :$port &> /dev/null; then
        echo "⚠️  Port $port is already in use. Please stop the service using this port."
        echo "   You can find the process with: lsof -i :$port"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
done

# Сборка и запуск сервисов
echo "🔨 Building BCM Platform services..."
# Note: Skip docker-compose build on Railway as it's not supported
if [ "$RAILWAY_ENVIRONMENT" != "" ]; then
    echo "ℹ️ Detected Railway environment - skipping docker-compose build"
else
    docker-compose build --no-cache
fi

echo "🚀 Starting BCM Platform services..."
# Note: Skip docker-compose up on Railway as single service deployment is used
if [ "$RAILWAY_ENVIRONMENT" != "" ]; then
    echo "ℹ️ Detected Railway environment - services will be started by Railway"
else
    docker-compose up -d
fi

# Ожидание готовности сервисов
echo "⏳ Waiting for services to be ready..."
sleep 30

# Проверка статуса сервисов
echo "🔍 Checking service health..."
services=("postgres" "redis" "rabbitmq" "keycloak" "ai_orchestrator" "bia_engine" "document_processor" "compliance_checker" "odoo")

for service in "${services[@]}"; do
    if docker-compose ps -q $service > /dev/null; then
        status=$(docker-compose ps $service | grep -o "Up\|Exit")
        if [[ $status == "Up" ]]; then
            echo "✅ $service is running"
        else
            echo "❌ $service failed to start"
        fi
    else
        echo "❌ $service not found"
    fi
done

# Отображение URL доступа
echo ""
echo "🎉 BCM Platform is starting up!"
echo "================================"
echo ""
echo "📱 Web Interfaces:"
echo "   • BCM Platform:      http://bcm-platform.local (or http://localhost:8069)"
echo "   • Keycloak Admin:    http://localhost:8080/admin (admin/admin123)"
echo "   • MailHog:          http://localhost:8025"
echo "   • Traefik Dashboard: http://localhost:8888"
echo ""
echo "🤖 AI Services:"
echo "   • AI Orchestrator:   http://localhost:8000"
echo "   • BIA Engine v2.0:   http://localhost:8082"
echo "   • Document Processor: http://localhost:8083"
echo "   • Compliance Checker: http://localhost:8084"
echo ""
echo "🗄️  Database & Infrastructure:"
echo "   • PostgreSQL:        localhost:5432"
echo "   • Redis:            localhost:6379"
echo "   • RabbitMQ:         localhost:15672 (bcm/bcm_password)"
echo ""
echo "⏳ Please wait 2-3 minutes for all services to fully initialize..."
echo ""
echo "📚 Default Login:"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "🔧 To stop the platform: docker-compose down"
echo "🔧 To view logs: docker-compose logs -f [service_name]"
echo "🔧 To restart: ./start-bcm-platform.sh"
echo ""
echo "📖 For full documentation, visit: /docs in your BCM Platform"

# Опционально открыть браузер
if command -v open &> /dev/null; then
    read -p "Open BCM Platform in browser? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open http://localhost:8069
    fi
fi

echo ""
echo "✨ BCM Platform startup complete! Happy Business Continuity Management! 🛡️"
