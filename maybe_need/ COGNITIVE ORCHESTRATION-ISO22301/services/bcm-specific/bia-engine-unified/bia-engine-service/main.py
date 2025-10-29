#!/usr/bin/env python3
"""
BIA Engine - Business Impact Analysis Service
Main entry point for the BIA Engine service
"""

import os
import sys
import logging
from datetime import datetime
import uvicorn

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bia_engine.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for BIA Engine service"""
    port = int(os.getenv("PORT", "8082"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting BIA Engine service on {host}:{port}")
    logger.info(f"Service started at: {datetime.now().isoformat()}")

    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start BIA Engine service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()