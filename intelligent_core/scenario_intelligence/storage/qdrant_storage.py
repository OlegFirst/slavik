"""
Qdrant Storage для Scenario Intelligence

Semantic search по сценариям используя vector embeddings.
Интеграция с Qdrant для быстрого similarity search.
"""

import logging
from typing import Dict, Any, List, Optional
import hashlib

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
except ImportError:
    QdrantClient = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QdrantScenarioStorage:
    """
    Qdrant Storage для semantic search по сценариям

    Features:
    - Автоматическая генерация embeddings
    - Similarity search
    - Фильтрация по метаданным (level, type, module)
    - Batch operations
    """

    def __init__(
        self,
        collection_name: str = "scenarios",
        qdrant_url: str = "localhost",
        qdrant_port: int = 6333,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize Qdrant storage

        Args:
            collection_name: Имя коллекции в Qdrant
            qdrant_url: URL Qdrant сервера
            qdrant_port: Порт Qdrant
            embedding_model: Модель для embeddings (sentence-transformers)
        """
        if QdrantClient is None:
            raise ImportError("qdrant-client is required: pip install qdrant-client")

        if SentenceTransformer is None:
            raise ImportError("sentence-transformers is required: pip install sentence-transformers")

        self.collection_name = collection_name
        self.client = QdrantClient(host=qdrant_url, port=qdrant_port)

        # Загрузить embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.encoder = SentenceTransformer(embedding_model)
        self.vector_size = self.encoder.get_sentence_embedding_dimension()

        logger.info(f" Qdrant client initialized (collection: {collection_name}, vector_size: {self.vector_size})")

    async def initialize(self):
        """Создать коллекцию если не существует"""
        try:
            # Проверить существует ли коллекция
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                # Создать коллекцию
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f" Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f" Qdrant collection exists: {self.collection_name}")

        except Exception as e:
            logger.error(f" Failed to initialize Qdrant collection: {e}")
            raise

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Генерировать embedding для текста

        Args:
            text: Текст для embedding

        Returns:
            Vector embedding
        """
        return self.encoder.encode(text).tolist()

    def _scenario_to_text(self, scenario: Dict[str, Any]) -> str:
        """
        Конвертировать сценарий в текст для embedding

        Args:
            scenario: Сценарий

        Returns:
            Текстовое представление
        """
        # Handle both formats
        if 'scenario' in scenario:
            scenario = scenario['scenario']

        meta = scenario.get('meta', {})
        description_obj = scenario.get('description', {})

        # Собрать текст из ключевых полей
        parts = []

        # Title
        title = description_obj.get('title', meta.get('id', ''))
        if title:
            parts.append(f"Title: {title}")

        # Summary
        summary = description_obj.get('summary', '')
        if summary:
            parts.append(f"Summary: {summary}")

        # Context
        context = description_obj.get('context', '')
        if context:
            parts.append(f"Context: {context}")

        # Goal
        goal = description_obj.get('goal', '')
        if goal:
            parts.append(f"Goal: {goal}")

        # Type
        scenario_type = meta.get('type', '')
        if scenario_type:
            parts.append(f"Type: {scenario_type}")

        # Module
        ownership = scenario.get('ownership', {})
        module = ownership.get('module', '')
        if module:
            parts.append(f"Module: {module}")

        return " | ".join(parts)

    def _scenario_to_payload(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Конвертировать сценарий в Qdrant payload (metadata)

        Args:
            scenario: Сценарий

        Returns:
            Payload для Qdrant
        """
        # Handle both formats
        if 'scenario' in scenario:
            scenario = scenario['scenario']

        meta = scenario.get('meta', {})
        ownership = scenario.get('ownership', {})
        description_obj = scenario.get('description', {})

        return {
            'id': meta.get('id'),
            'level': meta.get('level'),
            'type': meta.get('type'),
            'module': ownership.get('module'),
            'service': ownership.get('service'),
            'subsystem': ownership.get('subsystem'),
            'title': description_obj.get('title', ''),
            'summary': description_obj.get('summary', ''),
        }

    def _id_to_point_id(self, scenario_id: str) -> int:
        """
        Конвертировать scenario ID в Qdrant point ID (integer)

        Args:
            scenario_id: String ID

        Returns:
            Integer hash
        """
        # Использовать hash для получения integer ID
        return int(hashlib.md5(scenario_id.encode()).hexdigest()[:8], 16)

    async def register(self, scenario: Dict[str, Any]) -> bool:
        """
        Сохранить сценарий в Qdrant

        Args:
            scenario: Сценарий

        Returns:
            True если успешно
        """
        # Handle both formats
        if 'scenario' in scenario:
            scenario = scenario['scenario']

        meta = scenario.get('meta', {})
        scenario_id = meta.get('id')

        if not scenario_id:
            logger.error("Scenario без ID")
            return False

        try:
            # Генерировать embedding
            text = self._scenario_to_text(scenario)
            vector = self._generate_embedding(text)

            # Подготовить payload
            payload = self._scenario_to_payload(scenario)

            # Добавить полный сценарий в payload (для возврата при поиске)
            payload['full_scenario'] = scenario

            # Создать point
            point_id = self._id_to_point_id(scenario_id)
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )

            # Upsert (insert or update)
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )

            logger.info(f" Qdrant: indexed scenario {scenario_id} (point_id: {point_id})")
            return True

        except Exception as e:
            logger.error(f" Failed to index scenario {scenario_id} in Qdrant: {e}")
            return False

    async def search(
        self,
        query: str,
        level: Optional[int] = None,
        type: Optional[str] = None,
        module: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Semantic search по сценариям

        Args:
            query: Поисковый запрос (естественный язык)
            level: Фильтр по уровню
            type: Фильтр по типу
            module: Фильтр по модулю
            limit: Максимум результатов

        Returns:
            Список сценариев, отсортированных по similarity
        """
        try:
            # Генерировать embedding для запроса
            query_vector = self._generate_embedding(query)

            # Построить фильтр
            filter_conditions = []

            if level is not None:
                filter_conditions.append(
                    FieldCondition(key="level", match=MatchValue(value=level))
                )

            if type:
                filter_conditions.append(
                    FieldCondition(key="type", match=MatchValue(value=type))
                )

            if module:
                filter_conditions.append(
                    FieldCondition(key="module", match=MatchValue(value=module))
                )

            query_filter = Filter(must=filter_conditions) if filter_conditions else None

            # Поиск
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True
            )

            # Извлечь сценарии из payload
            scenarios = []
            for result in results:
                payload = result.payload
                full_scenario = payload.get('full_scenario')
                if full_scenario:
                    # Добавить score для отладки
                    full_scenario['_search_score'] = result.score
                    scenarios.append(full_scenario)

            logger.info(f" Qdrant search: found {len(scenarios)} scenarios for query '{query}'")
            return scenarios

        except Exception as e:
            logger.error(f" Failed to search in Qdrant: {e}")
            return []

    async def get_scenario_by_id(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить сценарий по ID

        Args:
            scenario_id: ID сценария

        Returns:
            Сценарий или None
        """
        try:
            point_id = self._id_to_point_id(scenario_id)

            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id],
                with_payload=True
            )

            if result and len(result) > 0:
                payload = result[0].payload
                return payload.get('full_scenario')
            else:
                return None

        except Exception as e:
            logger.error(f" Failed to get scenario {scenario_id} from Qdrant: {e}")
            return None

    async def delete_scenario(self, scenario_id: str) -> bool:
        """
        Удалить сценарий из Qdrant

        Args:
            scenario_id: ID сценария

        Returns:
            True если успешно
        """
        try:
            point_id = self._id_to_point_id(scenario_id)

            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id]
            )

            logger.info(f" Deleted scenario {scenario_id} from Qdrant")
            return True

        except Exception as e:
            logger.error(f" Failed to delete scenario {scenario_id} from Qdrant: {e}")
            return False

    async def bulk_register(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Массовое добавление сценариев

        Args:
            scenarios: Список сценариев

        Returns:
            {'success': count, 'failed': count}
        """
        success_count = 0
        failed_count = 0
        points = []

        for scenario in scenarios:
            try:
                # Handle both formats
                if 'scenario' in scenario:
                    scenario = scenario['scenario']

                meta = scenario.get('meta', {})
                scenario_id = meta.get('id')

                if not scenario_id:
                    failed_count += 1
                    continue

                # Генерировать embedding
                text = self._scenario_to_text(scenario)
                vector = self._generate_embedding(text)

                # Подготовить payload
                payload = self._scenario_to_payload(scenario)
                payload['full_scenario'] = scenario

                # Создать point
                point_id = self._id_to_point_id(scenario_id)
                point = PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )

                points.append(point)
                success_count += 1

            except Exception as e:
                logger.error(f" Failed to prepare scenario for Qdrant: {e}")
                failed_count += 1

        # Batch upsert
        if points:
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                logger.info(f" Qdrant bulk register: {success_count} scenarios indexed")
            except Exception as e:
                logger.error(f" Failed bulk upsert to Qdrant: {e}")
                return {'success': 0, 'failed': len(scenarios)}

        return {
            'success': success_count,
            'failed': failed_count
        }

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику по Qdrant коллекции

        Returns:
            Статистика
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)

            return {
                'total_scenarios': collection_info.points_count,
                'vector_size': collection_info.config.params.vectors.size,
                'distance': collection_info.config.params.vectors.distance,
            }

        except Exception as e:
            logger.error(f" Failed to get Qdrant statistics: {e}")
            return {}


