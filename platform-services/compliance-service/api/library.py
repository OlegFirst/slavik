"""
Library API - ISO 22301 Implementation Guides & Research

Provides access to:
- Implementation guides (BSI, NQA, ISO)
- Consultant research (Deloitte, EY, McKinsey, BearingPoint)
- Best practices and case studies

Note: Actual PDF files are stored in Documents service (port 8024)
This API provides metadata and references.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from pathlib import Path

router = APIRouter()


@router.get("/guides")
async def list_implementation_guides():
    """
    List all ISO 22301 implementation guides

    Returns metadata for:
    - BSI Implementation Guide (10 MB)
    - NQA Implementation Guide (3.5 MB)
    - ISO 2019 Implementation Guide (922 KB)

    Actual PDFs stored in Documents service at:
    /documents/library/iso22301/
    """
    guides = [
        {
            "id": "bsi-iso22301",
            "title": "BSI ISO 22301 Implementation Guide",
            "author": "British Standards Institution",
            "description": "Comprehensive implementation guide from the organization that created the predecessor to ISO 22301",
            "file_size": "10 MB",
            "pages": "~200",
            "year": 2019,
            "topics": [
                "Step-by-step implementation",
                "Clause-by-clause guidance",
                "Templates and checklists",
                "Case studies",
                "Certification preparation"
            ],
            "file_path": "/documents/library/iso22301/BSI-ISO-22301-Implementation-Guide.pdf",
            "download_url": "/api/documents/library/iso22301/BSI-ISO-22301-Implementation-Guide.pdf"
        },
        {
            "id": "nqa-iso22301",
            "title": "NQA ISO 22301 Implementation Guide",
            "author": "NQA (Certification Body)",
            "description": "Implementation guide from NQA - 400+ successful certifications without failures",
            "file_size": "3.5 MB",
            "pages": "~80",
            "year": 2019,
            "topics": [
                "Certification process",
                "Common pitfalls",
                "Audit preparation",
                "Evidence requirements",
                "Best practices"
            ],
            "file_path": "/documents/library/iso22301/NQA-ISO-22301-Implementation-Guide.pdf",
            "download_url": "/api/documents/library/iso22301/NQA-ISO-22301-Implementation-Guide.pdf"
        },
        {
            "id": "iso-2019-guide",
            "title": "ISO 22301:2019 Practical Implementation Guide",
            "author": "ISO / Industry Experts",
            "description": "Practical guide focused on ISO 22301:2019 updates and implementation",
            "file_size": "922 KB",
            "pages": "~50",
            "year": 2019,
            "topics": [
                "2019 updates",
                "Quick implementation",
                "PDCA cycle",
                "Documentation requirements",
                "Gap assessment"
            ],
            "file_path": "/documents/library/iso22301/ISO-22301-2019-Implementation-Guide.pdf",
            "download_url": "/api/documents/library/iso22301/ISO-22301-2019-Implementation-Guide.pdf"
        }
    ]

    return {
        "total_guides": len(guides),
        "guides": guides,
        "note": "Download PDFs via Documents service (port 8024)"
    }


@router.get("/guides/{guide_id}")
async def get_guide_detail(guide_id: str):
    """
    Get detailed information about specific implementation guide
    """
    guides_map = {
        "bsi-iso22301": {
            "id": "bsi-iso22301",
            "title": "BSI ISO 22301 Implementation Guide",
            "author": "British Standards Institution",
            "description": "Comprehensive implementation guide from the organization that created the predecessor to ISO 22301",
            "file_size": "10 MB",
            "file_path": "/documents/library/iso22301/BSI-ISO-22301-Implementation-Guide.pdf",
            "download_url": "/api/documents/library/iso22301/BSI-ISO-22301-Implementation-Guide.pdf",
            "table_of_contents": [
                "1. Introduction to ISO 22301",
                "2. Understanding the Standard",
                "3. Clause-by-Clause Implementation",
                "4. Templates and Tools",
                "5. Certification Process",
                "6. Case Studies",
                "7. Maintaining Certification"
            ],
            "target_audience": [
                "BCM Managers",
                "Consultants",
                "Organizations seeking certification"
            ]
        },
        "nqa-iso22301": {
            "id": "nqa-iso22301",
            "title": "NQA ISO 22301 Implementation Guide",
            "author": "NQA",
            "file_size": "3.5 MB",
            "file_path": "/documents/library/iso22301/NQA-ISO-22301-Implementation-Guide.pdf",
            "download_url": "/api/documents/library/iso22301/NQA-ISO-22301-Implementation-Guide.pdf"
        },
        "iso-2019-guide": {
            "id": "iso-2019-guide",
            "title": "ISO 22301:2019 Practical Implementation Guide",
            "file_size": "922 KB",
            "file_path": "/documents/library/iso22301/ISO-22301-2019-Implementation-Guide.pdf",
            "download_url": "/api/documents/library/iso22301/ISO-22301-2019-Implementation-Guide.pdf"
        }
    }

    if guide_id not in guides_map:
        raise HTTPException(status_code=404, detail=f"Guide {guide_id} not found")

    return guides_map[guide_id]


@router.get("/research")
async def get_consultant_research():
    """
    Get research and insights from consulting firms

    Returns findings from:
    - Deloitte
    - Ernst & Young (EY)
    - McKinsey & Company
    - BearingPoint
    """
    research = [
        {
            "source": "Deloitte",
            "title": "BCM ROI and Recovery Speed Study",
            "year": 2024,
            "key_findings": [
                "40% cost savings on recovery activities",
                "45% faster business process restoration",
                "Certified organizations show greater crisis resilience"
            ],
            "implications": [
                "Clear ROI case for ISO 22301 certification",
                "Faster recovery = competitive advantage",
                "Reduced insurance premiums possible"
            ]
        },
        {
            "source": "Ernst & Young (EY)",
            "title": "Supply Chain Resilience in BCM",
            "year": 2024,
            "key_findings": [
                "Fewer supply chain disruptions with ISO 22301",
                "20% faster recovery from interruptions",
                "Better vendor relationships and contracts"
            ],
            "implications": [
                "Supply chain should be core BCM focus",
                "Third-party risk management critical",
                "Vendor BCM requirements in contracts"
            ]
        },
        {
            "source": "McKinsey & Company",
            "title": "BCM Implementation Methodology",
            "year": 2023,
            "key_recommendations": [
                "Use iterative PDCA approach",
                "Start with gap assessment",
                "Focus on high-impact quick wins",
                "Build internal capability vs. outsource"
            ],
            "implementation_phases": [
                "Phase 1: Gap Assessment (4-6 weeks)",
                "Phase 2: Priority Implementations (12-16 weeks)",
                "Phase 3: Full BCMS Roll-out (6-12 months)",
                "Phase 4: Certification Preparation (8-12 weeks)"
            ]
        },
        {
            "source": "BearingPoint",
            "title": "European BCM Compliance Study",
            "year": 2023,
            "key_findings": [
                "Notable reputation improvement post-certification",
                "Enhanced regulatory compliance",
                "Improved internal operations efficiency"
            ],
            "regional_insights": [
                "EU: Strong focus on GDPR integration",
                "UK: Financial services regulation compliance",
                "Germany: Critical infrastructure requirements"
            ]
        }
    ]

    return {
        "total_research_sources": len(research),
        "research": research,
        "summary": {
            "avg_cost_savings": "40%",
            "avg_recovery_improvement": "32.5%",
            "recommended_approach": "Iterative PDCA",
            "typical_implementation_time": "12-18 months"
        }
    }


@router.get("/research/{source}")
async def get_research_by_source(source: str):
    """
    Get research from specific consulting firm

    Args:
    - source: deloitte, ey, mckinsey, bearingpoint
    """
    source_map = {
        "deloitte": {
            "firm": "Deloitte",
            "reports": [
                {
                    "title": "BCM ROI and Recovery Speed Study",
                    "findings": {
                        "cost_savings": "40%",
                        "recovery_speed": "45% faster",
                        "sample_size": "500+ organizations globally"
                    }
                }
            ]
        },
        "ey": {
            "firm": "Ernst & Young",
            "reports": [
                {
                    "title": "Supply Chain Resilience in BCM",
                    "findings": {
                        "supply_chain_improvements": "fewer disruptions",
                        "recovery_speed": "20% faster",
                        "focus_areas": ["vendor management", "contracts", "monitoring"]
                    }
                }
            ]
        },
        "mckinsey": {
            "firm": "McKinsey & Company",
            "reports": [
                {
                    "title": "BCM Implementation Methodology",
                    "approach": "Iterative PDCA",
                    "timeline": "12-18 months typical",
                    "focus": "Gap assessment → Quick wins → Full implementation"
                }
            ]
        },
        "bearingpoint": {
            "firm": "BearingPoint",
            "reports": [
                {
                    "title": "European BCM Compliance Study",
                    "benefits": ["reputation", "compliance", "operations"],
                    "regional_focus": "Europe"
                }
            ]
        }
    }

    source_key = source.lower().replace(" ", "").replace("&", "")
    if source_key not in source_map:
        raise HTTPException(status_code=404, detail=f"Research from {source} not found")

    return source_map[source_key]


@router.get("/best-practices")
async def get_best_practices():
    """
    Get aggregated best practices from all sources

    Combines insights from implementation guides and research
    """
    best_practices = {
        "implementation": [
            {
                "practice": "Start with Gap Assessment",
                "source": "McKinsey, BSI",
                "description": "Understand current state vs. ISO 22301 requirements before implementation",
                "effort": "4-6 weeks",
                "roi": "High - prevents wasted effort"
            },
            {
                "practice": "Use Iterative PDCA Approach",
                "source": "McKinsey, ISO",
                "description": "Plan-Do-Check-Act cycles for continuous improvement",
                "effort": "Ongoing",
                "roi": "High - sustainable improvement"
            },
            {
                "practice": "Focus on Quick Wins First",
                "source": "McKinsey, Deloitte",
                "description": "Implement high-impact, low-effort improvements early",
                "effort": "Varies",
                "roi": "Very High - builds momentum"
            },
            {
                "practice": "Engage Leadership Early",
                "source": "All sources",
                "description": "ISO 22301 Clause 5.1 - leadership commitment is mandatory",
                "effort": "2-4 weeks",
                "roi": "Critical - failure without it"
            },
            {
                "practice": "Build Internal Capability",
                "source": "McKinsey, BearingPoint",
                "description": "Train internal team vs. full outsourcing",
                "effort": "3-6 months",
                "roi": "High - long-term sustainability"
            }
        ],
        "common_pitfalls": [
            {
                "pitfall": "Treating BCM as IT-only initiative",
                "solution": "BCM is organization-wide, not just IT disaster recovery"
            },
            {
                "pitfall": "Documentation without implementation",
                "solution": "Focus on working BCMS, not just documents for audit"
            },
            {
                "pitfall": "Skipping exercises",
                "solution": "ISO 8.5 requires testing - no certification without it"
            },
            {
                "pitfall": "Ignoring supply chain",
                "solution": "Third-party dependencies are critical (EY research)"
            }
        ],
        "success_factors": [
            "Executive sponsorship and visible commitment",
            "Cross-functional team involvement",
            "Adequate resources (budget, time, people)",
            "Integration with existing risk management",
            "Regular communication and awareness",
            "Realistic timelines (12-18 months typical)"
        ]
    }

    return best_practices


@router.get("/case-studies")
async def get_case_studies():
    """
    Get case studies and success stories

    NOTE: Detailed case studies are in the PDF implementation guides
    """
    return {
        "note": "Detailed case studies available in BSI Implementation Guide",
        "download_guide": "/api/compliance/library/guides/bsi-iso22301",
        "summary_examples": [
            {
                "industry": "Financial Services",
                "challenge": "Regulatory compliance + operational resilience",
                "solution": "Integrated ISO 22301 with existing risk framework",
                "outcome": "Regulatory approval + 30% faster incident response"
            },
            {
                "industry": "Healthcare",
                "challenge": "Patient safety during emergencies",
                "solution": "WHO BCM framework + ISO 22301 certification",
                "outcome": "Zero patient safety incidents during 3 major crises"
            },
            {
                "industry": "Manufacturing",
                "challenge": "Supply chain disruptions",
                "solution": "ISO 22301 with vendor BCM requirements",
                "outcome": "50% reduction in supply chain disruptions"
            }
        ]
    }
