#!/usr/bin/env python3
"""
Direct runner for CodeMentor AI Backend - runs from project root
"""

if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path

    # Ensure we're in project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="backend_py/.env", override=False)
    load_dotenv(dotenv_path=".env", override=False)

    # Check for required API keys
    required_keys = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "GEMINI_API_KEY", "TAVILY_API_KEY"]
    missing_keys = [k for k in required_keys if not os.getenv(k)]

    if missing_keys:
        print(f"⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("📝 Please set them in backend_py/.env or .env")
        print("🧪 Continuing anyway...")

    print("🚀 Starting CodeMentor AI Backend...")
    print("🌐 Server will run on http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")

    # Start uvicorn from project root
    import uvicorn
    uvicorn.run(
        "backend_py.main_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["backend_py"]
    )
