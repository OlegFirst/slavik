"""
Creative Zones System
======================

Extracted from: /Users/MD/AI-Platform-ISO/SESSION_SUMMARY.md
Source lines: 2726-2963
Date extracted: 2025-10-04

Description:
-----------
Creative Zones define where and how AI can exercise creativity within workflows.
Manages the balance between freedom and constraints - AI can choose HOW to
achieve goals, but not WHAT the goals are.

Features:
- Creativity levels (None, Low, Medium, High, Unrestricted)
- Allowed approaches and forbidden actions
- Context-aware constraints
- BIA-specific creative zones

Philosophy:
- Checkpoints = жесткая валидация, нет творчества
- Creative Zones = AI свободен выбирать КАК, но не ЧТО
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass


class CreativityLevel(Enum):
    NONE = "none"              # Строго детерминированная логика
    LOW = "low"                # Минимальная свобода
    MEDIUM = "medium"          # Умеренная свобода
    HIGH = "high"              # Высокая свобода
    UNRESTRICTED = "unrestricted"  # Полная свобода


@dataclass
class CreativeZone:
    """Зона где AI может быть creative"""
    zone_id: str
    name: str
    description: str
    stage: str
    creativity_level: CreativityLevel
    allowed_approaches: List[str]
    forbidden_actions: List[str]
    guidance: str
    examples: List[str]


class CreativeZonesManager:
    """
    Управление творческими зонами для AI

    Philosophy:
    - Checkpoints = жесткая валидация, нет творчества
    - Creative Zones = AI свободен выбирать КАК, но не ЧТО
    """

    def __init__(self):
        self.zones: Dict[str, CreativeZone] = {}

    def register_zone(self, zone: CreativeZone):
        """Зарегистрировать creative zone"""
        self.zones[zone.zone_id] = zone

    def is_creative_zone(self, stage: str, action: str) -> bool:
        """Проверить является ли это creative zone"""
        for zone in self.zones.values():
            if zone.stage == stage:
                return True
        return False

    def get_creative_guidance(
        self,
        stage: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Получить guidance для creative zone"""
        zone = next(
            (z for z in self.zones.values() if z.stage == stage),
            None
        )

        if not zone:
            return None

        return {
            'creativity_level': zone.creativity_level.value,
            'allowed_approaches': zone.allowed_approaches,
            'forbidden_actions': zone.forbidden_actions,
            'guidance': zone.guidance,
            'examples': zone.examples,
            'constraints': self._get_contextual_constraints(zone, context)
        }

    def _get_contextual_constraints(
        self,
        zone: CreativeZone,
        context: Dict[str, Any]
    ) -> List[str]:
        """Контекстные ограничения"""
        constraints = []

        # Базовые ограничения
        if zone.creativity_level == CreativityLevel.LOW:
            constraints.append("Stay close to established patterns")
            constraints.append("Minimal deviation from standards")

        elif zone.creativity_level == CreativityLevel.MEDIUM:
            constraints.append("Balance innovation with proven approaches")
            constraints.append("Justify any unconventional recommendations")

        elif zone.creativity_level == CreativityLevel.HIGH:
            constraints.append("Feel free to explore novel approaches")
            constraints.append("Consider multiple perspectives")

        # Контекстные ограничения
        if context.get('org_maturity') == 'basic':
            constraints.append("Keep recommendations simple and practical")

        if context.get('regulatory_requirements'):
            constraints.append("Ensure all suggestions meet regulatory requirements")

        return constraints


