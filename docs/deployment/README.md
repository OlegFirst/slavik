# Deployment

Infrastructure deployment guides, port mapping, and production setup documentation.

## Documents

- [EVENT_INTELLIGENCE_DEPLOYMENT_GUIDE.md](./EVENT_INTELLIGENCE_DEPLOYMENT_GUIDE.md) - Event intelligence deployment
- [FINAL_INFRASTRUCTURE_SETUP.md](./FINAL_INFRASTRUCTURE_SETUP.md) - Complete infrastructure setup
- [INFRASTRUCTURE_DEPLOYMENT_COMPLETE.md](./INFRASTRUCTURE_DEPLOYMENT_COMPLETE.md) - Deployment checklist
- [DEPLOYMENT_PORT_MAP.md](./DEPLOYMENT_PORT_MAP.md) - Port mapping (20 services)

## Current Deployment

- **Development**: Docker Compose
- **Production**: Kubernetes-ready
- **Services**: 12 platform + 11 intelligent-core
- **Infrastructure**: PostgreSQL, Redis, RabbitMQ, Qdrant
- **Monitoring**: Prometheus + Grafana

**Port Range**: 8000-8050, 5432, 6379, 6333, 9090, 3000

**Last Updated**: 2025-10-09
