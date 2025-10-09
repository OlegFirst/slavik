import click
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from . import indexer, doc_sync, compliance, changelog, report, bpmn_yaml
from .config import load_config, save_config, get_config_path, get_repo_path
from .domain_detector import detect_domain, get_domain_config
from .modules.security import run_security_checks
from .modules.testing import run_testing_checks
from .modules.quality import run_quality_checks

console = Console()

@click.group()
def main():
    """Project Agent — Universal CLI for project analysis"""

@main.command("init")
@click.option("--domain", default="auto", help="Project domain: auto, iso22301, security, fintech, healthcare, ecommerce")
@click.option("--force", is_flag=True, help="Overwrite existing config")
def init_cmd(domain, force):
    """Initialize Project Agent configuration"""
    config_path = get_config_path()

    if config_path.exists() and not force:
        console.print(f"[yellow]Config already exists:[/yellow] {config_path}")
        console.print("Use --force to overwrite")
        return

    # Auto-detect domain if requested
    if domain == "auto":
        console.print("[cyan]Detecting project domain...[/cyan]")
        detection = detect_domain(get_repo_path())

        console.print(f"\n[green]Detection results:[/green]")
        console.print(f"  Primary domain: [bold]{detection['primary']}[/bold] (confidence: {detection['confidence']*100:.0f}%)")
        if detection['secondary']:
            console.print(f"  Secondary: {', '.join(detection['secondary'])}")

        domain = detection['primary']

    # Get recommended config for domain
    config = get_domain_config(domain)
    config["domain"] = domain

    # Save config
    save_config(config)

    console.print(f"\n[green]✓[/green] Configuration created: {config_path}")
    console.print(f"[green]✓[/green] Domain: [bold]{domain}[/bold]")
    console.print("\nNext steps:")
    console.print("  1. Review and edit config: .project-agent.yml")
    console.print("  2. Run analysis: project-agent scan")

@main.command("scan")
@click.option("--module", multiple=True, help="Run specific module(s): security, testing, quality, compliance")
def scan_cmd(module):
    """Run all enabled analysis modules"""
    config = load_config()
    modules_config = config.get("modules", {})

    # Определяем какие модули запускать
    if module:
        modules_to_run = list(module)
    else:
        modules_to_run = [m for m, cfg in modules_config.items() if cfg.get("enabled", False)]

    console.print(f"[cyan]Running modules:[/cyan] {', '.join(modules_to_run)}\n")

    results = {}

    # Security
    if "security" in modules_to_run:
        console.print("[cyan]→ Running security checks...[/cyan]")
        try:
            results["security"] = run_security_checks(config)
            status = results["security"]["summary"]["status"]
            color = "green" if status == "OK" else "red"
            console.print(f"[{color}]✓ Security: {status}[/{color}]\n")
        except Exception as e:
            console.print(f"[red]✗ Security failed: {e}[/red]\n")

    # Testing
    if "testing" in modules_to_run:
        console.print("[cyan]→ Running testing analysis...[/cyan]")
        try:
            results["testing"] = run_testing_checks(config)
            status = results["testing"]["summary"]["status"]
            coverage = results["testing"]["summary"]["average_coverage"]
            color = "green" if status == "OK" else "yellow"
            console.print(f"[{color}]✓ Testing: {status} (coverage: {coverage}%)[/{color}]\n")
        except Exception as e:
            console.print(f"[red]✗ Testing failed: {e}[/red]\n")

    # Quality
    if "quality" in modules_to_run:
        console.print("[cyan]→ Running quality analysis...[/cyan]")
        try:
            results["quality"] = run_quality_checks(config)
            console.print(f"[green]✓ Quality: OK[/green]\n")
        except Exception as e:
            console.print(f"[red]✗ Quality failed: {e}[/red]\n")

    # Compliance (ISO)
    if "compliance" in modules_to_run:
        console.print("[cyan]→ Running compliance checks...[/cyan]")
        try:
            compliance.run_iso_coverage()
            console.print(f"[green]✓ Compliance: OK[/green]\n")
        except Exception as e:
            console.print(f"[red]✗ Compliance failed: {e}[/red]\n")

    console.print("[green]Scan complete! Reports saved to docs/reports/[/green]")

@main.command("status")
def status_cmd():
    """Show project agent status and config"""
    config = load_config()

    # Domain info
    domain = config.get("domain", "unknown")
    console.print(Panel(f"[bold]Domain:[/bold] {domain}", title="Project Agent Status"))

    # Modules table
    table = Table(title="Enabled Modules")
    table.add_column("Module", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Config")

    modules = config.get("modules", {})
    for module_name, module_config in modules.items():
        enabled = module_config.get("enabled", False)
        status = "✓ Enabled" if enabled else "✗ Disabled"
        config_str = json.dumps(module_config, indent=None)[:60]
        table.add_row(module_name, status, config_str)

    console.print(table)

@main.command("index")
def index_cmd():
    """Index repository code and dependencies"""
    indexer.run()

@main.command("processmap")
def processmap_cmd():
    """Parse BPMN/YAML/JSON and build process_map.json"""
    bpmn_yaml.build_process_map()

@main.command("consistency")
def consistency_cmd():
    """Check documentation and code consistency"""
    doc_sync.check_consistency()

@main.command("iso")
def iso_cmd():
    """Run ISO 22301 compliance check"""
    compliance.run_iso_coverage()

@main.command("changelog")
@click.option("--days", default=7, help="Days back")
def changelog_cmd(days):
    """Generate changelog from git history"""
    changelog.generate_changelog(days=days)

@main.command("report")
@click.option("--weekly", is_flag=True, help="Produce donor summary")
def report_cmd(weekly):
    """Generate project reports"""
    # ensure maps exist
    try:
        bpmn_yaml.build_process_map()
    except Exception as e:
        console.print(f"[yellow]process_map skipped:[/yellow] {e}")
    report.build_daily_report()
    if weekly:
        report.build_donor_summary()
    console.print("[green]Reports generated.[/green]")
