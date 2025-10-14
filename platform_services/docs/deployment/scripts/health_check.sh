#!/bin/bash

################################################################################
# BCM Platform Health Check Script
#
# Checks health of all platform services and infrastructure components
#
# Usage: ./health_check.sh [--verbose] [--json]
# Exit codes: 0 = all healthy, 1 = some unhealthy, 2 = critical failure
################################################################################

set -euo pipefail

# Configuration
VERBOSE=false
JSON_OUTPUT=false
EXIT_CODE=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Colors (only if not JSON output)
if [ "$JSON_OUTPUT" = false ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    NC=''
fi

# JSON output storage
declare -a RESULTS=()

################################################################################
# Health Check Functions
################################################################################

check_service() {
    local service=$1
    local port=$2
    local endpoint=${3:-/health}

    if curl -f -s -o /dev/null --max-time 5 "http://localhost:${port}${endpoint}"; then
        if [ "$JSON_OUTPUT" = false ]; then
            echo -e "${GREEN}✓${NC} $service is healthy"
        fi
        RESULTS+=("{\"service\":\"$service\",\"status\":\"healthy\",\"port\":$port}")
        return 0
    else
        if [ "$JSON_OUTPUT" = false ]; then
            echo -e "${RED}✗${NC} $service is unhealthy"
        fi
        RESULTS+=("{\"service\":\"$service\",\"status\":\"unhealthy\",\"port\":$port}")
        EXIT_CODE=1
        return 1
    fi
}

check_docker_service() {
    local service=$1

    if docker ps --filter "name=$service" --filter "status=running" | grep -q "$service"; then
        local health=$(docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null || echo "unknown")

        if [ "$health" = "healthy" ] || [ "$health" = "unknown" ]; then
            if [ "$JSON_OUTPUT" = false ]; then
                echo -e "${GREEN}✓${NC} Docker container $service is running"
            fi
            RESULTS+=("{\"service\":\"$service\",\"status\":\"running\",\"health\":\"$health\"}")
            return 0
        else
            if [ "$JSON_OUTPUT" = false ]; then
                echo -e "${YELLOW}⚠${NC} Docker container $service is $health"
            fi
            RESULTS+=("{\"service\":\"$service\",\"status\":\"running\",\"health\":\"$health\"}")
            return 1
        fi
    else
        if [ "$JSON_OUTPUT" = false ]; then
            echo -e "${RED}✗${NC} Docker container $service is not running"
        fi
        RESULTS+=("{\"service\":\"$service\",\"status\":\"stopped\"}")
        EXIT_CODE=1
        return 1
    fi
}

check_database() {
    if docker compose exec -T postgres pg_isready -U bcm_user -d bcm_platform > /dev/null 2>&1; then
        if [ "$JSON_OUTPUT" = false ]; then
            echo -e "${GREEN}✓${NC} PostgreSQL is accessible"
        fi

        if [ "$VERBOSE" = true ] && [ "$JSON_OUTPUT" = false ]; then
            local connections=$(docker compose exec -T postgres psql -U bcm_user -t -c "SELECT count(*) FROM pg_stat_activity;" | tr -d '[:space:]')
            echo "  Active connections: $connections"
        fi

        RESULTS+=("{\"service\":\"postgres\",\"status\":\"healthy\"}")
        return 0
    else
        if [ "$JSON_OUTPUT" = false ]; then
            echo -e "${RED}✗${NC} PostgreSQL is not accessible"
        fi
        RESULTS+=("{\"service\":\"postgres\",\"status\":\"unhealthy\"}")
        EXIT_CODE=2
        return 1
    fi
}

check_redis() {
    if docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
        if [ "$JSON_OUTPUT" = false ]; then
            echo -e "${GREEN}✓${NC} Redis is accessible"
        fi

        if [ "$VERBOSE" = true ] && [ "$JSON_OUTPUT" = false ]; then
            local memory=$(docker compose exec -T redis redis-cli INFO memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
            echo "  Memory usage: $memory"
        fi

        RESULTS+=("{\"service\":\"redis\",\"status\":\"healthy\"}")
        return 0
    else
        if [ "$JSON_OUTPUT" = false ]; then
            echo -e "${RED}✗${NC} Redis is not accessible"
        fi
        RESULTS+=("{\"service\":\"redis\",\"status\":\"unhealthy\"}")
        EXIT_CODE=2
        return 1
    fi
}

check_disk_space() {
    local threshold=90
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

    if [ "$usage" -lt "$threshold" ]; then
        if [ "$JSON_OUTPUT" = false ]; then
            echo -e "${GREEN}✓${NC} Disk space is adequate (${usage}% used)"
        fi
        RESULTS+=("{\"service\":\"disk\",\"status\":\"ok\",\"usage\":$usage}")
        return 0
    else
        if [ "$JSON_OUTPUT" = false ]; then
            echo -e "${RED}✗${NC} Disk space is low (${usage}% used)"
        fi
        RESULTS+=("{\"service\":\"disk\",\"status\":\"critical\",\"usage\":$usage}")
        EXIT_CODE=1
        return 1
    fi
}

check_memory() {
    local threshold=85
    local usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')

    if [ "$usage" -lt "$threshold" ]; then
        if [ "$JSON_OUTPUT" = false ]; then
            echo -e "${GREEN}✓${NC} Memory usage is normal (${usage}% used)"
        fi
        RESULTS+=("{\"service\":\"memory\",\"status\":\"ok\",\"usage\":$usage}")
        return 0
    else
        if [ "$JSON_OUTPUT" = false ]; then
            echo -e "${YELLOW}⚠${NC} Memory usage is high (${usage}% used)"
        fi
        RESULTS+=("{\"service\":\"memory\",\"status\":\"warning\",\"usage\":$usage}")
        return 1
    fi
}

check_docker_resources() {
    if [ "$VERBOSE" = true ] && [ "$JSON_OUTPUT" = false ]; then
        echo ""
        echo "Docker Container Resource Usage:"
        echo "--------------------------------"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -n 10
    fi
}

################################################################################
# Main Health Check
################################################################################

main() {
    if [ "$JSON_OUTPUT" = false ]; then
        echo "=========================================="
        echo "BCM Platform Health Check"
        echo "Time: $(date)"
        echo "=========================================="
        echo ""
    fi

    # Check infrastructure components
    if [ "$JSON_OUTPUT" = false ]; then
        echo "Infrastructure Components:"
        echo "--------------------------"
    fi

    check_docker_service "bcm-postgres"
    check_docker_service "bcm-redis"
    check_database
    check_redis

    if [ "$JSON_OUTPUT" = false ]; then
        echo ""
        echo "Application Services:"
        echo "--------------------"
    fi

    # Check application services
    check_service "Planning Service" 8011
    check_service "Plans Service" 8023
    check_service "BIA Service" 8012
    check_service "Compliance Service" 8014

    if [ "$JSON_OUTPUT" = false ]; then
        echo ""
        echo "Monitoring Services:"
        echo "-------------------"
    fi

    # Check monitoring
    check_docker_service "bcm-prometheus"
    check_docker_service "bcm-grafana"
    check_service "Monitoring Service" 8045

    if [ "$JSON_OUTPUT" = false ]; then
        echo ""
        echo "System Resources:"
        echo "----------------"
    fi

    # Check system resources
    check_disk_space
    check_memory

    # Show detailed resource usage if verbose
    check_docker_resources

    # Output results
    if [ "$JSON_OUTPUT" = true ]; then
        echo "{"
        echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
        echo "  \"status\": \"$([ $EXIT_CODE -eq 0 ] && echo 'healthy' || echo 'unhealthy')\","
        echo "  \"checks\": ["
        for i in "${!RESULTS[@]}"; do
            echo "    ${RESULTS[$i]}$([ $i -lt $((${#RESULTS[@]}-1)) ] && echo ',')"
        done
        echo "  ]"
        echo "}"
    else
        echo ""
        echo "=========================================="
        if [ $EXIT_CODE -eq 0 ]; then
            echo -e "${GREEN}All systems healthy${NC}"
        elif [ $EXIT_CODE -eq 1 ]; then
            echo -e "${YELLOW}Some systems require attention${NC}"
        else
            echo -e "${RED}Critical systems are down${NC}"
        fi
        echo "=========================================="
    fi

    exit $EXIT_CODE
}

main "$@"
