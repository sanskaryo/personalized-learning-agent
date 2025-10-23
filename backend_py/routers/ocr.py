"""
OCR Router
Handles OCR text extraction (processed on frontend, saves to backend)
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from ..schemas import OCRRequest, OCRResponse
from ..dependencies.auth import get_current_user
from ..utils.supabase_client import get_supabase_client
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/ocr", tags=["ocr"])


class OCRSaveRequest(BaseModel):
    """Request model for saving OCR extracted text"""
    extracted_text: str
    image_url: Optional[str] = None
    subject: str = "General"
    topic: str = "Handwritten Notes"
    auto_save_as_note: bool = True
    confidence: Optional[float] = None


@router.post("/save", response_model=OCRResponse)
async def save_ocr_text(
    request: OCRSaveRequest,
    current_user = Depends(get_current_user)
):
    """
    Save OCR extracted text to database
    
    Note: OCR processing happens on frontend using Tesseract.js
    This endpoint saves the results to the backend
    
    - **extracted_text**: Text extracted by OCR
    - **image_url**: Optional URL/path to the original image
    - **subject**: Subject/category
    - **topic**: Specific topic
    - **auto_save_as_note**: Save as a note automatically
    - **confidence**: OCR confidence score (0-1)
    """
    logger.info(f"Saving OCR text from user {current_user['id']}")
    
    try:
        if not request.extracted_text or len(request.extracted_text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Extracted text cannot be empty"
            )
        
        supabase = get_supabase_client()
        
        # Generate OCR ID
        ocr_id = str(uuid.uuid4())
        word_count = len(request.extracted_text.split())
        
        # Save OCR record
        ocr_data = {
            "id": ocr_id,
            "user_id": current_user["id"],
            "extracted_text": request.extracted_text,
            "image_url": request.image_url,
            "subject": request.subject,
            "topic": request.topic,
            "confidence": request.confidence,
            "word_count": word_count,
            "created_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("ocr_extractions").insert(ocr_data).execute()
        logger.info(f"OCR text saved to database: {ocr_id}")
        
        # Optionally save as note
        note_id = None
        if request.auto_save_as_note:
            note_data = {
                "user_id": current_user["id"],
                "title": f"📄 {request.topic} - OCR Extraction",
                "content": request.extracted_text,
                "subject": request.subject,
                "tags": ["ocr-extraction", request.topic.lower()],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            note_result = supabase.table("notes").insert(note_data).execute()
            
            if note_result.data:
                note_id = note_result.data[0].get("id")
                logger.info(f"OCR text saved as note: {note_id}")
        
        return OCRResponse(
            ocr_id=ocr_id,
            extracted_text=request.extracted_text,
            confidence=request.confidence,
            word_count=word_count,
            note_id=note_id,
            status="success",
            message=f"OCR text saved successfully. {word_count} words extracted."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving OCR text: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save OCR text: {str(e)}"
        )


@router.get("/extractions")
async def get_user_ocr_extractions(
    limit: int = 10,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """Get user's OCR extraction history"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("ocr_extractions")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        logger.info(f"Retrieved {len(result.data)} OCR extractions for user {current_user['id']}")
        
        return {
            "extractions": result.data,
            "total": len(result.data),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching OCR extractions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch OCR extractions")


@router.get("/extractions/{ocr_id}")
async def get_ocr_extraction_detail(
    ocr_id: str,
    current_user = Depends(get_current_user)
):
    """Get details of a specific OCR extraction"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("ocr_extractions")\
            .select("*")\
            .eq("id", ocr_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="OCR extraction not found")
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching OCR extraction detail: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch OCR extraction")


@router.delete("/extractions/{ocr_id}")
async def delete_ocr_extraction(
    ocr_id: str,
    current_user = Depends(get_current_user)
):
    """Delete an OCR extraction"""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("ocr_extractions")\
            .delete()\
            .eq("id", ocr_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="OCR extraction not found")
        
        logger.info(f"Deleted OCR extraction: {ocr_id}")
        
        return {
            "message": "OCR extraction deleted successfully",
            "ocr_id": ocr_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting OCR extraction: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete OCR extraction")
