#!/usr/bin/env python3
"""
Merge Catalogs Script
Объединяет SERVICE_CATALOG_DETAILED.yaml с данными из SERVICE_INFO.yaml файлов

Обновляет:
- Порты сервисов (из runtime.port в SERVICE_INFO.yaml)
- Endpoints (из endpoints в SERVICE_INFO.yaml)
- Версии (из version в SERVICE_INFO.yaml)
- Статусы (из status в SERVICE_INFO.yaml)
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).parent.parent.parent.parent
DETAILED_CATALOG = BASE_DIR / "infrastructure/SERVICE_CATALOG_DETAILED.yaml"
SERVICE_INFO_DIR = BASE_DIR

# Mapping: service name in DETAILED catalog -> SERVICE_INFO.yaml path
SERVICE_INFO_MAPPING = {
    # Intelligent Core
    'workflow_engine': 'intelligent-core/workflow-engine/SERVICE_INFO.yaml',
    'ai_orchestration': 'intelligent-core/orchestration/ai-orchestration/SERVICE_INFO.yaml',
    'event_intelligence': 'intelligent-core/event_intelligence/SERVICE_INFO.yaml',
    'predictive': 'intelligent-core/predictive/SERVICE_INFO.yaml',
    'coordination_center': 'intelligent-core/coordination-center/SERVICE_INFO.yaml',
    'collective': 'intelligent-core/collective/SERVICE_INFO.yaml',
    'ai_workflow_optimizer': 'intelligent-core/ai_workflow_optimizer/SERVICE_INFO.yaml',

    # Platform Services
    'plans_service': 'platform-services/plans_service/SERVICE_INFO.yaml',
    'documents_service': 'platform-services/documents-service/SERVICE_INFO.yaml',
    'governance_service': 'platform-services/governance-service/SERVICE_INFO.yaml',
    'compliance_service': 'platform-services/compliance-service/SERVICE_INFO.yaml',
    'risk_service': 'platform-services/risk-service/SERVICE_INFO.yaml',
    'response_service': 'platform-services/response-service/SERVICE_INFO.yaml',
}


def load_service_info(path: Path) -> Dict[str, Any]:
    """Load SERVICE_INFO.yaml file"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"  ⚠️ Warning: Could not load {path}: {e}")
        return {}


def update_service_from_info(service: Dict[str, Any], service_info: Dict[str, Any]) -> Dict[str, Any]:
    """Update service entry with data from SERVICE_INFO.yaml"""

    # Update runtime port
    if 'runtime' in service_info:
        if 'runtime' not in service:
            service['runtime'] = {}
        if 'port' in service_info['runtime']:
            service['runtime']['port'] = service_info['runtime']['port']

    # Update endpoints
    if 'endpoints' in service_info:
        if 'endpoints' not in service:
            service['endpoints'] = {}
        service['endpoints'].update(service_info['endpoints'])

    # Update version
    if 'version' in service_info:
        service['version'] = service_info['version']

    # Update display_name
    if 'display_name' in service_info:
        service['display_name'] = service_info['display_name']

    # Update status from SERVICE_INFO
    if 'status' in service_info:
        if 'registration' not in service:
            service['registration'] = {}
        service['registration']['status'] = service_info['status']

    # Add source reference
    service['_updated_from_service_info'] = True

    return service


