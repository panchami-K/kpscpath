# app/core/supabase_client.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY: str = os.environ["SUPABASE_ANON_KEY"]
SUPABASE_SERVICE_ROLE_KEY: str = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Anon client — used in middleware for token validation
anon_client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Service role client — bypass RLS by setting auth header on postgrest session
service_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
service_client.postgrest.session.headers.update({
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
})