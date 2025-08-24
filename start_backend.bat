@echo off
echo 🚀 Starting AI Task Automation Assistant Backend
echo ==============================================

echo.
echo 🔧 Checking configuration...
python -c "from config import config; exit(0 if config.validate_config() else 1)"

if %errorlevel% neq 0 (
    echo ❌ Configuration validation failed!
    echo Please update your .env file with a valid GROQ_API_KEY
    echo.
    pause
    exit /b 1
)

echo ✅ Configuration valid!
echo.
echo 🌐 Starting FastAPI server...
echo Server will be available at: http://127.0.0.1:8000
echo.
echo 📝 Logs:
python main.py