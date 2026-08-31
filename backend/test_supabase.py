import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("e:/Antigravity_workspace/Ai_pathfinder/backend/.env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("URL or Key missing in .env")
    sys.exit(1)

try:
    print("Initializing Supabase Client...")
    supabase: Client = create_client(url, key)
    # Perform a dummy request to check if key is valid (even if table doesn't exist, it should return 4xx not 401 Unauthorized)
    response = supabase.table("users").select("*").limit(1).execute()
    print("Connection successful! Response:", response)
except Exception as e:
    print(f"Error testing connection: {e}")
