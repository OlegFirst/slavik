#!/bin/bash
# Pre-commit hook для проверки регистрации сервисов
# Автоматически проверяет, зарегистрирован ли новый сервис в каталоге

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
SCRIPTS_DIR="$REPO_ROOT/scripts/service-registry"
CATALOGS_DIR="$REPO_ROOT/catalogs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Checking for new services...${NC}"

# Получить список измененных файлов
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=A)

# Флаг для отслеживания найденных сервисов
NEW_SERVICES_FOUND=false
UNREGISTERED_SERVICES=""

# Проверить на новые main.py в infrastructure/ или intelligent_core/
for file in $CHANGED_FILES; do
    # Проверка на новый сервис (новый main.py)
    if [[ $file =~ (infrastructure|intelligent_core|platform_services)/([^/]+)/main\.py$ ]]; then
        SERVICE_DIR="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
        SERVICE_NAME="${BASH_REMATCH[2]}"

        echo -e "${YELLOW}📦 Found new service: ${SERVICE_NAME} (${SERVICE_DIR})${NC}"
        NEW_SERVICES_FOUND=true

        # Проверить, зарегистрирован ли сервис в каталоге
        CATALOG_FILE="$CATALOGS_DIR/platform-services/${SERVICE_NAME}.yaml"

        if [ ! -f "$CATALOG_FILE" ]; then
            echo -e "${RED}❌ Service NOT registered in catalog: ${SERVICE_NAME}${NC}"
            UNREGISTERED_SERVICES="${UNREGISTERED_SERVICES}\n  - ${SERVICE_NAME} (${SERVICE_DIR})"
        else
            echo -e "${GREEN}✅ Service registered: ${SERVICE_NAME}${NC}"
        fi
    fi
done

# Если найдены незарегистрированные сервисы
if [ -n "$UNREGISTERED_SERVICES" ]; then
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ UNREGISTERED SERVICES DETECTED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}The following services are not registered in the catalog:${NC}"
    echo -e "$UNREGISTERED_SERVICES"
    echo ""
    echo -e "${BLUE}To register a service, run:${NC}"
    echo -e "  ${GREEN}python scripts/service-registry/auto_register_service.py register${NC}"
    echo ""
    echo -e "${YELLOW}Or skip this check (not recommended):${NC}"
    echo -e "  ${GREEN}git commit --no-verify${NC}"
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Спросить пользователя
    read -p "Register services now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 "$SCRIPTS_DIR/auto_register_service.py" register
    else
        echo -e "${RED}Commit aborted. Please register services before committing.${NC}"
        exit 1
    fi
fi

# Проверка портов
echo -e "${BLUE}🔍 Checking for port conflicts...${NC}"

# Извлечь порты из новых файлов
for file in $CHANGED_FILES; do
    if [[ $file =~ \.py$ ]] || [[ $file =~ \.yaml$ ]]; then
        # Проверить на hardcoded порты
        if grep -qE "port\s*=\s*[0-9]+" "$file" 2>/dev/null; then
            PORT=$(grep -oE "port\s*=\s*[0-9]+" "$file" | grep -oE "[0-9]+" | head -1)
            echo -e "${YELLOW}⚠️  Found hardcoded port in ${file}: ${PORT}${NC}"
            echo -e "   Consider using environment variables: PORT = int(os.getenv('PORT', ${PORT}))"
        fi
    fi
done

if [ "$NEW_SERVICES_FOUND" = false ]; then
    echo -e "${GREEN}✅ No new services detected${NC}"
fi

echo -e "${GREEN}✅ Pre-commit service check passed${NC}"
exit 0
