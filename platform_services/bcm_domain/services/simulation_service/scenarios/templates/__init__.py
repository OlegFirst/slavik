"""
BCM Scenario Templates

Pre-built scenario templates for various BCM categories:
- IT System Failure
- Pandemic Response
- Natural Disaster
- Cyber Attack (Ransomware)
- Supply Chain Disruption
- Data Breach

Each template includes:
- Scenario narrative
- Timeline
- Injects
- Success metrics
- Participant roles
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path


# Template categories
TEMPLATE_CATEGORIES = {
    "cyber": "Cyber Security Incidents",
    "pandemic": "Pandemic and Health Emergencies",
    "disaster": "Natural Disasters",
    "supply_chain": "Supply Chain Disruptions",
    "data_breach": "Data Security Breaches",
    "power_outage": "Infrastructure Failures"
}

# Available template IDs
AVAILABLE_TEMPLATES = [
    "it_failure",
    "pandemic",
    "disaster",
    "ransomware",
    "supply_chain",
    "data_breach"
]


def get_template(template_id: str) -> Dict[str, Any]:
    """
    Get scenario template by ID

    Args:
        template_id: Template identifier

    Returns:
        Template dictionary

    Raises:
        ValueError: If template not found
    """
    templates = {
        "it_failure": get_it_failure_template(),
        "pandemic": get_pandemic_template(),
        "disaster": get_disaster_template(),
        "ransomware": get_ransomware_template(),
        "supply_chain": get_supply_chain_template(),
        "data_breach": get_data_breach_template(),
    }

    if template_id not in templates:
        raise ValueError(f"Template '{template_id}' not found. Available: {list(templates.keys())}")

    return templates[template_id]


def list_templates() -> List[Dict[str, Any]]:
    """
    List all available templates

    Returns:
        List of template metadata
    """
    return [
        {
            "id": "it_failure",
            "title": "IT System Failure and Recovery",
            "category": "disaster",
            "complexity": 3,
            "description": "Critical IT systems failure requiring emergency response"
        },
        {
            "id": "pandemic",
            "title": "Pandemic Response and Business Continuity",
            "category": "pandemic",
            "complexity": 4,
            "description": "Organizational response to pandemic affecting workforce"
        },
        {
            "id": "disaster",
            "title": "Natural Disaster - Facility Evacuation",
            "category": "disaster",
            "complexity": 4,
            "description": "Natural disaster requiring facility evacuation and relocation"
        },
        {
            "id": "ransomware",
            "title": "Ransomware Attack on Critical Systems",
            "category": "cyber",
            "complexity": 5,
            "description": "Sophisticated ransomware attack encrypting critical business systems"
        },
        {
            "id": "supply_chain",
            "title": "Supply Chain Disruption",
            "category": "supply_chain",
            "complexity": 3,
            "description": "Major supplier failure affecting production capabilities"
        },
        {
            "id": "data_breach",
            "title": "Data Breach and Customer Notification",
            "category": "data_breach",
            "complexity": 4,
            "description": "Customer data breach requiring notification and response"
        }
    ]


def get_it_failure_template() -> Dict[str, Any]:
    """IT System Failure template"""
    return {
        "title": "IT System Failure and Recovery",
        "category": "disaster",
        "complexity": 3,
        "scenario_type": "tabletop",
        "description": "Critical IT infrastructure failure affecting core business operations",
        "content": """
# IT System Failure Scenario

## Situation
At 09:15 AM, your organization's primary data center experiences a catastrophic cooling system failure.
Within 30 minutes, critical servers begin overheating and shutting down. The backup generator fails to
activate properly, compounding the emergency.

## Impact
- Email systems offline
- Customer database inaccessible
- Internal communication systems down
- E-commerce platform unavailable
- Financial systems offline

