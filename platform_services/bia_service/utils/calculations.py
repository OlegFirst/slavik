"""
BIA Service - Calculation Utilities

Helper functions for BIA calculations.
Copied from original main.py without any loss of functionality.
"""

from typing import Dict, Optional
from ..models.enums import CriticalityLevel, WHOTier, PatientSafetyImpact


def calculate_criticality_score(criticality: CriticalityLevel) -> int:
    """
    Convert criticality enum to numeric score 1-5.

    Args:
        criticality: CriticalityLevel enum value

    Returns:
        int: Score from 1 (LOW) to 5 (CRITICAL)
    """
    mapping = {
        CriticalityLevel.LOW: 1,
        CriticalityLevel.MINOR: 2,
        CriticalityLevel.MODERATE: 3,
        CriticalityLevel.HIGH: 4,
        CriticalityLevel.CRITICAL: 5
    }
    return mapping.get(criticality, 3)


def calculate_financial_impact_timeline(
    annual_revenue_impact: float,
    rto_hours: int
) -> Dict[str, float]:
    """
    Calculate financial impact at different time intervals.

    Args:
        annual_revenue_impact: Annual revenue affected by this process
        rto_hours: Recovery Time Objective in hours

    Returns:
        dict: Financial impact per time period
            {
                "1_hour": 5000.0,
                "4_hours": 20000.0,
                "8_hours": 40000.0,
                "24_hours": 120000.0,
                "3_days": 360000.0,
                "1_week": 840000.0,
                "1_month": 3600000.0
            }
    """
    hourly_rate = annual_revenue_impact / (365 * 24) if annual_revenue_impact > 0 else 0

    return {
        "1_hour": hourly_rate,
        "4_hours": hourly_rate * 4,
        "8_hours": hourly_rate * 8,
        "24_hours": hourly_rate * 24,
        "3_days": hourly_rate * 72,
        "1_week": hourly_rate * 168,
        "1_month": hourly_rate * 720
    }


def determine_who_tier(
    criticality: CriticalityLevel,
    rto_hours: int,
    patient_safety_impact: Optional[PatientSafetyImpact]
) -> WHOTier:
    """
    Determine WHO Essential Services Tier for healthcare processes.

    Based on WHO guidelines for essential healthcare services classification.

    Args:
        criticality: Process criticality level
        rto_hours: Recovery Time Objective in hours
        patient_safety_impact: Patient safety impact level (if applicable)

    Returns:
        WHOTier: WHO tier classification
            - TIER_1: IMMEDIATE (RTO: 0 minutes) - Life-threatening
            - TIER_2: URGENT (RTO: 2-4 hours) - Critical processes
            - TIER_3: IMPORTANT (RTO: 24 hours) - High/Moderate processes
            - TIER_4: NORMAL (RTO: 3-5 days) - Standard processes
    """
    if patient_safety_impact == PatientSafetyImpact.LIFE_THREATENING or rto_hours == 0:
        return WHOTier.TIER_1  # IMMEDIATE

    elif criticality == CriticalityLevel.CRITICAL or rto_hours <= 4:
        return WHOTier.TIER_2  # URGENT

    elif criticality in [CriticalityLevel.HIGH, CriticalityLevel.MODERATE] or rto_hours <= 24:
        return WHOTier.TIER_3  # IMPORTANT

    else:
        return WHOTier.TIER_4  # NORMAL
