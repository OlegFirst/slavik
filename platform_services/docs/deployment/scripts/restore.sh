#!/bin/bash

################################################################################
# BCM Platform Restore Script
#
# Restores BCM Platform from backup
#
# Usage: ./restore.sh <backup_timestamp> [--no-confirm]
# Example: ./restore.sh 20241003_120000
################################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/bcm}"
BACKUP_TIMESTAMP="${1:-}"
NO_CONFIRM="${2:-}"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

################################################################################
# Logging
################################################################################

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓${NC} $*"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠${NC} $*"
}

################################################################################
# Validation
################################################################################

validate_backup() {
    log "Validating backup..."

    if [ -z "$BACKUP_TIMESTAMP" ]; then
        log_error "No backup timestamp provided"
        echo ""
        echo "Usage: $0 <backup_timestamp>"
        echo ""
        echo "Available backups:"
        ls -lh "${BACKUP_DIR}/database/" | grep -E "_[0-9]{8}_[0-9]{6}" || echo "No backups found"
        exit 1
    fi

    # Check if backup files exist
    DATABASE_BACKUP="${BACKUP_DIR}/database/all_databases_${BACKUP_TIMESTAMP}.sql.gz"

    if [ ! -f "$DATABASE_BACKUP" ]; then
        log_error "Database backup not found: $DATABASE_BACKUP"
        echo ""
        echo "Available database backups:"
        ls -lh "${BACKUP_DIR}/database/" | grep "all_databases" || echo "No database backups found"
        exit 1
    fi

    # Verify backup integrity
    if ! gunzip -t "$DATABASE_BACKUP" 2>/dev/null; then
        log_error "Database backup is corrupted: $DATABASE_BACKUP"
        exit 1
    fi

    log_success "Backup validation passed"
}

################################################################################
# Confirmation
################################################################################

confirm_restore() {
    if [ "$NO_CONFIRM" = "--no-confirm" ]; then
        return 0
    fi

    log_warning "WARNING: This will stop all services and restore from backup"
    log_warning "Backup timestamp: ${BACKUP_TIMESTAMP}"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log "Restore cancelled by user"
        exit 0
    fi
}

################################################################################
# Pre-Restore Backup
################################################################################

create_pre_restore_backup() {
    log "Creating pre-restore backup of current state..."

    PRE_RESTORE_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    PRE_RESTORE_DIR="${BACKUP_DIR}/pre_restore_${PRE_RESTORE_TIMESTAMP}"

    mkdir -p "$PRE_RESTORE_DIR"

    # Backup current database
    docker compose -f "$COMPOSE_FILE" exec -T postgres pg_dumpall -U bcm_user | \
        gzip > "${PRE_RESTORE_DIR}/database.sql.gz" || {
        log_warning "Failed to backup current database"
    }

    log_success "Pre-restore backup created at: $PRE_RESTORE_DIR"
}

################################################################################
# Stop Services
################################################################################

stop_services() {
    log "Stopping all services..."

    cd "$PROJECT_ROOT"
    docker compose -f "$COMPOSE_FILE" down || {
        log_error "Failed to stop services"
        exit 1
    }

    log_success "All services stopped"
}

################################################################################
# Restore Database
################################################################################

restore_database() {
    log "Restoring database from backup..."

    # Start PostgreSQL
    docker compose -f "$COMPOSE_FILE" up -d postgres

    # Wait for PostgreSQL to be ready
    log "Waiting for PostgreSQL to be ready..."
    sleep 20

    for i in {1..30}; do
        if docker compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U bcm_user > /dev/null 2>&1; then
            break
        fi
        sleep 2
    done

    # Restore database
    DATABASE_BACKUP="${BACKUP_DIR}/database/all_databases_${BACKUP_TIMESTAMP}.sql.gz"

    zcat "$DATABASE_BACKUP" | docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U bcm_user postgres || {
        log_error "Database restore failed"
        exit 1
    }

    log_success "Database restored successfully"
}

################################################################################
# Restore Volumes
################################################################################

restore_volumes() {
    log "Restoring Docker volumes..."

    for volume in postgres_data redis_data grafana_data prometheus_data monitoring_logs; do
        VOLUME_BACKUP="${BACKUP_DIR}/volumes/${volume}_${BACKUP_TIMESTAMP}.tar.gz"

        if [ -f "$VOLUME_BACKUP" ]; then
            log "Restoring volume: $volume"

            # Remove existing volume
            docker volume rm "platform-services_${volume}" 2>/dev/null || true

            # Create new volume
            docker volume create "platform-services_${volume}"

            # Restore data
            docker run --rm \
                -v "platform-services_${volume}:/data" \
                -v "${BACKUP_DIR}/volumes:/backup" \
                alpine tar xzf "/backup/$(basename "$VOLUME_BACKUP")" -C / || {
                log_error "Failed to restore volume: $volume"
            }

            log_success "Volume $volume restored"
        else
            log_warning "Volume backup not found: $VOLUME_BACKUP"
        fi
    done
}

