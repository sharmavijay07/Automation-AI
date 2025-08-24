@echo off
echo 🚀 AI Task Automation Assistant - Setup Script
echo ================================================

echo.
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ✅ Dependencies installed successfully!

echo.
echo 🔧 Checking configuration...
python -c "from config import config; print('✅ Configuration loaded successfully!' if config.validate_config() else '⚠️ Please update your .env file with valid API keys')"

echo.
echo 🎯 Setup complete! 
echo.
echo Next steps:
echo 1. Update .env file with your Groq API key
echo 2. Run 'start_backend.bat' to start the FastAPI server
echo 3. Run 'start_frontend.bat' to start the Streamlit frontend
echo.
pause