"""Compliance Policies (ISO 22301)"""

ISO_22301_REQUIREMENTS = {
    "8.2.2": {  # BIA
        "name": "Business Impact Analysis",
        "mandatory_fields": ["rto", "rpo", "impact_analysis"],
        "approval_required": True,
        "review_frequency_months": 6,
        "min_documentation_quality": 0.8
    },
    "8.2.3": {  # Risk Assessment
        "name": "Risk Assessment",
        "mandatory_fields": ["likelihood", "impact", "treatment_strategy"],
        "approval_required": True,
        "review_frequency_months": 12
    },
    "8.4": {  # BC Plan
        "name": "Business Continuity Plan",
        "mandatory_fields": ["scope", "strategies", "procedures"],
        "approval_required": True,
        "review_frequency_months": 6,
        "test_frequency_months": 12
    }
}