class BIACreativeZones:
    """Creative zones для BIA workflow"""

    @staticmethod
    def get_all_zones() -> List[CreativeZone]:
        return [
            CreativeZone(
                zone_id="bia_cz_001",
                name="Process Suggestion",
                description="AI suggests typical processes for industry",
                stage="identify_processes",
                creativity_level=CreativityLevel.MEDIUM,
                allowed_approaches=[
                    "Industry benchmarking",
                    "Similar organization analysis",
                    "Regulatory requirement mapping",
                    "Best practice templates"
                ],
                forbidden_actions=[
                    "Create processes without user confirmation",
                    "Modify existing processes without asking",
                    "Make up fictitious processes"
                ],
                guidance="""
You can be creative in suggesting processes, but must:
- Base suggestions on real industry patterns
- Explain WHY each process is relevant
- Allow user to accept/reject each suggestion
- Adapt suggestions to organization context
""",
                examples=[
                    "For healthcare: Emergency Department, Patient Records, Pharmacy",
                    "For finance: Transaction Processing, Customer Accounts, Compliance Reporting"
                ]
            ),

            CreativeZone(
                zone_id="bia_cz_002",
                name="Impact Analysis",
                description="AI analyzes business impact creatively",
                stage="assess_impact",
                creativity_level=CreativityLevel.HIGH,
                allowed_approaches=[
                    "Multiple assessment frameworks (quantitative + qualitative)",
                    "Scenario analysis",
                    "Comparative analysis",
                    "Cascading impact modeling",
                    "Analogies from similar industries"
                ],
                forbidden_actions=[
                    "Invent financial data",
                    "Override user-provided impact data",
                    "Make definitive claims without data"
                ],
                guidance="""
You have HIGH creative freedom in impact analysis:
- Use multiple frameworks (FMEA, scenario-based, comparative)
- Consider direct AND indirect impacts
- Explore cascading effects
- Use analogies and case studies
- BUT: Always distinguish between:
  - Data-driven conclusions (when you have data)
  - Educated estimates (when inferring)
  - Hypothetical scenarios (when exploring possibilities)
""",
                examples=[
                    "If Patient Records unavailable: direct impact = care quality, indirect = legal liability, cascading = reputation damage",
                    "Use case studies: 'Hospital X lost $2M when similar process failed'"
                ]
            ),

            CreativeZone(
                zone_id="bia_cz_003",
                name="RTO Recommendation",
                description="AI recommends RTO with reasoning",
                stage="determine_rto",
                creativity_level=CreativityLevel.MEDIUM,
                allowed_approaches=[
                    "Industry benchmarks",
                    "Impact-based calculation",
                    "Cost-benefit analysis",
                    "Regulatory requirements",
                    "Similar case analysis"
                ],
                forbidden_actions=[
                    "Recommend RTO without justification",
                    "Ignore regulatory minimums",
                    "Disregard financial impact data"
                ],
                guidance="""
Balance creativity with data:
- Start with calculated recommendation (impact + industry norm)
- Explain reasoning step-by-step
- Present alternatives with trade-offs
- Reference similar organizations
- Acknowledge uncertainty when present
""",
                examples=[
                    "Tier 1 process + high financial impact → RTO 2-4h",
                    "Reference: 'Similar healthcare orgs use 4h RTO for this'"
                ]
            ),

            CreativeZone(
                zone_id="bia_cz_004",
                name="Dependency Discovery",
                description="AI helps discover hidden dependencies",
                stage="analyze_dependencies",
                creativity_level=CreativityLevel.HIGH,
                allowed_approaches=[
                    "Ask probing questions",
                    "Suggest typical dependencies",
                    "Map dependency chains",
                    "Identify hidden interdependencies",
                    "Use process mining concepts"
                ],
                forbidden_actions=[
                    "Assert dependencies without asking",
                    "Ignore user corrections"
                ],
                guidance="""
Be a detective - help user discover what they might miss:
- Ask: "Who needs to be available?", "What systems are critical?", "What data is required?"
- Suggest typical dependencies: "Most similar processes depend on X, Y, Z - do you?"
- Explore chains: "If A fails, what else is affected?"
- Highlight non-obvious: "Have you considered vendor dependencies?"
""",
                examples=[
                    "Emergency Dept depends on: physicians, nurses, EMR system, pharmacy, labs, imaging",
                    "Hidden: also depends on electricity, HVAC for medication storage, backup power"
                ]
            )
        ]
