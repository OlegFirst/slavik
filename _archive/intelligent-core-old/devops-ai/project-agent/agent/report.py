from __future__ import annotations
from pathlib import Path
import json, datetime as dt
from .config import get_repo_path, get_reports_dir

def _read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

def _write(p: Path, text: str):
    p.write_text(text, encoding="utf-8")

def _count_commits(repo_path: Path, days: int=1)->int:
    try:
        from git import Repo
        repo = Repo(str(repo_path))
        since = dt.datetime.now() - dt.timedelta(days=days)
        return sum(1 for _ in repo.iter_commits("HEAD", since=since.isoformat()))
    except Exception:
        return 0

def build_daily_report():
    repo = get_repo_path()
    out = get_reports_dir()
    inv = _read_json(out/"inventory.json")
    astmap = _read_json(out/"deps_ast.json")
    pmap = _read_json(out/"process_map.json")
    iso = _read_json(out/"iso_coverage.json")
    commits = _count_commits(repo, 1)

    lines = []
    lines.append("# Daily Technical Report")
    lines.append("")
    lines.append("## Inventory")
    lines.append(f"- Total files: **{inv.get('total_files',0)}**, Code: **{inv.get('code_files',0)}**, Docs: **{inv.get('docs_files',0)}**")
    lines.append("")
    # AST metrics
    if astmap:
        lines.append("## AST Dependency Metrics (Top)")
        for label, items in astmap.get("metrics", {}).items():
            lines.append(f"- {label}: " + ", ".join(f"{k}:{v}" for k,v in items))
        lines.append("")
    # Process map summary
    bpmn = pmap.get("bpmn", []) if pmap else []
    yamlj = pmap.get("yaml_json", []) if pmap else []
    total_tasks = sum(len(pr.get("tasks", [])) for f in bpmn for pr in f.get("processes", []))
    linked_tasks = 0
    for f in bpmn:
        for pr in f.get("processes", []):
            for t in pr.get("tasks", []):
                if t.get("code_refs"):
                    linked_tasks += 1
    lines.append("## BPMN / YAML Artifacts")
    lines.append(f"- BPMN files: **{len(bpmn)}**, YAML/JSON files: **{len(yamlj)}**")
    lines.append(f"- Tasks total: **{total_tasks}**, linked to code: **{linked_tasks}**")
    lines.append("")
    # ISO sample
    lines.append("## ISO 22301 Artifacts (sample)")
    for clause, data in list(iso.items())[:4]:
        ev = data.get("evidence", [])[:3]
        lines.append(f"- {clause}: {', '.join(ev) if ev else '—'}")
    lines.append("")
    lines.append("## CI / Commits")
    lines.append(f"- Commits (24h): **{commits}**")
    _write(out/"daily_report.md", "\n".join(lines))

def build_donor_summary():
    out = get_reports_dir()
    pmap = _read_json(out/"process_map.json")
    iso = _read_json(out/"iso_coverage.json")

    bpmn = pmap.get("bpmn", []) if pmap else []
    yamlj = pmap.get("yaml_json", []) if pmap else []
    total_processes = sum(len(f.get("processes", [])) for f in bpmn)
    total_tasks = sum(len(pr.get("tasks", [])) for f in bpmn for pr in f.get("processes", []))

    lines = []
    lines.append("# Weekly Progress (Non‑Technical)")
    lines.append("**Что сделали:** связали бизнес‑процессы (BPMN) и конфиги (YAML/JSON) с кодовой базой.**")
    lines.append(f"- Обнаружено процессов: **{total_processes}**, задач: **{total_tasks}**.")
    lines.append(f"- Файлов BPMN: **{len(bpmn)}**, YAML/JSON: **{len(yamlj)}**.")
    lines.append("")
    lines.append("**Зачем это нужно:** это даёт проверяемую трассируемость между планом/регламентом и реализацией в коде (важно для аудита и ISO 22301).")
    lines.append("")
    lines.append("**Дальше:** heatmap Annex SL, адаптеры TheHive/M365, auto‑evidence в отчётах.")
    _write(out/"donor_summary.md", "\n".join(lines))
