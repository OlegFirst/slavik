#!/usr/bin/env python3
"""Generate platform-services documentation"""
import os
from pathlib import Path
from datetime import datetime

SERVICES = {
    "compliance-service": {"port": 8014, "iso": "9.2, 10.1, 10.2"},
    "risk-service": {"port": 8040, "iso": "8.2.3"},
    "bcm-coordination-service": {"port": 8070, "iso": "All"},
    "response-service": {"port": 8050, "iso": "8.4"},
    "governance-service": {"port": 8030, "iso": "4, 5, 7"},
    "planning-service": {"port": 8035, "iso": "8.3"},
    "plans-service": {"port": 8045, "iso": "8.4.2"},
    "documents-service": {"port": 8060, "iso": "7.5"},
    "learning-service": {"port": 8055, "iso": "7.2, 10.2"},
    "validation-service": {"port": 8065, "iso": "8.5"},
    "community-service": {"port": 8075, "iso": "All"}
}

for svc_name, cfg in SERVICES.items():
    svc_path = Path(f"platform-services/{svc_name}")
    docs_path = svc_path / "docs"
    docs_path.mkdir(parents=True, exist_ok=True)
    
    # Create docs/README.md index
    (docs_path / "README.md").write_text(f"""# {svc_name.replace('-', ' ').title()} - Documentation Index

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}

## Documentation Structure

1. [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md) - Architecture
2. [API.md](API.md) - API Reference  
3. [BUSINESS_LOGIC.md](BUSINESS_LOGIC.md) - Business Rules
4. [INTEGRATION.md](INTEGRATION.md) - Integration Guide
5. [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment Guide

**ISO 22301 Clause**: {cfg['iso']}
**Port**: {cfg['port']}
""")
    
    # Create placeholder docs
    for doc in ["TECHNICAL_SPECIFICATION.md", "API.md", "BUSINESS_LOGIC.md", "INTEGRATION.md", "DEPLOYMENT.md"]:
        (docs_path / doc).write_text(f"""# {svc_name.replace('-', ' ').title()} - {doc.replace('.md', '').replace('_', ' ')}

**Version**: 1.0.0
**Date**: {datetime.now().strftime('%Y-%m-%d')}
**ISO 22301 Clause**: {cfg['iso']}

## Overview

[To be completed]

See code in `/Users/MD/AI-Platform-ISO/platform-services/{svc_name}` for implementation details.

---
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
""")
    
    print(f"✅ Created docs for {svc_name}")

print(f"\n✅ Generated documentation for {len(SERVICES)} services")
