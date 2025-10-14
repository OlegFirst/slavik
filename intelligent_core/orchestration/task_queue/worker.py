"""
Celery Worker Entry Point
==========================

Start with:
    celery -A worker worker --loglevel=info --queues=learning,batch,prediction

Or use multiple workers:
    celery multi start 3 -A worker \
        -Q:1 learning -Q:2 batch -Q:3 prediction \
        --loglevel=INFO
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from celery_app import app

if __name__ == '__main__':
    app.start()
