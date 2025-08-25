"""
Conversational Agent for AI Task Automation Assistant (Vaani)
Provides natural, friendly interactions with personality and context awareness
"""

import re
from typing import Dict, List, Any, Optional, TypedDict
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from datetime import datetime
from config import config

class ConversationState(TypedDict):
    """State for the conversation agent workflow"""
    user_input: str
    intent: str
    response: str
    context: Dict[str, Any]
    personality_response: str
    error: Optional[str]

class ConversationAgent:
    """LangGraph-powered Conversational Agent with Vaani personality"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=0.7,  # Higher temperature for more creative responses
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
        # Conversation context
        self.context = {
            "conversation_history": [],
            "user_preferences": {},
            "session_start": datetime.now().isoformat()
        }
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for conversational interactions"""
        
        def analyze_intent_node(state: ConversationState) -> ConversationState:
            """Analyze user intent and conversational context"""
            try:
                if 'intent' not in state:
                    state['intent'] = ""
                if 'error' not in state:
                    state['error'] = None
                if 'context' not in state:
                    state['context'] = {}
                
                system_prompt = """You are Vaani, a friendly and intelligent AI assistant for task automation.
                
                Your personality:
                - Warm, helpful, and conversational
                - Professional yet approachable
                - Proactive in understanding user needs
                - Clear in communication
                - Supportive and encouraging
                
                Analyze the user input and determine the intent category:
                
                CONVERSATION INTENTS:
                - greeting: Hello, hi, good morning, how are you, etc.
                - introduction: Who are you, what can you do, capabilities, features
                - gratitude: Thank you, thanks, appreciate it
                - farewell: Bye, goodbye, see you later, exit
                - help: Help, what can I do, commands, usage
                - casual: General conversation, small talk
                - task_command: Specific task requests (WhatsApp, files, etc.)
                - unclear: Ambiguous or unclear requests
                
                Return ONLY the intent category. Nothing else."""
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=state['user_input'])
                ]
                
                response = self.llm.invoke(messages)
                intent = response.content.strip().lower()
                
                state['intent'] = intent
                state['context'] = {
                    "timestamp": datetime.now().isoformat(),
                    "user_input_length": len(state['user_input']),
                    "detected_intent": intent
                }
                
                return state
                
            except Exception as e:
                state['error'] = f"Error analyzing intent: {str(e)}"
                return state
        
        def generate_response_node(state: ConversationState) -> ConversationState:
            """Generate appropriate conversational response"""
            if state.get('error'):
                return state
                
            try:
                intent = state.get('intent', 'unclear')
                user_input = state.get('user_input', '')
                
                # Define response templates based on intent
                if intent == 'greeting':
                    system_prompt = """You are Vaani, a friendly AI assistant. 
                    Respond to the greeting warmly and introduce yourself briefly.
                    Mention that you can help with WhatsApp messages, file searches, and other tasks.
                    Keep it conversational and welcoming (2-3 sentences max)."""
                
                elif intent == 'introduction':
                    system_prompt = """You are Vaani, an AI task automation assistant.
                    Introduce yourself and explain your capabilities:
                    - Send WhatsApp messages via voice/text
                    - Search and open files on any device
                    - Multi-agent task coordination
                    - Voice-powered hands-free operation
                    Be enthusiastic and helpful. End with asking how you can assist them."""
                
                elif intent == 'help':
                    system_prompt = """You are Vaani. Provide helpful guidance on what you can do:
                    
                    Available commands:
                    - "Send WhatsApp to [name]: [message]" - Send messages
                    - "Find file [filename]" - Search for files
                    - "Open [filename]" - Open specific files
                    - "Send [filename] to [contact] on WhatsApp" - Share files
                    
                    Be encouraging and mention you understand natural language, not just fixed patterns."""
                
                elif intent == 'gratitude':
                    system_prompt = """You are Vaani. Respond warmly to the user's gratitude.
                    Be humble and offer continued assistance. Keep it brief and friendly."""
                
                elif intent == 'farewell':
                    system_prompt = """You are Vaani. Say goodbye warmly and mention you're always here to help.
                    Be friendly and leave the door open for future interactions."""
                
                elif intent == 'casual':
                    system_prompt = """You are Vaani. Engage in brief, friendly conversation while 
                    gently steering toward how you can help with tasks. Be personable but professional."""
                
                elif intent == 'task_command':
                    system_prompt = """You are Vaani. The user has given a task command.
                    Acknowledge that you understand and will process their request.
                    Be encouraging and confirm what you're about to do."""
                
                else:  # unclear or other
                    system_prompt = """You are Vaani. The user's request isn't clear.
                    Politely ask for clarification and suggest some example commands you can help with.
                    Be helpful and encouraging, not frustrated."""
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f"User said: {user_input}")
                ]
                
                response = self.llm.invoke(messages)
                state['response'] = response.content.strip()
                
                return state
                
            except Exception as e:
                state['error'] = f"Error generating response: {str(e)}"
                return state
        
        # Build the workflow graph
        workflow = StateGraph(ConversationState)
        
        # Add nodes
        workflow.add_node("analyze_intent", analyze_intent_node)
        workflow.add_node("generate_response", generate_response_node)
        
        # Add edges
        workflow.set_entry_point("analyze_intent")
        workflow.add_edge("analyze_intent", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def process_conversation(self, user_input: str) -> Dict[str, Any]:
        """Process conversational input and generate appropriate response"""
        try:
            # Initialize state
            initial_state: ConversationState = {
                'user_input': user_input.strip(),
                'intent': '',
                'response': '',
                'context': {},
                'personality_response': '',
                'error': None
            }
            
            # Run the workflow
            result = self.workflow.invoke(initial_state)
            
            # Update conversation context
            self.context["conversation_history"].append({
                "user_input": user_input,
                "intent": result.get('intent', ''),
                "response": result.get('response', ''),
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last 10 conversations
            if len(self.context["conversation_history"]) > 10:
                self.context["conversation_history"] = self.context["conversation_history"][-10:]
            
            return {
                "success": not bool(result.get('error')),
                "message": result.get('response', ''),
                "intent": result.get('intent', ''),
                "context": result.get('context', {}),
                "conversation_context": self.context,
                "error": result.get('error')
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Hi! I'm Vaani, your AI assistant. I had a small hiccup there - could you please try again?",
                "intent": "error",
                "context": {},
                "conversation_context": self.context,
                "error": str(e)
            }
    
    def is_conversational_input(self, user_input: str) -> bool:
        """Determine if input is conversational rather than a task command"""
        conversational_patterns = [
            r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
            r'\b(how are you|what\'s up|how\'s it going)\b',
            r'\b(who are you|what can you do|help me|what are your capabilities)\b',
            r'\b(thank you|thanks|appreciate)\b',
            r'\b(bye|goodbye|see you|exit|quit)\b',
            r'^\s*vaani\b',  # Direct address to Vaani
            r'\?$',  # Questions
        ]
        
        user_input_lower = user_input.lower()
        return any(re.search(pattern, user_input_lower) for pattern in conversational_patterns)
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation session"""
        history_count = len(self.context["conversation_history"])
        if history_count == 0:
            return "New conversation session started"
        
        return f"Conversation active with {history_count} exchanges since {self.context['session_start']}"

# Global conversation agent instance
conversation_agent = ConversationAgent()