"""
ПРИОРИТЕТ 3: Проверка подключения к базам данных

После проверки портов и метрик, проверяем подключение к БД.
Каждый сервис должен:
1. Быть подключен к своей базе данных (PostgreSQL/Redis/etc)
2. Иметь правильную схему БД
3. Иметь миграции в актуальном состоянии

Это инструмент для проектного менеджера.
"""

import logging
import subprocess
import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConnection:
    """Подключение к базе данных"""
    service_name: str
    database_type: str  # 'postgresql', 'redis', 'mongodb', etc
    database_name: str
    is_connected: bool
    schema_exists: bool
    migrations_applied: bool
    connection_pool_size: Optional[int] = None
    error_message: Optional[str] = None


# ИСТОЧНИК ПРАВДЫ: Ожидаемые подключения к БД
EXPECTED_DATABASE_CONNECTIONS = {
    # Platform Services - PostgreSQL
    'planning-service': {
        'type': 'postgresql',
        'database': 'planning',
        'schemas': ['public', 'planning'],
        'required_tables': ['strategies', 'bcm_plans', 'policies']
    },
    'plans-service': {
        'type': 'postgresql',
        'database': 'plans',
        'schemas': ['public', 'plans'],
        'required_tables': ['plans', 'plan_versions', 'plan_exercises']
    },
    'governance-service': {
        'type': 'postgresql',
        'database': 'governance',
        'schemas': ['public', 'governance'],
        'required_tables': ['policies', 'compliance_checks', 'audit_logs']
    },
    'risk-service': {
        'type': 'postgresql',
        'database': 'risk',
        'schemas': ['public', 'risk'],
        'required_tables': ['risks', 'risk_assessments', 'controls']
    },
    'response-service': {
        'type': 'postgresql',
        'database': 'response',
        'schemas': ['public', 'response'],
        'required_tables': ['incidents', 'response_plans', 'teams']
    },
    'learning-service': {
        'type': 'postgresql',
        'database': 'learning',
        'schemas': ['public', 'learning'],
        'required_tables': ['lessons_learned', 'training', 'exercises']
    },

    # Intelligent Core Services
    'workflow-intelligence': {
        'type': 'postgresql',
        'database': 'workflow_intelligence',
        'schemas': ['public'],
        'required_tables': ['workflows', 'tasks', 'predictions']
    },
    'ai-workflow-optimizer': {
        'type': 'redis',
        'database': '0',  # Redis database number
        'key_patterns': ['optimizer:*', 'workflow:*']
    },

    # Monitoring
    'monitoring-service': {
        'type': 'postgresql',
        'database': 'monitoring',
        'schemas': ['public', 'observability'],
        'required_tables': ['metrics', 'alerts', 'incidents']
    },

    # All services use Redis for caching
    'redis-cache': {
        'type': 'redis',
        'database': '0',
        'key_patterns': ['cache:*', 'session:*']
    },
}

# Параметры подключения
DATABASE_CONNECTIONS = {
    'postgresql': {
        'host': 'localhost',
        'port': 5432,
        'user': 'bcm_user',
        'password': 'bcm_password_change_in_production'
    },
    'redis': {
        'host': 'localhost',
        'port': 6379
    }
}


