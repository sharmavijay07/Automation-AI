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
from utils.conversation_memory import conversation_memory
from utils.conversational_tts import conversational_tts

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
                file_keywords = ["find", "search", "open", "file", "document", "folder", "pdf", "doc", "excel", "photo", "video", "music", "ownership", "report", "presentation"]
                whatsapp_keywords = ["whatsapp", "message", "send to", "text", "tell", "let know", "inform", "send whatsapp", "whatsapp to", "message to", "share"]
                
                # Detect file intent with better distinction
                file_keywords = ["find", "search", "open", "ownership", "folder", "photo", "video", "pdf", "doc", "docx", "excel", "presentation", "report"]
                
                # Questions about capabilities (should go to conversation)
                capability_questions = ["can you", "are you able", "do you", "what can", "how do", "tell me about", "what is", "explain", "why", "how"]
                general_questions = ["what", "how", "why", "when", "where", "who", "?"]
                is_capability_question = any(phrase in user_input_lower for phrase in capability_questions)
                is_general_question = any(word in user_input_lower for word in general_questions) and not any(op_word in user_input_lower for op_word in ["find", "search", "open", "send"])
                
                # Actual file operations (should go to filesearch)
                file_operation_keywords = ["find", "search", "open", "locate", "show me"]
                has_file_operation = any(keyword in user_input_lower for keyword in file_operation_keywords) and not is_capability_question
                
                # Multi-agent detection (file + communication)
                has_whatsapp_intent = any(keyword in user_input_lower for keyword in whatsapp_keywords)
                
                # Special handling for multi-agent patterns
                multi_agent_patterns = ["send * to", "share * with", "find * and send", "send the * file"]
                is_multi_agent_command = any("send" in user_input_lower and keyword in user_input_lower for keyword in file_keywords)
                
                # Special handling for WhatsApp patterns
                whatsapp_patterns = ["send whatsapp", "whatsapp to", "message to", "text to"]
                is_whatsapp_command = any(pattern in user_input_lower for pattern in whatsapp_patterns)
                
                print(f"[DEBUG] Is capability question: {is_capability_question}")
                print(f"[DEBUG] Is general question: {is_general_question}")
                print(f"[DEBUG] Has file operation: {has_file_operation}")
                print(f"[DEBUG] Has WhatsApp intent: {has_whatsapp_intent}")
                print(f"[DEBUG] Is WhatsApp command: {is_whatsapp_command}")
                print(f"[DEBUG] Is multi-agent command: {is_multi_agent_command}")
                
                # Priority routing: Multi-agent commands first
                if is_multi_agent_command or (has_file_operation and has_whatsapp_intent):
                    state['detected_intent'] = "multi_agent"
                    state['agent_name'] = "multi_agent"
                    print(f"[DEBUG] Routed to: multi_agent (file + whatsapp)")
                    return state
                
                # WhatsApp commands override conversational detection
                elif is_whatsapp_command or (has_whatsapp_intent and not has_file_operation and not is_capability_question):
                    state['detected_intent'] = "whatsapp"
                    state['agent_name'] = "whatsapp"
                    print(f"[DEBUG] Routed to: whatsapp")
                    return state
                
                # File operations (actual operations, not capability questions)
                elif has_file_operation and not is_capability_question and not is_general_question:
                    state['detected_intent'] = "filesearch"
                    state['agent_name'] = "filesearch"
                    print(f"[DEBUG] Routed to: filesearch")
                    return state
                
                # Capability questions and general questions go to conversation
                elif is_capability_question or is_general_question:
                    state['detected_intent'] = "conversation"
                    state['agent_name'] = "conversation"
                    print(f"[DEBUG] Routed to: conversation (capability/general question)")
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
                  * Natural: "where is my report", "open that presentation", "find my photos"
                  
                - conversation: Conversational interactions, greetings, help
                  * Patterns: "hello", "help", "what can you do", "who are you", "thanks"
                  * Natural: "hi there", "I need help", "goodbye", "thank you"
                  
                - multi_agent: Complex tasks requiring multiple agents (FILE + COMMUNICATION)
                  * Patterns: "send [file] to [contact]", "find and share", "search and message"
                  * Natural: "send my report to boss on whatsapp", "find photo and share with mom"
                  * Key indicators: file words + communication words together
                
                CLASSIFICATION RULES:
                1. If command contains BOTH file operations AND communication -> multi_agent
                2. If contains file words (document, file, report, ownership, photo, etc.) AND send/share/message words -> multi_agent
                3. If clear WhatsApp/messaging intent only -> whatsapp  
                4. If clear file operation intent only -> filesearch
                5. If conversational/greeting -> conversation
                6. If unclear -> conversation (Vaani will ask for clarification)
                
                Examples:
                - "Send report.pdf to boss on WhatsApp" -> multi_agent
                - "Send the ownership file to jay" -> multi_agent (file + send)
                - "Find ownership document and send to jay" -> multi_agent
                - "Share my presentation with team" -> multi_agent
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
            # For simple WhatsApp messages without file operations, route directly to WhatsApp agent
            user_input_lower = user_input.lower()
            file_terms = ["ownership", "document", "file", "report", "presentation", "photo", "video", "pdf", "doc"]
            has_file_intent = any(term in user_input_lower for term in file_terms)
            
            print(f"[DEBUG] Multi-agent workflow called for: {user_input}")
            print(f"[DEBUG] Has file intent: {has_file_intent}")
            
            # If it's just a WhatsApp message without file operations, delegate to WhatsApp agent
            if not has_file_intent and any(pattern in user_input_lower for pattern in ["send whatsapp", "whatsapp to", "message to"]):
                print(f"[DEBUG] Multi-agent delegating to WhatsApp agent: {user_input}")
                whatsapp_result = self.agents["whatsapp"].process_command(user_input)
                return whatsapp_result
            
            # First, try to parse the multi-agent intent
            system_prompt = """Analyze this command to determine the multi-agent workflow needed:
            
            WORKFLOW TYPES:
            1. file_to_whatsapp: Find/prepare file and send via WhatsApp
            2. search_and_share: Search for files and prepare for sharing
            3. open_and_inform: Open file and notify someone
            4. whatsapp_only: Simple WhatsApp message without files
            
            Extract:
            - workflow_type: [file_to_whatsapp/search_and_share/open_and_inform/whatsapp_only]
            - file_query: [file name/pattern to find] (empty if no file)
            - recipient: [person to send to] (NEVER extract 'to', 'for', or prepositions)
            - message: [optional message content]
            
            IMPORTANT: For recipient extraction, identify the actual person's name:
            - "send WhatsApp message to Jay lion is coming" -> recipient: "Jay", message: "lion is coming"
            - "send report.pdf to boss" -> recipient: "boss", file: "report.pdf"
            - "message mom about dinner" -> recipient: "mom", message: "about dinner"
            
            NEVER extract prepositions (to, for, with, about) as recipient names.
            
            Examples:
            - "Send report.pdf to boss on WhatsApp" -> file_to_whatsapp, report.pdf, boss
            - "Find my photos and share with mom" -> search_and_share, photos, mom
            - "Send WhatsApp message to Jay lion is coming" -> whatsapp_only, (empty), Jay, lion is coming
            
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
            
            print(f"[DEBUG] LLM parsing response: {response_text}")
            
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
                    # Additional validation to prevent extracting prepositions
                    if recipient.lower() in ["to", "for", "with", "about", "from", "the", "a", "an"]:
                        print(f"[DEBUG] Ignoring invalid recipient: {recipient}")
                        recipient = ""
                elif line.startswith("MESSAGE:"):
                    message = line.replace("MESSAGE:", "").strip()
            
            print(f"[DEBUG] Parsed - Workflow: {workflow_type}, File: {file_query}, Recipient: {recipient}, Message: {message}")
            
            # Execute the multi-agent workflow
            if workflow_type == "file_to_whatsapp" and file_query and recipient:
                return self._execute_file_to_whatsapp_workflow(file_query, recipient, message)
            elif workflow_type == "search_and_share" and file_query:
                return self._execute_search_and_share_workflow(file_query, recipient)
            elif workflow_type == "whatsapp_only" and recipient:
                # For simple WhatsApp messages, delegate to WhatsApp agent
                whatsapp_command = f"Send WhatsApp to {recipient}: {message}" if message else f"Send WhatsApp to {recipient}"
                print(f"[DEBUG] Multi-agent creating WhatsApp command: {whatsapp_command}")
                whatsapp_result = self.agents["whatsapp"].process_command(whatsapp_command)
                return whatsapp_result
            else:
                # Fallback to generic workflow
                return self._execute_generic_multi_agent_workflow(user_input)
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Hi! I'm Vaani. I had trouble understanding that multi-agent request. Error: {str(e)}",
                "workflow": "multi_agent_error",
                "error": str(e)
            }
    
    def _execute_generic_multi_agent_workflow(self, user_input: str) -> Dict[str, Any]:
        """Execute generic multi-agent workflow when pattern isn't clear"""
        try:
            # Use LLM to understand what the user wants and execute it
            system_prompt = """You are Vaani, an AI assistant that executes tasks directly.
            
            The user gave a command that involves multiple actions. Analyze it and execute the appropriate workflow:
            
            AVAILABLE ACTIONS:
            1. Find/search files: Use filesearch agent
            2. Send WhatsApp messages: Use whatsapp agent 
            3. Combined file + messaging: Execute both in sequence
            
            EXECUTION APPROACH:
            - Don't ask for clarification - execute what makes the most sense
            - If file mentioned, try to find it first
            - If messaging mentioned, create WhatsApp message
            - If both, do file search then messaging
            
            Parse this command and determine the best execution path:
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            analysis = response.content.strip()
            
            # Try to extract file and recipient info from the original command
            user_input_lower = user_input.lower()
            
            # Extract potential file references
            file_terms = ["ownership", "document", "file", "report", "presentation", "photo", "video", "pdf", "doc"]
            mentioned_files = [term for term in file_terms if term in user_input_lower]
            
            # Extract potential recipients (improved logic to avoid extracting prepositions)
            words = user_input.split()
            potential_recipients = []
            for i, word in enumerate(words):
                if word.lower() in ["to", "for"] and i + 1 < len(words):
                    next_word = words[i + 1]
                    # Skip common words that aren't names
                    if next_word.lower() not in ["the", "a", "an", "my", "your", "his", "her", "their", "our", "whatsapp", "message", "file"]:
                        potential_recipients.append(next_word)
            
            print(f"[DEBUG] Generic multi-agent - Files: {mentioned_files}, Recipients: {potential_recipients}")
            
            # If we found file references and recipients, execute file-to-whatsapp workflow
            if mentioned_files and potential_recipients:
                file_query = mentioned_files[0]
                recipient = potential_recipients[0]
                return self._execute_file_to_whatsapp_workflow(file_query, recipient)
            
            # If only file mentioned, do file search
            elif mentioned_files:
                file_result = self.agents["filesearch"].process_command(f"find {mentioned_files[0]}")
                if file_result.get("success"):
                    return {
                        "success": True,
                        "message": f"✅ Found files related to '{mentioned_files[0]}'! {file_result.get('message', '')}",
                        "workflow": "file_search",
                        "file_results": file_result.get("search_results", [])
                    }
                else:
                    return {
                        "success": False,
                        "message": f"🔍 I couldn't find any files related to '{mentioned_files[0]}'. Could you be more specific?",
                        "workflow": "file_search_failed"
                    }
            
            # If messaging intent detected, handle as WhatsApp
            elif any(word in user_input_lower for word in ["send", "message", "tell", "whatsapp"]):
                print(f"[DEBUG] Generic multi-agent delegating to WhatsApp: {user_input}")
                whatsapp_result = self.agents["whatsapp"].process_command(user_input)
                return whatsapp_result
            
            # Fallback - execute direct action instead of giving guidance
            else:
                # Instead of generic guidance, try to execute the most likely action
                return self.agents["conversation"].process_conversation(user_input)
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Hi! I'm Vaani. I had trouble with that request. Could you try rephrasing it? Error: {str(e)}",
                "workflow": "generic_error",
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