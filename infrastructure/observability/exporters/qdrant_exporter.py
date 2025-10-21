#!/usr/bin/env python3
"""
Qdrant Vector DB Exporter for Prometheus
Exposes metrics from Qdrant Cloud instance
"""

import os
import time
from typing import Dict, Any
from prometheus_client import start_http_server, Gauge, Info, Counter
from qdrant_client import QdrantClient
from qdrant_client.models import CollectionInfo
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Qdrant connection from environment
QDRANT_URL = os.getenv(
    'QDRANT_URL',
    'https://fa9f6acd-aef9-4ebe-a3f5-f89c62bce378.eu-west-1-0.aws.cloud.qdrant.io:6333'
)
QDRANT_API_KEY = os.getenv(
    'QDRANT_API_KEY',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwiZXhwIjoxNzYwNjU1NDMyfQ.efuzaW9KZeAZbujOWbX33wzgtCGblTANCIgJXyNcjfw'
)
EXPORTER_PORT = int(os.getenv('QDRANT_EXPORTER_PORT', '9122'))
SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', '30'))

# Prometheus metrics
qdrant_up = Gauge('qdrant_up', 'Qdrant availability (1 = up, 0 = down)')
qdrant_info = Info('qdrant_info', 'Qdrant cluster information')

# Collection metrics
qdrant_collections_total = Gauge(
    'qdrant_collections_total',
    'Total number of collections'
)

qdrant_collection_vectors = Gauge(
    'qdrant_collection_vectors_total',
    'Number of vectors in collection',
    ['collection']
)

qdrant_collection_indexed_vectors = Gauge(
    'qdrant_collection_indexed_vectors_total',
    'Number of indexed vectors in collection',
    ['collection']
)

qdrant_collection_segments = Gauge(
    'qdrant_collection_segments_total',
    'Number of segments in collection',
    ['collection']
)

qdrant_collection_disk_size = Gauge(
    'qdrant_collection_disk_size_bytes',
    'Collection disk size in bytes',
    ['collection']
)

qdrant_collection_ram_size = Gauge(
    'qdrant_collection_ram_size_bytes',
    'Collection RAM size in bytes',
    ['collection']
)

# Operation counters
qdrant_scrape_errors = Counter(
    'qdrant_scrape_errors_total',
    'Total number of scrape errors'
)

qdrant_scrape_duration = Gauge(
    'qdrant_scrape_duration_seconds',
    'Duration of Qdrant metrics scrape'
)


class QdrantExporter:
    """Prometheus exporter for Qdrant vector database"""

    def __init__(self):
        """Initialize Qdrant client"""
        try:
            self.client = QdrantClient(
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY,
                timeout=10
            )
            logger.info(f" Connected to Qdrant: {QDRANT_URL}")
        except Exception as e:
            logger.error(f" Failed to connect to Qdrant: {e}")
            raise

    def collect_metrics(self):
        """Collect metrics from Qdrant"""
        start_time = time.time()

        try:
            # Test connection
            collections_response = self.client.get_collections()
            qdrant_up.set(1)

            # Set cluster info
            qdrant_info.info({
                'url': QDRANT_URL,
                'version': 'cloud',
                'cluster_id': 'fa9f6acd-aef9-4ebe-a3f5-f89c62bce378'
            })

            # Collections count
            collections = collections_response.collections
            qdrant_collections_total.set(len(collections))

            logger.info(f" Found {len(collections)} collections")

            # Collection-level metrics
            for collection in collections:
                collection_name = collection.name

                try:
                    # Get detailed collection info
                    info: CollectionInfo = self.client.get_collection(collection_name)

                    # Vector counts
                    points_count = info.points_count or 0
                    indexed_count = info.indexed_vectors_count or 0
                    segments_count = info.segments_count or 0

                    qdrant_collection_vectors.labels(collection=collection_name).set(points_count)
                    qdrant_collection_indexed_vectors.labels(collection=collection_name).set(indexed_count)
                    qdrant_collection_segments.labels(collection=collection_name).set(segments_count)

                    # Storage metrics (if available)
                    if hasattr(info, 'config') and hasattr(info.config, 'optimizer_config'):
                        # These are approximate values based on collection status
                        # Actual disk/RAM usage requires admin API access
                        estimated_disk = points_count * 1024  # ~1KB per vector (rough estimate)
                        estimated_ram = indexed_count * 512   # ~512B per indexed vector

                        qdrant_collection_disk_size.labels(collection=collection_name).set(estimated_disk)
                        qdrant_collection_ram_size.labels(collection=collection_name).set(estimated_ram)

                    logger.info(
                        f"  - {collection_name}: {points_count} vectors, "
                        f"{indexed_count} indexed, {segments_count} segments"
                    )

                except Exception as e:
                    logger.warning(f"️  Failed to get info for {collection_name}: {e}")
                    qdrant_scrape_errors.inc()

        except Exception as e:
            logger.error(f" Scrape failed: {e}")
            qdrant_up.set(0)
            qdrant_scrape_errors.inc()

        finally:
            # Record scrape duration
            duration = time.time() - start_time
            qdrant_scrape_duration.set(duration)
            logger.info(f"⏱️  Scrape completed in {duration:.2f}s")


def main():
    """Main exporter loop"""
    logger.info(" Starting Qdrant Prometheus Exporter")
    logger.info(f" Listening on port {EXPORTER_PORT}")
    logger.info(f" Scrape interval: {SCRAPE_INTERVAL}s")

    # Initialize exporter
    try:
        exporter = QdrantExporter()
    except Exception as e:
        logger.error(f"Failed to initialize exporter: {e}")
        return 1

    # Start HTTP server for Prometheus
    start_http_server(EXPORTER_PORT)
    logger.info(f" Metrics endpoint: http://localhost:{EXPORTER_PORT}/metrics")

    # Continuous collection loop
    while True:
        try:
            exporter.collect_metrics()
        except Exception as e:
            logger.error(f"Error in collection loop: {e}")
            qdrant_scrape_errors.inc()

        time.sleep(SCRAPE_INTERVAL)


if __name__ == '__main__':
    exit(main())
