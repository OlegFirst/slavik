"""
Compliance Engine - ISO 22301/27001 Compliance Checks

Проверяет соответствие стандартам и генерирует evidence
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceEngine:
    """
    Движок для проверки compliance (ISO 22301, ISO 27001)

    Поддерживает:
    - Compliance mapping (clauses)
    - Evidence generation
    - Retention policies
    - Review cycles
    """

    async def check_compliance(
        self,
        compliance_config: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Проверить соответствие стандартам

        Args:
            compliance_config: Конфигурация compliance из сценария
            execution_result: Результаты выполнения сценария

        Returns:
            Результаты проверки compliance
        """

        logger.info(f"  ✅ Checking compliance...")

        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'standards': {}
        }

        # ISO 22301
        if 'iso_22301' in compliance_config:
            logger.info(f"    📋 Checking ISO 22301...")
            iso22301_result = await self._check_iso_22301(
                compliance_config['iso_22301'],
                execution_result
            )
            results['standards']['iso_22301'] = iso22301_result

        # ISO 27001
        if 'iso_27001' in compliance_config:
            logger.info(f"    🔒 Checking ISO 27001...")
            iso27001_result = await self._check_iso_27001(
                compliance_config['iso_27001'],
                execution_result
            )
            results['standards']['iso_27001'] = iso27001_result

        # GDPR (если есть)
        if 'gdpr' in compliance_config:
            logger.info(f"    🇪🇺 Checking GDPR...")
            gdpr_result = await self._check_gdpr(
                compliance_config['gdpr'],
                execution_result
            )
            results['standards']['gdpr'] = gdpr_result

        return results

    async def _check_iso_22301(
        self,
        iso_config: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Проверить ISO 22301 compliance
        """

        result = {
            'clauses': [],
            'evidence': [],
            'retention': None,
            'review_cycle': None
        }

        # Проверить clauses
        for clause in iso_config.get('clauses', []):
            clause_result = await self._check_clause(clause, execution_result)
            result['clauses'].append(clause_result)

        # Сгенерировать evidence
        for evidence_config in iso_config.get('evidence_generated', []):
            evidence = await self._generate_evidence(
                evidence_config,
                execution_result
            )
            result['evidence'].append(evidence)

        # Retention policy
        result['retention'] = await self._apply_retention(
            iso_config.get('evidence_generated', [])
        )

        # Review cycle
        if 'review_cycle' in iso_config:
            result['review_cycle'] = iso_config['review_cycle']

        return result

    async def _check_iso_27001(
        self,
        iso_config: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Проверить ISO 27001 compliance
        """

        result = {
            'controls': []
        }

        # Проверить controls
        for control in iso_config.get('controls', []):
            control_result = await self._check_control(control, execution_result)
            result['controls'].append(control_result)

        return result

    async def _check_gdpr(
        self,
        gdpr_config: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Проверить GDPR compliance
        """

        result = {
            'articles': []
        }

        # Проверить articles
        for article in gdpr_config.get('articles', []):
            article_result = await self._check_article(article, execution_result)
            result['articles'].append(article_result)

        return result

    async def _check_clause(
        self,
        clause: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Проверить конкретную clause ISO 22301
        """

        clause_id = clause.get('id')
        clause_name = clause.get('name', '')
        requirement = clause.get('requirement', '')
        how_met = clause.get('how_met', '')

        logger.info(f"      📋 Clause {clause_id}: {clause_name}")

        # Проверить выполнение (упрощенно)
        # В production - сложная логика проверки
        compliance_status = 'compliant'  # Mock

        return {
            'id': clause_id,
            'name': clause_name,
            'requirement': requirement,
            'how_met': how_met,
            'status': compliance_status,
            'checked_at': datetime.utcnow().isoformat()
        }

    async def _check_control(
        self,
        control: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Проверить control ISO 27001
        """

        control_id = control.get('id')
        control_name = control.get('name', '')
        status = control.get('status', 'unknown')
        evidence = control.get('evidence', [])

        logger.info(f"      🔒 Control {control_id}: {control_name}")

        # Проверить evidence
        evidence_found = self._check_evidence_exists(evidence, execution_result)

        return {
            'id': control_id,
            'name': control_name,
            'status': status,
            'evidence': evidence,
            'evidence_found': evidence_found,
            'checked_at': datetime.utcnow().isoformat()
        }

    async def _check_article(
        self,
        article: str,
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Проверить article GDPR
        """

        logger.info(f"      🇪🇺 Article: {article}")

        return {
            'article': article,
            'compliant': True,  # Mock
            'checked_at': datetime.utcnow().isoformat()
        }

    async def _generate_evidence(
        self,
        evidence_config: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Сгенерировать evidence для аудита
        """

        evidence_type = evidence_config.get('type')
        evidence_format = evidence_config.get('format')
        storage = evidence_config.get('storage')
        retention = evidence_config.get('retention')

        logger.info(f"      📄 Generating evidence: {evidence_type} ({evidence_format})")

        # Извлечь данные для evidence
        evidence_data = self._extract_evidence_data(
            evidence_config,
            execution_result
        )

        # Вычислить дату удаления
        retention_until = self._calculate_retention_date(retention)

        evidence = {
            'type': evidence_type,
            'format': evidence_format,
            'generated_at': datetime.utcnow().isoformat(),
            'data': evidence_data,
            'storage': storage,
            'retention': retention,
            'retention_until': retention_until,
            'status': 'generated'
        }

        # Сохранить evidence (симуляция)
        await self._store_evidence(evidence)

        return evidence

    def _extract_evidence_data(
        self,
        evidence_config: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Извлечь данные для evidence из результата выполнения
        """

        includes = evidence_config.get('includes', [])
        data = {}

        for field in includes:
            # Извлечь из execution_result
            value = self._get_field_from_result(field, execution_result)
            if value:
                data[field] = value

        return data

    def _get_field_from_result(
        self,
        field: str,
        result: Dict[str, Any]
    ) -> Any:
        """Получить поле из result"""

        # Упрощенная версия
        return result.get(field, f"mock_{field}")

    def _calculate_retention_date(self, retention_str: str) -> str:
        """
        Вычислить дату до которой хранить evidence

        Args:
            retention_str: "7 years", "3 years", "90 days"
        """

        if not retention_str:
            return None

        # Parse retention string
        parts = retention_str.split()
        if len(parts) != 2:
            return None

        amount = int(parts[0])
        unit = parts[1].lower()

        if 'year' in unit:
            delta = timedelta(days=amount * 365)
        elif 'month' in unit:
            delta = timedelta(days=amount * 30)
        elif 'day' in unit:
            delta = timedelta(days=amount)
        else:
            delta = timedelta(days=365 * 7)  # default 7 years

        retention_date = datetime.utcnow() + delta

        return retention_date.isoformat()

    async def _store_evidence(self, evidence: Dict[str, Any]):
        """
        Сохранить evidence в compliance archive

        В production - сохранение в S3, database, etc.
        """

        logger.info(f"        💾 Storing evidence: {evidence['type']}")
        # Mock storage

    def _check_evidence_exists(
        self,
        evidence_list: List[str],
        execution_result: Dict[str, Any]
    ) -> bool:
        """
        Проверить наличие evidence в результате выполнения
        """

        # Упрощенная проверка
        for evidence_item in evidence_list:
            if evidence_item not in str(execution_result):
                return False

        return True

    async def _apply_retention(
        self,
        evidence_configs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Применить retention policies
        """

        retention_info = {
            'policies': [],
            'applied_at': datetime.utcnow().isoformat()
        }

        for config in evidence_configs:
            retention = config.get('retention')
            if retention:
                retention_info['policies'].append({
                    'type': config.get('type'),
                    'retention': retention,
                    'retention_until': self._calculate_retention_date(retention)
                })

        return retention_info
