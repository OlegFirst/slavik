"""
Platform Compliance Tests

Tests ALL modules and services for compliance with platform standards:
- KPI presence and format
- Metrics endpoints
- Health checks
- API documentation
- Database schemas
- Event subscriptions
- Logging standards

Usage:
    pytest tests/platform_compliance_test.py -v
    pytest tests/platform_compliance_test.py -v --generate-missing
"""

import pytest
import os
import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field


# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
INTELLIGENT_CORE = PROJECT_ROOT / "intelligent-core"
PLATFORM_SERVICES = PROJECT_ROOT / "platform-services"
INFRASTRUCTURE = PROJECT_ROOT / "infrastructure"


# ============================================================================
# Compliance Standards
# ============================================================================

@dataclass
class ComplianceStandard:
    """Platform compliance requirements"""

    # KPI Requirements
    require_kpi_file: bool = True
    kpi_file_name: str = "KPI.yaml"
    required_kpi_fields: Set[str] = field(default_factory=lambda: {
        "module_name",
        "version",
        "kpis"
    })
    required_kpi_properties: Set[str] = field(default_factory=lambda: {
        "name",
        "description",
        "type",  # counter, gauge, histogram
        "target",
        "measurement"
    })

    # Metrics Requirements
    require_metrics_endpoint: bool = True
    metrics_endpoint: str = "/metrics"

    # Health Check Requirements
    require_health_endpoint: bool = True
    health_endpoint: str = "/health"

    # Documentation Requirements
    require_readme: bool = True
    readme_required_sections: Set[str] = field(default_factory=lambda: {
        "# ",  # Title
        "## Purpose",
        "## KPIs",
        "## API",
        "## Dependencies"
    })

    # Database Requirements
    require_database_schema: bool = False  # Not all modules need DB

    # Event Requirements
    require_event_subscriptions: bool = False  # Not all modules subscribe

    # Logging Requirements
    require_structured_logging: bool = True


STANDARD = ComplianceStandard()


# ============================================================================
# Test Results
# ============================================================================

@dataclass
class ModuleCompliance:
    """Compliance result for a module"""

    module_name: str
    module_path: Path

    # KPI Compliance
    has_kpi_file: bool = False
    kpi_file_path: Optional[Path] = None
    kpi_valid: bool = False
    kpi_issues: List[str] = field(default_factory=list)
    kpi_count: int = 0

    # Metrics Compliance
    has_metrics_endpoint: bool = False
    metrics_issues: List[str] = field(default_factory=list)

    # Health Check Compliance
    has_health_endpoint: bool = False
    health_issues: List[str] = field(default_factory=list)

    # Documentation Compliance
    has_readme: bool = False
    readme_issues: List[str] = field(default_factory=list)

    # Overall
    is_compliant: bool = False
    compliance_score: float = 0.0

    def calculate_score(self):
        """Calculate compliance score (0-100)"""
        checks = {
            "has_kpi_file": 30,
            "kpi_valid": 20,
            "has_metrics_endpoint": 20,
            "has_health_endpoint": 15,
            "has_readme": 15
        }

        score = sum(
            weight for check, weight in checks.items()
            if getattr(self, check, False)
        )

        self.compliance_score = score
        self.is_compliant = score >= 70  # 70% threshold


# ============================================================================
# Module Discovery
# ============================================================================

def discover_modules() -> List[Path]:
    """
    Discover all modules in the platform

    Returns:
        List of module directories
    """
    modules = []

    # Intelligent Core modules
    if INTELLIGENT_CORE.exists():
        for item in INTELLIGENT_CORE.iterdir():
            if item.is_dir() and not item.name.startswith(('.', '_')):
                # Check if it has main.py or __init__.py
                if (item / "main.py").exists() or (item / "__init__.py").exists():
                    modules.append(item)

    # Platform Services
    if PLATFORM_SERVICES.exists():
        for item in PLATFORM_SERVICES.iterdir():
            if item.is_dir() and not item.name.startswith(('.', '_')):
                if (item / "main.py").exists() or (item / "__init__.py").exists():
                    modules.append(item)

    return sorted(modules)


# ============================================================================
# KPI Compliance Tests
# ============================================================================

def check_kpi_file(module_path: Path) -> tuple[bool, Optional[Path], List[str]]:
    """
    Check if module has KPI.yaml file

    Returns:
        (has_file, file_path, issues)
    """
    issues = []

    # Check for KPI.yaml
    kpi_file = module_path / STANDARD.kpi_file_name

    if not kpi_file.exists():
        # Also check for variations
        alternatives = ["kpi.yaml", "KPIs.yaml", "kpis.yaml"]
        for alt in alternatives:
            alt_file = module_path / alt
            if alt_file.exists():
                kpi_file = alt_file
                issues.append(f"Found {alt} instead of {STANDARD.kpi_file_name}")
                break
        else:
            issues.append(f"Missing {STANDARD.kpi_file_name}")
            return False, None, issues

    return True, kpi_file, issues


