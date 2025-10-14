#!/usr/bin/env python3
"""
Automation Toolkit Integration for ISO 22301 Compliance API

This module integrates tools/analyzers with the unified monitoring system:
1. AST Analyzer → Auto-discovery of services with /health and /metrics
2. Dependency Mapper → Root cause analysis for incidents
3. Security Scanner (Bandit) → Continuous security monitoring
4. Complexity Analyzer (Radon) → Code quality metrics

Integration with:
- Prometheus (metrics export)
- ISO 22301 Compliance API (compliance tracking)
- Grafana (visualization)
"""

import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Add tools to Python path
TOOLS_DIR = Path(__file__).parent.parent.parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))

try:
    from analyzers.ast_analyzer import ASTAnalyzer
    from analyzers.dependency_mapper import DependencyMapper
except ImportError as e:
    logging.warning(f"Automation Toolkit not found: {e}. Install with: cd tools && ./setup.sh")
    ASTAnalyzer = None
    DependencyMapper = None


logger = logging.getLogger("automation_toolkit_integration")


class AutomationToolkitIntegration:
    """
    Integration layer between Automation Toolkit and Monitoring System

    Provides:
    - Service auto-discovery via AST analysis
    - Root cause analysis via dependency mapping
    - Security metrics via Bandit
    - Code quality metrics via Radon
    """

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.tools_dir = self.project_root / "tools"
        self.reports_dir = self.tools_dir / "reports"

        # Initialize analyzers if available
        self.ast_analyzer = ASTAnalyzer() if ASTAnalyzer else None
        self.dependency_mapper = DependencyMapper() if DependencyMapper else None

        logger.info(f"Automation Toolkit Integration initialized (project: {self.project_root})")

    # ========================================================================
    # SERVICE DISCOVERY - Auto-detect services with /health and /metrics
    # ========================================================================

    async def discover_services(self) -> Dict[str, Any]:
        """
        Auto-discover all services by analyzing AST for /health and /metrics endpoints.

        Returns:
            {
                'total_services': int,
                'monitoring_endpoints': [
                    {
                        'service': str,
                        'file': str,
                        'port': int,
                        'has_health': bool,
                        'has_metrics': bool,
                        'endpoints': [...]
                    }
                ],
                'coverage': {
                    'total': int,
                    'with_health': int,
                    'with_metrics': int,
                    'percentage': float
                }
            }
        """
        if not self.ast_analyzer:
            logger.error("AST Analyzer not available. Install Automation Toolkit.")
            return {'error': 'AST Analyzer not available'}

        logger.info("Running AST analysis for service discovery...")

        # Run AST analysis
        try:
            results = self.ast_analyzer.analyze_project()
        except Exception as e:
            logger.error(f"AST analysis failed: {e}")
            return {'error': str(e)}

        # Extract services with monitoring endpoints
        services = {}

        for endpoint in results.get('endpoints', []):
            # Look for /health, /metrics, /ready endpoints
            path = endpoint.get('path', '')

            if path not in ['/health', '/metrics', '/ready']:
                continue

            # Extract service name from file path
            file_path = endpoint.get('file', '')
            service_name = self._extract_service_name(file_path)

            if service_name not in services:
                services[service_name] = {
                    'service': service_name,
                    'file': file_path,
                    'port': self._extract_port(file_path),
                    'has_health': False,
                    'has_metrics': False,
                    'endpoints': []
                }

            # Mark endpoint type
            if path == '/health':
                services[service_name]['has_health'] = True
            elif path == '/metrics':
                services[service_name]['has_metrics'] = True

            services[service_name]['endpoints'].append(endpoint)

        # Calculate coverage
        total = len(services)
        with_health = sum(1 for s in services.values() if s['has_health'])
        with_metrics = sum(1 for s in services.values() if s['has_metrics'])

        coverage = {
            'total': total,
            'with_health': with_health,
            'with_metrics': with_metrics,
            'percentage': (with_metrics / total * 100) if total > 0 else 0
        }

        logger.info(f"Service discovery complete: {total} services, {coverage['percentage']:.1f}% coverage")

        return {
            'total_services': total,
            'monitoring_endpoints': list(services.values()),
            'coverage': coverage,
            'timestamp': datetime.now().isoformat()
        }

    async def register_discovered_services(self, compliance_api_url: str = "http://localhost:8045") -> Dict:
        """
        Auto-register all discovered services with ISO 22301 Compliance API.

        Args:
            compliance_api_url: URL of ISO 22301 Compliance API

        Returns:
            {
                'registered': int,
                'failed': int,
                'services': [...]
            }
        """
        import httpx

        discovery = await self.discover_services()

        if 'error' in discovery:
            return discovery

        registered = 0
        failed = 0
        results = []

        async with httpx.AsyncClient() as client:
            for service in discovery['monitoring_endpoints']:
                # Skip if missing metrics endpoint
                if not service['has_metrics']:
                    logger.warning(f"Skipping {service['service']}: no /metrics endpoint")
                    failed += 1
                    continue

                # Prepare registration payload
                registration = {
                    'name': service['service'],
                    'url': f"http://localhost:{service['port']}",
                    'type': self._classify_service_type(service['service']),
                    'iso_clauses': self._map_iso_clauses(service['service']),
                    'description': f"Auto-discovered: {service['service']}",
                    'compliance_critical': self._is_critical_service(service['service']),
                    'metrics_endpoint': '/metrics',
                    'health_endpoint': '/health' if service['has_health'] else None
                }

                try:
                    response = await client.post(
                        f"{compliance_api_url}/register-service",
                        json=registration,
                        timeout=5.0
                    )

                    if response.status_code == 200:
                        registered += 1
                        logger.info(f"Registered: {service['service']}")
                        results.append({'service': service['service'], 'status': 'registered'})
                    else:
                        failed += 1
                        logger.error(f"Failed to register {service['service']}: {response.text}")
                        results.append({'service': service['service'], 'status': 'failed', 'error': response.text})

                except Exception as e:
                    failed += 1
                    logger.error(f"Exception registering {service['service']}: {e}")
                    results.append({'service': service['service'], 'status': 'error', 'error': str(e)})

        return {
            'registered': registered,
            'failed': failed,
            'services': results,
            'timestamp': datetime.now().isoformat()
        }

    # ========================================================================
    # ROOT CAUSE ANALYSIS - Dependency mapping for incident investigation
    # ========================================================================

    async def analyze_dependencies(self, service_name: str = None) -> Dict:
        """
        Build dependency graph and perform root cause analysis.

        Args:
            service_name: Service to analyze (None = all services)

        Returns:
            {
                'dependencies': {
                    'service_name': ['dependency1', 'dependency2', ...]
                },
                'reverse_dependencies': {...},
                'circular_dependencies': [...],
                'total_services': int
            }
        """
        if not self.dependency_mapper:
            logger.error("Dependency Mapper not available. Install Automation Toolkit.")
            return {'error': 'Dependency Mapper not available'}

        logger.info("Running dependency analysis...")

        try:
            results = self.dependency_mapper.analyze_dependencies()
        except Exception as e:
            logger.error(f"Dependency analysis failed: {e}")
            return {'error': str(e)}

        # If specific service requested, filter results
        if service_name:
            deps = results['dependencies'].get(service_name, [])
            return {
                'service': service_name,
                'dependencies': deps,
                'dependency_count': len(deps),
                'timestamp': datetime.now().isoformat()
            }

        return {
            **results,
            'timestamp': datetime.now().isoformat()
        }

    async def find_root_cause(self, failed_service: str, prometheus_url: str = "http://localhost:9090") -> Dict:
        """
        Find root cause of service failure by checking all dependencies.

        Args:
            failed_service: Service that is failing
            prometheus_url: Prometheus URL for health checks

        Returns:
            {
                'failed_service': str,
                'dependencies': [...],
                'down_dependencies': [...],
                'root_cause': str or None,
                'recommendation': str
            }
        """
        import httpx

        # Get dependencies
        dep_analysis = await self.analyze_dependencies(failed_service)

        if 'error' in dep_analysis:
            return dep_analysis

        dependencies = dep_analysis.get('dependencies', [])

        if not dependencies:
            return {
                'failed_service': failed_service,
                'dependencies': [],
                'root_cause': None,
                'recommendation': f'{failed_service} has no dependencies. Check service logs.'
            }

        # Check health of all dependencies via Prometheus
        down_dependencies = []

        async with httpx.AsyncClient() as client:
            for dep in dependencies:
                try:
                    # Query Prometheus for service health
                    query = f'up{{job="{dep}"}}'
                    response = await client.get(
                        f"{prometheus_url}/api/v1/query",
                        params={'query': query},
                        timeout=5.0
                    )

                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('data', {}).get('result', [])

                        if results:
                            value = int(results[0]['value'][1])
                            if value == 0:  # Service is down
                                down_dependencies.append(dep)
                                logger.warning(f"Dependency {dep} is DOWN")
                        else:
                            logger.warning(f"No metrics for {dep}")

                except Exception as e:
                    logger.error(f"Failed to check {dep}: {e}")

        # Determine root cause
        root_cause = None
        recommendation = ""

        if down_dependencies:
            root_cause = down_dependencies[0]  # First failed dependency
            recommendation = f"Root cause: {root_cause} is down. Restart {root_cause} to fix {failed_service}."
        else:
            recommendation = f"All dependencies are UP. Check {failed_service} internal errors."

        return {
            'failed_service': failed_service,
            'dependencies': dependencies,
            'down_dependencies': down_dependencies,
            'root_cause': root_cause,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }

    # ========================================================================
    # SECURITY MONITORING - Bandit security scans
    # ========================================================================

    async def run_security_scan(self, path: str = "platform-services") -> Dict:
        """
        Run Bandit security scan and return results.

        Args:
            path: Path to scan (default: platform-services)

        Returns:
            {
                'status': 'clean' or 'issues_found',
                'high_severity': int,
                'medium_severity': int,
                'low_severity': int,
                'issues': [...]
            }
        """
        logger.info(f"Running Bandit security scan on {path}...")

        scan_path = self.project_root / path

        try:
            result = subprocess.run(
                ['bandit', '-r', str(scan_path), '-f', 'json', '-ll'],
                capture_output=True,
                text=True,
                timeout=300
            )

            # Bandit returns non-zero exit code if issues found
            if result.returncode == 0:
                return {
                    'status': 'clean',
                    'high_severity': 0,
                    'medium_severity': 0,
                    'low_severity': 0,
                    'issues': [],
                    'timestamp': datetime.now().isoformat()
                }

            # Parse JSON output
            data = json.loads(result.stdout)
            issues = data.get('results', [])

            # Count by severity
            high = sum(1 for i in issues if i.get('issue_severity') == 'HIGH')
            medium = sum(1 for i in issues if i.get('issue_severity') == 'MEDIUM')
            low = sum(1 for i in issues if i.get('issue_severity') == 'LOW')

            logger.warning(f"Security issues found: HIGH={high}, MEDIUM={medium}, LOW={low}")

            return {
                'status': 'issues_found',
                'high_severity': high,
                'medium_severity': medium,
                'low_severity': low,
                'issues': issues,
                'timestamp': datetime.now().isoformat()
            }

        except subprocess.TimeoutExpired:
            logger.error("Bandit scan timed out")
            return {'error': 'Scan timed out'}
        except FileNotFoundError:
            logger.error("Bandit not found. Install with: pip install bandit")
            return {'error': 'Bandit not installed'}
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            return {'error': str(e)}

    # ========================================================================
    # CODE QUALITY METRICS - Radon complexity analysis
    # ========================================================================

    async def analyze_code_complexity(self, service_name: str = None) -> Dict:
        """
        Analyze code complexity using Radon.

        Args:
            service_name: Service to analyze (None = all services)

        Returns:
            {
                'avg_complexity': float,
                'max_complexity': int,
                'high_complexity_functions': [...],
                'complexity_distribution': {...}
            }
        """
        logger.info(f"Running Radon complexity analysis for {service_name or 'all services'}...")

        if service_name:
            scan_path = self.project_root / "platform-services" / service_name
        else:
            scan_path = self.project_root / "platform-services"

        try:
            # Run Radon cyclomatic complexity
            result = subprocess.run(
                ['radon', 'cc', str(scan_path), '-j'],  # JSON output
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                logger.error(f"Radon failed: {result.stderr}")
                return {'error': result.stderr}

            # Parse JSON
            data = json.loads(result.stdout)

            # Calculate metrics
            all_complexities = []
            high_complexity_funcs = []

            for file_path, functions in data.items():
                for func in functions:
                    complexity = func.get('complexity', 0)
                    all_complexities.append(complexity)

                    if complexity > 15:  # High complexity threshold
                        high_complexity_funcs.append({
                            'function': func.get('name'),
                            'file': file_path,
                            'complexity': complexity,
                            'rank': func.get('rank')
                        })

            avg_complexity = sum(all_complexities) / len(all_complexities) if all_complexities else 0
            max_complexity = max(all_complexities) if all_complexities else 0

            # Distribution by grade
            distribution = {
                'A': sum(1 for c in all_complexities if c <= 5),
                'B': sum(1 for c in all_complexities if 6 <= c <= 10),
                'C': sum(1 for c in all_complexities if 11 <= c <= 20),
                'D': sum(1 for c in all_complexities if 21 <= c <= 30),
                'E': sum(1 for c in all_complexities if 31 <= c <= 40),
                'F': sum(1 for c in all_complexities if c > 40)
            }

            logger.info(f"Complexity analysis: avg={avg_complexity:.1f}, max={max_complexity}")

            return {
                'service': service_name or 'all',
                'avg_complexity': round(avg_complexity, 2),
                'max_complexity': max_complexity,
                'total_functions': len(all_complexities),
                'high_complexity_functions': high_complexity_funcs,
                'complexity_distribution': distribution,
                'timestamp': datetime.now().isoformat()
            }

        except FileNotFoundError:
            logger.error("Radon not found. Install with: pip install radon")
            return {'error': 'Radon not installed'}
        except Exception as e:
            logger.error(f"Complexity analysis failed: {e}")
            return {'error': str(e)}

    # ========================================================================
    # PROMETHEUS METRICS EXPORT
    # ========================================================================

    def export_prometheus_metrics(self, discovery: Dict, security: Dict, complexity: Dict) -> str:
        """
        Export metrics in Prometheus format.

        Args:
            discovery: Service discovery results
            security: Security scan results
            complexity: Complexity analysis results

        Returns:
            Prometheus metrics string
        """
        metrics = []

        # Service discovery metrics
        if 'coverage' in discovery:
            coverage = discovery['coverage']
            metrics.append(f"# HELP automation_service_coverage Service discovery coverage percentage")
            metrics.append(f"# TYPE automation_service_coverage gauge")
            metrics.append(f"automation_service_coverage {coverage.get('percentage', 0)}")

            metrics.append(f"# HELP automation_services_total Total services discovered")
            metrics.append(f"# TYPE automation_services_total gauge")
            metrics.append(f"automation_services_total {coverage.get('total', 0)}")

        # Security metrics
        if 'status' in security and security['status'] == 'issues_found':
            metrics.append(f"# HELP automation_security_high_issues High severity security issues")
            metrics.append(f"# TYPE automation_security_high_issues gauge")
            metrics.append(f"automation_security_high_issues {security.get('high_severity', 0)}")

            metrics.append(f"# HELP automation_security_medium_issues Medium severity security issues")
            metrics.append(f"# TYPE automation_security_medium_issues gauge")
            metrics.append(f"automation_security_medium_issues {security.get('medium_severity', 0)}")

        # Complexity metrics
        if 'avg_complexity' in complexity:
            service = complexity.get('service', 'unknown')
            metrics.append(f"# HELP automation_code_complexity_avg Average cyclomatic complexity")
            metrics.append(f"# TYPE automation_code_complexity_avg gauge")
            metrics.append(f'automation_code_complexity_avg{{service="{service}"}} {complexity.get("avg_complexity", 0)}')

            metrics.append(f"# HELP automation_code_complexity_max Maximum cyclomatic complexity")
            metrics.append(f"# TYPE automation_code_complexity_max gauge")
            metrics.append(f'automation_code_complexity_max{{service="{service}"}} {complexity.get("max_complexity", 0)}')

        return "\n".join(metrics) + "\n"

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _extract_service_name(self, file_path: str) -> str:
        """Extract service name from file path."""
        path = Path(file_path)

        # Try to find service directory
        for part in path.parts:
            if part.endswith('-service') or part.endswith('_service'):
                return part.replace('-service', '_service').replace('_service', '-service')

        # Fallback: use parent directory
        return path.parent.name

    def _extract_port(self, file_path: str) -> int:
        """Extract port from file path (heuristic)."""
        # Default ports for known services
        ports = {
            'validation': 8022,
            'documents': 8024,
            'governance': 8020,
            'planning': 8011,
            'plans': 8023,
            'bia': 8012,
            'compliance': 8014,
            'learning': 8021,
            'response': 8041
        }

        service_name = self._extract_service_name(file_path)
        for key, port in ports.items():
            if key in service_name:
                return port

        return 8000  # Default

    def _classify_service_type(self, service_name: str) -> str:
        """Classify service type for ISO mapping."""
        bcm_services = ['validation', 'documents', 'governance', 'planning', 'plans', 'bia', 'compliance', 'learning', 'response']

        for bcm in bcm_services:
            if bcm in service_name:
                return 'bcm'

        return 'platform'

    def _map_iso_clauses(self, service_name: str) -> List[str]:
        """Map service to ISO 22301 clauses."""
        mapping = {
            'validation': ['8.5'],
            'documents': ['7.5'],
            'governance': ['5.3', '7.1', '7.3'],
            'planning': ['8.3'],
            'plans': ['8.4'],
            'bia': ['8.2.2'],
            'compliance': ['9.2', '10.1', '10.2'],
            'learning': ['7.2'],
            'response': ['8.4']
        }

        for key, clauses in mapping.items():
            if key in service_name:
                return clauses

        return []

    def _is_critical_service(self, service_name: str) -> bool:
        """Determine if service is compliance-critical."""
        critical = ['validation', 'documents', 'governance', 'planning', 'plans', 'bia', 'compliance', 'response']

        for crit in critical:
            if crit in service_name:
                return True

        return False


# Module-level convenience functions

async def auto_discover_and_register():
    """Convenience function: discover and register all services."""
    integration = AutomationToolkitIntegration()
    return await integration.register_discovered_services()


async def analyze_incident_root_cause(failed_service: str):
    """Convenience function: find root cause of service failure."""
    integration = AutomationToolkitIntegration()
    return await integration.find_root_cause(failed_service)
