"""
Load 328 parsed scenarios to PostgreSQL KQM database
"""

import json
import psycopg2
from urllib.parse import quote_plus
from datetime import datetime

# Database connection
password = quote_plus('K@x3ta9V8GK5rnW')
db_url = f'postgresql://postgres.tpdkhddtbhpoqzzgxfni:{password}@aws-1-eu-north-1.pooler.supabase.com:5432/postgres'

# Load scenarios
scenarios_file = '/Users/MD/AI-Platform-ISO/platform-services/docs/business-scenarios/scenarios_parsed.json'

print("=" * 60)
print("📦 LOADING SCENARIOS TO KQM DATABASE")
print("=" * 60)

print(f"\n📄 Loading scenarios from: {scenarios_file}")

with open(scenarios_file, 'r', encoding='utf-8') as f:
    scenarios = json.load(f)

print(f"✅ Loaded {len(scenarios)} scenarios")

# Connect to database
print("\n🔌 Connecting to PostgreSQL...")
conn = psycopg2.connect(db_url)
cur = conn.cursor()
print("✅ Connected")

# Insert scenarios
print("\n💾 Inserting scenarios...")

inserted = 0
skipped = 0

for scenario in scenarios:
    try:
        # Generate ID
        scenario_id = f"existing_{scenario.get('title', 'unknown').replace(' ', '_').replace('.', '_')[:100]}"

        # Insert
        cur.execute("""
            INSERT INTO public.kqm_scenarios (
                id, title, content, type,
                service, category, iso_clause,
                source, confidence,
                inputs, outputs, events, components
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            scenario_id,
            scenario.get('title', 'Untitled'),
            scenario.get('content', scenario.get('title', '')),
            'existing',
            scenario.get('service'),
            scenario.get('category'),
            scenario.get('iso_clause'),
            'ALL_USAGE_SCENARIOS_CATALOG.md',
            0.9,  # High confidence for existing scenarios
            scenario.get('inputs'),
            scenario.get('outputs'),
            scenario.get('events'),
            scenario.get('components')
        ))

        if cur.rowcount > 0:
            inserted += 1
        else:
            skipped += 1

    except Exception as e:
        print(f"❌ Error inserting scenario '{scenario.get('title', 'unknown')}': {e}")
        continue

conn.commit()

print(f"\n✅ Inserted: {inserted} scenarios")
print(f"⏭️  Skipped: {skipped} (already exist)")

# Verify
cur.execute("SELECT COUNT(*) FROM public.kqm_scenarios")
total = cur.fetchone()[0]

print(f"\n📊 Total scenarios in DB: {total}")

# Calculate knowledge values
print("\n💰 Calculating knowledge values...")

cur.execute("SELECT id FROM public.kqm_scenarios LIMIT 10")
sample_ids = [row[0] for row in cur.fetchall()]

for scenario_id in sample_ids:
    cur.execute("SELECT public.calculate_kqm_knowledge_value(%s)", (scenario_id,))
    value = cur.fetchone()[0]

conn.commit()

print(f"✅ Knowledge values calculated for sample scenarios")

# Show statistics
print("\n" + "=" * 60)
print("📊 STATISTICS")
print("=" * 60)

# By service
cur.execute("""
    SELECT service, COUNT(*) as count
    FROM public.kqm_scenarios
    WHERE service IS NOT NULL
    GROUP BY service
    ORDER BY count DESC
""")

print("\n📦 By Service:")
for service, count in cur.fetchall():
    print(f"   {service}: {count}")

# By type
cur.execute("""
    SELECT type, COUNT(*) as count
    FROM public.kqm_scenarios
    GROUP BY type
""")

print("\n🏷️  By Type:")
for stype, count in cur.fetchall():
    print(f"   {stype}: {count}")

cur.close()
conn.close()

print("\n" + "=" * 60)
print("✅ SCENARIOS LOADED SUCCESSFULLY!")
print("=" * 60)
