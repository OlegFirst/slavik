"""
Qdrant RAG Integration для Scenario Intelligence
Semantic search сценариев через vector embeddings
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)
import openai

# Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
COLLECTION_NAME = "scenarios"
VECTOR_SIZE = 1536  # OpenAI ada-002 embeddings


class ScenarioRAGStorage:
    """
    RAG Storage для сценариев с Qdrant
    Provides semantic search через embeddings
    """

    def __init__(
        self,
        host: str = QDRANT_HOST,
        port: int = QDRANT_PORT
    ):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = COLLECTION_NAME

        # Setup OpenAI
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY

        # Ensure collection exists
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        try:
            self.client.get_collection(self.collection_name)
            print(f"✅ Qdrant collection '{self.collection_name}' exists")
        except Exception as e:
            print(f"📝 Creating Qdrant collection '{self.collection_name}'...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
            print(f"✅ Collection created")

    async def _create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for text using OpenAI

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        if not OPENAI_API_KEY:
            # Fallback: dummy embedding for testing
            import random
            return [random.random() for _ in range(VECTOR_SIZE)]

        try:
            response = await asyncio.to_thread(
                openai.Embedding.create,
                input=text,
                model="text-embedding-ada-002"
            )
            return response['data'][0]['embedding']
        except Exception as e:
            print(f"⚠️ OpenAI embedding failed: {e}")
            # Fallback to dummy
            import random
            return [random.random() for _ in range(VECTOR_SIZE)]

    def _scenario_to_text(self, scenario: Dict[str, Any]) -> str:
        """
        Convert scenario to text for embedding

        Args:
            scenario: Scenario dict

        Returns:
            Text representation
        """
        parts = []

        # Meta
        if 'meta' in scenario:
            meta = scenario['meta']
            parts.append(f"ID: {meta.get('id', '')}")
            parts.append(f"Type: {meta.get('type', '')}")
            parts.append(f"Level: {meta.get('level', '')}")
            parts.append(f"Pillar: {meta.get('pillar', '')}")

        # Description
        if 'description' in scenario:
            desc = scenario['description']
            parts.append(f"Title: {desc.get('title', '')}")
            parts.append(f"Summary: {desc.get('summary', '')}")
            parts.append(f"Business Value: {desc.get('business_value', '')}")

        # Behavior (Gherkin)
        if 'behavior' in scenario:
            behavior = scenario['behavior']
            parts.append(f"Feature: {behavior.get('feature', '')}")
            parts.append(f"Scenario: {behavior.get('scenario', '')}")

            if 'given' in behavior:
                parts.append("Given: " + ", ".join(behavior['given']))
            if 'when' in behavior:
                parts.append("When: " + ", ".join(behavior['when']))
            if 'then' in behavior:
                parts.append("Then: " + ", ".join(behavior['then']))

        return "\n".join(parts)

    async def index_scenario(self, scenario: Dict[str, Any]) -> bool:
        """
        Index scenario in Qdrant

        Args:
            scenario: Scenario dictionary

        Returns:
            Success status
        """
        try:
            scenario_id = scenario['meta']['id']

            # Create text representation
            text = self._scenario_to_text(scenario)

            # Create embedding
            embedding = await self._create_embedding(text)

            # Prepare payload (metadata)
            payload = {
                "scenario_id": scenario_id,
                "level": scenario['meta'].get('level'),
                "type": scenario['meta'].get('type'),
                "pillar": scenario['meta'].get('pillar'),
                "title": scenario.get('description', {}).get('title', ''),
                "summary": scenario.get('description', {}).get('summary', ''),
                "module": scenario.get('meta', {}).get('module'),
                "subsystem": scenario.get('meta', {}).get('subsystem'),
                "full_scenario": scenario  # Store full scenario
            }

            # Upsert to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=scenario_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )

            print(f"✅ Indexed scenario: {scenario_id}")
            return True

        except Exception as e:
            print(f"❌ Failed to index scenario: {e}")
            return False

    async def search_similar(
        self,
        query: str,
        limit: int = 5,
        level: Optional[int] = None,
        scenario_type: Optional[str] = None,
        pillar: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for similar scenarios

        Args:
            query: Search query
            limit: Max results
            level: Filter by level (1-4)
            scenario_type: Filter by type (functional, chaos, etc)
            pillar: Filter by AWS pillar

        Returns:
            List of matching scenarios
        """
        try:
            # Create query embedding
            query_embedding = await self._create_embedding(query)

            # Build filter
            filter_conditions = []

            if level is not None:
                filter_conditions.append(
                    FieldCondition(
                        key="level",
                        match=MatchValue(value=level)
                    )
                )

            if scenario_type is not None:
                filter_conditions.append(
                    FieldCondition(
                        key="type",
                        match=MatchValue(value=scenario_type)
                    )
                )

            if pillar is not None:
                filter_conditions.append(
                    FieldCondition(
                        key="pillar",
                        match=MatchValue(value=pillar)
                    )
                )

            search_filter = Filter(must=filter_conditions) if filter_conditions else None

            # Search in Qdrant
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=search_filter
            )

            # Format results
            scenarios = []
            for result in results:
                scenarios.append({
                    "scenario_id": result.payload["scenario_id"],
                    "score": result.score,
                    "level": result.payload.get("level"),
                    "type": result.payload.get("type"),
                    "title": result.payload.get("title"),
                    "summary": result.payload.get("summary"),
                    "full_scenario": result.payload.get("full_scenario")
                })

            return scenarios

        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []

    async def get_by_id(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Get scenario by ID

        Args:
            scenario_id: Scenario ID

        Returns:
            Scenario dict or None
        """
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[scenario_id]
            )

            if result:
                return result[0].payload.get("full_scenario")

            return None

        except Exception as e:
            print(f"❌ Failed to get scenario: {e}")
            return None

    async def delete_scenario(self, scenario_id: str) -> bool:
        """
        Delete scenario from Qdrant

        Args:
            scenario_id: Scenario ID

        Returns:
            Success status
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[scenario_id]
            )

            print(f"✅ Deleted scenario: {scenario_id}")
            return True

        except Exception as e:
            print(f"❌ Failed to delete scenario: {e}")
            return False

    async def index_all_scenarios(self, scenarios: List[Dict[str, Any]]):
        """
        Batch index multiple scenarios

        Args:
            scenarios: List of scenario dicts
        """
        print(f"📝 Indexing {len(scenarios)} scenarios...")

        success_count = 0
        for scenario in scenarios:
            if await self.index_scenario(scenario):
                success_count += 1

        print(f"✅ Indexed {success_count}/{len(scenarios)} scenarios")

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            return {"error": str(e)}


