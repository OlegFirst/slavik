"""
RAG Integration for Scenario Intelligence

Stores and retrieves scenarios from Qdrant vector database
Enables AI-powered scenario discovery and recommendations
"""

import logging
import sys
from typing import List, Dict, Any, Optional

# Add paths
sys.path.insert(0, '/Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/rag')
sys.path.insert(0, '/Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/llm')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScenarioRAGIntegration:
    """Integration with RAG system for scenario storage and retrieval"""

    def __init__(self):
        self.collection_name = "scenario_intelligence"
        self.qdrant = None
        self.llm = None
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize Qdrant and LLM clients"""

        try:
            # Try to import Qdrant wrapper
            from qdrant_wrapper import QdrantWrapper
            self.qdrant = QdrantWrapper()
            logger.info("✅ Qdrant client initialized")
        except Exception as e:
            logger.warning(f"⚠️  Qdrant client not available: {e}")
            self.qdrant = None

        try:
            # Try to import LLM router for embeddings
            from llm_router import LLMRouter
            self.llm = LLMRouter()
            logger.info("✅ LLM router initialized")
        except Exception as e:
            logger.warning(f"⚠️  LLM router not available: {e}")
            self.llm = None

    async def store_scenario(self, scenario: dict) -> bool:
        """
        Store scenario in RAG for AI retrieval

        Args:
            scenario: Scenario dict (with or without 'scenario' wrapper)

        Returns:
            True if stored successfully
        """

        # Handle both formats
        if 'scenario' in scenario:
            scenario = scenario['scenario']

        scenario_id = scenario.get('id')

        if not self.qdrant or not self.llm:
            logger.warning(f"⚠️  RAG not available, scenario {scenario_id} not stored")
            return False

        try:
            # Create embedding-friendly text
            scenario_text = self._format_scenario_for_embedding(scenario)

            # Generate embeddings
            embeddings = await self.llm.generate_embeddings([scenario_text])

            # Prepare metadata
            payload = {
                "scenario_id": scenario_id,
                "type": scenario.get('type'),
                "category": scenario.get('category'),
                "level": scenario.get('level'),
                "description": scenario.get('description'),
                "business_value": scenario.get('business_value', ''),
                "scenario": scenario  # Store full scenario
            }

            # Store in Qdrant
            await self.qdrant.upsert(
                collection_name=self.collection_name,
                points=[{
                    "id": scenario_id,
                    "vector": embeddings[0],
                    "payload": payload
                }]
            )

            logger.info(f"✅ Stored scenario in RAG: {scenario_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to store scenario {scenario_id}: {e}")
            return False

    async def find_similar_scenarios(
        self,
        query: str,
        scenario_type: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[dict]:
        """
        Find scenarios similar to query

        Args:
            query: Search query
            scenario_type: Filter by type (system_test, user_workflow)
            category: Filter by category (chaos_engineering, security_testing, etc.)
            limit: Max results
            score_threshold: Minimum similarity score

        Returns:
            List of matching scenarios
        """

        if not self.qdrant or not self.llm:
            logger.warning(f"⚠️  RAG not available, returning empty results")
            return []

        try:
            # Generate query embedding
            query_embedding = await self.llm.generate_embeddings([query])

            # Build filter
            filter_conditions = []

            if scenario_type:
                filter_conditions.append({
                    "key": "type",
                    "match": {"value": scenario_type}
                })

            if category:
                filter_conditions.append({
                    "key": "category",
                    "match": {"value": category}
                })

            qdrant_filter = None
            if filter_conditions:
                qdrant_filter = {
                    "must": filter_conditions
                }

            # Search Qdrant
            results = await self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_embedding[0],
                limit=limit,
                score_threshold=score_threshold,
                filter=qdrant_filter
            )

            # Extract scenarios
            scenarios = []
            for result in results:
                scenario = result['payload']['scenario']
                scenario['_similarity_score'] = result.get('score', 0.0)
                scenarios.append(scenario)

            logger.info(f"🔍 Found {len(scenarios)} similar scenarios for query: {query}")

            return scenarios

        except Exception as e:
            logger.error(f"❌ Failed to search scenarios: {e}")
            return []

    async def get_scenario_by_id(self, scenario_id: str) -> Optional[dict]:
        """Get scenario by exact ID"""

        if not self.qdrant:
            logger.warning(f"⚠️  RAG not available")
            return None

        try:
            result = await self.qdrant.retrieve(
                collection_name=self.collection_name,
                ids=[scenario_id]
            )

            if result and len(result) > 0:
                return result[0]['payload']['scenario']

            return None

        except Exception as e:
            logger.error(f"❌ Failed to get scenario {scenario_id}: {e}")
            return None

    async def list_all_scenarios(
        self,
        scenario_type: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[dict]:
        """List all scenarios (with optional filters)"""

        if not self.qdrant:
            logger.warning(f"⚠️  RAG not available")
            return []

        try:
            # Build filter
            filter_conditions = []

            if scenario_type:
                filter_conditions.append({
                    "key": "type",
                    "match": {"value": scenario_type}
                })

            if category:
                filter_conditions.append({
                    "key": "category",
                    "match": {"value": category}
                })

            qdrant_filter = None
            if filter_conditions:
                qdrant_filter = {
                    "must": filter_conditions
                }

            # Scroll through all points
            results = await self.qdrant.scroll(
                collection_name=self.collection_name,
                limit=100,
                filter=qdrant_filter
            )

            scenarios = [r['payload']['scenario'] for r in results]

            logger.info(f"📋 Listed {len(scenarios)} scenarios")

            return scenarios

        except Exception as e:
            logger.error(f"❌ Failed to list scenarios: {e}")
            return []

    async def delete_scenario(self, scenario_id: str) -> bool:
        """Delete scenario from RAG"""

        if not self.qdrant:
            logger.warning(f"⚠️  RAG not available")
            return False

        try:
            await self.qdrant.delete(
                collection_name=self.collection_name,
                points_selector=[scenario_id]
            )

            logger.info(f"🗑️  Deleted scenario: {scenario_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete scenario {scenario_id}: {e}")
            return False

    async def update_scenario(self, scenario: dict) -> bool:
        """Update existing scenario (re-store with same ID)"""

        # Just re-store (upsert will update)
        return await self.store_scenario(scenario)

    def _format_scenario_for_embedding(self, scenario: dict) -> str:
        """Format scenario as text for embedding generation"""

        parts = []

        # Basic info
        parts.append(f"Scenario ID: {scenario.get('id')}")
        parts.append(f"Type: {scenario.get('type')}")

        if scenario.get('category'):
            parts.append(f"Category: {scenario.get('category')}")

        if scenario.get('level'):
            parts.append(f"Level: {scenario.get('level')}")

        # Description
        if scenario.get('description'):
            parts.append(f"Description: {scenario.get('description')}")

        # Business value
        if scenario.get('business_value'):
            parts.append(f"Business Value: {scenario.get('business_value')}")

        # Steps summary
        if scenario.get('steps'):
            steps_summary = self._summarize_steps(scenario['steps'])
            parts.append(f"Steps: {steps_summary}")

        # Assertions summary
        if scenario.get('assertions'):
            assertions_summary = self._summarize_assertions(scenario['assertions'])
            parts.append(f"Validations: {assertions_summary}")

        # Context (for user workflows)
        if scenario.get('context'):
            context = scenario['context']
            if context.get('user_role'):
                parts.append(f"User Role: {context['user_role']}")
            if context.get('organization'):
                parts.append(f"Organization: {context['organization']}")

        return "\n".join(parts)

    def _summarize_steps(self, steps: List[dict]) -> str:
        """Summarize scenario steps for embedding"""

        summaries = []

        for step in steps[:5]:  # Limit to first 5 steps
            step_id = step.get('id', '')
            service = step.get('service', '')
            action = step.get('action', '')

            if service and action:
                summaries.append(f"{step_id}: {service}.{action}")
            elif action:
                summaries.append(f"{step_id}: {action}")

        if len(steps) > 5:
            summaries.append(f"... and {len(steps) - 5} more steps")

        return ", ".join(summaries)

    def _summarize_assertions(self, assertions: List[dict]) -> str:
        """Summarize scenario assertions for embedding"""

        types = [a.get('type', '') for a in assertions]
        return ", ".join(types)

    async def create_collection_if_not_exists(self):
        """Create Qdrant collection for scenarios if it doesn't exist"""

        if not self.qdrant:
            logger.warning(f"⚠️  RAG not available")
            return False

        try:
            # Check if collection exists
            collections = await self.qdrant.list_collections()

            if self.collection_name not in [c.name for c in collections]:
                # Create collection
                await self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vector_size=3072,  # OpenAI text-embedding-3-large size
                    distance="Cosine"
                )

                logger.info(f"✅ Created collection: {self.collection_name}")
                return True
            else:
                logger.info(f"✅ Collection already exists: {self.collection_name}")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to create collection: {e}")
            return False


