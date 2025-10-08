"""
🧪 Integration Tests for Knowledge System

Tests complete workflow:
1. Load standards
2. Collect cases
3. Index in vector DB
4. Search via API
5. Monitor for updates
"""

import pytest
import asyncio
import json
from pathlib import Path
from datetime import datetime
import sys

# Add knowledge-system to path
ks_path = Path(__file__).parents[1]
if str(ks_path) not in sys.path:
    sys.path.insert(0, str(ks_path))


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def data_path():
    """Get data path"""
    return Path(__file__).parents[4] / "data"


@pytest.fixture
def standards_loader():
    """Create StandardsLoader instance"""
    from loader.standards_loader import StandardsLoader
    return StandardsLoader()


@pytest.fixture
def case_collector():
    """Create CaseCollector instance"""
    from loader.case_loader import CaseCollector
    return CaseCollector()


@pytest.fixture
async def vector_indexer():
    """Create VectorIndexer instance (skip if Qdrant not available)"""
    try:
        from indexer.vector_indexer import VectorIndexer

        indexer = VectorIndexer(
            qdrant_url="http://localhost:6333",
            embedding_provider="tfidf",  # Use TF-IDF for testing (no external deps)
            tenant_id="test"
        )

        await indexer.initialize_collections()

        return indexer

    except Exception as e:
        pytest.skip(f"Qdrant not available: {e}")


@pytest.fixture
def standards_monitor():
    """Create StandardsMonitor instance"""
    from updater.standards_monitor import StandardsMonitor
    return StandardsMonitor()


# ============================================================================
# TEST STANDARDS LOADER
# ============================================================================

@pytest.mark.asyncio
async def test_load_iso_standard(standards_loader, data_path):
    """Test loading ISO 22301 standard"""

    # Check if standard exists
    iso_path = data_path / "knowledge" / "standards" / "iso" / "iso-22301"
    if not iso_path.exists():
        pytest.skip("ISO 22301 not found in data/")

    # Load standard
    data = await standards_loader.load_iso_standard("iso-22301")

    # Verify structure
    assert data is not None
    assert "standard" in data
    assert "version" in data
    assert "metadata" in data
    assert "clauses" in data
    assert data["standard"] == "iso-22301"

    # Verify clauses
    assert len(data["clauses"]) > 0
    assert "number" in data["clauses"][0]
    assert "title" in data["clauses"][0]

    print(f"✅ Loaded ISO 22301: {len(data['clauses'])} clauses")


@pytest.mark.asyncio
async def test_standards_caching(standards_loader):
    """Test that standards are cached properly"""

    iso_path = Path(__file__).parents[4] / "data" / "knowledge" / "standards" / "iso" / "iso-22301"
    if not iso_path.exists():
        pytest.skip("ISO 22301 not found")

    # First load (cache miss)
    start1 = datetime.now()
    data1 = await standards_loader.load_iso_standard("iso-22301")
    duration1 = (datetime.now() - start1).total_seconds()

    # Second load (cache hit - should be faster)
    start2 = datetime.now()
    data2 = await standards_loader.load_iso_standard("iso-22301")
    duration2 = (datetime.now() - start2).total_seconds()

    assert data1 == data2
    assert duration2 < duration1 or duration2 < 0.1  # Cached should be much faster

    print(f"✅ Cache working: first={duration1:.3f}s, second={duration2:.3f}s")


# ============================================================================
# TEST CASE COLLECTOR
# ============================================================================

