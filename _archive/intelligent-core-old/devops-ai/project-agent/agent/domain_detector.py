"""Domain Detector — автоматическое определение тематики проекта"""
from __future__ import annotations
import re
from pathlib import Path
from collections import Counter
from typing import Dict, List

# Домены и их индикаторы (keywords в коде, доках, зависимостях)
DOMAIN_SIGNATURES = {
    "iso22301": {
        "keywords": ["bcm", "business continuity", "iso22301", "iso 22301", "incident",
                    "disaster recovery", "crisis", "bcp", "pdca", "bia"],
        "files": ["bcp", "bcm", "incident", "recovery", "continuity"],
        "packages": ["iso22301", "bcm"]
    },
    "security": {
        "keywords": ["security", "vulnerability", "pentest", "owasp", "cve", "exploit",
                    "encryption", "authentication", "authorization", "xss", "sql injection"],
        "files": ["security", "vuln", "exploit", "auth", "crypto"],
        "packages": ["security", "cryptography", "pyjwt", "bcrypt", "owasp"]
    },
    "fintech": {
        "keywords": ["payment", "transaction", "pci-dss", "stripe", "banking", "invoice",
                    "ledger", "wallet", "cryptocurrency", "blockchain"],
        "files": ["payment", "transaction", "invoice", "ledger", "billing"],
        "packages": ["stripe", "plaid", "dwolla", "payment"]
    },
    "healthcare": {
        "keywords": ["patient", "medical", "hipaa", "ehr", "phi", "diagnosis", "clinical",
                    "healthcare", "hospital", "doctor"],
        "files": ["patient", "medical", "clinical", "diagnosis"],
        "packages": ["fhir", "hl7", "healthcare"]
    },
    "ecommerce": {
        "keywords": ["cart", "checkout", "product", "order", "shipping", "inventory",
                    "ecommerce", "e-commerce", "shop", "store"],
        "files": ["cart", "product", "order", "shipping", "inventory"],
        "packages": ["shopify", "woocommerce", "magento"]
    },
    "saas": {
        "keywords": ["subscription", "billing", "tenant", "multi-tenant", "saas",
                    "workspace", "organization", "plan", "tier"],
        "files": ["subscription", "tenant", "workspace", "billing"],
        "packages": ["stripe", "chargebee"]
    }
}

def detect_domain(repo_path: Path) -> Dict[str, any]:
    """
    Анализирует проект и определяет домен(ы)

    Returns:
        {
            "primary": "iso22301",
            "secondary": ["security"],
            "scores": {"iso22301": 45, "security": 12, ...},
            "confidence": 0.85
        }
    """
    scores = Counter()

    # 1. Сканируем файлы в проекте
    file_matches = _scan_files(repo_path, scores)

    # 2. Сканируем содержимое документации
    doc_matches = _scan_docs(repo_path, scores)

    # 3. Сканируем зависимости (requirements.txt, package.json, go.mod)
    dep_matches = _scan_dependencies(repo_path, scores)

    # Считаем итоговые scores
    total = sum(scores.values())
    if total == 0:
        return {
            "primary": "unknown",
            "secondary": [],
            "scores": {},
            "confidence": 0.0
        }

    # Нормализуем scores к процентам
    normalized = {k: (v/total)*100 for k, v in scores.most_common()}

    # Определяем primary (самый высокий score > 30%)
    top = scores.most_common(1)[0]
    primary = top[0] if top[1]/total > 0.3 else "unknown"

    # Secondary домены (score > 15%)
    secondary = [k for k, v in scores.most_common()[1:4] if v/total > 0.15]

    confidence = min(1.0, (top[1]/total) * 2)  # max confidence при 50%+ score

    return {
        "primary": primary,
        "secondary": secondary,
        "scores": normalized,
        "confidence": round(confidence, 2),
        "details": {
            "file_matches": file_matches,
            "doc_matches": doc_matches,
            "dep_matches": dep_matches
        }
    }

def _scan_files(repo_path: Path, scores: Counter) -> Dict[str, int]:
    """Сканирует имена файлов на совпадение с индикаторами доменов"""
    matches = {}

    for domain, sig in DOMAIN_SIGNATURES.items():
        count = 0
        for pattern in sig["files"]:
            # Ищем файлы с этим паттерном в названии
            found = list(repo_path.rglob(f"*{pattern}*"))
            count += len(found)

        if count > 0:
            scores[domain] += count * 3  # weight = 3 за файл
            matches[domain] = count

    return matches

