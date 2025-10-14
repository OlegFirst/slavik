"""
BIA Service - Enums

All enum definitions for Business Impact Analysis.
Copied from original main.py without any loss of functionality.
"""

from enum import Enum


class CriticalityLevel(str, Enum):
    """Process criticality levels based on downtime tolerance"""
    LOW = "low"           # 1 - Can stop for weeks
    MINOR = "minor"       # 2 - Can stop for 3-7 days
    MODERATE = "moderate" # 3 - Can stop for 24-72 hours
    HIGH = "high"         # 4 - Can stop for 4-24 hours
    CRITICAL = "critical" # 5 - Cannot stop > 4 hours


class ProcessStatus(str, Enum):
    """BIA process completion status"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ReputationalImpact(str, Enum):
    """Reputational impact levels"""
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CATASTROPHIC = "catastrophic"


class RegulatoryImpact(str, Enum):
    """Regulatory/compliance impact levels"""
    NO_VIOLATIONS = "no_violations"
    MINOR_VIOLATIONS = "minor_violations"
    MAJOR_VIOLATIONS = "major_violations"
    LICENSE_AT_RISK = "license_at_risk"
    CRIMINAL_LIABILITY = "criminal_liability"


class PatientSafetyImpact(str, Enum):
    """Patient safety impact (healthcare-specific)"""
    NO_IMPACT = "no_impact"
    DELAYED_CARE = "delayed_care"
    COMPROMISED_QUALITY = "compromised_quality"
    PATIENT_HARM_PROBABLE = "patient_harm_probable"
    LIFE_THREATENING = "life_threatening"


class WHOTier(str, Enum):
    """WHO Essential Services Tiers (healthcare)"""
    TIER_1 = "tier_1"  # IMMEDIATE - RTO: 0 minutes
    TIER_2 = "tier_2"  # URGENT - RTO: 2-4 hours
    TIER_3 = "tier_3"  # IMPORTANT - RTO: 24 hours
    TIER_4 = "tier_4"  # NORMAL - RTO: 3-5 days


class GeographicalScope(str, Enum):
    """Geographical scope of process impact"""
    LOCAL = "local"
    REGIONAL = "regional"
    NATIONAL = "national"
    GLOBAL = "global"


class IndustryType(str, Enum):
    """Industry type for process context"""
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    IT = "it"
    ENERGY = "energy"
    TRANSPORT = "transport"
    GOVERNMENT = "government"
    EDUCATION = "education"
    OTHER = "other"
