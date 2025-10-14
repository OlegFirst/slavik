# intelligent-core/ace-engine/ace_engine.py

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ACEEngine:
    """
    Agentic Context Engineering Engine

    Implements the ACE framework with three specialized components:
    1. Generator - Create context with evolving playbook
    2. Reflector - Analyze trajectory and identify insights
    3. Curator - Update playbook incrementally
    """

    def __init__(self):
        """Initialize ACE Engine"""
        self.generator = ACEGenerator()
        self.reflector = ACEReflector()
        self.curator = ACECurator()

        # Playbooks storage (per task type)
        self.playbooks: Dict[str, Dict[str, Any]] = {}

        logger.info("Initialized ACE Engine")

    # =========================================================================
    # 1. GENERATOR Component
    # =========================================================================

    async def generate_context(
        self,
        task: str,
        base_context: Dict[str, Any],
        playbook: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate enhanced context using evolving playbook

        Args:
            task: Task type (e.g., "scenario_generation_L1")
            base_context: Base context dict
            playbook: Current playbook (strategies, patterns, knowledge)
            **kwargs: Additional context (domain_knowledge, etc.)

        Returns:
            Enhanced context dict
        """
        if playbook is None:
            playbook = self.get_playbook(task)

        # Generator creates context with playbook
        enhanced_context = await self.generator.generate(
            task=task,
            base_context=base_context,
            playbook=playbook,
            **kwargs
        )

        logger.info(
            f"Generated context for {task}: "
            f"{len(enhanced_context)} keys, "
            f"playbook_size={len(playbook)}"
        )

        return enhanced_context

    # =========================================================================
    # 2. REFLECTOR Component
    # =========================================================================

    async def reflect_on_trajectory(
        self,
        task: str,
        trajectory: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze trajectory and identify insights

        Args:
            task: Task type
            trajectory: Execution trajectory (input, output, metrics)

        Returns:
            Dict with insights:
                - successful_strategies: List[str]
                - failed_strategies: List[str]
                - new_patterns: List[Dict]
                - improvements: List[str]
        """
        insights = await self.reflector.reflect(
            task=task,
            trajectory=trajectory
        )

        logger.info(
            f"Reflected on trajectory for {task}: "
            f"{len(insights.get('successful_strategies', []))} successful, "
            f"{len(insights.get('new_patterns', []))} new patterns"
        )

        return insights

    # =========================================================================
    # 3. CURATOR Component
    # =========================================================================

    async def curate_playbook(
        self,
        task: str,
        current_playbook: Dict[str, Any],
        insights: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update playbook incrementally (no context collapse!)

        Args:
            task: Task type
            current_playbook: Current playbook
            insights: Insights from Reflector
            **kwargs: Additional curation params

        Returns:
            Updated playbook
        """
        # Extract preserve_knowledge from kwargs to avoid passing it twice
        preserve_knowledge = kwargs.pop("preserve_knowledge", True)

        updated_playbook = await self.curator.curate(
            task=task,
            current_playbook=current_playbook,
            insights=insights,
            preserve_knowledge=preserve_knowledge,
            **kwargs
        )

        # Store updated playbook
        self.playbooks[task] = updated_playbook

        logger.info(
            f"Curated playbook for {task}: "
            f"size_before={len(current_playbook)}, "
            f"size_after={len(updated_playbook)}"
        )

        return updated_playbook

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_playbook(self, task: str) -> Dict[str, Any]:
        """Get current playbook for task"""
        return self.playbooks.get(task, {
            "strategies": [],
            "patterns": [],
            "domain_knowledge": [],
            "successful_examples": [],
            "failed_examples": []
        })

    def get_playbook_stats(self, task: str) -> Dict[str, Any]:
        """Get playbook statistics"""
        playbook = self.get_playbook(task)

        return {
            "task": task,
            "strategies_count": len(playbook.get("strategies", [])),
            "patterns_count": len(playbook.get("patterns", [])),
            "knowledge_items": len(playbook.get("domain_knowledge", [])),
            "examples": {
                "successful": len(playbook.get("successful_examples", [])),
                "failed": len(playbook.get("failed_examples", []))
            }
        }


class ACEGenerator:
    """Generator component - creates context with playbook"""

    async def generate(
        self,
        task: str,
        base_context: Dict[str, Any],
        playbook: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate enhanced context"""

        # Combine base context with playbook strategies
        enhanced_context = {
            **base_context,
            "playbook_strategies": playbook.get("strategies", []),
            "known_patterns": playbook.get("patterns", []),
            "domain_expertise": playbook.get("domain_knowledge", []),
            "successful_examples": playbook.get("successful_examples", [])[:5],  # Top 5
            **kwargs
        }

        return enhanced_context


class ACEReflector:
    """Reflector component - analyzes trajectory"""

    async def reflect(
        self,
        task: str,
        trajectory: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze trajectory and extract insights"""

        insights = {
            "successful_strategies": [],
            "failed_strategies": [],
            "new_patterns": [],
            "improvements": []
        }

        # Analyze trajectory
        # (In production: use LLM to analyze)

        # Example: Check if validation passed
        if trajectory.get("validation", {}).get("approved"):
            insights["successful_strategies"].append(
                "Community validation approved"
            )

        # Example: Check effectiveness
        effectiveness = trajectory.get("effectiveness", 0)
        if effectiveness > 0.8:
            insights["successful_strategies"].append(
                f"High effectiveness achieved: {effectiveness:.2%}"
            )

        # Example: Detect new pattern
        if trajectory.get("pattern_detected"):
            insights["new_patterns"].append({
                "type": trajectory["pattern_type"],
                "confidence": trajectory["pattern_confidence"]
            })

        return insights


class ACECurator:
    """Curator component - updates playbook"""

    async def curate(
        self,
        task: str,
        current_playbook: Dict[str, Any],
        insights: Dict[str, Any],
        preserve_knowledge: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Curate playbook incrementally"""

        # Start with current playbook (preserve knowledge!)
        updated_playbook = {
            "strategies": current_playbook.get("strategies", []).copy(),
            "patterns": current_playbook.get("patterns", []).copy(),
            "domain_knowledge": current_playbook.get("domain_knowledge", []).copy(),
            "successful_examples": current_playbook.get("successful_examples", []).copy(),
            "failed_examples": current_playbook.get("failed_examples", []).copy()
        }

        # Add successful strategies
        for strategy in insights.get("successful_strategies", []):
            if strategy not in updated_playbook["strategies"]:
                updated_playbook["strategies"].append(strategy)

        # Remove failed strategies
        for strategy in insights.get("failed_strategies", []):
            if strategy in updated_playbook["strategies"]:
                updated_playbook["strategies"].remove(strategy)

        # Add new patterns
        for pattern in insights.get("new_patterns", []):
            updated_playbook["patterns"].append(pattern)

        # Add improvements to domain knowledge
        for improvement in insights.get("improvements", []):
            if improvement not in updated_playbook["domain_knowledge"]:
                updated_playbook["domain_knowledge"].append(improvement)

        # Limit size (keep most relevant)
        if len(updated_playbook["strategies"]) > 50:
            updated_playbook["strategies"] = updated_playbook["strategies"][-50:]

        if len(updated_playbook["patterns"]) > 100:
            updated_playbook["patterns"] = updated_playbook["patterns"][-100:]

        return updated_playbook


# Global instance
_ace_engine: Optional[ACEEngine] = None


def get_ace_engine() -> ACEEngine:
    """Get global ACE Engine instance"""
    global _ace_engine
    if _ace_engine is None:
        _ace_engine = ACEEngine()
    return _ace_engine
