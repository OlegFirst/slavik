#!/bin/bash
# ============================================================================
# Docker Build All - Build all containers in optimal order
# ============================================================================
# Usage: ./docker-build-all.sh [--no-cache] [--parallel]
# ============================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Options
NO_CACHE=""
PARALLEL=""

# Parse arguments
for arg in "$@"; do
    case $arg in
        --no-cache)
            NO_CACHE="--no-cache"
            echo -e "${YELLOW}Building with --no-cache${NC}"
            ;;
        --parallel)
            PARALLEL="--parallel"
            echo -e "${YELLOW}Building in parallel mode${NC}"
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            echo "Usage: ./docker-build-all.sh [--no-cache] [--parallel]"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Docker Build All - AI-Powered BCM Platform  ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if docker-compose exists
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose not found. Please install Docker Compose.${NC}"
    exit 1
fi

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo -e "${YELLOW}⚠️  .env.production not found${NC}"
    echo -e "${YELLOW}Creating from template...${NC}"
    cp .env.production.example .env.production
    echo -e "${GREEN}✅ Created .env.production${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env.production with your values${NC}"
    read -p "Press Enter to continue or Ctrl+C to exit..."
fi

# Build function
build_service() {
    local service=$1
    local description=$2

    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Building: $description${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    local start_time=$(date +%s)

    if docker-compose -f docker-compose.production.yml build $NO_CACHE $service; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        echo -e "${GREEN}✅ $description built successfully (${duration}s)${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to build $description${NC}"
        return 1
    fi
}

# Start time
START_TIME=$(date +%s)

if [ -n "$PARALLEL" ]; then
    # Parallel build (faster but harder to debug)
    echo -e "${YELLOW}Building all containers in parallel...${NC}"
    if docker-compose -f docker-compose.production.yml build $NO_CACHE $PARALLEL; then
        echo -e "${GREEN}✅ All containers built successfully${NC}"
    else
        echo -e "${RED}❌ Build failed${NC}"
        exit 1
    fi
else
    # Sequential build (safer, easier to debug)
    echo -e "${YELLOW}Building containers sequentially...${NC}"

    # Track failures
    FAILED_BUILDS=()

    # Build in dependency order
    build_service "redis" "Redis Cache" || FAILED_BUILDS+=("redis")
    build_service "eventbus" "EventBus" || FAILED_BUILDS+=("eventbus")
    build_service "security" "Security Services" || FAILED_BUILDS+=("security")
    build_service "runtime" "Runtime Services" || FAILED_BUILDS+=("runtime")
    build_service "db-services" "Database Services" || FAILED_BUILDS+=("db-services")
    build_service "platform-services" "Platform Services" || FAILED_BUILDS+=("platform-services")
    build_service "intelligent-core" "Intelligent Core" || FAILED_BUILDS+=("intelligent-core")
    build_service "ai-office" "AI Office" || FAILED_BUILDS+=("ai-office")
    build_service "monitoring" "Monitoring" || FAILED_BUILDS+=("monitoring")
    build_service "gateway" "API Gateway" || FAILED_BUILDS+=("gateway")
    build_service "interfaces" "Frontend Interfaces" || FAILED_BUILDS+=("interfaces")
    build_service "integrations" "External Integrations" || FAILED_BUILDS+=("integrations")

    # Summary
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Build Summary${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [ ${#FAILED_BUILDS[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ All 12 containers built successfully!${NC}"
    else
        echo -e "${RED}❌ ${#FAILED_BUILDS[@]} build(s) failed:${NC}"
        for service in "${FAILED_BUILDS[@]}"; do
            echo -e "${RED}  - $service${NC}"
        done
        exit 1
    fi
fi

# End time
END_TIME=$(date +%s)
TOTAL_DURATION=$((END_TIME - START_TIME))
MINUTES=$((TOTAL_DURATION / 60))
SECONDS=$((TOTAL_DURATION % 60))

echo ""
echo -e "${GREEN}Total build time: ${MINUTES}m ${SECONDS}s${NC}"

# Show images
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Docker Images${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
docker images | grep bcm

# Next steps
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Next Steps${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}1. Start all services:${NC}"
echo -e "   docker-compose -f docker-compose.production.yml up -d"
echo ""
echo -e "${GREEN}2. Check status:${NC}"
echo -e "   docker-compose -f docker-compose.production.yml ps"
echo ""
echo -e "${GREEN}3. View logs:${NC}"
echo -e "   docker-compose -f docker-compose.production.yml logs -f"
echo ""
echo -e "${GREEN}4. Test health:${NC}"
echo -e "   curl http://localhost:8000/health"
echo ""
echo -e "${GREEN}5. Stop all:${NC}"
echo -e "   docker-compose -f docker-compose.production.yml down"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Build complete! Ready to deploy!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
