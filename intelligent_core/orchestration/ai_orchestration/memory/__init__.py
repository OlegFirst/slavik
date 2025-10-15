"""
Distributed Memory System
==========================

4-layer memory architecture:

1. Working Memory (Redis):
   - Current context
   - Active workflows
   - Recent events
   - TTL: 1 hour

2. Short-Term Memory (PostgreSQL):
   - Recent decisions
   - Last 30 days
   - Fast retrieval

3. Long-Term Memory (Case Library + Vector DB):
   - Historical cases
   - Permanent storage
   - Semantic search

4. Procedural Memory (ML Models):
   - Learned patterns
   - Optimized strategies
   - Continuous improvement
"""

from .distributed_memory import DistributedMemory
from .working_memory import WorkingMemory
from .short_term_memory import ShortTermMemory
from .long_term_memory import LongTermMemory
from .procedural_memory import ProceduralMemory

__all__ = [
    'DistributedMemory',
    'WorkingMemory',
    'ShortTermMemory',
    'LongTermMemory',
    'ProceduralMemory'
]
