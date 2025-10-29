#!/usr/bin/env python3
"""
MSP Inspector - Инструмент для проверки и мониторинга MSP Server
Проверяет состояние всех компонентов и сервисов
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

import httpx
from anthropic_service import AnthropicService

class MSPInspector:
    """Инспектор для проверки MSP Server"""

    def __init__(self, msp_url: str = "http://localhost:8080"):
        """
        Initialize MSP Inspector

        Args:
            msp_url: URL MSP сервера
        """
        self.msp_url = msp_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "msp_url": msp_url,
            "checks": {},
            "summary": {},
            "issues": [],
            "recommendations": []
        }

    async def run_full_inspection(self) -> Dict[str, Any]:
        """Запуск полной проверки MSP сервера"""
        print("🔍 Запуск полной инспекции MSP Server...")
        print("=" * 60)

        # Проверки в последовательности
        checks = [
            ("Connectivity", self._check_connectivity),
            ("Health Status", self._check_health),
            ("Anthropic Service", self._check_anthropic_service),
            ("API Endpoints", self._check_api_endpoints),
            ("Orchestrator Instances", self._check_orchestrator_instances),
            ("Users & Projects", self._check_users_projects),
            ("Recent Tasks", self._check_recent_tasks),
            ("System Statistics", self._check_system_stats),
            ("Performance", self._check_performance),
            ("Security", self._check_security)
        ]

        for check_name, check_function in checks:
            print(f"\n📋 {check_name}...")
            try:
                result = await check_function()
                self.results["checks"][check_name] = result
                status = "✅ PASS" if result["status"] == "pass" else "❌ FAIL"
                print(f"   {status} - {result.get('message', 'No message')}")

                if result["status"] == "fail":
                    self.results["issues"].append({
                        "check": check_name,
                        "issue": result.get("error", "Unknown error"),
                        "severity": result.get("severity", "medium")
                    })

            except Exception as e:
                print(f"   ❌ ERROR - {e}")
                self.results["checks"][check_name] = {
                    "status": "error",
                    "error": str(e),
                    "severity": "high"
                }
                self.results["issues"].append({
                    "check": check_name,
                    "issue": str(e),
                    "severity": "high"
                })

        # Создание итогового отчета
        await self._generate_summary()

        print("\n" + "=" * 60)
        print("📊 ИТОГИ ИНСПЕКЦИИ")
        print("=" * 60)
        print(f"✅ Пройдено: {self.results['summary']['passed_checks']}")
        print(f"❌ Ошибок: {self.results['summary']['failed_checks']}")
        print(f"⚠️  Проблем: {len(self.results['issues'])}")
        print(f"💡 Рекомендаций: {len(self.results['recommendations'])}")

        return self.results

    async def _check_connectivity(self) -> Dict[str, Any]:
        """Проверка подключения к MSP серверу"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.msp_url}/")

                if response.status_code == 200:
                    return {
                        "status": "pass",
                        "message": f"MSP Server доступен (HTTP {response.status_code})",
                        "response_time": response.elapsed.total_seconds()
                    }
                else:
                    return {
                        "status": "fail",
                        "message": f"MSP Server вернул код {response.status_code}",
                        "severity": "high"
                    }

        except Exception as e:
            return {
                "status": "fail",
                "error": f"Не удается подключиться к MSP Server: {e}",
                "severity": "critical"
            }

    async def _check_health(self) -> Dict[str, Any]:
        """Проверка health endpoint"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.msp_url}/health")

                if response.status_code == 200:
                    health_data = response.json()

                    if health_data.get("status") == "healthy":
                        return {
                            "status": "pass",
                            "message": "Все сервисы работают нормально",
                            "data": health_data
                        }
                    else:
                        return {
                            "status": "fail",
                            "message": f"Проблемы со здоровьем сервисов: {health_data}",
                            "severity": "medium",
                            "data": health_data
                        }
                else:
                    return {
                        "status": "fail",
                        "message": f"Health endpoint недоступен (HTTP {response.status_code})",
                        "severity": "high"
                    }

        except Exception as e:
            return {
                "status": "fail",
                "error": f"Ошибка проверки health: {e}",
                "severity": "high"
            }

    async def _check_anthropic_service(self) -> Dict[str, Any]:
        """Проверка Anthropic сервиса"""
        try:
            anthropic_service = AnthropicService()
            health_result = await anthropic_service.health_check()

            if health_result["status"] == "healthy":
                return {
                    "status": "pass",
                    "message": "Anthropic сервис работает корректно",
                    "data": health_result
                }
            elif health_result["status"] == "unavailable":
                return {
                    "status": "fail",
                    "message": "Anthropic API key не сконфигурирован",
                    "severity": "medium",
                    "data": health_result
                }
            else:
                return {
                    "status": "fail",
                    "message": f"Anthropic сервис недоступен: {health_result.get('error', 'Unknown error')}",
                    "severity": "high",
                    "data": health_result
                }

        except Exception as e:
            return {
                "status": "fail",
                "error": f"Ошибка проверки Anthropic: {e}",
                "severity": "high"
            }

    async def _check_api_endpoints(self) -> Dict[str, Any]:
        """Проверка основных API endpoints"""
        endpoints_to_check = [
            ("/api/stats", "GET"),
            ("/api/instances", "GET"),
        ]

        working_endpoints = 0
        total_endpoints = len(endpoints_to_check)
        endpoint_results = []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                for endpoint, method in endpoints_to_check:
                    try:
                        if method == "GET":
                            response = await client.get(f"{self.msp_url}{endpoint}")
                        else:
                            response = await client.post(f"{self.msp_url}{endpoint}")

                        if 200 <= response.status_code < 300:
                            working_endpoints += 1
                            endpoint_results.append({
                                "endpoint": endpoint,
                                "status": "working",
                                "code": response.status_code
                            })
                        else:
                            endpoint_results.append({
                                "endpoint": endpoint,
                                "status": "failed",
                                "code": response.status_code
                            })

                    except Exception as e:
                        endpoint_results.append({
                            "endpoint": endpoint,
                            "status": "error",
                            "error": str(e)
                        })

            if working_endpoints == total_endpoints:
                return {
                    "status": "pass",
                    "message": f"Все {total_endpoints} API endpoints работают",
                    "data": endpoint_results
                }
            else:
                return {
                    "status": "fail",
                    "message": f"Работает {working_endpoints}/{total_endpoints} endpoints",
                    "severity": "medium",
                    "data": endpoint_results
                }

        except Exception as e:
            return {
                "status": "fail",
                "error": f"Ошибка проверки API endpoints: {e}",
                "severity": "high"
            }

    async def _check_orchestrator_instances(self) -> Dict[str, Any]:
        """Проверка оркестраторов"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.msp_url}/api/instances")

                if response.status_code == 200:
                    instances = response.json()

                    if not instances:
                        return {
                            "status": "fail",
                            "message": "Нет зарегистрированных orchestrator instances",
                            "severity": "critical",
                            "data": {"instances_count": 0}
                        }

                    active_instances = [
                        inst for inst in instances
                        if inst.get("status") == "active"
                    ]

                    if active_instances:
                        return {
                            "status": "pass",
                            "message": f"Найдено {len(active_instances)} активных orchestrator(s)",
                            "data": {
                                "total_instances": len(instances),
                                "active_instances": len(active_instances),
                                "instances": instances
                            }
                        }
                    else:
                        return {
                            "status": "fail",
                            "message": f"Нет активных orchestrator instances ({len(instances)} всего)",
                            "severity": "high",
                            "data": {"instances": instances}
                        }
                else:
                    return {
                        "status": "fail",
                        "message": f"Не удается получить список instances (HTTP {response.status_code})",
                        "severity": "high"
                    }

        except Exception as e:
            return {
                "status": "fail",
                "error": f"Ошибка проверки orchestrator instances: {e}",
                "severity": "high"
            }

    async def _check_users_projects(self) -> Dict[str, Any]:
        """Проверка пользователей и проектов"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                stats_response = await client.get(f"{self.msp_url}/api/stats")

                if stats_response.status_code == 200:
                    stats = stats_response.json()

                    total_users = stats.get("total_users", 0)
                    total_projects = stats.get("total_projects", 0)

                    if total_users > 0:
                        return {
                            "status": "pass",
                            "message": f"Система содержит {total_users} пользователей и {total_projects} проектов",
                            "data": stats
                        }
                    else:
                        return {
                            "status": "fail",
                            "message": "В системе нет пользователей",
                            "severity": "medium",
                            "data": stats
                        }
                else:
                    return {
                        "status": "fail",
                        "message": f"Не удается получить статистику (HTTP {stats_response.status_code})",
                        "severity": "medium"
                    }

        except Exception as e:
            return {
                "status": "fail",
                "error": f"Ошибка проверки пользователей и проектов: {e}",
                "severity": "medium"
            }

    async def _check_recent_tasks(self) -> Dict[str, Any]:
        """Проверка последних задач"""
        # Этот чек требует аутентификации, поэтому проверяем косвенно через stats
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                stats_response = await client.get(f"{self.msp_url}/api/stats")

                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    total_tasks = stats.get("total_tasks", 0)

                    return {
                        "status": "pass",
                        "message": f"В системе обработано {total_tasks} задач",
                        "data": {"total_tasks": total_tasks}
                    }
                else:
                    return {
                        "status": "fail",
                        "message": "Не удается получить информацию о задачах",
                        "severity": "low"
                    }

        except Exception as e:
            return {
                "status": "fail",
                "error": f"Ошибка проверки задач: {e}",
                "severity": "low"
            }

    async def _check_system_stats(self) -> Dict[str, Any]:
        """Проверка системной статистики"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.msp_url}/api/stats")

                if response.status_code == 200:
                    stats = response.json()

                    # Проверяем ключевые метрики
                    expected_fields = ["total_users", "total_projects", "total_tasks", "active_instances"]
                    missing_fields = [field for field in expected_fields if field not in stats]

                    if not missing_fields:
                        return {
                            "status": "pass",
                            "message": "Все системные метрики доступны",
                            "data": stats
                        }
                    else:
                        return {
                            "status": "fail",
                            "message": f"Отсутствуют метрики: {missing_fields}",
                            "severity": "medium",
                            "data": stats
                        }
                else:
                    return {
                        "status": "fail",
                        "message": f"Stats endpoint недоступен (HTTP {response.status_code})",
                        "severity": "high"
                    }

        except Exception as e:
            return {
                "status": "fail",
                "error": f"Ошибка проверки системной статистики: {e}",
                "severity": "medium"
            }

    async def _check_performance(self) -> Dict[str, Any]:
        """Проверка производительности"""
        try:
            start_time = datetime.now()

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Замеряем время ответа нескольких endpoint'ов
                response_times = []

                endpoints = ["/", "/health", "/api/stats", "/api/instances"]

                for endpoint in endpoints:
                    endpoint_start = datetime.now()
                    response = await client.get(f"{self.msp_url}{endpoint}")
                    endpoint_time = (datetime.now() - endpoint_start).total_seconds()

                    response_times.append({
                        "endpoint": endpoint,
                        "response_time": endpoint_time,
                        "status_code": response.status_code
                    })

            total_time = (datetime.now() - start_time).total_seconds()
            avg_response_time = sum(rt["response_time"] for rt in response_times) / len(response_times)

            if avg_response_time < 1.0:  # Менее секунды в среднем
                return {
                    "status": "pass",
                    "message": f"Хорошая производительность (среднее время ответа: {avg_response_time:.3f}s)",
                    "data": {
                        "total_check_time": total_time,
                        "average_response_time": avg_response_time,
                        "response_times": response_times
                    }
                }
            else:
                return {
                    "status": "fail",
                    "message": f"Медленные ответы (среднее время: {avg_response_time:.3f}s)",
                    "severity": "medium",
                    "data": {
                        "total_check_time": total_time,
                        "average_response_time": avg_response_time,
                        "response_times": response_times
                    }
                }

        except Exception as e:
            return {
                "status": "fail",
                "error": f"Ошибка проверки производительности: {e}",
                "severity": "medium"
            }

    async def _check_security(self) -> Dict[str, Any]:
        """Проверка безопасности"""
        security_issues = []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Проверяем защищенные endpoints без аутентификации
                protected_endpoints = [
                    "/api/users",
                    "/api/tasks/recent",
                    "/api/analytics"
                ]

                for endpoint in protected_endpoints:
                    try:
                        response = await client.get(f"{self.msp_url}{endpoint}")
                        if response.status_code == 200:
                            security_issues.append(f"Endpoint {endpoint} доступен без аутентификации")
                        elif response.status_code == 401:
                            # Это правильно - endpoint защищен
                            pass
                        else:
                            security_issues.append(f"Неожиданный ответ от {endpoint}: {response.status_code}")
                    except Exception:
                        # Endpoint недоступен - это нормально для этого теста
                        pass

                # Проверяем HTTPS (если это production)
                if self.msp_url.startswith("http://") and "localhost" not in self.msp_url:
                    security_issues.append("Сервер использует HTTP вместо HTTPS")

            if not security_issues:
                return {
                    "status": "pass",
                    "message": "Основные проверки безопасности пройдены",
                    "data": {"issues": []}
                }
            else:
                return {
                    "status": "fail",
                    "message": f"Обнаружено {len(security_issues)} проблем безопасности",
                    "severity": "high",
                    "data": {"issues": security_issues}
                }

        except Exception as e:
            return {
                "status": "fail",
                "error": f"Ошибка проверки безопасности: {e}",
                "severity": "medium"
            }

    async def _generate_summary(self):
        """Генерация итогового отчета"""
        total_checks = len(self.results["checks"])
        passed_checks = sum(1 for check in self.results["checks"].values() if check["status"] == "pass")
        failed_checks = total_checks - passed_checks

        # Группировка проблем по серьезности
        critical_issues = [issue for issue in self.results["issues"] if issue.get("severity") == "critical"]
        high_issues = [issue for issue in self.results["issues"] if issue.get("severity") == "high"]
        medium_issues = [issue for issue in self.results["issues"] if issue.get("severity") == "medium"]

        self.results["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "success_rate": round((passed_checks / total_checks) * 100, 1) if total_checks > 0 else 0,
            "critical_issues": len(critical_issues),
            "high_issues": len(high_issues),
            "medium_issues": len(medium_issues),
            "overall_status": "healthy" if failed_checks == 0 else ("degraded" if critical_issues == 0 else "critical")
        }

        # Генерация рекомендаций
        if critical_issues:
            self.results["recommendations"].append("🚨 КРИТИЧНО: Немедленно исправьте критические проблемы")

        if high_issues:
            self.results["recommendations"].append("⚠️ Исправьте проблемы высокой важности в ближайшее время")

        if self.results["summary"]["success_rate"] < 80:
            self.results["recommendations"].append("📈 Общий уровень работоспособности ниже 80% - требуется внимание")

        # Добавляем специфичные рекомендации на основе результатов
        anthropic_check = self.results["checks"].get("Anthropic Service", {})
        if anthropic_check.get("status") == "fail" and "API key" in str(anthropic_check.get("message", "")):
            self.results["recommendations"].append("🔑 Настройте ANTHROPIC_API_KEY для использования AI функций")

        instances_check = self.results["checks"].get("Orchestrator Instances", {})
        if instances_check.get("status") == "fail":
            self.results["recommendations"].append("🖥️ Зарегистрируйте orchestrator instances для обработки задач")

    def save_report(self, filename: Optional[str] = None):
        """Сохранение отчета в файл"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"msp_inspection_report_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)

        print(f"📄 Отчет сохранен в: {filename}")
        return filename

async def main():
    """Главная функция для запуска инспектора"""
    parser = argparse.ArgumentParser(description="MSP Inspector - проверка MSP Server")
    parser.add_argument("--url", default="http://localhost:8080",
                       help="URL MSP сервера (по умолчанию: http://localhost:8080)")
    parser.add_argument("--save-report", action="store_true",
                       help="Сохранить отчет в JSON файл")
    parser.add_argument("--output", help="Имя файла для сохранения отчета")

    args = parser.parse_args()

    inspector = MSPInspector(args.url)

    try:
        results = await inspector.run_full_inspection()

        if args.save_report or args.output:
            inspector.save_report(args.output)

        # Возвращаем код выхода на основе результатов
        if results["summary"]["overall_status"] == "critical":
            sys.exit(2)  # Критические проблемы
        elif results["summary"]["overall_status"] == "degraded":
            sys.exit(1)  # Некритические проблемы
        else:
            sys.exit(0)  # Все хорошо

    except KeyboardInterrupt:
        print("\n⏹️ Инспекция прервана пользователем")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Критическая ошибка инспектора: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())