def main():
    print("=" * 80)
    print("🔄 MERGE CATALOGS - Обновление SERVICE_CATALOG_DETAILED.yaml")
    print("=" * 80)

    # Load detailed catalog
    print(f"\n📖 Загрузка: {DETAILED_CATALOG}")
    with open(DETAILED_CATALOG, 'r', encoding='utf-8') as f:
        catalog = yaml.safe_load(f)

    print(f"  ✅ Загружено: версия {catalog.get('version', 'N/A')}, {catalog.get('total_services', 0)} сервисов")

    # Update services
    updated_count = 0
    print(f"\n🔄 Обновление сервисов из SERVICE_INFO.yaml файлов:")
    print("-" * 80)

    # Update Intelligent Core services
    if 'intelligent_core' in catalog:
        for service_name, service_data in catalog['intelligent_core'].items():
            if service_name == 'intelligent_core':  # skip metadata
                continue

            if isinstance(service_data, dict) and service_name in SERVICE_INFO_MAPPING:
                service_info_path = BASE_DIR / SERVICE_INFO_MAPPING[service_name]

                if service_info_path.exists():
                    print(f"  📄 {service_name:30} <- {SERVICE_INFO_MAPPING[service_name]}")
                    service_info = load_service_info(service_info_path)

                    if service_info:
                        catalog['intelligent_core'][service_name] = update_service_from_info(
                            service_data, service_info
                        )

                        # Show updated port
                        port = catalog['intelligent_core'][service_name].get('runtime', {}).get('port', 'N/A')
                        version = catalog['intelligent_core'][service_name].get('version', 'N/A')
                        print(f"     ✅ Обновлено: Port {port}, Version {version}")
                        updated_count += 1
                else:
                    print(f"  ⚠️  {service_name:30} - SERVICE_INFO.yaml не найден")

    # Update Platform Services
    if 'platform_services' in catalog:
        for service_name, service_data in catalog['platform_services'].items():
            if service_name == 'platform_services':  # skip metadata
                continue

            if isinstance(service_data, dict) and service_name in SERVICE_INFO_MAPPING:
                service_info_path = BASE_DIR / SERVICE_INFO_MAPPING[service_name]

                if service_info_path.exists():
                    print(f"  📄 {service_name:30} <- {SERVICE_INFO_MAPPING[service_name]}")
                    service_info = load_service_info(service_info_path)

                    if service_info:
                        catalog['platform_services'][service_name] = update_service_from_info(
                            service_data, service_info
                        )

                        # Show updated port
                        port = catalog['platform_services'][service_name].get('runtime', {}).get('port', 'N/A')
                        version = catalog['platform_services'][service_name].get('version', 'N/A')
                        print(f"     ✅ Обновлено: Port {port}, Version {version}")
                        updated_count += 1
                else:
                    print(f"  ⚠️  {service_name:30} - SERVICE_INFO.yaml не найден")

    print(f"\n" + "-" * 80)
    print(f"✅ Обновлено сервисов: {updated_count}")

    # Update metadata
    print(f"\n📊 Обновление метаданных...")
    # Версия остается как есть, так как это детальный каталог
    # Можно добавить timestamp обновления
    from datetime import datetime
    catalog['last_updated'] = datetime.now().isoformat()
    catalog['_merge_info'] = {
        'merged_at': datetime.now().isoformat(),
        'services_updated': updated_count,
        'source': 'SERVICE_INFO.yaml files'
    }

    # Save updated catalog
    output_path = DETAILED_CATALOG
    backup_path = DETAILED_CATALOG.parent / (DETAILED_CATALOG.stem + "_backup.yaml")

    # Create backup
    print(f"\n💾 Создание резервной копии: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        yaml.dump(catalog, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  ✅ Резервная копия сохранена")

    # Save updated catalog
    print(f"\n💾 Сохранение обновленного каталога: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        # Add header comment
        f.write("# 🏢 AI Platform Infrastructure - Detailed Service Catalog\n")
        f.write(f"# Version: {catalog.get('version', 'N/A')}\n")
        f.write(f"# Last Updated: {catalog.get('last_updated', 'N/A')}\n")
        f.write(f"# Purpose: Comprehensive service catalog with all metadata\n")
        f.write(f"# Updated from: SERVICE_INFO.yaml files\n")
        f.write("\n")

        yaml.dump(catalog, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"  ✅ Каталог обновлен")

    # Print summary
    print(f"\n" + "=" * 80)
    print(f"✅ MERGE COMPLETE")
    print(f"=" * 80)
    print(f"\n📊 Итоговая статистика:")
    print(f"  - Обновлено сервисов: {updated_count}")
    print(f"  - Резервная копия: {backup_path}")
    print(f"  - Обновленный каталог: {output_path}")
    print(f"\n🎉 Каталоги успешно объединены!")

    return 0


if __name__ == '__main__':
    sys.exit(main())
