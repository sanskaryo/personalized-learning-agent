"""
Flashcard Router
Handles flashcard generation from notes and spaced repetition
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid
from datetime import datetime

from ..schemas import (
    FlashcardGenerateRequest,
    FlashcardGenerateResponse,
    GeneratedFlashcard
)
from ..services.flashcard_service import FlashcardService
from ..dependencies.auth import get_current_user
from ..utils.supabase_client import get_supabase_client
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/flashcards", tags=["flashcards"])

# Initialize service
flashcard_service = FlashcardService()


@router.post("/generate", response_model=FlashcardGenerateResponse)
async def generate_flashcards_from_content(
    request: FlashcardGenerateRequest,
    current_user = Depends(get_current_user)
):
    """
    Generate flashcards from note content using AI
    
    - **note_id**: ID of the note to generate flashcards from (optional)
    - **content**: Direct content to generate flashcards from (optional)
    - **count**: Number of flashcards to generate (1-20)
    - **difficulty**: Difficulty level (easy, medium, hard)
    
    Note: Provide either note_id or content, not both
    """
    logger.info(f"Flashcard generation request from user {current_user['id']}")
    
    try:
        supabase = get_supabase_client()
        
        # Get content from note if note_id provided
        content = request.content
        source = "direct_content"
        note_title = "Custom Content"
        
        if request.note_id:
            note_result = supabase.table("notes")\
                .select("*")\
                .eq("id", request.note_id)\
                .eq("user_id", current_user["id"])\
                .execute()
            
            if not note_result.data:
                raise HTTPException(status_code=404, detail="Note not found")
            
            note = note_result.data[0]
            content = note["content"]
            note_title = note["title"]
            source = f"note:{request.note_id}"
            logger.info(f"Generating flashcards from note: {note_title}")
        
        if not content or len(content.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Content is too short to generate flashcards"
            )
        
        # Generate flashcards using AI
        flashcards = await flashcard_service.generate_flashcards(
            content=content,
            count=request.count,
            difficulty=request.difficulty or "medium"
        )
        
        if not flashcards:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate flashcards from content"
            )
        
        # Save flashcards to database
        saved_flashcards = []
        for card in flashcards:
            flashcard_id = str(uuid.uuid4())
            
            flashcard_data = {
                "id": flashcard_id,
                "user_id": current_user["id"],
                "question": card["question"],
                "answer": card["answer"],
                "difficulty": card["difficulty"],
                "hint": card.get("hint"),
                "source": source,
                "note_id": request.note_id,
                "next_review_date": datetime.utcnow().isoformat(),
                "review_count": 0,
                "correct_count": 0,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table("flashcards").insert(flashcard_data).execute()
            
            if result.data:
                saved_flashcards.append(card)
        
        logger.info(f"Generated and saved {len(saved_flashcards)} flashcards")
        
        # Award points for flashcard creation
        points_data = {
            "user_id": current_user["id"],
            "points": len(saved_flashcards) * 5,  # 5 points per flashcard
            "action_type": "flashcards_created",
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table("user_points").insert(points_data).execute()
        
        # Convert to response format
        flashcard_responses = [
            GeneratedFlashcard(**card) for card in saved_flashcards
        ]
        
        return FlashcardGenerateResponse(
            flashcards=flashcard_responses,
            total_count=len(flashcard_responses),
            source=source,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating flashcards: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate flashcards: {str(e)}"
        )


@router.get("/all")
async def get_all_flashcards(
    limit: int = 50,
    offset: int = 0,
    difficulty: str = None,
    current_user = Depends(get_current_user)
):
    """Get all user's flashcards"""
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("flashcards")\
            .select("*")\
            .eq("user_id", current_user["id"])
        
        if difficulty:
            query = query.eq("difficulty", difficulty)
        
        result = query.order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        logger.info(f"Retrieved {len(result.data)} flashcards for user")
        
        return {
            "flashcards": result.data,
            "total": len(result.data),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching flashcards: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch flashcards")


@router.get("/due")
async def get_due_flashcards(
    limit: int = 20,
    current_user = Depends(get_current_user)
):
    """Get flashcards due for review (spaced repetition)"""
    try:
        supabase = get_supabase_client()
        
        current_time = datetime.utcnow().isoformat()
        
        result = supabase.table("flashcards")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .lte("next_review_date", current_time)\
            .order("next_review_date", desc=False)\
            .limit(limit)\
            .execute()
        
        logger.info(f"Retrieved {len(result.data)} due flashcards for user")
        
        return {
            "flashcards": result.data,
            "total": len(result.data)
        }
        
    except Exception as e:
        logger.error(f"Error fetching due flashcards: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch due flashcards")


@router.post("/review/{flashcard_id}")
async def review_flashcard(
    flashcard_id: str,
    performance: str,  # "again", "hard", "good", "easy"
    current_user = Depends(get_current_user)
):
    """
    Record flashcard review and update next review date
    
    - **flashcard_id**: ID of the flashcard being reviewed
    - **performance**: User's performance rating (again, hard, good, easy)
    """
    if performance not in ["again", "hard", "good", "easy"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid performance rating. Use: again, hard, good, or easy"
        )
    
    try:
        supabase = get_supabase_client()
        
        # Get current flashcard data
        flashcard_result = supabase.table("flashcards")\
            .select("*")\
            .eq("id", flashcard_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not flashcard_result.data:
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        flashcard = flashcard_result.data[0]
        
        # Calculate next review using spaced repetition
        current_interval = 1  # You could store this in DB
        review_schedule = flashcard_service.calculate_next_review(
            performance=performance,
            current_interval=current_interval
        )
        
        # Update flashcard
        is_correct = performance in ["good", "easy"]
        
        update_data = {
            "next_review_date": review_schedule["next_review_date"],
            "review_count": flashcard["review_count"] + 1,
            "correct_count": flashcard["correct_count"] + (1 if is_correct else 0),
            "last_reviewed": datetime.utcnow().isoformat()
        }
        
        supabase.table("flashcards")\
            .update(update_data)\
            .eq("id", flashcard_id)\
            .execute()
        
        logger.info(f"Flashcard {flashcard_id} reviewed with performance: {performance}")
        
        # Award points for review
        points = {"again": 1, "hard": 2, "good": 3, "easy": 5}[performance]
        
        points_data = {
            "user_id": current_user["id"],
            "points": points,
            "action_type": "flashcard_reviewed",
            "reference_id": flashcard_id,
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table("user_points").insert(points_data).execute()
        
        return {
            "message": "Flashcard reviewed successfully",
            "flashcard_id": flashcard_id,
            "next_review": review_schedule["next_review_date"],
            "points_earned": points,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reviewing flashcard: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to review flashcard")


@router.delete("/{flashcard_id}")
async def delete_flashcard(
    flashcard_id: str,
    current_user = Depends(get_current_user)
):
    """Delete a flashcard"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("flashcards")\
            .delete()\
            .eq("id", flashcard_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        logger.info(f"Deleted flashcard: {flashcard_id}")
        
        return {
            "message": "Flashcard deleted successfully",
            "flashcard_id": flashcard_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting flashcard: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete flashcard")


@router.get("/stats")
async def get_flashcard_stats(
    current_user = Depends(get_current_user)
):
    """Get user's flashcard statistics"""
    try:
        supabase = get_supabase_client()
        
        # Get all flashcards
        flashcards = supabase.table("flashcards")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not flashcards.data:
            return {
                "total_flashcards": 0,
                "total_reviews": 0,
                "average_accuracy": 0,
                "due_today": 0
            }
        
        total_flashcards = len(flashcards.data)
        total_reviews = sum(f["review_count"] for f in flashcards.data)
        total_correct = sum(f["correct_count"] for f in flashcards.data)
        average_accuracy = (total_correct / total_reviews * 100) if total_reviews > 0 else 0
        
        # Count due flashcards
        current_time = datetime.utcnow().isoformat()
        due_today = sum(1 for f in flashcards.data if f["next_review_date"] <= current_time)
        
        return {
            "total_flashcards": total_flashcards,
            "total_reviews": total_reviews,
            "average_accuracy": round(average_accuracy, 2),
            "due_today": due_today,
            "mastered": sum(1 for f in flashcards.data if f["review_count"] >= 5 and (f["correct_count"] / max(f["review_count"], 1)) > 0.8)
        }
        
    except Exception as e:
        logger.error(f"Error fetching flashcard stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")
