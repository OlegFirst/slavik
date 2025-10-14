"""
AI Domain Integration - STAGE 4
Domain-aware AI prompt enhancement for BIA, Risk, and Planning modules
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from database.domain_models import Tenant, IndustryKnowledge


# ============================================================================
# CORE FUNCTION: ENHANCE AI PROMPT WITH DOMAIN CONTEXT
# ============================================================================

async def enhance_ai_prompt_with_domain(
    base_prompt: str,
    tenant_id: str,
    context_type: str,  # 'bia', 'risk', 'planning', 'exercise'
    db: AsyncSession,
    top_k_recommendations: int = 5
) -> str:
    """
    Enhance AI prompt with industry-specific context and recommendations.

    **Purpose:** Make AI responses industry-aware by injecting domain knowledge
    into prompts sent to LLM (Claude, GPT, etc.)

    **Example Usage:**
    ```python
    # Before (generic AI prompt):
    prompt = "Suggest an RTO for this critical process: Patient Registration"

    # After (domain-enhanced):
    enhanced = await enhance_ai_prompt_with_domain(
        base_prompt=prompt,
        tenant_id="hospital_001",
        context_type="bia",
        db=db
    )
    # Result: Prompt now includes:
    # - Industry context (healthcare, hospital, large)
    # - Typical RTOs for similar processes (2-4 hours)
    # - Regulatory requirements (HIPAA, Joint Commission)
    # - Common risks (ransomware, power outage)
    ```

    Args:
        base_prompt: Original AI prompt (e.g., "Suggest RTO for this process")
        tenant_id: Tenant identifier
        context_type: Type of context ('bia', 'risk', 'planning', 'exercise')
        db: Database session
        top_k_recommendations: Number of recommendations to include (default 5)

    Returns:
        Enhanced prompt with domain context and industry best practices
    """

    # Step 1: Get tenant domain classification
    tenant_stmt = select(Tenant).where(Tenant.id == tenant_id)
    tenant_result = await db.execute(tenant_stmt)
    tenant = tenant_result.scalar_one_or_none()

    # If tenant not classified, return original prompt
    if not tenant or not tenant.industry_domain:
        return base_prompt

    # Step 2: Get relevant industry knowledge
    recommendations = await get_tenant_recommendations_internal(
        tenant=tenant,
        context_type=context_type,
        db=db,
        limit=top_k_recommendations
    )

    # Step 3: Build enhanced prompt
    enhanced_prompt = _build_enhanced_prompt(
        base_prompt=base_prompt,
        tenant=tenant,
        recommendations=recommendations,
        context_type=context_type
    )

    return enhanced_prompt


# ============================================================================
# HELPER: GET TENANT RECOMMENDATIONS (INTERNAL)
# ============================================================================

async def get_tenant_recommendations_internal(
    tenant: Tenant,
    context_type: str,
    db: AsyncSession,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Internal function to get domain recommendations for tenant.

    Similar to domain_api.get_tenant_recommendations but returns raw dicts.
    """

    industry = tenant.industry_domain
    sub_domain = tenant.sub_domain

    # Build query for relevant knowledge
    conditions = [
        IndustryKnowledge.industry == industry,
        IndustryKnowledge.is_active == True
    ]

    if sub_domain:
        conditions.append(IndustryKnowledge.sub_domain == sub_domain)

    # Filter by context type
    if context_type:
        # Map context types to knowledge types
        context_mapping = {
            'bia': ['typical_rto', 'typical_rpo', 'critical_process'],
            'risk': ['common_risk', 'regulatory_requirement'],
            'planning': ['best_practice', 'regulatory_requirement'],
            'exercise': ['common_risk', 'best_practice']
        }

        knowledge_types = context_mapping.get(context_type, [])
        if knowledge_types:
            # Match any of the knowledge types
            type_conditions = [
                IndustryKnowledge.knowledge_type == kt for kt in knowledge_types
            ]
            conditions.append(or_(*type_conditions))

    stmt = select(IndustryKnowledge).where(and_(*conditions))
    stmt = stmt.order_by(
        IndustryKnowledge.confidence_level.desc(),
        IndustryKnowledge.usage_count.desc()
    ).limit(limit)

    result = await db.execute(stmt)
    knowledge_items = result.scalars().all()

    # Calculate relevance scores and convert to dicts
    confidence_scores = {'verified': 100, 'high': 85, 'medium': 70, 'low': 50}
    recommendations = []

    for k in knowledge_items:
        base_score = confidence_scores.get(k.confidence_level, 70)
        usage_boost = min(k.usage_count * 0.5, 15)
        relevance_score = min(base_score + usage_boost, 100)

        recommendations.append({
            'id': k.id,
            'title': k.title,
            'knowledge_type': k.knowledge_type,
            'description': k.description,
            'knowledge_data': k.knowledge_data,
            'source': k.source,
            'relevance_score': round(relevance_score, 2)
        })

    return recommendations


# ============================================================================
# HELPER: BUILD ENHANCED PROMPT
# ============================================================================

