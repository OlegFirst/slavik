# Simulation Templates Catalog

This directory contains reusable simulation templates for BCM exercises.

## Template Sources

Templates can come from:
1. **Built-in**: Pre-configured templates for common BCM scenarios
2. **AI Generated**: Created by the scenario generator
3. **User Created**: Custom templates created through usage
4. **Community**: Shared from Community Intelligence
5. **External**: Imported from external sources

## Template Structure

Each template is a JSON file with the following structure:

```json
{
  "id": "template_id",
  "name": "Template Name",
  "description": "Template description",
  "category": "bia_exercise|cyber_security|disaster_recovery|...",
  "difficulty": 1-5,
  "duration_minutes": 60-480,
  "parameters": {
    "configurable_fields": [],
    "default_values": {},
    "constraints": {}
  },
  "scenario": {
    "incidents": [],
    "affected_processes": [],
    "success_criteria": []
  },
  "metadata": {
    "created_by": "source",
    "usage_count": 0,
    "average_rating": null,
    "tags": []
  }
}
```

## Usage

Templates are loaded by the Simulation Service and can be:
- Used directly for simulations
- Customized before use
- Extended with AI-generated content
- Rated and improved based on usage
