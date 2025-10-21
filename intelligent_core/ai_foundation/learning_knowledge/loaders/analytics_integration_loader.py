"""
Analytics Integration Loader
============================

Загружает результаты работы analytics-specialist в learning-knowledge систему:

**Источник данных:**
`/infrastructure/AI-office-infrastructure/analytics-specialist/reports/`

**Что загружается:**
1. State Machine → Knowledge about system states
2. Behavioral Patterns → Learned user behaviors
3. Edge Cases → Known failure scenarios
4. Module Analyses → Domain expertise per module
5. Generated Rules → Business logic patterns

**Интеграция:**
- Результаты анализа → knowledge base
- Паттерны → training data для self-learning
- Edge cases → negative examples для ML
- Module expertise → domain knowledge graph

**Usage:**
    from intelligent_core.ai_foundation.learning_knowledge.loaders.analytics_integration_loader import AnalyticsIntegrationLoader

    loader = AnalyticsIntegrationLoader()

    # Load latest analysis
    await loader.load_latest_analysis()

    # Load all historical analyses
    await loader.load_all_analyses()
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsKnowledge:
    """Knowledge extracted from analytics"""
    source: str  # "state_machine", "behavioral_patterns", "edge_cases", "module_analysis"
    content_type: str
    data: Dict[str, Any]
    extracted_at: str
    confidence: float
    metadata: Dict[str, Any]


class AnalyticsIntegrationLoader:
    """
    Loads analytics results into learning-knowledge system

    Converts:
    - State machines → System behavior knowledge
    - Patterns → Training examples
    - Edge cases → Negative examples
    - Module analyses → Domain expertise
    """

    def __init__(
        self,
        analytics_reports_dir: Optional[Path] = None,
        knowledge_base_dir: Optional[Path] = None
    ):
        # Paths
        project_root = Path(__file__).parent.parent.parent.parent.parent
        self.analytics_dir = analytics_reports_dir or (
            project_root / "infrastructure" / "AI-office-infrastructure" / "analytics-specialist" / "reports"
        )
        self.knowledge_dir = knowledge_base_dir or (
            Path(__file__).parent.parent / "knowledge" / "analytics_learned"
        )
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"AnalyticsIntegrationLoader initialized")
        logger.info(f"  Source: {self.analytics_dir}")
        logger.info(f"  Target: {self.knowledge_dir}")

    async def load_latest_analysis(self) -> Dict[str, AnalyticsKnowledge]:
        """
        Load latest analysis results into knowledge base

        Returns:
            Dict mapping source type to extracted knowledge
        """
        logger.info("Loading latest analysis results...")

        knowledge = {}

        # 1. Load State Machine
        state_machine_file = self.analytics_dir / "state_machine.json"
        if state_machine_file.exists():
            sm_knowledge = await self._load_state_machine(state_machine_file)
            knowledge["state_machine"] = sm_knowledge
            logger.info(f"   Loaded state machine ({len(sm_knowledge.data['states'])} states)")

        # 2. Load Behavioral Patterns
        patterns_file = self.analytics_dir / "behavioral_patterns.json"
        if patterns_file.exists():
            patterns_knowledge = await self._load_behavioral_patterns(patterns_file)
            knowledge["behavioral_patterns"] = patterns_knowledge
            logger.info(f"   Loaded behavioral patterns ({len(patterns_knowledge.data['patterns'])} patterns)")

        # 3. Load Edge Cases
        edge_cases_file = self.analytics_dir / "edge_cases.json"
        if edge_cases_file.exists():
            edge_knowledge = await self._load_edge_cases(edge_cases_file)
            knowledge["edge_cases"] = edge_knowledge
            logger.info(f"   Loaded edge cases ({len(edge_knowledge.data['cases'])} cases)")

        # 4. Load Module Analyses
        module_analysis_dir = self.analytics_dir / "module_analysis"
        if module_analysis_dir.exists():
            modules_knowledge = await self._load_module_analyses(module_analysis_dir)
            knowledge["module_analyses"] = modules_knowledge
            logger.info(f"   Loaded module analyses ({len(modules_knowledge.data['modules'])} modules)")

        # 5. Save to knowledge base
        await self._save_to_knowledge_base(knowledge)

        logger.info(f" Latest analysis loaded: {len(knowledge)} knowledge types")
        return knowledge

    async def load_all_analyses(self) -> List[Dict[str, AnalyticsKnowledge]]:
        """
        Load all historical analyses for training

        Useful for:
        - Training ML models on historical patterns
        - Trend analysis (how system evolved)
        - Knowledge accumulation
        """
        logger.info("Loading ALL historical analyses...")

        all_knowledge = []

        # Find all pipeline reports
        pipeline_reports = sorted(self.analytics_dir.glob("pipeline_report_*.json"))

        for report_file in pipeline_reports:
            logger.info(f"  Loading report: {report_file.name}")

            try:
                with open(report_file) as f:
                    report = json.load(f)

                # Extract timestamp from report
                timestamp = report["pipeline_run"]["started_at"]

                # Load corresponding analysis files
                # (They should exist in same directory with same timestamp prefix)
                knowledge = await self._load_analysis_by_timestamp(timestamp)

                all_knowledge.append({
                    "timestamp": timestamp,
                    "knowledge": knowledge
                })

            except Exception as e:
                logger.error(f"   Failed to load {report_file.name}: {e}")

        logger.info(f" Loaded {len(all_knowledge)} historical analyses")
        return all_knowledge

    # === Loading Methods ===

    async def _load_state_machine(self, file_path: Path) -> AnalyticsKnowledge:
        """Load state machine knowledge"""
        with open(file_path) as f:
            data = json.load(f)

        # Extract key insights
        states = data.get("states", {})
        transitions = data.get("transitions", [])

        # Convert to knowledge format
        knowledge_data = {
            "states": states,
            "transitions": transitions,
            "total_states": len(states),
            "total_transitions": len(transitions),
            "insights": self._extract_state_machine_insights(states, transitions)
        }

        return AnalyticsKnowledge(
            source="state_machine",
            content_type="system_behavior",
            data=knowledge_data,
            extracted_at=datetime.now().isoformat(),
            confidence=0.95,  # High confidence from code analysis
            metadata={
                "file": str(file_path),
                "analysis_type": "static"
            }
        )

    def _extract_state_machine_insights(
        self,
        states: Dict[str, Any],
        transitions: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract insights from state machine"""
        insights = []

        # Count states by type
        journey_states = [s for s in states.keys() if "journey" in s]
        incident_states = [s for s in states.keys() if "incident" in s]

        insights.append(f"System has {len(journey_states)} journey states")
        insights.append(f"System has {len(incident_states)} incident states")

        # Find critical transitions
        critical_transitions = [
            t for t in transitions
            if t.get("priority") == "critical"
        ]

        if critical_transitions:
            insights.append(f"{len(critical_transitions)} critical transitions identified")

        return insights

    async def _load_behavioral_patterns(self, file_path: Path) -> AnalyticsKnowledge:
        """Load behavioral patterns knowledge"""
        with open(file_path) as f:
            data = json.load(f)

        # Patterns are list of pattern objects
        patterns = data if isinstance(data, list) else []

        # Categorize by frequency
        high_freq = [p for p in patterns if p.get("frequency", 0) > 100]
        medium_freq = [p for p in patterns if 10 < p.get("frequency", 0) <= 100]

        knowledge_data = {
            "patterns": patterns,
            "total_patterns": len(patterns),
            "high_frequency_patterns": len(high_freq),
            "medium_frequency_patterns": len(medium_freq),
            "insights": self._extract_pattern_insights(patterns)
        }

        return AnalyticsKnowledge(
            source="behavioral_patterns",
            content_type="user_behavior",
            data=knowledge_data,
            extracted_at=datetime.now().isoformat(),
            confidence=0.85,  # Medium-high from event observation
            metadata={
                "file": str(file_path),
                "analysis_type": "dynamic"
            }
        )

    def _extract_pattern_insights(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Extract insights from patterns"""
        insights = []

        # Find most common pattern
        if patterns:
            top_pattern = max(patterns, key=lambda p: p.get("frequency", 0))
            insights.append(
                f"Most common: {top_pattern.get('description', 'Unknown')} "
                f"({top_pattern.get('frequency', 0)} occurrences)"
            )

        # Identify user flow patterns
        user_flows = [p for p in patterns if p.get("pattern_type") == "user_flow"]
        if user_flows:
            insights.append(f"{len(user_flows)} user flow patterns identified")

        return insights

    async def _load_edge_cases(self, file_path: Path) -> AnalyticsKnowledge:
        """Load edge cases knowledge"""
        with open(file_path) as f:
            data = json.load(f)

        cases = data if isinstance(data, list) else []

        # Categorize by severity
        critical = [c for c in cases if c.get("severity") == "critical"]
        high = [c for c in cases if c.get("severity") == "high"]

        knowledge_data = {
            "cases": cases,
            "total_cases": len(cases),
            "critical_cases": len(critical),
            "high_priority_cases": len(high),
            "insights": self._extract_edge_case_insights(cases)
        }

        return AnalyticsKnowledge(
            source="edge_cases",
            content_type="failure_scenarios",
            data=knowledge_data,
            extracted_at=datetime.now().isoformat(),
            confidence=0.90,
            metadata={
                "file": str(file_path),
                "analysis_type": "static"
            }
        )

    def _extract_edge_case_insights(self, cases: List[Dict[str, Any]]) -> List[str]:
        """Extract insights from edge cases"""
        insights = []

        # Count by severity
        critical_count = len([c for c in cases if c.get("severity") == "critical"])
        if critical_count > 0:
            insights.append(f"{critical_count} critical edge cases need attention")

        # Common mitigation strategies
        mitigations = set()
        for case in cases:
            mitigation = case.get("mitigation", "")
            if "validation" in mitigation.lower():
                mitigations.add("validation")
            elif "saga" in mitigation.lower():
                mitigations.add("saga_pattern")

        if mitigations:
            insights.append(f"Mitigation strategies: {', '.join(mitigations)}")

        return insights

    async def _load_module_analyses(self, module_dir: Path) -> AnalyticsKnowledge:
        """Load all module analyses"""
        modules = []

        # Load all module analysis JSON files
        for json_file in module_dir.glob("*_analysis.json"):
            try:
                with open(json_file) as f:
                    module_data = json.load(f)
                    modules.append(module_data)
            except Exception as e:
                logger.error(f"Failed to load {json_file.name}: {e}")

        # Extract domain expertise
        domain_expertise = {}
        for module in modules:
            domain = module.get("domain_knowledge", {}).get("domain", "general")
            expertise_level = module.get("expertise_level", "beginner")

            if domain not in domain_expertise:
                domain_expertise[domain] = []

            domain_expertise[domain].append({
                "module": module.get("module_name"),
                "level": expertise_level,
                "concepts": module.get("domain_knowledge", {}).get("concepts", [])
            })

        knowledge_data = {
            "modules": modules,
            "total_modules": len(modules),
            "domain_expertise": domain_expertise,
            "insights": self._extract_module_insights(modules, domain_expertise)
        }

        return AnalyticsKnowledge(
            source="module_analyses",
            content_type="domain_expertise",
            data=knowledge_data,
            extracted_at=datetime.now().isoformat(),
            confidence=0.95,
            metadata={
                "directory": str(module_dir),
                "analysis_type": "comprehensive"
            }
        )

    def _extract_module_insights(
        self,
        modules: List[Dict[str, Any]],
        domain_expertise: Dict[str, List[Dict]]
    ) -> List[str]:
        """Extract insights from module analyses"""
        insights = []

        # Count expert modules
        expert_modules = [
            m for m in modules
            if m.get("expertise_level") == "expert"
        ]

        insights.append(f"{len(expert_modules)} expert modules identified")

        # Dominant domains
        if domain_expertise:
            top_domain = max(domain_expertise.items(), key=lambda x: len(x[1]))
            insights.append(f"Strongest domain: {top_domain[0]} ({len(top_domain[1])} modules)")

        # Total scenarios
        total_scenarios = sum(
            len(m.get("ai_extended_scenarios", [])) for m in modules
        )
        insights.append(f"{total_scenarios} total usage scenarios across all modules")

        return insights

    async def _load_analysis_by_timestamp(self, timestamp: str) -> Dict[str, AnalyticsKnowledge]:
        """Load analysis files by timestamp"""
        # TODO: Implement loading by timestamp
        # For now, just load latest
        return await self.load_latest_analysis()

    # === Saving Methods ===

    async def _save_to_knowledge_base(self, knowledge: Dict[str, AnalyticsKnowledge]):
        """Save knowledge to knowledge base"""

        # 1. Save as JSON (structured data)
        json_file = self.knowledge_dir / f"analytics_knowledge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        json_data = {
            source: asdict(know) for source, know in knowledge.items()
        }

        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)

        logger.info(f"   Saved to: {json_file}")

        # 2. Save as Markdown (human-readable)
        md_file = self.knowledge_dir / f"analytics_knowledge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        md_content = self._generate_markdown_summary(knowledge)

        with open(md_file, 'w') as f:
            f.write(md_content)

        logger.info(f"   Saved to: {md_file}")

        # 3. Update knowledge index
        await self._update_knowledge_index(knowledge)

    def _generate_markdown_summary(self, knowledge: Dict[str, AnalyticsKnowledge]) -> str:
        """Generate markdown summary of knowledge"""

        md = f"""# Analytics Knowledge Summary

**Generated:** {datetime.now().isoformat()}
**Sources:** {len(knowledge)}

---

"""

        for source, know in knowledge.items():
            md += f"""## {source.upper().replace('_', ' ')}

**Type:** {know.content_type}
**Confidence:** {know.confidence}

### Key Data

{json.dumps(know.data, indent=2)}

### Insights

{chr(10).join(f"- {insight}" for insight in know.data.get('insights', []))}

---

"""

        return md

    async def _update_knowledge_index(self, knowledge: Dict[str, AnalyticsKnowledge]):
        """Update knowledge index for fast lookup"""

        index_file = self.knowledge_dir / "KNOWLEDGE_INDEX.json"

        # Load existing index
        if index_file.exists():
            with open(index_file) as f:
                index = json.load(f)
        else:
            index = {
                "entries": [],
                "last_updated": None
            }

        # Add new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "sources": list(knowledge.keys()),
            "files": [
                str(f.name) for f in self.knowledge_dir.glob(f"analytics_knowledge_{datetime.now().strftime('%Y%m%d')}*")
            ]
        }

        index["entries"].append(entry)
        index["last_updated"] = datetime.now().isoformat()

        # Save updated index
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)

        logger.info(f"   Updated knowledge index")

    # === Query Methods ===

    async def query_knowledge(
        self,
        source: str,
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Query knowledge base

        Args:
            source: "state_machine", "behavioral_patterns", "edge_cases", "module_analyses"
            query: Search query (e.g., "critical edge cases")

        Returns:
            List of matching knowledge items
        """
        # TODO: Implement semantic search using embeddings
        # For now, simple keyword search

        results = []

        # Load all knowledge files
        for knowledge_file in self.knowledge_dir.glob("analytics_knowledge_*.json"):
            with open(knowledge_file) as f:
                data = json.load(f)

            if source in data:
                know = data[source]

                # Simple keyword matching
                if query.lower() in json.dumps(know).lower():
                    results.append(know)

        return results


async def main():
    """Test loader"""
    loader = AnalyticsIntegrationLoader()

    # Load latest
    knowledge = await loader.load_latest_analysis()

    print("\n Loaded knowledge:")
    for source, know in knowledge.items():
        print(f"  - {source}: {len(know.data)} items")

    # Query example
    # results = await loader.query_knowledge("edge_cases", "critical")
    # print(f"\n Query results: {len(results)}")


if __name__ == "__main__":
    asyncio.run(main())
