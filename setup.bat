@echo off
echo 🚀 Setting up CodeMentor AI...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

echo ✅ Node.js found
node --version

REM Setup Backend
echo 📦 Setting up backend...
cd backend

REM Install dependencies
echo Installing backend dependencies...
npm install

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy env.example .env
    echo ⚠️  Please edit backend\.env with your MongoDB URI and Anthropic API key
)

echo ✅ Backend setup complete!

REM Setup Frontend
echo 📦 Setting up frontend...
cd ..\frontend

REM Install dependencies
echo Installing frontend dependencies...
npm install

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    echo VITE_API_URL=http://localhost:5000/api > .env
)

echo ✅ Frontend setup complete!

echo.
echo 🎉 Setup complete! Next steps:
echo 1. Edit backend\.env with your MongoDB URI and Anthropic API key
echo 2. Start backend: cd backend ^&^& npm run dev
echo 3. Start frontend: cd frontend ^&^& npm run dev
echo 4. Open http://localhost:3000 in your browser
echo.
echo Happy coding! 🎓
pause

