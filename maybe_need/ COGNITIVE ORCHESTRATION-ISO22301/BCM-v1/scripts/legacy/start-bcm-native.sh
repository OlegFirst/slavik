#!/bin/bash

# BCM Platform - Поэтапный запуск без Docker
# Скрипт для запуска всей платформы ISO-22301 на хост-системе

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Конфигурация
POSTGRES_PORT=${POSTGRES_PORT:-5433}
REDIS_PORT=${REDIS_PORT:-6380}
RABBITMQ_PORT=${RABBITMQ_PORT:-5673}
RABBITMQ_MGMT_PORT=${RABBITMQ_MGMT_PORT:-15673}

# Порты сервисов
EVENTBUS_PORT=${EVENTBUS_PORT:-8001}
ORCHESTRATOR_PORT=${ORCHESTRATOR_PORT:-8002}
ODOO_PORT=${ODOO_PORT:-8069}
FRONTEND_PORT=${FRONTEND_PORT:-8081}

# Сервисы
BIA_ENGINE_PORT=${BIA_ENGINE_PORT:-8082}
DOC_PROCESSOR_PORT=${DOC_PROCESSOR_PORT:-8083}
COMPLIANCE_CHECKER_PORT=${COMPLIANCE_CHECKER_PORT:-8084}
BPMN_SERVICE_PORT=${BPMN_SERVICE_PORT:-8005}
LMS_ADAPTER_PORT=${LMS_ADAPTER_PORT:-8006}
THEHIVE_ADAPTER_PORT=${THEHIVE_ADAPTER_PORT:-8007}
GRAFANA_ADAPTER_PORT=${GRAFANA_ADAPTER_PORT:-8008}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_requirements() {
    print_status "Проверка системных требований..."
    
    # Проверка Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 не найден! Установите Python 3.11+"
        exit 1
    fi
    
    # Проверка Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js не найден! Установите Node.js 18+"
        exit 1
    fi
    
    # Проверка PostgreSQL
    if ! command -v psql &> /dev/null; then
        print_error "PostgreSQL client не найден! Установите postgresql-client"
        exit 1
    fi
    
    # Проверка Redis
    if ! command -v redis-cli &> /dev/null; then
        print_error "Redis CLI не найден! Установите redis-tools"
        exit 1
    fi
    
    print_success "Все системные требования выполнены"
}

setup_environment() {
    print_status "Настройка окружения..."
    
    # Создаем .env файл если его нет
    if [ ! -f .env ]; then
        print_warning "Файл .env не найден, создаем из .env.example"
        cp .env.example .env
        
        # Устанавливаем правильные порты для нативного запуска
        sed -i "s/DB_PORT=5432/DB_PORT=$POSTGRES_PORT/g" .env
        sed -i "s/REDIS_PORT=6379/REDIS_PORT=$REDIS_PORT/g" .env
        sed -i "s/localhost:5432/localhost:$POSTGRES_PORT/g" .env
        sed -i "s/localhost:6379/localhost:$REDIS_PORT/g" .env
        
        print_warning "Пожалуйста, отредактируйте .env файл с вашими настройками перед продолжением"
        read -p "Нажмите Enter для продолжения после редактирования .env..."
    fi
    
    # Загружаем переменные окружения
    export $(grep -v '^#' .env | xargs)
    
    print_success "Окружение настроено"
}

