#!/usr/bin/env python3
"""
Event Catalog Generator
======================

Automatically scans BCM Platform codebase and generates:
1. Event inventory (EVENTS.md)
2. Event publishers map
3. Event subscribers map
4. EventCatalog pages (optional)

Usage:
    python3 event_catalog_generator.py
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict


class EventCatalogGenerator:
    """Generates event catalog from codebase analysis."""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.events = defaultdict(lambda: {
            'publishers': set(),
            'subscribers': set(),
            'schema': None,
            'description': None
        })
        self.stats = {
            'total_events': 0,
            'total_publishers': 0,
            'total_subscribers': 0,
            'files_scanned': 0
        }

    def scan_codebase(self):
        """Scan entire codebase for event usage."""
        print(" Scanning codebase for events...")

        # Directories to scan
        scan_dirs = [
            'intelligent-core',
            'platform-services',
            'shared'
        ]

        for dir_name in scan_dirs:
            dir_path = self.root_dir / dir_name
            if not dir_path.exists():
                print(f"️  Directory not found: {dir_name}")
                continue

            print(f" Scanning: {dir_name}")
            self._scan_directory(dir_path, dir_name)

        self.stats['total_events'] = len(self.events)
        print(f"\n Scan complete!")
        print(f"   Found {self.stats['total_events']} unique events")
        print(f"   Scanned {self.stats['files_scanned']} files")

    def _scan_directory(self, path: Path, module_name: str):
        """Recursively scan directory for Python files."""
        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".pyc" in str(py_file):
                continue

            try:
                self._analyze_file(py_file, module_name)
                self.stats['files_scanned'] += 1
            except Exception as e:
                # Skip files that can't be read
                pass

    def _analyze_file(self, file_path: Path, module_name: str):
        """Analyze single file for event publishing and subscribing."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except:
            return

        relative_path = str(file_path.relative_to(self.root_dir))

        # Find event publishers
        self._find_publishers(content, relative_path, module_name)

        # Find event subscribers
        self._find_subscribers(content, relative_path, module_name)

    def _find_publishers(self, content: str, file_path: str, module: str):
        """Find event publishers in file."""

        # Pattern 1: eventbus.publish("event.type", {...})
        pattern1 = re.compile(
            r'(?:eventbus|event_bus)\.publish\s*\(\s*["\']([^"\']+)["\']',
            re.MULTILINE
        )

        # Pattern 2: await publish_event("event.type", ...)
        pattern2 = re.compile(
            r'(?:await\s+)?publish_event\s*\(\s*["\']([^"\']+)["\']',
            re.MULTILINE
        )

        # Pattern 3: EventPublisher.publish("event.type", ...)
        pattern3 = re.compile(
            r'EventPublisher\.publish\s*\(\s*["\']([^"\']+)["\']',
            re.MULTILINE
        )

        # Pattern 4: self.publish("event.type", ...)
        pattern4 = re.compile(
            r'self\.publish\s*\(\s*["\']([^"\']+)["\']',
            re.MULTILINE
        )

        # Combine all patterns
        for pattern in [pattern1, pattern2, pattern3, pattern4]:
            for match in pattern.finditer(content):
                event_type = match.group(1)
                self.events[event_type]['publishers'].add(f"{module}/{file_path}")
                self.stats['total_publishers'] += 1

    def _find_subscribers(self, content: str, file_path: str, module: str):
        """Find event subscribers in file."""

        # Pattern 1: eventbus.subscribe("event.type", handler)
        pattern1 = re.compile(
            r'(?:eventbus|event_bus)\.subscribe\s*\(\s*["\']([^"\']+)["\']',
            re.MULTILINE
        )

        # Pattern 2: @event_handler("event.type")
        pattern2 = re.compile(
            r'@event_handler\s*\(\s*["\']([^"\']+)["\']',
            re.MULTILINE
        )

        # Pattern 3: .on("event.type", handler)
        pattern3 = re.compile(
            r'\.on\s*\(\s*["\']([^"\']+)["\']',
            re.MULTILINE
        )

        # Combine all patterns
        for pattern in [pattern1, pattern2, pattern3]:
            for match in pattern.finditer(content):
                event_type = match.group(1)
                self.events[event_type]['subscribers'].add(f"{module}/{file_path}")
                self.stats['total_subscribers'] += 1

    def generate_markdown_report(self, output_path: str):
        """Generate Markdown event catalog."""
        print(f"\n Generating Markdown report...")

        output = []
        output.append("# BCM Platform Event Catalog\n")
        output.append(f"**Generated:** Automatically scanned from codebase\n")
        output.append(f"**Total Events:** {self.stats['total_events']}\n")
        output.append(f"**Files Scanned:** {self.stats['files_scanned']}\n")
        output.append("\n---\n")

        # Group events by domain
        domains = defaultdict(list)
        for event_type in sorted(self.events.keys()):
            domain = event_type.split('.')[0] if '.' in event_type else 'other'
            domains[domain].append(event_type)

        # Generate sections per domain
        for domain in sorted(domains.keys()):
            output.append(f"\n## {domain.upper()} Events\n")

            for event_type in domains[domain]:
                event_data = self.events[event_type]

                output.append(f"\n### `{event_type}`\n")

                # Publishers
                if event_data['publishers']:
                    output.append(f"\n**Publishers ({len(event_data['publishers'])}):**\n")
                    for publisher in sorted(event_data['publishers']):
                        # Shorten path for readability
                        short_path = publisher.split('/')[-2:] if '/' in publisher else publisher
                        output.append(f"- `{'/'.join(short_path)}`\n")
                else:
                    output.append(f"\n**Publishers:** ️ None found\n")

                # Subscribers
                if event_data['subscribers']:
                    output.append(f"\n**Subscribers ({len(event_data['subscribers'])}):**\n")
                    for subscriber in sorted(event_data['subscribers']):
                        short_path = subscriber.split('/')[-2:] if '/' in subscriber else subscriber
                        output.append(f"- `{'/'.join(short_path)}`\n")
                else:
                    output.append(f"\n**Subscribers:** ️ None found\n")

                output.append("\n")

        # Write to file
        report_path = Path(output_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(''.join(output))

        print(f" Markdown report: {report_path}")

    def generate_json_report(self, output_path: str):
        """Generate JSON event catalog."""
        print(f"\n Generating JSON report...")

        # Convert sets to lists for JSON serialization
        events_json = {}
        for event_type, event_data in self.events.items():
            events_json[event_type] = {
                'publishers': sorted(list(event_data['publishers'])),
                'subscribers': sorted(list(event_data['subscribers'])),
                'publisher_count': len(event_data['publishers']),
                'subscriber_count': len(event_data['subscribers'])
            }

        report = {
            'stats': self.stats,
            'events': events_json
        }

        # Write to file
        report_path = Path(output_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2))

        print(f" JSON report: {report_path}")

    def generate_mermaid_diagram(self, output_path: str):
        """Generate Mermaid event flow diagram."""
        print(f"\n Generating Mermaid diagram...")

        output = []
        output.append("```mermaid\n")
        output.append("graph LR\n")

        # Create unique service nodes
        services = set()
        for event_type, event_data in self.events.items():
            for publisher in event_data['publishers']:
                service = publisher.split('/')[0]
                services.add(service)
            for subscriber in event_data['subscribers']:
                service = subscriber.split('/')[0]
                services.add(service)

        # Define service nodes
        for service in sorted(services):
            service_id = service.replace('-', '_')
            output.append(f"    {service_id}[{service}]\n")

        output.append("\n")

        # Add event flows (limit to top 20 events to keep diagram readable)
        event_count = 0
        for event_type in sorted(self.events.keys()):
            if event_count >= 20:
                break

            event_data = self.events[event_type]
            if not event_data['publishers'] or not event_data['subscribers']:
                continue

            event_id = event_type.replace('.', '_')

            # Publisher -> Event
            for publisher in event_data['publishers']:
                publisher_service = publisher.split('/')[0].replace('-', '_')
                output.append(f"    {publisher_service} -->|{event_type}| {event_id}(({event_type}))\n")

            # Event -> Subscriber
            for subscriber in event_data['subscribers']:
                subscriber_service = subscriber.split('/')[0].replace('-', '_')
                output.append(f"    {event_id} --> {subscriber_service}\n")

            output.append("\n")
            event_count += 1

        output.append("```\n")

        # Write to file
        diagram_path = Path(output_path)
        diagram_path.parent.mkdir(parents=True, exist_ok=True)
        diagram_path.write_text(''.join(output))

        print(f" Mermaid diagram: {diagram_path}")

    def analyze_orphaned_events(self):
        """Find events with no publishers or no subscribers."""
        print("\n Analyzing orphaned events...")

        no_publishers = []
        no_subscribers = []

        for event_type, event_data in self.events.items():
            if not event_data['publishers']:
                no_publishers.append(event_type)
            if not event_data['subscribers']:
                no_subscribers.append(event_type)

        if no_publishers:
            print(f"\n️  Events with NO PUBLISHERS ({len(no_publishers)}):")
            for event in sorted(no_publishers)[:10]:  # Show first 10
                print(f"   - {event}")

        if no_subscribers:
            print(f"\n️  Events with NO SUBSCRIBERS ({len(no_subscribers)}):")
            for event in sorted(no_subscribers)[:10]:  # Show first 10
                print(f"   - {event}")

        return {
            'no_publishers': no_publishers,
            'no_subscribers': no_subscribers
        }


def main():
    """Main entry point."""
    root_dir = "/Users/MD/AI-Platform-ISO"

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" BCM Platform Event Catalog Generator")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # Initialize generator
    generator = EventCatalogGenerator(root_dir)

    # Scan codebase
    generator.scan_codebase()

    # Generate reports
    generator.generate_markdown_report(
        f"{root_dir}/infrastructure/events/EVENTS.md"
    )
    generator.generate_json_report(
        f"{root_dir}/infrastructure/events/events_catalog.json"
    )
    generator.generate_mermaid_diagram(
        f"{root_dir}/infrastructure/events/EVENT_FLOW.md"
    )

    # Analyze issues
    orphaned = generator.analyze_orphaned_events()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" Event Catalog Generation Complete!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"\n Output files:")
    print(f"   • {root_dir}/infrastructure/events/EVENTS.md")
    print(f"   • {root_dir}/infrastructure/events/events_catalog.json")
    print(f"   • {root_dir}/infrastructure/events/EVENT_FLOW.md")
    print(f"   • {root_dir}/infrastructure/events/asyncapi.yaml (already created)")
    print("\n")


if __name__ == "__main__":
    main()
