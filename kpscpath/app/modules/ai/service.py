import os
import json
from datetime import datetime, date
from typing import Generator

from groq import Groq
from sentence_transformers import SentenceTransformer

from app.core.supabase_client import service_client
from app.core.errors import AppError
from app.core.token_budget import check_budget, increment_budget

# ── load once at module level ──
_model = SentenceTransformer("BAAI/bge-small-en-v1.5")

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GROQ_MODEL   = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")


# ────────────────────────────────────────────
# Embedding
# ────────────────────────────────────────────

def embed_query(question: str) -> list:
    return _model.encode(question).tolist()


# ────────────────────────────────────────────
# Vector search
# ────────────────────────────────────────────

def search_similar_topics(query_vector: list, limit: int = 5) -> list:
    vector_str = "[" + ",".join(str(v) for v in query_vector) + "]"

    res = service_client.rpc(
        "match_topics",
        {
            "query_embedding": vector_str,
            "match_threshold": 0.25,
            "match_count": limit,
        },
    ).execute()

    return res.data or []


# ────────────────────────────────────────────
# Prompt builders
# ────────────────────────────────────────────

def build_system_prompt(language: str) -> str:
    if language == "kn":
        return (
            "ನೀವು KPSC ಪರೀಕ್ಷಾ ತಯಾರಿ ತಜ್ಞರು. ಕನ್ನಡದಲ್ಲಿ ಮಾತ್ರ ಉತ್ತರಿಸಿ. "
            "ನೀಡಿರುವ ಪಠ್ಯಕ್ರಮ ಸಂದರ್ಭದಿಂದ ಮಾತ್ರ ಉತ್ತರಿಸಿ. "
            "ಸಂಕ್ಷಿಪ್ತ ಮತ್ತು ಪರೀಕ್ಷಾ-ಕೇಂದ್ರಿತವಾಗಿರಿ."
        )
    return (
        "You are a KPSC exam preparation expert. "
        "Answer ONLY in English. "
        "Use ONLY the provided syllabus context. "
        "Be concise and exam-focused."
    )


def build_user_message(question: str, topics: list) -> str:
    context = "\n\n".join([
        f"Topic: {t['name_en']}\n{t.get('description', '')}"
        for t in topics
    ])
    return f"SYLLABUS CONTEXT:\n{context}\n\nQUESTION: {question}"


# ────────────────────────────────────────────
# Validation
# ────────────────────────────────────────────

def validate_kannada(text: str) -> bool:
    return any("\u0C80" <= ch <= "\u0CFF" for ch in text)


# ────────────────────────────────────────────
# Main streaming function
# ────────────────────────────────────────────

def stream_doubt_answer(request, user_id: str) -> Generator:
    # 1. Rate limit check
    check_budget(user_id)

    # 2. Embed the question
    query_vector = embed_query(request.question)

    # 3. Find relevant topics
    topics = search_similar_topics(query_vector)
    if not topics:
        yield f"data: {json.dumps({'token': 'No relevant syllabus topics found for your question. Please ask about KPSC exam topics.'})}\n\n"
        yield "data: [DONE]\n\n"
        return

    # 4. Build prompts
    system_prompt = build_system_prompt(request.language)
    user_message  = build_user_message(request.question, topics)

    # 5. Stream from Groq
    groq_client = Groq(api_key=GROQ_API_KEY)
    stream = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
        stream=True,
        temperature=0.3,
        max_tokens=1000,
    )

    # 6. Collect and yield tokens
    full_text = ""
    for chunk in stream:
        token = chunk.choices[0].delta.content or ""
        full_text += token
        if token:
            yield f"data: {json.dumps({'token': token})}\n\n"

    # 7. Kannada validation warning
    if request.language == "kn" and not validate_kannada(full_text):
        warning = " (Note: Kannada response unavailable)"
        yield f"data: {json.dumps({'token': warning})}\n\n"

    # 8. Done signal
    yield "data: [DONE]\n\n"

    # 9. Increment budget
    increment_budget(user_id)

    # 10. Log to agent_tasks
    try:
        tokens_in  = len(user_message.split())
        tokens_out = len(full_text.split())

        service_client.table("agent_tasks").insert({
            "user_id":        user_id,
            "agent_type":     "doubt_solver",
            "task_type":      "answer_question",
            "status":         "completed",
            "input_payload":  {
                "question":     request.question,
                "language":     request.language,
                "topic_id":     request.topic_id,
                "topics_found": len(topics),
            },
            "output_payload": {
                "answer":  full_text,
                "sources": [t["id"] for t in topics],
            },
            "model_used":    GROQ_MODEL,
            "tokens_in":     tokens_in,
            "tokens_out":    tokens_out,
            "completed_at":  datetime.utcnow().isoformat(),
        }).execute()
    except Exception:
        pass  # logging failure must never break the response


# ────────────────────────────────────────────
# History
# ────────────────────────────────────────────

def get_doubt_history(user_id: str) -> list:
    res = service_client.table("agent_tasks") \
        .select("id, input_payload, output_payload, model_used, queued_at") \
        .eq("user_id", user_id) \
        .eq("agent_type", "doubt_solver") \
        .order("queued_at", desc=True) \
        .limit(20) \
        .execute()

    history = []
    for row in (res.data or []):
        inp = row.get("input_payload") or {}
        out = row.get("output_payload") or {}
        history.append({
            "id":         row["id"],
            "question":   inp.get("question", ""),
            "answer":     out.get("answer", ""),
            "language":   inp.get("language", "en"),
            "model_used": row.get("model_used", ""),
            "created_at": row.get("queued_at", ""),
        })
    return history