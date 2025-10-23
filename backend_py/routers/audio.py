"""
Audio Transcription Router
Handles audio file uploads and transcription
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from typing import Optional
import os
import uuid
from datetime import datetime

from ..schemas import (
    AudioTranscriptionRequest,
    AudioTranscriptionResponse
)
from ..services.audio_service import AudioTranscriptionService
from ..dependencies.auth import get_current_user
from ..utils.supabase_client import get_supabase_client
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/audio", tags=["audio-transcription"])

# Initialize service
audio_service = AudioTranscriptionService()


@router.get("/health")
async def check_audio_service_health():
    """Check if audio transcription service is configured"""
    is_healthy = audio_service.check_service_health()
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "service": "AssemblyAI",
        "configured": is_healthy,
        "message": "Service is ready" if is_healthy else "AssemblyAI API key not configured"
    }


@router.post("/transcribe", response_model=AudioTranscriptionResponse)
async def transcribe_audio_file(
    audio_file: UploadFile = File(...),
    subject: str = Form("General"),
    topic: str = Form("Lecture Notes"),
    auto_save_as_note: bool = Form(True),
    current_user = Depends(get_current_user)
):
    """
    Transcribe an audio file to text
    
    - **audio_file**: Audio file (mp3, wav, m4a, etc.)
    - **subject**: Subject/category for the transcription
    - **topic**: Specific topic of the audio
    - **auto_save_as_note**: Automatically save transcription as a note
    """
    logger.info(f"Transcription request from user {current_user['id']} for file: {audio_file.filename}")
    
    try:
        # Validate file type
        allowed_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.webm', '.flac']
        file_ext = os.path.splitext(audio_file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            logger.warning(f"Invalid file type: {file_ext}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Create temp directory if it doesn't exist
        temp_dir = "temp_audio"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save uploaded file temporarily
        temp_file_id = str(uuid.uuid4())
        temp_file_path = os.path.join(temp_dir, f"{temp_file_id}{file_ext}")
        
        with open(temp_file_path, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)
        
        logger.info(f"Audio file saved temporarily: {temp_file_path}")
        
        # Transcribe audio
        transcription_result = await audio_service.transcribe_audio(
            audio_file_path=temp_file_path,
            enable_chapters=True
        )
        
        # Generate transcription ID
        transcription_id = str(uuid.uuid4())
        
        # Save to database
        supabase = get_supabase_client()
        
        transcription_data = {
            "id": transcription_id,
            "user_id": current_user["id"],
            "subject": subject,
            "topic": topic,
            "original_filename": audio_file.filename,
            "transcription_text": transcription_result["text"],
            "confidence": transcription_result.get("confidence"),
            "duration_seconds": transcription_result.get("duration"),
            "chapters": transcription_result.get("chapters"),
            "word_count": transcription_result["word_count"],
            "created_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("audio_transcriptions").insert(transcription_data).execute()
        logger.info(f"Transcription saved to database: {transcription_id}")
        
        # Optionally save as note
        note_id = None
        if auto_save_as_note:
            note_data = {
                "user_id": current_user["id"],
                "title": f"📝 {topic} - Audio Transcription",
                "content": transcription_result["text"],
                "subject": subject,
                "tags": ["audio-transcription", topic.lower()],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            note_result = supabase.table("notes").insert(note_data).execute()
            
            if note_result.data:
                note_id = note_result.data[0].get("id")
                logger.info(f"Transcription saved as note: {note_id}")
        
        # Clean up temp file
        try:
            os.remove(temp_file_path)
            logger.debug(f"Temp file removed: {temp_file_path}")
        except Exception as e:
            logger.warning(f"Failed to remove temp file: {str(e)}")
        
        return AudioTranscriptionResponse(
            transcription_id=transcription_id,
            text=transcription_result["text"],
            confidence=transcription_result.get("confidence"),
            duration=transcription_result.get("duration"),
            chapters=transcription_result.get("chapters"),
            word_count=transcription_result["word_count"],
            note_id=note_id,
            status="success",
            message=f"Audio transcribed successfully. {transcription_result['word_count']} words extracted."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.get("/transcriptions")
async def get_user_transcriptions(
    limit: int = 10,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """Get user's transcription history"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("audio_transcriptions")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        logger.info(f"Retrieved {len(result.data)} transcriptions for user {current_user['id']}")
        
        return {
            "transcriptions": result.data,
            "total": len(result.data),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching transcriptions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch transcriptions")


@router.get("/transcriptions/{transcription_id}")
async def get_transcription_detail(
    transcription_id: str,
    current_user = Depends(get_current_user)
):
    """Get details of a specific transcription"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("audio_transcriptions")\
            .select("*")\
            .eq("id", transcription_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Transcription not found")
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching transcription detail: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch transcription")


@router.delete("/transcriptions/{transcription_id}")
async def delete_transcription(
    transcription_id: str,
    current_user = Depends(get_current_user)
):
    """Delete a transcription"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("audio_transcriptions")\
            .delete()\
            .eq("id", transcription_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Transcription not found")
        
        logger.info(f"Deleted transcription: {transcription_id}")
        
        return {
            "message": "Transcription deleted successfully",
            "transcription_id": transcription_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting transcription: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete transcription")
