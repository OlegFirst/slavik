import os
import yaml
from pathlib import Path
from typing import Dict, Any

def get_repo_path() -> Path:
    p = os.environ.get("REPO_PATH", os.getcwd())
    return Path(p).resolve()

def get_reports_dir() -> Path:
    d = os.environ.get("REPORTS_DIR", str(get_repo_path() / "docs" / "reports"))
    Path(d).mkdir(parents=True, exist_ok=True)
    return Path(d)

def get_config_path() -> Path:
    """Возвращает путь к конфигурационному файлу"""
    return get_repo_path() / ".project-agent.yml"

def load_config() -> Dict[str, Any]:
    """Загружает конфигурацию из .project-agent.yml или возвращает дефолт"""
    config_file = get_config_path()

    if not config_file.exists():
        return get_default_config()

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        return config
    except Exception as e:
        print(f"Warning: Failed to load config: {e}")
        return get_default_config()

def save_config(config: Dict[str, Any]) -> None:
    """Сохраняет конфигурацию в .project-agent.yml"""
    config_file = get_config_path()

    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    except Exception as e:
        print(f"Error: Failed to save config: {e}")

def get_default_config() -> Dict[str, Any]:
    """Возвращает дефолтную конфигурацию"""
    return {
        "domain": "auto",  # auto-detect или конкретный: iso22301, security, fintech, healthcare
        "modules": {
            "security": {
                "enabled": True,
                "checks": ["secrets", "vulnerabilities", "dependencies"]
            },
            "testing": {
                "enabled": True,
                "coverage_threshold": 70,
                "frameworks": ["pytest", "jest", "go-test"]
            },
            "quality": {
                "enabled": True,
                "checks": ["complexity", "duplication", "tech-debt"]
            },
            "compliance": {
                "enabled": True,
                "standards": ["ISO22301"]
            }
        },
        "reports": {
            "formats": ["markdown", "html"],
            "audiences": ["dev", "business"]
        },
        "integrations": {
            "thehive": {
                "enabled": False,
                "url": "",
                "api_key": ""
            },
            "m365": {
                "enabled": False,
                "tenant_id": "",
                "client_id": "",
                "client_secret": ""
            }
        }
    }
