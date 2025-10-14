"""
Cross-Module Learning Engine

Enables learning between different BCM modules:
- BIA lessons → Risk mitigation
- Planning strategies → Validation KPIs
- Response patterns → Recovery procedures
"""

from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class CrossModuleLearning:
    """
    Cross-module learning engine

    Finds patterns and lessons across BCM modules to improve
    decision-making and recommendations.
    """

    # Module relationships for cross-learning
    MODULE_RELATIONSHIPS = {
        'bia': ['risk', 'planning', 'response'],
        'risk': ['bia', 'planning', 'compliance'],
        'planning': ['bia', 'risk', 'validation'],
        'response': ['bia', 'planning', 'validation'],
        'validation': ['planning', 'response', 'compliance'],
        'compliance': ['risk', 'validation', 'governance'],
        'governance': ['compliance', 'planning', 'documents'],
        'documents': ['governance', 'compliance', 'learning'],
        'learning': ['documents', 'bia', 'planning'],
    }

    # ISO clause relationships
    ISO_RELATIONSHIPS = {
        '8.2.2': ['8.2.3', '8.3'],     # BIA → Risk → Planning
        '8.2.3': ['8.2.2', '8.3'],     # Risk → BIA → Planning
        '8.3': ['8.2.2', '8.4'],       # Planning → BIA → Plans
        '8.4': ['8.3', '8.4.5'],       # Plans → Planning → Response
        '8.4.5': ['8.4', '8.4.6'],     # Response → Plans → Validation
        '8.4.6': ['8.4.5', '9.2'],     # Validation → Response → Compliance
        '9.2': ['8.4.6', '10.1'],      # Compliance → Validation → Review
        '10.1': ['9.2', '10.2'],       # Review → Compliance → Improvement
    }

    def __init__(self, storage_adapter):
        """
        Initialize cross-module learning

        Args:
            storage_adapter: Storage adapter for accessing cases
        """
        self.storage = storage_adapter

    def get_related_modules(self, module: str) -> List[str]:
        """
        Get modules related to current module

        Args:
            module: Current module name

        Returns:
            List of related module names
        """
        return self.MODULE_RELATIONSHIPS.get(module, [])

    def get_related_iso_clauses(self, iso_clause: str) -> List[str]:
        """
        Get ISO clauses related to current clause

        Args:
            iso_clause: Current ISO clause

        Returns:
            List of related ISO clauses
        """
        return self.ISO_RELATIONSHIPS.get(iso_clause, [])

    async def find_cross_module_cases(
        self,
        current_module: str,
        context: Dict[str, Any],
        limit: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find relevant cases from OTHER modules

        Args:
            current_module: Current module
            context: Current workflow context
            limit: Max cases per module

        Returns:
            {
                "risk": [case1, case2, ...],
                "planning": [case3, case4, ...],
                ...
            }
        """
        related_modules = self.get_related_modules(current_module)

        cross_module_cases = {}

        for module in related_modules:
            # Find similar cases in other module
            cases = await self.storage.find_similar_cases(
                module=module,
                org_context=context.get('org_context', {}),
                current_stage=context.get('current_stage', ''),
                limit=limit,
                tenant_id=None  # Cross-tenant learning (anonymized)
            )

            if cases:
                cross_module_cases[module] = cases

        logger.info(
            "cross_module_learning.found_cases",
            current_module=current_module,
            related_modules=len(cross_module_cases),
            total_cases=sum(len(cases) for cases in cross_module_cases.values())
        )

        return cross_module_cases

    def extract_cross_module_insights(
        self,
        cross_module_cases: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Extract actionable insights from cross_module cases

        Args:
            cross_module_cases: Cases from related modules

        Returns:
            {
                "patterns": [...],
                "recommendations": [...],
                "lessons_learned": [...]
            }
        """
        patterns = []
        recommendations = []
        lessons_learned = []

        for module, cases in cross_module_cases.items():
            for case in cases:
                # Extract patterns
                if 'success_patterns' in case:
                    for pattern in case['success_patterns']:
                        patterns.append({
                            'source_module': module,
                            'pattern': pattern,
                            'relevance': 'high' if case.get('success') else 'medium'
                        })

                # Extract lessons
                if 'lessons_learned' in case:
                    for lesson in case['lessons_learned']:
                        lessons_learned.append({
                            'source_module': module,
                            'lesson': lesson,
                            'applicability': 'cross-module'
                        })

        # Generate recommendations
        if patterns:
            recommendations.append({
                'type': 'apply_pattern',
                'description': f'Similar patterns found in {len(set(c["source_module"] for c in patterns))} related modules',
                'patterns': patterns[:5]  # Top 5
            })

        return {
            'patterns': patterns,
            'recommendations': recommendations,
            'lessons_learned': lessons_learned
        }
