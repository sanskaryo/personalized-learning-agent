from fastapi import APIRouter, Depends, HTTPException
from ..dependencies.auth import get_current_user
from ..schemas import ChatMessageCreate, ChatResponse
from ..services.gemini import generate_chat_reply
from ..utils.supabase_client import get_supabase_client

router = APIRouter(prefix="/api/chat", tags=["chat"]) 


@router.post("/send", response_model=ChatResponse)
def send_message(payload: ChatMessageCreate, user=Depends(get_current_user)):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")

    reply = generate_chat_reply(payload.message, payload.subject)

    # Persist user message and AI reply
    supabase = get_supabase_client()

    # Create a session id if not provided
    from uuid import uuid4
    session_id = payload.session_id or str(uuid4())

    # User message
    supabase.table("chat_messages").insert({
        "user_id": user.get("id", "anonymous"),
        "role": "user",
        "content": payload.message,
        "session_id": session_id,
    }).execute()

    # AI message
    ai_insert = supabase.table("chat_messages").insert({
        "user_id": user.get("id", "anonymous"),
        "role": "assistant",
        "content": reply,
        "session_id": session_id,
    }).execute()

    message_id = None
    try:
        data = getattr(ai_insert, "data", None)
        if data and len(data) > 0:
            message_id = data[0].get("id")
    except Exception:
        message_id = None

    return ChatResponse(reply=reply, message_id=message_id, session_id=session_id)
