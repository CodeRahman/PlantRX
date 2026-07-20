import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
# takes supabase url and key from the .env folder
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
