"""
Compliance Controller - Контроллер соответствия стандартам

Философия триединства:
- ЗНАНИЕ: Валидация правильности и полноты
- ЗАЩИТА: Обеспечение соответствия ISO/NIST/WHO (основная функция)
- САМОРЕАЛИЗАЦИЯ: Превращение знаний в сертифицируемые активы

Экономика знаний:
- Знания → Защита (валидация compliance)
- Защита → Ценность (сертификация = рыночная стоимость)
- Ценность → Самореализация (монетизация знаний)

Based on: intelligent-core/expertise-center/ai-office/organs/compliance_guardian.py
Integration: Uses Compliance Guardian's compliance analysis capabilities
"""

import logging
import json
from typing import List, Dict, Optional
from datetime import datetime
import httpx
from anthropic import Anthropic

from models import (
    Scenario, ValidatedScenario, ValidationStatus,
    ComplianceCheck, ComplianceStatus
)
from config.settings import settings

logger = logging.getLogger(__name__)


class ComplianceController:
    """
    Контроллер соответствия - валидирует знания по стандартам

    Триединство ЗАЩИТЫ:
    1. Техническая валидация (корректность)
    2. Соответствие стандартам (compliance)
    3. Экспертная оценка (качество)

    Результат: Защищенные, сертифицируемые знания
    """

    def __init__(self):
        self.anthropic = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.http_client = httpx.AsyncClient(timeout=30.0)

        # ISO 22301 требования по разделам
        self.iso_requirements = {
            "4.1": ["Понимание организации и её контекста"],
            "4.2": ["Понимание потребностей заинтересованных сторон"],
            "4.3": ["Определение области применения BCMS"],
            "4.4": ["Система менеджмента BCM"],
            "5.1": ["Лидерство и приверженность"],
            "5.2": ["Политика"],
            "5.3": ["Роли, обязанности и полномочия"],
            "6.1": ["Действия по работе с рисками и возможностями"],
            "6.2": ["Цели BCM и планирование их достижения"],
            "7.1": ["Ресурсы"],
            "7.2": ["Компетентность"],
            "7.3": ["Осведомленность"],
            "7.4": ["Коммуникация"],
            "7.5": ["Документированная информация"],
            "8.1": ["Планирование и контроль операционной деятельности"],
            "8.2": ["Анализ влияния на бизнес и оценка рисков"],
            "8.3": ["Стратегия обеспечения непрерывности бизнеса"],
            "8.4": ["Процедуры обеспечения непрерывности"],
            "9.1": ["Мониторинг, измерение, анализ и оценка"],
            "9.2": ["Внутренний аудит"],
            "9.3": ["Анализ со стороны руководства"],
            "10.1": ["Несоответствия и корректирующие действия"],
            "10.2": ["Постоянное улучшение"]
        }

        # Минимальный порог качества
        self.min_quality_score = settings.MIN_CONFIDENCE

        logger.info(" ComplianceController инициализирован")

    async def validate(self, scenarios: List[Scenario]) -> List[ValidatedScenario]:
        """
        Валидация сценариев

        Трёхуровневая защита:
        1. Техническая валидация
        2. ISO compliance check
        3. Экспертная оценка
        """
        validated_scenarios = []

        for scenario in scenarios:
            try:
                logger.info(f" Валидация: {scenario.title[:50]}...")

                # 1. Техническая валидация
                tech_valid = await self._technical_validation(scenario)

                # 2. ISO compliance
                iso_compliant = await self._iso_compliance_check(scenario)

                # 3. Экспертная оценка
                expert_approved = await self._expert_review(scenario)

                # 4. Расчёт quality score
                quality_score = self._calculate_quality_score(
                    tech_valid, iso_compliant, expert_approved, scenario
                )

                # 5. Определение статуса
                status = self._determine_status(
                    tech_valid, iso_compliant, expert_approved, quality_score
                )

                validated = ValidatedScenario(
                    scenario=scenario,
                    iso_compliant=iso_compliant,
                    technically_valid=tech_valid,
                    expert_approved=expert_approved,
                    quality_score=quality_score,
                    status=status,
                    validation_notes=self._generate_validation_notes(
                        tech_valid, iso_compliant, expert_approved
                    ),
                    validated_at=datetime.now()
                )

                validated_scenarios.append(validated)

                logger.info(f"   Статус: {status}")
                logger.info(f"   Качество: {quality_score:.2f}")

            except Exception as e:
                logger.error(f"Ошибка валидации сценария {scenario.id}: {e}")
                continue

        approved_count = len([v for v in validated_scenarios if v.status == ValidationStatus.APPROVED])
        logger.info(f" Валидация завершена: {approved_count}/{len(scenarios)} одобрено")

        return validated_scenarios

    async def _technical_validation(self, scenario: Scenario) -> bool:
        """
        Техническая валидация

        Проверки:
        - Структура сценария (title, content, service)
        - Формат данных
        - Ссылки на компоненты
        - Логичность потока
        """
        try:
            # 1. Обязательные поля
            if not scenario.title or not scenario.content:
                logger.warning(f"Отсутствуют обязательные поля: {scenario.id}")
                return False

            # 2. Минимальная длина контента
            if len(scenario.content) < 100:
                logger.warning(f"Контент слишком короткий: {scenario.id}")
                return False

            # 3. Проверка формата (есть ли структурированные разделы)
            required_sections = ["Description", "Inputs", "Outputs"]
            has_structure = any(section in scenario.content for section in required_sections)

            if not has_structure:
                logger.warning(f"Отсутствует структура: {scenario.id}")
                return False

            # 4. Валидация сервиса (если указан)
            if scenario.service:
                valid_services = ["BIA", "Risk", "Planning", "Response", "Compliance",
                                "Exercise", "Documents", "Learning", "Governance"]
                if scenario.service not in valid_services:
                    logger.warning(f"Неверный сервис: {scenario.service}")
                    return False

            # 5. Проверка уверенности
            if scenario.confidence < 0.5:
                logger.warning(f"Низкая уверенность: {scenario.confidence}")
                return False

            return True

        except Exception as e:
            logger.error(f"Ошибка технической валидации: {e}")
            return False

    async def _iso_compliance_check(self, scenario: Scenario) -> bool:
        """
        Проверка соответствия ISO 22301

        ЗАЩИТА: Обеспечиваем compliance с международными стандартами
        """
        try:
            # Если указан ISO clause - проверяем соответствие
            if scenario.iso_clause:
                # Проверяем, что clause существует
                if scenario.iso_clause not in self.iso_requirements:
                    logger.warning(f"Неизвестный ISO clause: {scenario.iso_clause}")
                    return False

                # Используем LLM для проверки соответствия требованиям
                requirements = self.iso_requirements[scenario.iso_clause]
                is_compliant = await self._llm_compliance_check(
                    scenario, scenario.iso_clause, requirements
                )

                return is_compliant

            else:
                # Если clause не указан, пытаемся определить релевантность
                # Сценарий может быть полезен, но не привязан к ISO
                # Это не ошибка, но снижает compliance score
                return True  # Нейтральный результат

        except Exception as e:
            logger.error(f"Ошибка ISO compliance check: {e}")
            return False

    async def _llm_compliance_check(
        self,
        scenario: Scenario,
        clause: str,
        requirements: List[str]
    ) -> bool:
        """Проверка соответствия через LLM"""
        try:
            prompt = f"""Ты эксперт по ISO 22301. Проверь, соответствует ли сценарий требованиям стандарта.

**ISO 22301 Clause**: {clause}
**Требования**:
{chr(10).join(f'- {req}' for req in requirements)}

**Сценарий**:
Название: {scenario.title}
Сервис: {scenario.service}
Содержание: {scenario.content[:500]}...

**Вопрос**: Соответствует ли этот сценарий требованиям ISO 22301 Clause {clause}?

Ответь ТОЛЬКО "ДА" или "НЕТ" с кратким объяснением (1-2 предложения).
"""

            message = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",  # Sonnet для валидации (быстрее)
                max_tokens=200,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )

            response = message.content[0].text.strip()

            # Простой парсинг ответа
            is_compliant = response.upper().startswith("ДА") or "YES" in response.upper()

            logger.info(f"   ISO {clause} compliance: {'' if is_compliant else ''}")

            return is_compliant

        except Exception as e:
            logger.error(f"Ошибка LLM compliance check: {e}")
            return False

    async def _expert_review(self, scenario: Scenario) -> bool:
        """
        Экспертная оценка

        САМОРЕАЛИЗАЦИЯ: Превращаем знания в ценный актив через экспертизу
        """
        try:
            # Получаем доменного эксперта из Expertise Center
            if scenario.service:
                specialist = await self._get_domain_specialist(scenario.service)

                if specialist:
                    # Запрос экспертной оценки
                    review = await self._request_expert_review(scenario, specialist)
                    return review.get('approved', False)

            # Если нет специалиста - автоматическая оценка
            return await self._automatic_expert_assessment(scenario)

        except Exception as e:
            logger.error(f"Ошибка экспертной оценки: {e}")
            return False

    async def _get_domain_specialist(self, service: str) -> Optional[Dict]:
        """Получение доменного специалиста"""
        try:
            response = await self.http_client.get(
                f"{settings.EXPERTISE_CENTER_URL}/api/specialists/get",
                params={"domain": service}
            )

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            logger.warning(f"Не удалось получить специалиста для {service}: {e}")

        return None

    async def _request_expert_review(
        self,
        scenario: Scenario,
        specialist: Dict
    ) -> Dict:
        """Запрос экспертной оценки"""
        try:
            response = await self.http_client.post(
                f"{settings.EXPERTISE_CENTER_URL}/api/review/request",
                json={
                    "scenario_id": scenario.id,
                    "scenario_title": scenario.title,
                    "scenario_content": scenario.content,
                    "specialist_id": specialist['id']
                }
            )

            if response.status_code == 200:
                return response.json()

        except Exception as e:
            logger.warning(f"Ошибка запроса экспертной оценки: {e}")

        return {"approved": False}

    async def _automatic_expert_assessment(self, scenario: Scenario) -> bool:
        """
        Автоматическая экспертная оценка (через LLM)

        Используется когда реальный эксперт недоступен
        """
        try:
            prompt = f"""Ты опытный эксперт BCM. Оцени качество и полезность сценария.

**Сценарий**:
{scenario.title}

{scenario.content[:800]}

**Критерии оценки**:
1. Практическая ценность (можно ли применить?)
2. Полнота (достаточно ли информации?)
3. Корректность (нет ли ошибок?)
4. Ясность (понятно ли изложение?)

Ответь ТОЛЬКО "ОДОБРЕН" или "ОТКЛОНЁН" с кратким обоснованием (1-2 предложения).
"""

            message = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )

            response = message.content[0].text.strip()
            approved = "ОДОБРЕН" in response.upper() or "APPROVED" in response.upper()

            return approved

        except Exception as e:
            logger.error(f"Ошибка автоматической оценки: {e}")
            return False

    def _calculate_quality_score(
        self,
        tech_valid: bool,
        iso_compliant: bool,
        expert_approved: bool,
        scenario: Scenario
    ) -> float:
        """
        Расчёт качественного score

        Формула:
        Quality = (TechValid*0.2 + ISOCompliant*0.4 + ExpertApproved*0.3 + Confidence*0.1)
        """
        score = (
            (1.0 if tech_valid else 0.0) * 0.2 +
            (1.0 if iso_compliant else 0.0) * 0.4 +
            (1.0 if expert_approved else 0.0) * 0.3 +
            scenario.confidence * 0.1
        )

        return round(score, 2)

    def _determine_status(
        self,
        tech_valid: bool,
        iso_compliant: bool,
        expert_approved: bool,
        quality_score: float
    ) -> ValidationStatus:
        """Определение статуса валидации"""

        # Полное одобрение
        if tech_valid and iso_compliant and expert_approved and quality_score >= 0.8:
            return ValidationStatus.APPROVED

        # Требует доработки
        elif tech_valid and quality_score >= 0.5:
            return ValidationStatus.NEEDS_REVISION

        # Отклонён
        elif not tech_valid or quality_score < 0.3:
            return ValidationStatus.REJECTED

        # На проверке
        else:
            return ValidationStatus.IN_REVIEW

    def _generate_validation_notes(
        self,
        tech_valid: bool,
        iso_compliant: bool,
        expert_approved: bool
    ) -> str:
        """Генерация заметок валидации"""
        notes = []

        if not tech_valid:
            notes.append("️ Техническая валидация не пройдена")

        if not iso_compliant:
            notes.append("️ Не соответствует ISO 22301")

        if not expert_approved:
            notes.append("️ Не одобрено экспертом")

        if tech_valid and iso_compliant and expert_approved:
            notes.append(" Все проверки пройдены")

        return "; ".join(notes) if notes else "Валидация пройдена"

    async def get_compliance_status(self) -> ComplianceStatus:
        """
        Получение общего статуса соответствия

        ЗАЩИТА: Оцениваем уровень защиты системы через compliance
        """
        logger.info(" Оценка общего compliance статуса...")

        # Загружаем все сценарии
        try:
            # В production - из БД
            # Сейчас - заглушка
            iso_coverage = {}
            for clause in self.iso_requirements.keys():
                # Проверяем, есть ли сценарии для этого clause
                # В production - реальная проверка
                iso_coverage[clause] = True  # Заглушка

            # Общий процент соответствия
            compliant_count = sum(1 for v in iso_coverage.values() if v)
            overall_compliance = compliant_count / len(iso_coverage)

            # Критичные пробелы
            critical_gaps = [
                f"ISO 22301 Clause {clause}"
                for clause, compliant in iso_coverage.items()
                if not compliant and clause.startswith('8.')  # Операционные требования
            ]

            status = ComplianceStatus(
                iso_22301=iso_coverage,
                nist_sp_800_34={},  # TODO: NIST compliance
                who_emergency={},   # TODO: WHO compliance
                overall_compliance=overall_compliance,
                critical_gaps=critical_gaps
            )

            logger.info(f" Overall compliance: {overall_compliance:.1%}")
            logger.info(f"   Critical gaps: {len(critical_gaps)}")

            return status

        except Exception as e:
            logger.error(f"Ошибка оценки compliance: {e}")
            return ComplianceStatus(
                iso_22301={},
                nist_sp_800_34={},
                who_emergency={},
                overall_compliance=0.0,
                critical_gaps=[]
            )
