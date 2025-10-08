"""
Sample Test Data - Realistic fixtures for testing
Provides real-world data for all test scenarios
"""
import pytest
from datetime import datetime, timedelta


# ============================================================================
# ORGANIZATIONS
# ============================================================================

@pytest.fixture
def healthcare_organization():
    """Large healthcare organization"""
    return {
        "id": "org-healthcare-001",
        "name": "City General Hospital",
        "industry": "healthcare",
        "size": "500-1000",
        "location": {
            "country": "USA",
            "state": "California",
            "city": "San Francisco",
            "address": "123 Medical Center Dr"
        },
        "established": "1985-03-15",
        "annual_revenue": "$250M",
        "employees": 850,
        "iso_certified": ["ISO 9001", "ISO 27001"],
        "compliance_requirements": ["HIPAA", "HITECH", "ISO 22301"],
        "contact": {
            "bcm_officer": "Dr. Sarah Johnson",
            "email": "bcm@citygeneralhospital.com",
            "phone": "+1-415-555-0100"
        }
    }


@pytest.fixture
def financial_organization():
    """Financial services company"""
    return {
        "id": "org-finance-001",
        "name": "SecureBank Financial Services",
        "industry": "finance",
        "size": "1000+",
        "location": {
            "country": "USA",
            "state": "New York",
            "city": "New York",
            "address": "456 Wall Street"
        },
        "established": "1995-06-01",
        "annual_revenue": "$2.5B",
        "employees": 2500,
        "iso_certified": ["ISO 22301", "ISO 27001", "ISO 27017"],
        "compliance_requirements": ["PCI-DSS", "SOX", "GDPR", "GLBA"],
        "contact": {
            "ciso": "Michael Chen",
            "email": "security@securebank.com",
            "phone": "+1-212-555-0200"
        }
    }


# ============================================================================
# BUSINESS PROCESSES
# ============================================================================

@pytest.fixture
def critical_healthcare_processes():
    """Critical processes for healthcare organization"""
    return [
        {
            "id": "proc-001",
            "name": "Emergency Room Operations",
            "description": "24/7 emergency patient care and triage",
            "department": "Emergency Medicine",
            "owner": "Dr. Emily Rodriguez",
            "criticality": "critical",
            "rto_target": "1h",
            "rpo_target": "15m",
            "mtpd": "4h",
            "annual_loss_exposure": "$5M",
            "dependencies": [
                {
                    "name": "Electronic Health Records (EHR)",
                    "type": "it_system",
                    "criticality": "high"
                },
                {
                    "name": "Lab Information System",
                    "type": "it_system",
                    "criticality": "high"
                },
                {
                    "name": "Radiology PACS",
                    "type": "it_system",
                    "criticality": "medium"
                },
                {
                    "name": "Emergency Response Team",
                    "type": "personnel",
                    "count": 15
                }
            ],
            "resources": [
                {"type": "staff", "role": "ER Physicians", "count": 8},
                {"type": "staff", "role": "ER Nurses", "count": 25},
                {"type": "equipment", "critical": ["MRI", "CT Scanner", "X-Ray"]},
                {"type": "supplies", "critical": ["Medications", "Sterile Equipment"]}
            ],
            "recovery_strategies": [
                "Redundant EHR system in DR site",
                "Paper-based backup procedures",
                "Satellite ER clinic activation"
            ]
        },
        {
            "id": "proc-002",
            "name": "Patient Registration and Admission",
            "description": "Patient intake and administrative processing",
            "department": "Administration",
            "owner": "Jane Smith",
            "criticality": "high",
            "rto_target": "4h",
            "rpo_target": "1h",
            "mtpd": "24h",
            "annual_loss_exposure": "$1M",
            "dependencies": [
                {"name": "EHR System", "type": "it_system", "criticality": "high"},
                {"name": "Insurance Verification System", "type": "it_system", "criticality": "medium"},
                {"name": "Patient Portal", "type": "it_system", "criticality": "low"}
            ],
            "resources": [
                {"type": "staff", "role": "Registrars", "count": 12},
                {"type": "staff", "role": "Admissions Coordinators", "count": 6}
            ]
        },
        {
            "id": "proc-003",
            "name": "Laboratory Services",
            "description": "Diagnostic testing and analysis",
            "department": "Laboratory",
            "owner": "Dr. Robert Lee",
            "criticality": "high",
            "rto_target": "2h",
            "rpo_target": "30m",
            "mtpd": "8h",
            "annual_loss_exposure": "$2M",
            "dependencies": [
                {"name": "Lab Information System (LIS)", "type": "it_system"},
                {"name": "Lab Equipment", "type": "equipment"},
                {"name": "Reagent Supply Chain", "type": "supplier"}
            ]
        }
    ]


