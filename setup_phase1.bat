@echo off
echo ============================================
echo 🚀 Phase 1 Setup Script
echo ============================================
echo.

echo [1/3] Installing Backend Dependencies...
cd backend_py
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Backend installation failed!
    pause
    exit /b 1
)
echo ✅ Backend dependencies installed
echo.

echo [2/3] Installing Frontend Dependencies...
cd ..\frontend
call npm install tesseract.js
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Frontend installation failed!
    pause
    exit /b 1
)
echo ✅ Frontend dependencies installed
echo.

echo [3/3] Checking Environment Variables...
cd ..
if exist .env (
    echo ✅ .env file found
    findstr /C:"ASSEMBLYAI_API_KEY" .env >nul
    if %ERRORLEVEL% EQU 0 (
        echo ✅ ASSEMBLYAI_API_KEY is configured
    ) else (
        echo ⚠️  ASSEMBLYAI_API_KEY not found in .env
        echo    Please add: ASSEMBLYAI_API_KEY=your_key_here
    )
) else (
    echo ⚠️  .env file not found
    echo    Please create .env file with required API keys
)
echo.

echo ============================================
echo ✅ Setup Complete!
echo ============================================
echo.
echo Next Steps:
echo 1. Add ASSEMBLYAI_API_KEY to your .env file
echo 2. Run database migration in Supabase (see PHASE1_SETUP_GUIDE.md)
echo 3. Start backend: cd backend_py ^&^& python -m uvicorn app_main:app --reload
echo 4. Test endpoints: http://localhost:8000/docs
echo.
pause
