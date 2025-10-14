#!/bin/bash

################################################################################
# BCM Platform Backup Script
#
# This script performs automated backups of:
# - PostgreSQL databases
# - Redis data
# - Docker volumes
# - Configuration files
# - Application logs
#
# Usage: ./backup.sh [type]
# Types: full, database, volumes, config
# Example: ./backup.sh full
################################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/bcm}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_TYPE="${1:-full}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BUCKET:-}"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

################################################################################
# Logging
################################################################################

log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓${NC} $*"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗${NC} $*"
}

################################################################################
# Backup Functions
################################################################################

backup_database() {
    log "Backing up PostgreSQL databases..."

    mkdir -p "${BACKUP_DIR}/database"

    # Backup all databases
    docker compose -f "$COMPOSE_FILE" exec -T postgres pg_dumpall -U bcm_user | \
        gzip > "${BACKUP_DIR}/database/all_databases_${TIMESTAMP}.sql.gz"

    # Backup individual databases
    for db in bcm_platform planning plans governance risk response learning; do
        docker compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U bcm_user "$db" 2>/dev/null | \
            gzip > "${BACKUP_DIR}/database/${db}_${TIMESTAMP}.sql.gz" || {
            log_error "Failed to backup database: $db"
        }
    done

    # Backup schema only (for quick structure restore)
    docker compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U bcm_user --schema-only bcm_platform | \
        gzip > "${BACKUP_DIR}/database/schema_${TIMESTAMP}.sql.gz"

    log_success "Database backup completed"
}

backup_volumes() {
    log "Backing up Docker volumes..."

    mkdir -p "${BACKUP_DIR}/volumes"

    for volume in postgres_data redis_data grafana_data prometheus_data monitoring_logs; do
        if docker volume ls | grep -q "$volume"; then
            log "Backing up volume: $volume"
            docker run --rm \
                -v "platform-services_${volume}:/data:ro" \
                -v "${BACKUP_DIR}/volumes:/backup" \
                alpine tar czf "/backup/${volume}_${TIMESTAMP}.tar.gz" /data || {
                log_error "Failed to backup volume: $volume"
            }
        fi
    done

    log_success "Volume backup completed"
}

backup_config() {
    log "Backing up configuration files..."

    mkdir -p "${BACKUP_DIR}/config"

    tar czf "${BACKUP_DIR}/config/config_${TIMESTAMP}.tar.gz" \
        -C "$PROJECT_ROOT" \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='node_modules' \
        --exclude='.git' \
        .env \
        docker-compose.yml \
        docker-compose.prod.yml \
        monitoring/ \
        docs/ \
        scripts/ 2>/dev/null || {
        log_error "Configuration backup failed"
    }

    log_success "Configuration backup completed"
}

backup_logs() {
    log "Backing up application logs..."

    mkdir -p "${BACKUP_DIR}/logs"

    # Archive logs older than 24 hours
    find /var/log/bcm -name "*.log" -mtime +1 -type f | \
        tar czf "${BACKUP_DIR}/logs/logs_${TIMESTAMP}.tar.gz" -T - 2>/dev/null || {
        log_error "Log backup failed"
    }

    # Docker container logs
    for container in planning-service plans-service bia-service compliance-service; do
        docker logs "$container" --since 24h > "${BACKUP_DIR}/logs/${container}_${TIMESTAMP}.log" 2>&1 || {
            log_error "Failed to backup logs for: $container"
        }
    done

    log_success "Log backup completed"
}

################################################################################
# Upload to S3 (Optional)
################################################################################

upload_to_s3() {
    if [ -n "$S3_BUCKET" ]; then
        log "Uploading backups to S3: $S3_BUCKET"

        if command -v aws &> /dev/null; then
            aws s3 sync "$BACKUP_DIR" "s3://${S3_BUCKET}/bcm-backups/" \
                --exclude "*" \
                --include "*${TIMESTAMP}*" || {
                log_error "S3 upload failed"
                return 1
            }
            log_success "Backups uploaded to S3"
        else
            log_error "AWS CLI not installed, skipping S3 upload"
        fi
    fi
}

################################################################################
# Cleanup Old Backups
################################################################################