################################################################################
# Restore Configuration
################################################################################

restore_config() {
    log "Restoring configuration files..."

    CONFIG_BACKUP="${BACKUP_DIR}/config/config_${BACKUP_TIMESTAMP}.tar.gz"

    if [ -f "$CONFIG_BACKUP" ]; then
        # Backup current config first
        if [ -f "${PROJECT_ROOT}/.env" ]; then
            cp "${PROJECT_ROOT}/.env" "${PROJECT_ROOT}/.env.pre_restore_${PRE_RESTORE_TIMESTAMP}"
        fi

        # Restore config (excluding .env for safety)
        tar xzf "$CONFIG_BACKUP" -C "$PROJECT_ROOT" \
            --exclude='.env' \
            docker-compose.yml \
            monitoring/ \
            docs/ \
            scripts/ 2>/dev/null || {
            log_warning "Configuration restore failed (partial)"
        }

        log_success "Configuration restored (excluding .env for safety)"
        log_warning "Previous .env backed up to: .env.pre_restore_${PRE_RESTORE_TIMESTAMP}"
    else
        log_warning "Configuration backup not found: $CONFIG_BACKUP"
    fi
}

################################################################################
# Start Services
################################################################################

start_services() {
    log "Starting all services..."

    cd "$PROJECT_ROOT"

    # Start infrastructure services
    docker compose -f "$COMPOSE_FILE" up -d postgres redis

    # Wait for infrastructure
    sleep 30

    # Start application services
    docker compose -f "$COMPOSE_FILE" up -d

    # Wait for services to start
    sleep 60

    log_success "All services started"
}

################################################################################
# Verify Restore
################################################################################

verify_restore() {
    log "Verifying restore..."

    # Run health checks
    "${SCRIPT_DIR}/health_check.sh" || {
        log_error "Health checks failed after restore"
        return 1
    }

    # Verify database
    if docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U bcm_user -d bcm_platform -c "SELECT 1" > /dev/null 2>&1; then
        log_success "Database is accessible"
    else
        log_error "Database is not accessible"
        return 1
    fi

    # Check service endpoints
    for port in 8011 8023 8012 8014; do
        if curl -f -s -o /dev/null --max-time 5 "http://localhost:${port}/health"; then
            log_success "Service on port $port is healthy"
        else
            log_warning "Service on port $port is not responding"
        fi
    done

    log_success "Restore verification completed"
}

################################################################################
# Generate Restore Report
################################################################################

generate_report() {
    log "Generating restore report..."

    REPORT_FILE="${BACKUP_DIR}/restore_report_${PRE_RESTORE_TIMESTAMP}.txt"

    cat > "$REPORT_FILE" <<EOF
BCM Platform Restore Report
===========================

Restore Date: $(date)
Backup Timestamp: ${BACKUP_TIMESTAMP}
Pre-Restore Backup: ${PRE_RESTORE_DIR}

Restore Summary:
----------------
Database: Restored from ${DATABASE_BACKUP}
Volumes: Restored from ${BACKUP_DIR}/volumes/
Configuration: Restored from ${BACKUP_DIR}/config/

Service Status:
---------------
$(docker compose -f "$COMPOSE_FILE" ps)

Database Status:
----------------
$(docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U bcm_user -c "\l" || echo "Database not accessible")

Disk Space After Restore:
-------------------------
$(df -h "${PROJECT_ROOT}" | awk 'NR==2 {print "Used: "$3" Available: "$4" Use%: "$5}')

EOF

    log_success "Restore report generated: $REPORT_FILE"
    cat "$REPORT_FILE"
}

################################################################################
# Main Execution
################################################################################

main() {
    log "=========================================="
    log "BCM Platform Restore Script"
    log "=========================================="

    # Validate backup
    validate_backup

    # Confirm restore
    confirm_restore

    # Create pre-restore backup
    create_pre_restore_backup

    # Stop services
    stop_services

    # Restore database
    restore_database

    # Restore volumes (optional - uncomment if needed)
    # restore_volumes

    # Restore configuration
    restore_config

    # Start services
    start_services

    # Verify restore
    if verify_restore; then
        log_success "Restore completed successfully!"
    else
        log_error "Restore completed but verification failed"
        log_warning "Please check the services manually"
    fi

    # Generate report
    generate_report

    log "=========================================="
    log "Restore process completed"
    log "Pre-restore backup available at: $PRE_RESTORE_DIR"
    log "=========================================="
}

main "$@"
