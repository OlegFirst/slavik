"""Simple Supabase test via REST API"""
import os
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"Testing Supabase connection...")
print(f"URL: {supabase_url}")
print(f"Key: {supabase_key[:20]}...")

try:
    client = create_client(supabase_url, supabase_key)
    print("✅ Client created")

    # Try to list auth users
    response = client.auth.admin.list_users()
    print(f"✅ Auth working: {len(response)} users")

    # Try to list storage buckets
    buckets = client.storage.list_buckets()
    print(f"✅ Storage working: {len(buckets)} buckets")

    print("\n✅ Supabase is working!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