cleanup_old_backups() {
    log "Cleaning up backups older than ${RETENTION_DAYS} days..."

    # Local cleanup
    find "$BACKUP_DIR" -type f -mtime +${RETENTION_DAYS} -delete
    find "$BACKUP_DIR" -type d -empty -delete

    # S3 cleanup (if configured)
    if [ -n "$S3_BUCKET" ] && command -v aws &> /dev/null; then
        aws s3 rm "s3://${S3_BUCKET}/bcm-backups/" \
            --recursive \
            --exclude "*" \
            --include "*" \
            --older-than ${RETENTION_DAYS}d 2>/dev/null || {
            log_error "S3 cleanup failed"
        }
    fi

    log_success "Cleanup completed"
}

################################################################################
# Backup Verification
################################################################################

verify_backup() {
    log "Verifying backup integrity..."

    # Verify database backup
    if [ -f "${BACKUP_DIR}/database/all_databases_${TIMESTAMP}.sql.gz" ]; then
        if gunzip -t "${BACKUP_DIR}/database/all_databases_${TIMESTAMP}.sql.gz" 2>/dev/null; then
            log_success "Database backup verification passed"
        else
            log_error "Database backup is corrupted"
            return 1
        fi
    fi

    # Verify volume backups
    for volume_backup in "${BACKUP_DIR}/volumes"/*_${TIMESTAMP}.tar.gz; do
        if [ -f "$volume_backup" ]; then
            if tar tzf "$volume_backup" >/dev/null 2>&1; then
                log_success "Volume backup $(basename "$volume_backup") verified"
            else
                log_error "Volume backup $(basename "$volume_backup") is corrupted"
            fi
        fi
    done

    log_success "Backup verification completed"
}

################################################################################
# Generate Backup Report
################################################################################

generate_report() {
    log "Generating backup report..."

    REPORT_FILE="${BACKUP_DIR}/backup_report_${TIMESTAMP}.txt"

    cat > "$REPORT_FILE" <<EOF
BCM Platform Backup Report
==========================

Backup Date: $(date)
Backup Type: ${BACKUP_TYPE}
Backup Directory: ${BACKUP_DIR}

Backup Contents:
----------------

Database Backups:
$(ls -lh "${BACKUP_DIR}/database/"*${TIMESTAMP}* 2>/dev/null || echo "None")

Volume Backups:
$(ls -lh "${BACKUP_DIR}/volumes/"*${TIMESTAMP}* 2>/dev/null || echo "None")

Configuration Backups:
$(ls -lh "${BACKUP_DIR}/config/"*${TIMESTAMP}* 2>/dev/null || echo "None")

Log Backups:
$(ls -lh "${BACKUP_DIR}/logs/"*${TIMESTAMP}* 2>/dev/null || echo "None")

Total Backup Size:
$(du -sh "${BACKUP_DIR}" | awk '{print $1}')

Disk Space:
$(df -h "${BACKUP_DIR}" | awk 'NR==2 {print "Used: "$3" Available: "$4" Use%: "$5}')

EOF

    log_success "Backup report generated: $REPORT_FILE"
    cat "$REPORT_FILE"
}

################################################################################
# Main Execution
################################################################################

main() {
    log "=========================================="
    log "BCM Platform Backup Script"
    log "Backup Type: ${BACKUP_TYPE}"
    log "=========================================="

    # Create backup directory
    mkdir -p "$BACKUP_DIR"

    # Execute backup based on type
    case $BACKUP_TYPE in
        full)
            backup_database
            backup_volumes
            backup_config
            backup_logs
            ;;
        database)
            backup_database
            ;;
        volumes)
            backup_volumes
            ;;
        config)
            backup_config
            ;;
        *)
            log_error "Invalid backup type: $BACKUP_TYPE"
            log "Valid types: full, database, volumes, config"
            exit 1
            ;;
    esac

    # Verify backups
    verify_backup

    # Upload to S3 (if configured)
    upload_to_s3

    # Cleanup old backups
    cleanup_old_backups

    # Generate report
    generate_report

    log "=========================================="
    log "Backup completed successfully"
    log "=========================================="
}

main "$@"