def _scan_docs(repo_path: Path, scores: Counter) -> Dict[str, int]:
    """Сканирует документацию (README, *.md, docs/) на keywords"""
    matches = {}

    # Ищем markdown файлы
    doc_files = list(repo_path.rglob("*.md")) + list(repo_path.rglob("*.txt"))
    doc_files = [f for f in doc_files if f.stat().st_size < 500_000]  # skip huge files

    for domain, sig in DOMAIN_SIGNATURES.items():
        count = 0
        for doc_file in doc_files[:50]:  # limit to 50 files
            try:
                content = doc_file.read_text(encoding="utf-8", errors="ignore").lower()
                for keyword in sig["keywords"]:
                    count += len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', content))
            except Exception:
                continue

        if count > 0:
            scores[domain] += count  # weight = 1 за keyword
            matches[domain] = count

    return matches

def _scan_dependencies(repo_path: Path, scores: Counter) -> Dict[str, int]:
    """Сканирует зависимости проекта"""
    matches = {}
    deps_text = ""

    # Python
    req_files = list(repo_path.rglob("requirements*.txt")) + list(repo_path.rglob("Pipfile"))
    for rf in req_files[:5]:
        try:
            deps_text += rf.read_text(encoding="utf-8", errors="ignore").lower() + "\n"
        except Exception:
            pass

    # Node.js
    package_json = repo_path / "package.json"
    if package_json.exists():
        try:
            deps_text += package_json.read_text(encoding="utf-8", errors="ignore").lower() + "\n"
        except Exception:
            pass

    # Go
    go_mod = repo_path / "go.mod"
    if go_mod.exists():
        try:
            deps_text += go_mod.read_text(encoding="utf-8", errors="ignore").lower() + "\n"
        except Exception:
            pass

    # Сканируем на keywords пакетов
    for domain, sig in DOMAIN_SIGNATURES.items():
        count = 0
        for pkg in sig["packages"]:
            count += deps_text.count(pkg.lower())

        if count > 0:
            scores[domain] += count * 5  # weight = 5 за package dependency
            matches[domain] = count

    return matches

def get_domain_config(domain: str) -> Dict[str, any]:
    """Возвращает рекомендуемую конфигурацию для домена"""
    configs = {
        "iso22301": {
            "modules": {
                "compliance": {"enabled": True, "standards": ["ISO22301", "ISO27001"]},
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
                }
            },
            "reports": {
                "formats": ["markdown", "html"],
                "audiences": ["dev", "business", "audit"]
            }
        },
        "security": {
            "modules": {
                "security": {
                    "enabled": True,
                    "checks": ["secrets", "vulnerabilities", "dependencies"],
                    "strict": True
                },
                "quality": {
                    "enabled": True,
                    "checks": ["complexity", "duplication", "tech-debt"]
                },
                "testing": {
                    "enabled": True,
                    "coverage_threshold": 80,
                    "frameworks": ["pytest", "jest", "go-test"]
                }
            },
            "reports": {
                "formats": ["markdown", "json"],
                "audiences": ["dev", "security"]
            }
        },
        "fintech": {
            "modules": {
                "security": {
                    "enabled": True,
                    "checks": ["secrets", "vulnerabilities", "dependencies"],
                    "strict": True
                },
                "compliance": {"enabled": True, "standards": ["PCI-DSS", "SOC2"]},
                "testing": {
                    "enabled": True,
                    "coverage_threshold": 90,
                    "frameworks": ["pytest", "jest", "go-test"]
                },
                "quality": {
                    "enabled": True,
                    "checks": ["complexity", "duplication", "tech-debt"]
                }
            },
            "reports": {
                "formats": ["markdown", "html", "pdf"],
                "audiences": ["dev", "business", "audit", "security"]
            }
        },
        "healthcare": {
            "modules": {
                "security": {
                    "enabled": True,
                    "checks": ["secrets", "vulnerabilities", "dependencies"],
                    "strict": True
                },
                "compliance": {"enabled": True, "standards": ["HIPAA", "GDPR"]},
                "testing": {
                    "enabled": True,
                    "coverage_threshold": 85,
                    "frameworks": ["pytest", "jest", "go-test"]
                }
            },
            "reports": {
                "formats": ["markdown", "html"],
                "audiences": ["dev", "security", "audit"]
            }
        }
    }

    # Default config для unknown доменов
    default = {
        "modules": {
            "security": {"enabled": True},
            "testing": {"enabled": True},
            "quality": {"enabled": True}
        },
        "reports": {
            "formats": ["markdown"],
            "audiences": ["dev"]
        }
    }

    return configs.get(domain, default)
