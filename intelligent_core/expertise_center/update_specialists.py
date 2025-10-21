#!/usr/bin/env python3
"""
Массовое обновление specialists для интеграции с ai-foundation
"""
import re
from pathlib import Path

FILES_TO_UPDATE = [
    "bcm_advisor.py",
    "compliance_auditor.py",
    "strategic_planner.py",
]

BASE_PATH = Path(__file__).parent / "domains/bcm/specialists"

def update_file(filepath: Path):
    """Update a single specialist file"""
    print(f"Processing {filepath.name}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract class name
    class_match = re.search(r'class (\w+)\(', content)
    if not class_match:
        print(f"   Could not find class")
        return

    class_name = class_match.group(1)
    specialist_id = filepath.stem  # e.g., "bcm_advisor"

    # Replace imports
    new_imports = '''"""
{docstring}
"""

from typing import Dict, Any, Optional, List
from expertise_center.shared.base import BaseSpecialist
from intelligent_core.ai_foundation import RAGPipeline, LLMRouter, ContextBuilder

'''.format(docstring=content.split('"""')[1] if '"""' in content else f"{class_name} Specialist")

    # Extract docstring from beginning
    docstring_match = re.search(r'^"""(.+?)"""', content, re.DOTALL)
    if docstring_match:
        docstring = docstring_match.group(1).strip()
        new_imports = f'"""\n{docstring}\n"""\n\nfrom typing import Dict, Any, Optional, List\nfrom expertise_center.shared.base import BaseSpecialist\nfrom ai_foundation import RAGPipeline, LLMRouter, ContextBuilder\n\n'

    # Find class definition
    class_pattern = r'class ' + class_name + r'\(.*?\):(.*?)(?=\nclass |\Z)'
    class_match = re.search(class_pattern, content, re.DOTALL)

    if not class_match:
        print(f"   Could not find class definition")
        return

    class_body = class_match.group(1)

    # Extract class docstring
    class_doc_match = re.search(r'^\s*"""(.+?)"""', class_body, re.DOTALL)
    class_docstring = class_doc_match.group(1).strip() if class_doc_match else f"{class_name} - Strategic BCM Expert"

    # Build new class
    new_class = f'''class {class_name}(BaseSpecialist):
    """
    {class_docstring}
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize {class_name}."""
        super().__init__(
            specialist_id="{specialist_id}",
            name="{class_name}",
            specialty="Strategic BCM Analysis",
            domain="bcm"
        )

        # AI Foundation integrations
        self.rag = RAGPipeline()
        self.llm = LLMRouter()
        self.context_builder = ContextBuilder()

        self.config = config or {{}}

    async def analyze(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Strategic analysis using ai-foundation

        Args:
            context: Analysis context
            query: Analysis query

        Returns:
            Analysis results with recommendations
        """
        # Build context using ai-foundation
        enriched_context = await self.context_builder.build(context, query)

        # Use RAG to find relevant knowledge
        rag_results = await self.rag.search(query, context)

        # Use LLM for strategic analysis
        analysis = await self.llm.generate(
            task_type="strategic_analysis",
            messages=[
                {{"role": "system", "content": f"You are {{self.name}}, a {{self.specialty}} expert."}},
                {{"role": "user", "content": f"Context: {{enriched_context}}\\n\\nQuery: {{query}}"}}
            ]
        )

        return {{
            "analysis": analysis,
            "context": enriched_context,
            "knowledge": rag_results,
            "specialist": self.name
        }}

    async def recommend(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate strategic recommendations

        Args:
            analysis: Analysis results

        Returns:
            List of recommendations
        """
        recommendations_prompt = f\"\"\"
        Based on this analysis:
        {{analysis.get('analysis', '')}}

        Generate strategic recommendations.
        \"\"\"

        recommendations = await self.llm.generate(
            task_type="content_generation",
            messages=[
                {{"role": "system", "content": f"You are {{self.name}}, generating strategic recommendations."}},
                {{"role": "user", "content": recommendations_prompt}}
            ]
        )

        return [
            {{
                "recommendation": recommendations,
                "priority": "high",
                "specialist": self.name
            }}
        ]
'''

    # Combine
    new_content = new_imports + new_class

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"   Updated {filepath.name}")

def main():
    """Main update function"""
    print(" Starting specialists update...")
    print(f"Base path: {BASE_PATH}")
    print()

    updated = 0
    for filename in FILES_TO_UPDATE:
        filepath = BASE_PATH / filename
        if filepath.exists():
            try:
                update_file(filepath)
                updated += 1
            except Exception as e:
                print(f"   Error: {e}")
        else:
            print(f"  ️  Not found: {filename}")

    print()
    print(f" Updated {updated}/{len(FILES_TO_UPDATE)} files")

if __name__ == "__main__":
    main()
