"""
Email Agent for AI Task Automation Assistant
Opens default email client with pre-filled email details
"""

import webbrowser
import urllib.parse
import subprocess
import platform
import re
from typing import Dict, Any, Optional, TypedDict
from langchain.tools import BaseTool
from langchain.schema import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from config import config

class EmailMessage(BaseModel):
    """Email message structure"""
    recipient: str
    subject: str = ""
    body: str = ""
    cc: Optional[str] = None

class AgentState(TypedDict):
    """State for the Email agent workflow"""
    user_input: str
    parsed_command: Dict[str, Any]
    email_url: str
    response_message: str
    error: Optional[str]

class EmailComposerTool(BaseTool):
    """Tool to compose and open email in default client"""
    name: str = "email_composer"
    description: str = "Open default email client with pre-filled email details"
    
    def _run(self, recipient: str, subject: str = "", body: str = "", cc: str = None) -> str:
        """Open email client with mailto URL"""
        try:
            # Build mailto URL
            mailto_parts = [f"mailto:{recipient}"]
            params = []
            
            if subject:
                params.append(f"subject={urllib.parse.quote(subject)}")
            if body:
                params.append(f"body={urllib.parse.quote(body)}")
            if cc:
                params.append(f"cc={urllib.parse.quote(cc)}")
            
            if params:
                mailto_parts.append("?" + "&".join(params))
            
            mailto_url = "".join(mailto_parts)
            
            # Open in default email client
            system = platform.system()
            
            if system == "Windows":
                # Windows: use start command
                subprocess.Popen(['cmd', '/c', 'start', mailto_url], shell=True)
            elif system == "Darwin":  # macOS
                subprocess.Popen(['open', mailto_url])
            else:  # Linux
                subprocess.Popen(['xdg-open', mailto_url])
            
            return f"Email client opened with recipient: {recipient}"
            
        except Exception as e:
            return f"Error opening email client: {str(e)}"

