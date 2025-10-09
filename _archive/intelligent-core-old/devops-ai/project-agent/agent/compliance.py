from __future__ import annotations
from pathlib import Path
import json
from .config import get_repo_path, get_reports_dir
from rich.console import Console

console = Console()

ISO_CLAUSES = [
    "Context of the organization",
    "Leadership & Policy",
    "Planning (BIA/Risk)",
    "Support (Docs/Training)",
    "Operation (Incident/Crisis)",
    "Performance evaluation (Audit/Monitoring)",
    "Improvement (PDCA/Corrective actions)"
]

RULES = {
    "Context of the organization": ["CONCEPT.md","TECH_SPEC.md"],
    "Leadership & Policy": ["policy","policies","docs/policies","governance"],
    "Planning (BIA/Risk)": ["BIA","risk","risk_service","risk_model"],
    "Support (Docs/Training)": ["docs/","Training","LMS","awareness"],
    "Operation (Incident/Crisis)": ["incident","crisis","thehive","playbook"],
    "Performance evaluation (Audit/Monitoring)": ["audit","evidence","dashboard","metrics"],
    "Improvement (PDCA/Corrective actions)": ["PDCA","roadmap","CHANGELOG.md"]
}

def run_iso_coverage():
    repo = get_repo_path()
    reports = get_reports_dir()
    coverage = {}
    for clause in ISO_CLAUSES:
        hints = RULES.get(clause, [])
        evidence = set()
        for hint in hints:
            for p in repo.rglob(f"*{hint}*"):
                evidence.add(p.as_posix())
        coverage[clause] = {"hints": hints, "evidence": sorted(evidence)}
    (reports/"iso_coverage.json").write_text(json.dumps(coverage, indent=2), encoding="utf-8")
    console.print(f"[green]ISO coverage written:[/green] {reports/'iso_coverage.json'}")
    return coverage