start_infrastructure() {
    print_status "Запуск инфраструктурных сервисов..."
    
    # PostgreSQL
    print_status "Запуск PostgreSQL на порту $POSTGRES_PORT..."
    if ! pgrep -f "postgres.*port=$POSTGRES_PORT" > /dev/null; then
        if command -v pg_ctl &> /dev/null; then
            # Инициализируем базу если нужно
            if [ ! -d "/tmp/postgres_bcm" ]; then
                mkdir -p /tmp/postgres_bcm
                initdb -D /tmp/postgres_bcm
            fi
            
            # Запускаем PostgreSQL
            pg_ctl -D /tmp/postgres_bcm -l /tmp/postgres_bcm/logfile -o "-p $POSTGRES_PORT" start
            sleep 3
            
            # Создаем базы данных
            createdb -h localhost -p $POSTGRES_PORT -U $(whoami) bcm_platform 2>/dev/null || true
            createdb -h localhost -p $POSTGRES_PORT -U $(whoami) keycloak 2>/dev/null || true
        else
            print_error "pg_ctl не найден! Запустите PostgreSQL вручную на порту $POSTGRES_PORT"
            exit 1
        fi
    else
        print_success "PostgreSQL уже запущен"
    fi
    
    # Redis
    print_status "Запуск Redis на порту $REDIS_PORT..."
    if ! pgrep -f "redis-server.*$REDIS_PORT" > /dev/null; then
        redis-server --port $REDIS_PORT --daemonize yes
        sleep 2
    else
        print_success "Redis уже запущен"
    fi
    
    # RabbitMQ (опционально, если установлен)
    if command -v rabbitmq-server &> /dev/null; then
        print_status "Запуск RabbitMQ на порту $RABBITMQ_PORT..."
        if ! pgrep -f rabbitmq > /dev/null; then
            RABBITMQ_NODE_PORT=$RABBITMQ_PORT RABBITMQ_DIST_PORT=$((RABBITMQ_PORT + 20000)) \
            RABBITMQ_SERVER_START_ARGS="-rabbitmq_management listener [{port,$RABBITMQ_MGMT_PORT}]" \
            rabbitmq-server -detached
            sleep 5
        else
            print_success "RabbitMQ уже запущен"
        fi
    else
        print_warning "RabbitMQ не установлен, пропускаем"
    fi
    
    print_success "Инфраструктурные сервисы запущены"
}

start_eventbus() {
    print_status "Запуск EventBus на порту $EVENTBUS_PORT..."
    
    cd backend/eventbus
    
    # Установка зависимостей
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Настройка переменных окружения
    export REDIS_URL="redis://localhost:$REDIS_PORT/0"
    export POSTGRES_URL="postgresql://$(whoami)@localhost:$POSTGRES_PORT/bcm_platform"
    
    # Запуск EventBus в фоне
    nohup uvicorn main:app --host 0.0.0.0 --port $EVENTBUS_PORT > eventbus.log 2>&1 &
    echo $! > eventbus.pid
    
    cd ../..
    sleep 3
    
    # Проверка запуска
    if curl -s http://localhost:$EVENTBUS_PORT/health > /dev/null; then
        print_success "EventBus запущен на порту $EVENTBUS_PORT"
    else
        print_error "Ошибка запуска EventBus"
        return 1
    fi
}

start_orchestrator() {
    print_status "Запуск Orchestrator на порту $ORCHESTRATOR_PORT..."
    
    cd backend/orchestrator_service
    
    # Установка зависимостей
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Настройка переменных окружения
    export REDIS_URL="redis://localhost:$REDIS_PORT/1"
    export POSTGRES_URL="postgresql://$(whoami)@localhost:$POSTGRES_PORT/bcm_platform"
    export EVENTBUS_URL="http://localhost:$EVENTBUS_PORT"
    
    # Запуск Orchestrator в фоне
    nohup uvicorn main:app --host 0.0.0.0 --port $ORCHESTRATOR_PORT > orchestrator.log 2>&1 &
    echo $! > orchestrator.pid
    
    cd ../..
    sleep 3
    
    # Проверка запуска
    if curl -s http://localhost:$ORCHESTRATOR_PORT/health > /dev/null; then
        print_success "Orchestrator запущен на порту $ORCHESTRATOR_PORT"
    else
        print_error "Ошибка запуска Orchestrator"
        return 1
    fi
}

