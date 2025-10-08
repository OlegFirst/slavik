"""
Celery Beat Entry Point - Scheduler
====================================

Start with:
    celery -A beat beat --loglevel=info
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from celery_app import app

if __name__ == '__main__':
    app.start(['beat', '--loglevel=INFO'])