## Your Challenge
As the BCM team, you must coordinate the response, activate recovery procedures, communicate with
stakeholders, and restore critical services within RTOs.
        """,
        "timeline": [
            {"time": "09:15", "event": "Cooling system alarm triggered"},
            {"time": "09:30", "event": "First servers begin shutting down"},
            {"time": "09:45", "event": "Backup generator fails to start"},
            {"time": "10:00", "event": "Complete data center outage"},
            {"time": "10:15", "event": "DR site activation initiated"},
            {"time": "12:00", "event": "Partial services restored"},
            {"time": "16:00", "event": "Full restoration target"}
        ],
        "injects": [
            {
                "time": "10:30",
                "title": "Media Inquiry",
                "description": "Local news outlet calls asking about service disruption",
                "requires_response": True
            },
            {
                "time": "11:00",
                "title": "Customer Escalation",
                "description": "Major client threatens to cancel contract due to outage",
                "requires_response": True
            },
            {
                "time": "13:00",
                "title": "Staff Morale",
                "description": "Staff becoming frustrated with manual workarounds",
                "requires_response": True
            }
        ],
        "success_metrics": {
            "recovery_time": "< 8 hours",
            "data_loss": "< 1 hour",
            "customer_satisfaction": "> 70%",
            "communication_effectiveness": "> 80%"
        },
        "participant_roles": [
            "BCM Coordinator",
            "IT Director",
            "Communications Manager",
            "Customer Service Lead",
            "Facilities Manager",
            "Executive Sponsor"
        ],
        "recommended_participants_count": 8
    }


def get_pandemic_template() -> Dict[str, Any]:
    """Pandemic Response template"""
    return {
        "title": "Pandemic Response and Business Continuity",
        "category": "pandemic",
        "complexity": 4,
        "scenario_type": "functional",
        "description": "Managing business operations during pandemic outbreak",
        "content": """
# Pandemic Response Scenario

## Situation
A highly contagious respiratory illness is spreading rapidly. Local authorities announce that 30% of
the workforce may be unable to work over the next 6 weeks due to illness or quarantine requirements.

## Impact
- Reduced workforce availability
- Remote work requirements
- Supply chain disruptions
- Customer service challenges
- Employee health and safety concerns

## Your Challenge
Implement pandemic response plans, enable remote work, maintain essential services, and support
employee well-being throughout the crisis.
        """,
        "timeline": [
            {"time": "Week 0", "event": "Initial outbreak reported"},
            {"time": "Week 1", "event": "10% workforce affected"},
            {"time": "Week 2", "event": "Remote work mandate"},
            {"time": "Week 3", "event": "Peak illness (30% workforce)"},
            {"time": "Week 4", "event": "Supply chain disruptions"},
            {"time": "Week 5", "event": "Recovery begins"},
            {"time": "Week 6", "event": "Return to normal operations"}
        ],
        "injects": [
            {
                "time": "Week 1 Day 3",
                "title": "Executive Illness",
                "description": "CEO tests positive and must quarantine",
                "requires_response": True
            },
            {
                "time": "Week 2 Day 2",
                "title": "Vendor Closure",
                "description": "Critical vendor closes facility due to outbreak",
                "requires_response": True
            },
            {
                "time": "Week 3 Day 4",
                "title": "Mental Health Crisis",
                "description": "Employees reporting high stress and burnout",
                "requires_response": True
            }
        ],
        "success_metrics": {
            "service_continuity": "> 80%",
            "employee_safety": "100%",
            "customer_retention": "> 90%",
            "remote_work_effectiveness": "> 75%"
        },
        "participant_roles": [
            "BCM Coordinator",
            "HR Director",
            "Operations Manager",
            "IT Director",
            "Health & Safety Officer",
            "Communications Lead",
            "Executive Leadership"
        ],
        "recommended_participants_count": 10
    }


def get_disaster_template() -> Dict[str, Any]:
    """Natural Disaster template"""
    return {
        "title": "Natural Disaster - Facility Evacuation",
        "category": "disaster",
        "complexity": 4,
        "scenario_type": "full_scale",
        "description": "Emergency evacuation and relocation due to natural disaster",
        "content": """
# Natural Disaster Scenario

## Situation
A category 4 hurricane is forecast to make landfall near your facility in 48 hours. Mandatory
evacuation orders are expected. You must secure the facility, evacuate staff, and activate
alternate site operations.

## Impact
- Facility closure for 2+ weeks
- Staff relocation required
- Equipment and data protection needed
- Customer service continuity challenges
- Potential physical damage to facility

