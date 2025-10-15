#!/usr/bin/env python3
"""
Массовое обновление tactical assistants для интеграции с ai-foundation
"""
import re
from pathlib import Path

# Список файлов для обновления
FILES_TO_UPDATE = [
    "compliance_copilot.py",
    "incident_advisor.py",
    "plan_generator.py",
    "project_manager.py",
    "exercise_designer.py",
    "documents_specialist.py",
    "governance_specialist.py",
    "validation_specialist.py",
    "community_specialist.py",
    "learning_specialist.py",
]

BASE_PATH = Path(__file__).parent / "domains/bcm/tactical_assistants"

def update_imports(content: str) -> str:
    """Update imports to use ai-foundation"""
    # Replace old imports
    content = re.sub(
        r'from colleagues\.base import.*?\n',
        'from expertise_center.shared.base import BaseTacticalAssistant\n',
        content
    )
    content = re.sub(
        r'from core import RAGPipeline.*?\n',
        'from intelligent_core.ai_foundation import RAGPipeline, LLMRouter, ContextBuilder\n',
        content
    )

    # Add Optional if not present
    if 'from typing import' in content and 'Optional' not in content:
        content = content.replace(
            'from typing import',
            'from typing import Optional,'
        )

    return content

def update_class_declaration(content: str) -> str:
    """Update class to extend BaseTacticalAssistant"""
    content = re.sub(
        r'class (\w+)\(BaseAIColleague\):',
        r'class \1(BaseTacticalAssistant):',
        content
    )
    return content

def update_init_method(content: str, class_name: str, assistant_id: str) -> str:
    """Update __init__ to use ai-foundation"""
    # Find existing __init__ method
    init_pattern = r'def __init__\(self.*?\):(.*?)(?=\n    def |\n\nclass |\Z)'

    def replace_init(match):
        # Extract name and specialty from old init
        old_init = match.group(0)

        # Try to extract name
        name_match = re.search(r'name="([^"]+)"', old_init)
        name = name_match.group(1) if name_match else class_name

        # Try to extract specialty
        specialty_match = re.search(r'specialty="([^"]+)"', old_init)
        specialty = specialty_match.group(1) if specialty_match else "BCM Expert"

        # Build new init
        new_init = f'''def __init__(self, config: Dict[str, Any] = None):
        """Initialize {class_name}."""
        super().__init__(
            assistant_id="{assistant_id}",
            name="{name}",
            specialty="{specialty}",
            domain="bcm"
        )

        # AI Foundation integrations
        self.rag = RAGPipeline()
        self.llm = LLMRouter()
        self.context_builder = ContextBuilder()

        self.config = config or {{}}'''

        # Preserve any custom initialization after super().__init__
        custom_init = re.search(r'super\(\).__init__\(.*?\)(.+?)(?=logger\.info|\n    def |\Z)', old_init, re.DOTALL)
        if custom_init:
            custom_lines = custom_init.group(1).strip()
            if custom_lines and 'self.' in custom_lines:
                new_init += '\n' + custom_lines

        # Preserve logger.info if exists
        logger_match = re.search(r'logger\.info\([^\)]+\)', old_init)
        if logger_match:
            new_init += '\n\n        ' + logger_match.group(0)

        return new_init

    content = re.sub(init_pattern, replace_init, content, flags=re.DOTALL)
    return content

def process_file(filepath: Path):
    """Process a single file"""
    print(f"Processing {filepath.name}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract class name
    class_match = re.search(r'class (\w+)\(', content)
    if not class_match:
        print(f"  ❌ Could not find class in {filepath.name}")
        return

    class_name = class_match.group(1)
    assistant_id = filepath.stem  # e.g., "compliance_copilot"

    # Apply updates
    content = update_imports(content)
    content = update_class_declaration(content)
    content = update_init_method(content, class_name, assistant_id)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  ✅ Updated {filepath.name}")

def main():
    """Main update function"""
    print("🚀 Starting tactical assistants update...")
    print(f"Base path: {BASE_PATH}")
    print()

    updated = 0
    for filename in FILES_TO_UPDATE:
        filepath = BASE_PATH / filename
        if filepath.exists():
            try:
                process_file(filepath)
                updated += 1
            except Exception as e:
                print(f"  ❌ Error processing {filename}: {e}")
        else:
            print(f"  ⚠️  File not found: {filename}")

    print()
    print(f"✅ Updated {updated}/{len(FILES_TO_UPDATE)} files")

if __name__ == "__main__":
    main()
