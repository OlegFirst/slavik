"""
Complete RAG Setup for KQM
Loads 328 scenarios from PostgreSQL to Qdrant
"""

import os
import sys
import json
import logging
import psycopg2
from urllib.parse import quote_plus

# Add paths
sys.path.insert(0, '/Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation')

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    from sentence_transformers import SentenceTransformer
except ImportError:
    print(" Installing required packages...")
    os.system("pip3 install -q qdrant-client sentence-transformers")
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
password = quote_plus('K@x3ta9V8GK5rnW')
db_url = f'postgresql://postgres.tpdkhddtbhpoqzzgxfni:{password}@aws-1-eu-north-1.pooler.supabase.com:5432/postgres'

print("=" * 60)
print(" KQM RAG SETUP - COMPLETE")
print("=" * 60)

# 1. Load scenarios from PostgreSQL
print("\n Step 1: Loading scenarios from PostgreSQL...")
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

print(f" Loaded {len(scenarios)} scenarios from database")

# 2. Setup Qdrant
print("\n Step 2: Setting up Qdrant...")

# Local mode (no server needed)
client = QdrantClient(path="./qdrant_local")
encoder = SentenceTransformer('all-MiniLM-L6-v2')
vector_size = 384

collection_name = "business_scenarios"

# Check if collection exists
try:
    collections = client.get_collections().collections
    if any(c.name == collection_name for c in collections):
        print(f"️  Collection {collection_name} exists - deleting...")
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

print(f" Created collection: {collection_name}")

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

print(" Created indexes")

# 3. Generate embeddings and upload
print("\n Step 3: Generating embeddings...")

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

    # Generate embedding
    embedding = encoder.encode(text).tolist()

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

print(f" Generated {len(points)} embeddings")

# 4. Upload to Qdrant
print("\n Step 4: Uploading to Qdrant...")

batch_size = 100
for i in range(0, len(points), batch_size):
    batch = points[i:i+batch_size]
    client.upsert(
        collection_name=collection_name,
        points=batch
    )
    print(f"   Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")

print(f" Uploaded all scenarios to Qdrant")

# 5. Verify
print("\n Step 5: Verification...")
collection_info = client.get_collection(collection_name)
print(f"   Collection: {collection_name}")
print(f"   Points: {collection_info.points_count}")
print(f"   Vector size: {collection_info.config.params.vectors.size}")

# 6. Test search
print("\n Step 6: Testing search...")

test_queries = [
    "How to conduct BIA?",
    "ISO 22301 compliance",
    "Risk assessment"
]

for query in test_queries:
    query_vector = encoder.encode(query).tolist()
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
print("\n Step 7: Saving configuration...")

config = {
    "qdrant_path": "./qdrant_local",
    "collection_name": "business_scenarios",
    "vector_size": 384,
    "model": "all-MiniLM-L6-v2",
    "total_scenarios": len(scenarios),
    "last_updated": "2025-10-11"
}

with open("qdrant_config.json", "w") as f:
    json.dump(config, f, indent=2)

print(" Saved qdrant_config.json")

print("\n" + "=" * 60)
print(" RAG SETUP COMPLETE!")
print("=" * 60)
print(f"\n Summary:")
print(f"   Database: {len(scenarios)} scenarios loaded")
print(f"   Qdrant: {collection_info.points_count} points")
print(f"   Model: all-MiniLM-L6-v2 (384-dim)")
print(f"   Location: ./qdrant_local")
print(f"\n Next: Update KQM settings to use RAG")
