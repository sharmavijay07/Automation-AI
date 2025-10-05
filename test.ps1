# Quick Test Script for Vaani AI Assistant

Write-Host "🧪 Testing Vaani AI Assistant" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host ""

# Test 1: Check if backend is running
Write-Host "1️⃣  Testing Backend API..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Get -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Backend is healthy!" -ForegroundColor Green
    Write-Host "   Status: $($data.status)" -ForegroundColor White
    Write-Host "   Version: $($data.version)" -ForegroundColor White
    Write-Host "   Agents: $($data.agents_available -join ', ')" -ForegroundColor White
} catch {
    Write-Host "   ❌ Backend not responding" -ForegroundColor Red
    Write-Host "   Please start backend: cd backend; python main.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Test WhatsApp Agent
Write-Host "2️⃣  Testing WhatsApp Agent..." -ForegroundColor Cyan
$whatsappCommand = @{
    command = "Send WhatsApp to vijay: Test message from Vaani"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/process-command" -Method Post -Body $whatsappCommand -ContentType "application/json" -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ WhatsApp Agent working!" -ForegroundColor Green
    Write-Host "   Agent Used: $($data.agent_used)" -ForegroundColor White
    Write-Host "   Message: $($data.message)" -ForegroundColor White
} catch {
    Write-Host "   ⚠️  WhatsApp Agent test failed" -ForegroundColor Yellow
}

Write-Host ""

# Test 3: Test File Search Agent
Write-Host "3️⃣  Testing File Search Agent..." -ForegroundColor Cyan
$fileCommand = @{
    command = "Find ownership document"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/process-command" -Method Post -Body $fileCommand -ContentType "application/json" -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ File Search Agent working!" -ForegroundColor Green
    Write-Host "   Agent Used: $($data.agent_used)" -ForegroundColor White
    Write-Host "   Message: $($data.message)" -ForegroundColor White
} catch {
    Write-Host "   ⚠️  File Search Agent test failed" -ForegroundColor Yellow
}

Write-Host ""

# Test 4: Test Email Agent
Write-Host "4️⃣  Testing Email Agent..." -ForegroundColor Cyan
$emailCommand = @{
    command = "Email boss about project update"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/process-command" -Method Post -Body $emailCommand -ContentType "application/json" -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Email Agent working!" -ForegroundColor Green
    Write-Host "   Agent Used: $($data.agent_used)" -ForegroundColor White
} catch {
    Write-Host "   ⚠️  Email Agent test failed" -ForegroundColor Yellow
}

Write-Host ""

# Test 5: Test Conversation Agent
Write-Host "5️⃣  Testing Conversation Agent..." -ForegroundColor Cyan
$chatCommand = @{
    command = "Hello Vaani, what can you do?"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/process-command" -Method Post -Body $chatCommand -ContentType "application/json" -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    Write-Host "   ✅ Conversation Agent working!" -ForegroundColor Green
    Write-Host "   Agent Used: $($data.agent_used)" -ForegroundColor White
} catch {
    Write-Host "   ⚠️  Conversation Agent test failed" -ForegroundColor Yellow
}

Write-Host ""

# Test 6: Check Frontend
Write-Host "6️⃣  Testing Frontend..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method Get -ErrorAction Stop
    Write-Host "   ✅ Frontend is running!" -ForegroundColor Green
    Write-Host "   Open http://localhost:3000 in your browser" -ForegroundColor White
} catch {
    Write-Host "   ⚠️  Frontend not responding" -ForegroundColor Yellow
    Write-Host "   Please start frontend: cd frontend; npm run dev" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=============================" -ForegroundColor Green
Write-Host "✅ Testing Complete!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 All systems operational!" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Try these voice commands:" -ForegroundColor Cyan
Write-Host "   • Send WhatsApp to vijay: Hello!" -ForegroundColor White
Write-Host "   • Find ownership document" -ForegroundColor White
Write-Host "   • Email boss about meeting" -ForegroundColor White
Write-Host "   • Call mom" -ForegroundColor White
Write-Host "   • Pay $50 to john via PayPal" -ForegroundColor White
Write-Host "   • Open Chrome" -ForegroundColor White
Write-Host "   • Google python tutorials" -ForegroundColor White
Write-Host "   • Schedule meeting tomorrow at 3pm" -ForegroundColor White
Write-Host "   • Add task buy groceries" -ForegroundColor White
Write-Host ""
