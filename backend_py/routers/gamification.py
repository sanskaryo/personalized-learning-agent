"""
Gamification Router
Handles user points, achievements, streaks, and leaderboard
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict
import math

from ..schemas import UserStats, Achievement, LeaderboardEntry
from ..dependencies.auth import get_current_user
from ..utils.supabase_client import get_supabase_client
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/gamification", tags=["gamification"])


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user = Depends(get_current_user)
):
    """
    Get user's gamification statistics
    
    Returns streak, points, level, achievements, and progress
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["id"]
        
        logger.info(f"Fetching gamification stats for user {user_id}")
        
        # Calculate streak from study sessions
        streak = await calculate_streak(user_id, supabase)
        
        # Get total points
        points_result = supabase.table("user_points")\
            .select("points")\
            .eq("user_id", user_id)\
            .execute()
        
        total_points = sum(p["points"] for p in points_result.data) if points_result.data else 0
        
        # Calculate level
        level = calculate_level(total_points)
        next_level_points = calculate_next_level_points(total_points)
        
        # Get achievements
        achievements_result = supabase.table("user_achievements")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("unlocked_at", desc=True)\
            .execute()
        
        achievements = achievements_result.data if achievements_result.data else []
        
        # Calculate daily goal progress (assumed 2 hours = 100%)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        sessions_today = supabase.table("study_sessions")\
            .select("duration_seconds")\
            .eq("user_id", user_id)\
            .gte("created_at", today_start.isoformat())\
            .execute()
        
        total_seconds_today = sum(s.get("duration_seconds", 0) for s in sessions_today.data) if sessions_today.data else 0
        daily_goal_progress = min((total_seconds_today / (2 * 3600)) * 100, 100)  # 2 hours = 100%
        
        # Calculate weekly study hours
        week_start = datetime.utcnow() - timedelta(days=7)
        
        sessions_week = supabase.table("study_sessions")\
            .select("duration_seconds")\
            .eq("user_id", user_id)\
            .gte("created_at", week_start.isoformat())\
            .execute()
        
        total_seconds_week = sum(s.get("duration_seconds", 0) for s in sessions_week.data) if sessions_week.data else 0
        weekly_study_hours = total_seconds_week / 3600
        
        logger.info(f"Stats calculated: Level {level}, {total_points} points, {streak} day streak")
        
        return UserStats(
            streak=streak,
            total_points=total_points,
            level=level,
            next_level_points=next_level_points,
            achievements=achievements,
            daily_goal_progress=round(daily_goal_progress, 2),
            weekly_study_hours=round(weekly_study_hours, 2)
        )
        
    except Exception as e:
        logger.error(f"Error fetching user stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 50,
    period: str = "all_time"  # "all_time", "weekly", "monthly"
):
    """
    Get global leaderboard
    
    - **limit**: Number of users to return (max 100)
    - **period**: Time period (all_time, weekly, monthly)
    """
    try:
        supabase = get_supabase_client()
        
        # Determine time filter
        time_filter = None
        if period == "weekly":
            time_filter = datetime.utcnow() - timedelta(days=7)
        elif period == "monthly":
            time_filter = datetime.utcnow() - timedelta(days=30)
        
        # Get points with user info
        query = supabase.table("user_points").select("user_id, points, created_at")
        
        if time_filter:
            query = query.gte("created_at", time_filter.isoformat())
        
        points_result = query.execute()
        
        # Aggregate points by user
        user_points = {}
        for p in points_result.data:
            user_id = p["user_id"]
            points = p["points"]
            
            if user_id not in user_points:
                user_points[user_id] = 0
            user_points[user_id] += points
        
        # Sort by points
        sorted_users = sorted(user_points.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        # Build leaderboard with user info
        leaderboard = []
        for rank, (user_id, points) in enumerate(sorted_users, 1):
            # Get user info
            user_result = supabase.table("users")\
                .select("email")\
                .eq("id", user_id)\
                .execute()
            
            username = user_result.data[0]["email"].split("@")[0] if user_result.data else "Anonymous"
            
            # Calculate streak
            streak = await calculate_streak(user_id, supabase)
            
            leaderboard.append(
                LeaderboardEntry(
                    rank=rank,
                    user_id=user_id,
                    username=username,
                    points=points,
                    level=calculate_level(points),
                    streak=streak
                )
            )
        
        logger.info(f"Generated leaderboard with {len(leaderboard)} entries for period: {period}")
        
        return {
            "leaderboard": leaderboard,
            "period": period,
            "total_users": len(leaderboard)
        }
        
    except Exception as e:
        logger.error(f"Error generating leaderboard: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate leaderboard")


@router.post("/check-achievements")
async def check_and_unlock_achievements(
    current_user = Depends(get_current_user)
):
    """
    Check and unlock new achievements for user
    
    Automatically called after major actions
    """
    try:
        supabase = get_supabase_client()
        user_id = current_user["id"]
        
        logger.info(f"Checking achievements for user {user_id}")
        
        newly_unlocked = []
        
        # Get existing achievements
        existing = supabase.table("user_achievements")\
            .select("achievement_type")\
            .eq("user_id", user_id)\
            .execute()
        
        existing_types = set(a["achievement_type"] for a in existing.data) if existing.data else set()
        
        # Define achievement checks
        achievements_to_check = [
            {
                "type": "first_note",
                "title": "First Note",
                "description": "Created your first note",
                "icon_url": "📝",
                "rarity": "common",
                "check": lambda: check_notes_count(user_id, supabase, 1)
            },
            {
                "type": "note_master",
                "title": "Note Master",
                "description": "Created 50 notes",
                "icon_url": "📚",
                "rarity": "rare",
                "check": lambda: check_notes_count(user_id, supabase, 50)
            },
            {
                "type": "week_streak",
                "title": "Week Warrior",
                "description": "Maintained a 7-day study streak",
                "icon_url": "🔥",
                "rarity": "uncommon",
                "check": lambda: check_streak(user_id, supabase, 7)
            },
            {
                "type": "month_streak",
                "title": "Month Dominator",
                "description": "Maintained a 30-day study streak",
                "icon_url": "💪",
                "rarity": "epic",
                "check": lambda: check_streak(user_id, supabase, 30)
            },
            {
                "type": "pyq_master",
                "title": "PYQ Master",
                "description": "Completed 20 practice questions",
                "icon_url": "🎯",
                "rarity": "rare",
                "check": lambda: check_pyq_count(user_id, supabase, 20)
            },
            {
                "type": "flashcard_creator",
                "title": "Flashcard Creator",
                "description": "Generated 100 flashcards",
                "icon_url": "🎴",
                "rarity": "rare",
                "check": lambda: check_flashcard_count(user_id, supabase, 100)
            }
        ]
        
        # Check each achievement
        for achievement in achievements_to_check:
            if achievement["type"] not in existing_types:
                if await achievement["check"]():
                    # Unlock achievement
                    achievement_data = {
                        "user_id": user_id,
                        "achievement_type": achievement["type"],
                        "title": achievement["title"],
                        "description": achievement["description"],
                        "icon_url": achievement["icon_url"],
                        "rarity": achievement["rarity"],
                        "unlocked_at": datetime.utcnow().isoformat()
                    }
                    
                    result = supabase.table("user_achievements").insert(achievement_data).execute()
                    
                    if result.data:
                        newly_unlocked.append(achievement)
                        logger.info(f"Unlocked achievement: {achievement['title']}")
                        
                        # Award points
                        points = {"common": 10, "uncommon": 25, "rare": 50, "epic": 100, "legendary": 200}
                        
                        points_data = {
                            "user_id": user_id,
                            "points": points.get(achievement["rarity"], 10),
                            "action_type": "achievement_unlocked",
                            "created_at": datetime.utcnow().isoformat()
                        }
                        
                        supabase.table("user_points").insert(points_data).execute()
        
        return {
            "newly_unlocked": newly_unlocked,
            "total_new": len(newly_unlocked),
            "message": f"Unlocked {len(newly_unlocked)} new achievements!" if newly_unlocked else "No new achievements"
        }
        
    except Exception as e:
        logger.error(f"Error checking achievements: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to check achievements")


# Helper functions

async def calculate_streak(user_id: str, supabase) -> int:
    """Calculate user's current study streak"""
    try:
        sessions = supabase.table("study_sessions")\
            .select("created_at")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(100)\
            .execute()
        
        if not sessions.data:
            return 0
        
        streak = 1
        last_date = datetime.fromisoformat(sessions.data[0]["created_at"].replace('Z', '+00:00')).date()
        current_date = datetime.utcnow().date()
        
        # Check if user studied today or yesterday
        if (current_date - last_date).days > 1:
            return 0
        
        for session in sessions.data[1:]:
            session_date = datetime.fromisoformat(session["created_at"].replace('Z', '+00:00')).date()
            
            if (last_date - session_date).days == 1:
                streak += 1
                last_date = session_date
            elif (last_date - session_date).days == 0:
                continue  # Same day
            else:
                break
        
        return streak
        
    except Exception as e:
        logger.error(f"Error calculating streak: {str(e)}")
        return 0


def calculate_level(points: int) -> int:
    """Calculate user level from points"""
    # Level formula: Level = floor(sqrt(points / 100)) + 1
    return int(math.sqrt(points / 100)) + 1


def calculate_next_level_points(points: int) -> int:
    """Calculate points needed for next level"""
    current_level = calculate_level(points)
    next_level_total = (current_level ** 2) * 100
    return next_level_total - points


async def check_notes_count(user_id: str, supabase, threshold: int) -> bool:
    """Check if user has created enough notes"""
    result = supabase.table("notes").select("id", count="exact").eq("user_id", user_id).execute()
    return result.count >= threshold if hasattr(result, 'count') else len(result.data) >= threshold


async def check_streak(user_id: str, supabase, days: int) -> bool:
    """Check if user has maintained streak"""
    current_streak = await calculate_streak(user_id, supabase)
    return current_streak >= days


async def check_pyq_count(user_id: str, supabase, threshold: int) -> bool:
    """Check if user has completed enough PYQs"""
    result = supabase.table("pyq_submissions").select("id", count="exact").eq("user_id", user_id).execute()
    return result.count >= threshold if hasattr(result, 'count') else len(result.data) >= threshold


async def check_flashcard_count(user_id: str, supabase, threshold: int) -> bool:
    """Check if user has created enough flashcards"""
    result = supabase.table("flashcards").select("id", count="exact").eq("user_id", user_id).execute()
    return result.count >= threshold if hasattr(result, 'count') else len(result.data) >= threshold
