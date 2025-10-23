"""
Study Planner Router
Handles AI-generated personalized study plans
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4
from ..dependencies.auth import get_current_user
from ..schemas import StudyPlanRequest, StudyPlanResponse
from ..services.gemini import get_gemini_service
from ..utils.logger import log_api_call, log_error, log_success
from ..utils.supabase_client import get_supabase_client

router = APIRouter(prefix="/api/planner", tags=["planner"])


@router.post("/generate", response_model=StudyPlanResponse)
async def generate_study_plan(
    request: StudyPlanRequest,
    user=Depends(get_current_user)
):
    """Generate a personalized study plan using AI"""
    
    try:
        log_api_call("/api/planner/generate", "POST", user["id"], **request.dict())
        
        # Generate plan using AI
        gemini_service = get_gemini_service()
        
        prompt = f"""
        Create a detailed study plan with the following requirements:
        - Subjects: {', '.join(request.subjects)}
        - Study hours per week: {request.study_hours_per_week}
        - Difficulty level: {request.difficulty_level}
        - Focus areas: {', '.join(request.focus_areas or ['General'])}
        
        Generate a weekly schedule for 4 weeks with:
        1. Daily study sessions with specific topics
        2. Breaks and review sessions
        3. Practice problems and projects
        4. Assessment milestones
        
        Return ONLY valid JSON with this exact structure (no markdown, no code blocks):
        {{
            "weeks": [
                {{
                    "week_number": 1,
                    "days": [
                        {{
                            "day": "Monday",
                            "sessions": [
                                {{
                                    "time": "9:00-10:30",
                                    "subject": "DSA",
                                    "topic": "Arrays and Strings",
                                    "activities": ["Theory", "Practice problems"],
                                    "duration_minutes": 90,
                                    "completed": false
                                }}
                            ]
                        }}
                    ]
                }}
            ],
            "milestones": ["Week 1: Complete basics", "Week 2: Intermediate topics"]
        }}
        """
        
        ai_response = await gemini_service.generate_content(prompt)
        
        # Clean up response - remove markdown code blocks if present
        import json
        clean_response = ai_response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.startswith("```"):
            clean_response = clean_response[3:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()
        
        plan_data = json.loads(clean_response)
        
        # Save to database
        plan_id = str(uuid4())
        supabase = get_supabase_client()
        
        supabase.table("study_plans").insert({
            "id": plan_id,
            "user_id": user["id"],
            "subjects": request.subjects,
            "study_hours_per_week": request.study_hours_per_week,
            "difficulty_level": request.difficulty_level,
            "focus_areas": request.focus_areas or [],
            "schedule": plan_data["weeks"],
            "milestones": plan_data.get("milestones", []),
            "progress": {},
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        log_success(f"Generated study plan: {plan_id}", "PlannerRouter")
        
        return StudyPlanResponse(
            plan_id=plan_id,
            schedule=plan_data["weeks"],
            total_weeks=len(plan_data["weeks"]),
            subjects=request.subjects,
            study_hours_per_week=request.study_hours_per_week,
            status="active",
            milestones=plan_data.get("milestones", [])
        )
        
    except Exception as e:
        log_error(e, "PlannerRouter.generate_study_plan")
        raise HTTPException(status_code=500, detail=f"Failed to generate study plan: {str(e)}")


@router.get("/plans", response_model=List[Dict[str, Any]])
async def get_user_plans(user=Depends(get_current_user)):
    """Get all study plans for the current user"""
    
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("study_plans").select("*").eq(
            "user_id", user["id"]
        ).order("created_at", desc=True).execute()
        
        plans = result.data or []
        
        log_success(f"Retrieved {len(plans)} study plans", "PlannerRouter")
        
        return plans
        
    except Exception as e:
        log_error(e, "PlannerRouter.get_user_plans")
        raise HTTPException(status_code=500, detail="Failed to get study plans")


@router.get("/plans/{plan_id}", response_model=Dict[str, Any])
async def get_plan_details(plan_id: str, user=Depends(get_current_user)):
    """Get details of a specific study plan"""
    
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("study_plans").select("*").eq(
            "id", plan_id
        ).eq("user_id", user["id"]).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Study plan not found")
        
        log_success(f"Retrieved plan details: {plan_id}", "PlannerRouter")
        
        return result.data
        
    except Exception as e:
        log_error(e, "PlannerRouter.get_plan_details")
        raise HTTPException(status_code=500, detail="Failed to get plan details")


@router.put("/plans/{plan_id}/progress")
async def update_plan_progress(
    plan_id: str,
    day: int,
    session_completed: bool,
    user=Depends(get_current_user)
):
    """Update progress on a study plan"""
    
    try:
        supabase = get_supabase_client()
        
        # Get current plan
        result = supabase.table("study_plans").select("progress").eq(
            "id", plan_id
        ).eq("user_id", user["id"]).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Study plan not found")
        
        progress = result.data.get("progress", {})
        progress[str(day)] = session_completed
        
        # Update progress
        supabase.table("study_plans").update({
            "progress": progress
        }).eq("id", plan_id).execute()
        
        log_success(f"Updated plan progress: {plan_id}", "PlannerRouter")
        
        return {"message": "Progress updated", "plan_id": plan_id}
        
    except Exception as e:
        log_error(e, "PlannerRouter.update_plan_progress")
        raise HTTPException(status_code=500, detail="Failed to update progress")


@router.delete("/plans/{plan_id}")
async def delete_plan(plan_id: str, user=Depends(get_current_user)):
    """Delete a study plan"""
    
    try:
        supabase = get_supabase_client()
        
        supabase.table("study_plans").delete().eq(
            "id", plan_id
        ).eq("user_id", user["id"]).execute()
        
        log_success(f"Deleted study plan: {plan_id}", "PlannerRouter")
        
        return {"message": "Study plan deleted successfully"}
        
    except Exception as e:
        log_error(e, "PlannerRouter.delete_plan")
        raise HTTPException(status_code=500, detail="Failed to delete study plan")
