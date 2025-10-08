"""
🔍 Vector Indexer - Semantic Search for Knowledge Base

Indexes standards and cases into Qdrant vector database for semantic search.

Architecture:
- Embeds text using OpenAI/local embeddings
- Stores in Qdrant collections (standards, cases)
- Supports similarity search, hybrid search
- Multi-tenant isolation via tenant_id metadata
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import logging
import asyncio
import hashlib

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance, VectorParams, PointStruct,
        Filter, FieldCondition, MatchValue,
        SearchParams
    )
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("Qdrant client not available. Install with: pip install qdrant-client")

logger = logging.getLogger(__name__)


# ============================================================================
# EMBEDDING PROVIDER
# ============================================================================

class EmbeddingProvider:
    """
    Embedding provider with fallback support

    Tries:
    1. OpenAI embeddings (if API key available)
    2. Local sentence-transformers (if available)
    3. Simple TF-IDF fallback
    """

    def __init__(self, provider: str = "auto"):
        """
        Args:
            provider: "openai", "local", "tfidf", or "auto" (tries in order)
        """
        self.provider = provider
        self.embedding_dim = None
        self._client = None
        self._model = None

        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize embedding provider"""

        if self.provider in ["auto", "openai"]:
            try:
                import openai
                import os

                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self._client = openai.OpenAI(api_key=api_key)
                    self.provider = "openai"
                    self.embedding_dim = 1536  # text-embedding-3-small
                    logger.info("✅ Using OpenAI embeddings (dim=1536)")
                    return
            except ImportError:
                pass

        if self.provider in ["auto", "local"]:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer('all-MiniLM-L6-v2')
                self.provider = "local"
                self.embedding_dim = 384
                logger.info("✅ Using local embeddings: all-MiniLM-L6-v2 (dim=384)")
                return
            except ImportError:
                pass

        # Fallback to TF-IDF
        from sklearn.feature_extraction.text import TfidfVectorizer

        self._model = TfidfVectorizer(max_features=384)
        self.provider = "tfidf"
        self.embedding_dim = 384
        logger.warning("⚠️ Using TF-IDF fallback (dim=384). Install sentence-transformers for better results.")

    async def embed(self, text: str) -> List[float]:
        """Generate embedding for text"""

        if self.provider == "openai":
            return await self._embed_openai(text)
        elif self.provider == "local":
            return await self._embed_local(text)
        else:
            return await self._embed_tfidf(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts"""

        if self.provider == "openai":
            return await self._embed_batch_openai(texts)
        elif self.provider == "local":
            return await self._embed_batch_local(texts)
        else:
            return await self._embed_batch_tfidf(texts)

    async def _embed_openai(self, text: str) -> List[float]:
        """OpenAI embeddings"""
        response = await asyncio.to_thread(
            self._client.embeddings.create,
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    async def _embed_batch_openai(self, texts: List[str]) -> List[List[float]]:
        """OpenAI batch embeddings"""
        response = await asyncio.to_thread(
            self._client.embeddings.create,
            model="text-embedding-3-small",
            input=texts
        )
        return [item.embedding for item in response.data]

    async def _embed_local(self, text: str) -> List[float]:
        """Local sentence-transformers embeddings"""
        embedding = await asyncio.to_thread(
            self._model.encode,
            text,
            convert_to_numpy=True
        )
        return embedding.tolist()

    async def _embed_batch_local(self, texts: List[str]) -> List[List[float]]:
        """Local batch embeddings"""
        embeddings = await asyncio.to_thread(
            self._model.encode,
            texts,
            convert_to_numpy=True
        )
        return embeddings.tolist()

    async def _embed_tfidf(self, text: str) -> List[float]:
        """TF-IDF fallback"""
        # For single text, use the model if it's fitted
        if hasattr(self._model, 'vocabulary_'):
            vec = self._model.transform([text])
            # Pad or truncate to 384
            dense = vec.toarray()[0]
            if len(dense) < 384:
                dense = list(dense) + [0.0] * (384 - len(dense))
            else:
                dense = dense[:384]
            return dense
        else:
            # Return zero vector if not fitted
            return [0.0] * 384

    async def _embed_batch_tfidf(self, texts: List[str]) -> List[List[float]]:
        """TF-IDF batch"""
        # Fit on batch
        vecs = self._model.fit_transform(texts)
        dense = vecs.toarray()

        # Pad or truncate to 384
        result = []
        for vec in dense:
            if len(vec) < 384:
                vec = list(vec) + [0.0] * (384 - len(vec))
            else:
                vec = vec[:384]
            result.append(vec)

        return result


# ============================================================================
# VECTOR INDEXER
# ============================================================================

class VectorIndexer:
    """
    Vector indexer for knowledge base

    Collections:
    - knowledge_standards: ISO/BCI/WHO standards
    - knowledge_cases: Workflow cases
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        embedding_provider: str = "auto",
        tenant_id: str = "default"
    ):
        """
        Args:
            qdrant_url: Qdrant server URL
            embedding_provider: "auto", "openai", "local", or "tfidf"
            tenant_id: Tenant ID for multi-tenancy
        """
        if not QDRANT_AVAILABLE:
            raise ImportError("Qdrant client not available. Install: pip install qdrant-client")

        self.qdrant_url = qdrant_url
        self.tenant_id = tenant_id

        # Initialize Qdrant client
        self.client = QdrantClient(url=qdrant_url)

        # Initialize embedding provider
        self.embedder = EmbeddingProvider(provider=embedding_provider)

        # Collection names
        self.standards_collection = "knowledge_standards"
        self.cases_collection = "knowledge_cases"

        logger.info(
            f"VectorIndexer initialized (qdrant={qdrant_url}, "
            f"embedder={self.embedder.provider}, dim={self.embedder.embedding_dim})"
        )

    async def initialize_collections(self):
        """Create Qdrant collections if they don't exist"""

        # Standards collection
        try:
            self.client.get_collection(self.standards_collection)
            logger.info(f"Collection '{self.standards_collection}' already exists")
        except:
            self.client.create_collection(
                collection_name=self.standards_collection,
                vectors_config=VectorParams(
                    size=self.embedder.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Created collection: {self.standards_collection}")

        # Cases collection
        try:
            self.client.get_collection(self.cases_collection)
            logger.info(f"Collection '{self.cases_collection}' already exists")
        except:
            self.client.create_collection(
                collection_name=self.cases_collection,
                vectors_config=VectorParams(
                    size=self.embedder.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Created collection: {self.cases_collection}")

    # ========================================================================
    # INDEX STANDARDS
    # ========================================================================

    async def index_standard(self, standard_data: Dict[str, Any]) -> str:
        """
        Index a standard into vector database

        Args:
            standard_data: Standard data from StandardsLoader

        Returns:
            Point ID
        """

        # Create searchable text from standard
        text_parts = [
            f"Standard: {standard_data['metadata']['title']}",
            f"Version: {standard_data['version']}"
        ]

        # Add clauses
        for clause in standard_data.get('clauses', []):
            text_parts.append(f"Clause {clause['number']}: {clause['title']}")
            if 'description' in clause:
                text_parts.append(clause['description'])

        searchable_text = "\n".join(text_parts)

        # Generate embedding
        embedding = await self.embedder.embed(searchable_text)

        # Create point ID (hash of standard + version)
        point_id = hashlib.md5(
            f"{standard_data['standard']}-{standard_data['version']}".encode()
        ).hexdigest()

        # Prepare payload
        payload = {
            "standard": standard_data["standard"],
            "version": standard_data["version"],
            "title": standard_data["metadata"]["title"],
            "clauses_count": len(standard_data.get("clauses", [])),
            "guides_count": len(standard_data.get("guides", [])),
            "indexed_at": datetime.utcnow().isoformat(),
            "tenant_id": self.tenant_id,
            "type": "standard"
        }

        # Upsert to Qdrant
        self.client.upsert(
            collection_name=self.standards_collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            ]
        )

        logger.info(f"✅ Indexed standard: {standard_data['standard']} (id={point_id[:8]}...)")

        return point_id

    # ========================================================================
    # INDEX CASES
    # ========================================================================

    async def index_case(self, case_data: Dict[str, Any]) -> str:
        """
        Index a workflow case into vector database

        Args:
            case_data: Case data from CaseCollector

        Returns:
            Point ID
        """

        # Create searchable text from case
        text_parts = [
            f"Module: {case_data['module']}",
            f"Outcome: {case_data['outcome']}",
            f"Industry: {case_data['organization_context'].get('industry', 'unknown')}",
            f"Organization size: {case_data['organization_context'].get('size', 'unknown')}",
            f"Maturity level: {case_data['organization_context'].get('maturity_level', 'unknown')}"
        ]

        # Add metrics
        metrics = case_data.get('metrics', {})
        for key, value in metrics.items():
            text_parts.append(f"{key}: {value}")

        # Add decisions if available
        for decision in case_data.get('decisions', []):
            if isinstance(decision, dict):
                text_parts.append(f"Decision: {decision.get('description', '')}")
            else:
                text_parts.append(f"Decision: {decision}")

        searchable_text = "\n".join(text_parts)

        # Generate embedding
        embedding = await self.embedder.embed(searchable_text)

        # Create point ID (use case_id)
        point_id = case_data["case_id"]

        # Prepare payload
        payload = {
            "case_id": case_data["case_id"],
            "workflow_id": case_data["workflow_id"],
            "module": case_data["module"],
            "outcome": case_data["outcome"],
            "industry": case_data["organization_context"].get("industry"),
            "org_size": case_data["organization_context"].get("size"),
            "maturity_level": case_data["organization_context"].get("maturity_level"),
            "metrics": metrics,
            "indexed_at": datetime.utcnow().isoformat(),
            "tenant_id": self.tenant_id,
            "type": "case"
        }

        # Upsert to Qdrant
        self.client.upsert(
            collection_name=self.cases_collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            ]
        )

        logger.info(f"✅ Indexed case: {case_data['case_id']} (module={case_data['module']})")

        return point_id

    # ========================================================================
    # SEARCH
    # ========================================================================

    async def search_standards(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search standards using semantic search

        Args:
            query: Search query
            limit: Number of results
            filters: Optional filters (standard, version, etc)

        Returns:
            List of matching standards with scores
        """

        # Generate query embedding
        query_embedding = await self.embedder.embed(query)

        # Prepare filter
        qdrant_filter = None
        if filters:
            conditions = []

            if "standard" in filters:
                conditions.append(
                    FieldCondition(key="standard", match=MatchValue(value=filters["standard"]))
                )

            if "version" in filters:
                conditions.append(
                    FieldCondition(key="version", match=MatchValue(value=filters["version"]))
                )

            # Always filter by tenant
            conditions.append(
                FieldCondition(key="tenant_id", match=MatchValue(value=self.tenant_id))
            )

            if conditions:
                qdrant_filter = Filter(must=conditions)

        # Search
        results = self.client.search(
            collection_name=self.standards_collection,
            query_vector=query_embedding,
            limit=limit,
            query_filter=qdrant_filter
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "standard": result.payload["standard"],
                "version": result.payload["version"],
                "title": result.payload["title"],
                "score": result.score,
                "payload": result.payload
            })

        return formatted_results

    async def search_cases(
        self,
        query: str,
        module: Optional[str] = None,
        industry: Optional[str] = None,
        org_size: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search cases using semantic search

        Args:
            query: Search query
            module: Filter by module
            industry: Filter by industry
            org_size: Filter by organization size
            limit: Number of results

        Returns:
            List of matching cases with scores
        """

        # Generate query embedding
        query_embedding = await self.embedder.embed(query)

        # Prepare filters
        conditions = []

        if module:
            conditions.append(
                FieldCondition(key="module", match=MatchValue(value=module))
            )

        if industry:
            conditions.append(
                FieldCondition(key="industry", match=MatchValue(value=industry))
            )

        if org_size:
            conditions.append(
                FieldCondition(key="org_size", match=MatchValue(value=org_size))
            )

        # Always filter by tenant
        conditions.append(
            FieldCondition(key="tenant_id", match=MatchValue(value=self.tenant_id))
        )

        qdrant_filter = Filter(must=conditions) if conditions else None

        # Search
        results = self.client.search(
            collection_name=self.cases_collection,
            query_vector=query_embedding,
            limit=limit,
            query_filter=qdrant_filter
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "case_id": result.payload["case_id"],
                "module": result.payload["module"],
                "outcome": result.payload["outcome"],
                "industry": result.payload.get("industry"),
                "score": result.score,
                "payload": result.payload
            })

        return formatted_results

    # ========================================================================
    # BATCH INDEXING
    # ========================================================================

    async def index_all_standards(self, standards_loader):
        """Index all available standards"""

        from pathlib import Path

        standards_path = standards_loader.standards_path
        indexed_count = 0

        # Scan all domains
        for domain_dir in standards_path.iterdir():
            if not domain_dir.is_dir():
                continue

            domain = domain_dir.name

            for standard_dir in domain_dir.iterdir():
                if not standard_dir.is_dir():
                    continue

                try:
                    standard_name = standard_dir.name

                    # Load standard
                    if domain == "iso":
                        data = await standards_loader.load_iso_standard(standard_name)
                    elif domain == "bci":
                        data = await standards_loader.load_bci_gpg(standard_name)
                    elif domain == "who":
                        data = await standards_loader.load_who_framework(standard_name)
                    elif domain == "nist":
                        data = await standards_loader.load_nist_framework(standard_name)
                    else:
                        continue

                    # Index
                    await self.index_standard(data)
                    indexed_count += 1

                except Exception as e:
                    logger.error(f"Failed to index {domain}/{standard_name}: {e}")

        logger.info(f"✅ Batch indexing complete: {indexed_count} standards indexed")

        return indexed_count

    async def index_all_cases(self, case_collector):
        """Index all existing cases"""

        import json

        cases_path = case_collector.workflow_cases_path
        indexed_count = 0

        # Scan all modules
        for module_dir in cases_path.iterdir():
            if not module_dir.is_dir():
                continue

            for case_file in module_dir.glob("*.json"):
                try:
                    case_data = json.loads(case_file.read_text())
                    await self.index_case(case_data)
                    indexed_count += 1

                except Exception as e:
                    logger.error(f"Failed to index case {case_file}: {e}")

        logger.info(f"✅ Batch indexing complete: {indexed_count} cases indexed")

        return indexed_count
