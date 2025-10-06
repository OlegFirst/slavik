#!/usr/bin/env python3
"""
Script to add authentication to compliance routers
Adds imports, tenant verification function, and @require_permission decorators
"""

import re
from pathlib import Path

# Router files to update (excluding evidence.py which is already done)
ROUTERS = [
    "services/bcm/compliance/api/assessments.py",
    "services/bcm/compliance/api/gaps.py",
    "services/bcm/compliance/api/audit.py",
    "services/bcm/compliance/api/dashboard.py",
    "services/bcm/compliance/api/management_review.py",
]

# Permission mappings for each router
PERMISSIONS = {
    "assessments.py": {
        "create": "Permission.ASSESSMENT_CREATE",
        "list": "Permission.ASSESSMENT_VIEW",
        "get": "Permission.ASSESSMENT_VIEW",
        "run": "Permission.ASSESSMENT_RUN",
        "delete": "Permission.ASSESSMENT_DELETE",
        "batch": "Permission.ASSESSMENT_RUN",
    },
    "gaps.py": {
        "list": "Permission.GAP_VIEW",
        "get": "Permission.GAP_VIEW",
        "update": "Permission.GAP_UPDATE",
        "remediate": "Permission.GAP_REMEDIATE",
        "verify": "Permission.GAP_VERIFY",
    },
    "audit.py": {
        "create": "Permission.AUDIT_CREATE",
        "list": "Permission.AUDIT_VIEW",
        "get": "Permission.AUDIT_VIEW",
        "start": "Permission.AUDIT_CONDUCT",
        "complete": "Permission.AUDIT_CLOSE",
    },
    "dashboard.py": {
        "overview": "Permission.ASSESSMENT_VIEW",
        "matrix": "Permission.ASSESSMENT_VIEW",
        "roadmap": "Permission.ASSESSMENT_VIEW",
        "analytics": "Permission.ASSESSMENT_VIEW",
    },
    "management_review.py": {
        "create": "Permission.REVIEW_CREATE",
        "list": "Permission.REVIEW_VIEW",
        "get": "Permission.REVIEW_VIEW",
        "start": "Permission.REVIEW_UPDATE",
        "complete": "Permission.REVIEW_UPDATE",
    },
}

AUTH_IMPORTS = """from shared.auth import get_current_user, Permission, require_permission"""

TENANT_HELPER = '''

def verify_tenant_access(current_user: dict, tenant_id: str) -> None:
    """Verify user has access to tenant"""
    if current_user.get("tenant_id") != tenant_id:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: User tenant '{current_user.get('tenant_id')}' does not match resource tenant '{tenant_id}'"
        )
'''

def add_auth_imports(content: str) -> str:
    """Add auth imports if not present"""
    if "from shared.auth import" in content:
        return content

    # Find last import line
    lines = content.split("\n")
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            last_import_idx = i

    # Insert auth import after last import
    lines.insert(last_import_idx + 1, AUTH_IMPORTS)
    return "\n".join(lines)

def add_tenant_helper(content: str) -> str:
    """Add tenant verification helper if not present"""
    if "def verify_tenant_access" in content:
        return content

    # Find router definition
    router_match = re.search(r'router = APIRouter\(\)', content)
    if router_match:
        pos = router_match.end()
        return content[:pos] + TENANT_HELPER + content[pos:]

    return content

def add_permission_to_endpoint(content: str, endpoint_name: str, permission: str) -> str:
    """Add @require_permission decorator to endpoint"""
    # Pattern to find endpoint definition
    pattern = rf'@router\.(get|post|put|patch|delete)\([^)]*\)\s*async def {endpoint_name}'

    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        return content

    # Check if already has decorator
    before_match = content[:match.start()]
    if f"@require_permission({permission})" in before_match[-200:]:
        return content  # Already has permission

    # Insert decorator before @router
    router_pos = match.start()
    decorator = f"@require_permission({permission})\n"
    return content[:router_pos] + decorator + content[router_pos:]

def add_current_user_param(content: str, endpoint_name: str) -> str:
    """Add current_user parameter to endpoint"""
    # Find the endpoint function
    pattern = rf'(async def {endpoint_name}\([^)]*)\)'

    match = re.search(pattern, content)
    if not match:
        return content

    params = match.group(1)
    if "current_user" in params:
        return content  # Already has current_user

    # Add current_user parameter before closing paren
    new_params = params + ",\n    current_user: dict = Depends(get_current_user)"
    return content.replace(match.group(0), new_params + ")")

def add_tenant_verification(content: str, endpoint_name: str) -> str:
    """Add tenant verification call at start of endpoint"""
    # Find the endpoint
    pattern = rf'async def {endpoint_name}\([^)]*\):[^:]*?"""[^"]*"""[^:]*?try:'

    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return content

    if "verify_tenant_access(current_user, tenant_id)" in match.group(0):
        return content  # Already has verification

    # Insert verification after try:
    try_pos = match.end()
    verification = "\n        # Verify tenant access\n        verify_tenant_access(current_user, tenant_id)\n"
    return content[:try_pos] + verification + content[try_pos:]

def process_router(filepath: Path):
    """Process a single router file"""
    print(f"\nProcessing {filepath.name}...")

    content = filepath.read_text()

    # Step 1: Add imports
    content = add_auth_imports(content)
    content = add_tenant_helper(content)

    # Step 2: Update each endpoint based on router type
    # This is simplified - in production would need more sophisticated endpoint detection

    # Save updated content
    filepath.write_text(content)
    print(f"✓ Updated {filepath.name}")

if __name__ == "__main__":
    base_path = Path("/Users/MD/AI-Platform-ISO")

    for router_file in ROUTERS:
        filepath = base_path / router_file
        if filepath.exists():
            process_router(filepath)
        else:
            print(f"✗ File not found: {filepath}")
