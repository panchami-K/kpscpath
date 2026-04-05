from app.core.supabase_client import service_client
from app.core.errors import AppError
from app.modules.syllabus.schemas import TopicStatus


# in service.py, temporarily
def get_all_syllabuses():
    print(">>>>>> URL:", service_client.supabase_url)
    
    # Test 1: no filter at all
    r1 = service_client.table("syllabuses").select("*").execute()
    print(">>>>>> NO FILTER:", len(r1.data))
    
    # Test 2: with is_active filter
    r2 = service_client.table("syllabuses").select("*").eq("is_active", True).execute()
    print(">>>>>> WITH FILTER:", len(r2.data))
    
    # Test 3: check what error/count says
    print(">>>>>> RAW r1:", r1)
    
    return r2.data

# in service.py, temporarily
def get_all_syllabuses():
    print(">>>>>> URL:", service_client.supabase_url)
    res = service_client.table("syllabuses") \
        .select("*") \
        .eq("is_active", True) \
        .order("exam_type") \
        .execute()
    print(">>>>>> COUNT:", len(res.data))
    return res.data


def get_subjects_with_progress(syllabus_id: str, user_id: str):
    # fetch all subjects for this syllabus
    sub_res = service_client.table("subjects") \
        .select("*") \
        .eq("syllabus_id", syllabus_id) \
        .eq("is_active", True) \
        .order("sort_order") \
        .execute()

    subjects = sub_res.data
    if not subjects:
        return []

    subject_ids = [s["id"] for s in subjects]

    # fetch topic counts per subject
    topic_res = service_client.table("topics") \
        .select("id, subject_id") \
        .in_("subject_id", subject_ids) \
        .eq("is_active", True) \
        .execute()

    topics_by_subject: dict = {}
    for t in topic_res.data:
        topics_by_subject.setdefault(t["subject_id"], []).append(t["id"])

    all_topic_ids = [t["id"] for t in topic_res.data]

    # fetch user progress for all topics in one query
    completed_set = set()
    if all_topic_ids and user_id:
        prog_res = service_client.table("user_topic_progress") \
            .select("topic_id") \
            .eq("user_id", user_id) \
            .eq("status", "completed") \
            .in_("topic_id", all_topic_ids) \
            .execute()
        completed_set = {r["topic_id"] for r in prog_res.data}

    result = []
    for s in subjects:
        topic_ids = topics_by_subject.get(s["id"], [])
        total = len(topic_ids)
        completed = len([tid for tid in topic_ids if tid in completed_set])
        pct = round((completed / total * 100), 1) if total > 0 else 0.0
        result.append({
            **s,
            "total_topics": total,
            "completed_topics": completed,
            "progress_pct": pct,
        })

    return result


def get_topics_for_subject(subject_id: str, user_id: str):
    # verify subject exists
    sub_res = service_client.table("subjects") \
        .select("id") \
        .eq("id", subject_id) \
        .single() \
        .execute()

    if not sub_res.data:
        raise AppError("NOT_FOUND", 404, "Subject not found")

    # fetch topics
    top_res = service_client.table("topics") \
        .select("*") \
        .eq("subject_id", subject_id) \
        .eq("is_active", True) \
        .order("sort_order") \
        .execute()

    topics = top_res.data
    if not topics:
        return []

    topic_ids = [t["id"] for t in topics]

    # fetch user progress in one query
    prog_map: dict = {}
    if user_id:
        prog_res = service_client.table("user_topic_progress") \
            .select("topic_id, status, confidence") \
            .eq("user_id", user_id) \
            .in_("topic_id", topic_ids) \
            .execute()
        prog_map = {r["topic_id"]: r for r in prog_res.data}

    result = []
    for t in topics:
        prog = prog_map.get(t["id"], {})
        result.append({
            **t,
            "status": prog.get("status", "not_started"),
            "confidence": prog.get("confidence"),
        })

    return result


def update_topic_status(topic_id: str, user_id: str, status: str, confidence=None):
    # verify topic exists
    top_res = service_client.table("topics") \
        .select("id") \
        .eq("id", topic_id) \
        .single() \
        .execute()

    if not top_res.data:
        raise AppError("NOT_FOUND", 404, "Topic not found")

    payload = {
        "user_id": user_id,
        "topic_id": topic_id,
        "status": status,
    }
    if confidence is not None:
        payload["confidence"] = confidence

    # upsert — insert or update if exists
    upsert_res = service_client.table("user_topic_progress") \
        .upsert(payload, on_conflict="user_id,topic_id") \
        .execute()

    return upsert_res.data[0] if upsert_res.data else payload


def get_progress_summary(user_id: str):
    # fetch all active topics
    top_res = service_client.table("topics") \
        .select("id, subject_id") \
        .eq("is_active", True) \
        .execute()

    all_topics = top_res.data
    total = len(all_topics)

    if total == 0:
        return {
            "total_topics": 0,
            "completed_topics": 0,
            "in_progress_topics": 0,
            "needs_revision_topics": 0,
            "overall_pct": 0.0,
            "by_subject": [],
        }

    topic_ids = [t["id"] for t in all_topics]

    # fetch all user progress
    prog_res = service_client.table("user_topic_progress") \
        .select("topic_id, status") \
        .eq("user_id", user_id) \
        .in_("topic_id", topic_ids) \
        .execute()

    prog_map = {r["topic_id"]: r["status"] for r in prog_res.data}

    completed        = sum(1 for tid in topic_ids if prog_map.get(tid) == "completed")
    in_progress      = sum(1 for tid in topic_ids if prog_map.get(tid) == "in_progress")
    needs_revision   = sum(1 for tid in topic_ids if prog_map.get(tid) == "needs_revision")
    overall_pct      = round(completed / total * 100, 1)

    # per-subject breakdown
    subject_map: dict = {}
    for t in all_topics:
        sid = t["subject_id"]
        subject_map.setdefault(sid, {"total": 0, "completed": 0})
        subject_map[sid]["total"] += 1
        if prog_map.get(t["id"]) == "completed":
            subject_map[sid]["completed"] += 1

    by_subject = [
        {
            "subject_id": sid,
            "total": v["total"],
            "completed": v["completed"],
            "pct": round(v["completed"] / v["total"] * 100, 1) if v["total"] > 0 else 0.0,
        }
        for sid, v in subject_map.items()
    ]

    return {
        "total_topics": total,
        "completed_topics": completed,
        "in_progress_topics": in_progress,
        "needs_revision_topics": needs_revision,
        "overall_pct": overall_pct,
        "by_subject": by_subject,
    }