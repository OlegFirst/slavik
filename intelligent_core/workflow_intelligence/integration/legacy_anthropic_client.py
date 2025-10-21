# -*- coding: utf-8 -*-
"""
Anthropic Integration for BCM Governance Brain
High-quality AI analysis for strategic governance decisions

Now uses ai-foundation/llm for LLM routing instead of direct httpx calls.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add ai-foundation to path
ai_foundation_path = Path(__file__).parent.parent.parent / 'ai-foundation'
sys.path.insert(0, str(ai_foundation_path))

try:
    from ai_foundation.llm import LLMRouter
except ImportError:
    # Fallback for development
    class LLMRouter:
        """Mock LLM Router"""
        async def generate(self, prompt: str, **kwargs):
            return {
                'text': '[MOCK] LLM response',
                'model': 'mock',
                'usage': {'output_tokens': 100}
            }

logger = logging.getLogger(__name__)

class AnthropicGovernanceBrain:
    """Anthropic Claude integration for governance intelligence"""

    def __init__(self):
        # Use LLMRouter from ai_foundation
        self.llm_router = LLMRouter()

        # Keep legacy API key for backward compatibility
        self.api_key = os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            logger.warning('Anthropic API key not configured - using fallback local AI')

    async def governance_analysis(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Strategic governance analysis via LLMRouter (ai-foundation)"""

        try:
            # Enhanced governance prompt
            enhanced_prompt = f"""
You are the AI Governance Brain for a Business Continuity Management platform. You possess deep expertise in:
- ISO 22301 Business Continuity Management
- Corporate governance best practices
- Risk management and compliance
- Strategic planning and oversight
- Crisis management and emergency response

Your role is to provide executive-level strategic intelligence and governance guidance.

GOVERNANCE REQUEST:
{prompt}

ORGANIZATIONAL CONTEXT:
- Company: {context.get('company', 'Unknown')}
- Governance Domain: {context.get('domain', 'General')}
- Priority Level: {context.get('priority', 'Medium')}
- AI Personality: {context.get('ai_personality', 'wise_ruler')}

Provide sophisticated, actionable governance intelligence worthy of C-level strategic decision making.
"""

            # Use LLMRouter instead of direct httpx call
            result = await self.llm_router.generate(
                prompt=enhanced_prompt,
                task_type='strategic_analysis',  # Routes to Claude Opus or GPT-4
                temperature=0.3,  # Lower temperature for strategic consistency
                max_tokens=4000
            )

            return {
                'analysis': result['text'],
                'confidence': 0.95,
                'reasoning': 'LLMRouter strategic governance analysis',
                'model_used': result.get('model', 'unknown'),
                'tokens_used': result.get('usage', {}).get('output_tokens', 0)
            }

        except Exception as e:
            logger.error(f'LLMRouter governance analysis failed: {e}')
            return await self._fallback_local_analysis(prompt, context)

    async def policy_analysis(self, policy_content: str, policy_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Anthropic Claude policy analysis"""

        policy_prompt = f"""
You are the AI Governance Brain analyzing a BCM policy document.

POLICY DETAILS:
Type: {policy_type}
Organization: {context.get('company', 'Unknown')}

POLICY CONTENT:
{policy_content}

Perform comprehensive policy analysis:

1. ISO 22301 COMPLIANCE ASSESSMENT:
   - Alignment with ISO 22301 requirements
   - Missing mandatory elements
   - Best practice compliance

2. STRATEGIC ANALYSIS:
   - Policy effectiveness assessment
   - Strategic alignment with BCM objectives
   - Risk mitigation adequacy

3. IMPLEMENTATION GUIDANCE:
   - Practical implementation recommendations
   - Resource requirements
   - Change management considerations

4. IMPROVEMENT RECOMMENDATIONS:
   - Specific enhancement suggestions
   - Regulatory alignment improvements
   - Operational efficiency gains

Provide executive-level policy intelligence with actionable recommendations.
"""

        return await self.governance_analysis(policy_prompt, context)

    async def board_report_generation(self, governance_analysis: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive board report via Anthropic"""

        board_prompt = f"""
You are the AI Governance Brain creating an executive board report.

GOVERNANCE ANALYSIS FOUNDATION:
{governance_analysis}

Create a professional C-level board report with:

1. EXECUTIVE SUMMARY (2-3 sentences)
   - Key findings and strategic implications

2. STRATEGIC ASSESSMENT
   - Business impact and risk analysis
   - Competitive implications
   - Stakeholder considerations

3. RECOMMENDATIONS
   - Immediate actions (next 30 days)
   - Strategic initiatives (next 90 days)
   - Long-term evolution (6-12 months)

4. RESOURCE REQUIREMENTS
   - Budget implications
   - Staffing needs
   - Technology requirements

5. SUCCESS METRICS
   - KPIs for measuring progress
   - Risk reduction indicators
   - ROI projections

Format for board presentation with clear action items and business justification.
"""

        return await self.governance_analysis(board_prompt, context)

    async def emergency_governance_analysis(self, emergency_situation: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Emergency governance analysis via Anthropic"""

        emergency_prompt = f"""
 EMERGENCY GOVERNANCE SESSION

You are the AI Governance Brain in EMERGENCY MODE responding to a critical governance issue.

EMERGENCY SITUATION:
{emergency_situation}

IMMEDIATE ANALYSIS REQUIRED:

1. CRISIS ASSESSMENT (URGENT):
   - Immediate threat level
   - Potential business impact
   - Regulatory/legal exposure
   - Reputational risk

2. IMMEDIATE ACTIONS (NEXT 24 HOURS):
   - Critical decisions required
   - Key stakeholders to notify
   - Resources to mobilize
   - Communications strategy

3. STRATEGIC RESPONSE:
   - Crisis management approach
   - Regulatory notifications required
   - Board/executive briefing needs
   - External communications

4. RISK MITIGATION:
   - Immediate protective measures
   - Damage control strategies
   - Recovery planning
   - Future prevention measures

Provide IMMEDIATE executive guidance for crisis governance.
"""

        result = await self.governance_analysis(emergency_prompt, context)
        result['emergency_level'] = True
        return result

    async def _fallback_local_analysis(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback to local AI if Anthropic unavailable"""

        try:
            # Call local AI Orchestrator
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'http://ai_orchestrator:8000/nlp/query',
                    json={
                        'query': prompt,
                        'context': context,
                        'user_role': 'governance_brain'
                    },
                    timeout=60.0
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        'analysis': result.get('response', ''),
                        'confidence': 0.7,  # Lower confidence for local fallback
                        'reasoning': 'Local AI fallback analysis',
                        'model_used': 'local_ai_orchestrator'
                    }

        except Exception as e:
            logger.error(f'Fallback local analysis failed: {e}')

        # Final fallback - basic structured response
        return {
            'analysis': f'<h3>Governance Analysis</h3><p>Topic: {context.get("domain", "Unknown")}</p><p>Basic analysis placeholder - AI services unavailable.</p>',
            'confidence': 0.1,
            'reasoning': 'Fallback analysis - AI services unavailable',
            'model_used': 'fallback_template'
        }

# Global instance
anthropic_governance = AnthropicGovernanceBrain()