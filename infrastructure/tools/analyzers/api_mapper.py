#!/usr/bin/env python3
"""
API Mapper
==========

Finds ALL APIs in the project:
1. FastAPI routes (@app.get, @app.post, etc.)
2. Flask routes (@bp.route, @app.route)
3. gRPC services
4. GraphQL resolvers
5. EventBus handlers (@event_handler)
6. Temporal activities (@activity.defn)
7. Temporal workflows (@workflow.defn)

Shows COMPLETE API surface of the platform!
"""

import os
import re
import json
import ast
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict


class APIMapper:
    """Maps all API endpoints across the platform."""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.apis = {
            'http_apis': [],
            'temporal_workflows': [],
            'temporal_activities': [],
            'eventbus_handlers': [],
            'grpc_services': [],
            'graphql_resolvers': []
        }
        self.stats = defaultdict(int)

    def scan_project(self, directories: List[str]):
        """Scan project for APIs."""
        print("🔍 Scanning for ALL APIs...\n")

        for directory in directories:
            dir_path = self.root_dir / directory
            if not dir_path.exists():
                print(f"⚠️  Directory not found: {directory}")
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
                pass

    def _analyze_file(self, file_path: Path, module_name: str):
        """Analyze single file for APIs."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except:
            return

        relative_path = str(file_path.relative_to(self.root_dir))

        # 1. HTTP APIs (FastAPI/Flask)
        self._find_http_apis(content, relative_path, module_name)

        # 2. Temporal Workflows
        self._find_temporal_workflows(content, relative_path, module_name)

        # 3. Temporal Activities
        self._find_temporal_activities(content, relative_path, module_name)

        # 4. EventBus Handlers
        self._find_eventbus_handlers(content, relative_path, module_name)

        # 5. gRPC Services
        self._find_grpc_services(content, relative_path, module_name)

        # 6. GraphQL Resolvers
        self._find_graphql_resolvers(content, relative_path, module_name)

    def _find_http_apis(self, content: str, file_path: str, module: str):
        """Find HTTP API endpoints - ULTRA-FIXED for all decorator patterns."""
        # ULTRA-FLEXIBLE regex:
        # Handles: @router.post("/path")
        #          @router.post("/path", response_model=...)
        #          @router.post(
        #              "/path",
        #              response_model=...
        #          )

        fastapi_pattern = re.compile(
            r'@(?:app|router)\.(get|post|put|delete|patch)\s*\('  # @router.post(
            r'[^)]*?'  # Any content before path (non-greedy)
            r'["\']([^"\']+)["\']',  # "/path"
            re.MULTILINE | re.DOTALL
        )

        flask_pattern = re.compile(
            r'@(?:app|bp)\.route\s*\(["\']([^"\']+)["\'].*?methods\s*=\s*\[([^\]]+)\]',
            re.MULTILINE | re.DOTALL
        )

        seen_endpoints = set()

        # FastAPI endpoints
        for match in fastapi_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            method = match.group(1).upper()
            path = match.group(2)

            endpoint_key = (method, path, file_path)
            if endpoint_key in seen_endpoints:
                continue
            seen_endpoints.add(endpoint_key)

            func_name = self._find_function_name(content, match.end())

            self.apis['http_apis'].append({
                'module': module,
                'file': file_path,
                'line': line_num,
                'framework': 'FastAPI',
                'method': method,
                'path': path,
                'function': func_name
            })
            self.stats['http_apis'] += 1

        # Flask endpoints
        for match in flask_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            path = match.group(1)
            method = match.group(2).strip('"\' ').split(',')[0]

            endpoint_key = (method, path, file_path)
            if endpoint_key in seen_endpoints:
                continue
            seen_endpoints.add(endpoint_key)

            func_name = self._find_function_name(content, match.end())

            self.apis['http_apis'].append({
                'module': module,
                'file': file_path,
                'line': line_num,
                'framework': 'Flask',
                'method': method,
                'path': path,
                'function': func_name
            })
            self.stats['http_apis'] += 1

    def _find_temporal_workflows(self, content: str, file_path: str, module: str):
        """Find Temporal workflows."""
        pattern = r'@workflow\.defn\s+class\s+(\w+)'
        matches = re.finditer(pattern, content, re.MULTILINE)

        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            workflow_name = match.group(1)

            self.apis['temporal_workflows'].append({
                'module': module,
                'file': file_path,
                'line': line_num,
                'workflow_name': workflow_name
            })
            self.stats['temporal_workflows'] += 1

    def _find_temporal_activities(self, content: str, file_path: str, module: str):
        """Find Temporal activities."""
        pattern = r'@activity\.defn\s+async def\s+(\w+)'
        matches = re.finditer(pattern, content, re.MULTILINE)

        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            activity_name = match.group(1)

            self.apis['temporal_activities'].append({
                'module': module,
                'file': file_path,
                'line': line_num,
                'activity_name': activity_name
            })
            self.stats['temporal_activities'] += 1

    def _find_eventbus_handlers(self, content: str, file_path: str, module: str):
        """Find EventBus event handlers."""
        patterns = [
            r'@event_handler\(["\']([^"\']+)["\']',
            r'event_bus\.subscribe\(["\']([^"\']+)["\']',
            r'\.on\(["\']([^"\']+)["\']'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                event_type = match.group(1)

                func_name = self._find_function_name(content, match.end())

                self.apis['eventbus_handlers'].append({
                    'module': module,
                    'file': file_path,
                    'line': line_num,
                    'event_type': event_type,
                    'handler': func_name
                })
                self.stats['eventbus_handlers'] += 1

    def _find_grpc_services(self, content: str, file_path: str, module: str):
        """Find gRPC service definitions."""
        # gRPC service classes
        pattern = r'class\s+(\w+Servicer)\('
        matches = re.finditer(pattern, content, re.MULTILINE)

        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            service_name = match.group(1)

            self.apis['grpc_services'].append({
                'module': module,
                'file': file_path,
                'line': line_num,
                'service_name': service_name
            })
            self.stats['grpc_services'] += 1

    def _find_graphql_resolvers(self, content: str, file_path: str, module: str):
        """Find GraphQL resolvers."""
        patterns = [
            r'@strawberry\.field',
            r'@strawberry\.mutation',
            r'@strawberry\.subscription'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                func_name = self._find_function_name(content, match.end())

                self.apis['graphql_resolvers'].append({
                    'module': module,
                    'file': file_path,
                    'line': line_num,
                    'resolver': func_name
                })
                self.stats['graphql_resolvers'] += 1

    def _find_function_name(self, content: str, start_pos: int) -> str:
        """Find function name after decorator."""
        # Look for next function definition
        func_match = re.search(r'(?:async\s+)?def\s+(\w+)', content[start_pos:start_pos+500])
        if func_match:
            return func_match.group(1)
        return "unknown"

    def generate_report(self, output_dir: str):
        """Generate API report."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)

        # JSON report
        json_path = output_path / "api_map.json"
        with open(json_path, 'w') as f:
            json.dump({
                'stats': dict(self.stats),
                'apis': self.apis
            }, f, indent=2)

        print(f"✅ JSON report: {json_path}")

        # Markdown report
        md_path = output_path / "api_map.md"
        with open(md_path, 'w') as f:
            f.write("# Complete API Map\n\n")
            f.write("## Statistics\n\n")

            total_apis = sum(self.stats.values())
            f.write(f"**Total APIs: {total_apis}**\n\n")

            for api_type, count in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{api_type}**: {count}\n")

            # HTTP APIs
            if self.apis['http_apis']:
                f.write("\n## HTTP APIs\n\n")
                f.write("| Method | Path | Module | File | Function |\n")
                f.write("|--------|------|--------|------|----------|\n")

                for api in sorted(self.apis['http_apis'], key=lambda x: (x['module'], x['path'])):
                    f.write(f"| {api['method']} | `{api['path']}` | {api['module']} | {api['file']}:{api['line']} | `{api['function']}()` |\n")

            # Temporal Workflows
            if self.apis['temporal_workflows']:
                f.write("\n## Temporal Workflows\n\n")
                f.write("| Workflow | Module | File |\n")
                f.write("|----------|--------|------|\n")

                for wf in sorted(self.apis['temporal_workflows'], key=lambda x: x['workflow_name']):
                    f.write(f"| `{wf['workflow_name']}` | {wf['module']} | {wf['file']}:{wf['line']} |\n")

            # Temporal Activities
            if self.apis['temporal_activities']:
                f.write("\n## Temporal Activities\n\n")
                f.write("| Activity | Module | File |\n")
                f.write("|----------|--------|------|\n")

                for act in sorted(self.apis['temporal_activities'], key=lambda x: x['activity_name']):
                    f.write(f"| `{act['activity_name']}()` | {act['module']} | {act['file']}:{act['line']} |\n")

            # EventBus Handlers
            if self.apis['eventbus_handlers']:
                f.write("\n## EventBus Handlers\n\n")
                f.write("| Event Type | Handler | Module | File |\n")
                f.write("|------------|---------|--------|------|\n")

                for handler in sorted(self.apis['eventbus_handlers'], key=lambda x: x['event_type']):
                    f.write(f"| `{handler['event_type']}` | `{handler['handler']}()` | {handler['module']} | {handler['file']}:{handler['line']} |\n")

        print(f"✅ Markdown report: {md_path}")

        # Summary
        print(f"\n📊 API SUMMARY:")
        print(f"   Total APIs: {total_apis}")
        for api_type, count in sorted(self.stats.items(), key=lambda x: x[1], reverse=True):
            print(f"   {api_type}: {count}")


def main():
    """Main entry point."""
    root_dir = "/Users/MD/AI-Platform-ISO"

    directories = [
        "intelligent-core",
        "platform-services",
        "infrastructure",
        "shared"
    ]

    mapper = APIMapper(root_dir)
    mapper.scan_project(directories)
    mapper.generate_report(f"{root_dir}/infrastructure/AI-office-infrastructure/devops-agent/reports-generated")


if __name__ == "__main__":
    main()
