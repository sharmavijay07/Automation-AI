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
            "whatsapp": whatsapp_agent
        }
        
        # Build MCP workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the MCP workflow for agent coordination"""
        
        def intent_detection_node(state: AgentManagerState) -> AgentManagerState:
            """Detect user intent and route to appropriate agent"""
            try:
                # Initialize default values if not present
                if 'detected_intent' not in state:
                    state['detected_intent'] = ""
                if 'agent_name' not in state:
                    state['agent_name'] = ""
                if 'error' not in state:
                    state['error'] = None
                system_prompt = """You are an intent classifier for an AI assistant that handles daily tasks.
                Analyze the user input and classify it into one of these categories:
                
                AVAILABLE AGENTS:
                - whatsapp: For sending WhatsApp messages (keywords: whatsapp, message, send to, text to)
                - unsupported: For any other requests not yet implemented
                
                Examples:
                - "Send WhatsApp to Jay: Hello" -> whatsapp
                - "Message Mom on WhatsApp: I'm coming" -> whatsapp
                - "WhatsApp Vijay: Meeting at 5pm" -> whatsapp
                - "Call John" -> unsupported
                - "Open file" -> unsupported
                
                Return ONLY the agent name (whatsapp, unsupported). Nothing else."""
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=state['user_input'])
                ]
                
                response = self.llm.invoke(messages)
                intent = response.content.strip().lower()
                
                # Validate intent
                if intent in self.agents:
                    state['detected_intent'] = intent
                    state['agent_name'] = intent
                elif intent == "unsupported":
                    state['detected_intent'] = "unsupported"
                    state['agent_name'] = "unsupported"
                else:
                    # Fallback to keyword detection
                    user_input_lower = state['user_input'].lower()
                    if any(keyword in user_input_lower for keyword in ["whatsapp", "message", "send to", "text to"]):
                        state['detected_intent'] = "whatsapp"
                        state['agent_name'] = "whatsapp"
                    else:
                        state['detected_intent'] = "unsupported"
                        state['agent_name'] = "unsupported"
                
                return state
                
            except Exception as e:
                state['error'] = f"Error in intent detection: {str(e)}"
                return state
        
        def route_to_agent_node(state: AgentManagerState) -> AgentManagerState:
            """Route command to the appropriate agent"""
            if state.get('error'):
                return state
            
            try:
                if state.get('agent_name') == "unsupported":
                    state['agent_response'] = {
                        "success": False,
                        "message": "🚧 This feature is not yet implemented. Currently, I only support WhatsApp messaging. Try: 'Send WhatsApp to [name]: [message]'",
                        "error": "Unsupported feature"
                    }
                    return state
                
                # Route to specific agent
                if state.get('agent_name') == "whatsapp":
                    state['agent_response'] = self.agents["whatsapp"].process_command(state['user_input'])
                else:
                    state['agent_response'] = {
                        "success": False,
                        "message": "❌ Unknown agent requested",
                        "error": "Unknown agent"
                    }
                
                return state
                
            except Exception as e:
                state['error'] = f"Error routing to agent: {str(e)}"
                state['agent_response'] = {
                    "success": False,
                    "message": f"❌ Error: {str(e)}",
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
            
            return {
                "success": not bool(result.get('error')),
                "message": result.get('final_response', ''),
                "intent": result.get('detected_intent', ''),
                "agent_used": result.get('agent_name', ''),
                "agent_response": result.get('agent_response', {}),
                "error": result.get('error')
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ MCP Error: {str(e)}",
                "intent": "error",
                "agent_used": "none",
                "agent_response": {},
                "error": str(e)
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