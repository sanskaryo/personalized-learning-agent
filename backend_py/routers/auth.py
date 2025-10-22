from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from ..utils.supabase_client import get_supabase_client
from ..utils.logger import log_success, log_error, log_api_call
from ..dependencies.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Pydantic models for request/response
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    year: Optional[str] = "2nd"
    subjects: Optional[List[str]] = []
    learningStyle: Optional[str] = "visual"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdateRequest(BaseModel):
    username: Optional[str] = None
    year: Optional[str] = None
    subjects: Optional[List[str]] = None
    learningStyle: Optional[str] = None


class AuthResponse(BaseModel):
    token: str
    user: dict


class ProfileResponse(BaseModel):
    user: dict


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    """
    Register a new user with Supabase Auth and create user profile
    """
    try:
        log_api_call("/api/auth/register", "POST", payload.email)
        
        supabase = get_supabase_client()
        
        # Validate password length
        if len(payload.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        # Create user with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password,
            "options": {
                "data": {
                    "username": payload.username,
                }
            }
        })
        
        if not auth_response.user:
            log_error(Exception("Registration failed"), "Auth.Register")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed. User may already exist."
            )
        
        user_id = auth_response.user.id
        token = auth_response.session.access_token if auth_response.session else None
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate authentication token"
            )
        
        # Create user profile in database
        try:
            profile_data = {
                "id": user_id,
                "username": payload.username,
                "email": payload.email,
                "year": payload.year,
                "subjects": payload.subjects,
                "learning_style": payload.learningStyle,
            }
            
            supabase.table("users").insert(profile_data).execute()
            
        except Exception as e:
            log_error(e, "Auth.Register.Profile")
            # If profile creation fails, we still have the auth user
            # Log the error but don't fail the registration
        
        user_data = {
            "id": user_id,
            "username": payload.username,
            "email": payload.email,
            "year": payload.year,
            "subjects": payload.subjects,
            "learningStyle": payload.learningStyle,
        }
        
        log_success(f"User registered successfully: {payload.email}", "Auth.Register")
        
        return AuthResponse(
            token=token,
            user=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, "Auth.Register")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    """
    Login user with Supabase Auth
    """
    try:
        log_api_call("/api/auth/login", "POST", payload.email)
        
        supabase = get_supabase_client()
        
        # Sign in with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password
        })
        
        if not auth_response.user or not auth_response.session:
            log_error(Exception("Invalid credentials"), "Auth.Login")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user_id = auth_response.user.id
        token = auth_response.session.access_token
        
        # Get user profile from database
        try:
            profile_response = supabase.table("users").select("*").eq("id", user_id).execute()
            
            if profile_response.data and len(profile_response.data) > 0:
                profile = profile_response.data[0]
                user_data = {
                    "id": user_id,
                    "username": profile.get("username", ""),
                    "email": auth_response.user.email,
                    "year": profile.get("year", "2nd"),
                    "subjects": profile.get("subjects", []),
                    "learningStyle": profile.get("learning_style", "visual"),
                }
            else:
                # Fallback if profile doesn't exist
                user_data = {
                    "id": user_id,
                    "username": auth_response.user.email.split("@")[0],
                    "email": auth_response.user.email,
                    "year": "2nd",
                    "subjects": [],
                    "learningStyle": "visual",
                }
        except Exception as e:
            log_error(e, "Auth.Login.Profile")
            # Fallback user data
            user_data = {
                "id": user_id,
                "username": auth_response.user.email.split("@")[0],
                "email": auth_response.user.email,
                "year": "2nd",
                "subjects": [],
                "learningStyle": "visual",
            }
        
        log_success(f"User logged in successfully: {payload.email}", "Auth.Login")
        
        return AuthResponse(
            token=token,
            user=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, "Auth.Login")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(user=Depends(get_current_user)):
    """
    Get current user's profile
    """
    try:
        log_api_call("/api/auth/profile", "GET", user.get("id", ""))
        
        supabase = get_supabase_client()
        user_id = user.get("id")
        
        # Get user profile from database
        profile_response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not profile_response.data or len(profile_response.data) == 0:
            # Return basic user data from auth
            user_data = {
                "id": user_id,
                "username": user.get("email", "").split("@")[0],
                "email": user.get("email", ""),
                "year": "2nd",
                "subjects": [],
                "learningStyle": "visual",
            }
        else:
            profile = profile_response.data[0]
            user_data = {
                "id": user_id,
                "username": profile.get("username", ""),
                "email": user.get("email", ""),
                "year": profile.get("year", "2nd"),
                "subjects": profile.get("subjects", []),
                "learningStyle": profile.get("learning_style", "visual"),
            }
        
        log_success(f"Profile retrieved for user: {user_id}", "Auth.Profile")
        
        return ProfileResponse(user=user_data)
        
    except Exception as e:
        log_error(e, "Auth.Profile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(payload: ProfileUpdateRequest, user=Depends(get_current_user)):
    """
    Update current user's profile
    """
    try:
        log_api_call("/api/auth/profile", "PUT", user.get("id", ""))
        
        supabase = get_supabase_client()
        user_id = user.get("id")
        
        # Build update data (only include provided fields)
        update_data = {}
        if payload.username is not None:
            update_data["username"] = payload.username
        if payload.year is not None:
            update_data["year"] = payload.year
        if payload.subjects is not None:
            update_data["subjects"] = payload.subjects
        if payload.learningStyle is not None:
            update_data["learning_style"] = payload.learningStyle
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Update user profile in database
        supabase.table("users").update(update_data).eq("id", user_id).execute()
        
        # Get updated profile
        profile_response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if profile_response.data and len(profile_response.data) > 0:
            profile = profile_response.data[0]
            user_data = {
                "id": user_id,
                "username": profile.get("username", ""),
                "email": user.get("email", ""),
                "year": profile.get("year", "2nd"),
                "subjects": profile.get("subjects", []),
                "learningStyle": profile.get("learning_style", "visual"),
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        log_success(f"Profile updated for user: {user_id}", "Auth.UpdateProfile")
        
        return ProfileResponse(user=user_data)
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, "Auth.UpdateProfile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/logout")
async def logout(user=Depends(get_current_user)):
    """
    Logout current user (mostly client-side, but can revoke token server-side)
    """
    try:
        log_api_call("/api/auth/logout", "POST", user.get("id", ""))
        
        supabase = get_supabase_client()
        
        # Sign out from Supabase
        try:
            supabase.auth.sign_out()
        except:
            pass  # Ignore errors as logout is mainly client-side
        
        log_success(f"User logged out: {user.get('id', '')}", "Auth.Logout")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        log_error(e, "Auth.Logout")
        # Don't fail logout even if there's an error
        return {"message": "Logged out successfully"}
