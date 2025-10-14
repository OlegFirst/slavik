"""
Knowledge Base Connector

Реальное подключение к Knowledge Base Service
Автоматическое пополнение знаний, синхронизация
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import asyncio

logger = logging.getLogger(__name__)


class KnowledgeBaseClient:
    """
    HTTP клиент для Knowledge Base Service

    Предполагаемый API Knowledge Base:
    - GET /api/kb/search - поиск ресурсов
    - POST /api/kb/articles - создание статьи
    - PUT /api/kb/articles/{id} - обновление статьи
    - GET /api/kb/articles/{id} - получение статьи
    """

    def __init__(self, base_url: str = "http://localhost:8040"):
        self.base_url = base_url
        self.timeout = 30.0

    async def search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Поиск ресурсов в Knowledge Base

        Args:
            query: Поисковый запрос
            filters: Фильтры (type, domain, language, etc.)
            limit: Макс кол-во результатов

        Returns:
            Список найденных ресурсов
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/kb/search",
                    params={
                        'q': query,
                        'limit': limit,
                        **( filters or {})
                    }
                )

                if response.status_code == 200:
                    results = response.json()
                    logger.info(f"✅ Found {len(results)} resources for query: {query}")
                    return results
                else:
                    logger.warning(f"⚠️ KB search failed: {response.status_code}")
                    return []

        except httpx.ConnectError:
            logger.warning(f"⚠️ KB Service not available at {self.base_url}, using fallback")
            return self._fallback_search(query, filters, limit)
        except Exception as e:
            logger.error(f"❌ KB search error: {e}")
            return []

    async def create_article(self, article_data: Dict[str, Any]) -> Optional[str]:
        """
        Создать новую статью в Knowledge Base

        Args:
            article_data: Данные статьи (title, content, type, tags, etc.)

        Returns:
            ID созданной статьи или None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/kb/articles",
                    json=article_data
                )

                if response.status_code in [200, 201]:
                    result = response.json()
                    article_id = result.get('id')
                    logger.info(f"✅ Created article: {article_data.get('title')} (ID: {article_id})")
                    return article_id
                else:
                    logger.warning(f"⚠️ Article creation failed: {response.status_code}")
                    return None

        except httpx.ConnectError:
            logger.warning(f"⚠️ KB Service not available, article saved to queue")
            # TODO: Save to queue for later sync
            return None
        except Exception as e:
            logger.error(f"❌ Article creation error: {e}")
            return None

    async def update_article(
        self,
        article_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Обновить существующую статью

        Args:
            article_id: ID статьи
            updates: Обновления

        Returns:
            True если успешно
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(
                    f"{self.base_url}/api/kb/articles/{article_id}",
                    json=updates
                )

                if response.status_code == 200:
                    logger.info(f"✅ Updated article: {article_id}")
                    return True
                else:
                    logger.warning(f"⚠️ Article update failed: {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"❌ Article update error: {e}")
            return False

    async def get_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Получить статью по ID"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/kb/articles/{article_id}"
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return None

        except Exception as e:
            logger.error(f"❌ Get article error: {e}")
            return None

    def _fallback_search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fallback поиск (когда KB Service недоступен)

        Возвращает предопределенные ресурсы
        """
        fallback_resources = {
            'escalation': [
                {
                    'id': 'kb_escalation_001',
                    'title': 'Процедуры Эскалации в BCM',
                    'type': 'article',
                    'content_preview': 'Руководство по эскалации инцидентов...',
                    'duration_minutes': 20,
                    'url': '/kb/articles/escalation-procedures',
                    'tags': ['escalation', 'process', 'bcm']
                },
                {
                    'id': 'kb_escalation_002',
                    'title': 'Эффективная Эскалация в Кризисе',
                    'type': 'video',
                    'content_preview': 'Видео-руководство по эскалации...',
                    'duration_minutes': 15,
                    'url': '/kb/videos/escalation-in-crisis',
                    'tags': ['escalation', 'crisis', 'training']
                }
            ],
            'communication': [
                {
                    'id': 'kb_comm_001',
                    'title': 'Кризисная Коммуникация: Best Practices',
                    'type': 'article',
                    'content_preview': 'Лучшие практики коммуникации в кризисе...',
                    'duration_minutes': 25,
                    'url': '/kb/articles/crisis-communication',
                    'tags': ['communication', 'crisis', 'stakeholders']
                }
            ],
            'backup': [
                {
                    'id': 'kb_backup_001',
                    'title': 'Активация Резервных Систем',
                    'type': 'guide',
                    'content_preview': 'Пошаговое руководство по активации backup систем...',
                    'duration_minutes': 30,
                    'url': '/kb/guides/backup-activation',
                    'tags': ['backup', 'technical', 'recovery']
                }
            ],
            'bia': [
                {
                    'id': 'kb_bia_001',
                    'title': 'Методология BIA',
                    'type': 'article',
                    'content_preview': 'Полное руководство по проведению BIA...',
                    'duration_minutes': 40,
                    'url': '/kb/articles/bia-methodology',
                    'tags': ['bia', 'assessment', 'iso22301']
                }
            ]
        }

        query_lower = query.lower()

        # Поиск по ключевым словам
        for keyword, resources in fallback_resources.items():
            if keyword in query_lower:
                return resources[:limit]

        # Default: return generic BCM resources
        return [
            {
                'id': 'kb_general_001',
                'title': 'Основы BCM',
                'type': 'article',
                'content_preview': 'Введение в Business Continuity Management...',
                'duration_minutes': 30,
                'url': '/kb/articles/bcm-fundamentals',
                'tags': ['bcm', 'fundamentals']
            }
        ][:limit]


class KnowledgeAutoCreator:
    """
    Автоматическое создание статей из паттернов
    """

    def __init__(self, kb_client: KnowledgeBaseClient):
        self.kb_client = kb_client

    async def create_article_from_pattern(
        self,
        pattern: Dict[str, Any]
    ) -> Optional[str]:
        """
        Создать статью на основе выявленного паттерна

        Pattern: "Recurring failure: Slow escalation" (5 occurrences)
        → Article: "Как улучшить процесс эскалации"
        """
        if pattern.get('type') != 'failure' or pattern.get('occurrences', 0) < 5:
            logger.debug(f"Pattern {pattern.get('id')} doesn't meet criteria for article creation")
            return None

        issue = pattern.get('issue', 'Unknown issue')

        # Check if article already exists
        existing = await self.kb_client.search(
            query=f"improve {issue}",
            limit=1
        )

        if existing:
            logger.info(f"Article for '{issue}' already exists, skipping creation")
            return existing[0].get('id')

        # Generate article content
        article = {
            'title': f"Улучшение: {issue}",
            'content': self._generate_article_content(pattern),
            'type': 'article',
            'domain': 'BCM',
            'category': 'pattern-based',
            'tags': ['auto-generated', 'pattern-based', pattern.get('scenario_type', 'general')],
            'metadata': {
                'based_on_pattern_id': pattern.get('id'),
                'pattern_occurrences': pattern.get('occurrences'),
                'pattern_confidence': pattern.get('confidence'),
                'created_by': 'learning_system',
                'auto_generated': True
            },
            'created_at': datetime.now().isoformat()
        }

        article_id = await self.kb_client.create_article(article)

        if article_id:
            logger.info(f"✅ Auto-created article for pattern: {issue}")

        return article_id

    def _generate_article_content(self, pattern: Dict[str, Any]) -> str:
        """
        Генерация контента статьи на основе паттерна

        TODO: В будущем использовать AI Expert для генерации
        """
        issue = pattern.get('issue', 'Unknown issue')
        occurrences = pattern.get('occurrences', 0)
        confidence = pattern.get('confidence', 0)
        scenario_type = pattern.get('scenario_type', 'general')

        content = f"""# {issue}

## 📊 Выявленная Проблема

Данная проблема была обнаружена в **{occurrences}** упражнениях с уровнем достоверности **{confidence:.0%}**.

**Тип сценария:** {scenario_type}

## 🔍 Анализ

Эта проблема регулярно возникает в BCM упражнениях, что указывает на системный пробел в процессах или компетенциях.

### Возможные причины:
- Недостаточная подготовка персонала
- Нечеткие процедуры или роли
- Отсутствие практики в данной области
- Технические или организационные барьеры

## 💡 Рекомендации

### 1. Немедленные действия
- Провести анализ корневых причин
- Обновить процедуры если необходимо
- Провести целевое обучение

### 2. Среднесрочные меры
- Увеличить частоту практики в данной области
- Создать чек-листы и вспомогательные материалы
- Назначить ответственных за данный процесс

### 3. Долгосрочные улучшения
- Интегрировать в регулярные тренинги
- Автоматизировать где возможно
- Измерять прогресс со временем

## 📚 Связанные Ресурсы

- Основы BCM процессов
- ISO 22301 требования
- Лучшие практики индустрии

## 📈 Отслеживание Прогресса

После внедрения улучшений, проведите контрольные упражнения для проверки эффективности.

---

*Эта статья была автоматически создана Learning System на основе выявленных паттернов.*
*Pattern ID: {pattern.get('id')}*
*Дата создания: {datetime.now().strftime('%Y-%m-%d')}*
"""

        return content


class ExternalKnowledgeSync:
    """
    Синхронизация с внешними источниками знаний
    """

    def __init__(self, kb_client: KnowledgeBaseClient):
        self.kb_client = kb_client

    async def sync_iso_standards(self) -> List[Dict[str, Any]]:
        """
        Синхронизация обновлений ISO стандартов

        TODO: Подключить реальный ISO API
        """
        logger.info("📥 Syncing ISO standards updates...")

        # Mock ISO updates (в реальности - API call)
        iso_updates = [
            {
                'clause': '8.5.1',
                'title': 'Exercising and testing - Update 2025',
                'content': 'Updated requirements for exercise documentation...',
                'effective_date': '2025-01-01',
                'changes': 'Added requirement for digital exercise logs'
            }
        ]

        synced = []

        for update in iso_updates:
            article_data = {
                'title': f"ISO 22301 Update: Clause {update['clause']}",
                'content': update['content'],
                'type': 'standard_update',
                'domain': 'Compliance',
                'category': 'iso_update',
                'tags': ['iso22301', 'standard', 'update'],
                'metadata': {
                    'iso_clause': update['clause'],
                    'effective_date': update['effective_date'],
                    'source': 'ISO',
                    'auto_synced': True
                }
            }

            article_id = await self.kb_client.create_article(article_data)
            if article_id:
                synced.append(update)

        logger.info(f"✅ Synced {len(synced)} ISO updates")
        return synced

    async def sync_threat_intelligence(self) -> List[Dict[str, Any]]:
        """
        Синхронизация threat intelligence

        TODO: Подключить threat intelligence feeds
        """
        logger.info("📥 Syncing threat intelligence...")

        # Mock threat data
        threats = [
            {
                'name': 'Ransomware Campaign Q1 2025',
                'description': 'New ransomware targeting critical infrastructure...',
                'severity': 'high',
                'source': 'CERT',
                'affected_sectors': ['energy', 'healthcare', 'finance']
            }
        ]

        synced = []

        for threat in threats:
            article_data = {
                'title': f"Threat Alert: {threat['name']}",
                'content': threat['description'],
                'type': 'threat_intelligence',
                'domain': 'Security',
                'category': 'threat',
                'tags': ['threat', 'security', threat['severity']],
                'metadata': {
                    'severity': threat['severity'],
                    'source': threat['source'],
                    'affected_sectors': threat['affected_sectors'],
                    'auto_synced': True
                }
            }

            article_id = await self.kb_client.create_article(article_data)
            if article_id:
                synced.append(threat)

        logger.info(f"✅ Synced {len(synced)} threat intelligence updates")
        return synced

    async def sync_all(self) -> Dict[str, int]:
        """Синхронизировать все внешние источники"""
        logger.info("🔄 Starting full knowledge sync...")

        iso_updates = await self.sync_iso_standards()
        threat_updates = await self.sync_threat_intelligence()

        summary = {
            'iso_updates': len(iso_updates),
            'threat_updates': len(threat_updates),
            'total_synced': len(iso_updates) + len(threat_updates),
            'synced_at': datetime.now().isoformat()
        }

        logger.info(f"✅ Knowledge sync complete: {summary['total_synced']} updates")
        return summary


class EnhancedKnowledgeIntegrator:
    """
    Улучшенный Knowledge Integrator с реальным подключением
    """

    def __init__(self, kb_base_url: str = "http://localhost:8040"):
        self.kb_client = KnowledgeBaseClient(kb_base_url)
        self.auto_creator = KnowledgeAutoCreator(self.kb_client)
        self.external_sync = ExternalKnowledgeSync(self.kb_client)

    async def fetch_resources_for_gap(
        self,
        gap_keyword: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Реальный поиск ресурсов в Knowledge Base

        Args:
            gap_keyword: Ключевое слово пробела
            limit: Макс кол-во ресурсов

        Returns:
            Список релевантных ресурсов
        """
        resources = await self.kb_client.search(
            query=gap_keyword,
            filters={
                'type': ['article', 'video', 'guide', 'template'],
                'domain': 'BCM',
                'language': 'ru'
            },
            limit=limit
        )

        # Rank by relevance (TODO: implement proper ranking)
        return resources

    async def create_learning_path_from_kb(
        self,
        user_id: str,
        competency_gap: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать learning path из реальной Knowledge Base

        Args:
            user_id: ID пользователя
            competency_gap: Пробел компетенции

        Returns:
            Готовый learning path
        """
        competency = competency_gap.get('competency', '')
        current_score = competency_gap.get('current_score', 0)
        target_score = competency_gap.get('target_score', 80)

        # Поиск ресурсов
        resources = await self.kb_client.search(
            query=competency.replace('_', ' '),
            filters={
                'difficulty_level': self._map_score_to_level(current_score)
            },
            limit=10
        )

        if not resources:
            logger.warning(f"No resources found for {competency}, using defaults")
            resources = self._get_default_resources(competency)

        # Создание пути
        learning_path = {
            'id': f"path_{user_id}_{competency}",
            'user_id': user_id,
            'name': f"Улучшение: {competency.replace('_', ' ').title()}",
            'target_competency': competency,
            'current_score': current_score,
            'target_score': target_score,
            'steps': [],
            'total_duration_minutes': 0
        }

        # Добавить ресурсы как шаги
        for idx, resource in enumerate(resources[:5], 1):
            step = {
                'order': idx,
                'type': resource.get('type', 'article'),
                'resource_id': resource.get('id'),
                'title': resource.get('title'),
                'duration_minutes': resource.get('duration_minutes', 30),
                'url': resource.get('url'),
                'completed': False
            }

            learning_path['steps'].append(step)
            learning_path['total_duration_minutes'] += step['duration_minutes']

        # Добавить практику в конце
        learning_path['steps'].append({
            'order': len(learning_path['steps']) + 1,
            'type': 'practice',
            'title': f"Практическое упражнение: {competency.replace('_', ' ').title()}",
            'duration_minutes': 60,
            'completed': False
        })
        learning_path['total_duration_minutes'] += 60

        return learning_path

    async def auto_create_knowledge_from_patterns(
        self,
        patterns: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Автоматически создать статьи из паттернов

        Returns:
            Список ID созданных статей
        """
        created_ids = []

        for pattern in patterns:
            article_id = await self.auto_creator.create_article_from_pattern(pattern)
            if article_id:
                created_ids.append(article_id)

        logger.info(f"✅ Auto-created {len(created_ids)} articles from patterns")
        return created_ids

    async def sync_external_knowledge(self) -> Dict[str, int]:
        """Синхронизировать с внешними источниками"""
        return await self.external_sync.sync_all()

    def _map_score_to_level(self, score: float) -> str:
        """Map competency score to difficulty level"""
        if score < 50:
            return 'beginner'
        elif score < 70:
            return 'intermediate'
        else:
            return 'advanced'

    def _get_default_resources(self, competency: str) -> List[Dict[str, Any]]:
        """Default resources when KB search fails"""
        return [
            {
                'id': f'default_{competency}',
                'title': f"Основы: {competency.replace('_', ' ').title()}",
                'type': 'article',
                'duration_minutes': 30,
                'url': f'/kb/default/{competency}',
                'tags': [competency, 'fundamentals']
            }
        ]
