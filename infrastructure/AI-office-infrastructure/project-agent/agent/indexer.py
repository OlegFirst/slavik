from __future__ import annotations
import os, json
from pathlib import Path
from typing import Dict, List, Any
from rich.console import Console
from .config import get_repo_path, get_reports_dir

console = Console()

def run():
    # Placeholder: assume Sprint 1 indexer present in repo; keep compatibility
    reports_dir = get_reports_dir()
    if not (reports_dir/"deps_ast.json").exists():
        (reports_dir/"deps_ast.json").write_text(json.dumps({"nodes":[],"edges":[],"metrics":{}}, indent=2), encoding="utf-8")
        console.print("[yellow]deps_ast.json placeholder written (Sprint 1 indexer not found).[/yellow]")
    if not (reports_dir/"inventory.json").exists():
        (reports_dir/"inventory.json").write_text(json.dumps({"total_files":0,"code_files":0,"docs_files":0,"by_module":{}}, indent=2), encoding="utf-8")
        console.print("[yellow]inventory.json placeholder written.[/yellow]")
    console.print("[green]Index step completed (compat mode).[/green]")
