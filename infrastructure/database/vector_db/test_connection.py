"""
Test Qdrant Cloud Connection

Quick script to verify connection to Qdrant Cloud.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qdrant_client import QdrantClient


def test_connection():
    """Test Qdrant Cloud connection"""

    print(" Testing Qdrant Cloud connection...")

    # Qdrant Cloud credentials
    url = "https://fa9f6acd-aef9-4ebe-a3f5-f89c62bce378.eu-west-1-0.aws.cloud.qdrant.io"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.XalkCWKEVbNd9P5Bj3f7Y4pPEySIZD3RyCc8EAG5EIE"

    try:
        # Initialize client
        client = QdrantClient(
            url=url,
            api_key=api_key
        )

        # Get collections
        collections = client.get_collections()

        print(f" Connected successfully!")
        print(f"\n Cluster Info:")
        print(f"   • URL: {url}")
        print(f"   • Version: v1.15.5")
        print(f"   • Region: eu-west-1 (AWS)")

        print(f"\n Collections ({len(collections.collections)}):")
        if collections.collections:
            for collection in collections.collections:
                print(f"   • {collection.name}")
        else:
            print("   (no collections yet)")

        return True

    except Exception as e:
        print(f" Connection failed: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
