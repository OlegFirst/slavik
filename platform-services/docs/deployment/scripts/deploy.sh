#!/bin/bash

################################################################################
# BCM Platform Production Deployment Script
#
# This script automates the deployment of the BCM Platform to production.
# It includes pre-flight checks, backup, deployment, and verification.
#
# Usage: ./deploy.sh [version]
# Example: ./deploy.sh 1.0.0
################################################################################

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/bcm}"
LOG_FILE="${LOG_FILE:-/var/log/bcm/deployment.log}"
VERSION="${1:-latest}"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.prod.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

################################################################################
# Logging Functions
################################################################################

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓${NC} $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗${NC} $*" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠${NC} $*" | tee -a "$LOG_FILE"
}

################################################################################
# Pre-flight Checks
################################################################################

preflight_checks() {
    log "Running pre-flight checks..."

    # Check if running as root (not recommended)
    if [ "$EUID" -eq 0 ]; then
        log_warning "Running as root is not recommended. Consider using a dedicated user."
    fi

    # Check Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    log_success "Docker is installed: $(docker --version)"

    # Check Docker Compose is installed
    if ! command -v docker compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    log_success "Docker Compose is installed: $(docker compose version)"

    # Check if .env file exists
    if [ ! -f "${PROJECT_ROOT}/.env" ]; then
        log_error ".env file not found at ${PROJECT_ROOT}/.env"
        exit 1
    fi
    log_success ".env file found"

    # Check required environment variables
    source "${PROJECT_ROOT}/.env"
    required_vars=("POSTGRES_PASSWORD" "JWT_PUBLIC_KEY" "ENVIRONMENT")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    log_success "Required environment variables are set"

    # Check disk space (minimum 10GB free)
    free_space=$(df -BG "${PROJECT_ROOT}" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$free_space" -lt 10 ]; then
        log_error "Insufficient disk space: ${free_space}GB available, minimum 10GB required"
        exit 1
    fi
    log_success "Sufficient disk space: ${free_space}GB available"

    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_warning "Production compose file not found, using docker-compose.yml"
        COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
    fi
    log_success "Compose file: $COMPOSE_FILE"

    log_success "All pre-flight checks passed"
}

################################################################################
# Backup Current Deployment
################################################################################

backup_current() {
    log "Creating backup of current deployment..."

    mkdir -p "$BACKUP_DIR"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="${BACKUP_DIR}/backup_${TIMESTAMP}"

    # Backup database
    log "Backing up database..."
    docker compose -f "$COMPOSE_FILE" exec -T postgres pg_dumpall -U bcm_user | gzip > "${BACKUP_PATH}_database.sql.gz" || {
        log_warning "Database backup failed (container may not be running)"
    }

    # Backup volumes
    log "Backing up volumes..."
    for volume in postgres_data redis_data grafana_data prometheus_data; do
        if docker volume ls | grep -q "$volume"; then
            docker run --rm -v "platform-services_${volume}:/data" -v "${BACKUP_DIR}:/backup" \
                alpine tar czf "/backup/${TIMESTAMP}_${volume}.tar.gz" /data 2>/dev/null || {
                log_warning "Backup of volume $volume failed"
            }
        fi
    done

    # Backup configuration
    log "Backing up configuration..."
    tar czf "${BACKUP_PATH}_config.tar.gz" \
        "${PROJECT_ROOT}/.env" \
        "${PROJECT_ROOT}/docker-compose.yml" \
        "${PROJECT_ROOT}/monitoring/" 2>/dev/null || {
        log_warning "Configuration backup failed"
    }

    # Keep only last 7 backups
    log "Cleaning old backups (keeping last 7)..."
    cd "$BACKUP_DIR" && ls -t backup_* | tail -n +8 | xargs -r rm -f

    log_success "Backup created at ${BACKUP_PATH}"
}

################################################################################
# Build and Tag Images
################################################################################

build_images() {
    log "Building Docker images for version ${VERSION}..."

    cd "$PROJECT_ROOT"

    export BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    export VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    export VERSION

    # Build all services
    docker compose -f "$COMPOSE_FILE" build --parallel || {
        log_error "Image build failed"
        exit 1
    }

    # Tag images
    for service in planning-service plans-service bia-service compliance-service; do
        docker tag "bcm/${service}:latest" "bcm/${service}:${VERSION}" || {
            log_warning "Failed to tag ${service}"
        }
    done

    log_success "Images built and tagged successfully"
}

################################################################################
# Deploy Services
################################################################################

deploy_services() {
    log "Deploying services..."

    cd "$PROJECT_ROOT"

    # Stop current services
    log "Stopping current services..."
    docker compose -f "$COMPOSE_FILE" down || {
        log_warning "Failed to stop services gracefully"
    }

    # Start infrastructure services first
    log "Starting infrastructure services (postgres, redis)..."
    docker compose -f "$COMPOSE_FILE" up -d postgres redis

    # Wait for health checks
    log "Waiting for infrastructure services to be healthy..."
    sleep 30

    # Verify infrastructure is healthy
    if ! docker compose -f "$COMPOSE_FILE" ps postgres | grep -q "healthy"; then
        log_error "PostgreSQL is not healthy"
        exit 1
    fi

    if ! docker compose -f "$COMPOSE_FILE" ps redis | grep -q "healthy"; then
        log_error "Redis is not healthy"
        exit 1
    fi

    log_success "Infrastructure services are healthy"

    # Run database migrations (if applicable)
    log "Running database migrations..."
    # Uncomment if migrations are needed
    # docker compose -f "$COMPOSE_FILE" run --rm planning-service alembic upgrade head

    # Start application services
    log "Starting application services..."
    docker compose -f "$COMPOSE_FILE" up -d planning-service plans-service bia-service compliance-service

    # Wait for application services
    log "Waiting for application services to start..."
    sleep 60

    # Start monitoring services
    log "Starting monitoring services..."
    docker compose -f "$COMPOSE_FILE" up -d prometheus grafana monitoring-service

    log_success "All services deployed"
}

################################################################################
# Health Checks
################################################################################

verify_deployment() {
    log "Verifying deployment..."

    cd "$PROJECT_ROOT"

    # Check container status
    log "Checking container status..."
    docker compose -f "$COMPOSE_FILE" ps

    # Check health endpoints
    services=(
        "planning-service:8011"
        "plans-service:8023"
        "bia-service:8012"
        "compliance-service:8014"
        "monitoring-service:8045"
    )

    failed_checks=0
    for service_port in "${services[@]}"; do
        IFS=':' read -r service port <<< "$service_port"
        if curl -f -s -o /dev/null "http://localhost:${port}/health"; then
            log_success "$service is healthy"
        else
            log_error "$service health check failed"
            ((failed_checks++))
        fi
    done

    if [ $failed_checks -gt 0 ]; then
        log_error "Deployment verification failed: $failed_checks service(s) unhealthy"
        return 1
    fi

    # Check database connectivity
    log "Checking database connectivity..."
    if docker compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U bcm_user; then
        log_success "Database is accessible"
    else
        log_error "Database is not accessible"
        return 1
    fi

    # Check Redis connectivity
    log "Checking Redis connectivity..."
    if docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping | grep -q PONG; then
        log_success "Redis is accessible"
    else
        log_error "Redis is not accessible"
        return 1
    fi

    log_success "Deployment verification passed"
    return 0
}

################################################################################
# Rollback Function
################################################################################

rollback() {
    log_error "Deployment failed. Initiating rollback..."

    cd "$PROJECT_ROOT"

    # Stop failed deployment
    docker compose -f "$COMPOSE_FILE" down

    # Find latest backup
    latest_backup=$(ls -t "${BACKUP_DIR}"/backup_*_database.sql.gz 2>/dev/null | head -n1)

    if [ -z "$latest_backup" ]; then
        log_error "No backup found for rollback"
        exit 1
    fi

    backup_timestamp=$(basename "$latest_backup" | sed 's/backup_\(.*\)_database.sql.gz/\1/')

    # Restore database
    log "Restoring database from backup..."
    docker compose -f "$COMPOSE_FILE" up -d postgres
    sleep 20
    zcat "$latest_backup" | docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U bcm_user

    # Restore volumes
    for volume in postgres_data redis_data grafana_data prometheus_data; do
        backup_file="${BACKUP_DIR}/${backup_timestamp}_${volume}.tar.gz"
        if [ -f "$backup_file" ]; then
            log "Restoring volume $volume..."
            docker run --rm -v "platform-services_${volume}:/data" -v "${BACKUP_DIR}:/backup" \
                alpine tar xzf "/backup/$(basename "$backup_file")" -C / || {
                log_warning "Failed to restore volume $volume"
            }
        fi
    done

    # Start services with previous version
    docker compose -f "$COMPOSE_FILE" up -d

    log_warning "Rollback completed. Please investigate the deployment failure."
    exit 1
}

################################################################################
# Post-Deployment Tasks
################################################################################

post_deployment() {
    log "Running post-deployment tasks..."

    # Capture performance baseline
    log "Capturing performance baseline..."
    curl -s "http://localhost:9090/api/v1/query?query=up" > /dev/null || {
        log_warning "Failed to capture metrics baseline"
    }

    # Log deployment info
    log "Deployment Summary:"
    log "  Version: ${VERSION}"
    log "  Date: $(date)"
    log "  Git Commit: ${VCS_REF:-unknown}"
    log "  Deployed by: ${USER}"

    # Send notification (if configured)
    # if [ -n "${SLACK_WEBHOOK:-}" ]; then
    #     curl -X POST -H 'Content-type: application/json' \
    #         --data "{\"text\":\"BCM Platform ${VERSION} deployed successfully\"}" \
    #         "$SLACK_WEBHOOK"
    # fi

    log_success "Post-deployment tasks completed"
}

################################################################################
# Main Deployment Flow
################################################################################

main() {
    log "=========================================="
    log "BCM Platform Deployment Script"
    log "Version: ${VERSION}"
    log "=========================================="

    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"

    # Run pre-flight checks
    preflight_checks

    # Backup current deployment
    backup_current

    # Build images
    build_images

    # Deploy services
    deploy_services

    # Verify deployment
    if verify_deployment; then
        log_success "Deployment successful!"
        post_deployment
    else
        rollback
    fi

    log "=========================================="
    log "Deployment completed at $(date)"
    log "=========================================="
}

# Run main function
main "$@"
