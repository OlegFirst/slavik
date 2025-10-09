"""
Digital Twin Universal Service - Main Entry Point

Run with: python main.py
Or with uvicorn: uvicorn main:app --reload
"""

import logging
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api import create_app

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('digital_twin.log')
    ]
)

logger = logging.getLogger(__name__)


def get_config():
    """Load configuration from environment or defaults"""
    import os
    
    return {
        'postgres': {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'digital_twin'),
            'username': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'pool_size': int(os.getenv('POSTGRES_POOL_SIZE', 20)),
            'max_overflow': int(os.getenv('POSTGRES_MAX_OVERFLOW', 10)),
        },
        'redis': {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', 6379)),
            'db': int(os.getenv('REDIS_DB', 0)),
            'password': os.getenv('REDIS_PASSWORD'),
            'prefix': os.getenv('REDIS_PREFIX', 'dt:'),
            'max_connections': int(os.getenv('REDIS_MAX_CONNECTIONS', 50)),
        },
        'cors_origins': os.getenv('CORS_ORIGINS', '*').split(','),
        'environment': os.getenv('ENVIRONMENT', 'development'),
    }


# Create FastAPI application
config = get_config()
app = create_app(config)

logger.info(f"Digital Twin API initialized - Environment: {config['environment']}")


if __name__ == "__main__":
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload in development
        log_level="info"
    )
