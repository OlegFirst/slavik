#!/usr/bin/env python3
"""Simple standalone test"""

from iso_loader import ISO22301Loader
from knowledge_graph import KnowledgeGraphBuilder, NodeType

print("\n" + "=" * 70)
print("  ISO-22301-LIBRARY INTEGRATION TEST")
print("=" * 70)

# Test 1
print("\n Loading ISO clauses...")
loader = ISO22301Loader("/Users/MD/AI-Platform-ISO/ISO-22301-Library")
clauses = loader.load_all_clauses()
print(f"   Loaded: {len(clauses)} clauses")

# Test 2
print("\n Get BIA clause...")
bia = loader.get_clause_by_number("8.2.2")
print(f"   {bia.clause_number}: {bia.clause_title}")
print(f"   Requirements: {len(bia.requirements)}")

# Test 3
print("\n Building Knowledge Graph...")
builder = KnowledgeGraphBuilder()
kg = builder.build_from_iso_clauses(clauses)
stats = kg.get_statistics()
print(f"   Nodes: {stats['total_nodes']}, Edges: {stats['total_edges']}")

# Test 4
print("\n Query BIA evidence...")
evidence = kg.get_iso_clause_evidence('8.2.2')
print(f"   Evidence items: {len(evidence)}")

# Test 5
print("\n BCI mapping...")
practice = kg.get_bci_practice_for_clause('8.2.2')
print(f"   BCI Practice: {practice}")

# Test 6
print("\n Operation clauses...")
operation = kg.query(node_type=NodeType.ISO_CLAUSE, filters={'category': 'operation'})
print(f"   Operation clauses: {len(operation)}")

print("\n" + "=" * 70)
print("   ALL TESTS PASSED!")
print("=" * 70)
print(f"\nKnowledge Base Ready:")
print(f"  - ISO Clauses: {len(clauses)}")
print(f"  - Graph Nodes: {stats['total_nodes']}")
print(f"  - Graph Edges: {stats['total_edges']}")
print("\n" + "=" * 70 + "\n")
