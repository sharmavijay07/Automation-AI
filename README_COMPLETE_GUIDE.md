# 🎤 Vaani - Voice AI Assistant

## Complete Voice-Powered Automation Assistant

Vaani is a comprehensive voice AI assistant that automates repetitive tasks through natural voice commands. It integrates with your system applications to handle emails, calls, payments, calendar events, file management, and much more - all through simple voice commands!

---

## 🌟 Key Features

### 📱 **Communication**
- **WhatsApp Messages**: Send WhatsApp messages to contacts with pre-filled text
- **Email**: Compose and send emails via your default mail client
- **Phone Calls**: Search contacts and initiate calls through system dialer

### 📅 **Productivity**
- **Calendar Management**: Schedule meetings and events on Google Calendar
- **Task Management**: Create, list, and manage tasks and reminders
- **File Search**: Find and open files from your local storage

### 💰 **Payments**
- **Multiple Payment Apps**: Support for PayPal, Google Pay, Paytm, PhonePe
- **Pre-filled Forms**: Opens payment apps with pre-filled recipient and amount

### 🚀 **System Control**
- **Application Launcher**: Open any application (Chrome, Calculator, Notepad, etc.)
- **Web Search**: Search on Google, YouTube, Bing, DuckDuckGo
- **Browser Control**: Open websites and manage browsers

### 🤖 **AI-Powered**
- **Natural Language Understanding**: Uses Groq AI for intelligent command interpretation
- **Multi-Agent Coordination**: Handles complex tasks requiring multiple agents
- **Conversational Interface**: Natural conversation with Vaani

---

## 🎯 Voice Commands Examples

### WhatsApp
```
"Send WhatsApp to vijay: Hey, are you free tomorrow?"
"Message mom I'm coming home"
"Tell jay the meeting is at 3pm"
```

### Email
```
"Email boss about the project deadline"
"Send email to john with subject Meeting Notes"
"Compose email to team@company.com"
```

### Phone Calls
```
"Call mom"
"Phone vijay"
"Dial 9876543210"
```

### Calendar
```
"Schedule meeting tomorrow at 3pm"
"Create event for Monday morning"
"Add appointment with doctor on Friday"
```

### Payments
```
"Pay $50 to john via PayPal"
"Send 100 rupees to vijay via Paytm"
"Transfer money to alice using Google Pay"
```

### File Operations
```
"Find ownership document"
"Open presentation.pptx"
"Search for photos from last week"
"Send report.pdf to boss on WhatsApp"
```

### Application Launcher
```
"Open Chrome"
"Launch calculator"
"Start Notepad"
"Run PowerPoint"
```

### Web Search
```
"Google python tutorials"
"Search for restaurants near me"
"YouTube how to code in JavaScript"
"Find images of mountains"
```

### Task Management
```
"Add task buy groceries"
"Remind me to call mom tomorrow"
"List my tasks"
"Mark task complete"
```

---

## 🏗️ Architecture

### Multi-Agent System
Vaani uses a sophisticated multi-agent architecture powered by LangGraph:

1. **Agent Manager (MCP)**: Routes commands to appropriate agents
2. **10 Specialized Agents**:
   - WhatsApp Agent
   - Email Agent
   - Calendar Agent
   - Phone Agent
   - Payment Agent
   - App Launcher Agent
   - Web Search Agent
   - Task Agent
   - File Search Agent
   - Conversation Agent

### Technology Stack

**Backend:**
- FastAPI (REST API & WebSocket)
- LangChain & LangGraph (Agent orchestration)
- Groq AI (LLM for NLU)
- Python 3.11+

**Frontend:**
- Next.js 14+ (React)
- TypeScript
- Tailwind CSS
- WebSocket for real-time updates

**AI/ML:**
- Groq API (llama3-8b-8192)
- Edge TTS (Text-to-Speech)
- Speech Recognition

---

## 📦 Installation

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ and npm/yarn
- Windows/macOS/Linux

### Backend Setup

1. **Clone the repository**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create/update `.env` file:
```env
# AI Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-8b-8192

# Server Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000

# Agent Configuration
AGENT_TEMPERATURE=0.1
MAX_RESPONSE_TOKENS=1000

# Email Configuration
EMAIL_CLIENT=default
DEFAULT_EMAIL_FROM=your-email@gmail.com

# Calendar Configuration
CALENDAR_APP=default

# Payment Configuration
PAYMENT_APPS=paypal,googlepay,paytm,phonepe

# File Search Configuration
SEARCH_DIRECTORIES=C:\Users,C:\Documents,C:\Downloads
MAX_SEARCH_RESULTS=10
```

5. **Run the backend**
```bash
python main.py
```

Backend will start at: `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
# or
yarn install
```

3. **Configure environment**
Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. **Run the frontend**
```bash
npm run dev
# or
yarn dev
```

Frontend will start at: `http://localhost:3000`

---

## 🔧 Configuration

### Adding Custom Contacts

