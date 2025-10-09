"""
Auto-generate KPI.yaml files for all modules

Analyzes module code to infer appropriate KPIs based on:
- Module purpose (from README)
- Existing metrics (if any)
- Module type (service, library, intelligence)
- Common patterns

Usage:
    python scripts/generate_kpis.py --dry-run  # Preview only
    python scripts/generate_kpis.py            # Generate files
"""

import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import re


# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
INTELLIGENT_CORE = PROJECT_ROOT / "intelligent-core"
PLATFORM_SERVICES = PROJECT_ROOT / "platform-services"


# ============================================================================
# KPI Templates by Module Type
# ============================================================================

def get_service_kpis(module_name: str, module_type: str) -> List[Dict]:
    """Get KPIs for platform services"""

    base_kpis = [
        {
            "name": "request_count",
            "description": f"Total number of requests processed by {module_name}",
            "type": "counter",
            "target": "> 1000/day",
            "measurement": "Count of API requests",
            "prometheus_metric": f"{module_name.replace('-', '_')}_requests_total"
        },
        {
            "name": "response_time_p95",
            "description": "95th percentile response time",
            "type": "histogram",
            "target": "< 500ms",
            "measurement": "Response time in milliseconds",
            "prometheus_metric": f"{module_name.replace('-', '_')}_response_time_ms"
        },
        {
            "name": "error_rate",
            "description": "Percentage of failed requests",
            "type": "gauge",
            "target": "< 1%",
            "measurement": "errors / total_requests * 100",
            "prometheus_metric": f"{module_name.replace('-', '_')}_error_rate"
        },
        {
            "name": "availability",
            "description": "Service uptime percentage",
            "type": "gauge",
            "target": "> 99.5%",
            "measurement": "uptime / total_time * 100",
            "prometheus_metric": f"{module_name.replace('-', '_')}_availability"
        }
    ]

    # Add specific KPIs based on module type
    if "bia" in module_name:
        base_kpis.extend([
            {
                "name": "bia_completed",
                "description": "Number of BIA analyses completed",
                "type": "counter",
                "target": "> 50/month",
                "measurement": "Count of completed BIA workflows",
                "prometheus_metric": "bia_completed_total"
            },
            {
                "name": "process_coverage",
                "description": "Percentage of critical processes analyzed",
                "type": "gauge",
                "target": "> 95%",
                "measurement": "analyzed_processes / total_critical_processes * 100",
                "prometheus_metric": "bia_process_coverage"
            }
        ])

    elif "risk" in module_name:
        base_kpis.extend([
            {
                "name": "risks_identified",
                "description": "Number of risks identified and tracked",
                "type": "counter",
                "target": "> 100 active risks",
                "measurement": "Count of active risks in system",
                "prometheus_metric": "risks_identified_total"
            },
            {
                "name": "mitigation_rate",
                "description": "Percentage of risks with mitigation plans",
                "type": "gauge",
                "target": "> 90%",
                "measurement": "risks_with_mitigation / total_risks * 100",
                "prometheus_metric": "risk_mitigation_rate"
            }
        ])

    elif "compliance" in module_name:
        base_kpis.extend([
            {
                "name": "compliance_score",
                "description": "Overall ISO 22301 compliance score",
                "type": "gauge",
                "target": "> 85%",
                "measurement": "compliant_controls / total_controls * 100",
                "prometheus_metric": "compliance_score"
            },
            {
                "name": "audit_findings",
                "description": "Number of open audit findings",
                "type": "gauge",
                "target": "< 10",
                "measurement": "Count of unresolved audit findings",
                "prometheus_metric": "audit_findings_open"
            }
        ])

    elif "document" in module_name:
        base_kpis.extend([
            {
                "name": "documents_managed",
                "description": "Total documents under management",
                "type": "gauge",
                "target": "> 500",
                "measurement": "Count of active documents",
                "prometheus_metric": "documents_total"
            },
            {
                "name": "document_compliance",
                "description": "Percentage of documents up-to-date",
                "type": "gauge",
                "target": "> 95%",
                "measurement": "updated_documents / total_documents * 100",
                "prometheus_metric": "documents_compliance_rate"
            }
        ])

    return base_kpis


