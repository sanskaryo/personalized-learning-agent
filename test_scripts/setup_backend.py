#!/usr/bin/env python3
"""
Setup script for CodeMentor AI Backend
This script helps you set up the environment variables and test the backend.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with template values"""
    
    env_content = """# Server Configuration
APP_NAME=codementor-ai-fastapi
APP_ENV=development
PORT=8000
CORS_ORIGINS=http://localhost:3000

# Supabase Configuration (Required for database)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Google Gemini API (Required for AI chat)
GEMINI_API_KEY=your_gemini_api_key

# Tavily API (Required for resource search)
TAVILY_API_KEY=your_tavily_api_key
"""
    
    env_path = Path("backend_py/.env")
    
    if env_path.exists():
        print("✅ .env file already exists")
        return
    
    try:
        env_path.write_text(env_content)
        print("✅ Created .env file template")
        print("📝 Please edit backend_py/.env and add your actual API keys")
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")

def check_environment():
    """Check if environment variables are properly set"""
    
    print("\n🔍 Checking environment variables...")
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "GEMINI_API_KEY",
        "TAVILY_API_KEY"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("your_") or value.startswith("https://your-"):
            missing_vars.append(var)
            print(f"❌ {var}: Not set or using template value")
        else:
            print(f"✅ {var}: Set")
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("📝 Please edit backend_py/.env and add your actual API keys")
        return False
    else:
        print("\n✅ All environment variables are set!")
        return True

def test_backend():
    """Test if the backend can start"""
    
    print("\n🧪 Testing backend startup...")
    
    try:
        # Change to backend directory
        os.chdir("backend_py")
        
        # Import and test
        from config import get_settings
        settings = get_settings()
        print("✅ Configuration loaded successfully")
        
        # Test service imports
        try:
            from services.tavily_service import get_tavily_service
            print("✅ Tavily service can be imported")
        except Exception as e:
            print(f"⚠️  Tavily service import failed: {e}")
        
        try:
            from services.pdf_service import get_pdf_service
            print("✅ PDF service can be imported")
        except Exception as e:
            print(f"⚠️  PDF service import failed: {e}")
        
        print("\n✅ Backend is ready to start!")
        return True
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def main():
    """Main setup function"""
    
    print("🚀 CodeMentor AI Backend Setup")
    print("=" * 40)
    
    # Create .env file if it doesn't exist
    create_env_file()
    
    # Check environment variables
    env_ok = check_environment()
    
    if not env_ok:
        print("\n📋 Next steps:")
        print("1. Get your API keys:")
        print("   - Supabase: https://supabase.com")
        print("   - Gemini: https://aistudio.google.com/")
        print("   - Tavily: https://tavily.com")
        print("2. Edit backend_py/.env with your actual keys")
        print("3. Run this script again to test")
        return
    
    # Test backend
    test_ok = test_backend()
    
    if test_ok:
        print("\n🎉 Setup complete! You can now start the backend:")
        print("   cd backend_py")
        print("   uvicorn main:app --reload --port 8000")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main()
