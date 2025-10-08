#!/usr/bin/env python3
"""
Professional documentation generator for AI-Platform-ISO modules
Complies with ISO/IEC/IEEE 26514:2022 standards
English only, no emojis, formal technical writing
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Module type descriptions
MODULE_DESCRIPTIONS = {
    "collective": "The Collective module provides collective intelligence and collaborative decision-making capabilities, implementing privacy-preserving collaboration through advanced anonymization and secure multi-party computation.",

    "community_intelligence": "The Community Intelligence module enables knowledge sharing, reputation management, and collaborative learning across the platform. It implements contribution tracking, peer review systems, and intelligent knowledge synthesis.",

    "predictive": "The Predictive module delivers advanced predictive analytics and proactive recommendations for business continuity scenarios. It leverages machine learning models to forecast risks, predict incident impacts, and recommend preventive actions.",

    "orchestration": "The Orchestration module provides centralized coordination and control for all AI services and workflows. It implements intelligent task routing, resource allocation, and service mesh management.",

    "expertise-center": "The Expertise Center module provides domain-specific expertise and specialized AI assistants for business continuity management. It implements tactical assistants for BIA, compliance, governance, and other BCM domains.",

    "workflow-engine": "The Workflow Engine module provides BPMN 2.0 compliant workflow execution with persistent state management. It implements expression evaluation, gateway logic, and event-driven workflow coordination.",

    "event_intelligence": "The Event Intelligence module provides intelligent event analysis, pattern detection, and automated code healing. It implements domain detection, error analysis, and self-healing mechanisms for platform stability.",

    "ai_workflow_optimizer": "The AI Workflow Optimizer module provides intelligent workflow optimization using machine learning. It analyzes workflow performance, identifies bottlenecks, and recommends optimization strategies."
}

def generate_readme(module_name: str, section: str) -> str:
    """Generate professional README.md content"""

    # Load scan data
    scan_file = Path(f"/Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/devops-agent/reports-generated/modules/{module_name}_scan.json")

    if not scan_file.exists():
        print(f"❌ Scan file not found: {scan_file}")
        sys.exit(1)

    with open(scan_file) as f:
        data = json.load(f)

    metrics = data.get('metrics', {})

    # Generate module title (capitalize properly)
    title = module_name.replace('_', ' ').replace('-', ' ').title()

    # Get description
    description = MODULE_DESCRIPTIONS.get(module_name, f"The {title} module provides core functionality for the AI-Platform-ISO system.")

    readme = f"""# {title}

**Type**: Core Module
**Domain**: {section.title()}
**Status**: Active
**Version**: 2.0.0

## Overview

{description}

## Metrics

| Metric | Value |
|--------|-------|
| **Total Lines of Code** | {metrics.get('loc', 0):,} |
| **Python Files** | {metrics.get('python_files', 0)} |
| **Classes** | {metrics.get('classes', 0)} |
| **Functions** | {metrics.get('functions', 0)} |
| **API Endpoints** | {metrics.get('endpoints', 0)} |
| **Dependencies** | {metrics.get('dependencies', 0)} |

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### Setup

```bash
cd {section}/{module_name}

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Start service
python main.py
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov={module_name.replace('-', '_')} --cov-report=html
```

## Standards Compliance

This module adheres to:

- **ISO/IEC/IEEE 26514:2022** - Software documentation standards
- **ISO/IEC/IEEE 42010:2011** - Architecture description
- **ISO 22301:2019** - Business Continuity Management Systems (where applicable)

## License

Proprietary - AI-Platform-ISO

---

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
**Maintainer**: AI Platform Team
"""

    return readme

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 generate-module-docs.py <module_name> <section>")
        sys.exit(1)

    module_name = sys.argv[1]
    section = sys.argv[2]

    # Generate README
    readme_content = generate_readme(module_name, section)

    # Write to file
    output_path = Path(f"/Users/MD/AI-Platform-ISO/{section}/{module_name}/README.md")

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(readme_content)

    print(f"✅ Generated: {output_path}")
    print(f"   Size: {len(readme_content)} characters")

if __name__ == "__main__":
    main()
