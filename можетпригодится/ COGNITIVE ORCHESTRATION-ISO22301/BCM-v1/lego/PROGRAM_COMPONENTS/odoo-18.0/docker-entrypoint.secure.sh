#!/bin/bash
# Secure Docker entry point for BCM Odoo Platform
set -e

# Security: Exit on any error, undefined variables, and pipe failures
set -euo pipefail

# Security: Clear potentially dangerous environment variables
unset IFS

# Security: Set umask for restrictive file permissions
umask 027

# Function to log securely
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SECURE-ENTRY] $*" >&2
}

log "Starting secure BCM Odoo platform initialization..."

# Security: Validate user permissions
if [ "$(id -u)" = "0" ]; then
    log "ERROR: Container running as root. Security policy violation."
    exit 1
fi

# Security: Validate required directories exist and have correct permissions
required_dirs="/opt/odoo/data /opt/odoo/logs /opt/odoo/config /opt/odoo/addons"
for dir in $required_dirs; do
    if [ ! -d "$dir" ]; then
        log "ERROR: Required directory $dir does not exist"
        exit 1
    fi

    # Check ownership
    if [ "$(stat -c %u "$dir")" != "$(id -u)" ]; then
        log "ERROR: Directory $dir has incorrect ownership"
        exit 1
    fi
done

# Security: Validate configuration file
CONFIG_FILE="/opt/odoo/config/odoo.conf"
if [ ! -f "$CONFIG_FILE" ]; then
    log "ERROR: Configuration file $CONFIG_FILE not found"
    exit 1
fi

# Check config file permissions (should be 640)
config_perms=$(stat -c %a "$CONFIG_FILE")
if [ "$config_perms" != "640" ]; then
    log "WARNING: Configuration file has insecure permissions: $config_perms"
fi

# Security: Run dependency checks
log "Running security dependency checks..."
if [ -x "/opt/odoo/check_dependencies.sh" ]; then
    /opt/odoo/check_dependencies.sh
else
    log "WARNING: Dependency check script not found or not executable"
fi

# Security: Validate BCM modules integrity
log "Validating BCM modules integrity..."
bcm_modules_count=$(find /opt/odoo/addons -name "bcm_*" -type d | wc -l)
log "Found $bcm_modules_count BCM modules"

if [ "$bcm_modules_count" -lt 5 ]; then
    log "WARNING: Expected more BCM modules. Found: $bcm_modules_count"
fi

# Security: Set runtime security options
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export ODOO_RC="/opt/odoo/config/odoo.conf"

# Security: Additional Python path hardening
export PYTHONPATH="/opt/odoo/addons:${PYTHONPATH:-}"

# Security: Limit resource usage
ulimit -f 1000000  # Limit file size to 1GB
ulimit -v 4194304  # Limit virtual memory to 4GB
ulimit -n 1024     # Limit number of open files

# Security: Clear sensitive environment variables that might contain secrets
unset POSTGRES_PASSWORD ADMIN_PASSWORD DB_PASSWORD

log "Security checks completed. Starting Odoo with secure configuration..."

# Security: Use exec to replace shell process and handle signals properly
# This ensures proper signal handling and prevents zombie processes
exec "$@"