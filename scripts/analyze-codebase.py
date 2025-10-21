#!/usr/bin/env python3
"""
Codebase Analysis for Team/Production Migration

Analyzes:
1. Cyrillic in folder/file names
2. Emojis in code vs documentation
3. Cyrillic in comments
4. Import dependencies

Generates migration plan with impact assessment.
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import json

# Configuration
ROOT_DIR = Path(__file__).parent.parent
EXCLUDE_DIRS = {
    '.git', 'node_modules', '_archive', 'можетпригодится',
    'dist', 'build', '.next', 'coverage', '__pycache__',
    '.venv', 'venv', '_BACKUP_', '_OLD', '.backup.',
    'BACKUP_', 'backup-', '.cleanup-report'
}

EMOJI_PATTERN = re.compile(r'[️️️️🆕🆓🆙️️]')
CYRILLIC_PATTERN = re.compile(r'[а-яА-ЯёЁ]+')

CODE_EXTENSIONS = {'.py', '.ts', '.tsx', '.js', '.jsx', '.go', '.java'}
DOC_EXTENSIONS = {'.md', '.rst', '.txt'}
CONFIG_EXTENSIONS = {'.json', '.yaml', '.yml', '.toml', '.ini'}

class CodebaseAnalyzer:
    def __init__(self):
        self.cyrillic_folders = []
        self.cyrillic_files = []
        self.emoji_stats = defaultdict(lambda: {'count': 0, 'files': []})
        self.cyrillic_comments = []
        self.import_dependencies = defaultdict(list)

    def is_excluded(self, path: Path) -> bool:
        """Check if path should be excluded"""
        parts = path.parts
        return any(excluded in parts for excluded in EXCLUDE_DIRS)

    def has_cyrillic(self, text: str) -> bool:
        """Check if text contains cyrillic characters"""
        return bool(CYRILLIC_PATTERN.search(text))

    def count_emojis(self, text: str) -> int:
        """Count emojis in text"""
        return len(EMOJI_PATTERN.findall(text))

    def analyze_folders(self):
        """Find all folders with cyrillic names"""
        print(" Analyzing folder names...")

        for root, dirs, files in os.walk(ROOT_DIR):
            root_path = Path(root)

            # Skip excluded directories
            if self.is_excluded(root_path):
                dirs[:] = []  # Don't descend into this directory
                continue

            for dir_name in dirs:
                if dir_name in EXCLUDE_DIRS:
                    continue

                if self.has_cyrillic(dir_name):
                    rel_path = root_path / dir_name
                    rel_path = rel_path.relative_to(ROOT_DIR)
                    self.cyrillic_folders.append(str(rel_path))

        print(f"  Found {len(self.cyrillic_folders)} folders with cyrillic names")

    def analyze_files(self):
        """Analyze all files for cyrillic names, emojis, comments"""
        print(" Analyzing files...")

        total_files = 0

        for root, dirs, files in os.walk(ROOT_DIR):
            root_path = Path(root)

            # Skip excluded directories
            if self.is_excluded(root_path):
                dirs[:] = []
                continue

            # Remove excluded dirs from traversal
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file_name in files:
                file_path = root_path / file_name
                rel_path = file_path.relative_to(ROOT_DIR)

                total_files += 1
                if total_files % 100 == 0:
                    print(f"  Processed {total_files} files...", end='\r')

                # Check filename for cyrillic
                if self.has_cyrillic(file_name):
                    self.cyrillic_files.append(str(rel_path))

                # Analyze file contents
                ext = file_path.suffix

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Count emojis
                    emoji_count = self.count_emojis(content)
                    if emoji_count > 0:
                        if ext in CODE_EXTENSIONS:
                            category = 'code'
                        elif ext in DOC_EXTENSIONS:
                            category = 'docs'
                        elif ext in CONFIG_EXTENSIONS:
                            category = 'config'
                        else:
                            category = 'other'

                        self.emoji_stats[category]['count'] += emoji_count
                        self.emoji_stats[category]['files'].append({
                            'path': str(rel_path),
                            'count': emoji_count
                        })

                    # Find cyrillic in comments (Python and TypeScript)
                    if ext in {'.py', '.ts', '.tsx', '.js', '.jsx'}:
                        lines = content.split('\n')
                        for line_num, line in enumerate(lines, 1):
                            # Python comments
                            if ext == '.py' and '#' in line:
                                comment = line.split('#', 1)[1]
                                if self.has_cyrillic(comment):
                                    self.cyrillic_comments.append({
                                        'file': str(rel_path),
                                        'line': line_num,
                                        'text': comment.strip()
                                    })

                            # TypeScript/JavaScript comments
                            elif ext in {'.ts', '.tsx', '.js', '.jsx'} and '//' in line:
                                comment = line.split('//', 1)[1]
                                if self.has_cyrillic(comment):
                                    self.cyrillic_comments.append({
                                        'file': str(rel_path),
                                        'line': line_num,
                                        'text': comment.strip()
                                    })

                    # Find imports (Python)
                    if ext == '.py':
                        for line in content.split('\n'):
                            if line.strip().startswith(('import ', 'from ')):
                                # Check if import references cyrillic folder
                                for cyrillic_folder in self.cyrillic_folders:
                                    folder_name = Path(cyrillic_folder).name
                                    if folder_name in line:
                                        self.import_dependencies[cyrillic_folder].append({
                                            'file': str(rel_path),
                                            'line': line.strip()
                                        })

                except (UnicodeDecodeError, PermissionError, FileNotFoundError):
                    pass

        print(f"  Analyzed {total_files} files" + " " * 20)

    def generate_report(self) -> str:
        """Generate comprehensive migration report"""

        report = []
        report.append("#  Codebase Migration Analysis Report")
        report.append("")
        report.append("**Date:** " + os.popen('date').read().strip())
        report.append("**Purpose:** Team collaboration and production deployment")
        report.append("")
        report.append("---")
        report.append("")

        # Summary
        report.append("##  Executive Summary")
        report.append("")

        total_emoji_count = sum(stats['count'] for stats in self.emoji_stats.values())
        code_emoji_count = self.emoji_stats.get('code', {}).get('count', 0)

        report.append(f"- **Cyrillic folders:** {len(self.cyrillic_folders)}")
        report.append(f"- **Cyrillic files:** {len(self.cyrillic_files)}")
        report.append(f"- **Emojis in code:** {code_emoji_count}")
        report.append(f"- **Emojis total:** {total_emoji_count}")
        report.append(f"- **Cyrillic comments:** {len(self.cyrillic_comments)}")
        report.append(f"- **Import dependencies:** {sum(len(v) for v in self.import_dependencies.values())}")
        report.append("")

        # Risk Assessment
        report.append("## ️ Risk Assessment")
        report.append("")
        report.append("| Task | Impact | Risk Level | Effort |")
        report.append("|------|--------|------------|--------|")
        report.append(f"| Rename folders | {len(self.cyrillic_folders)} folders → {sum(len(v) for v in self.import_dependencies.values())} imports |  High | Medium |")

        code_files_with_emoji = len(self.emoji_stats.get('code', {}).get('files', []))
        report.append(f"| Remove code emojis | {code_files_with_emoji} files |  Medium | High |")
        report.append(f"| Translate comments | {len(self.cyrillic_comments)} comments |  Medium | High |")
        report.append("")

        # Cyrillic Folders
        report.append("##  Cyrillic Folders (Need Renaming)")
        report.append("")

        if self.cyrillic_folders:
            report.append("| Current Path | Suggested Rename | Affected Imports |")
            report.append("|--------------|------------------|------------------|")

            for folder in sorted(self.cyrillic_folders):
                folder_name = Path(folder).name

                # Suggest English name
                translations = {
                    'админ': 'admin',
                    'инт': 'int',
                    'ВСМ-colleagues': 'VSM-colleagues',
                    'архив': 'archive'
                }

                suggested = translations.get(folder_name, folder_name)
                import_count = len(self.import_dependencies.get(folder, []))

                report.append(f"| `{folder}` | `{suggested}` | {import_count} |")
        else:
            report.append(" No cyrillic folders found")

        report.append("")

        # Import Dependencies
        if self.import_dependencies:
            report.append("##  Import Dependencies")
            report.append("")

            for folder, imports in sorted(self.import_dependencies.items()):
                report.append(f"### `{folder}` ({len(imports)} imports)")
                report.append("")

                for imp in imports[:10]:  # Show first 10
                    report.append(f"- `{imp['file']}`")
                    report.append(f"  ```python")
                    report.append(f"  {imp['line']}")
                    report.append(f"  ```")

                if len(imports) > 10:
                    report.append(f"- ... and {len(imports) - 10} more")

                report.append("")

        # Emoji Statistics
        report.append("##  Emoji Statistics")
        report.append("")
        report.append("| Category | Count | Files |")
        report.append("|----------|-------|-------|")

        for category in ['code', 'docs', 'config', 'other']:
            if category in self.emoji_stats:
                stats = self.emoji_stats[category]
                report.append(f"| {category.capitalize()} | {stats['count']} | {len(stats['files'])} |")

        report.append("")

        # Top files with emojis in code
        if 'code' in self.emoji_stats:
            code_files = sorted(
                self.emoji_stats['code']['files'],
                key=lambda x: x['count'],
                reverse=True
            )[:20]

            report.append("### Top 20 Code Files with Emojis")
            report.append("")
            report.append("| File | Emoji Count |")
            report.append("|------|-------------|")

            for file_info in code_files:
                report.append(f"| `{file_info['path']}` | {file_info['count']} |")

            report.append("")

        # Cyrillic Comments
        report.append("##  Cyrillic Comments")
        report.append("")

        if self.cyrillic_comments:
            report.append(f"Found {len(self.cyrillic_comments)} comments with cyrillic text.")
            report.append("")

            # Group by file
            comments_by_file = defaultdict(list)
            for comment in self.cyrillic_comments:
                comments_by_file[comment['file']].append(comment)

            report.append("### Top 10 Files with Cyrillic Comments")
            report.append("")

            top_files = sorted(
                comments_by_file.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )[:10]

            for file_path, comments in top_files:
                report.append(f"#### `{file_path}` ({len(comments)} comments)")
                report.append("")

                for comment in comments[:5]:  # Show first 5
                    report.append(f"- Line {comment['line']}: `{comment['text'][:100]}`")

                if len(comments) > 5:
                    report.append(f"- ... and {len(comments) - 5} more")

                report.append("")
        else:
            report.append(" No cyrillic comments found")
            report.append("")

        # Migration Plan
        report.append("##  Recommended Migration Plan")
        report.append("")
        report.append("### Phase 1: Rename Cyrillic Folders  SAFE")
        report.append("")
        report.append("```bash")
        report.append("# Automated with import updates")

        for folder in sorted(self.cyrillic_folders):
            folder_name = Path(folder).name
            translations = {
                'админ': 'admin',
                'инт': 'int',
                'ВСМ-colleagues': 'VSM-colleagues',
                'архив': 'archive'
            }
            suggested = translations.get(folder_name, folder_name)
            old_path = folder
            new_path = str(Path(folder).parent / suggested)

            report.append(f"git mv '{old_path}' '{new_path}'")

        report.append("```")
        report.append("")
        report.append(f"**Impact:** {sum(len(v) for v in self.import_dependencies.values())} imports need update")
        report.append("")

        report.append("### Phase 2: Remove Emojis from Code ️ MEDIUM RISK")
        report.append("")
        report.append("```bash")
        report.append("# Automated regex replacement in .py, .ts, .tsx, .js, .jsx")
        report.append("# KEEP emojis in .md documentation files")
        report.append("```")
        report.append("")
        report.append(f"**Impact:** {len(self.emoji_stats.get('code', {}).get('files', []))} code files")
        report.append("")

        report.append("### Phase 3: Translate Critical Comments  HIGH EFFORT")
        report.append("")
        report.append("```bash")
        report.append("# Semi-automated with AI assistance")
        report.append("# Translate API docs, complex logic explanations")
        report.append("# Remove or translate simple comments")
        report.append("```")
        report.append("")
        report.append(f"**Impact:** {len(self.cyrillic_comments)} comments")
        report.append("")

        # Save detailed data
        report.append("---")
        report.append("")
        report.append("**Full analysis data saved to:** `scripts/migration-data.json`")

        return "\n".join(report)

    def save_data(self, output_file: Path):
        """Save detailed analysis data as JSON"""

        data = {
            'cyrillic_folders': self.cyrillic_folders,
            'cyrillic_files': self.cyrillic_files,
            'emoji_stats': dict(self.emoji_stats),
            'cyrillic_comments': self.cyrillic_comments[:100],  # First 100
            'import_dependencies': dict(self.import_dependencies),
            'summary': {
                'total_cyrillic_folders': len(self.cyrillic_folders),
                'total_cyrillic_files': len(self.cyrillic_files),
                'total_emojis': sum(stats['count'] for stats in self.emoji_stats.values()),
                'code_emojis': self.emoji_stats.get('code', {}).get('count', 0),
                'total_cyrillic_comments': len(self.cyrillic_comments),
                'total_imports_to_update': sum(len(v) for v in self.import_dependencies.values())
            }
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    print("=" * 60)
    print("   AI-Platform-ISO Migration Analysis")
    print("=" * 60)
    print()

    analyzer = CodebaseAnalyzer()

    # Run analysis
    analyzer.analyze_folders()
    analyzer.analyze_files()

    # Generate report
    print()
    print(" Generating report...")
    report = analyzer.generate_report()

    # Save report
    report_file = ROOT_DIR / 'scripts' / 'MIGRATION_ANALYSIS_REPORT.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f" Report saved: {report_file}")

    # Save data
    data_file = ROOT_DIR / 'scripts' / 'migration-data.json'
    analyzer.save_data(data_file)

    print(f" Data saved: {data_file}")
    print()
    print("=" * 60)
    print("   Analysis Complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
