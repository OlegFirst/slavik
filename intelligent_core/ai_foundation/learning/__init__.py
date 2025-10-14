"""
Self-Learning Module

Enables the system to learn from completed workflows and improve over time.

Components:
- Self-Learning Engine: Orchestrates learning process
- Pattern Extractor: Extracts patterns from workflow data
- Rule Generator: Generates new rules based on patterns
"""

from .self_learning_engine import SelfLearningEngine
from .pattern_extractor import PatternExtractor
from .rule_generator import RuleGenerator

__all__ = [
    'SelfLearningEngine',
    'PatternExtractor',
    'RuleGenerator',
]
