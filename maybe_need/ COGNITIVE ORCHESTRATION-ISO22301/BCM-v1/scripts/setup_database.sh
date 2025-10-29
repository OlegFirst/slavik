#!/bin/bash

# ====================================
# BCM PLATFORM DATABASE SETUP
# Manual database initialization script
# ====================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}         BCM PLATFORM DATABASE SETUP${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Database configuration
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}
ODOO_USER=${ODOO_USER:-odoo}
ODOO_PASSWORD=${ODOO_PASSWORD:-postgres123}

# Function to check if PostgreSQL is running
check_postgres() {
    echo -e "${YELLOW}Checking PostgreSQL connection...${NC}"

    if pg_isready -h $DB_HOST -p $DB_PORT > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL is running${NC}"
        return 0
    else
        echo -e "${RED}❌ PostgreSQL is not running or not accessible${NC}"
        echo -e "${YELLOW}Please start PostgreSQL service:${NC}"
        echo "  - macOS: brew services start postgresql"
        echo "  - Linux: sudo systemctl start postgresql"
        echo "  - Docker: docker-compose up -d postgres"
        return 1
    fi
}

# Function to create odoo user
create_odoo_user() {
    echo -e "${YELLOW}Creating Odoo database user...${NC}"

    psql -h $DB_HOST -p $DB_PORT -U $DB_USER <<EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '$ODOO_USER') THEN
        CREATE USER $ODOO_USER WITH PASSWORD '$ODOO_PASSWORD';
        ALTER USER $ODOO_USER CREATEDB;
        RAISE NOTICE 'User $ODOO_USER created';
    ELSE
        ALTER USER $ODOO_USER WITH PASSWORD '$ODOO_PASSWORD';
        RAISE NOTICE 'User $ODOO_USER password updated';
    END IF;
END
\$\$;
EOF

    echo -e "${GREEN}✅ Odoo user ready${NC}"
}

# Function to create databases
create_databases() {
    echo -e "${YELLOW}Creating BCM Platform databases...${NC}"

    psql -h $DB_HOST -p $DB_PORT -U $DB_USER <<EOF
-- Create main BCM database
SELECT 'CREATE DATABASE bcm_platform OWNER $ODOO_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'bcm_platform');
\gexec

-- Create Keycloak database
SELECT 'CREATE DATABASE keycloak'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'keycloak');
\gexec

-- Create EventBus database
SELECT 'CREATE DATABASE eventbus_db OWNER $ODOO_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'eventbus_db');
\gexec

-- Create AI Orchestrator database
SELECT 'CREATE DATABASE ai_orchestrator_db OWNER $ODOO_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ai_orchestrator_db');
\gexec

-- Create Digital Twin database
SELECT 'CREATE DATABASE digital_twin_db OWNER $ODOO_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'digital_twin_db');
\gexec

-- Create Analytics database
SELECT 'CREATE DATABASE analytics_db OWNER $ODOO_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'analytics_db');
\gexec

-- Create test database
SELECT 'CREATE DATABASE bcm_test OWNER $ODOO_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'bcm_test');
\gexec

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE bcm_platform TO $ODOO_USER;
GRANT ALL PRIVILEGES ON DATABASE eventbus_db TO $ODOO_USER;
GRANT ALL PRIVILEGES ON DATABASE ai_orchestrator_db TO $ODOO_USER;
GRANT ALL PRIVILEGES ON DATABASE digital_twin_db TO $ODOO_USER;
GRANT ALL PRIVILEGES ON DATABASE analytics_db TO $ODOO_USER;
GRANT ALL PRIVILEGES ON DATABASE bcm_test TO $ODOO_USER;
EOF

    echo -e "${GREEN}✅ Databases created${NC}"
}

# Function to initialize schema
init_schema() {
    echo -e "${YELLOW}Initializing BCM Platform schema...${NC}"

    # Check if schema file exists
    SCHEMA_FILE="./core/database/02-init-bcm-schema.sql"
    if [ ! -f "$SCHEMA_FILE" ]; then
        echo -e "${RED}❌ Schema file not found: $SCHEMA_FILE${NC}"
        return 1
    fi

    # Execute schema
    PGPASSWORD=$ODOO_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $ODOO_USER -d bcm_platform -f "$SCHEMA_FILE"

    echo -e "${GREEN}✅ Schema initialized${NC}"
}

