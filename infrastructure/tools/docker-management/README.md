# Docker Management Module

## Overview
Production-ready Docker API wrapper for container lifecycle management supporting both docker-py client and docker-compose CLI.

## Extracted From
- **Source**: `/intelligent-core/orchestrator_обьединенный/core/docker_manager.py`
- **Date**: 2025-10-04
- **Original Size**: 421 lines

## What This Module Does
- **Lifecycle Management**: Start, stop, restart containers
- **Status Monitoring**: Get container status, health, uptime
- **Log Retrieval**: Fetch container logs
- **Scaling**: Scale services to N replicas
- **Command Execution**: Run commands inside containers
- **Dual Mode**: Works with docker-py SDK or falls back to CLI

## Status
**Production-Ready**

## Dependencies
- `docker-py` (optional) - Docker SDK for Python
- `docker-compose` CLI - Fallback mode
- Python 3.11+ with asyncio

## Key Features

### 1. Container Lifecycle
```python
# Start service
success = await docker_mgr.start_service("api_service", timeout=300)

# Stop service
success = await docker_mgr.stop_service("api_service")

# Restart service
success = await docker_mgr.restart_service("api_service")

# Force kill if needed
await docker_mgr._force_stop("api_service")
```

### 2. Status & Health Monitoring
```python
# Get detailed status
status = await docker_mgr.get_container_status("api_service")

if status:
    print(f"Status: {status.status}")
    print(f"Healthy: {status.is_healthy()}")
    print(f"Uptime: {status.uptime_seconds}s")
    print(f"Ports: {status.ports}")
```

### 3. Logs & Debugging
```python
# Get last 100 log lines
logs = await docker_mgr.get_container_logs("api_service", tail=100)
for line in logs:
    print(line)
```

### 4. Scaling
```python
# Scale to 3 replicas
success = await docker_mgr.scale_service("api_service", replicas=3)
```

### 5. Command Execution
```python
# Run command in container
output = await docker_mgr.execute_in_container(
    "postgres",
    ["psql", "-U", "postgres", "-c", "SELECT version();"]
)
```

## Container Status Object
```python
@dataclass
class ContainerStatus:
    name: str
    status: str  # running, stopped, restarting, exited, created
    health: Optional[str]  # healthy, unhealthy, starting, none
    uptime_seconds: Optional[int]
    ports: Dict[str, Any]
    image: Optional[str]
    labels: Dict[str, str]

    def is_running() -> bool
    def is_healthy() -> bool
```

## Usage Example
```python
from infrastructure.docker_management import DockerManager

# Initialize (tries docker-py, falls back to CLI)
docker_mgr = DockerManager(use_docker_client=True)

# Start multiple services
services = ['postgres', 'redis', 'api_service']
for service in services:
    success = await docker_mgr.start_service(service)
    if success:
        print(f"{service} started")

# Check status
status = await docker_mgr.get_container_status('postgres')
print(f"Postgres healthy: {status.is_healthy()}")

# Get logs if service fails
if not status.is_healthy():
    logs = await docker_mgr.get_container_logs('postgres', tail=50)
    print("Recent logs:", logs)

# Cleanup
docker_mgr.close()
```

## Configuration
```python
# Default configuration
compose_file = "docker-compose.yml"
project_name = "iso-22301"

# Timeouts
start_timeout = 300  # 5 minutes
stop_timeout = 60    # 1 minute
restart_timeout = 60 # 1 minute
```

## Operational Notes

### Dual Mode Operation
1. **Docker SDK Mode** (preferred):
   - Faster, more detailed info
   - Requires `docker-py` package
   - Direct API access

2. **CLI Fallback Mode**:
   - Works if SDK unavailable
   - Uses `docker-compose` commands
   - Slightly slower but reliable

### Health Checks
- Container is healthy if: `health == "healthy"` OR `(health is None AND status == "running")`
- Health check runs in executor to avoid blocking async loop

### Error Handling
- Timeouts trigger force kill
- 3+ failures stop deployment (via AI DevOps)
- All errors logged with context

## Integration Points
- **AI DevOps Engine**: Uses for deployment orchestration
- **Service Registry**: Provides container metadata
- **Health Monitor**: Container health status
- **Platform Orchestrator**: Service lifecycle management

## Production Best Practices
1. Always set reasonable timeouts
2. Check health after start/restart
3. Use force kill as last resort
4. Monitor logs on failures
5. Track uptime for SLA reporting

## Next Steps
1. Add Prometheus metrics export
2. Implement container resource limits checking
3. Add auto-restart on crash
4. Integrate with Kubernetes for production
5. Add container network inspection
