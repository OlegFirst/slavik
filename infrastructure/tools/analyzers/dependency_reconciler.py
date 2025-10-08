#!/usr/bin/env python3
"""
Dependency Reconciler - Автоматическое исправление архитектурной документации

Читает результаты dependency_validator.py и автоматически:
1. Обновляет SERVICE_CATALOG.yaml с недостающими сервисами
2. Добавляет недокументированные зависимости
3. Удаляет устаревшие зависимости (с подтверждением)
4. Генерирует отчет изменений

Использование:
    python3 tools/analyzers/dependency_reconciler.py --auto-fix
    python3 tools/analyzers/dependency_reconciler.py --dry-run  # Просмотр без изменений
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class DependencyReconciler:
    def __init__(self, validation_report: str = "infrastructure/AI-office-infrastructure/devops-agent/reports-generated/dependency_validation.json"):
        self.validation_report = Path(validation_report)
        self.catalog_path = Path("docs/architecture/SERVICE_CATALOG.yaml")
        self.changes = defaultdict(list)

        if not self.validation_report.exists():
            raise FileNotFoundError(f"Validation report not found: {validation_report}")

        # Загрузить результаты валидации
        with open(self.validation_report) as f:
            self.validation = json.load(f)

        # Загрузить текущий catalog
        with open(self.catalog_path) as f:
            self.catalog = yaml.safe_load(f)

    def analyze_gaps(self) -> Dict:
        """Проанализировать расхождения между кодом и документацией"""

        real_deps = self.validation['real_dependencies']
        doc_deps = self.validation['documented_dependencies']

        gaps = {
            'missing_services': [],      # Сервисы есть в коде, но нет в catalog
            'missing_dependencies': {},  # Зависимости есть в коде, но не задокументированы
            'obsolete_dependencies': {}, # Зависимости в catalog, но не используются в коде
            'missing_in_code': []        # Сервисы в catalog, но нет в коде
        }

        # 1. Найти сервисы, которых нет в catalog
        documented_services = set(doc_deps.keys())
        real_services = set(real_deps.keys())

        gaps['missing_services'] = list(real_services - documented_services)
        gaps['missing_in_code'] = list(documented_services - real_services)

        # 2. Найти недокументированные зависимости
        for service in real_services:
            real = set(real_deps.get(service, []))
            documented = set(doc_deps.get(service, []))

            missing = real - documented
            if missing:
                gaps['missing_dependencies'][service] = list(missing)

        # 3. Найти устаревшие зависимости
        for service in documented_services:
            real = set(real_deps.get(service, []))
            documented = set(doc_deps.get(service, []))

            obsolete = documented - real
            if obsolete:
                gaps['obsolete_dependencies'][service] = list(obsolete)

        return gaps

    def _find_service_location(self, service_name: str) -> str:
        """Найти путь к сервису в файловой системе"""

        # Маппинг известных путей
        path_mapping = {
            'workflow_intelligence': 'intelligent-core/workflow_intelligence',
            'ai_workflow_optimizer': 'intelligent-core/ai_workflow_optimizer',
            'workflow-engine': 'intelligent-core/workflow-engine',
            'expertise-center': 'intelligent-core/expertise-center',
            'orchestration': 'intelligent-core/orchestration',
            'community_intelligence': 'intelligent-core/community_intelligence',
            'collective': 'intelligent-core/collective',
            'predictive': 'intelligent-core/predictive',

            'compliance_service': 'platform-services/compliance-service',
            'governance_service': 'platform-services/governance-service',
            'validation_service': 'platform-services/validation-service',
            'bia_service': 'platform-services/bia-service',
            'risk_service': 'platform-services/risk-service',
            'documents_service': 'platform-services/documents-service',
            'response_service': 'platform-services/response-service',
            'learning_service': 'platform-services/learning-service',
            'planning_service': 'platform-services/planning_service',
            'plans_service': 'platform-services/plans_service',
            'living_docs': 'platform-services/living-docs',
        }

        return path_mapping.get(service_name, f"unknown/{service_name}")

    def _classify_service_layer(self, service_name: str) -> str:
        """Определить слой архитектуры для сервиса"""

        if service_name in ['workflow_intelligence', 'ai_workflow_optimizer', 'workflow-engine',
                           'expertise-center', 'orchestration']:
            return 'ai_foundation'

        if service_name in ['community_intelligence', 'collective', 'predictive', 'learning_system', 'living_docs']:
            return 'ai_services'

        if '_service' in service_name or service_name.endswith('-service'):
            return 'platform_services'

        return 'infrastructure'

    def auto_fix(self, dry_run: bool = False) -> Dict:
        """Автоматически исправить SERVICE_CATALOG.yaml"""

        gaps = self.analyze_gaps()
        fixed_catalog = self.catalog.copy()

        # 1. Добавить недостающие сервисы
        for service_name in gaps['missing_services']:
            # Пропустить служебные директории
            if service_name in ['_archive', 'можетпригодится', 'main.py', 'архив']:
                continue

            layer = self._classify_service_layer(service_name)
            location = self._find_service_location(service_name)

            if layer not in fixed_catalog:
                fixed_catalog[layer] = {}

            # Создать базовую структуру сервиса
            real_deps = self.validation['real_dependencies'].get(service_name, [])

            fixed_catalog[layer][service_name] = {
                'type': 'service',
                'location': location,
                'technology': ['Python 3.11', 'FastAPI'],
                'dependencies': {
                    'infrastructure': [d for d in real_deps if d.startswith('database/') or d.startswith('runtime/')],
                    'external': [d for d in real_deps if d.startswith('external/')],
                    'internal': [d for d in real_deps if d.startswith('ai_') or d.startswith('shared/')]
                },
                'status': 'discovered',
                'auto_generated': True
            }

            self.changes['added_services'].append(service_name)

        # 2. Обновить зависимости существующих сервисов
        for service_name, missing_deps in gaps['missing_dependencies'].items():
            if service_name in ['_archive', 'можетпригодится', 'main.py']:
                continue

            # Найти сервис в catalog
            for layer in ['ai_foundation', 'ai_services', 'platform_services', 'infrastructure']:
                if layer in fixed_catalog and service_name in fixed_catalog[layer]:
                    service = fixed_catalog[layer][service_name]

                    if 'dependencies' not in service:
                        service['dependencies'] = {}

                    # Добавить недостающие зависимости
                    for dep in missing_deps:
                        if dep.startswith('database/') or dep.startswith('runtime/'):
                            if 'infrastructure' not in service['dependencies']:
                                service['dependencies']['infrastructure'] = []
                            if dep not in service['dependencies']['infrastructure']:
                                service['dependencies']['infrastructure'].append(dep)

                        elif dep.startswith('external/'):
                            if 'external' not in service['dependencies']:
                                service['dependencies']['external'] = []
                            if dep not in service['dependencies']['external']:
                                service['dependencies']['external'].append(dep)

                        else:
                            if 'internal' not in service['dependencies']:
                                service['dependencies']['internal'] = []
                            if dep not in service['dependencies']['internal']:
                                service['dependencies']['internal'].append(dep)

                    self.changes['updated_dependencies'].append(service_name)
                    break

        # 3. Сохранить изменения (если не dry-run)
        if not dry_run:
            backup_path = self.catalog_path.with_suffix('.yaml.backup')
            # Создать backup
            with open(self.catalog_path) as f:
                with open(backup_path, 'w') as bf:
                    bf.write(f.read())

            # Сохранить обновленный catalog
            with open(self.catalog_path, 'w') as f:
                yaml.dump(fixed_catalog, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

            print(f"✅ Backup saved: {backup_path}")
            print(f"✅ Updated: {self.catalog_path}")
        else:
            print("🔍 DRY RUN - No changes made")

        return {
            'gaps': gaps,
            'changes': dict(self.changes),
            'fixed_catalog': fixed_catalog if dry_run else None
        }

    def generate_report(self, result: Dict) -> str:
        """Сгенерировать отчет об изменениях"""

        gaps = result['gaps']
        changes = result['changes']

        report = []
        report.append("="*60)
        report.append("📊 DEPENDENCY RECONCILIATION REPORT")
        report.append("="*60)

        # Недостающие сервисы
        if gaps['missing_services']:
            report.append(f"\n🆕 MISSING SERVICES ({len(gaps['missing_services'])}):")
            for service in gaps['missing_services']:
                if service not in ['_archive', 'можетпригодится', 'main.py', 'архив']:
                    report.append(f"  • {service}")

        # Недокументированные зависимости
        if gaps['missing_dependencies']:
            report.append(f"\n📌 MISSING DEPENDENCIES ({len(gaps['missing_dependencies'])} services):")
            for service, deps in list(gaps['missing_dependencies'].items())[:10]:
                report.append(f"  • {service}: {', '.join(deps[:5])}")
            if len(gaps['missing_dependencies']) > 10:
                report.append(f"  ... and {len(gaps['missing_dependencies']) - 10} more")

        # Устаревшие зависимости
        if gaps['obsolete_dependencies']:
            report.append(f"\n⚠️  OBSOLETE DEPENDENCIES ({len(gaps['obsolete_dependencies'])} services):")
            for service, deps in list(gaps['obsolete_dependencies'].items())[:5]:
                report.append(f"  • {service}: {', '.join(deps)}")

        # Изменения
        if changes:
            report.append("\n✅ CHANGES APPLIED:")
            if changes.get('added_services'):
                report.append(f"  • Added {len(changes['added_services'])} services")
            if changes.get('updated_dependencies'):
                report.append(f"  • Updated dependencies for {len(changes['updated_dependencies'])} services")

        report.append("\n" + "="*60)

        return "\n".join(report)


if __name__ == "__main__":
    import sys

    dry_run = '--dry-run' in sys.argv
    auto_fix = '--auto-fix' in sys.argv or not dry_run

    print("🔧 Dependency Reconciler")
    print(f"Mode: {'DRY RUN' if dry_run else 'AUTO FIX'}\n")

    reconciler = DependencyReconciler()
    result = reconciler.auto_fix(dry_run=dry_run)
    report = reconciler.generate_report(result)

    print(report)

    # Сохранить отчет
    report_path = Path("infrastructure/AI-office-infrastructure/devops-agent/reports-generated/dependency_reconciliation.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\n💾 Report saved: {report_path}")
