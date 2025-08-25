# 🚀 Production Deployment Guide - Vaani Conversational AI

## 📋 Environment Variables Configuration

### 🔑 Required Configuration (MUST SET)

```env
# Get your free Groq API key from https://console.groq.com/
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 🎤 Voice & TTS Configuration (Free Options)

```env
# Best free TTS engine (Microsoft Edge TTS - Excellent quality)
TTS_ENGINE=edge
VAANI_VOICE=en-US-AriaNeural
VAANI_VOICE_SPEED=1.0
ENABLE_VOICE_FEEDBACK=true

# Alternative TTS engines (all free):
# TTS_ENGINE=coqui          # Open source neural TTS
# TTS_ENGINE=pyttsx3        # System TTS (always works)
# TTS_ENGINE=gtts           # Google TTS
```

### 📊 Database Configuration (Optional)

```env
# Local MongoDB (free)
MONGODB_URL=mongodb://localhost:27017

# Or MongoDB Atlas (free tier)
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net

MONGODB_DATABASE=vaani_assistant
```

### 🔧 Advanced Configuration

```env
# AI Processing
GROQ_MODEL=llama-3.1-70b-versatile
AGENT_TEMPERATURE=0.1
MAX_RESPONSE_TOKENS=1000

# Speech Recognition
SPEECH_TIMEOUT=7
SPEECH_PHRASE_TIME_LIMIT=15

# Server Settings
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

## 🏗️ Installation & Setup

### 1. Quick Setup (Recommended)
```bash
# Run the automated setup
setup_enhanced_vaani.bat

# Edit your environment file
notepad backend/.env

# Add your Groq API key and save
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 2. Manual Installation
```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies  
cd ../frontend
npm install
```

### 3. Optional: MongoDB Setup

#### Option A: Local MongoDB (Recommended for Development)
```bash
# Download and install MongoDB Community Server
# https://www.mongodb.com/try/download/community
# Start MongoDB service
net start MongoDB
```

#### Option B: MongoDB Atlas (Cloud - Free Tier)
```bash
# 1. Create account at https://www.mongodb.com/atlas
# 2. Create free cluster
# 3. Get connection string
# 4. Update MONGODB_URL in .env
```

## 🚀 Starting the Application

### Backend (Enhanced AI Engine)
```bash
# Option 1: Using batch file
start_vaani_backend.bat

# Option 2: Manual command
cd backend
python crew_main.py
```

### Frontend (Next.js UI)
```bash
# Start development server
cd frontend
npm run dev

# Or production build
npm run build
npm start
```

### Alternative UI (Streamlit)
```bash
cd backend
streamlit run streamlit_app.py
```

## 🎯 Access Points

- **Main UI**: http://localhost:3000 (Next.js - Recommended)
- **Alternative UI**: http://localhost:8501 (Streamlit)
- **API Docs**: http://localhost:8000/docs (FastAPI)
- **Health Check**: http://localhost:8000/health

## 🎤 Voice Commands (Natural Language)

### ✅ Natural Conversation
```
"Hey Vaani, how are you?"
"What can you help me with?"
"Thanks for your help!"
"Tell me what you can do"
```

### 📱 WhatsApp (Natural Patterns)
```
"Send a message to mom saying I'll be late"
"Tell dad about the meeting tomorrow"
"Can you whatsapp jay that I'm coming?"
"Message my friend about the party"
```

### 📁 File Operations
```
"Find my presentation file"
"Search for documents with ownership in the name"
"Where are my photos?"
"Open that report I was working on"
```

### 🔄 Complex Workflows
```
"Send that ownership document to jay on whatsapp"
"Find my presentation and share it with the team"
"Search for contract files and send to my boss"
```

## 🔧 Free TTS Engines Comparison

| Engine | Quality | Speed | Offline | Best For |
|--------|---------|--------|---------|----------|
| **Edge TTS** | ⭐⭐⭐⭐⭐ | Fast | ❌ | **Production (Recommended)** |
| **Coqui TTS** | ⭐⭐⭐⭐ | Medium | ✅ | Privacy-focused |
| **Pyttsx3** | ⭐⭐⭐ | Very Fast | ✅ | Always works |
| **Google TTS** | ⭐⭐⭐ | Fast | ❌ | Reliable fallback |

## 📊 MongoDB Collections Structure

### Conversations Collection
```json
{
  "_id": "ObjectId",
  "conversation_id": "uuid",
  "user_id": "string",
  "session_id": "uuid", 
  "timestamp": "datetime",
  "user_message": "string",
  "vaani_response": "string",
  "metadata": {
    "agent_used": "string",
    "success": "boolean",
    "intent": "string",
    "response_time": "number"
  }
}
```

### User Profiles Collection
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "last_interaction": "datetime",
  "total_interactions": "number",
  "preferred_agents": {
    "whatsapp": "number",
    "filesearch": "number",
    "conversation": "number"
  },
  "preferences": {
    "voice_feedback": "boolean",
    "response_style": "string"
  }
}
```

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 1. Voice Not Working
```bash
# Check TTS engine availability
# Try different engines in .env:
TTS_ENGINE=edge     # Try this first
TTS_ENGINE=pyttsx3  # System fallback
TTS_ENGINE=gtts     # Google fallback
```

