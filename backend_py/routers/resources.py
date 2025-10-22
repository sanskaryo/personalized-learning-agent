from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..dependencies.auth import get_current_user
from ..schemas import ResourceSearchRequest, ResourceResponse, ResourceList
from ..services.tavily_service import get_tavily_service
from ..utils.logger import log_api_call, log_error, log_success
import asyncio

router = APIRouter(prefix="/api/resources", tags=["resources"])

@router.post("/search", response_model=ResourceList)
async def search_resources(
    request: ResourceSearchRequest,
    user=Depends(get_current_user)
):
    """Search for educational resources using Tavily API"""
    
    try:
        log_api_call("/api/resources/search", "POST", user["id"], **request.dict())
        
        # Search for resources
        tavily_service = get_tavily_service()
        resources = await tavily_service.search_resources(
            query=request.query,
            subject=request.subject,
            difficulty=request.difficulty,
            resource_type=request.resource_type,
            max_results=request.max_results or 10
        )
        
        log_success(f"Found {len(resources)} resources for query: {request.query}", "ResourceRouter")
        
        return ResourceList(
            resources=resources,
            total_count=len(resources),
            query=request.query,
            filters={
                "subject": request.subject,
                "difficulty": request.difficulty,
                "resource_type": request.resource_type
            }
        )
        
    except Exception as e:
        log_error(e, "ResourceRouter.search_resources")
        raise HTTPException(status_code=500, detail="Failed to search resources")

@router.get("/trending", response_model=ResourceList)
async def get_trending_resources(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    limit: int = Query(10, description="Number of resources to return"),
    user=Depends(get_current_user)
):
    """Get trending educational resources"""
    
    try:
        log_api_call("/api/resources/trending", "GET", user["id"], subject=subject, limit=limit)
        
        # Build trending query based on subject
        if subject and subject != "General":
            trending_query = f"trending {subject} programming tutorial course 2024"
        else:
            trending_query = "trending programming computer science tutorial course 2024"
        
        # Search for trending resources
        tavily_service = get_tavily_service()
        resources = await tavily_service.search_resources(
            query=trending_query,
            subject=subject,
            max_results=limit
        )
        
        log_success(f"Found {len(resources)} trending resources", "ResourceRouter")
        
        return ResourceList(
            resources=resources,
            total_count=len(resources),
            query=trending_query,
            filters={"subject": subject, "trending": True}
        )
        
    except Exception as e:
        log_error(e, "ResourceRouter.get_trending_resources")
        raise HTTPException(status_code=500, detail="Failed to get trending resources")

@router.get("/recommended", response_model=ResourceList)
async def get_recommended_resources(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    limit: int = Query(10, description="Number of resources to return"),
    user=Depends(get_current_user)
):
    """Get recommended resources based on user preferences"""
    
    try:
        log_api_call("/api/resources/recommended", "GET", user["id"], 
                    subject=subject, difficulty=difficulty, limit=limit)
        
        # Build recommendation query
        if subject and subject != "General":
            rec_query = f"best {subject} learning resources tutorial course"
        else:
            rec_query = "best programming computer science learning resources tutorial course"
        
        if difficulty:
            rec_query += f" {difficulty} level"
        
        # Search for recommended resources
        tavily_service = get_tavily_service()
        resources = await tavily_service.search_resources(
            query=rec_query,
            subject=subject,
            difficulty=difficulty,
            max_results=limit
        )
        
        log_success(f"Found {len(resources)} recommended resources", "ResourceRouter")
        
        return ResourceList(
            resources=resources,
            total_count=len(resources),
            query=rec_query,
            filters={
                "subject": subject,
                "difficulty": difficulty,
                "recommended": True
            }
        )
        
    except Exception as e:
        log_error(e, "ResourceRouter.get_recommended_resources")
        raise HTTPException(status_code=500, detail="Failed to get recommended resources")

@router.get("/subjects")
async def get_available_subjects(user=Depends(get_current_user)):
    """Get list of available subjects for resource filtering"""
    
    try:
        subjects = [
            {"id": "general", "name": "General", "description": "General programming topics"},
            {"id": "dsa", "name": "DSA", "description": "Data Structures and Algorithms"},
            {"id": "os", "name": "OS", "description": "Operating Systems"},
            {"id": "dbms", "name": "DBMS", "description": "Database Management Systems"},
            {"id": "cn", "name": "CN", "description": "Computer Networks"},
            {"id": "se", "name": "SE", "description": "Software Engineering"},
            {"id": "ai", "name": "AI", "description": "Artificial Intelligence"},
            {"id": "ml", "name": "ML", "description": "Machine Learning"},
            {"id": "web", "name": "Web Dev", "description": "Web Development"},
            {"id": "mobile", "name": "Mobile Dev", "description": "Mobile Development"}
        ]
        
        log_success("Retrieved available subjects", "ResourceRouter")
        
        return {"subjects": subjects}
        
    except Exception as e:
        log_error(e, "ResourceRouter.get_available_subjects")
        raise HTTPException(status_code=500, detail="Failed to get subjects")

@router.get("/types")
async def get_resource_types(user=Depends(get_current_user)):
    """Get list of available resource types"""
    
    try:
        resource_types = [
            {"id": "video", "name": "Video Tutorials", "description": "Video-based learning content"},
            {"id": "course", "name": "Online Courses", "description": "Structured online courses"},
            {"id": "documentation", "name": "Documentation", "description": "Technical documentation and guides"},
            {"id": "practice", "name": "Practice Exercises", "description": "Coding exercises and problems"},
            {"id": "paper", "name": "Academic Papers", "description": "Research papers and articles"}
        ]
        
        log_success("Retrieved resource types", "ResourceRouter")
        
        return {"resource_types": resource_types}
        
    except Exception as e:
        log_error(e, "ResourceRouter.get_resource_types")
        raise HTTPException(status_code=500, detail="Failed to get resource types")

@router.get("/difficulties")
async def get_difficulty_levels(user=Depends(get_current_user)):
    """Get list of available difficulty levels"""
    
    try:
        difficulties = [
            {"id": "beginner", "name": "Beginner", "description": "Introductory level content"},
            {"id": "intermediate", "name": "Intermediate", "description": "Intermediate level content"},
            {"id": "advanced", "name": "Advanced", "description": "Advanced level content"}
        ]
        
        log_success("Retrieved difficulty levels", "ResourceRouter")
        
        return {"difficulties": difficulties}
        
    except Exception as e:
        log_error(e, "ResourceRouter.get_difficulty_levels")
        raise HTTPException(status_code=500, detail="Failed to get difficulty levels")
