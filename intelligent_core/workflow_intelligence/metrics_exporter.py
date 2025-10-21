#!/usr/bin/env python3
"""
 Workflow Intelligence Metrics Exporter
==========================================

Standalone HTTP server для экспорта метрик Workflow Intelligence.
Используется когда workflow_intelligence используется как библиотека.

Usage:
    python3 -m intelligent_core.workflow_intelligence.metrics_exporter

    # Or with custom port:
    python3 -m intelligent_core.workflow_intelligence.metrics_exporter --port 9001
"""

from prometheus_client import start_http_server, make_wsgi_app
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import time
import argparse
import logging

# Import all workflow intelligence metrics to register them
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from intelligent_core.workflow_intelligence.monitoring.metrics import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """Create WSGI app with metrics endpoint"""
    # Create a simple WSGI app
    def simple_app(environ, start_response):
        """Simple landing page"""
        if environ['PATH_INFO'] == '/':
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [b"""
            <html>
            <head><title>Workflow Intelligence Metrics</title></head>
            <body>
                <h1>Workflow Intelligence Metrics Exporter</h1>
                <p>Metrics available at: <a href="/metrics">/metrics</a></p>
                <ul>
                    <li>27 workflow intelligence metrics exported</li>
                    <li>Performance, Quality, Business metrics</li>
                </ul>
            </body>
            </html>
            """]
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'Not Found']

    # Mount metrics app
    app = DispatcherMiddleware(simple_app, {
        '/metrics': make_wsgi_app()
    })

    return app


def main():
    parser = argparse.ArgumentParser(description='Workflow Intelligence Metrics Exporter')
    parser.add_argument('--port', type=int, default=9001,
                       help='Port to run metrics server (default: 9001)')
    parser.add_argument('--host', default='0.0.0.0',
                       help='Host to bind (default: 0.0.0.0)')
    args = parser.parse_args()

    logger.info(f" Starting Workflow Intelligence Metrics Exporter on {args.host}:{args.port}")
    logger.info(f" Metrics endpoint: http://{args.host}:{args.port}/metrics")

    app = create_app()
    run_simple(args.host, args.port, app)


if __name__ == '__main__':
    main()