# Helper functions for easy usage

async def store_scenario(scenario: dict) -> bool:
    """Store scenario in RAG (convenience function)"""
    rag = ScenarioRAGIntegration()
    return await rag.store_scenario(scenario)


async def find_scenarios(query: str, scenario_type: str = None, limit: int = 5) -> List[dict]:
    """Find scenarios by query (convenience function)"""
    rag = ScenarioRAGIntegration()
    return await rag.find_similar_scenarios(query, scenario_type=scenario_type, limit=limit)


async def get_scenario(scenario_id: str) -> Optional[dict]:
    """Get scenario by ID (convenience function)"""
    rag = ScenarioRAGIntegration()
    return await rag.get_scenario_by_id(scenario_id)


# Test
async def main():
    """Test RAG integration"""

    rag = ScenarioRAGIntegration()

    # Test scenario
    test_scenario = {
        "id": "test-bia-workflow",
        "type": "user_workflow",
        "category": "business_process",
        "level": 4,
        "description": "Complete BIA workflow for healthcare organization",
        "business_value": "ISO 22301 compliance + risk mitigation",
        "steps": [
            {
                "id": "create_assessment",
                "service": "bia-service",
                "action": "create_assessment",
                "params": {"name": "Q1 BIA"}
            }
        ],
        "assertions": [
            {"type": "compliance", "check": "ISO_22301_clause_8.2.2"}
        ]
    }

    # Store
    print("\n📝 Storing test scenario...")
    success = await rag.store_scenario(test_scenario)
    print(f"  {'✅' if success else '❌'} Store result: {success}")

    # Search
    print("\n🔍 Searching for BIA scenarios...")
    results = await rag.find_similar_scenarios(
        query="healthcare BIA workflow",
        scenario_type="user_workflow"
    )
    print(f"  Found {len(results)} scenarios:")
    for scenario in results:
        print(f"    - {scenario['id']}: {scenario.get('description', 'No description')}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