start_microservices() {
    print_status "Запуск микросервисов..."
    
    # Список микросервисов для запуска
    declare -A SERVICES=(
        ["bia_engine"]="$BIA_ENGINE_PORT"
        ["document_processor"]="$DOC_PROCESSOR_PORT" 
        ["bpmn_service"]="$BPMN_SERVICE_PORT"
        ["lms_adapter"]="$LMS_ADAPTER_PORT"
        ["thehive_adapter"]="$THEHIVE_ADAPTER_PORT"
        ["grafana_adapter"]="$GRAFANA_ADAPTER_PORT"
    )
    
    for service in "${!SERVICES[@]}"; do
        port=${SERVICES[$service]}
        service_dir="backend/$service"
        
        if [ -d "$service_dir" ]; then
            print_status "Запуск $service на порту $port..."
            
            cd $service_dir
            
            # Установка зависимостей
            if [ ! -d "venv" ]; then
                python3 -m venv venv
                source venv/bin/activate
                pip install -r requirements.txt
            else
                source venv/bin/activate
            fi
            
            # Настройка переменных окружения для сервиса
            export REDIS_URL="redis://localhost:$REDIS_PORT/$((port % 10))"
            export POSTGRES_URL="postgresql://$(whoami)@localhost:$POSTGRES_PORT/bcm_platform"
            export EVENTBUS_URL="http://localhost:$EVENTBUS_PORT"
            export PORT=$port
            
            # Запуск сервиса в фоне
            nohup uvicorn main:app --host 0.0.0.0 --port $port > ${service}.log 2>&1 &
            echo $! > ${service}.pid
            
            cd ../..
            sleep 2
        else
            print_warning "Сервис $service не найден в $service_dir"
        fi
    done
    
    print_success "Микросервисы запущены"
}

start_odoo() {
    print_status "Запуск Odoo на порту $ODOO_PORT..."
    
    cd core/odoo-18.0
    
    # Установка Python зависимостей для Odoo
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Настройка переменных окружения для Odoo
    export DB_HOST="localhost"
    export DB_PORT="$POSTGRES_PORT"
    export DB_USER="$(whoami)"
    export DB_NAME="bcm_platform"
    export REDIS_HOST="localhost"
    export REDIS_PORT="$REDIS_PORT"
    
    # Создаем конфиг для нативного запуска
    cat > odoo_native.conf << EOF
[options]
addons_path = addons
admin_passwd = admin
db_host = localhost
db_port = $POSTGRES_PORT
db_user = $(whoami)
db_name = bcm_platform
xmlrpc_port = $ODOO_PORT
logfile = odoo.log
log_level = info
EOF
    
    # Запуск Odoo в фоне
    nohup python3 odoo-bin -c odoo_native.conf > odoo_startup.log 2>&1 &
    echo $! > odoo.pid
    
    cd ../..
    sleep 10
    
    # Проверка запуска
    if curl -s http://localhost:$ODOO_PORT > /dev/null; then
        print_success "Odoo запущен на порту $ODOO_PORT"
    else
        print_error "Ошибка запуска Odoo"
        return 1
    fi
}

start_frontend() {
    print_status "Запуск Frontend на порту $FRONTEND_PORT..."
    
    cd frontend/web_portal
    
    # Установка Node.js зависимостей
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    
    # Настройка переменных окружения для frontend
    export VUE_APP_API_URL="http://localhost:$ODOO_PORT/api/v1"
    export VUE_APP_EVENTBUS_URL="http://localhost:$EVENTBUS_PORT/api"
    export VUE_APP_BPMN_URL="http://localhost:$BPMN_SERVICE_PORT/api"
    export PORT=$FRONTEND_PORT
    
    # Запуск Frontend в фоне
    nohup npm run serve -- --port $FRONTEND_PORT > frontend.log 2>&1 &
    echo $! > frontend.pid
    
    cd ../..
    sleep 5
    
    # Проверка запуска
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null; then
        print_success "Frontend запущен на порту $FRONTEND_PORT"
    else
        print_error "Ошибка запуска Frontend"
        return 1
    fi
}

