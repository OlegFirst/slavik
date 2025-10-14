"""
RAG + LLM Integration Example

Demonstrates how to use RAG pipeline with LLM router for intelligent Q&A
"""

import asyncio
import logging
from ai_foundation import RAGPipeline, LLMRouter, QdrantCollectionSetup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_qdrant_collections():
    """Setup Qdrant collections if needed"""
    try:
        setup = QdrantCollectionSetup()
        setup.setup_all_collections()
        logger.info("✓ Qdrant collections ready")
    except Exception as e:
        logger.warning(f"Qdrant setup skipped: {e}")


async def ingest_sample_knowledge(rag: RAGPipeline):
    """Ingest sample BCM knowledge"""

    sample_docs = [
        {
            "text": """
            Business Impact Analysis (BIA) is the process of identifying critical business functions
            and their dependencies. It determines recovery priorities based on financial, operational,
            and reputational impact. The BIA typically assesses Recovery Time Objective (RTO) and
            Recovery Point Objective (RPO) for each critical function.
            """,
            "metadata": {
                "source_type": "iso_standard",
                "module": "bia",
                "clause": "8.2.2"
            }
        },
        {
            "text": """
            Risk Assessment involves identifying threats and vulnerabilities that could disrupt
            critical business operations. This includes natural disasters, cyber attacks, supply
            chain disruptions, and human errors. Each risk is evaluated based on likelihood and
            potential impact to prioritize mitigation efforts.
            """,
            "metadata": {
                "source_type": "iso_standard",
                "module": "risk_assessment",
                "clause": "8.2.1"
            }
        },
        {
            "text": """
            Case Study: Financial Services Company
            Industry: Banking
            Challenge: Extended downtime during hurricane
            Solution: Implemented geographic redundancy with hot standby datacenter
            Outcome: Achieved 99.99% uptime during subsequent major weather events
            RTO improved from 24 hours to 2 hours.
            """,
            "metadata": {
                "source_type": "case_study",
                "industry": "banking",
                "module": "bia"
            }
        }
    ]

    try:
        doc_ids = await rag.ingest_documents(sample_docs)
        logger.info(f"✓ Ingested {len(doc_ids)} knowledge chunks")
    except Exception as e:
        logger.warning(f"Knowledge ingestion skipped: {e}")


async def rag_enhanced_qa():
    """Demonstrate RAG-enhanced Q&A"""

    # Initialize components
    llm = LLMRouter()
    rag = RAGPipeline(
        embedding_provider="voyage",  # or "openai"
        top_k=3
    )

    logger.info("=== RAG + LLM Integration Demo ===\n")

    # Setup (optional - skip if already done)
    # await setup_qdrant_collections()
    # await ingest_sample_knowledge(rag)

    # Example 1: RAG-enhanced answer
    logger.info("Example 1: RAG-Enhanced Q&A")
    logger.info("-" * 50)

    query = "What is Business Impact Analysis and why is it important?"

    # Retrieve relevant knowledge
    try:
        knowledge = await rag.retrieve(
            query=query,
            top_k=2,
            enable_reranking=True
        )

        # Build context from retrieved knowledge
        context_str = await rag.build_context(query=query, max_context_length=1000)

        # Generate answer with LLM
        system_prompt = """You are a BCM (Business Continuity Management) expert.
        Use the provided knowledge context to answer questions accurately and concisely.
        Always cite sources when possible."""

        user_prompt = f"""Context from knowledge base:
{context_str}

Question: {query}

Please provide a comprehensive answer based on the context above."""

        answer = await llm.query(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            task_type="content_generation",
            temperature=0.3
        )

        logger.info(f"Query: {query}")
        logger.info(f"\nRetrieved {len(knowledge)} relevant chunks")
        logger.info(f"\nAnswer:\n{answer}\n")

    except Exception as e:
        logger.error(f"RAG query failed: {e}")

    # Example 2: Strategic analysis with multiple sources
    logger.info("\nExample 2: Strategic Analysis with Context")
    logger.info("-" * 50)

    strategic_query = "How should a banking company approach RTO planning?"

    try:
        # Retrieve with filtering
        knowledge = await rag.retrieve(
            query=strategic_query,
            filters={"industry": "banking"},
            top_k=2,
            enable_reranking=True
        )

        context_str = await rag.build_context(query=strategic_query)

        system_prompt = """You are a senior BCM consultant specializing in financial services.
        Provide strategic recommendations based on industry best practices and real-world examples."""

        user_prompt = f"""Knowledge base context:
{context_str}

Question: {strategic_query}

Provide strategic recommendations with justification."""

        answer = await llm.query(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            task_type="strategic_analysis",
            temperature=0.5
        )

        logger.info(f"Query: {strategic_query}")
        logger.info(f"\nAnswer:\n{answer}\n")

    except Exception as e:
        logger.error(f"Strategic query failed: {e}")

    # Example 3: Quick task (no RAG needed)
    logger.info("\nExample 3: Quick Task (No RAG)")
    logger.info("-" * 50)

    quick_answer = await llm.query(
        system_prompt="You are a helpful BCM assistant.",
        user_prompt="List the main components of a BCM program in 3 bullet points.",
        task_type="quick_tasks",
        temperature=0.2
    )

    logger.info(f"Answer:\n{quick_answer}\n")

    # Show stats
    logger.info("\nSystem Statistics:")
    logger.info("-" * 50)
    rag_stats = rag.get_stats()
    llm_info = llm.get_provider_info()

    logger.info(f"RAG: {rag_stats}")
    logger.info(f"LLM: {llm_info}")


async def main():
    """Main demo"""
    try:
        await rag_enhanced_qa()
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
