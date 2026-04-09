import os
from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer

load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)

print("Loading embedding model: BAAI/bge-small-en-v1.5 ...")
model = SentenceTransformer("BAAI/bge-small-en-v1.5")
print("Model loaded.\n")

res = supabase.table("topics") \
    .select("id, name_en, name_kn, description") \
    .eq("is_active", True) \
    .execute()

topics = res.data
total = len(topics)
print(f"Found {total} topics to embed.\n")

success = 0
failed = 0

for t in topics:
    try:
        text = f"{t['name_en']}. {t.get('name_kn', '')}. {t.get('description', '')}"
        embedding = model.encode(text).tolist()

        supabase.table("topics") \
            .update({"embedding": embedding}) \
            .eq("id", t["id"]) \
            .execute()

        print(f"  ✓ {t['name_en']}")
        success += 1

    except Exception as e:
        print(f"  ✗ {t['name_en']} — {e}")
        failed += 1

print(f"\n✅ {success}/{total} topics embedded.")
if failed:
    print(f"   ✗ {failed} failed — re-run script to retry.")