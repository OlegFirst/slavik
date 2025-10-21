#!/usr/bin/env python3
"""
Emoji Removal Script for Production/Team Codebase

Removes emojis from code files while preserving them in documentation.

Usage:
    ./scripts/remove-emojis.py              # Dry-run (report only)
    ./scripts/remove-emojis.py --apply      # Apply changes
    ./scripts/remove-emojis.py --verbose    # Detailed output
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# Configuration
ROOT_DIR = Path(__file__).parent.parent
REPORT_DIR = ROOT_DIR / '.migration-report'
REPORT_DIR.mkdir(exist_ok=True)

EXCLUDE_DIRS = {
    '.git', 'node_modules', '_archive', 'можетпригодится',
    'dist', 'build', '.next', 'coverage', '__pycache__',
    '.venv', 'venv', '_BACKUP_', '_OLD', '.backup.',
    'BACKUP_', 'backup-', '.cleanup-report', '.migration-report'
}

# File types to process (remove emojis)
CODE_EXTENSIONS = {'.py', '.ts', '.tsx', '.js', '.jsx', '.go', '.java', '.c', '.cpp', '.h', '.hpp'}

# File types to preserve (keep emojis)
PRESERVE_EXTENSIONS = {'.md', '.rst', '.txt', '.html'}

# Comprehensive emoji pattern
EMOJI_PATTERN = re.compile(
    r'[\U0001F300-\U0001F9FF'  # Emoticons, symbols, pictographs
    r'\U0001F600-\U0001F64F'   # Emoticons
    r'\U0001F680-\U0001F6FF'   # Transport and map
    r'\U0001F1E0-\U0001F1FF'   # Flags
    r'\u2600-\u26FF'           # Misc symbols
    r'\u2700-\u27BF'           # Dingbats
    r'\u2B50'                  # Star
    r'\u2705'                  # Check mark
    r'\u274C'                  # Cross mark
    r'\u26A0'                  # Warning
    r'\u2728'                  # Sparkles
    r'\u2B55'                  # Circle
    r'\u2753-\u2755'           # Question marks
    r'\u2795-\u2797'           # Plus/minus
    r'\u27A1'                  # Right arrow
    r'\u2934-\u2935'           # Arrows
    r'\u3030'                  # Wavy dash
    r'\u303D'                  # Part alternation mark
    r'\u3297-\u3299'           # Circled ideographs
    r'\u25AA-\u25AB'           # Squares
    r'\u25B6'                  # Play
    r'\u25C0'                  # Reverse
    r'\u25FB-\u25FE'           # Squares
    r']+',
    flags=re.UNICODE
)

class EmojiRemover:
    def __init__(self, dry_run=True, verbose=False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'emojis_removed': 0,
            'files_skipped': 0,
            'errors': 0
        }
        self.modifications = defaultdict(list)

    def is_excluded(self, path: Path) -> bool:
        """Check if path should be excluded"""
        parts = path.parts
        return any(excluded in parts for excluded in EXCLUDE_DIRS)

    def remove_emojis_from_text(self, text: str) -> tuple[str, int]:
        """Remove emojis from text and return cleaned text + count"""
        emojis_found = EMOJI_PATTERN.findall(text)
        emoji_count = len(emojis_found)
        cleaned = EMOJI_PATTERN.sub('', text)
        return cleaned, emoji_count

    def process_file(self, file_path: Path) -> dict:
        """Process a single file and return statistics"""
        result = {
            'path': str(file_path.relative_to(ROOT_DIR)),
            'emojis_removed': 0,
            'modified': False,
            'error': None
        }

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()

            # Remove emojis
            cleaned_content, emoji_count = self.remove_emojis_from_text(original_content)

            if emoji_count > 0:
                result['emojis_removed'] = emoji_count
                result['modified'] = True

                if not self.dry_run:
                    # Apply changes
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)

                self.modifications[file_path].append({
                    'emojis_removed': emoji_count,
                    'original_size': len(original_content),
                    'new_size': len(cleaned_content)
                })

                if self.verbose:
                    print(f"  {'[DRY-RUN] ' if self.dry_run else ''}✓ {result['path']}: {emoji_count} emojis")

        except Exception as e:
            result['error'] = str(e)
            self.stats['errors'] += 1
            if self.verbose:
                print(f"  ✗ {result['path']}: Error - {e}")

        return result

    def scan_codebase(self):
        """Scan entire codebase and remove emojis from code files"""
        print("=" * 70)
        print(f"  🧹 Emoji Removal - {'DRY-RUN' if self.dry_run else 'APPLY MODE'}")
        print("=" * 70)
        print()

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
                ext = file_path.suffix

                # Skip if not a code file
                if ext not in CODE_EXTENSIONS:
                    if ext in PRESERVE_EXTENSIONS and self.verbose:
                        print(f"  📝 Preserving: {file_path.relative_to(ROOT_DIR)}")
                    continue

                # Skip this script itself
                if file_path.name == 'remove-emojis.py':
                    continue

                self.stats['files_processed'] += 1

                if self.stats['files_processed'] % 100 == 0:
                    print(f"  Processed {self.stats['files_processed']} files...", end='\r')

                result = self.process_file(file_path)

                if result['modified']:
                    self.stats['files_modified'] += 1
                    self.stats['emojis_removed'] += result['emojis_removed']

        print(f"  Processed {self.stats['files_processed']} files" + " " * 30)
        print()

    def generate_report(self) -> str:
        """Generate detailed report"""
        report = []
        report.append("# 🧹 Emoji Removal Report")
        report.append("")
        report.append(f"**Date:** {os.popen('date').read().strip()}")
        report.append(f"**Mode:** {'DRY-RUN' if self.dry_run else 'APPLY'}")
        report.append("")
        report.append("---")
        report.append("")

        # Summary
        report.append("## 📊 Summary")
        report.append("")
        report.append(f"- **Files processed:** {self.stats['files_processed']}")
        report.append(f"- **Files modified:** {self.stats['files_modified']}")
        report.append(f"- **Emojis removed:** {self.stats['emojis_removed']}")
        report.append(f"- **Errors:** {self.stats['errors']}")
        report.append("")

        # Modified files
        if self.modifications:
            report.append("## 📝 Modified Files")
            report.append("")
            report.append("| File | Emojis Removed | Size Change |")
            report.append("|------|----------------|-------------|")

            for file_path, mods in sorted(self.modifications.items()):
                rel_path = file_path.relative_to(ROOT_DIR)
                total_emojis = sum(m['emojis_removed'] for m in mods)
                size_diff = mods[0]['new_size'] - mods[0]['original_size']

                report.append(f"| `{rel_path}` | {total_emojis} | {size_diff:+d} bytes |")

            report.append("")

        # What was preserved
        report.append("## ✅ What Was Preserved")
        report.append("")
        report.append("- ✅ All `.md` documentation files")
        report.append("- ✅ All `.rst` documentation files")
        report.append("- ✅ All `.txt` text files")
        report.append("- ✅ All `.html` files")
        report.append("- ✅ All archive directories")
        report.append("")

        # What was cleaned
        report.append("## 🧹 What Was Cleaned")
        report.append("")
        report.append("- 🧹 `.py` Python files")
        report.append("- 🧹 `.ts`, `.tsx` TypeScript files")
        report.append("- 🧹 `.js`, `.jsx` JavaScript files")
        report.append("- 🧹 `.go` Go files")
        report.append("- 🧹 `.java` Java files")
        report.append("")

        if self.dry_run:
            report.append("## ⚠️ Next Steps")
            report.append("")
            report.append("This was a **DRY-RUN**. No files were modified.")
            report.append("")
            report.append("To apply changes:")
            report.append("```bash")
            report.append("./scripts/remove-emojis.py --apply")
            report.append("```")
            report.append("")

        return "\n".join(report)

    def print_summary(self):
        """Print summary to console"""
        print("=" * 70)
        print("  📊 Summary")
        print("=" * 70)
        print()
        print(f"Files processed:  {self.stats['files_processed']}")
        print(f"Files modified:   {self.stats['files_modified']}")
        print(f"Emojis removed:   {self.stats['emojis_removed']}")
        print(f"Errors:           {self.stats['errors']}")
        print()

        if self.dry_run:
            print("⚠️  This was a DRY-RUN. No files were modified.")
            print("   Run with --apply to make changes.")
        else:
            print("✅ Changes applied successfully!")

        print()


def main():
    # Parse arguments
    dry_run = True
    verbose = False

    if '--apply' in sys.argv:
        dry_run = False
    if '--verbose' in sys.argv or '-v' in sys.argv:
        verbose = True
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        return

    # Run emoji removal
    remover = EmojiRemover(dry_run=dry_run, verbose=verbose)
    remover.scan_codebase()

    # Generate report
    report = remover.generate_report()

    # Save report
    timestamp = os.popen('date +%Y%m%d_%H%M%S').read().strip()
    report_file = REPORT_DIR / f'emoji-removal-{timestamp}.md'

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    # Print summary
    remover.print_summary()

    print(f"📄 Report saved: {report_file.relative_to(ROOT_DIR)}")
    print()


if __name__ == '__main__':
    main()
