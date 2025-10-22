from fastapi import APIRouter, Depends, HTTPException
from ..dependencies.auth import get_current_user
from ..schemas import StartSessionRequest, StartSessionResponse, EndSessionResponse, ProgressStats
from ..utils.supabase_client import get_supabase_client
from uuid import uuid4
from datetime import datetime, timezone

router = APIRouter(prefix="/api/progress", tags=["progress"]) 


@router.post("/session/start", response_model=StartSessionResponse)
def start_session(payload: StartSessionRequest | None = None, user=Depends(get_current_user)):
    supabase = get_supabase_client()
    session_id = str(uuid4())
    subject = (payload.subject if payload else None) or None
    now = datetime.now(timezone.utc).isoformat()

    supabase.table("study_sessions").insert({
        "id": session_id,
        "user_id": user["id"],
        "subject": subject,
        "started_at": now,
        "ended_at": None,
        "duration_seconds": 0,
    }).execute()

    return StartSessionResponse(session_id=session_id)


@router.put("/session/{session_id}/end", response_model=EndSessionResponse)
def end_session(session_id: str, user=Depends(get_current_user)):
    supabase = get_supabase_client()
    # Fetch session
    res = supabase.table("study_sessions").select("*").eq("id", session_id).eq("user_id", user["id"]).single().execute()
    session = getattr(res, "data", None)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    started_at = session.get("started_at")
    if not started_at:
        raise HTTPException(status_code=400, detail="Session has no start time")

    start_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    end_dt = datetime.now(timezone.utc)
    duration = int((end_dt - start_dt).total_seconds())

    supabase.table("study_sessions").update({
        "ended_at": end_dt.isoformat(),
        "duration_seconds": duration,
    }).eq("id", session_id).eq("user_id", user["id"]).execute()

    return EndSessionResponse(session_id=session_id, duration_seconds=duration)


@router.get("/stats", response_model=ProgressStats)
def get_stats(user=Depends(get_current_user)):
    supabase = get_supabase_client()
    res = supabase.table("study_sessions").select("subject, duration_seconds").eq("user_id", user["id"]).execute()
    rows = getattr(res, "data", []) or []

    total = 0
    breakdown: dict[str, int] = {}
    for row in rows:
        seconds = int(row.get("duration_seconds") or 0)
        total += seconds
        subj = row.get("subject") or "General"
        breakdown[subj] = breakdown.get(subj, 0) + seconds

    return ProgressStats(total_seconds=total, subject_breakdown=breakdown)
