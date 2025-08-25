@echo off
echo ================================================
echo 🤖 Starting Enhanced AI Assistant Backend (Vaani)
echo ================================================
echo.
echo Features:
echo ✨ Conversational AI with Vaani personality
echo 📁 FileSearch Agent with cross-platform support
echo 🔄 Multi-agent coordination workflows
echo 💬 Enhanced natural language processing
echo.

cd /d "%~dp0backend"

echo 🔍 Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo 📦 Installing/updating dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ⚠️ Some dependencies failed to install. The system may still work.
)

echo.
echo 🚀 Starting Enhanced Vaani Backend...
echo 🌐 Backend will be available at: http://localhost:8000
echo 🧠 Features: Conversation, WhatsApp, FileSearch
echo.

python main.py

echo.
echo 👋 Vaani backend stopped.
pause