import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)

# Fetch topics with descriptions
res = supabase.table("topics") \
    .select("name_en, description") \
    .order("name_en") \
    .execute()

topics = res.data

print(f"\nFound {len(topics)} topics:\n")

for t in topics:
    print(f"📌 {t['name_en']}")
    print(f"📝 {t['description']}\n")