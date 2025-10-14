"""
📊 Metrics Integration Example

Shows how to add /metrics endpoint to any FastAPI service
"""

from fastapi import FastAPI, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import logging

logger = logging.getLogger(__name__)

# Example: ai-foundation service
app = FastAPI(title="AI Foundation")


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint

    Exposes all collected metrics in Prometheus format.
    Prometheus will scrape this endpoint every 15-30 seconds.

    Returns:
        Prometheus-formatted metrics
    """
    try:
        metrics_output = generate_latest()
        return Response(
            content=metrics_output,
            media_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}")
        return Response(
            content=b"# Failed to generate metrics\n",
            media_type=CONTENT_TYPE_LATEST,
            status_code=500
        )


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-foundation",
        "version": "1.0.0"
    }


# Example API endpoint with metrics integration
from ai_foundation.rag.metrics import track_rag_search

@app.post("/rag/search")
@track_rag_search(collection="knowledge_base", query_type="hybrid")
async def rag_search(query: str, top_k: int = 10):
    """
    RAG search endpoint

    Metrics automatically tracked:
    - Search duration
    - Results count
    - Relevance scores
    """
    from ai_foundation.rag import RAGPipeline

    rag = RAGPipeline()
    results = await rag.retrieve(query=query, top_k=top_k)

    return {
        "query": query,
        "results": results,
        "count": len(results)
    }


# Example usage in analyzer
from expertise_center.monitoring.metrics import track_analyzer_call

@app.post("/analyze/impact")
@track_analyzer_call(analyzer_name="impact_analyzer", domain="bcm")
async def analyze_impact(data: dict):
    """
    Impact analysis endpoint

    Metrics automatically tracked:
    - Analysis duration
    - Success/error count
    - Recommendations generated
    """
    from expertise_center.analyzers.impact_analyzer import ImpactAnalyzer

    analyzer = ImpactAnalyzer()
    result = await analyzer.analyze(data)

    return result


if __name__ == "__main__":
    import uvicorn

    # Start server
    # Metrics will be available at http://localhost:9001/metrics
    uvicorn.run(app, host="0.0.0.0", port=9001)

    print("""
    ✅ Service started!

    Endpoints:
    - http://localhost:9001/metrics      (Prometheus metrics)
    - http://localhost:9001/health       (Health check)
    - http://localhost:9001/rag/search   (RAG search with metrics)
    - http://localhost:9001/analyze/impact (Impact analysis with metrics)

    Test metrics:
    curl http://localhost:9001/metrics

    Expected output:
    # HELP ai_foundation_rag_search_duration_seconds ...
    # TYPE ai_foundation_rag_search_duration_seconds histogram
    ai_foundation_rag_search_duration_seconds_bucket{collection="knowledge_base",...} ...

    # HELP expertise_center_analyzer_calls_total ...
    # TYPE expertise_center_analyzer_calls_total counter
    expertise_center_analyzer_calls_total{analyzer_name="impact_analyzer",...} ...
    """)
