#!/usr/bin/env python3
"""
Generate OpenAPI specification for Community Intelligence API

Usage:
    python scripts/generate_openapi.py

Outputs:
    - openapi.json (JSON format)
    - openapi.yaml (YAML format)
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from community_intelligence.main import app


def generate_openapi_spec():
    """Generate and save OpenAPI specification"""

    # Get OpenAPI spec from FastAPI
    spec = app.openapi()

    # Save as JSON
    json_path = Path(__file__).parent.parent / 'openapi.json'
    with open(json_path, 'w') as f:
        json.dump(spec, f, indent=2)

    print(f" OpenAPI JSON saved to: {json_path}")

    # Try to save as YAML (if pyyaml available)
    try:
        import yaml
        yaml_path = Path(__file__).parent.parent / 'openapi.yaml'
        with open(yaml_path, 'w') as f:
            yaml.dump(spec, f, sort_keys=False)
        print(f" OpenAPI YAML saved to: {yaml_path}")
    except ImportError:
        print("️  pyyaml not installed - skipping YAML output")
        print("   Install with: pip install pyyaml")

    # Print summary
    print("\n API Summary:")
    print(f"   Title: {spec['info']['title']}")
    print(f"   Version: {spec['info']['version']}")
    print(f"   Endpoints: {len(spec['paths'])}")
    print(f"   Tags: {len(spec.get('tags', []))}")

    # List all endpoints
    print("\n Endpoints:")
    for path, methods in spec['paths'].items():
        for method in methods.keys():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                summary = methods[method].get('summary', 'No summary')
                print(f"   {method.upper():6} {path:60} - {summary}")


if __name__ == "__main__":
    generate_openapi_spec()
