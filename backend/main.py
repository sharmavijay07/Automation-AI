"""
FastAPI Backend for AI Task Automation Assistant
Main server handling voice/text commands and agent coordination
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import logging
from datetime import datetime

from config import config
from agents.agent_manager import agent_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Task Automation Assistant",
    description="Voice-powered AI assistant for automating daily tasks",
    version="1.0.0"
)

# Add CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Allow Next.js dev server and all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class CommandRequest(BaseModel):
    """Request model for text commands"""
    command: str
    user_id: Optional[str] = "default_user"

class CommandResponse(BaseModel):
    """Response model for processed commands"""
    success: bool
    message: str
    intent: str
    agent_used: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    agents_available: list

# @app.on_startup
# async def startup_event():
#     """Initialize application on startup"""
#     logger.info("🚀 Starting AI Task Automation Assistant...")
    
#     # Validate configuration
#     if not config.validate_config():
#         logger.warning("⚠️  Configuration validation failed. Some features may not work.")
    
#     logger.info("✅ AI Task Automation Assistant started successfully!")

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        agents_available=agent_manager.get_available_agents()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        agents_available=agent_manager.get_available_agents()
    )

@app.post("/process-command", response_model=CommandResponse)
async def process_command(request: CommandRequest):
    """
    Process text or voice-to-text commands through MCP agent manager
    """
    try:
        logger.info(f"Processing command: {request.command}")
        
        if not request.command or not request.command.strip():
            raise HTTPException(status_code=400, detail="Command cannot be empty")
        
        # Process command through agent manager
        result = agent_manager.process_command(request.command)
        
        # Log the result
        logger.info(f"Command processed - Success: {result['success']}, Agent: {result['agent_used']}")
        
        response = CommandResponse(
            success=result["success"],
            message=result["message"],
            intent=result["intent"],
            agent_used=result["agent_used"],
            timestamp=datetime.now().isoformat(),
            details={
                "original_command": request.command,
                "agent_response": result["agent_response"],
                "error": result.get("error")
            }
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing command: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/process-voice")
async def process_voice(audio_file: UploadFile = File(...)):
    """
    Process voice commands (placeholder for future implementation)
    Currently returns a message directing to use text commands
    """
    try:
        logger.info(f"Voice file received: {audio_file.filename}")
        
        # For MVP, we'll direct users to use text commands
        # In future versions, this will handle speech-to-text conversion
        
        return JSONResponse(
            content={
                "success": False,
                "message": "🎤 Voice processing is not yet implemented in the backend. Please use text commands for now. Try: 'Send WhatsApp to Jay: Hello!'",
                "intent": "voice_not_implemented",
                "agent_used": "none",
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing voice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")

@app.get("/agents")
async def get_agents():
    """Get list of available agents"""
    try:
        agents = agent_manager.get_available_agents()
        return {
            "success": True,
            "agents": agents,
            "count": len(agents),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config")
async def get_config():
    """Get application configuration (non-sensitive info only)"""
    try:
        return {
            "success": True,
            "config": {
                "groq_model": config.GROQ_MODEL,
                "fastapi_host": config.FASTAPI_HOST,
                "fastapi_port": config.FASTAPI_PORT,
                "agent_temperature": config.AGENT_TEMPERATURE,
                "max_response_tokens": config.MAX_RESPONSE_TOKENS,
                "agents_available": agent_manager.get_available_agents()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Endpoint not found",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    # Validate configuration before starting
    if not config.validate_config():
        logger.error("❌ Configuration validation failed. Please check your .env file.")
        exit(1)
    
    # Use port 8000 for Next.js frontend integration
    HOST = "0.0.0.0"
    PORT = 8000
    
    logger.info(f"🚀 Starting FastAPI server on {HOST}:{PORT}")
    logger.info(f"📡 API will be available at: http://localhost:{PORT}")
    logger.info(f"🌐 Next.js frontend should connect to: http://localhost:{PORT}")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )