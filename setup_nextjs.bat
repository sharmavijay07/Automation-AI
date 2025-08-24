@echo off
echo 🤖 AI Task Automation Assistant - Complete Setup
echo ================================================
echo.
echo This will set up both the FastAPI backend and Next.js frontend
echo.

echo 📦 Step 1: Installing Frontend Dependencies...
cd ai-assistant-frontend
call npm install

if %errorlevel% neq 0 (
    echo ❌ Frontend dependency installation failed!
    pause
    exit /b 1
)

echo ✅ Frontend dependencies installed successfully!
echo.

cd ..

echo 🔧 Step 2: Checking Backend Dependencies...
python -c "import fastapi, uvicorn, langchain" 2>NUL
if %errorlevel% neq 0 (
    echo ⚠️  Backend dependencies missing. Installing...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Backend dependency installation failed!
        pause
        exit /b 1
    )
)

echo ✅ Backend dependencies verified!
echo.

echo 🔑 Step 3: Checking Configuration...
python -c "from config import config; print('✅ Configuration loaded!' if config.validate_config() else '⚠️ Please update .env with Groq API key')"

echo.
echo 🎉 Setup Complete!
echo.
echo 📚 Next Steps:
echo   1. Make sure your .env file has a valid GROQ_API_KEY
echo   2. Start the backend: start_backend_nextjs.bat
echo   3. Start the frontend: start_frontend_nextjs.bat  
echo   4. Open http://localhost:3000 in your browser
echo.
echo 🚀 Your AI Assistant with beautiful Next.js interface is ready!
echo.
pause