# Service Discovery Configs

This directory contains Prometheus service discovery configurations for dynamically registered services.

## How It Works

1. **Automatic Registration**: When a BCM service starts, it calls `/register-service` endpoint on ISO 22301 Compliance API
2. **File Creation**: Compliance API creates a JSON file here: `{service_name}.json`
3. **Prometheus Discovery**: Prometheus automatically discovers the new service within 30 seconds
4. **Metrics Scraping**: Prometheus begins scraping metrics from the service's `/metrics` endpoint

## File Format

Each service discovery file is a JSON array with target and labels:

```json
[{
  "targets": ["service-name:port"],
  "labels": {
    "job": "service_name",
    "service_type": "bcm",
    "iso_clauses": "8.2.2,8.3",
    "compliance_critical": "true",
    "__metrics_path__": "/metrics"
  }
}]
```

## Manual Registration

You can manually create files here for services that don't auto-register:

```bash
# Example: Register external monitoring endpoint
cat > external-api.json <<EOF
[{
  "targets": ["api.example.com:443"],
  "labels": {
    "job": "external_api",
    "service_type": "external",
    "compliance_critical": "false"
  }
}]
EOF
```

Prometheus will discover it automatically within 30 seconds.

## Deregistration

When a service is deregistered via `/deregister-service/{name}`, its JSON file is automatically removed.
