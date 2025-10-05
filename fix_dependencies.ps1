# Fix and Reinstall Dependencies Script

Write-Host "🔧 Fixing Vaani Dependencies" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host ""

# Navigate to backend
Set-Location -Path "backend"

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
} else {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "📦 Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install/Upgrade core dependencies first
Write-Host ""
Write-Host "📦 Installing core dependencies..." -ForegroundColor Cyan
pip install --upgrade pydantic>=2.0
pip install --upgrade langchain
pip install --upgrade langchain-groq
pip install --upgrade langchain-core
pip install --upgrade langchain-community
pip install --upgrade langgraph

# Install all requirements
Write-Host ""
Write-Host "📦 Installing all requirements..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host ""
Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
Write-Host ""

# Test imports
Write-Host "🧪 Testing imports..." -ForegroundColor Cyan
python -c "from langchain.tools import BaseTool; print('✅ LangChain OK')"
python -c "from langchain_groq import ChatGroq; print('✅ Groq OK')"
python -c "from langgraph.graph import StateGraph, END; print('✅ LangGraph OK')"
python -c "from fastapi import FastAPI; print('✅ FastAPI OK')"
python -c "from pydantic import BaseModel; print('✅ Pydantic OK')"

Write-Host ""
Write-Host "=============================" -ForegroundColor Green
Write-Host "✅ All Fixed!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Now you can run:" -ForegroundColor Cyan
Write-Host "   python main.py" -ForegroundColor White
Write-Host ""

Set-Location -Path ".."
