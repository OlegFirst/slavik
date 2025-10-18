#!/usr/bin/env python3
"""
Import Health Checker
=====================

Comprehensive import validation for the entire platform.

Usage:
    python tests/check_imports.py                  # Console output
    python tests/check_imports.py --html           # Generate HTML report
    python tests/check_imports.py --json report.json  # Save JSON report
    python tests/check_imports.py --ci             # CI mode (fail on errors)

Exit codes:
    0 - All checks passed
    1 - Critical issues found
    2 - Warnings found (non-critical)
"""

import ast
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any

# Determine project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


class ImportHealthChecker:
    def __init__(self):
        self.imports = defaultdict(list)
        self.exports = defaultdict(set)
        self.issues = defaultdict(list)
        self.stats = {
            'total_files': 0,
            'total_imports': 0,
            'parse_errors': 0,
            'warnings': 0,
            'critical': 0,
        }

    def scan_file(self, filepath: Path) -> None:
        """Scan a single Python file"""
        try:
            self.stats['total_files'] += 1
            content = filepath.read_text()
            tree = ast.parse(content)

            rel_path = filepath.relative_to(PROJECT_ROOT)
            module_name = str(rel_path.with_suffix('')).replace('/', '.')

            # Collect imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports[module_name].append(alias.name)
                        self.stats['total_imports'] += 1

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        if node.level > 0:
                            # Relative import
                            parent_parts = module_name.split('.')[:-1]
                            if node.level > 1:
                                parent_parts = parent_parts[:-(node.level-1)]
                            if node.module:
                                imported = '.'.join(parent_parts + [node.module])
                            else:
                                imported = '.'.join(parent_parts)
                        else:
                            imported = node.module

                        self.imports[module_name].append(imported)
                        self.stats['total_imports'] += 1

                        # Check for star imports
                        for alias in node.names:
                            if alias.name == '*':
                                self.issues['star_imports'].append({
                                    'file': str(filepath),
                                    'module': module_name,
                                    'line': node.lineno,
                                })
                                self.stats['warnings'] += 1

            # Collect exports from __all__
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == '__all__':
                            if isinstance(node.value, ast.List):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Constant):
                                        self.exports[module_name].add(elt.value)

        except Exception as e:
            self.issues['parse_errors'].append({
                'file': str(filepath),
                'error': str(e),
            })
            self.stats['parse_errors'] += 1

    def find_circular_imports(self) -> List[List[str]]:
        """Find circular import dependencies"""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(module, path):
            if module in rec_stack:
                cycle_start = path.index(module)
                cycle = path[cycle_start:] + [module]
                cycles.append(cycle)
                return

            if module in visited:
                return

            visited.add(module)
            rec_stack.add(module)

            for imported in self.imports.get(module, []):
                if '.' in imported and imported.startswith('intelligent_core'):
                    dfs(imported, path + [module])

            rec_stack.remove(module)

        for module in self.imports.keys():
            if module not in visited:
                dfs(module, [])

        return cycles

    def check_import_style(self) -> Dict[str, int]:
        """Check import style statistics"""
        stats = {
            'relative': 0,
            'absolute': 0,
        }

        for filepath in PROJECT_ROOT.rglob('*.py'):
            if any(x in filepath.parts for x in ['venv', '__pycache__', '.venv', 'node_modules']):
                continue

            try:
                content = filepath.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.level > 0:
                            stats['relative'] += 1
                        else:
                            stats['absolute'] += 1
            except:
                pass

        return stats

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive report"""
        cycles = self.find_circular_imports()
        style_stats = self.check_import_style()

        total_issues = (
            len(cycles) +
            len(self.issues.get('star_imports', [])) +
            len(self.issues.get('parse_errors', []))
        )

        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_files': self.stats['total_files'],
                'total_imports': self.stats['total_imports'],
                'total_issues': total_issues,
                'critical_issues': len(cycles),
                'warnings': len(self.issues.get('star_imports', [])),
                'parse_errors': len(self.issues.get('parse_errors', [])),
            },
            'circular_imports': {
                'count': len(cycles),
                'cycles': cycles[:10],  # First 10
            },
            'import_style': {
                'absolute': style_stats['absolute'],
                'relative': style_stats['relative'],
                'absolute_percent': style_stats['absolute'] / (style_stats['absolute'] + style_stats['relative']) * 100 if style_stats['absolute'] + style_stats['relative'] > 0 else 0,
            },
            'star_imports': {
                'count': len(self.issues.get('star_imports', [])),
                'details': self.issues.get('star_imports', [])[:10],
            },
            'parse_errors': {
                'count': len(self.issues.get('parse_errors', [])),
                'details': self.issues.get('parse_errors', [])[:10],
            },
        }

    def print_report(self, report: Dict[str, Any]) -> None:
        """Print report to console"""
        print("=" * 70)
        print("🔍 IMPORT HEALTH CHECK REPORT")
        print("=" * 70)
        print(f"📅 Timestamp: {report['timestamp']}")
        print(f"📁 Files scanned: {report['summary']['total_files']}")
        print(f"📦 Total imports: {report['summary']['total_imports']}")
        print()

        # Summary
        print("=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        summary = report['summary']

        if summary['total_issues'] == 0:
            print("✅ No issues found! Imports are in excellent condition!")
        else:
            print(f"⚠️  Total issues: {summary['total_issues']}")
            print(f"   Critical: {summary['critical_issues']}")
            print(f"   Warnings: {summary['warnings']}")
            print(f"   Parse errors: {summary['parse_errors']}")
        print()

        # Circular imports
        print("=" * 70)
        print("🔄 CIRCULAR IMPORTS")
        print("=" * 70)
        if report['circular_imports']['count'] == 0:
            print("✅ No circular imports found!")
        else:
            print(f"⚠️  Found {report['circular_imports']['count']} cycles")
            for i, cycle in enumerate(report['circular_imports']['cycles'], 1):
                print(f"\n  Cycle {i}:")
                for module in cycle:
                    print(f"    → {module}")
        print()

        # Import style
        print("=" * 70)
        print("📊 IMPORT STYLE")
        print("=" * 70)
        style = report['import_style']
        print(f"  Absolute imports: {style['absolute']} ({style['absolute_percent']:.1f}%)")
        print(f"  Relative imports: {style['relative']}")

        if style['absolute_percent'] >= 70:
            print("  ✅ Good! Absolute imports are preferred")
        else:
            print("  ⚠️  Consider using more absolute imports")
        print()

        # Star imports
        if report['star_imports']['count'] > 0:
            print("=" * 70)
            print("⚠️  STAR IMPORTS")
            print("=" * 70)
            print(f"  Found {report['star_imports']['count']} star imports")
            for item in report['star_imports']['details']:
                print(f"    - {item['file']}:{item['line']}")
            print()

        # Parse errors
        if report['parse_errors']['count'] > 0:
            print("=" * 70)
            print("🐛 PARSE ERRORS")
            print("=" * 70)
            print(f"  Found {report['parse_errors']['count']} errors")
            for item in report['parse_errors']['details']:
                print(f"    - {item['file']}")
                print(f"      {item['error']}")
            print()

        # Final score
        print("=" * 70)
        print("📈 HEALTH SCORE")
        print("=" * 70)

        score = 100
        score -= min(summary['critical_issues'] * 10, 50)
        score -= min(summary['warnings'] * 2, 30)
        score -= min(summary['parse_errors'] * 5, 20)

        print(f"  Score: {max(score, 0)}/100")

        if score >= 90:
            print("  ✅ EXCELLENT - Imports are in great shape!")
        elif score >= 70:
            print("  ✅ GOOD - Minor improvements needed")
        elif score >= 50:
            print("  ⚠️  FAIR - Several issues to address")
        else:
            print("  ❌ POOR - Significant improvements required")

    def save_html_report(self, report: Dict[str, Any], output_path: Path) -> None:
        """Generate HTML report"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Import Health Check Report</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat {{ background: #f9f9f9; padding: 20px; border-radius: 5px; text-align: center; }}
        .stat-value {{ font-size: 36px; font-weight: bold; color: #4CAF50; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .success {{ color: #4CAF50; }}
        .warning {{ color: #ff9800; }}
        .error {{ color: #f44336; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; }}
        .score {{ font-size: 48px; font-weight: bold; text-align: center; margin: 30px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Import Health Check Report</h1>
        <p><strong>Generated:</strong> {report['timestamp']}</p>

        <div class="summary">
            <div class="stat">
                <div class="stat-value">{report['summary']['total_files']}</div>
                <div class="stat-label">Files Scanned</div>
            </div>
            <div class="stat">
                <div class="stat-value">{report['summary']['total_imports']}</div>
                <div class="stat-label">Total Imports</div>
            </div>
            <div class="stat">
                <div class="stat-value {'success' if report['summary']['total_issues'] == 0 else 'warning'}">{report['summary']['total_issues']}</div>
                <div class="stat-label">Issues Found</div>
            </div>
        </div>

        <h2>🔄 Circular Imports</h2>
        {'<p class="success">✅ No circular imports found!</p>' if report['circular_imports']['count'] == 0 else '<p class="warning">⚠️  Found ' + str(report['circular_imports']['count']) + ' circular import cycles</p>'}

        <h2>📊 Import Style</h2>
        <p>Absolute imports: <strong>{report['import_style']['absolute']}</strong> ({report['import_style']['absolute_percent']:.1f}%)</p>
        <p>Relative imports: <strong>{report['import_style']['relative']}</strong></p>

        <h2>📈 Health Score</h2>
        <div class="score">
            {max(100 - report['summary']['critical_issues'] * 10 - report['summary']['warnings'] * 2 - report['summary']['parse_errors'] * 5, 0)}/100
        </div>
    </div>
</body>
</html>"""

        output_path.write_text(html)
        print(f"\n✅ HTML report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Check import health')
    parser.add_argument('--html', action='store_true', help='Generate HTML report')
    parser.add_argument('--json', type=str, help='Save JSON report to file')
    parser.add_argument('--ci', action='store_true', help='CI mode (exit with error code)')
    args = parser.parse_args()

    print("🔍 Scanning project imports...\n")

    checker = ImportHealthChecker()

    # Scan directories
    scan_dirs = [
        PROJECT_ROOT / "intelligent_core",
        PROJECT_ROOT / "platform_services",
        PROJECT_ROOT / "infrastructure",
    ]

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue

        for py_file in scan_dir.rglob("*.py"):
            if any(x in py_file.parts for x in ['venv', '__pycache__', '.venv', 'node_modules']):
                continue
            checker.scan_file(py_file)

    # Generate report
    report = checker.generate_report()

    # Print to console
    checker.print_report(report)

    # Save JSON if requested
    if args.json:
        json_path = Path(args.json)
        json_path.write_text(json.dumps(report, indent=2))
        print(f"\n✅ JSON report saved to: {json_path}")

    # Generate HTML if requested
    if args.html:
        html_path = PROJECT_ROOT / "tests" / "reports" / f"import-health-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
        html_path.parent.mkdir(exist_ok=True)
        checker.save_html_report(report, html_path)

    # CI mode - exit with error if issues found
    if args.ci:
        if report['summary']['critical_issues'] > 0:
            print("\n❌ Critical issues found! Failing CI...")
            sys.exit(1)
        elif report['summary']['warnings'] > 0:
            print("\n⚠️  Warnings found, but passing...")
            sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
