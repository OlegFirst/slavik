#!/usr/bin/env python3
"""
📊 Unified Metrics Exporter
============================

Собирает и экспортирует метрики из всех core модулей:
- AI-Foundation (58 metrics)
- Workflow Intelligence (27 metrics)
- Expertise Center (27 metrics)

Total: 112 metrics

Usage:
    python3 infrastructure/observability/unified_metrics_exporter.py

    # Custom port:
    python3 infrastructure/observability/unified_metrics_exporter.py --port 9000
"""

from prometheus_client import make_wsgi_app
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import all metrics to register them with prometheus_client
logger.info("Loading metrics from all modules...")

metrics_loaded = []

# 1. Workflow Intelligence Metrics
try:
    from intelligent_core.workflow_intelligence.monitoring import metrics as wf_metrics
    metrics_loaded.append("✅ Workflow Intelligence (27 metrics)")
    logger.info("Loaded Workflow Intelligence metrics")
except ImportError as e:
    logger.warning(f"❌ Could not load Workflow Intelligence metrics: {e}")
    metrics_loaded.append(f"❌ Workflow Intelligence - {e}")

# 2. Expertise Center Metrics
try:
    from intelligent_core.expertise_center.monitoring import metrics as ec_metrics
    metrics_loaded.append("✅ Expertise Center (27 metrics)")
    logger.info("Loaded Expertise Center metrics")
except ImportError as e:
    logger.warning(f"❌ Could not load Expertise Center metrics: {e}")
    metrics_loaded.append(f"❌ Expertise Center - {e}")

# 3. AI-Foundation Metrics (multiple files)
try:
    from intelligent_core.ai_foundation.llm import metrics as llm_metrics
    metrics_loaded.append("✅ AI-Foundation LLM (20 metrics)")
    logger.info("Loaded AI-Foundation LLM metrics")
except ImportError as e:
    logger.warning(f"❌ Could not load AI-Foundation LLM metrics: {e}")
    metrics_loaded.append(f"❌ AI-Foundation LLM - {e}")

try:
    from intelligent_core.ai_foundation.rag import metrics as rag_metrics
    metrics_loaded.append("✅ AI-Foundation RAG (20 metrics)")
    logger.info("Loaded AI-Foundation RAG metrics")
except ImportError as e:
    logger.warning(f"❌ Could not load AI-Foundation RAG metrics: {e}")
    metrics_loaded.append(f"❌ AI-Foundation RAG - {e}")

try:
    from intelligent_core.ai_foundation.learning_knowledge.monitoring import metrics as learning_metrics
    metrics_loaded.append("✅ AI-Foundation Learning (18 metrics)")
    logger.info("Loaded AI-Foundation Learning metrics")
except ImportError as e:
    logger.warning(f"❌ Could not load AI-Foundation Learning metrics: {e}")
    metrics_loaded.append(f"❌ AI-Foundation Learning - {e}")


def create_app():
    """Create WSGI app with metrics endpoint"""
    def landing_page(environ, start_response):
        """Landing page with metrics status"""
        if environ['PATH_INFO'] == '/':
            start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])

            html = f"""
            <html>
            <head>
                <title>Unified Metrics Exporter</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #333; }}
                    .status {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                    .metric-group {{ margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #4CAF50; }}
                    .error {{ border-left-color: #f44336; }}
                    a {{ color: #2196F3; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                </style>
            </head>
            <body>
                <h1>📊 Unified Metrics Exporter</h1>

                <div class="status">
                    <h2>Metrics Endpoint</h2>
                    <p><a href="/metrics"><strong>/metrics</strong></a> - Prometheus metrics endpoint</p>
                </div>

                <h2>Loaded Modules</h2>
                <div class="metric-groups">
                    {''.join(f'<div class="metric-group {"error" if "❌" in m else ""}">{m}</div>' for m in metrics_loaded)}
                </div>

                <h2>Core Modules Coverage</h2>
                <ul>
                    <li><strong>Workflow Intelligence:</strong> Performance, Quality, Business metrics</li>
                    <li><strong>Expertise Center:</strong> Analyzers, Specialists, HTTP calls</li>
                    <li><strong>AI-Foundation LLM:</strong> LLM requests, tokens, costs</li>
                    <li><strong>AI-Foundation RAG:</strong> RAG search, embeddings, relevance</li>
                    <li><strong>AI-Foundation Learning:</strong> Knowledge, cases, updates</li>
                </ul>

                <p><em>Total: Up to 112 metrics exported</em></p>
            </body>
            </html>
            """
            return [html.encode('utf-8')]

        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'Not Found']

    # Mount metrics app
    app = DispatcherMiddleware(landing_page, {
        '/metrics': make_wsgi_app()
    })

    return app


def main():
    parser = argparse.ArgumentParser(description='Unified Metrics Exporter')
    parser.add_argument('--port', type=int, default=9000,
                       help='Port to run metrics server (default: 9000)')
    parser.add_argument('--host', default='0.0.0.0',
                       help='Host to bind (default: 0.0.0.0)')
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("🚀 Starting Unified Metrics Exporter")
    logger.info("=" * 60)
    logger.info(f"📊 Metrics endpoint: http://{args.host}:{args.port}/metrics")
    logger.info(f"🏠 Landing page: http://{args.host}:{args.port}/")
    logger.info("")
    logger.info("Loaded modules:")
    for status in metrics_loaded:
        logger.info(f"   {status}")
    logger.info("=" * 60)

    app = create_app()
    run_simple(args.host, args.port, app, use_reloader=False, use_debugger=False)


if __name__ == '__main__':
    main()