## Your Challenge
Execute evacuation plan, activate alternate site, maintain business operations, ensure staff
safety, and prepare for facility recovery.
        """,
        "timeline": [
            {"time": "T-48h", "event": "Hurricane warning issued"},
            {"time": "T-36h", "event": "Evacuation plan activated"},
            {"time": "T-24h", "event": "Facility shutdown begins"},
            {"time": "T-12h", "event": "Complete evacuation"},
            {"time": "T+0h", "event": "Hurricane landfall"},
            {"time": "T+24h", "event": "Damage assessment begins"},
            {"time": "T+72h", "event": "Alternate site fully operational"}
        ],
        "injects": [
            {
                "time": "T-30h",
                "title": "Key Personnel Unavailable",
                "description": "DR site manager unable to travel due to family emergency",
                "requires_response": True
            },
            {
                "time": "T+6h",
                "title": "Facility Damage Report",
                "description": "Security cameras show water damage to ground floor",
                "requires_response": True
            },
            {
                "time": "T+48h",
                "title": "Vendor Price Gouging",
                "description": "Emergency suppliers demanding 300% markup",
                "requires_response": True
            }
        ],
        "success_metrics": {
            "staff_safety": "100%",
            "data_protection": "100%",
            "service_recovery_time": "< 72 hours",
            "facility_readiness": "> 80%"
        },
        "participant_roles": [
            "BCM Coordinator",
            "Facilities Manager",
            "IT Director",
            "HR Director",
            "Security Manager",
            "Operations Lead",
            "Executive Team"
        ],
        "recommended_participants_count": 12
    }


def get_ransomware_template() -> Dict[str, Any]:
    """Ransomware Attack template"""
    return {
        "title": "Ransomware Attack on Critical Systems",
        "category": "cyber",
        "complexity": 5,
        "scenario_type": "functional",
        "description": "Sophisticated ransomware attack encrypting business-critical systems",
        "content": """
# Ransomware Attack Scenario

## Situation
At 02:30 AM, security systems detect widespread file encryption across the network. A ransomware
strain has compromised multiple systems. Attackers demand $2M Bitcoin payment within 72 hours or
threaten to release encrypted data publicly.

## Impact
- Critical systems encrypted
- Production halted
- Customer data potentially compromised
- Backup systems partially affected
- Legal and regulatory implications

## Your Challenge
Contain the attack, assess damage, restore systems from clean backups, manage law enforcement
coordination, and communicate with stakeholders while maintaining business operations.
        """,
        "timeline": [
            {"time": "02:30", "event": "Ransomware detected"},
            {"time": "03:00", "event": "Network isolation initiated"},
            {"time": "04:00", "event": "Incident response team assembled"},
            {"time": "08:00", "event": "Full scope assessment"},
            {"time": "12:00", "event": "Recovery plan finalized"},
            {"time": "Day 2", "event": "System restoration begins"},
            {"time": "Day 3-5", "event": "Full recovery and hardening"}
        ],
        "injects": [
            {
                "time": "06:00",
                "title": "Media Leak",
                "description": "Anonymous source tips off media about the attack",
                "requires_response": True
            },
            {
                "time": "Day 1 16:00",
                "title": "Backup Corruption",
                "description": "Some backup files found to be corrupted",
                "requires_response": True
            },
            {
                "time": "Day 2 10:00",
                "title": "Law Enforcement Request",
                "description": "FBI requests delay in system wipe for evidence collection",
                "requires_response": True
            }
        ],
        "success_metrics": {
            "containment_time": "< 4 hours",
            "recovery_time": "< 5 days",
            "data_loss": "< 24 hours",
            "zero_ransom_payment": True,
            "regulatory_compliance": "100%"
        },
        "participant_roles": [
            "BCM Coordinator",
            "CISO",
            "IT Director",
            "Legal Counsel",
            "Communications Director",
            "Law Enforcement Liaison",
            "Executive Leadership",
            "Forensics Team"
        ],
        "recommended_participants_count": 15
    }


def get_supply_chain_template() -> Dict[str, Any]:
    """Supply Chain Disruption template"""
    return {
        "title": "Supply Chain Disruption",
        "category": "supply_chain",
        "complexity": 3,
        "scenario_type": "tabletop",
        "description": "Critical supplier failure affecting production and delivery",
        "content": """
# Supply Chain Disruption Scenario

## Situation
Your primary component supplier announces immediate bankruptcy and ceases all operations. They
supply 60% of a critical component with no immediately available alternatives. Current inventory
will last 3-4 weeks.