show_status() {
    print_status "Статус сервисов:"
    echo
    
    # Проверка портов
    check_service() {
        local name=$1
        local port=$2
        if nc -z localhost $port 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $name: http://localhost:$port"
        else
            echo -e "  ${RED}✗${NC} $name: порт $port недоступен"
        fi
    }
    
    check_service "PostgreSQL" $POSTGRES_PORT
    check_service "Redis" $REDIS_PORT
    check_service "EventBus" $EVENTBUS_PORT
    check_service "Orchestrator" $ORCHESTRATOR_PORT
    check_service "Odoo" $ODOO_PORT
    check_service "Frontend" $FRONTEND_PORT
    check_service "BIA Engine" $BIA_ENGINE_PORT
    check_service "BPMN Service" $BPMN_SERVICE_PORT
    
    echo
    echo -e "${BLUE}Основные URL:${NC}"
    echo -e "  Frontend:     ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
    echo -e "  Odoo:         ${GREEN}http://localhost:$ODOO_PORT${NC}"
    echo -e "  EventBus API: ${GREEN}http://localhost:$EVENTBUS_PORT/docs${NC}"
    echo -e "  Orchestrator: ${GREEN}http://localhost:$ORCHESTRATOR_PORT/docs${NC}"
    echo
}

create_stop_script() {
    print_status "Создание скрипта остановки..."
    
    cat > stop-bcm-native.sh << 'EOF'
#!/bin/bash

print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

print_status "Остановка BCM платформы..."

# Останавливаем сервисы по PID файлам
stop_service() {
    local service=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat $pid_file)
        if kill $pid 2>/dev/null; then
            print_status "Остановлен $service (PID: $pid)"
        fi
        rm -f $pid_file
    fi
}

# Backend сервисы
stop_service "EventBus" "backend/eventbus/eventbus.pid"
stop_service "Orchestrator" "backend/orchestrator_service/orchestrator.pid"
stop_service "BIA Engine" "backend/bia_engine/bia_engine.pid"
stop_service "Document Processor" "backend/document_processor/document_processor.pid"
stop_service "BPMN Service" "backend/bpmn_service/bpmn_service.pid"
stop_service "LMS Adapter" "backend/lms_adapter/lms_adapter.pid"
stop_service "TheHive Adapter" "backend/thehive_adapter/thehive_adapter.pid"
stop_service "Grafana Adapter" "backend/grafana_adapter/grafana_adapter.pid"

# Odoo
stop_service "Odoo" "core/odoo-18.0/odoo.pid"

# Frontend
stop_service "Frontend" "frontend/web_portal/frontend.pid"

# PostgreSQL (только если мы его запускали)
if [ -f "/tmp/postgres_bcm/postmaster.pid" ]; then
    pg_ctl -D /tmp/postgres_bcm stop
    print_status "PostgreSQL остановлен"
fi

# Redis (останавливаем все redis процессы на наших портах)
pkill -f "redis-server.*6380" 2>/dev/null || true

print_success "Все сервисы остановлены"
EOF

    chmod +x stop-bcm-native.sh
    print_success "Скрипт остановки создан: ./stop-bcm-native.sh"
}

main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║              BCM Platform Native Startup                 ║"
    echo "║         Business Continuity Management System            ║"
    echo "║              Запуск без Docker контейнеров               ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_requirements
    setup_environment
    
    print_status "Запуск платформы по этапам..."
    
    # Этап 1: Инфраструктура
    start_infrastructure
    
    # Этап 2: Core сервисы
    start_eventbus
    start_orchestrator
    
    # Этап 3: Микросервисы
    start_microservices
    
    # Этап 4: Odoo
    start_odoo
    
    # Этап 5: Frontend
    start_frontend
    
    # Создаем скрипт остановки
    create_stop_script
    
    # Показываем статус
    show_status
    
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                BCM Platform запущена!                    ║"
    echo "║                                                          ║"
    echo "║  Для остановки используйте: ./stop-bcm-native.sh        ║"
    echo "║                                                          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Обработка аргументов
case ${1:-start} in
    start)
        main
        ;;
    status)
        show_status
        ;;
    stop)
        ./stop-bcm-native.sh
        ;;
    *)
        echo "Использование: $0 {start|status|stop}"
        exit 1
        ;;
esac