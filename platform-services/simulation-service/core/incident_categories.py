"""
Default Incident/Scenario Categories and Escalation Rules
==========================================================

Extracted from BCM Incident module __init__.py (lines 24-76)

Provides default categories with:
- Severity levels
- RTO targets
- Auto-escalation timeouts
- Category codes

These can be used as templates for scenario generation.
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class IncidentCategory:
    """Incident/Scenario category template"""
    name: str
    code: str
    severity_default: str
    rto_default_hours: float
    auto_escalate_after_minutes: int
    description: str = ""


# Default categories from BCM Incident module
DEFAULT_CATEGORIES: List[IncidentCategory] = [
    IncidentCategory(
        name='Operational Disruption',
        code='OPS',
        severity_default='medium',
        rto_default_hours=4.0,
        auto_escalate_after_minutes=60,
        description='System outages, service disruptions, operational failures'
    ),
    IncidentCategory(
        name='Cyber Security Incident',
        code='CYBER',
        severity_default='high',
        rto_default_hours=1.0,
        auto_escalate_after_minutes=30,
        description='Ransomware, data breaches, DDoS attacks, unauthorized access'
    ),
    IncidentCategory(
        name='Natural Disaster',
        code='NATURAL',
        severity_default='critical',
        rto_default_hours=8.0,
        auto_escalate_after_minutes=15,
        description='Earthquakes, floods, fires, hurricanes, severe weather'
    ),
    IncidentCategory(
        name='Supply Chain Disruption',
        code='SUPPLY',
        severity_default='medium',
        rto_default_hours=24.0,
        auto_escalate_after_minutes=120,
        description='Supplier failures, logistics delays, procurement issues'
    ),
    IncidentCategory(
        name='Health & Safety Emergency',
        code='HEALTH',
        severity_default='critical',
        rto_default_hours=0.5,
        auto_escalate_after_minutes=10,
        description='Medical emergencies, contamination, evacuations, accidents'
    ),
    IncidentCategory(
        name='Financial Impact Event',
        code='FINANCIAL',
        severity_default='high',
        rto_default_hours=2.0,
        auto_escalate_after_minutes=45,
        description='Fraud, payment failures, market disruptions, financial losses'
    ),
]


# Response team templates from BCM Incident module (lines 120-169)
@dataclass
class ResponseTeamTemplate:
    """Response team template"""
    name: str
    code: str
    description: str
    activation_criteria: str
    roles: List[str]


DEFAULT_RESPONSE_TEAMS: List[ResponseTeamTemplate] = [
    ResponseTeamTemplate(
        name='Crisis Management Team',
        code='CMT',
        description='Executive-level crisis management',
        activation_criteria='Critical incidents requiring executive decision',
        roles=[
            'Incident Commander',
            'Communications Lead',
            'Operations Manager',
            'Legal Advisor',
            'HR Representative'
        ]
    ),
    ResponseTeamTemplate(
        name='IT Emergency Response',
        code='IT-ERT',
        description='Technical incident response team',
        activation_criteria='IT systems and cyber security incidents',
        roles=[
            'IT Manager',
            'Security Specialist',
            'Systems Administrator',
            'Network Engineer',
            'Database Administrator'
        ]
    ),
    ResponseTeamTemplate(
        name='Physical Security Team',
        code='PST',
        description='Physical security and safety response',
        activation_criteria='Physical security breaches and safety emergencies',
        roles=[
            'Security Manager',
            'Safety Officer',
            'Facilities Manager',
            'First Aid Responder',
            'Local Emergency Contact'
        ]
    ),
]


# AI Commander automation rules from BCM Incident (lines 79-117)
@dataclass
class AIAutomationRule:
    """AI automation rule"""
    name: str
    trigger_type: str
    condition: str
    action: str
    active: bool


DEFAULT_AI_RULES: List[AIAutomationRule] = [
    AIAutomationRule(
        name='Auto-classify by keywords',
        trigger_type='on_create',
        condition='description_contains_keywords',
        action='classify_incident',
        active=True
    ),
    AIAutomationRule(
        name='Auto-escalate critical incidents',
        trigger_type='on_severity_change',
        condition='severity_is_critical',
        action='immediate_escalation',
        active=True
    ),
    AIAutomationRule(
        name='Generate response checklist',
        trigger_type='on_status_change',
        condition='status_is_responding',
        action='create_checklist',
        active=True
    ),
    AIAutomationRule(
        name='Find similar incidents',
        trigger_type='on_create',
        condition='always',
        action='analyze_similar',
        active=True
    ),
]


# Helper functions

def get_category_by_code(code: str) -> IncidentCategory | None:
    """Get category by code"""
    for cat in DEFAULT_CATEGORIES:
        if cat.code == code:
            return cat
    return None


def get_category_by_name(name: str) -> IncidentCategory | None:
    """Get category by name"""
    for cat in DEFAULT_CATEGORIES:
        if cat.name.lower() == name.lower():
            return cat
    return None


def get_category_for_scenario_type(scenario_type: str) -> IncidentCategory | None:
    """
    Map scenario type to incident category

    Args:
        scenario_type: Scenario type from our system

    Returns:
        Matching incident category or None
    """
    mapping = {
        'cyber_security': 'CYBER',
        'disaster_recovery': 'OPS',
        'supply_chain': 'SUPPLY',
        'pandemic': 'HEALTH',
        'facility_damage': 'NATURAL',
        'system_failure': 'OPS',
        'crisis_management': 'OPS',
        'incident_response': 'OPS'
    }

    code = mapping.get(scenario_type)
    if code:
        return get_category_by_code(code)
    return None


def get_rto_for_category(category_code: str) -> float:
    """
    Get default RTO (hours) for category

    Args:
        category_code: Category code (OPS, CYBER, etc.)

    Returns:
        RTO in hours
    """
    cat = get_category_by_code(category_code)
    return cat.rto_default_hours if cat else 4.0  # Default 4 hours


def get_escalation_timeout(category_code: str) -> int:
    """
    Get auto-escalation timeout (minutes) for category

    Args:
        category_code: Category code

    Returns:
        Timeout in minutes
    """
    cat = get_category_by_code(category_code)
    return cat.auto_escalate_after_minutes if cat else 60  # Default 60 min


def get_response_team_for_category(category_code: str) -> ResponseTeamTemplate | None:
    """
    Get appropriate response team for category

    Args:
        category_code: Category code

    Returns:
        Response team template or None
    """
    team_mapping = {
        'CYBER': 'IT-ERT',
        'NATURAL': 'PST',
        'HEALTH': 'PST',
        'OPS': 'CMT',
        'SUPPLY': 'CMT',
        'FINANCIAL': 'CMT'
    }

    team_code = team_mapping.get(category_code)
    if team_code:
        for team in DEFAULT_RESPONSE_TEAMS:
            if team.code == team_code:
                return team

    return None


def to_dict_list() -> Dict[str, List[Dict[str, Any]]]:
    """
    Export all defaults as dictionaries

    Returns:
        Dictionary with categories, teams, and rules
    """
    return {
        'categories': [
            {
                'name': cat.name,
                'code': cat.code,
                'severity_default': cat.severity_default,
                'rto_default_hours': cat.rto_default_hours,
                'auto_escalate_after_minutes': cat.auto_escalate_after_minutes,
                'description': cat.description
            }
            for cat in DEFAULT_CATEGORIES
        ],
        'response_teams': [
            {
                'name': team.name,
                'code': team.code,
                'description': team.description,
                'activation_criteria': team.activation_criteria,
                'roles': team.roles
            }
            for team in DEFAULT_RESPONSE_TEAMS
        ],
        'ai_rules': [
            {
                'name': rule.name,
                'trigger_type': rule.trigger_type,
                'condition': rule.condition,
                'action': rule.action,
                'active': rule.active
            }
            for rule in DEFAULT_AI_RULES
        ]
    }