## Impact
- Production slowdown imminent
- Customer deliveries at risk
- Revenue impact significant
- Alternative suppliers needed
- Contract obligations threatened

## Your Challenge
Identify and qualify alternative suppliers, manage existing inventory, communicate with customers,
renegotiate contracts, and maintain business relationships during the transition.
        """,
        "timeline": [
            {"time": "Day 0", "event": "Supplier bankruptcy announced"},
            {"time": "Day 1", "event": "Impact assessment completed"},
            {"time": "Day 3", "event": "Alternative suppliers identified"},
            {"time": "Week 2", "event": "Inventory depletion warning"},
            {"time": "Week 3", "event": "First alternative deliveries"},
            {"time": "Week 4", "event": "Production stabilization"},
            {"time": "Week 6", "event": "Full supply chain recovery"}
        ],
        "injects": [
            {
                "time": "Day 2",
                "title": "Major Customer Threat",
                "description": "Largest customer threatens to find new supplier",
                "requires_response": True
            },
            {
                "time": "Week 1",
                "title": "Quality Issues",
                "description": "Alternative supplier samples fail quality testing",
                "requires_response": True
            },
            {
                "time": "Week 3",
                "title": "Price Increase",
                "description": "Alternative suppliers demand 40% price increase",
                "requires_response": True
            }
        ],
        "success_metrics": {
            "customer_retention": "> 90%",
            "production_continuity": "> 75%",
            "cost_control": "< 25% increase",
            "supplier_qualification_time": "< 4 weeks"
        },
        "participant_roles": [
            "BCM Coordinator",
            "Procurement Manager",
            "Operations Director",
            "Quality Assurance Lead",
            "Customer Relations Manager",
            "Finance Director"
        ],
        "recommended_participants_count": 8
    }


def get_data_breach_template() -> Dict[str, Any]:
    """Data Breach template"""
    return {
        "title": "Data Breach and Customer Notification",
        "category": "data_breach",
        "complexity": 4,
        "scenario_type": "functional",
        "description": "Customer data breach requiring notification and regulatory response",
        "content": """
# Data Breach Scenario

## Situation
Security team discovers that an exposed API endpoint has been leaking customer personal information
(names, emails, phone numbers, partial payment data) for approximately 3 weeks. Estimated 50,000
customer records affected.

## Impact
- Customer trust damaged
- Regulatory notification required (GDPR, CCPA)
- Legal liability exposure
- Media attention likely
- Credit monitoring obligations

## Your Challenge
Contain the breach, assess full impact, notify affected customers, coordinate with regulators,
manage media response, and implement corrective actions to prevent recurrence.
        """,
        "timeline": [
            {"time": "Hour 0", "event": "Breach discovered"},
            {"time": "Hour 2", "event": "API endpoint secured"},
            {"time": "Hour 6", "event": "Full impact assessment"},
            {"time": "Day 1", "event": "Legal and regulatory consultation"},
            {"time": "Day 2", "event": "Customer notification plan finalized"},
            {"time": "Day 3", "event": "Regulatory notification submitted"},
            {"time": "Day 5", "event": "Customer notifications sent"},
            {"time": "Week 2", "event": "Credit monitoring established"}
        ],
        "injects": [
            {
                "time": "Day 1 14:00",
                "title": "Activist Group",
                "description": "Privacy advocacy group demands immediate public disclosure",
                "requires_response": True
            },
            {
                "time": "Day 3 09:00",
                "title": "Regulator Questions",
                "description": "Data protection authority requests detailed incident report",
                "requires_response": True
            },
            {
                "time": "Day 4 16:00",
                "title": "Class Action",
                "description": "Law firm announces class action lawsuit investigation",
                "requires_response": True
            }
        ],
        "success_metrics": {
            "regulatory_compliance": "100%",
            "notification_timeliness": "< 72 hours",
            "customer_communication_effectiveness": "> 80%",
            "remediation_completion": "< 30 days"
        },
        "participant_roles": [
            "BCM Coordinator",
            "CISO",
            "Legal Counsel",
            "Privacy Officer",
            "Communications Director",
            "Customer Service Lead",
            "Executive Leadership"
        ],
        "recommended_participants_count": 10
    }
