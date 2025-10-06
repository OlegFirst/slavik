"""
Embedding Generation Module

Generates vector embeddings for semantic search using various embedding models.
"""

from typing import List, Dict, Any, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Embedding Generator

    Generates vector embeddings for text using:
    - Voyage AI (preferred)
    - OpenAI embeddings (fallback)
    - Local model (development)
    """

    def __init__(
        self,
        provider: str = "voyage",
        model: str = "voyage-2",
        dimension: int = 1024
    ):
        """
        Initialize embedding generator

        Args:
            provider: Embedding provider ('voyage', 'openai', 'local')
            model: Model name
            dimension: Embedding dimension
        """
        self.provider = provider
        self.model = model
        self.dimension = dimension
        self.client = self._initialize_client()

    def _initialize_client(self):
        """Initialize embedding client"""

        if self.provider == "voyage":
            try:
                import voyageai
                import os
                api_key = os.getenv('VOYAGE_API_KEY')
                if api_key:
                    return voyageai.Client(api_key=api_key)
                else:
                    logger.warning("VOYAGE_API_KEY not found, using mock embeddings")
                    return None
            except ImportError:
                logger.warning("voyageai not installed, using mock embeddings")
                return None

        elif self.provider == "openai":
            try:
                import openai
                import os
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    return openai.AsyncOpenAI(api_key=api_key)
                else:
                    logger.warning("OPENAI_API_KEY not found, using mock embeddings")
                    return None
            except ImportError:
                logger.warning("openai not installed, using mock embeddings")
                return None

        else:
            logger.info("Using mock embeddings for development")
            return None

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for single text

        Args:
            text: Input text

        Returns:
            Embedding vector
        """

        if not self.client:
            return self._mock_embedding(text)

        if self.provider == "voyage":
            return await self._voyage_embedding(text)
        elif self.provider == "openai":
            return await self._openai_embedding(text)
        else:
            return self._mock_embedding(text)

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch)

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """

        if not self.client:
            return [self._mock_embedding(text) for text in texts]

        if self.provider == "voyage":
            return await self._voyage_embeddings_batch(texts)
        elif self.provider == "openai":
            return await self._openai_embeddings_batch(texts)
        else:
            return [self._mock_embedding(text) for text in texts]

    async def _voyage_embedding(self, text: str) -> List[float]:
        """Generate embedding using Voyage AI"""

        try:
            result = self.client.embed([text], model=self.model)
            return result.embeddings[0]
        except Exception as e:
            logger.error(f"Voyage embedding failed: {e}")
            return self._mock_embedding(text)

    async def _voyage_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Voyage AI (batch)"""

        try:
            result = self.client.embed(texts, model=self.model)
            return result.embeddings
        except Exception as e:
            logger.error(f"Voyage batch embedding failed: {e}")
            return [self._mock_embedding(text) for text in texts]

    async def _openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""

        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            return self._mock_embedding(text)

    async def _openai_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI (batch)"""

        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI batch embedding failed: {e}")
            return [self._mock_embedding(text) for text in texts]

    def _mock_embedding(self, text: str) -> List[float]:
        """
        Generate mock embedding for development

        Uses simple hash-based pseudo-random vector
        """

        # Seed based on text for consistency
        seed = hash(text) % (2**32)
        np.random.seed(seed)

        # Generate random vector
        embedding = np.random.randn(self.dimension).tolist()

        return embedding

    def cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between embeddings

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (0-1)
        """

        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)

        # Normalize to 0-1 range
        return (similarity + 1) / 2


class DocumentChunker:
    """
    Document Chunker

    Splits documents into chunks for embedding and retrieval.
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        strategy: str = "sentence"
    ):
        """
        Initialize document chunker

        Args:
            chunk_size: Target chunk size (characters or tokens)
            chunk_overlap: Overlap between chunks
            strategy: Chunking strategy ('sentence', 'paragraph', 'fixed')
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy

    def chunk_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk document into smaller pieces

        Args:
            text: Document text
            metadata: Document metadata

        Returns:
            List of chunks with metadata
        """

        if self.strategy == "sentence":
            chunks = self._chunk_by_sentence(text)
        elif self.strategy == "paragraph":
            chunks = self._chunk_by_paragraph(text)
        else:
            chunks = self._chunk_fixed(text)

        # Add metadata to chunks
        chunk_dicts = []
        for i, chunk_text in enumerate(chunks):
            chunk_dict = {
                "text": chunk_text,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "char_count": len(chunk_text)
            }

            if metadata:
                chunk_dict.update(metadata)

            chunk_dicts.append(chunk_dict)

        return chunk_dicts

    def _chunk_by_sentence(self, text: str) -> List[str]:
        """Chunk by sentences"""

        # Simple sentence splitting (production should use spaCy or NLTK)
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(' '.join(current_chunk))

                # Start new chunk with overlap
                overlap_sentences = current_chunk[-1:] if self.chunk_overlap > 0 else []
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        # Add final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def _chunk_by_paragraph(self, text: str) -> List[str]:
        """Chunk by paragraphs"""

        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            para_length = len(para)

            if current_length + para_length > self.chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length

        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        return chunks

    def _chunk_fixed(self, text: str) -> List[str]:
        """Chunk by fixed size"""

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap

        return chunks