# Function to verify installation
verify_installation() {
    echo -e "${YELLOW}Verifying installation...${NC}"

    # Check tables
    TABLES=$(PGPASSWORD=$ODOO_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $ODOO_USER -d bcm_platform -t -c "
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema IN ('bcm', 'digital_twin', 'ai', 'eventbus', 'analytics');
    ")

    echo -e "  Tables created: ${TABLES// /}"

    # Check AI organs
    ORGANS=$(PGPASSWORD=$ODOO_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $ODOO_USER -d bcm_platform -t -c "
        SELECT COUNT(*) FROM ai.organs;
    ")

    echo -e "  AI organs registered: ${ORGANS// /}"

    # Check platform health
    PGPASSWORD=$ODOO_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $ODOO_USER -d bcm_platform -c "
        SELECT * FROM bcm.v_platform_health;
    "

    echo -e "${GREEN}✅ Installation verified${NC}"
}

# Function to show connection info
show_connection_info() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}          DATABASE CONNECTION INFO${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}PostgreSQL Connection:${NC}"
    echo "  Host: $DB_HOST"
    echo "  Port: $DB_PORT"
    echo "  Database: bcm_platform"
    echo "  Username: $ODOO_USER"
    echo "  Password: $ODOO_PASSWORD"
    echo ""
    echo -e "${GREEN}Connection string for Odoo:${NC}"
    echo "  postgresql://$ODOO_USER:$ODOO_PASSWORD@$DB_HOST:$DB_PORT/bcm_platform"
    echo ""
    echo -e "${GREEN}Databases created:${NC}"
    echo "  - bcm_platform (main)"
    echo "  - keycloak (SSO)"
    echo "  - eventbus_db (messaging)"
    echo "  - ai_orchestrator_db (AI)"
    echo "  - digital_twin_db (Digital Twin)"
    echo "  - analytics_db (reporting)"
    echo "  - bcm_test (testing)"
    echo ""
}

# Main execution
main() {
    case "${1:-}" in
        drop)
            echo -e "${RED}⚠️ WARNING: This will DROP all BCM databases!${NC}"
            read -p "Are you sure? Type 'yes' to confirm: " -r
            if [[ $REPLY == "yes" ]]; then
                echo -e "${YELLOW}Dropping databases...${NC}"
                psql -h $DB_HOST -p $DB_PORT -U $DB_USER <<EOF
DROP DATABASE IF EXISTS bcm_platform;
DROP DATABASE IF EXISTS eventbus_db;
DROP DATABASE IF EXISTS ai_orchestrator_db;
DROP DATABASE IF EXISTS digital_twin_db;
DROP DATABASE IF EXISTS analytics_db;
DROP DATABASE IF EXISTS bcm_test;
EOF
                echo -e "${GREEN}✅ Databases dropped${NC}"
            else
                echo "Cancelled"
            fi
            ;;

        reset)
            echo -e "${YELLOW}Resetting BCM Platform database...${NC}"
            $0 drop
            $0 init
            ;;

        verify)
            check_postgres || exit 1
            verify_installation
            ;;

        info)
            show_connection_info
            ;;

        init|*)
            # Full initialization
            check_postgres || exit 1
            create_odoo_user
            create_databases
            init_schema
            verify_installation
            show_connection_info

            echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
            echo -e "${GREEN}     🎉 DATABASE SETUP COMPLETED SUCCESSFULLY! 🎉${NC}"
            echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
            echo ""
            echo -e "${YELLOW}Next steps:${NC}"
            echo "  1. Start the platform: ./launch_bcm_platform.sh"
            echo "  2. Access Odoo: http://localhost:8069"
            echo "  3. Login with: admin/admin"
            echo ""
            echo -e "${YELLOW}Useful commands:${NC}"
            echo "  ./setup_database.sh verify  - Verify installation"
            echo "  ./setup_database.sh info    - Show connection info"
            echo "  ./setup_database.sh reset   - Reset database (DROP and recreate)"
            echo "  ./setup_database.sh drop    - Drop all databases"
            ;;
    esac
}

# Check for psql command
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ psql command not found${NC}"
    echo "Please install PostgreSQL client:"
    echo "  - macOS: brew install postgresql"
    echo "  - Ubuntu: sudo apt-get install postgresql-client"
    echo "  - CentOS: sudo yum install postgresql"
    exit 1
fi

# Run main function
main "$@"