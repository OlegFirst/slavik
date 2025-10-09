"""
🔄 Enable PDCA for Workflow Intelligence

Это стартовый скрипт чтобы включить PDCA правила для всех workflows.

Usage:
    # Option 1: Run this script once
    python enable_pdca.py

    # Option 2: Import in main.py
    from workflow_intelligence.enable_pdca import enable_all

    enable_all()
"""

import logging
from .core.pdca_rules import pdca_rules, enable_pdca_for_workflow_engine
from .core import workflow_engine

logger = logging.getLogger(__name__)


def enable_all():
    """
    Enable PDCA для всей Workflow Intelligence системы

    Эта функция:
    1. Подключает PDCA rules к Workflow Engine
    2. Интегрирует с существующими модулями (опционально)
    """

    logger.info("🔄 Enabling PDCA for Workflow Intelligence...")

    # 1. Enable PDCA rules
    enable_pdca_for_workflow_engine(workflow_engine)

    # 2. Try to integrate with other modules (optional)
    try:
        from intelligent_core.collective.services.case_library import CaseLibrary
        # pdca_rules.integrate_case_library(case_library_instance)
        logger.info("✅ Case Library integration available")
    except ImportError:
        logger.info("⚠️  Case Library not available (optional)")

    try:
        from intelligent_core.ai_foundation.learning_knowledge import KnowledgeBase
        # pdca_rules.integrate_knowledge_base(knowledge_base_instance)
        logger.info("✅ Knowledge Base integration available")
    except ImportError:
        logger.info("⚠️  Knowledge Base not available (optional)")

    try:
        from intelligent_core.ai_foundation.learning_knowledge import PatternDetector
        # pdca_rules.integrate_pattern_detector(pattern_detector_instance)
        logger.info("✅ Pattern Detector integration available")
    except ImportError:
        logger.info("⚠️  Pattern Detector not available (optional)")

    logger.info("✅ PDCA enabled successfully!")
    logger.info("   All workflows will now automatically go through PDCA cycles")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Enable PDCA
    enable_all()

    logger.info("PDCA rules are now active!")
    logger.info("Every workflow will:")
    logger.info("  • PLAN: Get AI recommendations from past cases")
    logger.info("  • DO: Track execution")
    logger.info("  • CHECK: Validate vs benchmarks")
    logger.info("  • ACT: Extract lessons & improve")
