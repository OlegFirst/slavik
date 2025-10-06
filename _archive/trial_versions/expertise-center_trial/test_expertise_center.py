#!/usr/bin/env python3
"""
Test Expertise Center

Quick test to verify expertise center setup and functionality.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add current and parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

# Import with fallback
try:
    from expertise_center.initialize import initialize_expertise_center
except ModuleNotFoundError:
    from initialize import initialize_expertise_center


async def test_basic_functionality():
    """Test basic expertise center functionality"""
    print("\n" + "="*70)
    print("TESTING EXPERTISE CENTER")
    print("="*70)

    # Initialize
    print("\n1. Initializing Expertise Center...")
    chief = initialize_expertise_center(auto_load_domains=True)

    # Check status
    print("\n2. Checking Status...")
    status = chief.get_status()
    print(f"   ✓ Loaded domains: {status['loaded_domains']}")
    print(f"   ✓ Total experts: {status['registry_stats']['total_experts']}")
    print(f"   ✓ Total requests: {status['metrics']['total_requests']}")

    # Test queries
    test_cases = [
        {
            "name": "BIA Calculation",
            "query": "Calculate BIA for payment processing",
            "context": {"organization": "acme_corp", "user_id": "user123"}
        },
        {
            "name": "Criticality Assessment",
            "query": "Assess criticality of customer service process",
            "context": {"organization": "acme_corp", "user_id": "user123"}
        },
        {
            "name": "RTO/RPO Calculation",
            "query": "Calculate RTO and RPO for database operations",
            "context": {"organization": "acme_corp", "user_id": "user123"}
        },
        {
            "name": "Dependency Mapping",
            "query": "Map dependencies for payment processing",
            "context": {"organization": "acme_corp", "user_id": "user123"}
        }
    ]

    print("\n3. Testing Queries...")
    for i, test in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test['name']}")
        print(f"   Query: '{test['query']}'")

        result = await chief.handle_request(
            user_query=test['query'],
            context=test['context']
        )

        if result.get("success"):
            print(f"   ✓ Success")
            if "metadata" in result:
                meta = result["metadata"]
                print(f"     - Domain: {meta.get('domain', 'N/A')}")
                print(f"     - Expertise: {meta.get('expertise', 'N/A')}")
                print(f"     - Confidence: {meta.get('confidence', 0):.2f}")
                print(f"     - Response time: {meta.get('response_time', 0):.3f}s")
        else:
            print(f"   ✗ Failed: {result.get('error', 'Unknown error')}")

    # Final status
    print("\n4. Final Status...")
    final_status = chief.get_status()
    print(f"   ✓ Total requests handled: {final_status['metrics']['total_requests']}")
    print(f"   ✓ Successful routes: {final_status['metrics']['successful_routes']}")
    print(f"   ✓ Failed routes: {final_status['metrics']['failed_routes']}")
    if final_status['metrics']['total_requests'] > 0:
        success_rate = final_status['metrics']['success_rate']
        print(f"   ✓ Success rate: {success_rate:.1%}")

    print("\n" + "="*70)
    print("TEST COMPLETED")
    print("="*70 + "\n")


async def test_registry_search():
    """Test expert registry search functionality"""
    print("\n" + "="*70)
    print("TESTING EXPERT REGISTRY SEARCH")
    print("="*70)

    chief = initialize_expertise_center(auto_load_domains=True)

    # Search by capability
    print("\n1. Search by capability 'business_impact_analysis'...")
    experts = chief.expert_registry.find_experts_by_capability("business_impact_analysis")
    print(f"   Found {len(experts)} expert(s):")
    for exp in experts:
        print(f"   - {exp.domain}.{exp.expertise}: {exp.description[:60]}...")

    # Search by query
    print("\n2. Search by query 'risk'...")
    experts = chief.expert_registry.search_experts("risk", domain="bcm")
    print(f"   Found {len(experts)} expert(s):")
    for exp in experts:
        print(f"   - {exp.domain}.{exp.expertise}")

    # List all domains
    print("\n3. List all domains...")
    domains = chief.expert_registry.list_domains()
    print(f"   Domains: {domains}")

    # Domain experts
    if domains:
        domain = domains[0]
        print(f"\n4. List all experts in '{domain}' domain...")
        experts = chief.expert_registry.get_domain_experts(domain)
        print(f"   Found {len(experts)} expert(s):")
        for exp in experts:
            print(f"   - {exp.expertise}: {len(exp.capabilities)} capabilities")

    print("\n" + "="*70 + "\n")


async def test_error_handling():
    """Test error handling"""
    print("\n" + "="*70)
    print("TESTING ERROR HANDLING")
    print("="*70)

    chief = initialize_expertise_center(auto_load_domains=True)

    # Test with unknown domain/expertise
    print("\n1. Testing unknown expertise...")
    result = await chief.handle_request(
        user_query="Analyze quantum entanglement in finance",
        context={"organization": "test", "user_id": "test"}
    )

    if not result.get("success"):
        print(f"   ✓ Properly handled: {result.get('error', '')}")
        if "suggestions" in result:
            print(f"   ✓ Provided suggestions")
    else:
        print(f"   ✗ Should have failed but didn't")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run tests
    asyncio.run(test_basic_functionality())
    asyncio.run(test_registry_search())
    asyncio.run(test_error_handling())

    print("\n✅ All tests completed!\n")
