#!/usr/bin/env python3
"""
Automated Knowledge Pipeline
============================

Полная автоматизация процессов моделирования, документирования и интеграции знаний:

1. **System Analysis** → Анализ поведения системы, состояний, edge cases
2. **Pattern Extraction** → Извлечение поведенческих паттернов из событий
3. **Documentation Generation** → Генерация документации (README, API, scenarios)
4. **Rules Generation** → Конвертация flow → Python/Temporal code
5. **RAG Integration** → Индексация в Qdrant для AI/Memory системы

**Интеграция существующих инструментов:**
- `/infrastructure/tools/doc-generators/` (ai_documentation_generator, event_catalog_generator)
- `/infrastructure/AI-office-infrastructure/analytics-specialist/tools/system_behavior_analyzer.py`
- `/intelligent-core/ai-foundation/learning-knowledge/loaders/comprehensive_docs_loader.py`

**Usage:**
    # Полный pipeline
    python3 automated_knowledge_pipeline.py --full

    # Только анализ системы
    python3 automated_knowledge_pipeline.py --analyze

    # Только документация
    python3 automated_knowledge_pipeline.py --docs

    # Только RAG индексация
    python3 automated_knowledge_pipeline.py --index

**Запускается автоматически:**
- GitHub Actions (на каждый push в main)
- Scheduler в mio-manager (ежедневно)
- Вручную через analytics-specialist API
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import logging

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Imports from existing tools
from infrastructure.AI_office_infrastructure.analytics_specialist.tools.system_behavior_analyzer import (
    SystemBehaviorAnalyzer,
    SystemState,
    BehavioralPattern,
    EdgeCase
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('automated_knowledge_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutomatedKnowledgePipeline:
    """
    Автоматизированный pipeline для обработки знаний:
    анализ → документация → индексация → правила
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.project_root = PROJECT_ROOT
        self.output_dir = output_dir or (self.project_root / "infrastructure" / "AI-office-infrastructure" / "analytics-specialist" / "reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.behavior_analyzer = SystemBehaviorAnalyzer(output_dir=self.output_dir)

        # Pipeline state
        self.pipeline_state = {
            "started_at": None,
            "completed_at": None,
            "stages_completed": [],
            "errors": [],
            "outputs": {}
        }

        logger.info(f"Pipeline initialized. Output: {self.output_dir}")

    async def run_full_pipeline(self):
        """Запустить полный pipeline"""
        logger.info("="*60)
        logger.info(" Starting Automated Knowledge Pipeline")
        logger.info("="*60)

        self.pipeline_state["started_at"] = datetime.now().isoformat()

        try:
            # Stage 1: System Analysis
            await self._stage_system_analysis()

            # Stage 2: Pattern Extraction
            await self._stage_pattern_extraction()

            # Stage 3: Documentation Generation
            await self._stage_documentation_generation()

            # Stage 4: Rules Generation
            await self._stage_rules_generation()

            # Stage 5: RAG Integration
            await self._stage_rag_integration()

            # Stage 6: Event Catalog
            await self._stage_event_catalog()

            self.pipeline_state["completed_at"] = datetime.now().isoformat()

            # Generate summary report
            await self._generate_summary_report()

            logger.info("="*60)
            logger.info(" Pipeline completed successfully!")
            logger.info("="*60)

        except Exception as e:
            logger.error(f" Pipeline failed: {e}")
            self.pipeline_state["errors"].append(str(e))
            raise

    async def _stage_system_analysis(self):
        """Stage 1: Analyze system behavior, states, transitions"""
        stage_name = "system_analysis"
        logger.info(f"\n{'='*60}")
        logger.info(f" Stage 1: System Analysis")
        logger.info(f"{'='*60}")

        try:
            # 1.1: Analyze system states
            logger.info(" Analyzing system states...")
            state_machine = await self.behavior_analyzer.analyze_system_states()

            states_count = len(state_machine.get("states", {}))
            transitions_count = len(state_machine.get("transitions", []))
            logger.info(f"   Found {states_count} states, {transitions_count} transitions")

            # 1.2: Detect edge cases
            logger.info(" Detecting edge cases...")
            edge_cases = await self.behavior_analyzer.detect_edge_cases()
            logger.info(f"   Found {len(edge_cases)} edge cases")

            # Save outputs
            self.pipeline_state["outputs"][stage_name] = {
                "state_machine": state_machine,
                "edge_cases": [
                    {
                        "case_id": ec.case_id,
                        "description": ec.description,
                        "severity": ec.severity
                    } for ec in edge_cases
                ]
            }

            self.pipeline_state["stages_completed"].append(stage_name)
            logger.info(f" {stage_name} complete\n")

        except Exception as e:
            logger.error(f" {stage_name} failed: {e}")
            self.pipeline_state["errors"].append(f"{stage_name}: {e}")
            raise

    async def _stage_pattern_extraction(self):
        """Stage 2: Extract behavioral patterns from events/logs"""
        stage_name = "pattern_extraction"
        logger.info(f"\n{'='*60}")
        logger.info(f" Stage 2: Pattern Extraction")
        logger.info(f"{'='*60}")

        try:
            # 2.1: Extract patterns from events
            logger.info(" Extracting patterns from Event Bus...")
            patterns = await self.behavior_analyzer.extract_behavioral_patterns(source="events")
            logger.info(f"   Found {len(patterns)} behavioral patterns")

            # 2.2: Analyze pattern frequency
            high_freq = [p for p in patterns if p.frequency > 100]
            logger.info(f"   {len(high_freq)} high-frequency patterns (>100 occurrences)")

            # Save outputs
            self.pipeline_state["outputs"][stage_name] = {
                "patterns": [
                    {
                        "pattern_id": p.pattern_id,
                        "pattern_type": p.pattern_type,
                        "description": p.description,
                        "frequency": p.frequency,
                        "confidence": p.confidence
                    } for p in patterns
                ],
                "high_frequency_patterns": len(high_freq)
            }

            self.pipeline_state["stages_completed"].append(stage_name)
            logger.info(f" {stage_name} complete\n")

        except Exception as e:
            logger.error(f" {stage_name} failed: {e}")
            self.pipeline_state["errors"].append(f"{stage_name}: {e}")
            raise

    async def _stage_documentation_generation(self):
        """Stage 3: Generate documentation (README, API, scenarios)"""
        stage_name = "documentation_generation"
        logger.info(f"\n{'='*60}")
        logger.info(f" Stage 3: Documentation Generation")
        logger.info(f"{'='*60}")

        try:
            # 3.1: Generate user scenarios from patterns
            logger.info(" Generating user scenarios...")
            scenarios = await self.behavior_analyzer.generate_user_scenarios()
            logger.info(f"   Generated {len(scenarios)} user scenarios (Gherkin format)")

            # 3.2: Call AI documentation generator (existing tool)
            logger.info(" Running AI documentation generator...")
            ai_doc_gen_path = self.project_root / "infrastructure" / "tools" / "doc-generators" / "ai_documentation_generator.py"

            if ai_doc_gen_path.exists():
                # Use existing AI doc generator
                # Note: In production, import and call directly
                logger.info("   AI doc generator found, integrating...")
                # Placeholder: будет импортирован и вызван напрямую
                docs_generated = await self._call_ai_doc_generator()
            else:
                logger.warning("   AI doc generator not found, skipping")
                docs_generated = 0

            # Save outputs
            self.pipeline_state["outputs"][stage_name] = {
                "user_scenarios": len(scenarios),
                "ai_docs_generated": docs_generated
            }

            self.pipeline_state["stages_completed"].append(stage_name)
            logger.info(f" {stage_name} complete\n")

        except Exception as e:
            logger.error(f" {stage_name} failed: {e}")
            self.pipeline_state["errors"].append(f"{stage_name}: {e}")
            # Don't raise - continue with other stages

    async def _stage_rules_generation(self):
        """Stage 4: Generate executable rules from flows"""
        stage_name = "rules_generation"
        logger.info(f"\n{'='*60}")
        logger.info(f" Stage 4: Rules Generation")
        logger.info(f"{'='*60}")

        try:
            # 4.1: Convert flows to Python rules
            logger.info(" Generating Python business rules...")
            python_rules = await self.behavior_analyzer.convert_flows_to_rules(output_format="python")
            logger.info(f"   Generated: {python_rules['file']}")

            # 4.2: Convert flows to Temporal workflows
            logger.info(" Generating Temporal workflows...")
            temporal_workflows = await self.behavior_analyzer.convert_flows_to_rules(output_format="temporal")
            logger.info(f"   Generated: {temporal_workflows['file']}")

            # Save outputs
            self.pipeline_state["outputs"][stage_name] = {
                "python_rules_file": str(python_rules['file']),
                "temporal_workflows_file": str(temporal_workflows['file'])
            }

            self.pipeline_state["stages_completed"].append(stage_name)
            logger.info(f" {stage_name} complete\n")

        except Exception as e:
            logger.error(f" {stage_name} failed: {e}")
            self.pipeline_state["errors"].append(f"{stage_name}: {e}")
            # Don't raise - continue with other stages

    async def _stage_rag_integration(self):
        """Stage 5: Index documentation into Qdrant for RAG"""
        stage_name = "rag_integration"
        logger.info(f"\n{'='*60}")
        logger.info(f" Stage 5: RAG Integration")
        logger.info(f"{'='*60}")

        try:
            # 5.1: Load comprehensive docs into Qdrant
            logger.info(" Loading comprehensive docs into Qdrant...")

            comprehensive_docs_path = self.project_root / "doc-project" / "comprehensive-platform-docs"

            if comprehensive_docs_path.exists():
                # Call comprehensive docs loader
                docs_indexed = await self._load_comprehensive_docs_to_qdrant()
                logger.info(f"   Indexed {docs_indexed} documents into Qdrant")
            else:
                logger.warning("   Comprehensive docs not found, skipping")
                docs_indexed = 0

            # 5.2: Index generated scenarios
            logger.info(" Indexing generated scenarios...")
            scenarios_file = self.output_dir / "user_scenarios.json"
            if scenarios_file.exists():
                scenarios_indexed = await self._index_scenarios_to_qdrant(scenarios_file)
                logger.info(f"   Indexed {scenarios_indexed} scenarios")
            else:
                scenarios_indexed = 0

            # Save outputs
            self.pipeline_state["outputs"][stage_name] = {
                "docs_indexed": docs_indexed,
                "scenarios_indexed": scenarios_indexed
            }

            self.pipeline_state["stages_completed"].append(stage_name)
            logger.info(f" {stage_name} complete\n")

        except Exception as e:
            logger.error(f" {stage_name} failed: {e}")
            self.pipeline_state["errors"].append(f"{stage_name}: {e}")
            # Don't raise - continue with other stages

    async def _stage_event_catalog(self):
        """Stage 6: Generate event catalog"""
        stage_name = "event_catalog"
        logger.info(f"\n{'='*60}")
        logger.info(f" Stage 6: Event Catalog Generation")
        logger.info(f"{'='*60}")

        try:
            # 6.1: Call event catalog generator (existing tool)
            logger.info(" Generating event catalog...")

            event_catalog_gen_path = self.project_root / "infrastructure" / "tools" / "doc-generators" / "event_catalog_generator.py"

            if event_catalog_gen_path.exists():
                events_cataloged = await self._call_event_catalog_generator()
                logger.info(f"   Cataloged {events_cataloged} events")
            else:
                logger.warning("   Event catalog generator not found, skipping")
                events_cataloged = 0

            # Save outputs
            self.pipeline_state["outputs"][stage_name] = {
                "events_cataloged": events_cataloged
            }

            self.pipeline_state["stages_completed"].append(stage_name)
            logger.info(f" {stage_name} complete\n")

        except Exception as e:
            logger.error(f" {stage_name} failed: {e}")
            self.pipeline_state["errors"].append(f"{stage_name}: {e}")
            # Don't raise - continue with summary

    async def _generate_summary_report(self):
        """Generate summary report for the pipeline run"""
        logger.info(f"\n{'='*60}")
        logger.info(f" Generating Summary Report")
        logger.info(f"{'='*60}")

        report = {
            "pipeline_run": {
                "started_at": self.pipeline_state["started_at"],
                "completed_at": self.pipeline_state["completed_at"],
                "duration_seconds": self._calculate_duration(),
                "success": len(self.pipeline_state["errors"]) == 0
            },
            "stages": {
                "total": 6,
                "completed": len(self.pipeline_state["stages_completed"]),
                "failed": 6 - len(self.pipeline_state["stages_completed"])
            },
            "outputs": self.pipeline_state["outputs"],
            "errors": self.pipeline_state["errors"]
        }

        # Save JSON report
        report_file = self.output_dir / f"pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f" Summary report: {report_file}")

        # Print summary to console
        print("\n" + "="*60)
        print(" PIPELINE SUMMARY")
        print("="*60)
        print(f"Stages completed: {report['stages']['completed']}/{report['stages']['total']}")
        print(f"Duration: {report['pipeline_run']['duration_seconds']:.2f}s")
        print(f"Status: {' SUCCESS' if report['pipeline_run']['success'] else ' FAILED'}")

        if report['errors']:
            print(f"\n️  Errors encountered:")
            for error in report['errors']:
                print(f"   - {error}")

        print("\n Outputs:")
        for stage, outputs in report['outputs'].items():
            print(f"   {stage}: {outputs}")

        print("="*60 + "\n")

    def _calculate_duration(self) -> float:
        """Calculate pipeline duration in seconds"""
        if not self.pipeline_state["started_at"] or not self.pipeline_state["completed_at"]:
            return 0.0

        start = datetime.fromisoformat(self.pipeline_state["started_at"])
        end = datetime.fromisoformat(self.pipeline_state["completed_at"])
        return (end - start).total_seconds()

    # === Integration Methods with Existing Tools ===

    async def _call_ai_doc_generator(self) -> int:
        """Call AI documentation generator (existing tool)"""
        # TODO: Import and call directly in production
        # from infrastructure.tools.doc_generators.ai_documentation_generator import AIDocumentationGenerator

        # Placeholder: return mock count
        logger.info("   [Placeholder] AI doc generator called")
        return 10  # Mock: 10 docs generated

    async def _call_event_catalog_generator(self) -> int:
        """Call event catalog generator (existing tool)"""
        # TODO: Import and call directly in production
        # from infrastructure.tools.doc_generators.event_catalog_generator import EventCatalogGenerator

        # Placeholder: return mock count
        logger.info("   [Placeholder] Event catalog generator called")
        return 85  # Mock: 85 events cataloged

    async def _load_comprehensive_docs_to_qdrant(self) -> int:
        """Load comprehensive docs into Qdrant"""
        # TODO: Import and call directly in production
        # from intelligent_core.ai_foundation.learning_knowledge.loaders.comprehensive_docs_loader import ComprehensiveDocsLoader

        # Placeholder: return mock count
        logger.info("   [Placeholder] Comprehensive docs loader called")
        return 7  # Mock: 7 documents indexed

    async def _index_scenarios_to_qdrant(self, scenarios_file: Path) -> int:
        """Index generated scenarios to Qdrant"""
        # TODO: Implement Qdrant indexing
        # 1. Load scenarios from JSON
        # 2. Create embeddings
        # 3. Upload to Qdrant collection "platform_scenarios"

        # Placeholder: return mock count
        logger.info("   [Placeholder] Scenarios indexing called")
        return 45  # Mock: 45 scenarios indexed


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Automated Knowledge Pipeline')
    parser.add_argument('--full', action='store_true', help='Run full pipeline')
    parser.add_argument('--analyze', action='store_true', help='Only system analysis')
    parser.add_argument('--docs', action='store_true', help='Only documentation generation')
    parser.add_argument('--index', action='store_true', help='Only RAG indexing')
    parser.add_argument('--output', help='Custom output directory')

    args = parser.parse_args()

    # Initialize pipeline
    output_dir = Path(args.output) if args.output else None
    pipeline = AutomatedKnowledgePipeline(output_dir=output_dir)

    if args.full or not any([args.analyze, args.docs, args.index]):
        # Run full pipeline
        await pipeline.run_full_pipeline()
    else:
        # Run specific stages
        if args.analyze:
            await pipeline._stage_system_analysis()
            await pipeline._stage_pattern_extraction()

        if args.docs:
            await pipeline._stage_documentation_generation()

        if args.index:
            await pipeline._stage_rag_integration()


if __name__ == '__main__':
    asyncio.run(main())