@pytest.mark.asyncio
async def test_collect_workflow_case(case_collector):
    """Test collecting a workflow case"""

    case_data = await case_collector.collect_workflow_case(
        workflow_id="test-workflow-001",
        module="bia",
        outcome="success",
        organization_context={
            "industry": "healthcare",
            "size": "medium",
            "org_type": "hospital",
            "maturity_level": "intermediate"
        },
        metrics={
            "total_duration_days": 14,
            "total_steps": 8,
            "processes_identified": 12,
            "critical_processes": 5,
            "completed_successfully": True
        },
        decisions=[
            {"step": "scoping", "decision": "Include all critical processes"},
            {"step": "analysis", "decision": "Use FAIR methodology"}
        ],
        final_variables={
            "rto_target": "4 hours",
            "rpo_target": "1 hour",
            "certification_ready": True
        }
    )

    # Verify case was created
    assert case_data is not None
    assert "case_id" in case_data
    assert "file_path" in case_data
    assert case_data["module"] == "bia"

    # Verify file exists
    case_file = Path(case_data["file_path"])
    assert case_file.exists()

    # Verify file content
    saved_case = json.loads(case_file.read_text())
    assert saved_case["workflow_id"] == "test-workflow-001"
    assert saved_case["outcome"] == "success"
    assert saved_case["organization_context"]["industry"] == "healthcare"

    print(f"✅ Case collected: {case_data['case_id']}")

    # Cleanup
    case_file.unlink()


@pytest.mark.asyncio
async def test_find_similar_cases(case_collector, data_path):
    """Test finding similar cases"""

    # Check if any cases exist
    cases_path = data_path / "cases" / "workflow_cases" / "bia"
    if not cases_path.exists() or not list(cases_path.glob("*.json")):
        pytest.skip("No BIA cases available for testing")

    # Find similar cases
    similar = await case_collector.find_similar_cases(
        module="bia",
        organization_context={
            "industry": "healthcare",
            "size": "medium"
        },
        limit=5
    )

    # Should find at least one case
    assert len(similar) > 0
    assert "case_id" in similar[0]
    assert "similarity_score" in similar[0]

    print(f"✅ Found {len(similar)} similar cases")


# ============================================================================
# TEST VECTOR INDEXER
# ============================================================================

@pytest.mark.asyncio
async def test_index_and_search_standard(vector_indexer, standards_loader, data_path):
    """Test indexing and searching standards"""

    # Check if ISO 22301 exists
    iso_path = data_path / "knowledge" / "standards" / "iso" / "iso-22301"
    if not iso_path.exists():
        pytest.skip("ISO 22301 not found")

    # Load standard
    standard_data = await standards_loader.load_iso_standard("iso-22301")

    # Index standard
    point_id = await vector_indexer.index_standard(standard_data)
    assert point_id is not None

    print(f"✅ Indexed standard: {point_id[:16]}...")

    # Search for standard
    results = await vector_indexer.search_standards(
        query="business continuity management requirements",
        limit=3
    )

    # Should find the indexed standard
    assert len(results) > 0
    assert any(r["standard"] == "iso-22301" for r in results)

    print(f"✅ Search found {len(results)} results")


@pytest.mark.asyncio
async def test_index_and_search_case(vector_indexer, case_collector):
    """Test indexing and searching cases"""

    # Create a test case
    case_data_dict = {
        "case_id": "test-case-vector-001",
        "workflow_id": "wf-001",
        "module": "bia",
        "outcome": "success",
        "organization_context": {
            "industry": "finance",
            "size": "large",
            "org_type": "bank",
            "maturity_level": "advanced"
        },
        "metrics": {
            "total_duration_days": 21,
            "processes_identified": 25,
            "critical_processes": 10
        },
        "decisions": [
            {"step": "analysis", "decision": "Focus on tier 1 processes"}
        ],
        "collected_at": datetime.utcnow().isoformat(),
        "source": "test"
    }

    # Index case
    point_id = await vector_indexer.index_case(case_data_dict)
    assert point_id == "test-case-vector-001"

    print(f"✅ Indexed case: {point_id}")

    # Search for case
    results = await vector_indexer.search_cases(
        query="large bank with advanced BCM maturity",
        module="bia",
        limit=3
    )

    # Should find the indexed case
    assert len(results) > 0
    assert any(r["case_id"] == "test-case-vector-001" for r in results)

    print(f"✅ Search found {len(results)} results")


