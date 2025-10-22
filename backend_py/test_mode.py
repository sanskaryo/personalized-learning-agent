"""
Test mode for CodeMentor AI Backend
This allows the backend to start without all API keys for testing purposes.
"""

import os
from typing import Optional

def enable_test_mode():
    """Enable test mode by setting environment variables"""
    
    # Set test mode flag
    os.environ["TEST_MODE"] = "true"
    
    # Set dummy values for missing API keys
    if not os.getenv("SUPABASE_URL"):
        os.environ["SUPABASE_URL"] = "https://test.supabase.co"
    
    if not os.getenv("SUPABASE_ANON_KEY"):
        os.environ["SUPABASE_ANON_KEY"] = "test_anon_key"
    
    if not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test_service_key"
    
    if not os.getenv("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = "test_gemini_key"
    
    if not os.getenv("TAVILY_API_KEY"):
        os.environ["TAVILY_API_KEY"] = "test_tavily_key"
    
    print("🧪 Test mode enabled - using dummy API keys")

def is_test_mode() -> bool:
    """Check if test mode is enabled"""
    return os.getenv("TEST_MODE") == "true"

def get_test_response() -> str:
    """Get a test response for AI features"""
    return "This is a test response. Please set up your API keys to use the full features."

def get_test_resources() -> list:
    """Get test resources for resource search"""
    return [
        {
            "title": "Test Resource 1",
            "url": "https://example.com/resource1",
            "content": "This is a test resource for demonstration purposes.",
            "excerpts": ["Test excerpt 1", "Test excerpt 2"],
            "resource_type": "documentation",
            "difficulty_level": "beginner",
            "quality_score": 0.8,
            "relevance_score": 0.9,
            "domain": "example.com",
            "last_updated": "2024-01-01"
        },
        {
            "title": "Test Resource 2",
            "url": "https://example.com/resource2",
            "content": "Another test resource for demonstration purposes.",
            "excerpts": ["Test excerpt 3", "Test excerpt 4"],
            "resource_type": "video",
            "difficulty_level": "intermediate",
            "quality_score": 0.7,
            "relevance_score": 0.8,
            "domain": "example.com",
            "last_updated": "2024-01-02"
        }
    ]
