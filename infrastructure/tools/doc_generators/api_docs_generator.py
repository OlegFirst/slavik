#!/usr/bin/env python3
"""
API Documentation Generator - Генерация документации из OpenAPI спецификаций
"""

import json
import httpx
import asyncio
from pathlib import Path
from typing import Dict, List
from jinja2 import Template


class APIDocsGenerator:
    def __init__(self, output_dir: str = "docs/api"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Список сервисов и их портов
        self.services = {
            'validation': 8022,
            'documents': 8024,
            'governance': 8020,
            'incident': 8025,
        }

        self.specs = {}

    async def fetch_openapi_specs(self):
        """Получить OpenAPI спецификации от запущенных сервисов"""
        print(" Fetching OpenAPI specifications from services...\n")

        async with httpx.AsyncClient(timeout=5.0) as client:
            for service_name, port in self.services.items():
                try:
                    url = f"http://localhost:{port}/openapi.json"
                    response = await client.get(url)
                    if response.status_code == 200:
                        self.specs[service_name] = response.json()
                        print(f" {service_name}: {len(self.specs[service_name].get('paths', {}))} endpoints")
                    else:
                        print(f"️  {service_name}: Service not responding (port {port})")
                except Exception as e:
                    print(f"️  {service_name}: {str(e)[:50]}")

    def generate_markdown_docs(self):
        """Генерировать Markdown документацию"""
        print("\n Generating Markdown documentation...\n")

        for service_name, spec in self.specs.items():
            self._generate_service_markdown(service_name, spec)

        # Создать общий index
        self._generate_index()

    def _generate_service_markdown(self, service_name: str, spec: Dict):
        """Генерировать Markdown для одного сервиса"""
        md_content = f"# {spec.get('info', {}).get('title', service_name)} API\n\n"
        md_content += f"{spec.get('info', {}).get('description', '')}\n\n"
        md_content += f"**Version:** {spec.get('info', {}).get('version', 'N/A')}\n\n"

        md_content += "## Endpoints\n\n"

        # Группировать по тегам
        endpoints_by_tag = {}
        for path, methods in spec.get('paths', {}).items():
            for method, details in methods.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    tags = details.get('tags', ['Default'])
                    tag = tags[0] if tags else 'Default'

                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []

                    endpoints_by_tag[tag].append({
                        'path': path,
                        'method': method.upper(),
                        'summary': details.get('summary', ''),
                        'description': details.get('description', ''),
                        'parameters': details.get('parameters', []),
                        'request_body': details.get('requestBody', {}),
                        'responses': details.get('responses', {})
                    })

        # Генерировать документацию по тегам
        for tag, endpoints in sorted(endpoints_by_tag.items()):
            md_content += f"### {tag}\n\n"

            for endpoint in endpoints:
                md_content += f"#### `{endpoint['method']}` {endpoint['path']}\n\n"

                if endpoint['summary']:
                    md_content += f"**{endpoint['summary']}**\n\n"

                if endpoint['description']:
                    md_content += f"{endpoint['description']}\n\n"

                # Parameters
                if endpoint['parameters']:
                    md_content += "**Parameters:**\n\n"
                    md_content += "| Name | Type | Location | Required | Description |\n"
                    md_content += "|------|------|----------|----------|-------------|\n"
                    for param in endpoint['parameters']:
                        name = param.get('name', '')
                        param_type = param.get('schema', {}).get('type', 'string')
                        location = param.get('in', '')
                        required = '' if param.get('required', False) else ''
                        description = param.get('description', '')
                        md_content += f"| `{name}` | {param_type} | {location} | {required} | {description} |\n"
                    md_content += "\n"

                # Request Body
                if endpoint['request_body']:
                    md_content += "**Request Body:**\n\n"
                    content = endpoint['request_body'].get('content', {})
                    if 'application/json' in content:
                        schema = content['application/json'].get('schema', {})
                        md_content += f"```json\n{json.dumps(schema, indent=2)}\n```\n\n"

                # Responses
                if endpoint['responses']:
                    md_content += "**Responses:**\n\n"
                    for status, response in endpoint['responses'].items():
                        md_content += f"- **{status}**: {response.get('description', '')}\n"
                    md_content += "\n"

                md_content += "---\n\n"

        # Сохранить файл
        output_file = self.output_dir / f"{service_name}.md"
        with open(output_file, 'w') as f:
            f.write(md_content)

        print(f" {service_name}: {output_file}")

    def _generate_index(self):
        """Генерировать индексный файл"""
        md_content = "# AI-Platform-ISO API Documentation\n\n"
        md_content += "## Services\n\n"

        for service_name, spec in self.specs.items():
            title = spec.get('info', {}).get('title', service_name)
            description = spec.get('info', {}).get('description', '')
            endpoint_count = len(spec.get('paths', {}))

            md_content += f"### [{title}]({service_name}.md)\n\n"
            md_content += f"{description}\n\n"
            md_content += f"- **Endpoints:** {endpoint_count}\n"
            md_content += f"- **Version:** {spec.get('info', {}).get('version', 'N/A')}\n\n"

        output_file = self.output_dir / "README.md"
        with open(output_file, 'w') as f:
            f.write(md_content)

        print(f"\n Index: {output_file}")

    def generate_postman_collection(self):
        """Генерировать Postman коллекцию"""
        print("\n Generating Postman collection...\n")

        collection = {
            "info": {
                "name": "AI-Platform-ISO API",
                "description": "Complete API collection for all services",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }

        for service_name, spec in self.specs.items():
            service_folder = {
                "name": spec.get('info', {}).get('title', service_name),
                "item": []
            }

            for path, methods in spec.get('paths', {}).items():
                for method, details in methods.items():
                    if method in ['get', 'post', 'put', 'delete', 'patch']:
                        request = {
                            "name": details.get('summary', f"{method.upper()} {path}"),
                            "request": {
                                "method": method.upper(),
                                "header": [
                                    {"key": "Content-Type", "value": "application/json"}
                                ],
                                "url": {
                                    "raw": f"{{{{base_url}}}}{path}",
                                    "host": ["{{base_url}}"],
                                    "path": path.strip('/').split('/')
                                }
                            }
                        }

                        # Добавить request body для POST/PUT/PATCH
                        if method in ['post', 'put', 'patch'] and 'requestBody' in details:
                            request['request']['body'] = {
                                "mode": "raw",
                                "raw": json.dumps({}, indent=2)
                            }

                        service_folder['item'].append(request)

            collection['item'].append(service_folder)

        # Сохранить коллекцию
        output_file = self.output_dir / "postman_collection.json"
        with open(output_file, 'w') as f:
            json.dump(collection, f, indent=2)

        print(f" Postman collection: {output_file}")
        print(f"   Import to Postman: Collections → Import → {output_file.name}")

    async def run(self):
        """Запустить генерацию документации"""
        print(" API Documentation Generator\n")

        await self.fetch_openapi_specs()

        if not self.specs:
            print("\n️  No services are running. Start services first:")
            print("   cd platform-services/validation-service && python main.py")
            print("   cd platform-services/documents-service && python main.py")
            return

        self.generate_markdown_docs()
        self.generate_postman_collection()

        print("\n Documentation generation complete!")
        print(f"\nDocumentation: {self.output_dir.absolute()}")


if __name__ == "__main__":
    generator = APIDocsGenerator()
    asyncio.run(generator.run())