#### 2. MongoDB Connection Issues
```bash
# Use in-memory fallback (no setup required)
# Comment out MONGODB_URL in .env
# System will work without MongoDB
```

#### 3. Groq API Issues
```bash
# Verify API key is correct
# Check rate limits at https://console.groq.com/
# Ensure internet connection for API calls
```

#### 4. WhatsApp Not Opening
```bash
# WhatsApp desktop app should be installed
# Or use WhatsApp Web in browser
# Links use standard wa.me format
```

### Log Analysis
```bash
# Backend logs show:
🎤 = Voice/TTS operations
📱 = WhatsApp operations  
📁 = File operations
🤖 = AI processing
🔗 = WebSocket connections
```

## 🌟 Production Optimizations

### Performance Tuning
```env
# Faster response times
AGENT_TEMPERATURE=0.0
MAX_RESPONSE_TOKENS=500

# Better speech recognition
SPEECH_TIMEOUT=10
SPEECH_PHRASE_TIME_LIMIT=20
```

### Security (Production)
```env
# Use environment-specific values
FASTAPI_HOST=127.0.0.1  # Local only
DEBUG_MODE=false
LOG_LEVEL=WARNING
```

### Scaling Considerations
1. **MongoDB Atlas** for cloud persistence
2. **Redis** for session management
3. **Load balancer** for multiple instances
4. **API rate limiting** for Groq calls
5. **CDN** for frontend assets

## 📈 Monitoring & Analytics

### Built-in Endpoints
- `/conversation/history?user_id=test` - Get conversation history
- `/conversation/analytics?user_id=test` - Get usage analytics
- `/health` - System health check
- `/config` - Configuration status

### Analytics Data
- Conversation count by user
- Most used agents
- Success rates
- Response times
- Daily/weekly activity patterns

## 🎯 Production Checklist

- [ ] Groq API key configured
- [ ] TTS engine working (test with voice command)
- [ ] MongoDB connected (optional)
- [ ] WhatsApp integration working
- [ ] File search operational
- [ ] Frontend builds successfully
- [ ] WebSocket connections stable
- [ ] Error handling tested
- [ ] Performance optimized
- [ ] Security settings applied

---

## 🚀 **Ready for Production!**

Your Vaani AI assistant is now configured with production-level features:
- ✅ **Natural Voice Synthesis** using free premium TTS engines
- ✅ **Conversation Memory** with MongoDB persistence  
- ✅ **Zero-Popup Experience** with direct WhatsApp integration
- ✅ **Natural Language Processing** without rigid command patterns
- ✅ **Cross-Platform Compatibility** for all file operations
- ✅ **Real-Time Communication** via WebSocket
- ✅ **Comprehensive Analytics** and conversation tracking

**Experience the future of conversational AI!** 🎤✨