Edit `backend/agents/whatsapp_agent.py` and `phone_agent.py`:
```python
mock_contacts: ClassVar[Dict[str, str]] = {
    "vijay": "+919876543211",
    "mom": "+919876543212",
    "your_name": "+91xxxxxxxxxx",
}
```

### Customizing Application Paths

Edit `backend/agents/app_launcher_agent.py`:
```python
WINDOWS_APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "custom_app": r"C:\Path\To\Your\App.exe",
}
```

### File Search Directories

Update `.env`:
```env
SEARCH_DIRECTORIES=C:\Users\YourName\Documents,D:\Projects,C:\Downloads
```

---

## 📡 API Endpoints

### REST API

**Health Check**
```http
GET /health
```

**Process Command**
```http
POST /process-command
Content-Type: application/json

{
  "command": "Send WhatsApp to vijay: Hello!"
}
```

**Get Available Agents**
```http
GET /agents
```

**Text-to-Speech**
```http
POST /text-to-speech
Content-Type: application/json

{
  "text": "Hello, this is Vaani!",
  "language": "en"
}
```

### WebSocket

Connect to: `ws://localhost:8000/ws`

**Send Command**
```json
{
  "type": "command",
  "command": "Find ownership document"
}
```

**Receive Response**
```json
{
  "type": "command_result",
  "data": {
    "success": true,
    "message": "Found ownership document!",
    "intent": "filesearch",
    "agent_used": "filesearch"
  }
}
```

---

## 🎨 Frontend Usage

1. **Voice Input**: Click the microphone button and speak your command
2. **Text Input**: Type your command in the text box
3. **View Results**: See agent responses and action buttons
4. **Execute Actions**: Click generated buttons (e.g., "Open WhatsApp", "Open File")

---

## 🔐 Security & Privacy

- **Local Processing**: All file searches and app launching happen locally
- **No Data Storage**: Commands are processed in real-time, not stored
- **Secure APIs**: Environment variables for sensitive data
- **No Recording**: Voice input is converted to text and discarded
- **Contact Privacy**: Mock contacts are local; integrate with system contacts for production

---

## 🤝 Agent Capabilities

| Agent | Capabilities | Example Commands |
|-------|-------------|------------------|
| **WhatsApp** | Send messages, contact search | "Message vijay: Hello!" |
| **Email** | Compose emails, open mail client | "Email boss about meeting" |
| **Calendar** | Schedule events, create appointments | "Schedule meeting tomorrow" |
| **Phone** | Call contacts, dial numbers | "Call mom" |
| **Payment** | Send payments via multiple apps | "Pay $50 via PayPal" |
| **App Launcher** | Open applications | "Open Chrome" |
| **Web Search** | Google, YouTube, etc. | "Search for tutorials" |
| **Task** | Manage tasks and reminders | "Add task buy milk" |
| **File Search** | Find and open files | "Find report.pdf" |
| **Conversation** | Chat and help | "Hello, what can you do?" |

---

## 🚀 Advanced Features

### Multi-Agent Workflows

Vaani can coordinate multiple agents for complex tasks:

```
"Find ownership document and send to vijay on WhatsApp"
```

This command:
1. Uses File Search Agent to find the document
2. Uses WhatsApp Agent to prepare the message
3. Opens WhatsApp with pre-filled message and file info

### Natural Language Processing

Vaani understands natural language variations:
- "Call my mom" = "Phone mom" = "Dial mom's number"
- "Schedule a meeting" = "Create event" = "Add to calendar"
- "Send money" = "Make payment" = "Transfer funds"

---

## 📝 Development

### Adding New Agents

1. Create agent file: `backend/agents/your_agent.py`
2. Implement agent class with `process_command()` method
3. Register in `agent_manager.py`
4. Add keywords and routing logic
5. Update `main.py` agent_info

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 🐛 Troubleshooting

### Common Issues

**"Groq API Key Error"**
- Solution: Add valid GROQ_API_KEY to `.env`

**"Agent not found"**
- Solution: Check if agent is registered in `agent_manager.py`

**"File not found"**
- Solution: Update SEARCH_DIRECTORIES in `.env`

**"WhatsApp/Email not opening"**
- Solution: Ensure default apps are set in Windows/OS settings

---

## 📄 License

MIT License - Feel free to use and modify

---

## 🙏 Credits

- **AI**: Groq (llama3-8b-8192)
- **Framework**: LangChain, LangGraph
- **Backend**: FastAPI
- **Frontend**: Next.js
- **TTS**: Edge TTS

---

## 📞 Support

For issues or questions:
- Create an issue on GitHub
- Check documentation in `/docs`
- Review code comments

---

## 🎉 Future Enhancements

- [ ] Voice output for all responses
- [ ] Integration with real contacts API
- [ ] Cloud calendar sync (Google, Outlook)
- [ ] Email template support
- [ ] Advanced file preview
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Custom agent creation UI

---

**Made with ❤️ by Vaani Team**

*Your voice-powered productivity assistant*
