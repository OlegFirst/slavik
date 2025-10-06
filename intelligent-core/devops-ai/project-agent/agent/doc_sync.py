from __future__ import annotations
from pathlib import Path
import re, json
from .config import get_repo_path, get_reports_dir
from rich.console import Console

console = Console()

FEATURE_KEYS = [
    "PDCA","Compliance Officer","Crisis room","FAIR","Monte Carlo",
    "Risk Analytics","BIA","Incident","Training","Audit","Evidence",
    "Policy","Templates","Keycloak","Vault","EventBus","Orchestrator",
    "SharePoint","M365","GRC","Dashboard","Benchmarking"
]

CODE_HINTS = {
    "Crisis room": ["crisis","warroom","bridge","incident_room"],
    "Risk Analytics": ["risk","analytics","risk_service","risk_model"],
    "BIA": ["bia","business_impact"],
    "Incident": ["incident","thehive","alert"],
    "Policy": ["policy","document","doc_service"],
    "Training": ["lms","training","course"],
    "Audit": ["audit","evidence","compliance"],
    "EventBus": ["eventbus","broker","kafka","redis"],
    "Orchestrator": ["orchestrator","workflow","bpmn"],
}

def _read(path: Path)->str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def extract_features(text: str):
    found = set()
    for k in FEATURE_KEYS:
        if re.search(re.escape(k), text, re.IGNORECASE):
            found.add(k)
    return sorted(found)

def check_consistency():
    repo = get_repo_path()
    reports = get_reports_dir()
    text = _read(repo/"ROADMAP.md") + "\n" + _read(repo/"TECH_SPEC.md") + "\n" + _read(repo/"CONCEPT.md")
    declared = extract_features(text)

    implemented = []
    missing = []
    for feat in declared:
        hints = CODE_HINTS.get(feat, [feat.lower()])
        matched = False
        for hint in hints:
            if list(repo.rglob(f"*{hint}*")):
                matched = True
                break
        (implemented if matched else missing).append(feat)

    res = {"declared_features": declared, "implemented_features": implemented, "missing_features": missing}
    (reports/"consistency.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    console.print(f"[yellow]Consistency check written:[/yellow] {reports/'consistency.json'}")
    return res
