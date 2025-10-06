"""
Knowledge Base API - ISO 22301, BCI GPG, WHO Standards

Provides access to:
- ISO 22301:2019 clauses breakdown
- BCI GPG 6 Professional Practices
- WHO Health Emergency BCM
- ISO ↔ BCI ↔ Platform mapping
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
import json
import os
from pathlib import Path

router = APIRouter()

# Path to knowledge base
KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent / "knowledge" / "standards"


@router.get("/standards")
async def list_standards():
    """
    List all available standards in knowledge base

    Returns:
    - ISO 22301:2019
    - BCI GPG 7.0
    - WHO Health Emergency BCM
    """
    return {
        "standards": [
            {
                "id": "iso_22301",
                "name": "ISO 22301:2019",
                "title": "Business Continuity Management Systems",
                "version": "2019",
                "type": "international_standard",
                "clauses": "4-10",
                "endpoint": "/api/compliance/knowledge/iso22301"
            },
            {
                "id": "bci_gpg",
                "name": "BCI Good Practice Guidelines",
                "title": "Professional Practices for BCM",
                "version": "7.0",
                "type": "best_practices",
                "practices": "6 Professional Practices",
                "endpoint": "/api/compliance/knowledge/bci"
            },
            {
                "id": "who_bcm",
                "name": "WHO Health Emergency BCM",
                "title": "Healthcare Business Continuity",
                "version": "2018",
                "type": "sector_specific",
                "focus": "Healthcare & NPO",
                "endpoint": "/api/compliance/knowledge/who"
            }
        ],
        "total": 3
    }


@router.get("/iso22301/clauses")
async def get_iso22301_clauses():
    """
    Get all ISO 22301:2019 clauses

    Returns complete breakdown of clauses 4-10
    """
    try:
        clause_file = KNOWLEDGE_BASE_PATH / "ISO_22301" / "clauses_breakdown.md"

        if not clause_file.exists():
            raise HTTPException(status_code=404, detail="ISO 22301 clauses file not found")

        # Read the markdown file
        content = clause_file.read_text(encoding='utf-8')

        # Parse clauses (simplified - in production would use proper markdown parser)
        clauses = {
            "4": {
                "title": "Context of the Organization",
                "sub_clauses": ["4.1", "4.2", "4.3", "4.4"],
                "description": "Understanding organization context and stakeholders"
            },
            "5": {
                "title": "Leadership",
                "sub_clauses": ["5.1", "5.2", "5.3", "5.4"],
                "description": "Leadership commitment and policy"
            },
            "6": {
                "title": "Planning",
                "sub_clauses": ["6.1", "6.2"],
                "description": "Risk assessment and BC objectives"
            },
            "7": {
                "title": "Support",
                "sub_clauses": ["7.1", "7.2", "7.3", "7.4", "7.5"],
                "description": "Resources, competence, awareness, communication, documentation"
            },
            "8": {
                "title": "Operation",
                "sub_clauses": ["8.1", "8.2", "8.3", "8.4", "8.5"],
                "description": "Operational planning, BIA, risk assessment, strategies, plans, exercises"
            },
            "9": {
                "title": "Performance Evaluation",
                "sub_clauses": ["9.1", "9.2", "9.3"],
                "description": "Monitoring, internal audit, management review"
            },
            "10": {
                "title": "Improvement",
                "sub_clauses": ["10.1", "10.2"],
                "description": "Nonconformity, corrective action, continual improvement"
            }
        }

        return {
            "standard": "ISO 22301:2019",
            "total_clauses": 7,
            "clauses": clauses,
            "content_file": str(clause_file),
            "full_content_available": True
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading ISO 22301 clauses: {str(e)}")


@router.get("/iso22301/{clause}")
async def get_iso22301_clause_detail(
    clause: str,
    include_evidence: bool = Query(True, description="Include evidence requirements"),
    include_audit_questions: bool = Query(True, description="Include audit questions")
):
    """
    Get detailed information for specific ISO 22301 clause

    Args:
    - clause: Clause number (e.g., "4.1", "8.2.2")
    """
    # Get from existing standards/iso_22301.py
    from ..standards.iso_22301 import ISO_22301_REQUIREMENTS

    if clause not in ISO_22301_REQUIREMENTS:
        raise HTTPException(status_code=404, detail=f"Clause {clause} not found")

    requirement = ISO_22301_REQUIREMENTS[clause]

    response = {
        "clause": clause,
        "title": requirement.title,
        "description": requirement.description,
        "category": requirement.category,
        "mandatory": requirement.mandatory,
        "weight": requirement.weight
    }

    if include_evidence:
        response["evidence_required"] = requirement.evidence_required
        response["verification_guidance"] = requirement.verification_guidance

    if include_audit_questions:
        # Add audit questions (would be in knowledge base)
        response["audit_questions"] = [
            f"Is there documented evidence of {requirement.title.lower()}?",
            f"How does the organization ensure {requirement.title.lower()}?",
            "Can you demonstrate the implementation?"
        ]

    response["related_clauses"] = requirement.related_clauses or []

    return response


@router.get("/bci/practices")
async def get_bci_practices():
    """
    Get BCI Good Practice Guidelines - 6 Professional Practices
    """
    try:
        bci_file = KNOWLEDGE_BASE_PATH / "BCI_GPG" / "six_practices.md"

        practices = {
            "PP1": {
                "name": "Establishing the BCM Program",
                "description": "Policy & Program Management",
                "key_activities": [
                    "BCM policy development",
                    "Program governance",
                    "Resource allocation",
                    "Roles & responsibilities"
                ]
            },
            "PP2": {
                "name": "Embracing BC",
                "description": "Embedding BC Culture",
                "key_activities": [
                    "Awareness campaigns",
                    "Training programs",
                    "Competency development",
                    "Cultural change"
                ]
            },
            "PP3": {
                "name": "Analysis",
                "description": "BIA & Risk Assessment",
                "key_activities": [
                    "Business Impact Analysis",
                    "Risk assessment",
                    "Dependency mapping",
                    "Critical process identification"
                ]
            },
            "PP4": {
                "name": "Solutions Design",
                "description": "BC Strategies",
                "key_activities": [
                    "Strategy development",
                    "Solution selection",
                    "Cost-benefit analysis",
                    "Resource planning"
                ]
            },
            "PP5": {
                "name": "Enabling Solutions",
                "description": "Plans & Procedures",
                "key_activities": [
                    "Plan development",
                    "Procedure documentation",
                    "Template creation",
                    "Implementation"
                ]
            },
            "PP6": {
                "name": "Validation",
                "description": "Exercising & Testing",
                "key_activities": [
                    "Exercise planning",
                    "Testing execution",
                    "Results analysis",
                    "Continuous improvement"
                ]
            }
        }

        return {
            "standard": "BCI Good Practice Guidelines 7.0",
            "total_practices": 6,
            "practices": practices,
            "content_file": str(bci_file) if bci_file.exists() else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading BCI practices: {str(e)}")


@router.get("/who/framework")
async def get_who_framework():
    """
    Get WHO Health Emergency BCM framework

    Healthcare-specific BCM guidance
    """
    try:
        who_file = KNOWLEDGE_BASE_PATH / "WHO" / "health_emergency_bcm.md"

        framework = {
            "name": "WHO Health Emergency BCM",
            "focus": "Healthcare Essential Services",
            "service_tiers": {
                "tier_1": {
                    "name": "Life-Saving Services",
                    "rto": "< 1 hour",
                    "examples": ["Emergency department", "ICU", "Surgery"]
                },
                "tier_2": {
                    "name": "Critical Clinical Services",
                    "rto": "< 4 hours",
                    "examples": ["Laboratory", "Radiology", "Pharmacy"]
                },
                "tier_3": {
                    "name": "Essential Support Services",
                    "rto": "< 24 hours",
                    "examples": ["Medical records", "IT systems", "Sterilization"]
                },
                "tier_4": {
                    "name": "Non-Critical Services",
                    "rto": "< 7 days",
                    "examples": ["Elective procedures", "Administrative", "Training"]
                }
            },
            "regulatory_compliance": [
                "HIPAA",
                "CMS Emergency Preparedness Rule",
                "Joint Commission Standards",
                "State health department requirements"
            ],
            "all_hazards_approach": [
                "Natural disasters",
                "Pandemics",
                "Cyber attacks",
                "Infrastructure failures",
                "Mass casualty events"
            ]
        }

        return {
            "framework": framework,
            "content_file": str(who_file) if who_file.exists() else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading WHO framework: {str(e)}")


@router.get("/mapping")
async def get_iso_bci_platform_mapping():
    """
    Get ISO 22301 ↔ BCI ↔ Platform mapping

    CRITICAL DOCUMENT: Shows how platform services map to standards
    """
    try:
        mapping_file = KNOWLEDGE_BASE_PATH / "mapping" / "iso_bci_platform_mapping.md"

        # Simplified mapping (full mapping in the markdown file)
        mapping = {
            "iso_22301": {
                "clause_4": {
                    "title": "Context of Organization",
                    "bci_practice": "PP1",
                    "platform_service": "Governance (8020)",
                    "coverage": "95%"
                },
                "clause_5": {
                    "title": "Leadership",
                    "bci_practice": "PP1",
                    "platform_service": "Governance (8020)",
                    "coverage": "90%"
                },
                "clause_6": {
                    "title": "Planning",
                    "bci_practice": "PP1, PP3",
                    "platform_service": "Risk (8013), Planning (8005)",
                    "coverage": "95%"
                },
                "clause_7": {
                    "title": "Support",
                    "bci_practice": "PP2",
                    "platform_service": "Learning (8021), Documents (8024)",
                    "coverage": "85%"
                },
                "clause_8_2": {
                    "title": "BIA & Risk Assessment",
                    "bci_practice": "PP3",
                    "platform_service": "BIA (8012), Risk (8013)",
                    "coverage": "95%"
                },
                "clause_8_3": {
                    "title": "BC Strategies",
                    "bci_practice": "PP4",
                    "platform_service": "Planning (8005)",
                    "coverage": "90%"
                },
                "clause_8_4": {
                    "title": "BC Plans",
                    "bci_practice": "PP5",
                    "platform_service": "Plans (8023), Response (8007)",
                    "coverage": "100%"
                },
                "clause_8_5": {
                    "title": "Exercising",
                    "bci_practice": "PP6",
                    "platform_service": "Validation (8022)",
                    "coverage": "95%"
                },
                "clause_9": {
                    "title": "Performance Evaluation",
                    "bci_practice": "PP6",
                    "platform_service": "Validation (8022), Compliance (8014)",
                    "coverage": "85%"
                },
                "clause_10": {
                    "title": "Improvement",
                    "bci_practice": "PP6",
                    "platform_service": "Compliance (8014), Validation (8022)",
                    "coverage": "90%"
                }
            },
            "overall_coverage": {
                "iso_22301": "92%",
                "bci_gpg": "88%"
            },
            "gaps": [
                "External audit interface",
                "Third-party risk management",
                "Supply chain resilience"
            ]
        }

        return {
            "mapping": mapping,
            "content_file": str(mapping_file) if mapping_file.exists() else None,
            "last_updated": "2025-10-02"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading mapping: {str(e)}")


@router.get("/search")
async def search_knowledge_base(
    query: str = Query(..., min_length=3, description="Search query"),
    standard: Optional[str] = Query(None, description="Filter by standard (iso22301, bci, who)")
):
    """
    Search across all knowledge base content

    Args:
    - query: Search term
    - standard: Optional filter by standard
    """
    # Simplified search - in production would use full-text search
    results = []

    # Search ISO 22301
    if not standard or standard == "iso22301":
        from ..standards.iso_22301 import ISO_22301_REQUIREMENTS

        for clause_id, req in ISO_22301_REQUIREMENTS.items():
            if (query.lower() in req.title.lower() or
                query.lower() in req.description.lower()):
                results.append({
                    "source": "ISO 22301:2019",
                    "type": "clause",
                    "id": clause_id,
                    "title": req.title,
                    "excerpt": req.description[:200] + "...",
                    "url": f"/api/compliance/knowledge/iso22301/{clause_id}"
                })

    return {
        "query": query,
        "total_results": len(results),
        "results": results[:20]  # Limit to 20 results
    }
