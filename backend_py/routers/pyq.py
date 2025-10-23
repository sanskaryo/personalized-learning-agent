"""
PYQ (Previous Year Questions) Router
Handles question generation and answer evaluation
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid
from datetime import datetime

from ..schemas import (
    PYQGenerateRequest,
    PYQGenerateResponse,
    PYQAnswerSubmission,
    PYQEvaluationResponse,
    PYQQuestion,
    PYQEvaluation
)
from ..services.pyq_service import PYQService
from ..dependencies.auth import get_current_user
from ..utils.supabase_client import get_supabase_client
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/pyq", tags=["previous-year-questions"])

# Initialize service
pyq_service = PYQService()


@router.post("/generate", response_model=PYQGenerateResponse)
async def generate_pyq_questions(
    request: PYQGenerateRequest,
    current_user = Depends(get_current_user)
):
    """
    Generate Previous Year Question style questions using AI
    
    - **subject**: Subject name (e.g., Physics, Mathematics)
    - **topic**: Specific topic within the subject
    - **difficulty**: Question difficulty (easy, medium, hard)
    - **count**: Number of questions to generate (1-20)
    """
    logger.info(f"Generating {request.count} PYQs for {request.subject} - {request.topic}")
    
    try:
        # Generate questions using AI
        questions = await pyq_service.generate_questions(
            subject=request.subject,
            topic=request.topic,
            difficulty=request.difficulty,
            count=request.count
        )
        
        # Save questions to database for tracking
        supabase = get_supabase_client()
        
        for question in questions:
            question_data = {
                "id": question["id"],
                "user_id": current_user["id"],
                "subject": request.subject,
                "topic": request.topic,
                "question_text": question["question"],
                "marks": question["marks"],
                "difficulty": question["difficulty"],
                "year": question.get("year", 2024),
                "key_points": question.get("key_points", []),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Use upsert to avoid duplicates
            supabase.table("pyq_questions").upsert(question_data).execute()
        
        logger.info(f"Generated and saved {len(questions)} questions")
        
        # Convert to response format
        question_responses = [
            PYQQuestion(**q) for q in questions
        ]
        
        return PYQGenerateResponse(
            questions=question_responses,
            total_count=len(question_responses),
            subject=request.subject,
            topic=request.topic
        )
        
    except Exception as e:
        logger.error(f"Error generating PYQ questions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate questions: {str(e)}"
        )


@router.post("/evaluate", response_model=PYQEvaluationResponse)
async def evaluate_pyq_answer(
    submission: PYQAnswerSubmission,
    current_user = Depends(get_current_user)
):
    """
    Evaluate student's answer using AI
    
    - **question_id**: ID of the question being answered
    - **question_text**: The question text
    - **answer**: Student's answer
    - **subject**: Subject context
    """
    logger.info(f"Evaluating answer for question {submission.question_id}")
    
    try:
        # Get question details to determine max marks
        supabase = get_supabase_client()
        
        question_result = supabase.table("pyq_questions")\
            .select("marks")\
            .eq("id", submission.question_id)\
            .execute()
        
        max_marks = 10  # Default
        if question_result.data:
            max_marks = question_result.data[0].get("marks", 10)
        
        # Evaluate answer using AI
        evaluation_data = await pyq_service.evaluate_answer(
            question_text=submission.question_text,
            student_answer=submission.answer,
            subject=submission.subject,
            max_marks=max_marks
        )
        
        # Generate submission ID
        submission_id = str(uuid.uuid4())
        
        # Save submission and evaluation to database
        submission_data = {
            "id": submission_id,
            "user_id": current_user["id"],
            "question_id": submission.question_id,
            "question_text": submission.question_text,
            "answer": submission.answer,
            "subject": submission.subject,
            "score": evaluation_data["score"],
            "max_score": evaluation_data["max_score"],
            "evaluation": evaluation_data,
            "created_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("pyq_submissions").insert(submission_data).execute()
        logger.info(f"Saved evaluation: {submission_id} (Score: {evaluation_data['score']}/{evaluation_data['max_score']})")
        
        # Update user points for gamification
        points_earned = int(evaluation_data["score"] * 10)  # 10 points per mark
        
        points_data = {
            "user_id": current_user["id"],
            "points": points_earned,
            "action_type": "pyq_completed",
            "reference_id": submission_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("user_points").insert(points_data).execute()
        logger.info(f"Awarded {points_earned} points to user")
        
        return PYQEvaluationResponse(
            evaluation=PYQEvaluation(**evaluation_data),
            submission_id=submission_id,
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Error evaluating PYQ answer: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate answer: {str(e)}"
        )


@router.get("/questions/history")
async def get_question_history(
    subject: str = None,
    limit: int = 20,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """Get user's generated question history"""
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("pyq_questions")\
            .select("*")\
            .eq("user_id", current_user["id"])
        
        if subject:
            query = query.eq("subject", subject)
        
        result = query.order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        logger.info(f"Retrieved {len(result.data)} questions for user")
        
        return {
            "questions": result.data,
            "total": len(result.data),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching question history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch questions")


@router.get("/submissions/history")
async def get_submission_history(
    subject: str = None,
    limit: int = 20,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """Get user's answer submission history"""
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("pyq_submissions")\
            .select("*")\
            .eq("user_id", current_user["id"])
        
        if subject:
            query = query.eq("subject", subject)
        
        result = query.order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        logger.info(f"Retrieved {len(result.data)} submissions for user")
        
        return {
            "submissions": result.data,
            "total": len(result.data),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching submission history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch submissions")


@router.get("/stats")
async def get_pyq_stats(
    current_user = Depends(get_current_user)
):
    """Get user's PYQ performance statistics"""
    try:
        supabase = get_supabase_client()
        
        # Get all submissions
        submissions = supabase.table("pyq_submissions")\
            .select("score, max_score, subject, created_at")\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not submissions.data:
            return {
                "total_submissions": 0,
                "average_score": 0,
                "total_questions_attempted": 0,
                "subject_performance": {},
                "recent_trend": []
            }
        
        # Calculate statistics
        total_submissions = len(submissions.data)
        total_score = sum(s["score"] for s in submissions.data)
        total_max_score = sum(s["max_score"] for s in submissions.data)
        average_score = (total_score / total_max_score * 100) if total_max_score > 0 else 0
        
        # Subject-wise performance
        subject_performance = {}
        for sub in submissions.data:
            subject = sub["subject"]
            if subject not in subject_performance:
                subject_performance[subject] = {
                    "count": 0,
                    "total_score": 0,
                    "total_max_score": 0
                }
            
            subject_performance[subject]["count"] += 1
            subject_performance[subject]["total_score"] += sub["score"]
            subject_performance[subject]["total_max_score"] += sub["max_score"]
        
        # Calculate percentages
        for subject in subject_performance:
            perf = subject_performance[subject]
            perf["percentage"] = (perf["total_score"] / perf["total_max_score"] * 100) if perf["total_max_score"] > 0 else 0
        
        logger.info(f"Retrieved PYQ stats for user: {total_submissions} submissions")
        
        return {
            "total_submissions": total_submissions,
            "average_score": round(average_score, 2),
            "total_questions_attempted": total_submissions,
            "subject_performance": subject_performance,
            "recent_submissions": submissions.data[:5]  # Last 5
        }
        
    except Exception as e:
        logger.error(f"Error fetching PYQ stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")


@router.get("/questions/{question_id}/hints")
async def get_question_hints(
    question_id: str,
    current_user = Depends(get_current_user)
):
    """Get hints for a specific question"""
    try:
        supabase = get_supabase_client()
        
        # Get question details
        question_result = supabase.table("pyq_questions")\
            .select("*")\
            .eq("id", question_id)\
            .execute()
        
        if not question_result.data:
            raise HTTPException(status_code=404, detail="Question not found")
        
        question = question_result.data[0]
        
        # Generate hints using AI
        hints = await pyq_service.get_question_hints(
            question_text=question["question_text"],
            subject=question["subject"]
        )
        
        return {
            "question_id": question_id,
            "hints": hints
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating hints: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate hints")
