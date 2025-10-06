#!/usr/bin/env python3
import csv
import json

CSV_FILE = "/Users/MD/Downloads/Supabase Performance Security Lints (tpdkhddtbhpoqzzgxfni) (2).csv"

tables_with_issues = set()

with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['name'] == 'multiple_permissive_policies':
            try:
                metadata = json.loads(row['metadata'])
                schema = metadata['schema']
                table = metadata['name']
                tables_with_issues.add(f"{schema}.{table}")
            except:
                pass

print(f"Total unique tables with multiple_permissive_policies issues: {len(tables_with_issues)}")
print("\nTables:")
for table in sorted(tables_with_issues):
    print(f"  - {table}")
