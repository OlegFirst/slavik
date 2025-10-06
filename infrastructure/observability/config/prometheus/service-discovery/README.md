# File-Based Service Discovery

Alternative service discovery directory for YAML/JSON format targets.

## Usage

Place YAML or JSON files here with target definitions:

**YAML Format:**
```yaml
- targets:
  - 'service1:8080'
  - 'service2:8081'
  labels:
    job: 'custom-services'
    environment: 'production'
```

**JSON Format:**
```json
[{
  "targets": ["service1:8080", "service2:8081"],
  "labels": {
    "job": "custom-services",
    "environment": "production"
  }
}]
```

Prometheus refreshes this directory every 30 seconds.
