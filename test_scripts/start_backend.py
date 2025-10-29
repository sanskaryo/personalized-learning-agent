#!/usr/bin/env python3
"""
Start script for CodeMentor AI Backend
This script starts the backend in test mode if API keys are missing.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_api_keys():
    """Check if API keys are available"""
    
    required_keys = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "GEMINI_API_KEY",
        "TAVILY_API_KEY"
    ]
    
    missing_keys = []
    
    for key in required_keys:
        value = os.getenv(key)
        if not value or value.startswith("your_") or value.startswith("https://your-"):
            missing_keys.append(key)
    
    return missing_keys

def main():
    """Main function"""
    
    print("🚀 Starting CodeMentor AI Backend...")
    
    # Check if we're in the right directory
    if not Path("backend_py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Load env files first (backend_py/.env takes precedence)
    load_dotenv(dotenv_path=Path("backend_py/.env"), override=False)
    load_dotenv(dotenv_path=Path(".env"), override=False)

    # Check API keys
    missing_keys = check_api_keys()
    
    if missing_keys:
        print(f"⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("🧪 Starting in test mode...")
        
        # Enable test mode
        os.environ["TEST_MODE"] = "true"
        
        # Set dummy values
        if "SUPABASE_URL" in missing_keys:
            os.environ["SUPABASE_URL"] = "https://test.supabase.co"
        if "SUPABASE_ANON_KEY" in missing_keys:
            os.environ["SUPABASE_ANON_KEY"] = "test_anon_key"
        if "SUPABASE_SERVICE_ROLE_KEY" in missing_keys:
            os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test_service_key"
        if "GEMINI_API_KEY" in missing_keys:
            os.environ["GEMINI_API_KEY"] = "test_gemini_key"
        if "TAVILY_API_KEY" in missing_keys:
            os.environ["TAVILY_API_KEY"] = "test_tavily_key"
        
        print("✅ Test mode enabled - using dummy API keys")
        print("📝 To use full features, set up your API keys in backend_py/.env")
    else:
        print("✅ All API keys found - starting in full mode")
    
    # Change to backend directory
    os.chdir("backend_py")
    
    # Start the server
    print("🌐 Starting server on http://localhost:8000")
    print("📚 API docs available at http://localhost:8000/docs")
    
    try:
        import uvicorn
        # Our FastAPI app lives in main_app.py inside backend_py
        uvicorn.run("main_app:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
