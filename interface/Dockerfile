# ============================================================================
# Frontend Interfaces Container - Production
# ============================================================================
# Contains: Admin Panel, User Portal, Control Center
# Ports: 3000, 3001, 3002
# ============================================================================

FROM node:20-alpine AS base

LABEL maintainer="AI Platform Team"
LABEL version="1.0.0"
LABEL description="Frontend Interfaces - Admin Panel, User Portal, Control Center"

WORKDIR /app

# ============================================================================
# System Dependencies
# ============================================================================
RUN apk add --no-cache \
    curl \
    bash \
    supervisor

# ============================================================================
# Build Admin Panel
# ============================================================================
FROM base AS build-admin
WORKDIR /build/admin
COPY admin_panel/package*.json ./
RUN npm ci --only=production
COPY admin_panel/ ./
RUN npm run build

# ============================================================================
# Build User Portal
# ============================================================================
FROM base AS build-portal
WORKDIR /build/portal
COPY user-portal/package*.json ./
RUN npm ci --only=production
COPY user-portal/ ./
RUN npm run build

# ============================================================================
# Build Control Center
# ============================================================================
FROM base AS build-control
WORKDIR /build/control
COPY admin-control-center/package*.json ./
RUN npm ci --only=production
COPY admin-control-center/ ./
RUN npm run build

# ============================================================================
# Production Stage
# ============================================================================
FROM base AS production

# Copy built applications
COPY --from=build-admin /build/admin /app/admin_panel
COPY --from=build-portal /build/portal /app/user-portal
COPY --from=build-control /build/control /app/admin-control-center

# ============================================================================
# Supervisor Configuration
# ============================================================================
RUN mkdir -p /var/log/supervisor /var/run

COPY <<EOF /etc/supervisord.conf
[supervisord]
nodaemon=true
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[program:admin-panel]
command=npm start
directory=/app/admin_panel
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/admin-panel.err.log
stdout_logfile=/var/log/supervisor/admin-panel.out.log
environment=PORT=3000,NODE_ENV=production

[program:user-portal]
command=npm start
directory=/app/user-portal
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/user-portal.err.log
stdout_logfile=/var/log/supervisor/user-portal.out.log
environment=PORT=3001,NODE_ENV=production

[program:control-center]
command=npm start
directory=/app/admin-control-center
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/control-center.err.log
stdout_logfile=/var/log/supervisor/control-center.out.log
environment=PORT=3002,NODE_ENV=production
EOF

# ============================================================================
# Health Check Script
# ============================================================================
COPY <<'EOF' /app/healthcheck.sh
#!/bin/bash
# Check if all frontend apps are responding

# Check Admin Panel
if ! wget -q --spider http://localhost:3000 2>/dev/null; then
    echo "❌ Admin Panel health check failed"
    exit 1
fi

# Check User Portal
if ! wget -q --spider http://localhost:3001 2>/dev/null; then
    echo "❌ User Portal health check failed"
    exit 1
fi

# Check Control Center
if ! wget -q --spider http://localhost:3002 2>/dev/null; then
    echo "❌ Control Center health check failed"
    exit 1
fi

echo "✅ All frontend interfaces healthy"
exit 0
EOF

RUN chmod +x /app/healthcheck.sh

# ============================================================================
# Non-root User
# ============================================================================
RUN adduser -D -u 1000 appuser && \
    chown -R appuser:appuser /app /var/log/supervisor /var/run

USER appuser

# ============================================================================
# Ports
# ============================================================================
EXPOSE 3000 3001 3002

# ============================================================================
# Health Check
# ============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD /app/healthcheck.sh

# ============================================================================
# Startup
# ============================================================================
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
