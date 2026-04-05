import os
import time
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# ── CONFIG ─────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

SARVAM_API_KEY = os.environ["SARVAM_API_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# ── CLIENTS ────────────────────────────
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# ── PROMPT ─────────────────────────────
def build_prompt(topic, subject, exam):
    return f"""You are an expert content writer for KPSC exam preparation.

Write a clear, factual description for:

Topic: {topic}
Subject: {subject}
Exam: {exam}

Requirements:
- Exactly 3-4 sentences
- Cover what it is, why it matters, key areas to focus
- Plain English
- No headings or bullets
- Do not start with "This topic"

Output only the description."""

# ── SARVAM CALL ───────────────────────
def generate_with_sarvam(prompt):
    url = "https://api.sarvam.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sarvam-m",  # free model
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Sarvam error: {response.text}")

    return response.json()["choices"][0]["message"]["content"].strip()

# ── GEMINI FALLBACK ───────────────────
def generate_with_gemini(prompt):
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

# ── MAIN GENERATOR ────────────────────
def generate_description(topic, subject, exam):
    prompt = build_prompt(topic, subject, exam)

    # 1️⃣ Try Sarvam first
    try:
        result = generate_with_sarvam(prompt)
        print(f"  ⚡ Sarvam used")
        return result

    except Exception as e:
        print(f"  ⚠️ Sarvam failed → {e}")

    # 2️⃣ Fallback to Gemini
    try:
        result = generate_with_gemini(prompt)
        print(f"  🔁 Gemini fallback used")
        return result

    except Exception as e:
        raise Exception(f"Both APIs failed: {e}")

# ── FETCH TOPICS ──────────────────────
res = supabase.table("topics") \
    .select("id, name_en, subjects(name_en, syllabuses(exam_type))") \
    .is_("description", "null") \
    .eq("is_active", True) \
    .execute()

topics = res.data
print(f"Found {len(topics)} topics\n")

# ── PROCESS LOOP ──────────────────────
success, failed = 0, 0

for t in topics:
    topic = t["name_en"]
    subject = t["subjects"]["name_en"] if t.get("subjects") else "General"
    exam = t["subjects"]["syllabuses"]["exam_type"] if t.get("subjects") else "KAS"

    try:
        desc = generate_description(topic, subject, exam)

        supabase.table("topics") \
            .update({"description": desc}) \
            .eq("id", t["id"]) \
            .execute()

        print(f"  ✓ {topic}")
        success += 1

        time.sleep(0.4)

    except Exception as e:
        print(f"  ✗ {topic} — {e}")
        failed += 1

print(f"\n✅ Done → Success: {success}, Failed: {failed}")