# Test
async def main():
    """Test Qdrant Storage"""

    storage = QdrantScenarioStorage(
        collection_name="scenarios_test",
        qdrant_url="localhost",
        qdrant_port=6333
    )

    try:
        await storage.initialize()

        # Тестовые сценарии
        test_scenarios = [
            {
                'meta': {
                    'id': 'test-vault-store-qdrant',
                    'level': 1,
                    'type': 'functional'
                },
                'ownership': {
                    'module': 'vault'
                },
                'description': {
                    'title': 'Vault Store Scenario',
                    'summary': 'Testing secure secret storage in vault',
                    'context': 'Secrets management for production environment'
                }
            },
            {
                'meta': {
                    'id': 'test-bia-creation-qdrant',
                    'level': 1,
                    'type': 'business_process'
                },
                'ownership': {
                    'module': 'bia'
                },
                'description': {
                    'title': 'BIA Creation Workflow',
                    'summary': 'Creating Business Impact Analysis document',
                    'context': 'BCM specialist creates BIA for critical business process'
                }
            }
        ]

        # Bulk register
        result = await storage.bulk_register(test_scenarios)
        print(f"\n Bulk register: {result}")

        # Semantic search
        scenarios = await storage.search("how to store secrets securely?", limit=5)
        print(f"\n Semantic search (secrets): {len(scenarios)} scenarios found")
        for s in scenarios:
            print(f"  - {s['meta']['id']}: {s['description']['title']} (score: {s.get('_search_score', 0):.4f})")

        # Search with filters
        scenarios = await storage.search("business process", level=1, limit=5)
        print(f"\n Semantic search (business + level=1): {len(scenarios)} scenarios found")
        for s in scenarios:
            print(f"  - {s['meta']['id']}: {s['description']['title']} (score: {s.get('_search_score', 0):.4f})")

        # Get by ID
        scenario = await storage.get_scenario_by_id('test-vault-store-qdrant')
        if scenario:
            print(f"\n Get by ID: {scenario['meta']['id']}")

        # Statistics
        stats = await storage.get_statistics()
        print(f"\n Statistics: {stats}")

        # Clean up
        # await storage.delete_scenario('test-vault-store-qdrant')
        # await storage.delete_scenario('test-bia-creation-qdrant')

    except Exception as e:
        logger.error(f" Test failed: {e}")
        raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
