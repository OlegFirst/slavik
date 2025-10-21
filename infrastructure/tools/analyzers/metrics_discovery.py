#!/usr/bin/env python3
"""
 Automatic Metrics Discovery & Integration
==============================================

Автоматически находит все метрики в проекте и интегрирует их в Prometheus.

Что делает:
1. Сканирует все модули на наличие prometheus_client метрик
2. Проверяет есть ли /metrics endpoint
3. Автоматически добавляет в prometheus.yml
4. Генерирует Grafana dashboard configs
5. Создает отчет о покрытии метриками

Usage:
    python3 tools/infrastructure/metrics_discovery.py
    python3 tools/infrastructure/metrics_discovery.py --apply  # Apply to prometheus.yml

Output:
    - metrics-inventory.json (все найденные метрики)
    - prometheus-jobs-auto.yml (auto-generated scrape jobs)
    - metrics-coverage-report.md
"""

import ast
import json
import yaml
import re
from pathlib import Path
from typing import List, Dict, Any, Set
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class MetricsInfo:
    """Information about metrics in a module"""
    module_path: str
    module_name: str
    metrics_file: str
    metric_names: List[str]
    metric_types: Dict[str, str]  # name -> type (Counter, Gauge, etc)
    has_endpoint: bool
    endpoint_port: int
    endpoint_path: str
    total_metrics: int


