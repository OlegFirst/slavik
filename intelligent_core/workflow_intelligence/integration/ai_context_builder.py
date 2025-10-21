"""
AI Context Builder
==================

Extracted from: /Users/MD/AI-Platform-ISO/SESSION_SUMMARY.md
Source lines: 1900-2110
Date extracted: 2025-10-04

Description:
-----------
Builds comprehensive context for AI Advisor by combining:
- Current workflow state and validation status
- Similar successful cases from case library
- Industry benchmarks
- Comparison to benchmarks
- Trending patterns
- Formatted prompts for LLM

This ensures AI has all necessary context to provide informed, data-driven advice.

Dependencies:
- state_machine_extracted.py (StateMachine)
- case_library_extracted.py (CaseRepository)
"""

from typing import Dict, Any, List, Optional


class AIContextBuilder:
    """
    Построитель контекста для AI Advisor

    Собирает всю информацию которую AI должен знать:
    - Workflow state (откуда, куда, что сделано)
    - Validation errors (что не хватает)
    - Similar cases (что работало у других)
    - Benchmarks (как мы на фоне индустрии)
    - Available actions (что можно сделать)
    """

    def __init__(
        self,
        workflow_engine,  # StateMachine
        case_repository  # CaseRepository
    ):
        self.workflow = workflow_engine
        self.cases = case_repository

    async def build_full_context(
        self,
        org_context: Dict[str, Any],
        user_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Построить полный контекст для AI

        Это ВСЁ что AI должен знать для качественного advice
        """

        # 1. Workflow state
        workflow_context = self.workflow.get_context()

        # 2. Similar successful cases
        similar_cases = await self.cases.find_similar_cases(
            industry=org_context['industry'],
            size=org_context['size'],
            module=self.workflow.current_state.data.get('module', 'bia'),
            current_stage=workflow_context['current_state'],
            success_only=True,
            limit=3
        )

        # 3. Benchmarks
        benchmarks = await self.cases.get_benchmarks(
            industry=org_context['industry'],
            size=org_context['size'],
            module=self.workflow.current_state.data.get('module', 'bia')
        )

        # 4. Compare to benchmarks
        comparison = await self.cases.compare_to_benchmarks(
            current_metrics={
                'duration_days': workflow_context['time_in_state'] / 86400,
                'ai_usage_count': len([
                    a for a in workflow_context['completed_actions']
                    if 'ai' in a.lower()
                ])
            },
            industry=org_context['industry'],
            size=org_context['size'],
            module=self.workflow.current_state.data.get('module', 'bia')
        )

        # 5. Trending patterns
        trending = await self.cases.get_trending_patterns(
            module=self.workflow.current_state.data.get('module', 'bia'),
            days=30
        )

        return {
            'workflow': workflow_context,
            'organization': org_context,
            'similar_cases': [self._format_case_for_ai(c) for c in similar_cases],
            'benchmarks': benchmarks,
            'comparison': comparison,
            'trending_patterns': trending,
            'user_message': user_message
        }

    def _format_case_for_ai(self, case) -> Dict[str, Any]:
        """Форматировать case для AI prompt"""
        return {
            'industry': case.organization_context.industry,
            'size': case.organization_context.size,
            'duration_days': case.metrics.total_duration_days,
            'success_patterns': case.success_patterns[:5],  # Top 5
            'lessons_learned': case.lessons_learned[:3],    # Top 3
            'key_metrics': {
                'processes': case.metrics.processes_count,
                'ai_usage': case.metrics.ai_usage_count,
                'challenges': case.metrics.challenges_encountered
            }
        }

    def format_for_llm_prompt(self, context: Dict[str, Any]) -> str:
        """
        Форматировать контекст в текстовый prompt для LLM

        Это финальный промпт который пойдет в Claude/GPT
        """

        workflow = context['workflow']
        org = context['organization']
        cases = context.get('similar_cases', [])
        benchmarks = context.get('benchmarks', {})
        comparison = context.get('comparison', {})

        prompt = f"""You are a BCM expert advisor helping with {workflow.get('module', 'workflow')}.

CURRENT SITUATION:
Stage: {workflow['current_state']}
Progress: {workflow['progress']:.0f}%
Time in current stage: {workflow['time_in_state'] / 3600:.1f} hours

Organization:
- Industry: {org['industry']}
- Size: {org['size']}
- BCM Maturity: {org.get('bcm_maturity', 'unknown')}

Current Data:
{self._format_workflow_data(workflow['data'])}

VALIDATION STATUS:
{" All requirements met" if workflow['is_valid'] else " Issues found:"}
{self._format_errors(workflow['validation_errors'])}

SIMILAR SUCCESSFUL CASES:
"""

        if cases:
            for i, case in enumerate(cases, 1):
                prompt += f"""
Case {i}: {case['industry']} ({case['size']})
- Completed in: {case['duration_days']} days
- What worked well:
{self._format_list(case['success_patterns'], prefix='  ')}
"""
        else:
            prompt += "No similar cases available yet.\n"

        if benchmarks.get('total_cases', 0) > 0:
            prompt += f"""
INDUSTRY BENCHMARKS ({benchmarks['total_cases']} similar organizations):
- Average duration: {benchmarks['duration']['avg_days']} days (you: {comparison.get('comparison', {}).get('duration', {}).get('current', 'N/A')} days)
- AI usage correlation: {benchmarks['ai_usage'].get('correlation_with_success', 0):.0%} success rate with high AI usage

Top practices in industry:
{self._format_list([p['pattern'] for p in benchmarks.get('top_success_patterns', [])[:5]], prefix='  •')}

Your progress: {comparison.get('comparison', {}).get('overall_assessment', 'N/A')}
"""

        if context.get('user_message'):
            prompt += f"""
USER QUESTION:
{context['user_message']}
"""
        else:
            prompt += """
USER NEEDS:
Proactive guidance on next steps
"""

        prompt += """
YOUR TASK:
1. Analyze the current situation vs. similar successful cases
2. Identify if user is on track or struggling
3. Provide specific, actionable advice
4. Suggest concrete next steps
5. Warn about common pitfalls from similar organizations

Be conversational, encouraging, and specific. Use examples from similar cases.
Do NOT be generic - reference actual data and patterns.
"""

        return prompt

    def _format_workflow_data(self, data: Dict[str, Any]) -> str:
        """Format workflow data for prompt"""
        lines = []
        for key, value in data.items():
            if isinstance(value, list):
                lines.append(f"- {key}: {len(value)} items")
            elif isinstance(value, dict):
                lines.append(f"- {key}: {len(value)} entries")
            else:
                lines.append(f"- {key}: {value}")
        return '\n'.join(lines) if lines else "No data yet"

    def _format_errors(self, errors: List[str]) -> str:
        """Format validation errors"""
        if not errors:
            return ""
        return '\n'.join(f"  • {error}" for error in errors)

    def _format_list(self, items: List[str], prefix: str = '•') -> str:
        """Format list with prefix"""
        if not items:
            return f"{prefix} None"
        return '\n'.join(f"{prefix} {item}" for item in items)