class EmailAgent:
    """LangGraph-powered Email Agent"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        # Initialize tools
        self.email_tool = EmailComposerTool()
        self.tools = [self.email_tool]
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for email sending"""
        
        def parse_command_node(state: AgentState) -> AgentState:
            """Parse user command to extract email details"""
            try:
                user_input = state['user_input']
                
                # Use LLM to extract email components
                system_msg = SystemMessage(content="""You are an email parsing assistant. Extract the following from the user's command:
                - recipient: email address or name (extract actual email if provided)
                - subject: email subject (if mentioned)
                - body: email body/message content (if provided)
                - use_ai: true if user wants AI to write/enhance the email (keywords: "ai", "groq", "generate", "write for me", "compose", "draft")
                - context: any additional context for AI to use when generating content
                
                Examples:
                - "send email to jay@email.com subject meeting" -> recipient: jay@email.com, subject: meeting, body: "", use_ai: false
                - "email jay about internship, use AI to write it" -> recipient: jay, subject: internship, use_ai: true
                - "compose email to hr@company.com about application, groq should write details" -> use_ai: true
                
                Return ONLY a JSON object with these fields. If not mentioned, use empty string for text fields and false for use_ai.""")
                
                human_msg = HumanMessage(content=f"Parse this email command: {user_input}")
                
                response = self.llm.invoke([system_msg, human_msg])
                
                # Try to parse JSON from response
                import json
                try:
                    parsed = json.loads(response.content)
                except:
                    # Fallback parsing
                    parsed = {
                        "recipient": self._extract_recipient(user_input),
                        "subject": self._extract_subject(user_input),
                        "body": self._extract_body(user_input),
                        "use_ai": self._detect_ai_request(user_input),
                        "context": user_input
                    }
                
                state['parsed_command'] = parsed
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to parse email command: {str(e)}"
                state['parsed_command'] = {}
                
            return state
        
        def generate_email_content_node(state: AgentState) -> AgentState:
            """Use AI to generate professional email content if requested"""
            try:
                if state.get('error'):
                    return state
                
                parsed = state['parsed_command']
                
                # Check if AI content generation is requested
                if parsed.get('use_ai', False) or not parsed.get('body', '').strip():
                    # Generate email body using Groq AI
                    recipient = parsed.get('recipient', '')
                    subject = parsed.get('subject', '')
                    context = parsed.get('context', state['user_input'])
                    
                    # Create prompt for AI to generate email
                    system_msg = SystemMessage(content="""You are a professional email writing assistant. 
                    Generate clear, professional, and concise email content based on the user's requirements.
                    
                    Guidelines:
                    - Keep it professional but friendly
                    - Be concise and to the point
                    - Use proper email etiquette (greetings, closing, etc.)
                    - Format with proper paragraphs
                    - Don't include subject line in body (it's separate)
                    - Don't add email headers like "To:", "From:" etc.
                    
                    Return ONLY the email body content, ready to paste.""")
                    
                    human_msg = HumanMessage(content=f"""Generate email body for:
                    Recipient: {recipient}
                    Subject: {subject}
                    Context/Instructions: {context}
                    
                    Write a professional email body that addresses this subject and context.""")
                    
                    response = self.llm.invoke([system_msg, human_msg])
                    
                    # Update body with AI-generated content
                    parsed['body'] = response.content.strip()
                    parsed['ai_generated'] = True
                    
                    state['parsed_command'] = parsed
                
            except Exception as e:
                # If AI generation fails, continue with whatever body we have
                print(f"[DEBUG] Email AI generation failed: {str(e)}")
                parsed['ai_generated'] = False
                state['parsed_command'] = parsed
                
            return state
        
        def compose_email_node(state: AgentState) -> AgentState:
            """Compose and open email"""
            try:
                if state.get('error'):
                    return state
                
                parsed = state['parsed_command']
                recipient = parsed.get('recipient', '')
                subject = parsed.get('subject', '')
                body = parsed.get('body', '')
                ai_generated = parsed.get('ai_generated', False)
                
                # Open email client
                result = self.email_tool._run(recipient, subject, body)
                
                # Build response message
                response_parts = [f"✅ Email client opened for {recipient}"]
                if subject:
                    response_parts.append(f"📧 Subject: {subject}")
                if ai_generated:
                    response_parts.append(f"🤖 AI-generated email content ready!")
                    response_parts.append(f"📝 Preview: {body[:100]}..." if len(body) > 100 else f"📝 Content: {body}")
                elif body:
                    response_parts.append(f"📝 Message included")
                
                state['email_url'] = f"mailto:{recipient}"
                state['response_message'] = "\n".join(response_parts)
                state['error'] = None
                
            except Exception as e:
                state['error'] = f"Failed to open email client: {str(e)}"
                state['response_message'] = "❌ Failed to open email"
                
            return state
        
        # Build workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("parse_command", parse_command_node)
        workflow.add_node("generate_content", generate_email_content_node)
        workflow.add_node("compose_email", compose_email_node)
        
        # Add edges
        workflow.set_entry_point("parse_command")
        workflow.add_edge("parse_command", "generate_content")
        workflow.add_edge("generate_content", "compose_email")
        workflow.add_edge("compose_email", END)
        
        return workflow.compile()
    
    def _detect_ai_request(self, text: str) -> bool:
        """Detect if user wants AI to generate email content"""
        ai_keywords = ['ai', 'groq', 'generate', 'write', 'compose', 'draft', 'create content', 'write for me']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in ai_keywords)
    
    def _extract_recipient(self, text: str) -> str:
        """Extract email recipient from text"""
        # Look for email patterns (handle spaces in email addresses)
        # First, try to find emails with potential spaces: "7819 Vijay sharma@gmail.com" -> "7819Vijaysharma@gmail.com"
        email_with_spaces = r'([\w\d\s]+@[\w\d.-]+\.[A-Za-z]{2,})'
        match = re.search(email_with_spaces, text)
        if match:
            # Remove spaces from email
            email = match.group(0).replace(' ', '')
            return email
        
        # Standard email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        if match:
            return match.group(0)
        
        # Look for "to [name]" pattern
        to_pattern = r'(?:to|email)\s+([A-Za-z\s]+?)(?:\s+about|\s+regarding|\s+his|\s+her|$)'
        match = re.search(to_pattern, text.lower())
        if match:
            return match.group(1).strip()
        
        return ""
    
    def _extract_subject(self, text: str) -> str:
        """Extract email subject from text"""
        subject_pattern = r'(?:subject|about|regarding)\s+[\'"]?([^\'"\n]+)[\'"]?'
        match = re.search(subject_pattern, text.lower())
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_body(self, text: str) -> str:
        """Extract email body from text"""
        body_pattern = r'(?:body|message|saying|tell)\s+[\'"]?([^\'"\n]+)[\'"]?'
        match = re.search(body_pattern, text.lower())
        if match:
            return match.group(1).strip()
        
        # Fallback: use entire text if no specific pattern
        return text
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process email command and return result"""
        try:
            initial_state = {
                "user_input": user_input,
                "parsed_command": {},
                "email_url": "",
                "response_message": "",
                "error": None
            }
            
            # Run workflow
            final_state = self.workflow.invoke(initial_state)
            
            return {
                "success": final_state.get('error') is None,
                "message": final_state.get('response_message', 'Email processed'),
                "email_url": final_state.get('email_url', ''),
                "details": final_state.get('parsed_command', {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Email agent error: {str(e)}",
                "email_url": "",
                "details": {}
            }

# Create global instance
email_agent = EmailAgent()
