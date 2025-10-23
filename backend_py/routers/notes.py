"""
Notes Router
Handles note creation, retrieval, update, and deletion
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel
from ..dependencies.auth import get_current_user
from ..utils.logger import log_api_call, log_error, log_success
from ..utils.supabase_client import get_supabase_client

router = APIRouter(prefix="/api/notes", tags=["notes"])


class NoteCreate(BaseModel):
    title: str
    content: str
    subject: str = "General"
    tags: Optional[List[str]] = []


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    subject: Optional[str] = None
    tags: Optional[List[str]] = None


@router.post("", response_model=Dict[str, Any])
async def create_note(
    note: NoteCreate,
    user=Depends(get_current_user)
):
    """Create a new note"""
    
    try:
        log_api_call("/api/notes", "POST", user["id"], **note.dict())
        
        note_id = str(uuid4())
        supabase = get_supabase_client()
        
        note_data = {
            "id": note_id,
            "user_id": user["id"],
            "title": note.title,
            "content": note.content,
            "subject": note.subject,
            "tags": note.tags or [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("notes").insert(note_data).execute()
        
        log_success(f"Created note: {note_id}", "NotesRouter")
        
        return result.data[0] if result.data else note_data
        
    except Exception as e:
        log_error(e, "NotesRouter.create_note")
        raise HTTPException(status_code=500, detail=f"Failed to create note: {str(e)}")


@router.get("", response_model=List[Dict[str, Any]])
async def get_user_notes(
    subject: Optional[str] = None,
    user=Depends(get_current_user)
):
    """Get all notes for the current user, optionally filtered by subject"""
    
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("notes").select("*").eq("user_id", user["id"])
        
        if subject and subject != "All":
            query = query.eq("subject", subject)
        
        result = query.order("created_at", desc=True).execute()
        
        notes = result.data or []
        
        log_success(f"Retrieved {len(notes)} notes", "NotesRouter")
        
        return notes
        
    except Exception as e:
        log_error(e, "NotesRouter.get_user_notes")
        raise HTTPException(status_code=500, detail="Failed to get notes")


@router.get("/{note_id}", response_model=Dict[str, Any])
async def get_note(note_id: str, user=Depends(get_current_user)):
    """Get a specific note"""
    
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("notes").select("*").eq(
            "id", note_id
        ).eq("user_id", user["id"]).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Note not found")
        
        log_success(f"Retrieved note: {note_id}", "NotesRouter")
        
        return result.data
        
    except Exception as e:
        log_error(e, "NotesRouter.get_note")
        raise HTTPException(status_code=500, detail="Failed to get note")


@router.put("/{note_id}", response_model=Dict[str, Any])
async def update_note(
    note_id: str,
    note_update: NoteUpdate,
    user=Depends(get_current_user)
):
    """Update a note"""
    
    try:
        supabase = get_supabase_client()
        
        # Check if note exists
        existing = supabase.table("notes").select("*").eq(
            "id", note_id
        ).eq("user_id", user["id"]).single().execute()
        
        if not existing.data:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Prepare update data
        update_data = {k: v for k, v in note_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = supabase.table("notes").update(update_data).eq(
            "id", note_id
        ).execute()
        
        log_success(f"Updated note: {note_id}", "NotesRouter")
        
        return result.data[0] if result.data else {**existing.data, **update_data}
        
    except Exception as e:
        log_error(e, "NotesRouter.update_note")
        raise HTTPException(status_code=500, detail="Failed to update note")


@router.delete("/{note_id}")
async def delete_note(note_id: str, user=Depends(get_current_user)):
    """Delete a note"""
    
    try:
        supabase = get_supabase_client()
        
        supabase.table("notes").delete().eq(
            "id", note_id
        ).eq("user_id", user["id"]).execute()
        
        log_success(f"Deleted note: {note_id}", "NotesRouter")
        
        return {"message": "Note deleted successfully"}
        
    except Exception as e:
        log_error(e, "NotesRouter.delete_note")
        raise HTTPException(status_code=500, detail="Failed to delete note")


@router.get("/search/{query}", response_model=List[Dict[str, Any]])
async def search_notes(query: str, user=Depends(get_current_user)):
    """Search notes by title or content"""
    
    try:
        supabase = get_supabase_client()
        
        # Get all user notes and filter in Python (Supabase free tier limitation)
        result = supabase.table("notes").select("*").eq(
            "user_id", user["id"]
        ).execute()
        
        notes = result.data or []
        query_lower = query.lower()
        
        # Filter notes by query
        filtered_notes = [
            note for note in notes
            if query_lower in note["title"].lower() or query_lower in note["content"].lower()
        ]
        
        log_success(f"Found {len(filtered_notes)} notes matching query", "NotesRouter")
        
        return filtered_notes
        
    except Exception as e:
        log_error(e, "NotesRouter.search_notes")
        raise HTTPException(status_code=500, detail="Failed to search notes")