@pytest.fixture
def banking_processes():
    """Critical banking processes"""
    return [
        {
            "id": "proc-bank-001",
            "name": "Online Banking Platform",
            "criticality": "critical",
            "rto_target": "15m",
            "rpo_target": "0m",
            "transactions_per_day": 500000,
            "revenue_per_hour": "$250K"
        },
        {
            "id": "proc-bank-002",
            "name": "ATM Network",
            "criticality": "high",
            "rto_target": "1h",
            "rpo_target": "5m",
            "atm_count": 500
        }
    ]


# ============================================================================
# THREATS & RISKS
# ============================================================================

@pytest.fixture
def cyber_threats():
    """Common cyber security threats"""
    return [
        {
            "id": "threat-001",
            "name": "Ransomware Attack",
            "category": "cyber",
            "description": "Malware encrypts critical data and systems",
            "likelihood": "medium",
            "likelihood_score": 3,
            "impact": "critical",
            "impact_score": 5,
            "risk_score": 15,
            "threat_actors": ["Organized Crime", "Nation State"],
            "attack_vectors": [
                "Phishing emails",
                "Unpatched vulnerabilities",
                "RDP exploitation"
            ],
            "affected_assets": [
                "Patient database",
                "EHR system",
                "File servers",
                "Backup systems"
            ],
            "mitigation_strategies": [
                "Regular backups (3-2-1 rule)",
                "EDR deployment",
                "Security awareness training",
                "Network segmentation",
                "Patch management"
            ],
            "estimated_loss": "$5M-$15M"
        },
        {
            "id": "threat-002",
            "name": "Data Center Failure",
            "category": "infrastructure",
            "description": "Complete failure of primary data center",
            "likelihood": "low",
            "likelihood_score": 2,
            "impact": "critical",
            "impact_score": 5,
            "risk_score": 10,
            "causes": [
                "Natural disaster (earthquake, flood)",
                "Fire",
                "Power outage",
                "HVAC failure"
            ],
            "affected_systems": [
                "All IT systems",
                "EHR",
                "Lab systems",
                "Communication"
            ],
            "mitigation_strategies": [
                "Geographic redundancy",
                "Hot DR site",
                "Regular DR drills",
                "Cloud backup"
            ]
        },
        {
            "id": "threat-003",
            "name": "Supply Chain Disruption",
            "category": "operational",
            "description": "Critical supplier unable to deliver",
            "likelihood": "medium",
            "impact": "high",
            "risk_score": 12,
            "examples": [
                "Medical supplies shortage",
                "Pharmaceutical delays",
                "Equipment vendor bankruptcy"
            ]
        }
    ]


# ============================================================================
# BIA WORKFLOW DATA
# ============================================================================

@pytest.fixture
def bia_workflow_input():
    """Complete BIA workflow input data"""
    return {
        "tenant_id": "tenant-healthcare-001",
        "organization_id": "org-healthcare-001",
        "analysis_id": "bia-2024-q1",
        "analysis_type": "full_bia",
        "scope": {
            "departments": ["Emergency", "Laboratory", "Administration", "ICU"],
            "locations": ["Main Campus", "Satellite Clinic A"],
            "timeframe": "2024-Q1"
        },
        "objectives": [
            "Identify critical business processes",
            "Determine RTOs and RPOs",
            "Assess impact of disruptions",
            "Prioritize recovery strategies"
        ],
        "stakeholders": [
            {"name": "Dr. Sarah Johnson", "role": "BCM Officer"},
            {"name": "Michael Brown", "role": "CIO"},
            {"name": "Lisa Anderson", "role": "CFO"}
        ],
        "methodology": "ISO 22301 compliant",
        "previous_bia": {
            "date": "2023-Q1",
            "findings": 25,
            "critical_processes": 8
        }
    }


@pytest.fixture
def bia_expected_output():
    """Expected BIA analysis output"""
    return {
        "analysis_id": "bia-2024-q1",
        "completion_date": datetime.now().isoformat(),
        "processes_analyzed": 25,
        "critical_processes": 8,
        "high_priority_processes": 12,
        "medium_priority_processes": 5,
        "processes": [
            {
                "name": "Emergency Room Operations",
                "criticality": "critical",
                "recommended_rto": "1h",
                "recommended_rpo": "15m",
                "mtpd": "4h",
                "financial_impact_per_hour": "$125K",
                "regulatory_impact": "HIPAA violation risk",
                "reputational_impact": "High"
            }
        ],
        "recommendations": [
            "Implement hot DR site for critical systems",
            "Establish redundant EHR system",
            "Create manual backup procedures for ER",
            "Conduct quarterly DR drills"
        ],
        "total_risk_exposure": "$25M annually",
        "compliance_gaps": [
            "ISO 22301 Clause 8.2.3: Incomplete dependency mapping",
            "HIPAA: Insufficient backup procedures"
        ]
    }


# ============================================================================
# RISK ASSESSMENT DATA
# ============================================================================

