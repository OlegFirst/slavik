"""Security Policies for Process Framework"""

ROLE_PERMISSIONS = {
    "admin": ["*"],
    "bcm_manager": [
        "process.bia.create",
        "process.bia.execute",
        "process.risk.create",
        "process.risk.execute",
        "document.approve"
    ],
    "bcm_analyst": [
        "process.bia.execute",
        "process.risk.execute"
    ],
    "process_owner": [
        "process.view",
        "process.execute"
    ],
    "viewer": [
        "process.view",
        "document.view"
    ]
}

def check_permission(user_roles: list, required_permission: str) -> bool:
    """Check if user has permission"""
    for role in user_roles:
        permissions = ROLE_PERMISSIONS.get(role, [])
        if "*" in permissions or required_permission in permissions:
            return True
    return False
