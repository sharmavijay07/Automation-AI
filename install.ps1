# Installation and Setup Script for Vaani AI Assistant

Write-Host "🚀 Vaani AI Assistant - Installation Script" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Check Python version
Write-Host "1️⃣  Checking Python version..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python not found! Please install Python 3.11 or higher." -ForegroundColor Red
    exit 1
}

# Navigate to backend
Write-Host ""
Write-Host "2️⃣  Setting up backend..." -ForegroundColor Cyan
Set-Location -Path "backend"

# Create virtual environment
Write-Host "   Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "   Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "   Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "   ✅ Backend setup complete!" -ForegroundColor Green

# Check for .env file
Write-Host ""
Write-Host "3️⃣  Checking configuration..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host "   ✅ .env file found" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  .env file not found - using defaults" -ForegroundColor Yellow
}

# Navigate to frontend
Write-Host ""
Write-Host "4️⃣  Setting up frontend..." -ForegroundColor Cyan
Set-Location -Path "..\frontend"

# Check Node.js version
try {
    $nodeVersion = node --version 2>&1
    Write-Host "   ✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Node.js not found! Please install Node.js 18 or higher." -ForegroundColor Red
    Set-Location -Path ".."
    exit 1
}

# Install frontend dependencies
Write-Host "   Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

Write-Host "   ✅ Frontend setup complete!" -ForegroundColor Green

# Return to root
Set-Location -Path ".."

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "✅ Installation Complete!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Add your Groq API key to backend/.env" -ForegroundColor White
Write-Host "   2. Run backend: cd backend; python main.py" -ForegroundColor White
Write-Host "   3. Run frontend (new terminal): cd frontend; npm run dev" -ForegroundColor White
Write-Host "   4. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host ""
Write-Host "🎤 Try saying: 'Send WhatsApp to vijay: Hello!'" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   - QUICKSTART.md - 5-minute guide" -ForegroundColor White
Write-Host "   - README_COMPLETE_GUIDE.md - Full documentation" -ForegroundColor White
Write-Host "   - IMPLEMENTATION_SUMMARY.md - What's included" -ForegroundColor White
Write-Host ""
