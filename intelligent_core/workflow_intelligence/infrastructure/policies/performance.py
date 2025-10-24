"""Performance & SLA Policies"""

SLA_POLICIES = {
    "bia_initiation": {
        "max_duration_hours": 24,
        "escalation_after_hours": 48,
        "priority": "high"
    },
    "impact_analysis": {
        "max_duration_hours": 72,
        "escalation_after_hours": 96
    },
    "approval": {
        "max_duration_hours": 48,
        "auto_escalate": True,
        "escalation_chain": ["manager", "senior_management"]
    }
}

TIMEOUT_POLICIES = {
    "form_fill": 300,  # 5 minutes
    "ai_analysis": 180,  # 3 minutes
    "document_generation": 120,  # 2 minutes
    "approval_notification": 30  # 30 seconds
}
