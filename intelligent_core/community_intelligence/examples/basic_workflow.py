"""
Basic workflow example for Community Intelligence

Demonstrates:
1. Submitting a case for review
2. Peer reviewing a case
3. Checking reputation
4. Adding annotations
5. Getting synthesized guidance
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directories to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent.parent))

try:
    from intelligent_core.community_intelligence.services.anonymizer import SmartAnonymizer
except ImportError:
    # Fallback: direct import
    sys.path.insert(0, str(current_dir.parent))
    from services.anonymizer import SmartAnonymizer

async def example_case_submission():
    """Example: Submit a workflow case for community review"""

    # Sample case data from completed BIA workflow
    case_data = {
        "organization_name": "Healthcare Provider ABC",  # Will be removed
        "organization_context": {
            "industry": "healthcare",
            "location": "Tallinn, Estonia",  # Will be generalized
            "employee_count": 150,  # Will be generalized to 'medium'
            "maturity_level": "developing"
        },
        "module": "bia",
        "workflow_name": "Business Impact Analysis",
        "journey": [
            {
                "stage": "discovery",
                "started_at": "2025-10-01",
                "actions": [
                    {
                        "type": "process_identified",
                        "data": {
                            "process_name": "Emergency Department at City Hospital",
                            "criticality": "critical"
                        }
                    }
                ]
            },
            {
                "stage": "analysis",
                "started_at": "2025-10-05",
                "actions": [
                    {
                        "type": "bia_completed",
                        "data": {
                            "rto": 4,
                            "rpo": 1,
                            "financial_impact": "high"
                        }
                    }
                ]
            }
        ],
        "metrics": {
            "processes_count": 25,
            "duration_days": 45,
            "completed_successfully": True
        },
        "success_patterns": [
            "Strong executive sponsorship enabled rapid progress",
            "Cross-functional team included IT, operations, and compliance",
            "Used automated dependency mapping tool"
        ],
        "challenges": [
            "Initial resistance from department heads",
            "Data quality issues in existing process documentation"
        ]
    }

    # Initialize services
    anonymizer = SmartAnonymizer(k_anonymity=5)
    # db, case_library would come from dependency injection in real app

    # 1. Anonymize the case
    print("🔒 Anonymizing case data...")
    result = await anonymizer.anonymize_case(case_data)

    print(f"   Removed fields: {result.removed_fields}")
    print(f"   Transformed fields: {result.transformed_fields}")
    print(f"   Re-identification risk: {result.risk_score:.2f}")

    # Check if risk is acceptable
    if result.risk_score > 0.7:
        print("   ⚠️  Risk too high! Consider more generalization.")
        return

    print("   ✅ Anonymization successful")

    # 2. Submit for peer review (would use ContributionService)
    print("\n📤 Submitting to peer review...")
    print("   Assigned 3 reviewers based on expertise")
    print("   Review deadline: 7 days from now")
    print("   ✅ Submission complete")

    return result

async def example_peer_review():
    """Example: Review a submitted case"""

    print("\n👥 PEER REVIEW PROCESS")
    print("=" * 50)

    # Reviewer sees anonymized case
    review_data = {
        "approved": True,
        "quality_score": 8,  # 1-10
        "feedback": "Great case study! Success patterns are clear and actionable.",
        "improvements": {
            "suggestions": [
                "Add more details on tool selection process",
                "Include timeline for each stage"
            ]
        },
        "anonymization_ok": True,
        "relevance_ok": True,
        "completeness_ok": True,
        "lessons_clear": True
    }

    print(f"   Quality Score: {review_data['quality_score']}/10")
    print(f"   Approved: {'✅' if review_data['approved'] else '❌'}")
    print(f"   Feedback: {review_data['feedback']}")

    # When 2/3 reviewers approve → case added to library
    print("\n   📊 Review status:")
    print("   ✅ Reviewer 1: Approved (score: 8)")
    print("   ✅ Reviewer 2: Approved (score: 9)")
    print("   ⏳ Reviewer 3: Pending")
    print("\n   → Majority reached! Case APPROVED")
    print("   → Added to Case Library")
    print("   → Contributor earned 40 reputation points")

async def example_reputation():
    """Example: Check user reputation"""

    print("\n🏆 REPUTATION SYSTEM")
    print("=" * 50)

    reputation = {
        "user_id": "user_123",
        "total_points": 340,
        "level": "contributor",  # newcomer → contributor → expert → master
        "contribution_points": 280,  # From approved cases
        "review_points": 45,  # From peer reviews
        "helpfulness_points": 15,  # From helpful answers
        "expertise": {
            "bia": 75,
            "risk": 50,
            "planning": 30
        },
        "badges": ["First Contribution", "Quality Reviewer", "BIA Expert"],
        "contributions_count": 6,
        "reviews_count": 9
    }

    print(f"   Level: {reputation['level'].upper()}")
    print(f"   Total Points: {reputation['total_points']}")
    print(f"\n   Expertise:")
    for domain, score in reputation['expertise'].items():
        bar = "█" * (score // 10)
        print(f"   {domain.upper():12s}: {bar} {score}/100")

    print(f"\n   Badges: {', '.join(reputation['badges'])}")

    # Level progression
    print("\n   📈 Progress to next level (Expert):")
    print(f"   Current: 340 / 500 points")
    bar_filled = int((340 / 500) * 30)
    bar = "█" * bar_filled + "░" * (30 - bar_filled)
    print(f"   [{bar}] 68%")

async def example_living_documentation():
    """Example: Add interpretation and get synthesized guidance"""

    print("\n📚 LIVING DOCUMENTATION")
    print("=" * 50)

    # Expert adds interpretation
    annotation = {
        "clause_id": "4.1",  # ISO 22301: Understanding the organization
        "interpretation": """
        In healthcare context, understanding the organization requires:
        1. Mapping all patient-facing services and their dependencies
        2. Identifying regulatory compliance requirements (HIPAA, HITECH)
        3. Understanding data flows between EMR, lab systems, imaging
        4. Documenting third-party dependencies (labs, pharmacies, specialists)

        Key insight: Many healthcare orgs miss dependencies on support services
        (e.g., HVAC for lab equipment, power for medical devices).
        """,
        "industry_specific": "healthcare",
        "org_size": "medium",
        "examples": [
            "Hospital mapped 150+ processes, found 30 critical dependencies",
            "Clinic discovered unrecognized dependency on cloud EMR provider"
        ]
    }

    print(f"   Expert added interpretation for clause {annotation['clause_id']}")
    print(f"   Industry: {annotation['industry_specific']}")
    print(f"   Examples: {len(annotation['examples'])}")

    # Community votes
    print("\n   Community feedback:")
    print("   ⬆️  Upvotes: 15")
    print("   ⬇️  Downvotes: 2")
    print("   ⭐ Helpful marks: 12")

    # AI synthesizes unified guidance
    print("\n   🤖 AI Synthesizing unified guidance...")
    synthesized = {
        "guidance": """
        ISO 22301 Clause 4.1 requires organizations to understand their context,
        including internal/external factors affecting BCM objectives.

        For healthcare organizations, this means:
        - Map all clinical and administrative processes
        - Identify regulatory requirements (HIPAA, local health codes)
        - Document technology dependencies (EMR, PACS, lab systems)
        - Understand third-party dependencies (labs, pharmacies, vendors)
        """,
        "steps": [
            "Create inventory of all services (patient-facing and support)",
            "Map technology infrastructure and dependencies",
            "Identify regulatory and compliance requirements",
            "Document stakeholder relationships (patients, regulators, partners)",
            "Review and validate with department heads"
        ],
        "pitfalls": [
            "Missing support service dependencies (HVAC, power, facilities)",
            "Underestimating third-party risks (cloud providers, vendors)",
            "Incomplete documentation of data flows"
        ],
        "patterns": [
            "Cross-functional workshops reveal hidden dependencies",
            "Automated discovery tools find technical dependencies",
            "Regular reviews keep documentation current"
        ]
    }

    print("   ✅ Synthesis complete!")
    print(f"\n   📖 Unified Guidance:")
    print(f"   {synthesized['guidance'][:200]}...")
    print(f"\n   ✓ {len(synthesized['steps'])} practical steps")
    print(f"   ✓ {len(synthesized['pitfalls'])} common pitfalls")
    print(f"   ✓ {len(synthesized['patterns'])} success patterns")

async def main():
    """Run all examples"""

    print("=" * 70)
    print("COMMUNITY INTELLIGENCE - EXAMPLE WORKFLOWS")
    print("=" * 70)

    # 1. Case submission
    await example_case_submission()

    # 2. Peer review
    await example_peer_review()

    # 3. Reputation
    await example_reputation()

    # 4. Living documentation
    await example_living_documentation()

    print("\n" + "=" * 70)
    print("✅ All examples complete!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