# ============================================================================
# TEST STANDARDS MONITOR
# ============================================================================

@pytest.mark.asyncio
async def test_standards_update_check(standards_monitor):
    """Test checking for standards updates"""

    # Run one check cycle
    summary = await standards_monitor.run_check_cycle()

    # Verify summary structure
    assert "checked_at" in summary
    assert "sources_checked" in summary
    assert "updates_found" in summary
    assert "by_source" in summary

    # Should check at least ISO source
    assert summary["sources_checked"] > 0
    assert "iso" in summary["by_source"]

    print(f"✅ Update check complete: {summary['updates_found']} updates found")
    print(f"   Sources checked: {summary['sources_checked']}")
    print(f"   By source: {summary['by_source']}")


# ============================================================================
# TEST API
# ============================================================================

@pytest.mark.asyncio
async def test_api_health():
    """Test API health endpoint"""

    from api.main import health_check

    response = await health_check()

    assert response.status == "healthy"
    assert "components" in response.components
    assert "api" in response.components

    print(f"✅ API health check passed")


@pytest.mark.asyncio
async def test_api_list_standards(data_path):
    """Test API list standards endpoint"""

    from api.main import list_standards

    # Check if any standards exist
    standards_path = data_path / "knowledge" / "standards"
    if not standards_path.exists():
        pytest.skip("No standards available")

    standards = await list_standards(domain=None, tenant_id="default")

    # Should return list of standards
    assert isinstance(standards, list)
    assert len(standards) > 0

    print(f"✅ API returned {len(standards)} standards")


# ============================================================================
# INTEGRATION TEST: FULL WORKFLOW
# ============================================================================

@pytest.mark.asyncio
async def test_complete_workflow(
    standards_loader,
    case_collector,
    data_path
):
    """
    Test complete workflow:
    1. Load ISO standard
    2. Collect workflow case
    3. Find similar cases
    """

    print("\n" + "="*60)
    print("RUNNING COMPLETE INTEGRATION TEST")
    print("="*60)

    # Step 1: Load ISO 22301
    print("\n[1/3] Loading ISO 22301...")
    iso_path = data_path / "knowledge" / "standards" / "iso" / "iso-22301"
    if not iso_path.exists():
        pytest.skip("ISO 22301 not found")

    standard = await standards_loader.load_iso_standard("iso-22301")
    assert standard is not None
    print(f"✅ Loaded: {standard['metadata']['title']}")
    print(f"   Clauses: {len(standard['clauses'])}")

    # Step 2: Collect a test case
    print("\n[2/3] Collecting workflow case...")
    case = await case_collector.collect_workflow_case(
        workflow_id="integration-test-001",
        module="bia",
        outcome="success",
        organization_context={
            "industry": "technology",
            "size": "medium",
            "org_type": "saas",
            "maturity_level": "intermediate"
        },
        metrics={
            "total_duration_days": 10,
            "total_steps": 6,
            "processes_identified": 15,
            "critical_processes": 7,
            "completed_successfully": True
        },
        decisions=[],
        final_variables={}
    )

    assert case is not None
    print(f"✅ Case collected: {case['case_id']}")
    print(f"   File: {case['file_path']}")

    # Step 3: Find similar cases
    print("\n[3/3] Finding similar cases...")
    similar = await case_collector.find_similar_cases(
        module="bia",
        organization_context={
            "industry": "technology",
            "size": "medium"
        },
        limit=3
    )

    assert len(similar) > 0
    print(f"✅ Found {len(similar)} similar cases:")
    for i, case in enumerate(similar[:3], 1):
        print(f"   {i}. {case['case_id']} (score: {case.get('similarity_score', 'N/A')})")

    # Cleanup
    Path(case["file_path"]).unlink()

    print("\n" + "="*60)
    print("✅ INTEGRATION TEST PASSED")
    print("="*60 + "\n")


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
