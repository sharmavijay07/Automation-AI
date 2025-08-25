@echo off
echo ================================================================
echo 🤖 Enhanced AI Task Automation Assistant (Vaani) - Setup
echo ================================================================
echo.
echo This will set up your enhanced AI assistant with:
echo ✨ Conversational AI (Vaani personality)
echo 📁 Advanced FileSearch across all devices
echo 💬 Enhanced WhatsApp integration
echo 🔄 Multi-agent coordination
echo 🧠 Natural language understanding
echo.

cd /d "%~dp0"

echo 📁 Setting up backend...
cd backend
if not exist ".env" (
    echo 📝 Creating .env file...
    echo # Enhanced AI Assistant Configuration > .env
    echo GROQ_API_KEY=your_groq_api_key_here >> .env
    echo GROQ_MODEL=llama-3.1-70b-versatile >> .env
    echo FASTAPI_HOST=0.0.0.0 >> .env
    echo FASTAPI_PORT=8000 >> .env
    echo. >> .env
    echo # Speech Configuration >> .env
    echo SPEECH_TIMEOUT=7 >> .env
    echo SPEECH_PHRASE_TIME_LIMIT=15 >> .env
    echo AGENT_TEMPERATURE=0.1 >> .env
    echo MAX_RESPONSE_TOKENS=1000 >> .env
    echo.
    echo ✅ .env file created!
    echo ⚠️  IMPORTANT: Please edit .env and add your Groq API key!
) else (
    echo ✅ .env file already exists
)

echo 📦 Installing Python dependencies...
pip install -r requirements.txt

cd ../frontend
echo 📱 Setting up frontend...
if not exist "node_modules" (
    echo 📦 Installing Node.js dependencies...
    npm install
) else (
    echo ✅ Node.js dependencies already installed
)

cd ..
echo.
echo ================================================================
echo 🎉 Enhanced Vaani Setup Complete!
echo ================================================================
echo.
echo Next steps:
echo 1. Edit backend/.env and add your Groq API key
echo 2. Run start_vaani_backend.bat to start the backend
echo 3. Run start_frontend_nextjs.bat to start the frontend
echo 4. Open http://localhost:3000 and meet Vaani!
echo.
echo Features you can try:
echo 🗣️  "Hello Vaani!"
echo 💬 "Send WhatsApp to Mom: I'm coming home"
echo 📁 "Find my photos"
echo 🔍 "Search for report.pdf"
echo 📤 "Send presentation.pptx to boss on WhatsApp"
echo.
pause