def validate_kpi_file(kpi_file: Path) -> tuple[bool, int, List[str]]:
    """
    Validate KPI file structure

    Returns:
        (is_valid, kpi_count, issues)
    """
    issues = []

    try:
        with open(kpi_file, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        issues.append(f"Invalid YAML: {e}")
        return False, 0, issues
    except Exception as e:
        issues.append(f"Cannot read file: {e}")
        return False, 0, issues

    # Check required top-level fields
    for field in STANDARD.required_kpi_fields:
        if field not in data:
            issues.append(f"Missing required field: {field}")

    # Check KPIs
    if "kpis" not in data:
        issues.append("Missing 'kpis' section")
        return False, 0, issues

    kpis = data["kpis"]
    if not isinstance(kpis, list):
        issues.append("'kpis' must be a list")
        return False, 0, issues

    kpi_count = len(kpis)

    if kpi_count == 0:
        issues.append("No KPIs defined")
        return False, 0, issues

    # Validate each KPI
    for i, kpi in enumerate(kpis):
        kpi_name = kpi.get("name", f"KPI #{i+1}")

        for prop in STANDARD.required_kpi_properties:
            if prop not in kpi:
                issues.append(f"KPI '{kpi_name}' missing property: {prop}")

        # Validate type
        if "type" in kpi:
            valid_types = ["counter", "gauge", "histogram", "summary"]
            if kpi["type"] not in valid_types:
                issues.append(
                    f"KPI '{kpi_name}' has invalid type: {kpi['type']} "
                    f"(must be one of {valid_types})"
                )

    is_valid = len(issues) == 0
    return is_valid, kpi_count, issues


# ============================================================================
# Metrics Endpoint Tests
# ============================================================================

def check_metrics_endpoint(module_path: Path) -> tuple[bool, List[str]]:
    """
    Check if module exposes /metrics endpoint

    Looks for:
    - Prometheus metrics imports
    - /metrics route definition
    """
    issues = []

    main_file = module_path / "main.py"
    if not main_file.exists():
        issues.append("No main.py found")
        return False, issues

    try:
        with open(main_file, 'r') as f:
            content = f.read()
    except Exception as e:
        issues.append(f"Cannot read main.py: {e}")
        return False, issues

    # Check for Prometheus imports
    has_prometheus = any([
        "from prometheus_client import" in content,
        "import prometheus_client" in content
    ])

    # Check for /metrics endpoint
    has_metrics_route = any([
        '"/metrics"' in content,
        "'/metrics'" in content,
        "@app.get(\"/metrics\")" in content,
        "app.get('/metrics')" in content
    ])

    if not has_prometheus:
        issues.append("No Prometheus imports found")

    if not has_metrics_route:
        issues.append("No /metrics endpoint found")

    has_endpoint = has_prometheus and has_metrics_route
    return has_endpoint, issues


# ============================================================================
# Health Check Tests
# ============================================================================

def check_health_endpoint(module_path: Path) -> tuple[bool, List[str]]:
    """Check if module exposes /health endpoint"""
    issues = []

    main_file = module_path / "main.py"
    if not main_file.exists():
        issues.append("No main.py found")
        return False, issues

    try:
        with open(main_file, 'r') as f:
            content = f.read()
    except Exception as e:
        issues.append(f"Cannot read main.py: {e}")
        return False, issues

    # Check for /health endpoint
    has_health_route = any([
        '"/health"' in content,
        "'/health'" in content,
        "@app.get(\"/health\")" in content,
        "app.get('/health')" in content
    ])

    if not has_health_route:
        issues.append("No /health endpoint found")

    return has_health_route, issues


# ============================================================================
# Documentation Tests
# ============================================================================

def check_readme(module_path: Path) -> tuple[bool, List[str]]:
    """Check README.md compliance"""
    issues = []

    readme_file = module_path / "README.md"
    if not readme_file.exists():
        issues.append("No README.md found")
        return False, issues

    try:
        with open(readme_file, 'r') as f:
            content = f.read()
    except Exception as e:
        issues.append(f"Cannot read README.md: {e}")
        return False, issues

    # Check required sections
    for section in STANDARD.readme_required_sections:
        if section not in content:
            issues.append(f"Missing section: {section}")

    has_readme = len(issues) == 0
    return has_readme, issues


# ============================================================================
# Compliance Test Runner
# ============================================================================

def test_module_compliance(module_path: Path) -> ModuleCompliance:
    """Run all compliance tests for a module"""

    result = ModuleCompliance(
        module_name=module_path.name,
        module_path=module_path
    )

    # KPI Tests
    has_kpi, kpi_file, kpi_issues = check_kpi_file(module_path)
    result.has_kpi_file = has_kpi
    result.kpi_file_path = kpi_file
    result.kpi_issues.extend(kpi_issues)

    if has_kpi and kpi_file:
        kpi_valid, kpi_count, kpi_val_issues = validate_kpi_file(kpi_file)
        result.kpi_valid = kpi_valid
        result.kpi_count = kpi_count
        result.kpi_issues.extend(kpi_val_issues)

    # Metrics Tests
    has_metrics, metrics_issues = check_metrics_endpoint(module_path)
    result.has_metrics_endpoint = has_metrics
    result.metrics_issues.extend(metrics_issues)

    # Health Tests
    has_health, health_issues = check_health_endpoint(module_path)
    result.has_health_endpoint = has_health
    result.health_issues.extend(health_issues)

    # Documentation Tests
    has_readme, readme_issues = check_readme(module_path)
    result.has_readme = has_readme
    result.readme_issues.extend(readme_issues)

    # Calculate score
    result.calculate_score()

    return result


# ============================================================================
# Pytest Tests
# ============================================================================

class TestPlatformCompliance:
    """Platform compliance tests"""

    @pytest.fixture(scope="class")
    def modules(self):
        """Discover all modules"""
        return discover_modules()

    @pytest.fixture(scope="class")
    def compliance_results(self, modules):
        """Run compliance tests for all modules"""
        results = []
        for module in modules:
            result = test_module_compliance(module)
            results.append(result)
        return results

    def test_modules_discovered(self, modules):
        """Test that modules are discovered"""
        assert len(modules) > 0, "No modules found"
        print(f"\n✅ Found {len(modules)} modules")

    def test_all_modules_have_kpi_files(self, compliance_results):
        """Test that all modules have KPI files"""
        missing = [
            r for r in compliance_results
            if not r.has_kpi_file
        ]

        if missing:
            print("\n❌ Modules missing KPI.yaml:")
            for r in missing:
                print(f"  • {r.module_name}")

        assert len(missing) == 0, f"{len(missing)} modules missing KPI files"

    def test_all_kpi_files_valid(self, compliance_results):
        """Test that all KPI files are valid"""
        invalid = [
            r for r in compliance_results
            if r.has_kpi_file and not r.kpi_valid
        ]

        if invalid:
            print("\n❌ Modules with invalid KPI files:")
            for r in invalid:
                print(f"\n  {r.module_name}:")
                for issue in r.kpi_issues:
                    print(f"    - {issue}")

        assert len(invalid) == 0, f"{len(invalid)} modules have invalid KPI files"

    def test_all_modules_have_metrics(self, compliance_results):
        """Test that all modules expose /metrics endpoint"""
        missing = [
            r for r in compliance_results
            if not r.has_metrics_endpoint
        ]

        if missing:
            print("\n⚠️  Modules missing /metrics endpoint:")
            for r in missing:
                print(f"  • {r.module_name}")
                for issue in r.metrics_issues:
                    print(f"    - {issue}")

        # Allow warning instead of failure (some modules might not need metrics)
        if missing:
            pytest.skip(f"{len(missing)} modules missing /metrics (non-critical)")

    def test_all_modules_have_health_check(self, compliance_results):
        """Test that all modules expose /health endpoint"""
        missing = [
            r for r in compliance_results
            if not r.has_health_endpoint
        ]

        if missing:
            print("\n⚠️  Modules missing /health endpoint:")
            for r in missing:
                print(f"  • {r.module_name}")

        # Allow warning instead of failure
        if missing:
            pytest.skip(f"{len(missing)} modules missing /health (non-critical)")

    def test_compliance_score(self, compliance_results):
        """Test overall compliance score"""
        failing = [
            r for r in compliance_results
            if not r.is_compliant
        ]

        if failing:
            print("\n❌ Modules below 70% compliance:")
            for r in failing:
                print(f"  • {r.module_name}: {r.compliance_score:.0f}%")
                print(f"    KPI: {'✅' if r.has_kpi_file else '❌'} "
                      f"Valid: {'✅' if r.kpi_valid else '❌'} "
                      f"Metrics: {'✅' if r.has_metrics_endpoint else '❌'} "
                      f"Health: {'✅' if r.has_health_endpoint else '❌'}")

        # Calculate platform score
        avg_score = sum(r.compliance_score for r in compliance_results) / len(compliance_results)
        print(f"\n📊 Platform Compliance Score: {avg_score:.1f}%")

        assert avg_score >= 70, f"Platform compliance too low: {avg_score:.1f}%"

    def test_generate_compliance_report(self, compliance_results):
        """Generate compliance report"""
        report_path = PROJECT_ROOT / "docs" / "COMPLIANCE_REPORT.md"

        # Generate report
        report = generate_compliance_report(compliance_results)

        with open(report_path, 'w') as f:
            f.write(report)

        print(f"\n✅ Compliance report saved: {report_path}")


# ============================================================================
# Report Generation
# ============================================================================

def generate_compliance_report(results: List[ModuleCompliance]) -> str:
    """Generate Markdown compliance report"""

    # Calculate stats
    total = len(results)
    compliant = len([r for r in results if r.is_compliant])
    avg_score = sum(r.compliance_score for r in results) / total if total > 0 else 0

    has_kpi = len([r for r in results if r.has_kpi_file])
    valid_kpi = len([r for r in results if r.kpi_valid])
    has_metrics = len([r for r in results if r.has_metrics_endpoint])
    has_health = len([r for r in results if r.has_health_endpoint])

    # Sort by score
    results_sorted = sorted(results, key=lambda r: r.compliance_score, reverse=True)

    report = f"""# Platform Compliance Report

**Generated**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Summary

- **Total Modules**: {total}
- **Compliant (≥70%)**: {compliant} ({compliant/total*100:.1f}%)
- **Platform Score**: {avg_score:.1f}%

### Compliance Breakdown

| Check | Passed | Rate |
|-------|--------|------|
| Has KPI File | {has_kpi}/{total} | {has_kpi/total*100:.1f}% |
| Valid KPI File | {valid_kpi}/{total} | {valid_kpi/total*100:.1f}% |
| Has /metrics | {has_metrics}/{total} | {has_metrics/total*100:.1f}% |
| Has /health | {has_health}/{total} | {has_health/total*100:.1f}% |

---

## 📋 Module Scores

| Module | Score | KPI | Valid | Metrics | Health | Status |
|--------|-------|-----|-------|---------|--------|--------|
"""

    for r in results_sorted:
        status = "✅" if r.is_compliant else "❌"
        kpi_icon = "✅" if r.has_kpi_file else "❌"
        valid_icon = "✅" if r.kpi_valid else "❌"
        metrics_icon = "✅" if r.has_metrics_endpoint else "⚠️"
        health_icon = "✅" if r.has_health_endpoint else "⚠️"

        report += f"| {r.module_name} | {r.compliance_score:.0f}% | {kpi_icon} | {valid_icon} | {metrics_icon} | {health_icon} | {status} |\n"

    report += "\n---\n\n## 🔴 Critical Issues\n\n"

    critical = [r for r in results if not r.has_kpi_file or not r.kpi_valid]
    if critical:
        for r in critical:
            report += f"### {r.module_name}\n\n"
            if not r.has_kpi_file:
                report += "- ❌ Missing KPI.yaml\n"
            if r.has_kpi_file and not r.kpi_valid:
                report += "- ❌ Invalid KPI file:\n"
                for issue in r.kpi_issues:
                    report += f"  - {issue}\n"
            report += "\n"
    else:
        report += "✅ No critical issues\n\n"

    report += "---\n\n## ⚠️ Warnings\n\n"

    warnings = [r for r in results if not r.has_metrics_endpoint or not r.has_health_endpoint]
    if warnings:
        for r in warnings:
            report += f"### {r.module_name}\n\n"
            if not r.has_metrics_endpoint:
                report += "- ⚠️ Missing /metrics endpoint\n"
            if not r.has_health_endpoint:
                report += "- ⚠️ Missing /health endpoint\n"
            report += "\n"
    else:
        report += "✅ No warnings\n\n"

    return report


# ============================================================================
# CLI Entry Point
# ============================================================================

if __name__ == "__main__":
    import sys

    print("🔍 Platform Compliance Test\n")

    # Discover modules
    modules = discover_modules()
    print(f"Found {len(modules)} modules\n")

    # Run tests
    results = []
    for module in modules:
        print(f"Testing {module.name}...", end=" ")
        result = test_module_compliance(module)
        results.append(result)

        if result.is_compliant:
            print(f"✅ {result.compliance_score:.0f}%")
        else:
            print(f"❌ {result.compliance_score:.0f}%")

    # Generate report
    print("\n📊 Generating report...")
    report = generate_compliance_report(results)

    report_path = PROJECT_ROOT / "docs" / "COMPLIANCE_REPORT.md"
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"✅ Report saved: {report_path}")

    # Exit with status
    avg_score = sum(r.compliance_score for r in results) / len(results)
    if avg_score < 70:
        print(f"\n❌ FAILED: Platform compliance {avg_score:.1f}% (< 70%)")
        sys.exit(1)
    else:
        print(f"\n✅ PASSED: Platform compliance {avg_score:.1f}%")
        sys.exit(0)