class DatabaseConnectionChecker:
    """
    Проверка подключений к базам данных

    ПРИОРИТЕТ 3: Запускается после проверки портов и метрик
    """

    def __init__(self):
        self.connections: Dict[str, DatabaseConnection] = {}
        self.postgres_available = False
        self.redis_available = False

    def check_postgres_available(self) -> bool:
        """Проверить доступность PostgreSQL"""
        try:
            config = DATABASE_CONNECTIONS['postgresql']

            result = subprocess.run(
                [
                    'psql',
                    '-h', config['host'],
                    '-p', str(config['port']),
                    '-U', config['user'],
                    '-c', 'SELECT 1;'
                ],
                env={'PGPASSWORD': config['password']},
                capture_output=True,
                timeout=5
            )

            self.postgres_available = (result.returncode == 0)
            return self.postgres_available

        except Exception as e:
            logger.error(f"Не удалось подключиться к PostgreSQL: {e}")
            self.postgres_available = False
            return False

    def check_redis_available(self) -> bool:
        """Проверить доступность Redis"""
        try:
            config = DATABASE_CONNECTIONS['redis']

            result = subprocess.run(
                [
                    'redis-cli',
                    '-h', config['host'],
                    '-p', str(config['port']),
                    'PING'
                ],
                capture_output=True,
                timeout=5
            )

            self.redis_available = (
                result.returncode == 0 and
                b'PONG' in result.stdout
            )
            return self.redis_available

        except Exception as e:
            logger.error(f"Не удалось подключиться к Redis: {e}")
            self.redis_available = False
            return False

    def check_postgres_database(self, database_name: str) -> Dict[str, any]:
        """
        Проверить PostgreSQL базу данных

        Args:
            database_name: Имя базы данных

        Returns:
            Результат проверки
        """
        if not self.postgres_available:
            return {
                'exists': False,
                'error': 'PostgreSQL недоступен'
            }

        try:
            config = DATABASE_CONNECTIONS['postgresql']

            # Проверяем существование БД
            result = subprocess.run(
                [
                    'psql',
                    '-h', config['host'],
                    '-p', str(config['port']),
                    '-U', config['user'],
                    '-d', 'postgres',  # Подключаемся к postgres БД
                    '-t',  # Только данные, без заголовков
                    '-c', f"SELECT 1 FROM pg_database WHERE datname = '{database_name}';"
                ],
                env={'PGPASSWORD': config['password']},
                capture_output=True,
                timeout=5
            )

            exists = (result.returncode == 0 and result.stdout.strip())

            if not exists:
                return {
                    'exists': False,
                    'error': f'База данных {database_name} не существует'
                }

            # Получаем список таблиц
            result = subprocess.run(
                [
                    'psql',
                    '-h', config['host'],
                    '-p', str(config['port']),
                    '-U', config['user'],
                    '-d', database_name,
                    '-t',
                    '-c', "SELECT tablename FROM pg_tables WHERE schemaname = 'public';"
                ],
                env={'PGPASSWORD': config['password']},
                capture_output=True,
                timeout=5
            )

            tables = [
                line.strip()
                for line in result.stdout.decode('utf-8').split('\n')
                if line.strip()
            ]

            return {
                'exists': True,
                'tables': tables,
                'table_count': len(tables)
            }

        except Exception as e:
            return {
                'exists': False,
                'error': str(e)
            }

    def check_redis_database(self, db_number: str) -> Dict[str, any]:
        """
        Проверить Redis базу данных

        Args:
            db_number: Номер БД (0-15)

        Returns:
            Результат проверки
        """
        if not self.redis_available:
            return {
                'exists': False,
                'error': 'Redis недоступен'
            }

        try:
            config = DATABASE_CONNECTIONS['redis']

            # Переключаемся на нужную БД и получаем количество ключей
            result = subprocess.run(
                [
                    'redis-cli',
                    '-h', config['host'],
                    '-p', str(config['port']),
                    '-n', db_number,
                    'DBSIZE'
                ],
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                key_count = int(result.stdout.strip())

                return {
                    'exists': True,
                    'key_count': key_count
                }

            return {
                'exists': False,
                'error': 'Не удалось получить информацию о БД'
            }

        except Exception as e:
            return {
                'exists': False,
                'error': str(e)
            }

    def check_connections(self) -> List[DatabaseConnection]:
        """
        Проверить все подключения к БД

        Returns:
            Список подключений
        """
        logger.info("=" * 80)
        logger.info("ПРИОРИТЕТ 3: Проверка подключений к базам данных")
        logger.info("=" * 80)

        # Проверяем доступность БД
        postgres_ok = self.check_postgres_available()
        redis_ok = self.check_redis_available()

        logger.info(f"PostgreSQL: {'✅ доступен' if postgres_ok else '❌ недоступен'}")
        logger.info(f"Redis: {'✅ доступен' if redis_ok else '❌ недоступен'}")
        logger.info("")

        connections = []

        for service_name, config in EXPECTED_DATABASE_CONNECTIONS.items():
            db_type = config['type']
            db_name = config['database']

            is_connected = False
            schema_exists = False
            migrations_applied = False
            error_msg = None

            # Проверяем подключение в зависимости от типа БД
            if db_type == 'postgresql':
                result = self.check_postgres_database(db_name)

                is_connected = result.get('exists', False)

                if is_connected:
                    # Проверяем наличие обязательных таблиц
                    tables = result.get('tables', [])
                    required_tables = config.get('required_tables', [])

                    schema_exists = all(
                        table in tables
                        for table in required_tables
                    )

                    if schema_exists:
                        migrations_applied = True  # Упрощение
                    else:
                        missing = [t for t in required_tables if t not in tables]
                        error_msg = f"Отсутствуют таблицы: {', '.join(missing)}"
                else:
                    error_msg = result.get('error', 'База данных не существует')

            elif db_type == 'redis':
                result = self.check_redis_database(db_name)

                is_connected = result.get('exists', False)
                schema_exists = is_connected  # Redis не имеет схемы
                migrations_applied = is_connected

                if not is_connected:
                    error_msg = result.get('error', 'Redis недоступен')

            connection = DatabaseConnection(
                service_name=service_name,
                database_type=db_type,
                database_name=db_name,
                is_connected=is_connected,
                schema_exists=schema_exists,
                migrations_applied=migrations_applied,
                error_message=error_msg
            )

            connections.append(connection)
            self.connections[service_name] = connection

            # Логирование
            status = "✅" if is_connected and schema_exists else "❌"
            logger.info(f"{status} {service_name}:")
            logger.info(f"   Тип БД: {db_type}")
            logger.info(f"   БД: {db_name}")
            logger.info(f"   Подключено: {'✅' if is_connected else '❌'}")
            logger.info(f"   Схема существует: {'✅' if schema_exists else '❌'}")

            if error_msg:
                logger.info(f"   Ошибка: {error_msg}")

            logger.info("")

        # Итоговый отчет
        total = len(connections)
        connected = sum(1 for c in connections if c.is_connected and c.schema_exists)

        logger.info(f"Итого: {connected}/{total} сервисов подключены к БД")

        return connections

    def get_database_state_for_central_brain(self) -> Dict[str, any]:
        """
        Получить состояние БД для Центрального Мозга

        Returns:
            Фактическое состояние БД
        """
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'postgres_available': self.postgres_available,
            'redis_available': self.redis_available,
            'services_connected': sum(
                1 for c in self.connections.values()
                if c.is_connected and c.schema_exists
            ),
            'total_services': len(self.connections)
        }

    def generate_report(self) -> str:
        """Сгенерировать отчет"""
        report = []
        report.append("=" * 80)
        report.append("ПРИОРИТЕТ 3: Отчет о подключениях к базам данных")
        report.append("=" * 80)
        report.append(f"Дата проверки: {datetime.utcnow().isoformat()}")
        report.append("")

        report.append("Доступность БД:")
        report.append(f"  PostgreSQL: {'✅ доступен' if self.postgres_available else '❌ недоступен'}")
        report.append(f"  Redis: {'✅ доступен' if self.redis_available else '❌ недоступен'}")
        report.append("")

        # Статистика
        total = len(self.connections)
        connected = sum(1 for c in self.connections.values() if c.is_connected)
        with_schema = sum(1 for c in self.connections.values() if c.schema_exists)

        report.append("Статистика подключений:")
        report.append(f"  Всего сервисов: {total}")
        report.append(f"  Подключено к БД: {connected}")
        report.append(f"  Схема существует: {with_schema}")
        report.append(f"  Процент готовности: {(with_schema / total * 100) if total > 0 else 0:.1f}%")
        report.append("")

        # Проблемные сервисы
        problems = [
            c for c in self.connections.values()
            if not (c.is_connected and c.schema_exists)
        ]

        if problems:
            report.append(f"❌ Сервисы с проблемами БД ({len(problems)}):")
            for conn in problems:
                report.append(f"  - {conn.service_name}:")
                report.append(f"    БД: {conn.database_type}/{conn.database_name}")

                if conn.error_message:
                    report.append(f"    Проблема: {conn.error_message}")

            report.append("")
        else:
            report.append("✅ Все сервисы корректно подключены к БД")
            report.append("")

        report.append("=" * 80)

        return "\n".join(report)


def check_database_connections() -> bool:
    """
    Проверить подключения к БД (основная функция)

    Returns:
        True если все OK
    """
    checker = DatabaseConnectionChecker()
    connections = checker.check_connections()

    print(checker.generate_report())

    # Проверяем критичные БД
    if not checker.postgres_available:
        logger.error("❌ PostgreSQL недоступен - критичная проблема")
        return False

    if not checker.redis_available:
        logger.warning("⚠️  Redis недоступен - некоторые функции могут не работать")

    # Проверяем процент подключенных сервисов
    connected = sum(1 for c in connections if c.is_connected and c.schema_exists)
    total = len(connections)

    if connected / total < 0.7:  # Менее 70% подключены
        logger.error(
            f"❌ Недостаточно сервисов подключены к БД: "
            f"{connected}/{total} ({connected / total * 100:.0f}%)"
        )
        return False

    return True


if __name__ == '__main__':
    """Запуск проверки"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

    success = check_database_connections()

    exit(0 if success else 1)
