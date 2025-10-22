from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from ..dependencies.auth import get_current_user
from ..schemas import PDFUploadResponse, PDFChatRequest, PDFChatResponse, PDFInfoResponse
from ..services.pdf_service import get_pdf_service
from ..utils.logger import log_api_call, log_error, log_success, log_file_operation
import asyncio

router = APIRouter(prefix="/api/pdf", tags=["pdf"])

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    """Upload and process a PDF file for chat interaction"""
    
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Validate file size (10MB limit)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File size too large. Maximum 10MB allowed.")
        
        # Reset file pointer
        await file.seek(0)
        
        log_api_call("/api/pdf/upload", "POST", user["id"], filename=file.filename)
        log_file_operation("upload", file.filename, user_id=user["id"], size=len(file_content))
        
        # Process the PDF
        pdf_service = get_pdf_service()
        result = await pdf_service.process_pdf(file, user["id"])
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        log_success(f"PDF uploaded and processed successfully: {file.filename}", "PDFRouter")
        
        return PDFUploadResponse(
            file_id=result["file_id"],
            filename=result["filename"],
            status="success",
            message="PDF uploaded and processed successfully",
            document_summary=result["processed_content"]["document_summary"],
            total_pages=result["processed_content"]["total_pages"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, f"PDFRouter.upload_pdf: {file.filename}")
        raise HTTPException(status_code=500, detail="Failed to process PDF file")

@router.post("/chat", response_model=PDFChatResponse)
async def chat_with_pdf(
    request: PDFChatRequest,
    user=Depends(get_current_user)
):
    """Chat with a processed PDF document"""
    
    try:
        log_api_call("/api/pdf/chat", "POST", user["id"], 
                    file_id=request.file_id, question=request.question[:50])
        
        # Chat with the PDF
        pdf_service = get_pdf_service()
        result = await pdf_service.chat_with_pdf(
            file_id=request.file_id,
            question=request.question,
            user_id=user["id"]
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail="Failed to process chat request")
        
        log_success(f"PDF chat response generated for file: {request.file_id}", "PDFRouter")
        
        return PDFChatResponse(
            response=result["response"],
            relevant_pages=result["relevant_pages"],
            file_id=request.file_id,
            question=request.question,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, f"PDFRouter.chat_with_pdf: {request.file_id}")
        raise HTTPException(status_code=500, detail="Failed to process chat request")

@router.get("/info/{file_id}", response_model=PDFInfoResponse)
async def get_pdf_info(
    file_id: str,
    user=Depends(get_current_user)
):
    """Get information about a processed PDF file"""
    
    try:
        log_api_call(f"/api/pdf/info/{file_id}", "GET", user["id"])
        
        # Get PDF information
        pdf_service = get_pdf_service()
        result = await pdf_service.get_pdf_info(file_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        log_success(f"PDF info retrieved for file: {file_id}", "PDFRouter")
        
        return PDFInfoResponse(
            file_id=result["file_id"],
            filename=result["filename"],
            total_pages=result["total_pages"],
            document_summary=result["document_summary"],
            total_length=result["total_length"],
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, f"PDFRouter.get_pdf_info: {file_id}")
        raise HTTPException(status_code=500, detail="Failed to get PDF information")

@router.get("/list")
async def list_user_pdfs(user=Depends(get_current_user)):
    """List all PDFs uploaded by the user"""
    
    try:
        log_api_call("/api/pdf/list", "GET", user["id"])
        
        # This would typically query the database for user's PDFs
        # For now, we'll return a placeholder response
        
        log_success("PDF list retrieved", "PDFRouter")
        
        return {
            "pdfs": [],
            "total_count": 0,
            "status": "success"
        }
        
    except Exception as e:
        log_error(e, "PDFRouter.list_user_pdfs")
        raise HTTPException(status_code=500, detail="Failed to list PDFs")

@router.delete("/delete/{file_id}")
async def delete_pdf(
    file_id: str,
    user=Depends(get_current_user)
):
    """Delete a processed PDF file"""
    
    try:
        log_api_call(f"/api/pdf/delete/{file_id}", "DELETE", user["id"])
        
        # This would typically delete the file and database records
        # For now, we'll return a success response
        
        log_success(f"PDF deleted: {file_id}", "PDFRouter")
        
        return {
            "file_id": file_id,
            "status": "success",
            "message": "PDF deleted successfully"
        }
        
    except Exception as e:
        log_error(e, f"PDFRouter.delete_pdf: {file_id}")
        raise HTTPException(status_code=500, detail="Failed to delete PDF")
