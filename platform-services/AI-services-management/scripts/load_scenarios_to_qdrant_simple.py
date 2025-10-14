"""
Simple RAG Setup for KQM - Python 3.9 Compatible
Loads 328 scenarios from PostgreSQL to Qdrant without sentence-transformers
Uses mock embeddings for development
"""

import os
import sys
import json
import logging
import psycopg2
from urllib.parse import quote_plus
import random

# Add paths
sys.path.insert(0, '/Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation')

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    print("📦 Installing qdrant-client...")
    os.system("pip3 install -q qdrant-client")
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_mock_embedding(text: str, dimension: int = 384) -> list:
    """
    Generate mock embedding for development

    In production, this would be replaced with:
    - Voyage AI embeddings
    - OpenAI embeddings
    - or sentence-transformers (Python 3.10+)
    """
    # Deterministic random based on text hash
    random.seed(hash(text) % (2**32))

    # Generate normalized random vector
    vector = [random.gauss(0, 1) for _ in range(dimension)]

    # Normalize
    magnitude = sum(x**2 for x in vector) ** 0.5
    vector = [x / magnitude for x in vector]

    return vector


print("=" * 60)
print("🚀 KQM RAG SETUP - Simple (Python 3.9 Compatible)")
print("=" * 60)

# Database connection
password = quote_plus('K@x3ta9V8GK5rnW')
db_url = f'postgresql://postgres.tpdkhddtbhpoqzzgxfni:{password}@aws-1-eu-north-1.pooler.supabase.com:5432/postgres'

# 1. Load scenarios from PostgreSQL
print("\n📊 Step 1: Loading scenarios from PostgreSQL...")
conn = psycopg2.connect(db_url)
cur = conn.cursor()

cur.execute("""
    SELECT id, title, content, service, category, iso_clause,
           inputs, outputs, events, components, confidence
    FROM public.kqm_scenarios
    ORDER BY created_at DESC
""")

scenarios = []
for row in cur.fetchall():
    scenarios.append({
        'id': row[0],
        'title': row[1],
        'content': row[2],
        'service': row[3],
        'category': row[4],
        'iso_clause': row[5],
        'inputs': row[6],
        'outputs': row[7],
        'events': row[8],
        'components': row[9],
        'confidence': float(row[10]) if row[10] else 0.9
    })

cur.close()
conn.close()

print(f"✅ Loaded {len(scenarios)} scenarios from database")

# 2. Setup Qdrant (Local mode - no server needed)
print("\n🔧 Step 2: Setting up Qdrant...")

qdrant_path = "./qdrant_local"
client = QdrantClient(path=qdrant_path)
vector_size = 384  # Standard embedding dimension
collection_name = "business_scenarios"

# Check if collection exists
try:
    collections = client.get_collections().collections
    if any(c.name == collection_name for c in collections):
        print(f"⚠️  Collection {collection_name} exists - deleting...")
        client.delete_collection(collection_name)
except:
    pass

# Create collection
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=vector_size,
        distance=Distance.COSINE
    )
)

print(f"✅ Created collection: {collection_name}")

# Create indexes
client.create_payload_index(
    collection_name=collection_name,
    field_name="service",
    field_schema="keyword"
)

client.create_payload_index(
    collection_name=collection_name,
    field_name="iso_clause",
    field_schema="keyword"
)

print("✅ Created indexes")

# 3. Generate embeddings and upload
print("\n🤖 Step 3: Generating embeddings (mock for development)...")

points = []
for idx, scenario in enumerate(scenarios):
    # Create searchable text
    text = f"""
    {scenario['title']}
    {scenario['content'][:500]}
    Service: {scenario['service']}
    Category: {scenario['category']}
    ISO Clause: {scenario['iso_clause']}
    Inputs: {scenario['inputs']}
    Outputs: {scenario['outputs']}
    Components: {scenario['components']}
    """.strip()

    # Generate mock embedding
    embedding = generate_mock_embedding(text, dimension=vector_size)

    # Create point
    point = PointStruct(
        id=idx,
        vector=embedding,
        payload={
            "scenario_id": scenario['id'],
            "title": scenario['title'],
            "content": scenario['content'][:1000],  # First 1000 chars
            "service": scenario['service'],
            "category": scenario['category'],
            "iso_clause": scenario['iso_clause'],
            "inputs": scenario['inputs'],
            "outputs": scenario['outputs'],
            "events": scenario['events'],
            "components": scenario['components'],
            "confidence": scenario['confidence']
        }
    )

    points.append(point)

    if (idx + 1) % 50 == 0:
        print(f"   Generated embeddings: {idx + 1}/{len(scenarios)}")

print(f"✅ Generated {len(points)} embeddings")

# 4. Upload to Qdrant
print("\n💾 Step 4: Uploading to Qdrant...")

batch_size = 100
for i in range(0, len(points), batch_size):
    batch = points[i:i+batch_size]
    client.upsert(
        collection_name=collection_name,
        points=batch
    )
    print(f"   Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")

print(f"✅ Uploaded all scenarios to Qdrant")

# 5. Verify
print("\n✅ Step 5: Verification...")
collection_info = client.get_collection(collection_name)
print(f"   Collection: {collection_name}")
print(f"   Points: {collection_info.points_count}")
print(f"   Vector size: {collection_info.config.params.vectors.size}")

# 6. Test search
print("\n🔍 Step 6: Testing search...")

test_queries = [
    "How to conduct BIA?",
    "ISO 22301 compliance",
    "Risk assessment"
]

for query in test_queries:
    query_vector = generate_mock_embedding(query, dimension=vector_size)
    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=3
    )

    print(f"\n   Query: '{query}'")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result.payload['title']} (score: {result.score:.3f})")
        print(f"      Service: {result.payload['service']}")

# 7. Save connection info
print("\n📝 Step 7: Saving configuration...")

config = {
    "qdrant_path": qdrant_path,
    "collection_name": "business_scenarios",
    "vector_size": 384,
    "embedding_type": "mock",
    "total_scenarios": len(scenarios),
    "last_updated": "2025-10-11",
    "note": "Using mock embeddings for development. For production, use Voyage AI or OpenAI embeddings."
}

config_path = os.path.join(os.path.dirname(__file__), "..", "qdrant_config.json")
with open(config_path, "w") as f:
    json.dump(config, f, indent=2)

print(f"✅ Saved {config_path}")

print("\n" + "=" * 60)
print("✅ RAG SETUP COMPLETE!")
print("=" * 60)
print(f"\n📊 Summary:")
print(f"   Database: {len(scenarios)} scenarios loaded")
print(f"   Qdrant: {collection_info.points_count} points")
print(f"   Embeddings: Mock (development mode)")
print(f"   Location: {qdrant_path}")
print(f"\n🎯 Next: KQM can now use RAG for semantic search")
print(f"\n⚠️  Note: Using mock embeddings for Python 3.9 compatibility")
print(f"   For production, upgrade to Python 3.10+ and use real embeddings")
