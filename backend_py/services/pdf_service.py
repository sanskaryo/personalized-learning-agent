import os
import uuid
from typing import List, Dict, Any, Optional
import PyPDF2
import aiofiles
from fastapi import UploadFile
from ..utils.logger import log_file_operation, log_error, log_success
from ..services.gemini import generate_chat_reply
import json

class PDFProcessingService:
    def __init__(self):
        self.upload_dir = "uploads/pdfs"
        self.processed_dir = "processed/pdfs"
        
        # Create directories if they don't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        log_success("PDF service initialized", "PDFProcessingService")

    async def process_pdf(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        """Process uploaded PDF file and extract content"""
        
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"{file_id}_{file.filename}"
            file_path = os.path.join(self.upload_dir, filename)
            
            # Save uploaded file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            log_file_operation("uploaded", filename, user_id=user_id)
            
            # Extract text from PDF
            extracted_text = await self._extract_text_from_pdf(file_path)
            
            # Process and structure the content
            processed_content = await self._process_pdf_content(extracted_text, filename)
            
            # Save processed content
            processed_file_path = os.path.join(self.processed_dir, f"{file_id}.json")
            async with aiofiles.open(processed_file_path, 'w') as f:
                await f.write(json.dumps(processed_content, indent=2))
            
            log_success(f"PDF processed successfully: {filename}", "PDFProcessingService")
            
            return {
                "file_id": file_id,
                "filename": file.filename,
                "file_path": file_path,
                "processed_content": processed_content,
                "status": "success"
            }
            
        except Exception as e:
            log_error(e, f"PDFProcessingService.process_pdf: {file.filename}")
            return {
                "file_id": None,
                "filename": file.filename,
                "error": str(e),
                "status": "error"
            }

    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        
        try:
            text_content = ""
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text_content += f"\n--- Page {page_num + 1} ---\n"
                    text_content += page_text
                
                log_success(f"Extracted text from {len(pdf_reader.pages)} pages", "PDFProcessingService")
            
            return text_content
            
        except Exception as e:
            log_error(e, f"PDFProcessingService._extract_text_from_pdf: {file_path}")
            raise

    async def _process_pdf_content(self, text_content: str, filename: str) -> Dict[str, Any]:
        """Process and structure PDF content"""
        
        try:
            # Split content into pages
            pages = text_content.split("--- Page")
            processed_pages = []
            
            for i, page_content in enumerate(pages[1:], 1):  # Skip first empty split
                page_text = page_content.strip()
                
                # Extract key information from each page
                page_info = {
                    "page_number": i,
                    "content": page_text,
                    "summary": await self._generate_page_summary(page_text),
                    "keywords": await self._extract_keywords(page_text),
                    "length": len(page_text)
                }
                
                processed_pages.append(page_info)
            
            # Generate overall document summary
            full_text = "\n".join([page["content"] for page in processed_pages])
            document_summary = await self._generate_document_summary(full_text, filename)
            
            processed_content = {
                "filename": filename,
                "total_pages": len(processed_pages),
                "document_summary": document_summary,
                "pages": processed_pages,
                "full_text": full_text,
                "total_length": len(full_text)
            }
            
            return processed_content
            
        except Exception as e:
            log_error(e, "PDFProcessingService._process_pdf_content")
            raise

    async def _generate_page_summary(self, page_text: str) -> str:
        """Generate summary for a single page"""
        
        try:
            if len(page_text) < 100:
                return page_text[:200] + "..." if len(page_text) > 200 else page_text
            
            prompt = f"Summarize the key points from this page content in 2-3 sentences:\n\n{page_text[:1000]}"
            summary = generate_chat_reply(prompt, "General")
            
            return summary[:300] + "..." if len(summary) > 300 else summary
            
        except Exception as e:
            log_error(e, "PDFProcessingService._generate_page_summary")
            return page_text[:200] + "..." if len(page_text) > 200 else page_text

    async def _generate_document_summary(self, full_text: str, filename: str) -> str:
        """Generate overall document summary"""
        
        try:
            # Use first 2000 characters for summary generation
            text_sample = full_text[:2000]
            
            prompt = f"Provide a comprehensive summary of this document '{filename}' focusing on main topics, key concepts, and learning objectives:\n\n{text_sample}"
            summary = generate_chat_reply(prompt, "General")
            
            return summary
            
        except Exception as e:
            log_error(e, "PDFProcessingService._generate_document_summary")
            return f"Document summary for {filename} - {len(full_text)} characters of content."

    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        
        try:
            prompt = f"Extract 5-10 key technical terms and concepts from this text:\n\n{text[:500]}"
            keywords_response = generate_chat_reply(prompt, "General")
            
            # Parse keywords from response
            keywords = [kw.strip() for kw in keywords_response.split('\n') if kw.strip()]
            return keywords[:10]  # Limit to 10 keywords
            
        except Exception as e:
            log_error(e, "PDFProcessingService._extract_keywords")
            return []

    async def chat_with_pdf(self, file_id: str, question: str, user_id: str) -> Dict[str, Any]:
        """Chat with PDF document using AI"""
        
        try:
            # Load processed PDF content
            processed_file_path = os.path.join(self.processed_dir, f"{file_id}.json")
            
            if not os.path.exists(processed_file_path):
                raise FileNotFoundError(f"Processed PDF file not found: {file_id}")
            
            async with aiofiles.open(processed_file_path, 'r') as f:
                content = await f.read()
                processed_content = json.loads(content)
            
            # Generate contextual response
            response = await self._generate_pdf_response(question, processed_content)
            
            # Find relevant page references
            relevant_pages = await self._find_relevant_pages(question, processed_content)
            
            log_success(f"Generated PDF chat response for question: {question[:50]}...", "PDFProcessingService")
            
            return {
                "response": response,
                "relevant_pages": relevant_pages,
                "file_id": file_id,
                "question": question,
                "status": "success"
            }
            
        except Exception as e:
            log_error(e, f"PDFProcessingService.chat_with_pdf: {file_id}")
            return {
                "response": f"Sorry, I couldn't process your question about the PDF. Error: {str(e)}",
                "relevant_pages": [],
                "file_id": file_id,
                "question": question,
                "status": "error"
            }

    async def _generate_pdf_response(self, question: str, processed_content: Dict[str, Any]) -> str:
        """Generate AI response based on PDF content and question"""
        
        try:
            # Build context from PDF content
            context = f"""
            Document: {processed_content['filename']}
            Summary: {processed_content['document_summary']}
            Total Pages: {processed_content['total_pages']}
            
            Full Content:
            {processed_content['full_text'][:3000]}  # Limit context length
            """
            
            prompt = f"""
            Based on the following document content, answer the user's question:
            
            Document Context:
            {context}
            
            User Question: {question}
            
            Please provide a comprehensive answer based on the document content. If the question cannot be answered from the document, please say so and suggest what information might be helpful.
            """
            
            response = generate_chat_reply(prompt, "General")
            return response
            
        except Exception as e:
            log_error(e, "PDFProcessingService._generate_pdf_response")
            return "I apologize, but I'm having trouble processing your question about this document. Please try rephrasing your question."

    async def _find_relevant_pages(self, question: str, processed_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find pages most relevant to the question"""
        
        try:
            relevant_pages = []
            
            for page in processed_content['pages']:
                # Simple relevance scoring based on keyword matching
                question_lower = question.lower()
                content_lower = page['content'].lower()
                summary_lower = page['summary'].lower()
                
                # Count keyword matches
                matches = 0
                for word in question_lower.split():
                    if word in content_lower or word in summary_lower:
                        matches += 1
                
                # If page has relevant content, include it
                if matches > 0:
                    relevant_pages.append({
                        "page_number": page['page_number'],
                        "summary": page['summary'],
                        "relevance_score": matches / len(question.split())
                    })
            
            # Sort by relevance score and return top 3
            relevant_pages.sort(key=lambda x: x['relevance_score'], reverse=True)
            return relevant_pages[:3]
            
        except Exception as e:
            log_error(e, "PDFProcessingService._find_relevant_pages")
            return []

    async def get_pdf_info(self, file_id: str) -> Dict[str, Any]:
        """Get information about a processed PDF"""
        
        try:
            processed_file_path = os.path.join(self.processed_dir, f"{file_id}.json")
            
            if not os.path.exists(processed_file_path):
                raise FileNotFoundError(f"Processed PDF file not found: {file_id}")
            
            async with aiofiles.open(processed_file_path, 'r') as f:
                content = await f.read()
                processed_content = json.loads(content)
            
            return {
                "file_id": file_id,
                "filename": processed_content['filename'],
                "total_pages": processed_content['total_pages'],
                "document_summary": processed_content['document_summary'],
                "total_length": processed_content['total_length'],
                "status": "success"
            }
            
        except Exception as e:
            log_error(e, f"PDFProcessingService.get_pdf_info: {file_id}")
            return {
                "file_id": file_id,
                "error": str(e),
                "status": "error"
            }

# Global instance - will be initialized when first accessed
pdf_service = None

def get_pdf_service():
    global pdf_service
    if pdf_service is None:
        pdf_service = PDFProcessingService()
    return pdf_service
