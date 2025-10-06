#!/usr/bin/env python3
"""
UI Blueprint Generator - Генерация схем UI на основе API эндпоинтов
"""

import json
from pathlib import Path
from typing import Dict, List
from jinja2 import Template


class UIBlueprintGenerator:
    def __init__(self, reports_dir: str = "tools/reports", output_dir: str = "docs/ui"):
        self.reports_dir = Path(reports_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.ast_data = None
        self._load_data()

    def _load_data(self):
        """Загрузить AST анализ"""
        ast_file = self.reports_dir / "ast_analysis.json"
        if ast_file.exists():
            with open(ast_file) as f:
                self.ast_data = json.load(f)

    def generate_blueprints(self):
        """Генерировать UI blueprints для всех сервисов"""
        if not self.ast_data:
            print("❌ No AST data. Run AST analyzer first!")
            return

        print("🎨 Generating UI Blueprints...\n")

        # Группировать эндпоинты по сервисам
        services = self._group_by_service()

        for service_name, endpoints in services.items():
            self._generate_service_blueprint(service_name, endpoints)

        # Генерировать общую навигацию
        self._generate_navigation(services)

        print("\n🎉 UI Blueprints generated!")

    def _group_by_service(self) -> Dict[str, List]:
        """Группировать эндпоинты по сервисам"""
        services = {}

        for endpoint in self.ast_data['endpoints']:
            # Извлечь имя сервиса из пути к файлу
            file_parts = Path(endpoint['file']).parts
            if 'validation-service' in file_parts:
                service_name = 'Validation'
            elif 'documents-service' in file_parts:
                service_name = 'Documents'
            elif 'governance-service' in file_parts:
                service_name = 'Governance'
            elif 'incident-service' in file_parts:
                service_name = 'Incident'
            else:
                service_name = 'Other'

            if service_name not in services:
                services[service_name] = []

            services[service_name].append(endpoint)

        return services

    def _generate_service_blueprint(self, service_name: str, endpoints: List[Dict]):
        """Генерировать blueprint для одного сервиса"""
        # Группировать по ресурсам (извлечь из path)
        resources = {}

        for endpoint in endpoints:
            path = endpoint['path']
            # Извлечь основной ресурс из пути
            parts = [p for p in path.split('/') if p and not p.startswith('{')]
            resource = parts[0] if parts else 'default'

            if resource not in resources:
                resources[resource] = {
                    'list': None,
                    'create': None,
                    'detail': None,
                    'update': None,
                    'delete': None,
                    'custom': []
                }

            # Классифицировать операцию
            method = endpoint['method']
            has_id = '{' in path

            if method == 'GET' and not has_id:
                resources[resource]['list'] = endpoint
            elif method == 'POST' and not has_id:
                resources[resource]['create'] = endpoint
            elif method == 'GET' and has_id:
                resources[resource]['detail'] = endpoint
            elif method == 'PUT' and has_id:
                resources[resource]['update'] = endpoint
            elif method == 'DELETE' and has_id:
                resources[resource]['delete'] = endpoint
            else:
                resources[resource]['custom'].append(endpoint)

        # Генерировать HTML blueprint
        html = self._generate_html_blueprint(service_name, resources)

        output_file = self.output_dir / f"{service_name.lower()}_blueprint.html"
        with open(output_file, 'w') as f:
            f.write(html)

        print(f"✅ {service_name}: {output_file}")

        # Также генерировать JSON спецификацию
        json_spec = {
            'service': service_name,
            'resources': {}
        }

        for resource, operations in resources.items():
            json_spec['resources'][resource] = {
                'screens': self._generate_screen_specs(resource, operations)
            }

        json_file = self.output_dir / f"{service_name.lower()}_spec.json"
        with open(json_file, 'w') as f:
            json.dump(json_spec, f, indent=2)

    def _generate_screen_specs(self, resource: str, operations: Dict) -> List[Dict]:
        """Генерировать спецификации экранов"""
        screens = []

        # List screen
        if operations['list']:
            screens.append({
                'name': f'{resource.title()} List',
                'type': 'list',
                'components': [
                    {'type': 'table', 'data_source': operations['list']['path']},
                    {'type': 'search_bar'},
                    {'type': 'filters'},
                    {'type': 'pagination'},
                    {'type': 'button', 'action': 'create', 'label': f'New {resource.title()}'}
                ]
            })

        # Create screen
        if operations['create']:
            screens.append({
                'name': f'Create {resource.title()}',
                'type': 'form',
                'components': [
                    {'type': 'form', 'endpoint': operations['create']['path'], 'method': 'POST'},
                    {'type': 'button', 'action': 'submit', 'label': 'Create'},
                    {'type': 'button', 'action': 'cancel', 'label': 'Cancel'}
                ]
            })

        # Detail screen
        if operations['detail']:
            screens.append({
                'name': f'{resource.title()} Details',
                'type': 'detail',
                'components': [
                    {'type': 'detail_view', 'data_source': operations['detail']['path']},
                    {'type': 'button', 'action': 'edit', 'label': 'Edit'},
                    {'type': 'button', 'action': 'delete', 'label': 'Delete', 'confirm': True}
                ]
            })

        # Custom actions
        for custom_endpoint in operations['custom']:
            action_name = custom_endpoint['function'].replace('_', ' ').title()
            screens.append({
                'name': action_name,
                'type': 'action',
                'endpoint': custom_endpoint['path'],
                'method': custom_endpoint['method']
            })

        return screens

    def _generate_html_blueprint(self, service_name: str, resources: Dict) -> str:
        """Генерировать HTML blueprint"""
        template = Template('''
<!DOCTYPE html>
<html>
<head>
    <title>{{ service_name }} Service - UI Blueprint</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f5f5f5; }
        h1 { color: #333; }
        .resource { background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .resource h2 { margin-top: 0; color: #0066cc; }
        .screen { border-left: 4px solid #0066cc; padding-left: 15px; margin: 15px 0; }
        .screen h3 { margin: 5px 0; color: #333; }
        .components { margin: 10px 0; }
        .component { background: #f8f9fa; padding: 8px 12px; margin: 5px 0; border-radius: 4px; display: inline-block; margin-right: 10px; }
        .endpoint { font-family: monospace; background: #e9ecef; padding: 3px 8px; border-radius: 3px; font-size: 0.9em; }
        .method { display: inline-block; padding: 2px 8px; border-radius: 3px; color: white; font-size: 0.8em; margin-right: 5px; }
        .get { background: #28a745; }
        .post { background: #007bff; }
        .put { background: #ffc107; }
        .delete { background: #dc3545; }
    </style>
</head>
<body>
    <h1>{{ service_name }} Service - UI Blueprint</h1>
    <p>Автоматически сгенерированные схемы UI на основе API эндпоинтов</p>

    {% for resource, operations in resources.items() %}
    <div class="resource">
        <h2>{{ resource.title() }}</h2>

        {% if operations.list %}
        <div class="screen">
            <h3>📋 List Screen</h3>
            <p><span class="method get">{{ operations.list.method }}</span> <span class="endpoint">{{ operations.list.path }}</span></p>
            <div class="components">
                <span class="component">📊 Data Table</span>
                <span class="component">🔍 Search Bar</span>
                <span class="component">🔧 Filters</span>
                <span class="component">📄 Pagination</span>
                <span class="component">➕ Create Button</span>
            </div>
        </div>
        {% endif %}

        {% if operations.create %}
        <div class="screen">
            <h3>➕ Create Screen</h3>
            <p><span class="method post">{{ operations.create.method }}</span> <span class="endpoint">{{ operations.create.path }}</span></p>
            <div class="components">
                <span class="component">📝 Form</span>
                <span class="component">💾 Submit Button</span>
                <span class="component">❌ Cancel Button</span>
            </div>
        </div>
        {% endif %}

        {% if operations.detail %}
        <div class="screen">
            <h3>👁️ Detail Screen</h3>
            <p><span class="method get">{{ operations.detail.method }}</span> <span class="endpoint">{{ operations.detail.path }}</span></p>
            <div class="components">
                <span class="component">📄 Detail View</span>
                <span class="component">✏️ Edit Button</span>
                <span class="component">🗑️ Delete Button</span>
            </div>
        </div>
        {% endif %}

        {% if operations.update %}
        <div class="screen">
            <h3>✏️ Edit Screen</h3>
            <p><span class="method put">{{ operations.update.method }}</span> <span class="endpoint">{{ operations.update.path }}</span></p>
            <div class="components">
                <span class="component">📝 Form (Pre-filled)</span>
                <span class="component">💾 Save Button</span>
                <span class="component">❌ Cancel Button</span>
            </div>
        </div>
        {% endif %}

        {% if operations.custom %}
        <div class="screen">
            <h3>⚡ Custom Actions</h3>
            {% for custom in operations.custom %}
            <p><span class="method {{ custom.method.lower() }}">{{ custom.method }}</span> <span class="endpoint">{{ custom.path }}</span> - {{ custom.function }}</p>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    {% endfor %}

    <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
        <p>🤖 Автоматически сгенерировано UI Blueprint Generator</p>
    </footer>
</body>
</html>
        ''')

        return template.render(service_name=service_name, resources=resources)

    def _generate_navigation(self, services: Dict):
        """Генерировать общую навигацию"""
        template = Template('''
<!DOCTYPE html>
<html>
<head>
    <title>AI-Platform-ISO UI Blueprints</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f5f5f5; }
        h1 { color: #333; }
        .service-card { background: white; margin: 20px 0; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .service-card h2 { margin-top: 0; color: #0066cc; }
        .stat { display: inline-block; margin: 10px 20px 10px 0; }
        .stat-value { font-size: 2em; font-weight: bold; color: #0066cc; }
        .stat-label { color: #666; font-size: 0.9em; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .button { display: inline-block; background: #0066cc; color: white; padding: 10px 20px; border-radius: 5px; margin: 10px 10px 0 0; }
        .button:hover { background: #0052a3; text-decoration: none; }
    </style>
</head>
<body>
    <h1>🎨 AI-Platform-ISO UI Blueprints</h1>
    <p>Автоматически сгенерированные схемы интерфейсов для всех микросервисов</p>

    {% for service_name, endpoints in services.items() %}
    <div class="service-card">
        <h2>{{ service_name }} Service</h2>
        <div class="stat">
            <div class="stat-value">{{ endpoints|length }}</div>
            <div class="stat-label">Эндпоинтов</div>
        </div>
        <div class="stat">
            <div class="stat-value">{{ endpoints|selectattr('method', 'equalto', 'GET')|list|length }}</div>
            <div class="stat-label">GET</div>
        </div>
        <div class="stat">
            <div class="stat-value">{{ endpoints|selectattr('method', 'equalto', 'POST')|list|length }}</div>
            <div class="stat-label">POST</div>
        </div>
        <br>
        <a class="button" href="{{ service_name.lower() }}_blueprint.html">📋 View Blueprint</a>
        <a class="button" href="{{ service_name.lower() }}_spec.json">📄 JSON Spec</a>
    </div>
    {% endfor %}

    <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
        <p>🤖 Автоматически сгенерировано UI Blueprint Generator</p>
        <p>Используйте эти blueprints для создания фронтенд интерфейсов (React, Vue, Angular)</p>
    </footer>
</body>
</html>
        ''')

        html = template.render(services=services)

        output_file = self.output_dir / "index.html"
        with open(output_file, 'w') as f:
            f.write(html)

        print(f"\n✅ Navigation: {output_file}")
        print(f"   Open in browser: file://{output_file.absolute()}")


if __name__ == "__main__":
    generator = UIBlueprintGenerator()
    generator.generate_blueprints()
