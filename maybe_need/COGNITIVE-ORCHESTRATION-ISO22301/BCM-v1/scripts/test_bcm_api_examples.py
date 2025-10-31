#!/usr/bin/env python3
"""
Примеры тестирования BCM REST API endpoints
Требования: requests, json

Использование:
python test_bcm_api_examples.py

Или для отдельных тестов:
python test_bcm_api_examples.py --test modules
python test_bcm_api_examples.py --test clients
python test_bcm_api_examples.py --test scenarios
"""

import requests
import json
import argparse
import sys
from typing import Dict, Any, Optional

class BCMAPITester:
    def __init__(self, base_url: str = "http://localhost:8069", database: str = "bcm_db"):
        """
        Инициализация тестера BCM API

        Args:
            base_url: базовый URL Odoo сервера
            database: имя базы данных
        """
        self.base_url = base_url
        self.database = database
        self.session = requests.Session()
        self.session_id = None

    def authenticate(self, username: str = "admin", password: str = "admin") -> bool:
        """
        Аутентификация в Odoo

        Args:
            username: имя пользователя
            password: пароль

        Returns:
            True если аутентификация успешна
        """
        auth_url = f"{self.base_url}/web/session/authenticate"
        auth_data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": self.database,
                "login": username,
                "password": password,
            },
            "id": 1
        }

        try:
            response = self.session.post(auth_url, json=auth_data)
            result = response.json()

            if result.get('result') and result['result'].get('uid'):
                print(f"✅ Authentication successful. User ID: {result['result']['uid']}")
                return True
            else:
                print(f"❌ Authentication failed: {result}")
                return False

        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False

    def call_api(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Вызов API endpoint

        Args:
            endpoint: API endpoint (например, '/api/bcm/modules')
            params: параметры запроса

        Returns:
            Ответ API или None при ошибке
        """
        url = f"{self.base_url}{endpoint}"
        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": params or {},
            "id": 1
        }

        try:
            response = self.session.post(url, json=data)
            result = response.json()

            if 'error' in result:
                print(f"❌ API Error: {result['error']}")
                return None

            return result.get('result')

        except Exception as e:
            print(f"❌ Request error: {e}")
            return None

    def test_bcm_modules(self):
        """Тестирование /api/bcm/modules"""
        print("\n🔧 Testing BCM Modules API")
        print("=" * 50)

        # Тест 1: Получить все BCM модули
        print("\n1. Getting all BCM modules:")
        result = self.call_api("/api/bcm/modules")
        if result:
            print(f"   ✅ Success: Found {result.get('total', 0)} modules")
            if result.get('data'):
                for module in result['data'][:3]:  # Показать первые 3
                    print(f"      - {module.get('name')}: {module.get('state')}")

        # Тест 2: Фильтрация по состоянию
        print("\n2. Getting installed BCM modules:")
        result = self.call_api("/api/bcm/modules", {"state": "installed"})
        if result:
            print(f"   ✅ Success: Found {result.get('total', 0)} installed modules")

        # Тест 3: Пагинация
        print("\n3. Testing pagination (limit=5):")
        result = self.call_api("/api/bcm/modules", {"limit": 5, "offset": 0})
        if result:
            print(f"   ✅ Success: Retrieved {len(result.get('data', []))} of {result.get('total', 0)} modules")

    def test_clients_api(self):
        """Тестирование /api/clients"""
        print("\n👥 Testing Clients API")
        print("=" * 50)

        # Тест 1: Получить всех клиентов
        print("\n1. Getting all clients:")
        result = self.call_api("/api/clients")
        if result:
            print(f"   ✅ Success: Found {result.get('total', 0)} clients")
            if result.get('data'):
                for client in result['data'][:3]:
                    print(f"      - {client.get('name')}: {client.get('sector')} ({client.get('status')})")

        # Тест 2: Фильтрация по сектору
        print("\n2. Getting healthcare clients:")
        result = self.call_api("/api/clients", {"sector": "hospital"})
        if result:
            print(f"   ✅ Success: Found {result.get('total', 0)} healthcare clients")

        # Тест 3: Поиск по названию
        print("\n3. Searching clients by name:")
        result = self.call_api("/api/clients", {"search": "test"})
        if result:
            print(f"   ✅ Success: Found {result.get('total', 0)} clients matching 'test'")

        # Тест 4: Детали конкретного клиента
        print("\n4. Getting client details:")
        clients_result = self.call_api("/api/clients", {"limit": 1})
        if clients_result and clients_result.get('data'):
            client_id = clients_result['data'][0]['id']
            result = self.call_api(f"/api/clients/{client_id}")
            if result:
                client_data = result.get('data', {})
                print(f"   ✅ Success: Retrieved details for '{client_data.get('name')}'")
                print(f"      - Contacts: {client_data.get('metrics', {}).get('contact_count', 0)}")
                print(f"      - Plans: {client_data.get('metrics', {}).get('plan_count', 0)}")

    def test_scenarios_api(self):
        """Тестирование /api/scenarios"""
        print("\n🎭 Testing Scenarios API")
        print("=" * 50)

        # Тест 1: Получить все сценарии
        print("\n1. Getting all scenarios:")
        result = self.call_api("/api/scenarios")
        if result:
            print(f"   ✅ Success: Found {result.get('total', 0)} scenarios")
            if result.get('data'):
                for scenario in result['data'][:3]:
                    print(f"      - {scenario.get('title')}: {scenario.get('category')} ({scenario.get('level')})")

        # Тест 2: Фильтрация по категории
        print("\n2. Getting cyber security scenarios:")
        result = self.call_api("/api/scenarios", {"category": "cyber"})
        if result:
            print(f"   ✅ Success: Found {result.get('total', 0)} cyber scenarios")

        # Тест 3: Фильтрация по уровню
        print("\n3. Getting tabletop exercises:")
        result = self.call_api("/api/scenarios", {"level": "tabletop"})
        if result:
            print(f"   ✅ Success: Found {result.get('total', 0)} tabletop exercises")

        # Тест 4: Поиск по тексту
        print("\n4. Searching scenarios:")
        result = self.call_api("/api/scenarios", {"search": "pandemic"})
        if result:
            print(f"   ✅ Success: Found {result.get('total', 0)} scenarios matching 'pandemic'")

        # Тест 5: Детали конкретного сценария
        print("\n5. Getting scenario details:")
        scenarios_result = self.call_api("/api/scenarios", {"limit": 1})
        if scenarios_result and scenarios_result.get('data'):
            scenario_id = scenarios_result['data'][0]['id']
            result = self.call_api(f"/api/scenarios/{scenario_id}")
            if result:
                scenario_data = result.get('data', {})
                print(f"   ✅ Success: Retrieved details for '{scenario_data.get('title')}'")
                print(f"      - Author: {scenario_data.get('author', {}).get('name')}")
                print(f"      - Rating: {scenario_data.get('avg_rating', 0):.1f}")
                print(f"      - Templates: {len(scenario_data.get('available_templates', []))}")

    def test_dashboard_api(self):
        """Тестирование /api/dashboard/{type}"""
        print("\n📊 Testing Dashboard API")
        print("=" * 50)

        dashboard_types = ['overview', 'incidents', 'risk', 'plans', 'kpi', 'clients']

        for dashboard_type in dashboard_types:
            print(f"\n{dashboard_type.capitalize()} Dashboard:")
            result = self.call_api(f"/api/dashboard/{dashboard_type}")
            if result:
                data = result.get('data', {})
                print(f"   ✅ Success: Retrieved {dashboard_type} dashboard data")

                # Показать основные метрики
                if dashboard_type == 'overview':
                    summary = data.get('summary', {})
                    print(f"      - Total clients: {summary.get('total_clients', 0)}")
                    print(f"      - Active incidents: {summary.get('active_incidents', 0)}")
                elif dashboard_type == 'clients':
                    print(f"      - Total clients: {data.get('total_clients', 0)}")
                    sectors = data.get('clients_by_sector', {})
                    if sectors:
                        print(f"      - Sectors: {list(sectors.keys())}")
                elif dashboard_type == 'incidents':
                    severity = data.get('incidents_by_severity', {})
                    print(f"      - Incidents by severity: {severity}")
            else:
                print(f"   ❌ Failed to retrieve {dashboard_type} dashboard")

    def test_notifications_api(self):
        """Тестирование /api/notifications"""
        print("\n🔔 Testing Notifications API")
        print("=" * 50)

        # Тест 1: Получить все уведомления
        print("\n1. Getting all notifications:")
        result = self.call_api("/api/notifications")
        if result:
            print(f"   ✅ Success: Found {result.get('total', 0)} notifications")
            if result.get('data'):
                for notif in result['data'][:3]:
                    print(f"      - {notif.get('subject', 'No subject')}: {notif.get('message_type')}")

        # Тест 2: Фильтрация непрочитанных
        print("\n2. Getting unread notifications:")
        result = self.call_api("/api/notifications", {"unread_only": "true"})
        if result:
            print(f"   ✅ Success: Found {result.get('total', 0)} unread notifications")

    def test_kpi_api(self):
        """Тестирование /api/kpi"""
        print("\n📈 Testing KPI API")
        print("=" * 50)

        print("\n1. Getting KPI data:")
        result = self.call_api("/api/kpi")
        if result:
            data = result.get('data', {})
            print(f"   ✅ Success: Retrieved KPI data")

            # Показать основные KPI
            incidents_kpi = data.get('incidents', {})
            if incidents_kpi:
                print(f"      - Total incidents: {incidents_kpi.get('total_incidents', 0)}")
                print(f"      - Active incidents: {incidents_kpi.get('active_incidents', 0)}")

            clients_kpi = data.get('clients', {})
            if clients_kpi:
                print(f"      - Total clients: {clients_kpi.get('total_clients', 0)}")
                print(f"      - Active clients: {clients_kpi.get('active_clients', 0)}")

    def test_utility_apis(self):
        """Тестирование утилитарных API"""
        print("\n🛠️ Testing Utility APIs")
        print("=" * 50)

        # Health check
        print("\n1. Health check:")
        result = self.call_api("/api/bcm/health")
        if result:
            data = result.get('data', {})
            print(f"   ✅ Success: System status is {data.get('status')}")
            models = data.get('models', {})
            for model_name, model_info in models.items():
                status = "✅" if model_info.get('available') else "❌"
                print(f"      {status} {model_name}: {model_info.get('count', 0)} records")

        # Stats
        print("\n2. BCM Statistics:")
        result = self.call_api("/api/bcm/stats")
        if result:
            data = result.get('data', {})
            print(f"   ✅ Success: Retrieved BCM statistics")
            modules = data.get('modules', {})
            print(f"      - Installed modules: {modules.get('installed_count', 0)}")
            print(f"      - Available modules: {modules.get('available_count', 0)}")

            data_stats = data.get('data', {})
            print(f"      - Clients: {data_stats.get('clients', 0)}")
            print(f"      - Scenarios: {data_stats.get('scenarios', 0)}")

    def run_all_tests(self):
        """Запустить все тесты"""
        print("🚀 Starting BCM API Tests")
        print("=" * 60)

        if not self.authenticate():
            print("❌ Failed to authenticate. Exiting.")
            return False

        self.test_bcm_modules()
        self.test_clients_api()
        self.test_scenarios_api()
        self.test_dashboard_api()
        self.test_notifications_api()
        self.test_kpi_api()
        self.test_utility_apis()

        print("\n🎉 All tests completed!")
        return True

    def run_specific_test(self, test_name: str):
        """Запустить конкретный тест"""
        if not self.authenticate():
            print("❌ Failed to authenticate. Exiting.")
            return False

        test_methods = {
            'modules': self.test_bcm_modules,
            'clients': self.test_clients_api,
            'scenarios': self.test_scenarios_api,
            'dashboard': self.test_dashboard_api,
            'notifications': self.test_notifications_api,
            'kpi': self.test_kpi_api,
            'utility': self.test_utility_apis,
        }

        if test_name in test_methods:
            test_methods[test_name]()
            print(f"\n✅ Test '{test_name}' completed!")
        else:
            print(f"❌ Unknown test: {test_name}")
            print(f"Available tests: {', '.join(test_methods.keys())}")


def main():
    parser = argparse.ArgumentParser(description='Test BCM REST API endpoints')
    parser.add_argument('--url', default='http://localhost:8069', help='Odoo server URL')
    parser.add_argument('--database', default='bcm_db', help='Database name')
    parser.add_argument('--username', default='admin', help='Username')
    parser.add_argument('--password', default='admin', help='Password')
    parser.add_argument('--test', help='Specific test to run')

    args = parser.parse_args()

    tester = BCMAPITester(args.url, args.database)

    if args.test:
        tester.run_specific_test(args.test)
    else:
        tester.run_all_tests()


if __name__ == "__main__":
    main()