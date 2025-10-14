"""
Case Collector - Unified case management

Collects cases from multiple sources:
- Workflow completions (workflow_intelligence)
- Community marketplace (user-submitted)
- Simulation results (digital-twin)

Features:
- PostgreSQL persistence
- File system storage (JSON)
- Vector DB indexing (semantic search)
- Deduplication (hash-based)
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CaseCollector:
    """
    Collect and manage workflow cases from multiple sources

    Storage layers:
    1. PostgreSQL (via workflow_intelligence.case_library.repository)
    2. File System (data/cases/)
    3. Vector DB (for semantic search)
    """

    def __init__(
        self,
        data_path: Optional[Path] = None,
        repository=None,  # CaseRepository from workflow_intelligence
        vector_indexer=None  # VectorIndexer
    ):
        if data_path is None:
            project_root = Path(__file__).parents[3]
            data_path = project_root / "data"

        self.data_path = Path(data_path)
        self.cases_path = self.data_path / "cases"
        self.workflow_cases_path = self.cases_path / "workflow_cases"
        self.community_cases_path = self.cases_path / "community_cases"
        self.simulation_cases_path = self.cases_path / "simulation_cases"

        # Ensure paths exist
        for path in [self.workflow_cases_path, self.community_cases_path, self.simulation_cases_path]:
            path.mkdir(parents=True, exist_ok=True)

        self.repository = repository
        self.vector_indexer = vector_indexer

    async def collect_workflow_case(
        self,
        workflow_id: str,
        module: str,
        outcome: str,
        organization_context: Dict[str, Any],
        metrics: Dict[str, Any],
        decisions: Optional[List[Dict]] = None,
        final_variables: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Collect case from completed workflow

        Flow:
        1. Save to PostgreSQL (via CaseRepository)
        2. Save to file system (JSON)
        3. Index in Vector DB (for search)
        4. Return case data

        Args:
            workflow_id: Workflow instance ID
            module: Module name (bia, risk, compliance, etc.)
            outcome: success/partial/failed
            organization_context: Industry, size, etc.
            metrics: Duration, task count, etc.
            decisions: Key decisions made
            final_variables: Final workflow variables

        Returns:
            Dict with case_id and storage locations
        """

        logger.info(f"📦 Collecting workflow case: {workflow_id} (module={module})")

        # Generate case ID
        case_id = self._generate_case_id(workflow_id, module)

        # Build case data
        case_data = {
            "case_id": case_id,
            "workflow_id": workflow_id,
            "module": module,
            "outcome": outcome,
            "organization_context": organization_context,
            "metrics": metrics,
            "decisions": decisions or [],
            "final_variables": final_variables or {},
            "collected_at": datetime.utcnow().isoformat(),
            "source": "workflow"
        }

        # 1. PostgreSQL (if repository available)
        if self.repository:
            try:
                await self.repository.save_case(case_data)
                logger.debug(f"✅ Saved to PostgreSQL")
            except Exception as e:
                logger.error(f"❌ PostgreSQL save failed: {e}")

        # 2. File System
        case_file = self.workflow_cases_path / module / f"{case_id}.json"
        case_file.parent.mkdir(parents=True, exist_ok=True)
        case_file.write_text(json.dumps(case_data, indent=2, default=str))
        logger.debug(f"✅ Saved to {case_file}")

        # 3. Vector DB indexing (if available)
        if self.vector_indexer:
            try:
                await self.vector_indexer.index_case(case_data)
                logger.debug(f"✅ Indexed in Vector DB")
            except Exception as e:
                logger.error(f"❌ Vector indexing failed: {e}")

        logger.info(f"✅ Case collected: {case_id}")

        return {
            "case_id": case_id,
            "file_path": str(case_file),
            "module": module,
            "outcome": outcome
        }

    async def import_community_case(
        self,
        case_data: Dict[str, Any],
        source: str = "marketplace"
    ) -> Dict[str, Any]:
        """
        Import case from Community Marketplace

        Sources:
        - marketplace: User-submitted cases
        - templates: Pre-built workflow templates
        - best_practices: Curated best practices

        Args:
            case_data: Case data from community
            source: Source type (marketplace/templates/best_practices)

        Returns:
            Dict with import result
        """

        logger.info(f"📥 Importing community case from {source}")

        case_id = case_data.get("id") or case_data.get("case_id")
        if not case_id:
            case_id = self._generate_case_id(
                case_data.get("title", "unknown"),
                case_data.get("module", "general")
            )
            case_data["case_id"] = case_id

        # Add metadata
        case_data["source"] = f"community_{source}"
        case_data["imported_at"] = datetime.utcnow().isoformat()

        # Check for duplicates
        if await self._is_duplicate(case_data):
            logger.warning(f"⚠️ Duplicate case detected: {case_id}")
            return {"status": "duplicate", "case_id": case_id}

        # Save to file system
        case_file = self.community_cases_path / source / f"{case_id}.json"
        case_file.parent.mkdir(parents=True, exist_ok=True)
        case_file.write_text(json.dumps(case_data, indent=2, default=str))

        # Index in Vector DB
        if self.vector_indexer:
            try:
                await self.vector_indexer.index_case(case_data)
            except Exception as e:
                logger.error(f"❌ Vector indexing failed: {e}")

        logger.info(f"✅ Community case imported: {case_id}")

        return {
            "status": "imported",
            "case_id": case_id,
            "file_path": str(case_file),
            "source": source
        }

    async def collect_simulation_case(
        self,
        scenario_id: str,
        scenario_type: str,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect case from simulation results

        Args:
            scenario_id: Scenario instance ID
            scenario_type: Type of scenario (bcm_incident, etc.)
            results: Simulation results

        Returns:
            Dict with case info
        """

        logger.info(f"🎮 Collecting simulation case: {scenario_id}")

        case_id = self._generate_case_id(scenario_id, scenario_type)

        case_data = {
            "case_id": case_id,
            "scenario_id": scenario_id,
            "scenario_type": scenario_type,
            "results": results,
            "collected_at": datetime.utcnow().isoformat(),
            "source": "simulation"
        }

        # Save to file system
        case_file = self.simulation_cases_path / scenario_type / f"{case_id}.json"
        case_file.parent.mkdir(parents=True, exist_ok=True)
        case_file.write_text(json.dumps(case_data, indent=2, default=str))

        logger.info(f"✅ Simulation case collected: {case_id}")

        return {
            "case_id": case_id,
            "file_path": str(case_file),
            "scenario_type": scenario_type
        }

    # ========== Search & Retrieval ==========

    async def find_similar_cases(
        self,
        module: str,
        organization_context: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar cases based on module and organization context

        Uses:
        - Vector DB (if available) for semantic search
        - File system fallback (exact match on module/industry)

        Args:
            module: Module name
            organization_context: Industry, size, etc.
            limit: Max results

        Returns:
            List of similar cases
        """

        # Try Vector DB first
        if self.vector_indexer and self.repository:
            try:
                return await self.repository.find_similar_cases(
                    industry=organization_context.get("industry"),
                    size=organization_context.get("size"),
                    module=module,
                    limit=limit
                )
            except Exception as e:
                logger.warning(f"Vector search failed: {e}, falling back to file search")

        # Fallback: File system search
        return await self._find_cases_filesystem(module, organization_context, limit)

    async def _find_cases_filesystem(
        self,
        module: str,
        organization_context: Dict[str, Any],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search cases in file system"""

        module_path = self.workflow_cases_path / module

        if not module_path.exists():
            return []

        cases = []

        for case_file in module_path.glob("*.json"):
            case_data = json.loads(case_file.read_text())

            # Simple matching on industry
            if case_data.get("organization_context", {}).get("industry") == organization_context.get("industry"):
                cases.append(case_data)

                if len(cases) >= limit:
                    break

        return cases

    async def get_case_stats(self) -> Dict[str, Any]:
        """Get statistics about collected cases"""

        stats = {
            "total": 0,
            "by_module": {},
            "by_source": {},
            "by_outcome": {}
        }

        # Workflow cases
        for module_dir in self.workflow_cases_path.iterdir():
            if module_dir.is_dir():
                count = len(list(module_dir.glob("*.json")))
                stats["by_module"][module_dir.name] = count
                stats["total"] += count

        # Community cases
        for source_dir in self.community_cases_path.iterdir():
            if source_dir.is_dir():
                count = len(list(source_dir.glob("*.json")))
                stats["by_source"][f"community_{source_dir.name}"] = count
                stats["total"] += count

        # Simulation cases
        for scenario_dir in self.simulation_cases_path.iterdir():
            if scenario_dir.is_dir():
                count = len(list(scenario_dir.glob("*.json")))
                stats["by_source"][f"simulation_{scenario_dir.name}"] = count
                stats["total"] += count

        return stats

    # ========== Helper Methods ==========

    def _generate_case_id(self, identifier: str, module: str) -> str:
        """Generate unique case ID from identifier + module"""

        content = f"{identifier}:{module}:{datetime.utcnow().isoformat()}"
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:12]
        return f"{module}_{hash_val}"

    async def _is_duplicate(self, case_data: Dict[str, Any]) -> bool:
        """Check if case already exists (basic hash-based check)"""

        # Hash key fields
        key_fields = {
            "title": case_data.get("title"),
            "module": case_data.get("module"),
            "organization_industry": case_data.get("organization_context", {}).get("industry")
        }

        content_hash = hashlib.md5(json.dumps(key_fields, sort_keys=True).encode()).hexdigest()

        # Check all case directories
        for cases_dir in [self.workflow_cases_path, self.community_cases_path]:
            for case_file in cases_dir.rglob("*.json"):
                existing_case = json.loads(case_file.read_text())
                existing_hash = hashlib.md5(
                    json.dumps({
                        "title": existing_case.get("title"),
                        "module": existing_case.get("module"),
                        "organization_industry": existing_case.get("organization_context", {}).get("industry")
                    }, sort_keys=True).encode()
                ).hexdigest()

                if content_hash == existing_hash:
                    return True

        return False
