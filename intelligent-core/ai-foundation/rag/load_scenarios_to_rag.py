"""
Load Business Scenarios Catalog to RAG

Loads ALL_USAGE_SCENARIOS_CATALOG.md (570+ scenarios) into Qdrant
instead of rewriting them in detailed files.
"""

import os
import sys
import logging
from typing import List, Dict
from pathlib import Path

# Fix circular import - rename conflicting file or import directly
try:
    from qdrant_client import QdrantClient as QdrantClientLib
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    print("Installing required packages...")
    os.system("pip install -q qdrant-client sentence-transformers")
    from qdrant_client import QdrantClient as QdrantClientLib
    from qdrant_client.models import Distance, VectorParams, PointStruct

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    os.system("pip install -q sentence-transformers")
    from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class ScenarioLoader:
    """Load scenarios from markdown catalog to Qdrant"""

    def __init__(self, qdrant_url: str = None, qdrant_api_key: str = None):
        """Initialize loader"""
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL")
        self.qdrant_api_key = qdrant_api_key or os.getenv("QDRANT_API_KEY")

        if self.qdrant_url and self.qdrant_api_key:
            self.client = QdrantClientLib(url=self.qdrant_url, api_key=self.qdrant_api_key)
        else:
            # Local mode
            logger.warning("No Qdrant credentials - using local mode")
            self.client = QdrantClientLib(path="./qdrant_local")

        # Embedding model
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_size = 384  # all-MiniLM-L6-v2 output size

    def create_scenario_collection(self):
        """Create business_scenarios collection"""
        collection_name = "business_scenarios"

        try:
            collections = self.client.get_collections().collections
            if any(c.name == collection_name for c in collections):
                logger.info(f"Collection {collection_name} already exists")
                return

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )

            # Create indexes for filtering
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="service",
                field_schema="keyword"
            )

            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="category",
                field_schema="keyword"
            )

            logger.info(f"✅ Created collection: {collection_name}")

        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise

    def parse_catalog(self, catalog_path: str) -> List[Dict]:
        """
        Parse ALL_USAGE_SCENARIOS_CATALOG.md into structured scenarios

        Returns:
            List of scenarios with metadata
        """
        with open(catalog_path, 'r', encoding='utf-8') as f:
            content = f.read()

        scenarios = []
        current_service = None
        current_category = None

        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Detect service headers (### 1. BIA Service - 25 сценариев)
            if line.startswith('###') and 'Service' in line and 'сценариев' in line:
                # Extract service name
                parts = line.split('.')
                if len(parts) > 1:
                    service_part = parts[1].split('-')[0].strip()
                    current_service = service_part
                    logger.info(f"Found service: {current_service}")

            # Detect category headers (#### Основные сценарии)
            elif line.startswith('####'):
                current_category = line.replace('#', '').strip()

            # Detect scenario (**1.1 Start New BIA**)
            elif line.startswith('**') and '.' in line and not line.startswith('**Входы'):
                scenario_title = line.replace('**', '').strip()

                # Extract scenario details
                scenario = {
                    'title': scenario_title,
                    'service': current_service or 'Unknown',
                    'category': current_category or 'General',
                    'inputs': '',
                    'outputs': '',
                    'events': '',
                    'components': ''
                }

                # Read next lines for details
                j = i + 1
                while j < len(lines) and not lines[j].startswith('**'):
                    detail_line = lines[j].strip()

                    if detail_line.startswith('- Входы:'):
                        scenario['inputs'] = detail_line.replace('- Входы:', '').strip()
                    elif detail_line.startswith('- Выходы:'):
                        scenario['outputs'] = detail_line.replace('- Выходы:', '').strip()
                    elif detail_line.startswith('- События:'):
                        scenario['events'] = detail_line.replace('- События:', '').strip()
                    elif detail_line.startswith('- Компоненты:'):
                        scenario['components'] = detail_line.replace('- Компоненты:', '').strip()

                    j += 1

                scenarios.append(scenario)

            i += 1

        logger.info(f"✅ Parsed {len(scenarios)} scenarios from catalog")
        return scenarios

    def load_scenarios_to_qdrant(self, scenarios: List[Dict]):
        """Load scenarios into Qdrant"""

        collection_name = "business_scenarios"
        points = []

        for idx, scenario in enumerate(scenarios):
            # Create searchable text
            text = f"""
            {scenario['title']}
            Service: {scenario['service']}
            Category: {scenario['category']}
            Inputs: {scenario['inputs']}
            Outputs: {scenario['outputs']}
            Events: {scenario['events']}
            Components: {scenario['components']}
            """.strip()

            # Generate embedding
            embedding = self.encoder.encode(text).tolist()

            # Create point
            point = PointStruct(
                id=idx,
                vector=embedding,
                payload={
                    "title": scenario['title'],
                    "service": scenario['service'],
                    "category": scenario['category'],
                    "inputs": scenario['inputs'],
                    "outputs": scenario['outputs'],
                    "events": scenario['events'],
                    "components": scenario['components'],
                    "full_text": text
                }
            )

            points.append(point)

        # Upload in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            self.client.upsert(
                collection_name=collection_name,
                points=batch
            )
            logger.info(f"Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")

        logger.info(f"✅ Loaded {len(scenarios)} scenarios to Qdrant")

    def load_catalog(self, catalog_path: str):
        """
        Main method: Load catalog to RAG

        Args:
            catalog_path: Path to ALL_USAGE_SCENARIOS_CATALOG.md
        """
        logger.info(f"Loading catalog from: {catalog_path}")

        # 1. Create collection
        self.create_scenario_collection()

        # 2. Parse catalog
        scenarios = self.parse_catalog(catalog_path)

        # 3. Load to Qdrant
        self.load_scenarios_to_qdrant(scenarios)

        # 4. Verify
        collection_info = self.client.get_collection("business_scenarios")
        logger.info(f"✅ Collection now has {collection_info.points_count} points")

    def search_scenarios(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search scenarios by query

        Args:
            query: Search query (e.g., "How to conduct BIA?")
            top_k: Number of results

        Returns:
            List of matching scenarios
        """
        query_vector = self.encoder.encode(query).tolist()

        results = self.client.search(
            collection_name="business_scenarios",
            query_vector=query_vector,
            limit=top_k
        )

        scenarios = []
        for result in results:
            scenarios.append({
                "title": result.payload['title'],
                "service": result.payload['service'],
                "score": result.score,
                "inputs": result.payload['inputs'],
                "outputs": result.payload['outputs'],
                "events": result.payload['events'],
                "components": result.payload['components']
            })

        return scenarios


def main():
    """Main script to load catalog"""
    logging.basicConfig(level=logging.INFO)

    # Path to catalog
    catalog_path = "/Users/MD/AI-Platform-ISO/platform-services/docs/business-scenarios/ALL_USAGE_SCENARIOS_CATALOG.md"

    if not os.path.exists(catalog_path):
        logger.error(f"Catalog not found: {catalog_path}")
        return

    # Load
    loader = ScenarioLoader()
    loader.load_catalog(catalog_path)

    # Test search
    logger.info("\n🔍 Testing search...")
    results = loader.search_scenarios("How to conduct BIA interview?", top_k=3)

    for i, result in enumerate(results, 1):
        logger.info(f"\n{i}. {result['title']} (score: {result['score']:.3f})")
        logger.info(f"   Service: {result['service']}")
        logger.info(f"   Components: {result['components']}")


if __name__ == "__main__":
    main()
