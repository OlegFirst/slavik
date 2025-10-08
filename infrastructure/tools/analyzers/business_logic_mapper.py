#!/usr/bin/env python3
"""
Business Logic Mapper
=====================

Finds REAL business logic that dependency_mapper and ast_analyzer miss:

1. EventBus patterns (publish/subscribe)
2. HTTP service calls (httpx/requests)
3. Temporal workflows (workflow calls)
4. Database operations (CRUD patterns)
5. Analyzer calls (AI analysis)
6. Service Registry lookups

This shows HOW components ACTUALLY communicate at runtime!
"""

import os
import re
import json
import ast
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict

# Patterns to detect business logic
PATTERNS = {
    'eventbus_publish': [
        r'\.publish\(',
        r'event_bus\.publish',
        r'EventBus\.publish',
        r'await.*\.publish\(',
        r'publish_event\(',  # ✅ ADD - catches direct publish_event() calls
        r'await\s+publish_event\('  # ✅ ADD - catches await publish_event()
    ],
    'eventbus_subscribe': [
        r'\.subscribe\(',
        r'@event_handler',
        r'event_bus\.subscribe',
        r'on_event\('
    ],
    'http_call': [
        r'httpx\.AsyncClient',
        r'httpx\.Client',
        r'requests\.get\(',
        r'requests\.post\(',
        r'async with httpx',
        r'await client\.(get|post|put|delete)'
    ],
    'temporal_workflow': [
        r'@workflow\.defn',
        r'@activity\.defn',
        r'workflow\.execute_activity',
        r'temporal_client\.start_workflow',
        r'await.*start_workflow'
    ],
    'analyzer_call': [
        r'analyzer_coordinator\.route_analysis',
        r'\.route_analysis\(',
        r'AnalyzerType\.',
        r'await.*analyze\('
    ],
    'service_registry': [
        r'service_registry\.get_service_url',
        r'BCMServiceType\.',
        r'find_service',
        r'get_service_url'
    ],
    'database_query': [
        r'session\.query\(',
        r'session\.execute\(',
        r'db\.query\(',
        r'await.*\.fetch',
        r'SELECT.*FROM'
    ],
    'coordination_intent': [
        r'coordination_center',
        r'CommandInterpreter',
        r'ToolRegistry',
        r'translate.*intent'
    ]
}


class BusinessLogicMapper:
    """Maps real business logic across the platform."""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.business_logic = defaultdict(lambda: defaultdict(list))
        self.stats = defaultdict(int)

    def scan_project(self, directories: List[str]):
        """Scan project for business logic patterns."""
        print("🔍 Scanning for business logic patterns...\n")

        for directory in directories:
            dir_path = self.root_dir / directory
            if not dir_path.exists():
                continue

            print(f"📂 Scanning: {directory}")
            self._scan_directory(dir_path, directory)

        print(f"\n✅ Scan complete!")

    def _scan_directory(self, path: Path, module_name: str):
        """Recursively scan directory."""
        for item in path.rglob("*.py"):
            if "__pycache__" in str(item) or ".pyc" in str(item):
                continue

            try:
                self._analyze_file(item, module_name)
            except Exception as e:
                # Silently skip files with errors
                pass

    def _analyze_file(self, file_path: Path, module_name: str):
        """Analyze single file for business logic."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except:
            return

        relative_path = str(file_path.relative_to(self.root_dir))

        # Check each pattern
        for pattern_type, patterns in PATTERNS.items():
            matches = []

            for pattern in patterns:
                found = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                for match in found:
                    # Get line number
                    line_num = content[:match.start()].count('\n') + 1

                    # Get surrounding context
                    lines = content.split('\n')
                    context_start = max(0, line_num - 2)
                    context_end = min(len(lines), line_num + 1)
                    context = '\n'.join(lines[context_start:context_end])

                    matches.append({
                        'line': line_num,
                        'pattern': pattern,
                        'match': match.group(0),
                        'context': context[:200]  # Limit context
                    })

            if matches:
                self.business_logic[module_name][pattern_type].append({
                    'file': relative_path,
                    'matches': matches
                })
                self.stats[pattern_type] += len(matches)

    def generate_report(self, output_dir: str):
        """Generate business logic report."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)

        # JSON report
        json_path = output_path / "business_logic.json"
        with open(json_path, 'w') as f:
            json.dump({
                'stats': dict(self.stats),
                'logic': dict(self.business_logic)
            }, f, indent=2)

        print(f"✅ JSON report: {json_path}")

        # Markdown report
        md_path = output_path / "business_logic.md"
        with open(md_path, 'w') as f:
            f.write("# Business Logic Map\n\n")
            f.write("## Statistics\n\n")

            for pattern_type, count in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{pattern_type}**: {count} occurrences\n")

            f.write("\n## Patterns by Module\n\n")

            for module, patterns in sorted(self.business_logic.items()):
                f.write(f"### {module}\n\n")

                for pattern_type, files in sorted(patterns.items()):
                    if not files:
                        continue

                    f.write(f"#### {pattern_type} ({len(files)} files)\n\n")

                    for file_info in files[:10]:  # Limit to 10 files per pattern
                        f.write(f"**{file_info['file']}**\n")
                        f.write(f"- Found {len(file_info['matches'])} matches\n\n")

        print(f"✅ Markdown report: {md_path}")

        # Summary
        print(f"\n📊 BUSINESS LOGIC SUMMARY:")
        print(f"   Modules scanned: {len(self.business_logic)}")
        for pattern_type, count in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
            print(f"   {pattern_type}: {count}")


def main():
    """Main entry point."""
    root_dir = "/Users/MD/AI-Platform-ISO"

    directories = [
        "intelligent-core/orchestration",
        "intelligent-core/workflow_intelligence",
        "intelligent-core/coordination-center",
        "intelligent-core/expertise-center",
        "platform-services",
        "infrastructure/eventbus",
        "shared"
    ]

    mapper = BusinessLogicMapper(root_dir)
    mapper.scan_project(directories)
    mapper.generate_report(f"{root_dir}/infrastructure/AI-office-infrastructure/devops-agent/reports-generated")


if __name__ == "__main__":
    main()