# Global instance
global_rag_storage: Optional[ScenarioRAGStorage] = None


def get_rag_storage() -> ScenarioRAGStorage:
    """Get or create global RAG storage instance"""
    global global_rag_storage

    if global_rag_storage is None:
        global_rag_storage = ScenarioRAGStorage()

    return global_rag_storage


# Example usage
async def example_usage():
    """Example usage of RAG storage"""

    storage = get_rag_storage()

    # Index a scenario
    scenario = {
        "meta": {
            "id": "test-scenario-1",
            "level": 1,
            "type": "functional",
            "pillar": "security"
        },
        "description": {
            "title": "Test Scenario",
            "summary": "This is a test scenario for authentication",
            "business_value": "Ensure secure authentication"
        },
        "behavior": {
            "feature": "Authentication",
            "scenario": "User login",
            "given": ["User exists", "Credentials are valid"],
            "when": ["User submits login form"],
            "then": ["User is authenticated", "Token is issued"]
        }
    }

    await storage.index_scenario(scenario)

    # Search
    results = await storage.search_similar(
        query="authentication and login",
        limit=5,
        level=1
    )

    print(f"Found {len(results)} similar scenarios:")
    for result in results:
        print(f"  - {result['title']} (score: {result['score']:.2f})")


if __name__ == "__main__":
    asyncio.run(example_usage())
