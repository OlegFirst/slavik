"""
Basic tests for Knowledge System

Run: pytest tests/test_basic.py -v
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from learning_knowledge.knowledge.loader.standards_loader import StandardsLoader
from learning_knowledge.knowledge.loader.case_loader import CaseCollector


class TestStandardsLoader:
    """Test StandardsLoader functionality"""

    @pytest.mark.asyncio
    async def test_load_iso_22301(self):
        """Test loading ISO 22301 standard"""

        loader = StandardsLoader()

        data = await loader.load_iso_standard("iso-22301")

        # Assertions
        assert data is not None
        assert data["standard"] == "iso-22301"
        assert "metadata" in data
        assert data["metadata"]["title"] is not None
        assert "guides" in data
        assert len(data["guides"]) >= 3  # BSI, NQA, ISO

        print(f"\n Loaded ISO 22301:")
        print(f"   Title: {data['metadata']['title']}")
        print(f"   Version: {data['metadata']['version']}")
        print(f"   Guides: {len(data['guides'])}")

    @pytest.mark.asyncio
    async def test_cache_functionality(self):
        """Test that caching works"""

        loader = StandardsLoader(cache_enabled=True)

        # First load
        data1 = await loader.load_iso_standard("iso-22301")

        # Second load (should be from cache)
        data2 = await loader.load_iso_standard("iso-22301")

        assert data1 == data2

        print("\n Cache working correctly")

    @pytest.mark.asyncio
    async def test_list_available_standards(self):
        """Test listing available standards"""

        loader = StandardsLoader()

        available = await loader.list_available_standards()

        assert "iso" in available
        assert "iso-22301" in available["iso"]

        print(f"\n Available standards: {available}")


class TestCaseCollector:
    """Test CaseCollector functionality"""

    @pytest.mark.asyncio
    async def test_collect_workflow_case(self):
        """Test collecting a workflow case"""

        collector = CaseCollector()

        case = await collector.collect_workflow_case(
            workflow_id="test-workflow-123",
            module="bia",
            outcome="success",
            organization_context={
                "industry": "healthcare",
                "size": "medium",
                "employees": 500
            },
            metrics={
                "duration_days": 14,
                "total_tasks": 8,
                "completion_rate": 1.0
            },
            decisions=[
                {
                    "step": "rto_definition",
                    "value": "4 hours",
                    "rationale": "Critical patient care systems"
                }
            ]
        )

        # Assertions
        assert case is not None
        assert "case_id" in case
        assert case["module"] == "bia"
        assert case["outcome"] == "success"

        print(f"\n Workflow case collected:")
        print(f"   Case ID: {case['case_id']}")
        print(f"   File: {case['file_path']}")

    @pytest.mark.asyncio
    async def test_get_case_stats(self):
        """Test getting case statistics"""

        collector = CaseCollector()

        stats = await collector.get_case_stats()

        assert "total" in stats
        assert "by_module" in stats
        assert "by_source" in stats

        print(f"\n Case stats: {stats}")

    @pytest.mark.asyncio
    async def test_import_community_case(self):
        """Test importing community case"""

        collector = CaseCollector()

        case_data = {
            "title": "Healthcare BIA Template",
            "module": "bia",
            "organization_context": {
                "industry": "healthcare",
                "size": "medium"
            },
            "template": {
                "steps": ["identify", "analyze", "report"]
            }
        }

        result = await collector.import_community_case(
            case_data=case_data,
            source="templates"
        )

        assert result["status"] in ["imported", "duplicate"]

        if result["status"] == "imported":
            print(f"\n Community case imported: {result['case_id']}")
        else:
            print(f"\n️  Duplicate case detected: {result['case_id']}")


if __name__ == "__main__":
    # Run tests manually
    print(" Running Knowledge System Tests\n")

    async def run_tests():
        print("=" * 60)
        print("TEST: StandardsLoader")
        print("=" * 60)

        test_loader = TestStandardsLoader()
        await test_loader.test_load_iso_22301()
        await test_loader.test_cache_functionality()
        await test_loader.test_list_available_standards()

        print("\n" + "=" * 60)
        print("TEST: CaseCollector")
        print("=" * 60)

        test_collector = TestCaseCollector()
        await test_collector.test_collect_workflow_case()
        await test_collector.test_import_community_case()
        await test_collector.test_get_case_stats()

        print("\n" + "=" * 60)
        print(" ALL TESTS PASSED!")
        print("=" * 60)

    asyncio.run(run_tests())
