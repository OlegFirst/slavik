"""
Expertise Center Initialization

Sets up the expertise center with all domain plugins.
"""

import logging
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from expertise_center.core import (
    ChiefExecutiveAI,
    DomainLoader,
    ExpertRegistry
)

logger = logging.getLogger(__name__)


def initialize_expertise_center(
    llm_client=None,
    auto_load_domains: bool = True
):
    """
    Initialize the Expertise Center

    Args:
        llm_client: Optional LLM client for advanced intent detection
        auto_load_domains: Whether to auto-load all available domains

    Returns:
        ChiefExecutiveAI instance ready to handle requests
    """
    logger.info("Initializing Expertise Center...")

    # Step 1: Create expert registry
    expert_registry = ExpertRegistry()
    logger.info("Created ExpertRegistry")

    # Step 2: Create domain loader
    domain_loader = DomainLoader(expert_registry)
    logger.info("Created DomainLoader")

    # Step 3: Load domains
    if auto_load_domains:
        loaded_domains = domain_loader.load_all_domains()
        logger.info(f"Loaded {len(loaded_domains)} domains: {list(loaded_domains.keys())}")
    else:
        logger.info("Skipping auto-load of domains")

    # Step 4: Create Chief Executive AI
    chief_executive = ChiefExecutiveAI(
        expert_registry=expert_registry,
        domain_loader=domain_loader,
        llm_client=llm_client
    )
    logger.info("Created ChiefExecutiveAI")

    # Step 5: Log statistics
    stats = expert_registry.get_stats()
    logger.info(f"Expertise Center ready with {stats['total_experts']} experts across {stats['total_domains']} domains")

    return chief_executive


def get_expertise_center_status(chief_executive: ChiefExecutiveAI):
    """
    Get detailed status of expertise center

    Args:
        chief_executive: ChiefExecutiveAI instance

    Returns:
        Status dictionary
    """
    return chief_executive.get_status()


async def test_expertise_center(chief_executive: ChiefExecutiveAI):
    """
    Test expertise center with sample queries

    Args:
        chief_executive: ChiefExecutiveAI instance
    """
    test_queries = [
        {
            "query": "Calculate BIA for payment processing",
            "context": {"organization": "test_org", "user_id": "test_user"}
        },
        {
            "query": "Analyze risk for data center failure",
            "context": {"organization": "test_org", "user_id": "test_user"}
        },
        {
            "query": "Check compliance with ISO 22301",
            "context": {"organization": "test_org", "user_id": "test_user"}
        }
    ]

    logger.info("Testing Expertise Center with sample queries...")

    for i, test in enumerate(test_queries, 1):
        logger.info(f"\nTest {i}: {test['query']}")

        result = await chief_executive.handle_request(
            user_query=test['query'],
            context=test['context']
        )

        logger.info(f"Result: {result.get('success', False)}")
        if 'metadata' in result:
            logger.info(f"Metadata: {result['metadata']}")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize
    chief = initialize_expertise_center()

    # Show status
    status = get_expertise_center_status(chief)
    print("\n" + "="*60)
    print("EXPERTISE CENTER STATUS")
    print("="*60)
    print(f"Total Experts: {status['metrics']['total_requests']}")
    print(f"Loaded Domains: {status['loaded_domains']}")
    print(f"\nRegistry Stats:")
    for domain, info in status['registry_stats']['domains'].items():
        print(f"  {domain}: {info['expertise_count']} experts - {info['expertise_areas']}")
    print("="*60)

    # Run async test
    import asyncio
    asyncio.run(test_expertise_center(chief))
