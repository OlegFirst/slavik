"""
Batch Tasks - Parallel Processing
===================================
"""
import logging
from typing import List, Dict, Any
from celery import group, chord

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from celery_app import app
from tasks.learning_tasks import CallbackTask

logger = logging.getLogger(__name__)


@app.task(base=CallbackTask, bind=True)
def analyze_document(self, doc_id: str, analyzer_type: str) -> Dict[str, Any]:
    """
    Analyze single document

    Used in batch processing via group/chord
    """
    logger.info(f"📄 Analyzing document {doc_id} with {analyzer_type}")

    try:
        from intelligent_core.expertise_center.domains.bcm.analyzers import get_analyzer

        analyzer = get_analyzer(analyzer_type)

        # Fetch document
        document = fetch_document(doc_id)

        # Analyze
        result = analyzer.analyze(document)

        return {
            'doc_id': doc_id,
            'analyzer': analyzer_type,
            'result': result,
            'status': 'success'
        }

    except Exception as exc:
        logger.error(f"❌ Document analysis failed: {exc}")
        return {
            'doc_id': doc_id,
            'status': 'failed',
            'error': str(exc)
        }


@app.task(base=CallbackTask)
def aggregate_analysis_results(results: List[Dict]) -> Dict[str, Any]:
    """
    Aggregate results from batch analysis

    Used as callback in chord
    """
    logger.info(f"📊 Aggregating {len(results)} analysis results...")

    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']

    return {
        'total': len(results),
        'successful': len(successful),
        'failed': len(failed),
        'results': results,
        'summary': {
            'success_rate': len(successful) / len(results) if results else 0
        }
    }


def batch_analyze_documents(doc_ids: List[str], analyzer_type: str) -> Any:
    """
    Analyze multiple documents in parallel

    Usage:
        result = batch_analyze_documents(['doc1', 'doc2', 'doc3'], 'compliance')
        result.get()  # Wait for completion
    """
    # Create parallel tasks
    job = chord(
        (analyze_document.s(doc_id, analyzer_type) for doc_id in doc_ids),
        aggregate_analysis_results.s()
    )

    return job.apply_async()


@app.task
def cleanup_old_results():
    """
    Cleanup old task results from Redis

    Runs every 6 hours
    """
    logger.info("🧹 Cleaning up old task results...")

    from celery.result import AsyncResult
    from datetime import datetime, timedelta

    # Delete results older than 7 days
    cutoff = datetime.utcnow() - timedelta(days=7)

    # Implementation depends on backend
    # This is placeholder

    return {'status': 'cleaned'}


def fetch_document(doc_id: str) -> Dict:
    """Fetch document from database"""
    # Placeholder - implement actual document fetching
    return {'id': doc_id, 'content': '...'}