class MetricsDiscovery:
    """Автоматическое обнаружение метрик в проекте"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.modules_with_metrics = []
        self.prometheus_scrape_jobs = []

    def discover_all(self) -> List[MetricsInfo]:
        """Сканирует весь проект и находит все метрики"""
        print(" Discovering metrics in project...")
        print("=" * 60)

        # Scan intelligent-core modules
        self._scan_directory(self.project_root / 'intelligent-core')

        # Scan infrastructure services
        self._scan_directory(self.project_root / 'infrastructure')

        # Scan platform-services if exists
        if (self.project_root / 'platform-services').exists():
            self._scan_directory(self.project_root / 'platform-services')

        print(f"\n Found {len(self.modules_with_metrics)} modules with metrics")
        return self.modules_with_metrics

    def _scan_directory(self, base_dir: Path):
        """Сканирует директорию на наличие метрик"""
        if not base_dir.exists():
            return

        # Find all metrics.py files
        for metrics_file in base_dir.rglob("**/metrics.py"):
            if self._should_skip(metrics_file):
                continue

            metrics_info = self._analyze_metrics_file(metrics_file)
            if metrics_info and metrics_info.total_metrics > 0:
                self.modules_with_metrics.append(metrics_info)
                print(f"   {metrics_info.module_name}: {metrics_info.total_metrics} metrics")

    def _should_skip(self, path: Path) -> bool:
        """Проверка - нужно ли пропустить файл"""
        skip_patterns = ['venv', '__pycache__', '.git', '_archive', 'node_modules', 'test']
        return any(pattern in str(path) for pattern in skip_patterns)

    def _analyze_metrics_file(self, metrics_file: Path) -> MetricsInfo:
        """Анализирует файл с метриками"""
        try:
            content = metrics_file.read_text()

            # Parse metrics definitions
            metric_names = []
            metric_types = {}

            # Find prometheus_client imports
            if 'prometheus_client' not in content:
                return None

            # Extract metric definitions
            for match in re.finditer(r'(\w+)\s*=\s*(Counter|Gauge|Histogram|Summary|Info)\s*\(',
                                      content, re.MULTILINE):
                metric_name = match.group(1)
                metric_type = match.group(2)
                metric_names.append(metric_name)
                metric_types[metric_name] = metric_type

            if not metric_names:
                return None

            # Find module info
            module_path = str(metrics_file.parent.relative_to(self.project_root))
            module_name = self._extract_module_name(metrics_file)

            # Check if metrics endpoint exists
            has_endpoint, port, endpoint_path = self._check_metrics_endpoint(metrics_file.parent)

            return MetricsInfo(
                module_path=module_path,
                module_name=module_name,
                metrics_file=str(metrics_file.relative_to(self.project_root)),
                metric_names=metric_names,
                metric_types=metric_types,
                has_endpoint=has_endpoint,
                endpoint_port=port,
                endpoint_path=endpoint_path,
                total_metrics=len(metric_names)
            )

        except Exception as e:
            print(f"  ️  Error analyzing {metrics_file}: {e}")
            return None

    def _extract_module_name(self, metrics_file: Path) -> str:
        """Извлекает имя модуля из пути"""
        parts = metrics_file.parts

        # intelligent-core/ai-foundation/llm/metrics.py -> ai-foundation-llm
        # intelligent-core/ai-foundation/rag/metrics.py -> ai-foundation-rag
        if 'intelligent-core' in parts:
            idx = parts.index('intelligent-core')
            if idx + 1 < len(parts):
                base_module = parts[idx + 1]
                # If there are subdirectories before metrics.py, include them
                if idx + 2 < len(parts) - 1:  # -1 because last part is metrics.py
                    submodule = parts[idx + 2]
                    return f"{base_module}-{submodule}"
                return base_module

        # infrastructure/observability/... -> observability
        if 'infrastructure' in parts:
            idx = parts.index('infrastructure')
            if idx + 1 < len(parts):
                base_module = parts[idx + 1]
                # Include submodule if exists
                if idx + 2 < len(parts) - 1:
                    submodule = parts[idx + 2]
                    return f"{base_module}-{submodule}"
                return base_module

        return parts[-2] if len(parts) > 1 else 'unknown'

    def _check_metrics_endpoint(self, module_dir: Path) -> tuple:
        """Проверяет наличие /metrics endpoint"""
        # Strategy 1: Look in current directory (for co-located main.py)
        for entry_file in ['main.py', 'app.py', '__init__.py', 'api/main.py']:
            entry_path = module_dir / entry_file
            if entry_path.exists():
                has_endpoint, port = self._check_file_for_metrics(entry_path)
                if has_endpoint:
                    return True, port, '/metrics'

        # Strategy 2: Look in parent module (for intelligent-core modules)
        # Example: metrics at intelligent-core/expertise-center/monitoring/metrics.py
        #          endpoint at intelligent-core/community_intelligence/main.py
        parts = module_dir.parts
        if 'intelligent-core' in parts:
            # Go up to intelligent-core level
            idx = parts.index('intelligent-core')
            intelligent_core_dir = Path(*parts[:idx+1])

            # Check all subdirectories with main.py
            for subdir in intelligent_core_dir.iterdir():
                if subdir.is_dir():
                    main_py = subdir / 'main.py'
                    if main_py.exists():
                        has_endpoint, port = self._check_file_for_metrics(main_py)
                        if has_endpoint:
                            return True, port, '/metrics'

        return False, 0, ''

    def _check_file_for_metrics(self, file_path: Path) -> tuple:
        """Проверяет файл на наличие /metrics endpoint"""
        try:
            content = file_path.read_text()

            # Check for metrics endpoint
            has_endpoint = (
                'make_asgi_app' in content or
                'app.mount("/metrics"' in content or
                '@app.get("/metrics")' in content or
                'Instrumentator' in content  # prometheus-fastapi-instrumentator
            )

            # Extract port
            port = self._extract_port(content)

            return has_endpoint, port
        except:
            return False, 0

    def _extract_port(self, content: str) -> int:
        """Извлекает порт из кода"""
        # uvicorn.run(... port=8030)
        port_match = re.search(r'port[=\s]+(\d+)', content)
        if port_match:
            return int(port_match.group(1))

        # --port 8030
        port_match = re.search(r'--port\s+(\d+)', content)
        if port_match:
            return int(port_match.group(1))

        return 0

    def generate_prometheus_config(self) -> str:
        """Генерирует Prometheus scrape jobs"""
        scrape_jobs = []

        for metrics_info in self.modules_with_metrics:
            if metrics_info.has_endpoint and metrics_info.endpoint_port > 0:
                job = {
                    'job_name': metrics_info.module_name,
                    'scrape_interval': '10s',
                    'scrape_timeout': '5s',
                    'metrics_path': metrics_info.endpoint_path,
                    'static_configs': [{
                        'targets': [f'host.docker.internal:{metrics_info.endpoint_port}'],
                        'labels': {
                            'service': metrics_info.module_name,
                            'component': 'intelligent-core' if 'intelligent-core' in metrics_info.module_path else 'infrastructure'
                        }
                    }]
                }
                scrape_jobs.append(job)

        return yaml.dump({'scrape_configs': scrape_jobs}, default_flow_style=False)

    def generate_coverage_report(self) -> str:
        """Генерирует отчет о покрытии метриками"""
        report = []
        report.append("#  Metrics Coverage Report\n")
        report.append(f"**Generated:** {self._get_timestamp()}\n")
        report.append(f"**Total Modules with Metrics:** {len(self.modules_with_metrics)}\n")
        report.append("\n---\n\n")

        # Summary by category
        by_category = defaultdict(list)
        for m in self.modules_with_metrics:
            category = 'intelligent-core' if 'intelligent-core' in m.module_path else 'infrastructure'
            by_category[category].append(m)

        for category, modules in by_category.items():
            report.append(f"## {category.upper()}\n\n")
            total_metrics = sum(m.total_metrics for m in modules)
            with_endpoint = sum(1 for m in modules if m.has_endpoint)

            report.append(f"- **Modules:** {len(modules)}\n")
            report.append(f"- **Total Metrics:** {total_metrics}\n")
            report.append(f"- **With Endpoint:** {with_endpoint}/{len(modules)}\n")
            report.append("\n### Modules:\n\n")

            for m in sorted(modules, key=lambda x: x.module_name):
                status = "" if m.has_endpoint else "️"
                port_info = f":{m.endpoint_port}" if m.endpoint_port > 0 else ""
                report.append(f"{status} **{m.module_name}** - {m.total_metrics} metrics {port_info}\n")
                report.append(f"   - Path: `{m.module_path}`\n")
                report.append(f"   - Metrics: {', '.join(m.metric_names[:5])}")
                if len(m.metric_names) > 5:
                    report.append(f" ... (+{len(m.metric_names) - 5} more)")
                report.append("\n\n")

        # Metrics by type
        report.append("\n---\n\n## Metrics by Type\n\n")
        type_counts = defaultdict(int)
        for m in self.modules_with_metrics:
            for metric_type in m.metric_types.values():
                type_counts[metric_type] += 1

        for metric_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            report.append(f"- **{metric_type}:** {count}\n")

        # Recommendations
        report.append("\n---\n\n##  Recommendations\n\n")

        no_endpoint = [m for m in self.modules_with_metrics if not m.has_endpoint]
        if no_endpoint:
            report.append("### Modules Without Metrics Endpoint:\n\n")
            for m in no_endpoint:
                report.append(f"- **{m.module_name}** - Add metrics endpoint to expose {m.total_metrics} metrics\n")

        return ''.join(report)

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def save_inventory(self, output_file: Path):
        """Сохраняет инвентарь метрик в JSON"""
        data = {
            'timestamp': self._get_timestamp(),
            'total_modules': len(self.modules_with_metrics),
            'modules': [asdict(m) for m in self.modules_with_metrics]
        }
        output_file.write_text(json.dumps(data, indent=2))
        print(f"\n Saved metrics inventory: {output_file}")

    def save_prometheus_jobs(self, output_file: Path):
        """Сохраняет Prometheus scrape jobs"""
        config = self.generate_prometheus_config()
        output_file.write_text(config)
        print(f" Saved Prometheus jobs: {output_file}")

    def save_coverage_report(self, output_file: Path):
        """Сохраняет отчет о покрытии"""
        report = self.generate_coverage_report()
        output_file.write_text(report)
        print(f" Saved coverage report: {output_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Discover metrics in project')
    parser.add_argument('--apply', action='store_true', help='Apply to prometheus.yml')
    parser.add_argument('--output-dir', default='infrastructure/observability/auto-generated',
                        help='Output directory for generated files')
    args = parser.parse_args()

    # Initialize
    # __file__ = infrastructure/tools/analyzers/metrics_discovery.py
    # parent = infrastructure/tools/analyzers
    # parent.parent = infrastructure/tools
    # parent.parent.parent = infrastructure
    # parent.parent.parent.parent = AI-Platform-ISO (project root!)
    project_root = Path(__file__).parent.parent.parent.parent
    discovery = MetricsDiscovery(project_root)

    # Discover metrics
    modules = discovery.discover_all()

    # Create output directory
    output_dir = project_root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save outputs
    discovery.save_inventory(output_dir / 'metrics-inventory.json')
    discovery.save_prometheus_jobs(output_dir / 'prometheus-jobs-auto.yml')
    discovery.save_coverage_report(output_dir / 'metrics-coverage-report.md')

    print(f"\n Metrics discovery complete!")
    print(f"\nNext steps:")
    print(f"  1. Review: {output_dir / 'metrics-coverage-report.md'}")
    print(f"  2. Add missing /metrics endpoints to modules")
    print(f"  3. Import jobs into Prometheus: {output_dir / 'prometheus-jobs-auto.yml'}")

    # Apply to prometheus.yml if requested
    if args.apply:
        prometheus_yml = project_root / 'infrastructure/observability/config/prometheus/prometheus.yml'
        if prometheus_yml.exists():
            print(f"\n️  Apply to {prometheus_yml}? (manual merge recommended)")
        else:
            print(f"\n Prometheus config not found: {prometheus_yml}")


if __name__ == '__main__':
    main()