@pytest.fixture
def risk_assessment_input():
    """Risk assessment workflow input"""
    return {
        "tenant_id": "tenant-healthcare-001",
        "organization_id": "org-healthcare-001",
        "assessment_id": "risk-2024-q1",
        "scope": "it_infrastructure_and_cyber",
        "methodology": "FAIR + ISO 27005",
        "assets": [
            {
                "id": "asset-001",
                "name": "Patient Database",
                "type": "data",
                "classification": "highly_confidential",
                "value": "$10M",
                "records": 500000
            },
            {
                "id": "asset-002",
                "name": "EHR System",
                "type": "application",
                "criticality": "critical",
                "users": 850
            }
        ],
        "threat_scenarios": [
            "Ransomware attack on EHR",
            "Data breach of patient records",
            "DDoS attack on online systems",
            "Insider threat - data theft"
        ]
    }


# ============================================================================
# INCIDENT RESPONSE DATA
# ============================================================================

@pytest.fixture
def incident_data():
    """Sample incident data"""
    return {
        "incident_id": "INC-2024-001",
        "title": "Ransomware Attack on File Server",
        "severity": "critical",
        "status": "active",
        "detected_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "reported_by": "Security Operations Center",
        "affected_systems": [
            "File Server FS-01",
            "Backup Server BK-02",
            "50 user workstations"
        ],
        "symptoms": [
            "Files encrypted with .locked extension",
            "Ransom note displayed on screens",
            "Backup systems inaccessible"
        ],
        "initial_response": [
            "Isolated affected systems from network",
            "Activated incident response team",
            "Notified senior management"
        ],
        "estimated_impact": {
            "financial": "$500K-$2M",
            "downtime": "4-24 hours",
            "data_loss": "Minimal (last backup 2h ago)"
        }
    }


# ============================================================================
# MOCK LLM RESPONSES
# ============================================================================

@pytest.fixture
def mock_llm_bia_response():
    """Realistic LLM response for BIA process identification"""
    return {
        "response": {
            "processes_identified": 25,
            "critical_processes": 8,
            "analysis": {
                "executive_summary": "Identified 25 business processes across 4 departments. 8 processes classified as critical with RTO < 4h.",
                "processes": [
                    {
                        "name": "Emergency Room Operations",
                        "criticality": "critical",
                        "justification": "Life-critical patient care, 24/7 operation, regulatory requirement for continuous service",
                        "recommended_rto": "1 hour",
                        "recommended_rpo": "15 minutes",
                        "mtpd": "4 hours",
                        "dependencies": ["EHR", "Lab", "Radiology", "Pharmacy"],
                        "recovery_strategies": [
                            "Implement redundant EHR system with hot failover",
                            "Maintain paper-based backup procedures",
                            "Establish alternate care site capability"
                        ]
                    }
                ],
                "recommendations": [
                    "Priority 1: Implement DR site for critical systems (EHR, Lab)",
                    "Priority 2: Develop and test manual workaround procedures",
                    "Priority 3: Conduct quarterly business continuity drills"
                ]
            }
        },
        "metadata": {
            "model": "claude-3-opus",
            "tokens": 2500,
            "confidence": 0.95
        }
    }


@pytest.fixture
def mock_llm_risk_response():
    """Realistic LLM response for risk assessment"""
    return {
        "response": {
            "threats_analyzed": 15,
            "high_risk_scenarios": 5,
            "analysis": {
                "top_threats": [
                    {
                        "threat": "Ransomware Attack",
                        "likelihood": "Medium (30%)",
                        "impact": "Critical",
                        "fair_analysis": {
                            "loss_event_frequency": 0.3,
                            "probable_loss_magnitude": "$5M-$15M",
                            "annual_loss_expectancy": "$3M"
                        },
                        "mitigations": [
                            "Implement EDR on all endpoints",
                            "Deploy email security gateway",
                            "Conduct security awareness training quarterly"
                        ],
                        "residual_risk": "Low (after mitigations)"
                    }
                ],
                "recommendations": [
                    "Immediate: Deploy EDR solution ($200K investment)",
                    "Short-term: Implement 3-2-1 backup strategy",
                    "Long-term: Establish SOC capability"
                ]
            }
        }
    }


# ============================================================================
# VALIDATION SCHEMAS
# ============================================================================

@pytest.fixture
def expected_bia_output_schema():
    """JSON schema for BIA output validation"""
    return {
        "type": "object",
        "required": ["analysis_id", "processes_analyzed", "critical_processes"],
        "properties": {
            "analysis_id": {"type": "string"},
            "processes_analyzed": {"type": "integer", "minimum": 1},
            "critical_processes": {"type": "integer", "minimum": 0},
            "processes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "criticality", "recommended_rto"],
                    "properties": {
                        "name": {"type": "string"},
                        "criticality": {"enum": ["critical", "high", "medium", "low"]},
                        "recommended_rto": {"type": "string"}
                    }
                }
            }
        }
    }
