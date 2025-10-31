# Environment Stability Issues and Solutions

## Problem
The development environment keeps disconnecting due to:
1. Docker daemon instability
2. Large image builds (815MB context) causing timeouts
3. Multiple services requiring orchestration

## Root Causes
- Docker build timeout (default 2 minutes) insufficient for 815MB BCM modules context
- Environment resource constraints causing Docker daemon crashes
- Heavy I/O during image builds affecting stability

## Solution Implemented

### 1. Staged Module Installation
Instead of installing all 19 BCM modules at once:
- First install only `bcm_core` foundation module
- Then install other modules incrementally via web interface or script
- This reduces initial load and improves stability

### 2. Startup Scripts Created
- `start-bcm-platform.sh` - Main startup script with staged installation
- `install-bcm-module.sh` - Helper script for installing additional modules

### 3. Environment Configuration
Created `.env` file with:
```
ODOO_INIT_BASE=1
ODOO_INSTALL_BCM_CORE=1
ODOO_CREATEDB=1
```
This ensures minimal initial setup, reducing timeout risks.

### 4. Ngrok Integration
- Configured ngrok with auth token: [REDACTED_FOR_SECURITY]
- Tunnel automatically starts on port 8069
- Public URL logged to ngrok.log

## Quick Recovery Steps

When environment disconnects:

1. Ensure Docker is running:
   ```bash
   docker version
   ```

2. Run the startup script:
   ```bash
   ./start-bcm-platform.sh
   ```

3. Check ngrok URL:
   ```bash
   grep 'url=' ngrok.log
   ```

## Module Installation Order

Based on dependencies, install modules in this order:
1. bcm_core (foundation - auto-installed)
2. bcm_config
3. bcm_risk_management
4. bcm_incident_management
5. bcm_business_impact_analysis
6. bcm_business_continuity_plan
7. bcm_reporting
8. Other modules as needed

## Current Status
- PostgreSQL, Redis, RabbitMQ: Running
- Odoo: Build completed, ready for staged deployment
- Ngrok: Configured and ready
- BCM Modules: 19 modules ready for incremental installation