def get_intelligence_kpis(module_name: str) -> List[Dict]:
    """Get KPIs for intelligent core modules"""

    kpis = [
        {
            "name": "predictions_made",
            "description": f"Number of predictions/recommendations made by {module_name}",
            "type": "counter",
            "target": "> 100/day",
            "measurement": "Count of AI predictions",
            "prometheus_metric": f"{module_name.replace('-', '_')}_predictions_total"
        },
        {
            "name": "prediction_accuracy",
            "description": "Accuracy of AI predictions",
            "type": "gauge",
            "target": "> 85%",
            "measurement": "correct_predictions / total_predictions * 100",
            "prometheus_metric": f"{module_name.replace('-', '_')}_accuracy"
        },
        {
            "name": "processing_time",
            "description": "Time to generate prediction",
            "type": "histogram",
            "target": "< 2s",
            "measurement": "Time in seconds",
            "prometheus_metric": f"{module_name.replace('-', '_')}_processing_time_seconds"
        },
        {
            "name": "model_confidence",
            "description": "Average confidence score of predictions",
            "type": "gauge",
            "target": "> 0.8",
            "measurement": "avg(confidence_scores)",
            "prometheus_metric": f"{module_name.replace('-', '_')}_confidence"
        }
    ]

    # Module-specific KPIs
    if "workflow" in module_name:
        kpis.extend([
            {
                "name": "workflows_completed",
                "description": "Number of workflows successfully completed",
                "type": "counter",
                "target": "> 1000/month",
                "measurement": "Count of completed workflows",
                "prometheus_metric": "workflows_completed_total"
            },
            {
                "name": "workflow_success_rate",
                "description": "Percentage of workflows completed successfully",
                "type": "gauge",
                "target": "> 95%",
                "measurement": "successful_workflows / total_workflows * 100",
                "prometheus_metric": "workflow_success_rate"
            }
        ])

    elif "predictive" in module_name:
        kpis.extend([
            {
                "name": "forecast_accuracy",
                "description": "Accuracy of timeline forecasts",
                "type": "gauge",
                "target": "> 80%",
                "measurement": "accurate_forecasts / total_forecasts * 100",
                "prometheus_metric": "predictive_forecast_accuracy"
            }
        ])

    elif "community" in module_name or "collective" in module_name:
        kpis.extend([
            {
                "name": "case_contributions",
                "description": "Number of cases contributed to library",
                "type": "counter",
                "target": "> 50/month",
                "measurement": "Count of approved case contributions",
                "prometheus_metric": "case_contributions_total"
            },
            {
                "name": "k_anonymity_compliance",
                "description": "Percentage of patterns with k≥5 anonymity",
                "type": "gauge",
                "target": "100%",
                "measurement": "compliant_patterns / total_patterns * 100",
                "prometheus_metric": "k_anonymity_compliance_rate"
            }
        ])

    return kpis


def detect_module_type(module_path: Path) -> str:
    """Detect module type from path and code"""

    # Check path
    if "platform-services" in str(module_path):
        return "service"
    elif "intelligent-core" in str(module_path):
        return "intelligence"
    else:
        return "library"