def _build_enhanced_prompt(
    base_prompt: str,
    tenant: Tenant,
    recommendations: List[Dict[str, Any]],
    context_type: str
) -> str:
    """
    Build enhanced prompt with domain context.
    """

    # Format regulatory requirements
    reg_reqs = ', '.join(tenant.regulatory_requirements) if tenant.regulatory_requirements else 'Not specified'

    # Build industry context section
    industry_context = f"""
INDUSTRY CONTEXT:
- Organization Type: {tenant.organizational_type or 'Not specified'}
- Industry: {tenant.industry_domain}
- Sub-domain: {tenant.sub_domain or 'General'}
- Company Size: {tenant.company_size or 'Not specified'}
- Geographic Scope: {tenant.geographic_scope or 'Not specified'}
- Regulatory Requirements: {reg_reqs}
"""

    # Build recommendations section
    if recommendations:
        rec_section = f"\nINDUSTRY BEST PRACTICES AND BENCHMARKS ({context_type.upper()}):\n"

        for i, rec in enumerate(recommendations, 1):
            rec_section += f"\n{i}. {rec['title']} (Type: {rec['knowledge_type']}, Relevance: {rec['relevance_score']}%)\n"

            # Add key details from knowledge_data
            if rec['knowledge_data']:
                data = rec['knowledge_data']

                # Extract relevant fields based on knowledge type
                if rec['knowledge_type'] == 'typical_rto':
                    if 'typical_rto_hours' in data:
                        rec_section += f"   - Typical RTO: {data['typical_rto_hours']} hours (Range: {data.get('range_min_hours', 'N/A')}-{data.get('range_max_hours', 'N/A')}h)\n"
                    if 'reasoning' in data:
                        rec_section += f"   - Reasoning: {data['reasoning']}\n"

                elif rec['knowledge_type'] == 'common_risk':
                    if 'risk_name' in data:
                        rec_section += f"   - Risk: {data['risk_name']} (Likelihood: {data.get('likelihood', 'N/A')}, Impact: {data.get('typical_impact', 'N/A')})\n"
                    if 'mitigation_strategies' in data and isinstance(data['mitigation_strategies'], list):
                        rec_section += f"   - Mitigations: {', '.join(data['mitigation_strategies'][:3])}\n"

                elif rec['knowledge_type'] == 'regulatory_requirement':
                    if 'regulation' in data:
                        rec_section += f"   - Regulation: {data['regulation']}\n"
                    if 'requirement' in data:
                        rec_section += f"   - Requirement: {data['requirement']}\n"
                    if 'recommended_rto' in data:
                        rec_section += f"   - Recommended RTO: {data['recommended_rto']}\n"

                elif rec['knowledge_type'] == 'best_practice':
                    if 'practice_name' in data:
                        rec_section += f"   - Practice: {data['practice_name']}\n"
                    if 'description' in data:
                        rec_section += f"   - Description: {data['description'][:200]}...\n"

            if rec['source']:
                rec_section += f"   - Source: {rec['source']}\n"

    else:
        rec_section = "\nINDUSTRY BEST PRACTICES: No specific recommendations available for this context.\n"

    # Build final enhanced prompt
    enhanced_prompt = f"""{base_prompt}

{industry_context}
{rec_section}

INSTRUCTIONS FOR AI:
Provide recommendations that are specific to this industry context. Reference the industry best practices above when relevant. Consider regulatory requirements and industry-specific risks in your response. Be specific and actionable.
"""

    return enhanced_prompt


# ============================================================================
# HELPER FUNCTION: FORMAT RECOMMENDATIONS FOR DISPLAY
# ============================================================================

def format_recommendations_summary(recommendations: List[Dict[str, Any]]) -> str:
    """
    Format recommendations as a concise summary string.

    Useful for embedding in API responses or UI displays.
    """

    if not recommendations:
        return "No industry recommendations available."

    summary = []
    for rec in recommendations[:5]:  # Top 5
        summary.append(f"• {rec['title']} ({rec['knowledge_type']}, {rec['relevance_score']}% relevant)")

    return "\n".join(summary)


# ============================================================================
# CONTEXT TYPE VALIDATORS
# ============================================================================

VALID_CONTEXT_TYPES = ['bia', 'risk', 'planning', 'exercise']

def validate_context_type(context_type: str) -> bool:
    """Validate context type is supported."""
    return context_type in VALID_CONTEXT_TYPES


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

"""
Example integration in BIA module:

from governance.ai_domain_integration import enhance_ai_prompt_with_domain

@router.post("/api/bia/processes/{process_id}/suggest-rto")
async def suggest_rto_with_domain(
    process_id: int,
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
):
    # Get process details
    process = await get_process(process_id, db)

    # Build base prompt
    base_prompt = f\"\"\"
Suggest an appropriate RTO (Recovery Time Objective) for the following business process:

Process Name: {process.name}
Description: {process.description}
Current Criticality: {process.criticality_level}
Dependencies: {process.dependencies}

What RTO would you recommend and why?
\"\"\"

    # Enhance with domain intelligence
    enhanced_prompt = await enhance_ai_prompt_with_domain(
        base_prompt=base_prompt,
        tenant_id=tenant_id,
        context_type='bia',
        db=db
    )

    # Call AI orchestrator with enhanced prompt
    ai_response = await call_ai_orchestrator(enhanced_prompt)

    return {
        "process_id": process_id,
        "suggested_rto": ai_response.rto,
        "reasoning": ai_response.reasoning,
        "industry_context_applied": True
    }
"""
