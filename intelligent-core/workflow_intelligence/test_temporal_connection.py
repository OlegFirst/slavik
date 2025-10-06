"""
Test Temporal Cloud Connection
"""
import asyncio
import os
from dotenv import load_dotenv
from temporalio.client import Client

# Load environment variables
load_dotenv('/Users/MD/AI-Platform-ISO/.env')

async def test_connection():
    """Test connection to Temporal Cloud"""
    
    print("🔌 Testing Temporal Cloud connection...")
    print(f"   Namespace: {os.getenv('TEMPORAL_NAMESPACE')}")
    print(f"   Address: {os.getenv('TEMPORAL_ADDRESS')}")
    
    try:
        # Connect to Temporal Cloud (API Key auth)
        client = await Client.connect(
            target_host=os.getenv('TEMPORAL_ADDRESS'),
            namespace=os.getenv('TEMPORAL_NAMESPACE'),
            api_key=os.getenv('TEMPORAL_API_KEY'),
        )
        
        print(f"\n✅ Connected successfully!")
        print(f"   Client identity: {client.identity}")
        print(f"   Namespace: {client.namespace}")
        
        # Try to list workflows (should be empty)
        count = 0
        async for workflow in client.list_workflows(""):
            count += 1
        
        print(f"   Active workflows: {count}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
