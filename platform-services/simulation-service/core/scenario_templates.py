"""
BCM Scenario Templates
======================

Pre-built scenario templates for common BCM exercises.

Includes:
- Cyber Attack Response
- Supply Chain Disruption
- Natural Disaster Response

Adapted from: /simulation/sim_adapter.py sample scenarios
"""

from typing import List, Dict, Any
from enum import Enum


class ScenarioComplexity(str, Enum):
    """Scenario complexity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ScenarioTemplate:
    """Pre-built BCM scenario template"""

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        complexity: ScenarioComplexity,
        duration_minutes: int,
        objectives: List[str],
        affected_processes: List[str],
        required_roles: List[str],
        injects: List[Dict[str, Any]],
        iso_requirements: List[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.complexity = complexity
        self.duration_minutes = duration_minutes
        self.objectives = objectives
        self.affected_processes = affected_processes
        self.required_roles = required_roles
        self.injects = injects
        self.iso_requirements = iso_requirements or ["ISO 22301:2019"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "complexity": self.complexity,
            "duration_minutes": self.duration_minutes,
            "objectives": self.objectives,
            "affected_processes": self.affected_processes,
            "required_roles": self.required_roles,
            "injects": self.injects,
            "iso_requirements": self.iso_requirements
        }


# ============================================================================
# Pre-built Scenario Templates
# ============================================================================

CYBER_ATTACK_SCENARIO = ScenarioTemplate(
    id="TEMPLATE-001",
    name="Cyber Attack Response Exercise",
    description=(
        "Ransomware attack on critical systems. Tests organization's ability "
        "to detect, respond to, and recover from a cyber security incident "
        "targeting critical business systems and data."
    ),
    complexity=ScenarioComplexity.HIGH,
    duration_minutes=180,  # 3 hours
    objectives=[
        "Activate Incident Response Team within 15 minutes",
        "Isolate affected systems to prevent spread",
        "Communicate with internal and external stakeholders",
        "Implement emergency recovery procedures",
        "Assess business impact and prioritize recovery",
        "Document incident for post-incident review"
    ],
    affected_processes=[
        "IT Services",
        "Operations",
        "Customer Service",
        "Finance",
        "Communications"
    ],
    required_roles=[
        "IT Manager",
        "Chief Information Security Officer (CISO)",
        "Communications Lead",
        "Crisis Management Team Lead",
        "Legal Counsel",
        "Business Continuity Manager"
    ],
    injects=[
        {
            "sequence": 1,
            "title": "Initial Security Alert",
            "description": (
                "Security monitoring team detects unusual network activity. "
                "Multiple systems showing signs of encryption. "
                "Antivirus alerts being triggered across the organization."
            ),
            "trigger_time": 0,  # Start of exercise
            "expected_response": "Activate incident response procedures and notify CISO",
            "evaluation_criteria": [
                "Response time under 15 minutes",
                "Proper escalation to CISO",
                "Initial containment actions initiated"
            ],
            "event_type": "detection"
        },
        {
            "sequence": 2,
            "title": "Scope Expansion - Multiple Systems Compromised",
            "description": (
                "Investigation reveals ransomware has spread to: "
                "- File servers (80% encrypted) "
                "- Email systems (offline) "
                "- ERP system (partially affected) "
                "Ransom note demands $500,000 in cryptocurrency."
            ),
            "trigger_time": 30,  # 30 minutes in
            "expected_response": "Escalate to crisis management team, isolate systems, activate DR plan",
            "evaluation_criteria": [
                "Crisis team activated within 10 minutes",
                "Network segmentation implemented",
                "Backup systems assessed"
            ],
            "event_type": "escalation"
        },
        {
            "sequence": 3,
            "title": "Stakeholder Pressure - Customer Inquiries",
            "description": (
                "Customer service receiving numerous calls about service unavailability. "
                "Social media reports of issues spreading. "
                "Key clients requesting status updates."
            ),
            "trigger_time": 60,  # 1 hour in
            "expected_response": "Activate crisis communication plan, prepare public statement",
            "evaluation_criteria": [
                "Communication plan activated",
                "Consistent messaging to stakeholders",
                "Customer service script deployed"
            ],
            "event_type": "communication"
        },
        {
            "sequence": 4,
            "title": "Recovery Decision Point",
            "description": (
                "IT team confirms clean backups available from 12 hours ago. "
                "Estimated recovery time: 24-48 hours. "
                "Alternative: Pay ransom (no guarantee of recovery). "
                "Management decision required."
            ),
            "trigger_time": 90,  # 1.5 hours in
            "expected_response": "Crisis team makes recovery decision, initiates chosen path",
            "evaluation_criteria": [
                "Decision documented with rationale",
                "Recovery timeline communicated",
                "Resources mobilized"
            ],
            "event_type": "decision"
        },
        {
            "sequence": 5,
            "title": "Media Contact",
            "description": (
                "Local news outlet contacts organization requesting statement "
                "about 'reported cyber attack and data breach'. "
                "Reporter has deadline in 2 hours."
            ),
            "trigger_time": 120,  # 2 hours in
            "expected_response": "Communications team prepares approved statement, coordinates with legal",
            "evaluation_criteria": [
                "Statement reviewed by legal",
                "Consistent with internal messaging",
                "Timely response provided"
            ],
            "event_type": "communication"
        }
    ],
    iso_requirements=[
        "ISO 22301:2019 - Clause 8.4 (Incident Response)",
        "ISO 27001:2013 - A.16 (Information Security Incident Management)",
        "ISO 22301:2019 - Clause 8.3 (Business Continuity Procedures)"
    ]
)


SUPPLY_CHAIN_SCENARIO = ScenarioTemplate(
    id="TEMPLATE-002",
    name="Supply Chain Disruption Exercise",
    description=(
        "Key supplier unable to deliver critical components due to factory fire. "
        "Tests organization's ability to manage supply chain disruptions and "
        "activate alternate supplier arrangements."
    ),
    complexity=ScenarioComplexity.MEDIUM,
    duration_minutes=120,  # 2 hours
    objectives=[
        "Assess impact on production schedule",
        "Activate alternate supplier protocols",
        "Communicate with customers about potential delays",
        "Implement mitigation strategies to minimize disruption",
        "Coordinate with procurement and operations teams"
    ],
    affected_processes=[
        "Manufacturing",
        "Procurement",
        "Supply Chain Management",
        "Customer Service",
        "Quality Assurance"
    ],
    required_roles=[
        "Operations Manager",
        "Procurement Lead",
        "Customer Service Manager",
        "Supply Chain Director",
        "Quality Manager"
    ],
    injects=[
        {
            "sequence": 1,
            "title": "Supplier Notification",
            "description": (
                "Email received from critical supplier: "
                "'Factory fire last night. Facility offline for minimum 4 weeks. "
                "Cannot fulfill pending orders. Alternative arrangements urgently needed.'"
            ),
            "trigger_time": 0,
            "expected_response": "Assess current inventory, identify alternate suppliers",
            "evaluation_criteria": [
                "Inventory assessment completed within 30 minutes",
                "Alternate suppliers identified",
                "Impact analysis initiated"
            ],
            "event_type": "notification"
        },
        {
            "sequence": 2,
            "title": "Production Impact Assessment",
            "description": (
                "Manufacturing reports: "
                "- Current inventory sufficient for 5 days production "
                "- 3 major customer orders at risk (delivery due in 10 days) "
                "- Estimated revenue impact: $2M if orders delayed"
            ),
            "trigger_time": 30,
            "expected_response": "Activate business continuity plan, contact alternate suppliers",
            "evaluation_criteria": [
                "BC plan activated",
                "Alternate suppliers contacted",
                "Customer notification plan prepared"
            ],
            "event_type": "assessment"
        },
        {
            "sequence": 3,
            "title": "Customer Communication Required",
            "description": (
                "Three major customers contact sales team requesting order status. "
                "One customer threatens to cancel if delays occur. "
                "Decision needed on customer communications."
            ),
            "trigger_time": 60,
            "expected_response": "Customer communication plan executed, honest updates provided",
            "evaluation_criteria": [
                "Timely customer communication",
                "Transparent about situation",
                "Options presented to customers"
            ],
            "event_type": "communication"
        },
        {
            "sequence": 4,
            "title": "Alternate Supplier Quote Received",
            "description": (
                "Alternate supplier responds: "
                "- Can supply needed components "
                "- 30% higher cost than current supplier "
                "- 2-week lead time "
                "- Minimum order quantity applies "
                "Decision needed on acceptance."
            ),
            "trigger_time": 90,
            "expected_response": "Evaluate financial impact, make supplier decision",
            "evaluation_criteria": [
                "Financial analysis completed",
                "Decision documented",
                "Purchase order issued if approved"
            ],
            "event_type": "decision"
        }
    ],
    iso_requirements=[
        "ISO 22301:2019 - Clause 8.3 (Business Continuity Procedures)",
        "ISO 22301:2019 - Clause 8.4 (Communication)"
    ]
)


NATURAL_DISASTER_SCENARIO = ScenarioTemplate(
    id="TEMPLATE-003",
    name="Natural Disaster Response Exercise",
    description=(
        "Major earthquake damages primary facility. Tests organization's ability "
        "to ensure personnel safety, assess damage, activate alternate site, "
        "and resume critical operations."
    ),
    complexity=ScenarioComplexity.CRITICAL,
    duration_minutes=240,  # 4 hours
    objectives=[
        "Ensure safety of all personnel",
        "Conduct facility damage assessment",
        "Activate alternate site operations",
        "Resume critical business functions",
        "Communicate with stakeholders and authorities",
        "Implement emergency response procedures"
    ],
    affected_processes=[
        "All Operations",
        "Facilities Management",
        "Human Resources",
        "IT Infrastructure",
        "Safety & Security",
        "Communications"
    ],
    required_roles=[
        "Crisis Manager",
        "Facilities Manager",
        "HR Director",
        "Safety Officer",
        "IT Manager",
        "Communications Director",
        "Business Continuity Manager"
    ],
    injects=[
        {
            "sequence": 1,
            "title": "Earthquake Strike - Magnitude 6.8",
            "description": (
                "Major earthquake strikes at 2:45 PM during business hours. "
                "Building shaking stops after 45 seconds. "
                "Fire alarms activated. Power flickering. "
                "Staff reporting to designated assembly areas."
            ),
            "trigger_time": 0,
            "expected_response": "Activate emergency response, account for personnel, assess safety",
            "evaluation_criteria": [
                "Emergency procedures activated immediately",
                "Personnel accountability process started",
                "Initial safety assessment conducted"
            ],
            "event_type": "emergency"
        },
        {
            "sequence": 2,
            "title": "Initial Damage Report",
            "description": (
                "Facility team reports: "
                "- Structural cracks in main building "
                "- Water main break in basement "
                "- Partial roof collapse in warehouse "
                "- Power and network infrastructure damaged "
                "- Building declared unsafe for re-entry "
                "All personnel confirmed safe, 3 minor injuries."
            ),
            "trigger_time": 30,
            "expected_response": "Activate business continuity plan, prepare alternate site",
            "evaluation_criteria": [
                "BC plan activated within 15 minutes",
                "Alternate site notification sent",
                "Critical function priorities identified"
            ],
            "event_type": "assessment"
        },
        {
            "sequence": 3,
            "title": "Critical Systems Offline",
            "description": (
                "IT reports: "
                "- Primary data center offline "
                "- DR site operational but requires manual failover "
                "- Estimated 4-6 hours to restore systems "
                "- Critical customer-facing systems down "
                "- Backup systems available at alternate location"
            ),
            "trigger_time": 60,
            "expected_response": "Initiate IT disaster recovery, failover to alternate systems",
            "evaluation_criteria": [
                "DR procedures initiated",
                "Failover decision made",
                "Recovery timeline communicated"
            ],
            "event_type": "technical"
        },
        {
            "sequence": 4,
            "title": "Stakeholder Communication Crisis",
            "description": (
                "Multiple urgent communications required: "
                "- Customers unable to access services "
                "- Employees awaiting instructions "
                "- Media requesting information "
                "- Regulators requiring compliance reports "
                "- Investors concerned about business impact"
            ),
            "trigger_time": 90,
            "expected_response": "Activate crisis communication plan, coordinate messaging",
            "evaluation_criteria": [
                "Communication plan activated",
                "Consistent messaging across channels",
                "Priority stakeholders contacted"
            ],
            "event_type": "communication"
        },
        {
            "sequence": 5,
            "title": "Alternate Site Activation",
            "description": (
                "Alternate site ready for operations: "
                "- 40% of normal capacity available "
                "- Key staff can work remotely "
                "- Critical systems online at DR site "
                "- Decision needed on which functions to prioritize "
                "- Transportation and logistics to be arranged"
            ),
            "trigger_time": 120,
            "expected_response": "Prioritize critical functions, deploy resources to alternate site",
            "evaluation_criteria": [
                "Critical functions prioritized correctly",
                "Resource deployment coordinated",
                "Timeline for resumption communicated"
            ],
            "event_type": "recovery"
        },
        {
            "sequence": 6,
            "title": "Long-term Recovery Planning",
            "description": (
                "Initial assessments complete: "
                "- Primary facility requires 6-12 months to repair "
                "- Insurance assessor scheduled for next week "
                "- Alternate site can support operations for 3 months "
                "- Long-term facility solution needed "
                "- Board of Directors requesting briefing"
            ),
            "trigger_time": 180,
            "expected_response": "Develop long-term recovery plan, prepare executive briefing",
            "evaluation_criteria": [
                "Recovery plan developed",
                "Executive briefing prepared",
                "Long-term options identified"
            ],
            "event_type": "planning"
        }
    ],
    iso_requirements=[
        "ISO 22301:2019 - Clause 8.3 (Business Continuity Procedures)",
        "ISO 22301:2019 - Clause 8.4 (Incident Response)",
        "ISO 22301:2019 - Clause 8.5 (Communication)",
        "ISO 45001:2018 - Emergency Preparedness and Response"
    ]
)


# ============================================================================
# Template Registry
# ============================================================================

SCENARIO_TEMPLATES = {
    "cyber_attack": CYBER_ATTACK_SCENARIO,
    "supply_chain": SUPPLY_CHAIN_SCENARIO,
    "natural_disaster": NATURAL_DISASTER_SCENARIO
}


def get_template(template_id: str) -> ScenarioTemplate:
    """Get scenario template by ID"""
    if template_id in SCENARIO_TEMPLATES:
        return SCENARIO_TEMPLATES[template_id]
    raise ValueError(f"Template not found: {template_id}")


def list_templates() -> List[Dict[str, Any]]:
    """List all available scenario templates"""
    return [
        {
            "id": key,
            "name": template.name,
            "description": template.description,
            "complexity": template.complexity,
            "duration_minutes": template.duration_minutes,
            "objectives_count": len(template.objectives),
            "injects_count": len(template.injects)
        }
        for key, template in SCENARIO_TEMPLATES.items()
    ]


def get_template_details(template_id: str) -> Dict[str, Any]:
    """Get full template details"""
    template = get_template(template_id)
    return template.to_dict()
