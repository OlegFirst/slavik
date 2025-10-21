#!/usr/bin/env python3
"""Fix indentation issues in specialists"""
import re
from pathlib import Path

FILES = [
    "governance_specialist.py",
    "validation_specialist.py",
    "learning_specialist.py"
]

BASE_PATH = Path(__file__).parent / "domains/bcm/tactical_assistants"

for filename in FILES:
    filepath = BASE_PATH / filename
    if not filepath.exists():
        continue

    print(f"Fixing {filename}...")

    with open(filepath, 'r') as f:
        content = f.read()

    # Fix: self.config = config or {}\nself.xxx = 0
    content = re.sub(
        r'(\s+)self\.config = config or \{\}\n(\w+)',
        r'\1self.config = config or {}\n\1\2',
        content
    )

    # Fix: logger.info(...)\n    def _build_system_prompt
    content = re.sub(
        r'(logger\.info\([^\)]+\))\n    def _build_system_prompt',
        r'\1\n\n    async def assist(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:\n        """Execute task using ai-foundation"""\n        pass\n\n    def _build_system_prompt',
        content
    )

    # Fix: AssistantContext -> Dict[str, Any]
    content = content.replace('context: AssistantContext', 'context: Dict[str, Any]')

    # Fix config.get to self.config.get
    content = re.sub(r'config\.get\(', 'self.config.get(', content)

    with open(filepath, 'w') as f:
        f.write(content)

    print(f"   Fixed {filename}")

print("\n All files fixed")