def generate_kpi_file(module_path: Path, module_type: str) -> Dict:
    """Generate KPI.yaml content for module"""

    module_name = module_path.name

    # Get description from README if exists
    description = f"{module_name} module"
    readme_path = module_path / "README.md"
    if readme_path.exists():
        try:
            with open(readme_path, 'r') as f:
                content = f.read()
                # Extract first paragraph after title
                lines = [l for l in content.split('\n') if l.strip()]
                if len(lines) > 1:
                    description = lines[1].strip()
        except:
            pass

    # Generate KPIs based on type
    if module_type == "service":
        kpis = get_service_kpis(module_name, module_type)
    elif module_type == "intelligence":
        kpis = get_intelligence_kpis(module_name)
    else:
        # Default KPIs for libraries
        kpis = [
            {
                "name": "usage_count",
                "description": f"Number of times {module_name} is imported/used",
                "type": "counter",
                "target": "> 100/day",
                "measurement": "Import count across platform",
                "prometheus_metric": f"{module_name.replace('-', '_')}_usage_total"
            },
            {
                "name": "function_calls",
                "description": "Number of function calls",
                "type": "counter",
                "target": "> 1000/day",
                "measurement": "Count of function invocations",
                "prometheus_metric": f"{module_name.replace('-', '_')}_calls_total"
            },
            {
                "name": "error_rate",
                "description": "Error rate in module functions",
                "type": "gauge",
                "target": "< 0.1%",
                "measurement": "errors / total_calls * 100",
                "prometheus_metric": f"{module_name.replace('-', '_')}_error_rate"
            }
        ]

    # Build YAML structure
    kpi_data = {
        "module_name": module_name,
        "version": "1.0.0",
        "description": description,
        "module_type": module_type,
        "owner": "platform-team",
        "kpis": kpis,
        "monitoring": {
            "prometheus_enabled": True,
            "grafana_dashboard": f"dashboards/{module_name}.json",
            "alert_rules": f"alerts/{module_name}.yaml"
        },
        "targets": {
            "daily": "Track daily metrics",
            "weekly": "Review weekly trends",
            "monthly": "Monthly performance review"
        }
    }

    return kpi_data


def save_kpi_file(module_path: Path, kpi_data: Dict, dry_run: bool = False):
    """Save KPI.yaml file"""

    kpi_file = module_path / "KPI.yaml"

    if dry_run:
        print(f"\n{'='*60}")
        print(f"Would create: {kpi_file}")
        print(f"{'='*60}")
        print(yaml.dump(kpi_data, default_flow_style=False, sort_keys=False))
        return

    # Save file
    with open(kpi_file, 'w') as f:
        yaml.dump(kpi_data, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Created: {kpi_file}")


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate KPI.yaml files for all modules")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating files")
    parser.add_argument("--module", type=str, help="Generate for specific module only")
    args = parser.parse_args()

    print("🎯 KPI Auto-Generator\n")

    # Discover modules
    def discover_modules() -> List[Path]:
        modules = []
        if INTELLIGENT_CORE.exists():
            for item in INTELLIGENT_CORE.iterdir():
                if item.is_dir() and not item.name.startswith(('.', '_')):
                    if (item / "main.py").exists() or (item / "__init__.py").exists():
                        modules.append(item)
        if PLATFORM_SERVICES.exists():
            for item in PLATFORM_SERVICES.iterdir():
                if item.is_dir() and not item.name.startswith(('.', '_')):
                    if (item / "main.py").exists() or (item / "__init__.py").exists():
                        modules.append(item)
        return sorted(modules)

    modules = discover_modules()

    if args.module:
        modules = [m for m in modules if m.name == args.module]
        if not modules:
            print(f"❌ Module '{args.module}' not found")
            return

    print(f"Found {len(modules)} modules")

    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No files will be created\n")

    # Generate KPIs
    generated = 0
    for module_path in modules:
        # Check if KPI.yaml already exists
        kpi_file = module_path / "KPI.yaml"
        if kpi_file.exists() and not args.dry_run:
            print(f"⏭️  Skipping {module_path.name} (KPI.yaml exists)")
            continue

        # Detect module type
        module_type = detect_module_type(module_path)

        # Generate KPI data
        kpi_data = generate_kpi_file(module_path, module_type)

        # Save file
        save_kpi_file(module_path, kpi_data, dry_run=args.dry_run)
        generated += 1

    print(f"\n{'='*60}")
    if args.dry_run:
        print(f"✅ Would generate {generated} KPI files")
        print("Run without --dry-run to create files")
    else:
        print(f"✅ Generated {generated} KPI files")
        print("\n🎯 Next steps:")
        print("1. Review generated KPI.yaml files")
        print("2. Adjust targets based on business requirements")
        print("3. Implement Prometheus metrics in code")
        print("4. Run: pytest tests/platform_compliance_test.py")


if __name__ == "__main__":
    main()
