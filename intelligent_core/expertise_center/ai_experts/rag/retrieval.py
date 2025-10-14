"""
Hybrid Retrieval Module

Combines vector similarity search with keyword search for optimal retrieval.
"""

from typing import List, Dict, Any, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Hybrid Retriever

    Combines multiple retrieval strategies:
    - Vector similarity (semantic search)
    - Keyword matching (BM25-like)
    - Filtered search (metadata filters)
    """

    def __init__(
        self,
        embedding_generator,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ):
        """
        Initialize hybrid retriever

        Args:
            embedding_generator: EmbeddingGenerator instance
            vector_weight: Weight for vector similarity (0-1)
            keyword_weight: Weight for keyword matching (0-1)
        """
        self.embedding_generator = embedding_generator
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight

        # Normalize weights
        total_weight = vector_weight + keyword_weight
        self.vector_weight = vector_weight / total_weight
        self.keyword_weight = keyword_weight / total_weight

    async def retrieve(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents using hybrid search

        Args:
            query: Search query
            documents: Document collection with embeddings
            top_k: Number of results to return
            filters: Metadata filters

        Returns:
            Top-k relevant documents with scores
        """

        # Apply filters first
        if filters:
            documents = self._apply_filters(documents, filters)

        if not documents:
            return []

        # Generate query embedding
        query_embedding = await self.embedding_generator.generate_embedding(query)

        # Calculate scores
        scored_docs = []

        for doc in documents:
            # Vector similarity score
            vector_score = 0.0
            if 'embedding' in doc:
                vector_score = self.embedding_generator.cosine_similarity(
                    query_embedding,
                    doc['embedding']
                )

            # Keyword matching score
            keyword_score = self._keyword_match_score(
                query,
                doc.get('text', '') or doc.get('content', '')
            )

            # Combined score
            combined_score = (
                self.vector_weight * vector_score +
                self.keyword_weight * keyword_score
            )

            scored_doc = doc.copy()
            scored_doc['score'] = combined_score
            scored_doc['vector_score'] = vector_score
            scored_doc['keyword_score'] = keyword_score

            scored_docs.append(scored_doc)

        # Sort by score
        scored_docs.sort(key=lambda x: x['score'], reverse=True)

        # Return top-k
        return scored_docs[:top_k]

    def _apply_filters(
        self,
        documents: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply metadata filters"""

        filtered = []

        for doc in documents:
            match = True

            for key, value in filters.items():
                doc_value = doc.get(key)

                if doc_value is None:
                    match = False
                    break

                if isinstance(value, list):
                    # Match any value in list
                    if doc_value not in value:
                        match = False
                        break
                else:
                    # Exact match
                    if doc_value != value:
                        match = False
                        break

            if match:
                filtered.append(doc)

        return filtered

    def _keyword_match_score(self, query: str, text: str) -> float:
        """
        Calculate keyword matching score (simplified BM25-like)

        Args:
            query: Search query
            text: Document text

        Returns:
            Keyword match score (0-1)
        """

        query_lower = query.lower()
        text_lower = text.lower()

        # Extract query terms
        query_terms = set(query_lower.split())

        if not query_terms:
            return 0.0

        # Calculate term frequency
        matches = 0
        for term in query_terms:
            if term in text_lower:
                # Count occurrences
                term_freq = text_lower.count(term)
                # Apply logarithmic scaling
                matches += min(1.0, np.log1p(term_freq) / 3)

        # Normalize by number of query terms
        score = matches / len(query_terms)

        return min(1.0, score)


class VectorStore:
    """
    Simple in-memory vector store

    For production, use Supabase pgvector, Pinecone, or Weaviate.
    """

    def __init__(self, embedding_generator):
        """
        Initialize vector store

        Args:
            embedding_generator: EmbeddingGenerator instance
        """
        self.embedding_generator = embedding_generator
        self.documents = []

    async def add_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add document to vector store

        Args:
            text: Document text
            metadata: Document metadata

        Returns:
            Document ID
        """

        # Generate embedding
        embedding = await self.embedding_generator.generate_embedding(text)

        # Create document
        doc_id = f"doc_{len(self.documents)}"

        doc = {
            'id': doc_id,
            'text': text,
            'embedding': embedding,
            'metadata': metadata or {}
        }

        # Merge metadata into doc for easier filtering
        doc.update(metadata or {})

        self.documents.append(doc)

        return doc_id

    async def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Add multiple documents (batch)

        Args:
            texts: List of document texts
            metadatas: List of metadata dicts

        Returns:
            List of document IDs
        """

        # Generate embeddings (batch)
        embeddings = await self.embedding_generator.generate_embeddings(texts)

        doc_ids = []

        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            doc_id = f"doc_{len(self.documents)}"

            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}

            doc = {
                'id': doc_id,
                'text': text,
                'embedding': embedding,
                'metadata': metadata
            }

            # Merge metadata
            doc.update(metadata)

            self.documents.append(doc)
            doc_ids.append(doc_id)

        return doc_ids

    async def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search vector store

        Args:
            query: Search query
            top_k: Number of results
            filters: Metadata filters

        Returns:
            Top-k relevant documents
        """

        # Use hybrid retriever
        retriever = HybridRetriever(self.embedding_generator)

        results = await retriever.retrieve(
            query=query,
            documents=self.documents,
            top_k=top_k,
            filters=filters
        )

        return results

    def clear(self):
        """Clear all documents"""
        self.documents = []

    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""

        return {
            'total_documents': len(self.documents),
            'embedding_dimension': len(self.documents[0]['embedding']) if self.documents else 0,
            'total_text_chars': sum(len(doc.get('text', '')) for doc in self.documents)
        }
