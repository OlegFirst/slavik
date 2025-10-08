"""
Reaction Layer - Rapid Automated Response System

This layer handles automated reactions to system events:
- Level 1: Instant reflexes (<10s)
- Level 2: Quick responses (<1min)
- Level 3: Escalation to Brain

Components:
- ReactionRulesEngine: Classifies events and determines reaction level
- ActionExecutor: Executes automated actions
- EscalationManager: Escalates to Brain when needed
"""

from .reaction_rules_engine import ReactionRulesEngine, ReactionLevel
from .action_executor import ActionExecutor
from .escalation_manager import EscalationManager

__all__ = [
    'ReactionRulesEngine',
    'ReactionLevel',
    'ActionExecutor',
    'EscalationManager',
]
