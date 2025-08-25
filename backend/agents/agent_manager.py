"""
Multi-Agent Coordinator (MCP) for AI Task Automation Assistant
Handles routing commands to appropriate agents using LangGraph
"""

from typing import Dict, Any, List, Optional, TypedDict
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from agents.whatsapp_agent import whatsapp_agent
from agents.conversation_agent import conversation_agent
from agents.filesearch_agent import filesearch_agent
from config import config

class AgentManagerState(TypedDict):
    """State for the agent manager workflow"""
    user_input: str
    detected_intent: str
    agent_name: str
    agent_response: Dict[str, Any]
    final_response: str
    error: Optional[str]

class AgentManager:
    """
    Multi-Agent Coordinator (MCP) that routes commands to appropriate agents
    Uses LangGraph for stateful workflow management
    """
    
    def __init__(self):
        # Initialize LLM for intent detection
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.GROQ_MODEL,
            temperature=config.AGENT_TEMPERATURE,
            max_tokens=config.MAX_RESPONSE_TOKENS
        )
        
        # Register available agents
        self.agents = {
            "whatsapp": whatsapp_agent,
            "conversation": conversation_agent,
            "filesearch": filesearch_agent
        }
        
        # Build MCP workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the MCP workflow for agent coordination"""
        
        def intent_detection_node(state: AgentManagerState) -> AgentManagerState:
            """Enhanced intent detection with conversational AI and natural language understanding"""
            try:
                # Initialize default values if not present
                if 'detected_intent' not in state:
                    state['detected_intent'] = ""
                if 'agent_name' not in state:
                    state['agent_name'] = ""
                if 'error' not in state:
                    state['error'] = None
                
                user_input = state['user_input']
                user_input_lower = user_input.lower()
                
                print(f"\n[DEBUG] Intent Detection:")
                print(f"[DEBUG] User input: '{user_input}'")
                
                # Check conversational input first
                is_conversational = conversation_agent.is_conversational_input(user_input)
                print(f"[DEBUG] Is conversational: {is_conversational}")
                
                # Enhanced keyword detection with NLP patterns
                file_keywords = ["find", "search", "open", "file", "document", "folder", "pdf", "doc", "excel", "photo", "video", "music"]
                whatsapp_keywords = ["whatsapp", "message", "send to", "text", "tell", "let know", "inform", "send whatsapp", "whatsapp to", "message to"]
                
                # Multi-agent detection (file + communication)
                has_file_intent = any(keyword in user_input_lower for keyword in file_keywords)
                has_whatsapp_intent = any(keyword in user_input_lower for keyword in whatsapp_keywords)
                
                # Special handling for WhatsApp patterns
                whatsapp_patterns = ["send whatsapp", "whatsapp to", "message to", "text to"]
                is_whatsapp_command = any(pattern in user_input_lower for pattern in whatsapp_patterns)
                
                print(f"[DEBUG] Has file intent: {has_file_intent}")
                print(f"[DEBUG] Has WhatsApp intent: {has_whatsapp_intent}")
                print(f"[DEBUG] Is WhatsApp command: {is_whatsapp_command}")
                
                # Priority routing: WhatsApp commands override conversational detection
                if is_whatsapp_command or has_whatsapp_intent:
                    if has_file_intent:
                        state['detected_intent'] = "multi_agent"
                        state['agent_name'] = "multi_agent"
                        print(f"[DEBUG] Routed to: multi_agent (file + whatsapp)")
                    else:
                        state['detected_intent'] = "whatsapp"
                        state['agent_name'] = "whatsapp"
                        print(f"[DEBUG] Routed to: whatsapp")
                    return state
                
                # File operations
                elif has_file_intent:
                    state['detected_intent'] = "filesearch"
                    state['agent_name'] = "filesearch"
                    print(f"[DEBUG] Routed to: filesearch")
                    return state
                
                # Pure conversational input
                elif is_conversational:
                    state['detected_intent'] = "conversation"
                    state['agent_name'] = "conversation"
                    print(f"[DEBUG] Routed to: conversation (pure conversational)")
                    return state
                
                # Use LLM for complex intent detection
                print(f"[DEBUG] Using LLM for intent detection...")
                
                system_prompt = """You are Vaani, an advanced AI assistant with natural language understanding.
                Analyze the user input and classify it into the most appropriate category:
                
                AVAILABLE AGENTS:
                - whatsapp: WhatsApp messaging and communication
                  * Patterns: "send message", "whatsapp", "text someone", "message [name]"
                  * Natural: "tell mom I'm coming", "let dad know about meeting", "send hello to friend"
                  
                - filesearch: File operations, search, open, and sharing
                  * Patterns: "find file", "open document", "search for", "locate", "show me files"
                  * Natural: "where is my report", "open that presentation", "find my photos", "send file to someone"
                  
                - conversation: Conversational interactions, greetings, help
                  * Patterns: "hello", "help", "what can you do", "who are you", "thanks"
                  * Natural: "hi there", "I need help", "goodbye", "thank you"
                  
                - multi_agent: Complex tasks requiring multiple agents
                  * Patterns: "send [file] to [contact]", "find and share", "search and message"
                  * Natural: "send my report to boss on whatsapp", "find photo and share with mom"
                
                CLASSIFICATION RULES:
                1. If mentioning files AND communication -> multi_agent
                2. If clear WhatsApp/messaging intent -> whatsapp  
                3. If clear file operation intent -> filesearch
                4. If conversational/greeting -> conversation
                5. If unclear -> conversation (Vaani will ask for clarification)
                
                Examples:
                - "Send report.pdf to boss on WhatsApp" -> multi_agent
                - "Tell Sarah I'm running late" -> whatsapp
                - "Find my Excel files" -> filesearch
                - "Open presentation.pptx" -> filesearch
                - "Send hello to mom" -> whatsapp
                - "Hi, what can you do?" -> conversation
                - "Where are my documents?" -> filesearch
                
                Return ONLY the agent name. Nothing else."""
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_input)
                ]
                
                response = self.llm.invoke(messages)
                intent = response.content.strip().lower()
                
                print(f"[DEBUG] LLM detected intent: '{intent}'")
                
                # Enhanced intent validation with fallbacks
                if intent in self.agents or intent == "multi_agent":
                    state['detected_intent'] = intent
                    state['agent_name'] = intent
                    print(f"[DEBUG] Final routing: {intent}")
                else:
                    # Default to conversation for unknown intents
                    state['detected_intent'] = "conversation"
                    state['agent_name'] = "conversation"
                    print(f"[DEBUG] Unknown intent '{intent}', defaulting to conversation")
                
                return state
                
            except Exception as e:
                print(f"[DEBUG] Error in intent detection: {str(e)}")
                state['error'] = f"Error in intent detection: {str(e)}"
                return state
        
        def route_to_agent_node(state: AgentManagerState) -> AgentManagerState:
            """Enhanced routing with multi-agent coordination"""
            if state.get('error'):
                return state
            
            try:
                agent_name = state.get('agent_name')
                user_input = state['user_input']
                
                # Handle multi-agent workflows
                if agent_name == "multi_agent":
                    state['agent_response'] = self._handle_multi_agent_workflow(user_input)
                    return state
                
                # Route to specific agents
                if agent_name == "conversation":
                    state['agent_response'] = self.agents["conversation"].process_conversation(user_input)
                elif agent_name == "whatsapp":
                    state['agent_response'] = self.agents["whatsapp"].process_command(user_input)
                elif agent_name == "filesearch":
                    state['agent_response'] = self.agents["filesearch"].process_command(user_input)
                else:
                    # Fallback to conversation agent for unknown intents
                    state['agent_response'] = {
                        "success": True,
                        "message": "Hi! I'm Vaani, your AI assistant. I can help with WhatsApp messages, finding files, and general tasks. What would you like me to do?",
                        "intent": "fallback",
                        "context": {}
                    }
                
                return state
                
            except Exception as e:
                state['error'] = f"Error routing to agent: {str(e)}"
                state['agent_response'] = {
                    "success": False,
                    "message": f"Hi! I'm Vaani. I encountered a small issue: {str(e)}. Please try again!",
                    "error": str(e)
                }
                return state
        
        def generate_response_node(state: AgentManagerState) -> AgentManagerState:
            """Generate final response based on agent output"""
            try:
                if state.get('error'):
                    state['final_response'] = f"❌ System Error: {state['error']}"
                    return state
                
                agent_response = state.get('agent_response', {})
                
                if agent_response.get("success", False):
                    state['final_response'] = agent_response.get("message", "✅ Task completed successfully!")
                else:
                    error_msg = agent_response.get("error", "Unknown error occurred")
                    state['final_response'] = agent_response.get("message", f"❌ Error: {error_msg}")
                
                return state
                
            except Exception as e:
                state['final_response'] = f"❌ Error generating response: {str(e)}"
                return state
        
        # Build the workflow graph
        workflow = StateGraph(AgentManagerState)
        
        # Add nodes
        workflow.add_node("detect_intent", intent_detection_node)
        workflow.add_node("route_to_agent", route_to_agent_node)
        workflow.add_node("generate_response", generate_response_node)
        
        # Add edges
        workflow.set_entry_point("detect_intent")
        workflow.add_edge("detect_intent", "route_to_agent")
        workflow.add_edge("route_to_agent", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def _handle_multi_agent_workflow(self, user_input: str) -> Dict[str, Any]:
        """Handle complex workflows requiring multiple agents"""
        try:
            # First, try to parse the multi-agent intent
            system_prompt = """Analyze this command to determine the multi-agent workflow needed:
            
            WORKFLOW TYPES:
            1. file_to_whatsapp: Find/prepare file and send via WhatsApp
            2. search_and_share: Search for files and prepare for sharing
            3. open_and_inform: Open file and notify someone
            
            Extract:
            - workflow_type: [file_to_whatsapp/search_and_share/open_and_inform]
            - file_query: [file name/pattern to find]
            - recipient: [person to send to]
            - message: [optional message content]
            
            Examples:
            - "Send report.pdf to boss on WhatsApp" -> file_to_whatsapp, report.pdf, boss
            - "Find my photos and share with mom" -> search_and_share, photos, mom
            - "Open presentation and tell team it's ready" -> open_and_inform, presentation, team
            
            Return format:
            WORKFLOW: [type]
            FILE: [query]
            RECIPIENT: [name]
            MESSAGE: [content or empty]
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Parse workflow parameters
            workflow_type = ""
            file_query = ""
            recipient = ""
            message = ""
            
            for line in response_text.split('\n'):
                if line.startswith("WORKFLOW:"):
                    workflow_type = line.replace("WORKFLOW:", "").strip()
                elif line.startswith("FILE:"):
                    file_query = line.replace("FILE:", "").strip()
                elif line.startswith("RECIPIENT:"):
                    recipient = line.replace("RECIPIENT:", "").strip()
                elif line.startswith("MESSAGE:"):
                    message = line.replace("MESSAGE:", "").strip()
            
            # Execute the multi-agent workflow
            if workflow_type == "file_to_whatsapp" and file_query and recipient:
                return self._execute_file_to_whatsapp_workflow(file_query, recipient, message)
            elif workflow_type == "search_and_share" and file_query:
                return self._execute_search_and_share_workflow(file_query, recipient)
            else:
                # Fallback: try to handle as best as possible
                return self._execute_generic_multi_agent_workflow(user_input)
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Hi! I'm Vaani. I had trouble understanding that complex request. Could you try breaking it down? For example: 'Find my report' first, then 'Send report.pdf to boss on WhatsApp'.",
                "error": str(e)
            }
    
    def _execute_file_to_whatsapp_workflow(self, file_query: str, recipient: str, custom_message: str = "") -> Dict[str, Any]:
        """Execute file search + WhatsApp sharing workflow"""
        try:
            # Step 1: Search for the file
            file_result = self.agents["filesearch"].process_command(f"find {file_query}")
            
            if not file_result.get("success") or not file_result.get("search_results"):
                return {
                    "success": False,
                    "message": f"🔍 I couldn't find '{file_query}'. Please check the filename and try again.",
                    "workflow": "file_to_whatsapp",
                    "step": "file_search_failed"
                }
            
            # Get the best matching file
            best_file = file_result["search_results"][0]["file_info"]
            file_name = best_file["name"]
            file_path = best_file["path"]
            file_size_mb = best_file["size"] / (1024 * 1024)
            
            # Step 2: Prepare sharing message
            if custom_message:
                sharing_text = custom_message
            else:
                sharing_text = f"📁 Sharing file: {file_name} ({file_size_mb:.1f}MB)"
            
            # Step 3: Create WhatsApp message
            whatsapp_command = f"Send WhatsApp to {recipient}: {sharing_text}"
            whatsapp_result = self.agents["whatsapp"].process_command(whatsapp_command)
            
            if whatsapp_result.get("success"):
                return {
                    "success": True,
                    "message": f"✅ Great! I found '{file_name}' and prepared WhatsApp message for {recipient}!\n\n📁 File: {file_name} ({file_size_mb:.1f}MB)\n💬 {whatsapp_result['message']}",
                    "workflow": "file_to_whatsapp",
                    "file_info": best_file,
                    "whatsapp_result": whatsapp_result,
                    "whatsapp_url": whatsapp_result.get("whatsapp_url", "")
                }
            else:
                return {
                    "success": False,
                    "message": f"📁 I found '{file_name}' but couldn't create WhatsApp message: {whatsapp_result.get('message', 'Unknown error')}",
                    "workflow": "file_to_whatsapp",
                    "step": "whatsapp_failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Hi! I'm Vaani. I had trouble with that file sharing request. Error: {str(e)}",
                "workflow": "file_to_whatsapp",
                "error": str(e)
            }
    
    def _execute_search_and_share_workflow(self, file_query: str, recipient: str = "") -> Dict[str, Any]:
        """Execute file search and prepare for sharing"""
        try:
            # Search for files
            file_result = self.agents["filesearch"].process_command(f"search {file_query}")
            
            if not file_result.get("success") or not file_result.get("search_results"):
                return {
                    "success": False,
                    "message": f"🔍 No files found matching '{file_query}'. Try a different search term.",
                    "workflow": "search_and_share"
                }
            
            # Format results for sharing
            results = file_result["search_results"]
            response_message = f"🔍 Found {len(results)} file(s) matching '{file_query}' ready for sharing:\n\n"
            
            for i, result in enumerate(results[:3], 1):
                file_info = result["file_info"]
                size_mb = file_info["size"] / (1024 * 1024)
                response_message += f"{i}. 📄 {file_info['name']} ({size_mb:.1f}MB)\n"
            
            if recipient:
                response_message += f"\n💡 Say 'Send [filename] to {recipient} on WhatsApp' to share!"
            else:
                response_message += f"\n💡 Say 'Send [filename] to [contact] on WhatsApp' to share!"
            
            return {
                "success": True,
                "message": response_message,
                "workflow": "search_and_share",
                "search_results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Search and share failed: {str(e)}",
                "workflow": "search_and_share",
                "error": str(e)
            }
    
    def _execute_generic_multi_agent_workflow(self, user_input: str) -> Dict[str, Any]:
        """Generic handler for complex requests"""
        return {
            "success": True,
            "message": "Hi! I'm Vaani. That sounds like a complex task! I can help with:\n\n📱 WhatsApp: 'Send message to [contact]'\n📁 Files: 'Find [filename]' or 'Open [filename]'\n🔄 Combined: 'Send [filename] to [contact] on WhatsApp'\n\nWhat would you like me to help you with first?",
            "workflow": "generic_guidance"
        }
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process user command through MCP workflow"""
        try:
            # Initialize state with proper structure
            initial_state: AgentManagerState = {
                'user_input': user_input.strip(),
                'detected_intent': '',
                'agent_name': '',
                'agent_response': {},
                'final_response': '',
                'error': None
            }
            
            # Run the workflow
            result = self.workflow.invoke(initial_state)
            
            # Ensure all required fields exist in response
            agent_response = result.get('agent_response', {})
            
            return {
                "success": not bool(result.get('error')),
                "message": result.get('final_response', 'Task completed'),
                "intent": result.get('detected_intent', ''),
                "agent_used": result.get('agent_name', ''),
                "agent_response": agent_response,
                "error": result.get('error'),
                # Additional fields for specific agents
                "search_results": agent_response.get('search_results', []),
                "selected_file": agent_response.get('selected_file'),
                "action_type": agent_response.get('action_type'),
                "whatsapp_url": agent_response.get('whatsapp_url'),
                "workflow": agent_response.get('workflow')
            }
            
        except Exception as e:
            error_msg = f"MCP Error: {str(e)}"
            return {
                "success": False,
                "message": f"❌ {error_msg}",
                "intent": "error",
                "agent_used": "none",
                "agent_response": {},
                "error": error_msg,
                "search_results": [],
                "selected_file": None,
                "action_type": "error",
                "whatsapp_url": None,
                "workflow": None
            }
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agents"""
        return list(self.agents.keys())
    
    def add_agent(self, name: str, agent_instance):
        """Add a new agent to the MCP"""
        self.agents[name] = agent_instance
        # Rebuild workflow when new agents are added
        self.workflow = self._build_workflow()

# Global MCP instance
agent_manager = AgentManager()