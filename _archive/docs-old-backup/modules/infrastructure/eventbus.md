# Eventbus

**Type**: Infrastructure Component
**Domain**: Platform Infrastructure
**Status**: Active
**Version**: 2.0.0

## Overview

The Event Bus infrastructure provides asynchronous event-driven communication across all platform services. It implements publish-subscribe patterns using RabbitMQ, with support for event routing, dead letter queues, and message persistence.

## Metrics

| Metric | Value |
|--------|-------|
| **Total Lines of Code** | 3,445 |
| **Python Files** | 27 |
| **Classes** | 22 |
| **Functions** | 25 |
| **Configuration Files** | 0 |

## Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized components)
- Access to platform configuration

### Setup

```bash
cd infrastructure/eventbus

# Install dependencies (if applicable)
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Initialize component
./setup.sh
```

## Configuration

Infrastructure components are configured through environment variables and configuration files. Refer to component-specific documentation for detailed configuration options.

## Testing

```bash
# Run infrastructure tests
pytest tests/ -v

# Run integration tests
pytest tests/integration/ -v
```

## Standards Compliance

This infrastructure component adheres to:

- **ISO/IEC 27001:2022** - Information security management
- **ISO/IEC/IEEE 26514:2022** - Software documentation
- **Infrastructure as Code best practices**
- **Twelve-Factor App methodology**

## Related Components

- [Intelligent Core](../../intelligent-core/README.md) - AI and intelligence layer
- [Platform Services](../../platform-services/README.md) - Business services
- [Infrastructure Overview](../README.md) - Infrastructure layer overview

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: 2025-10-08
**Maintainer**: Platform Infrastructure Team
