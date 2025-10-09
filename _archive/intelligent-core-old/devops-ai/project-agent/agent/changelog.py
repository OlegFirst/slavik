from __future__ import annotations
from pathlib import Path
from datetime import datetime, timedelta
from git import Repo
from .config import get_repo_path, get_reports_dir
from rich.console import Console
console = Console()

def generate_changelog(days:int=7):
    repo_path = get_repo_path()
    reports = get_reports_dir()
    repo = Repo(str(repo_path))
    since = datetime.now() - timedelta(days=days)
    lines = [f"# Change Log (last {days} days)\n"]
    for commit in repo.iter_commits("HEAD", since=since.isoformat()):
        dt = datetime.fromtimestamp(commit.committed_date).isoformat(timespec="seconds")
        lines.append(f"- {dt} {commit.hexsha[:7]} — {commit.summary} ({commit.author.name})")
    path = reports / "CHANGELOG.generated.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"[cyan]Generated changelog:[/cyan] {path}")
    return str(path)
