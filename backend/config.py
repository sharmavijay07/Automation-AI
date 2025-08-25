"""
Configuration module for AI Task Automation Assistant
Handles environment variables and application settings
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # AI/LLM Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    
    # WhatsApp Configuration
    WHATSAPP_API_KEY: str = os.getenv("WHATSAPP_API_KEY", "demo_whatsapp_api_key_12345")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "demo_phone_id_67890")
    
    # Server Configuration
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "127.0.0.1")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", "8000"))
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    # Speech Configuration
    SPEECH_TIMEOUT: int = int(os.getenv("SPEECH_TIMEOUT", "5"))
    SPEECH_PHRASE_TIME_LIMIT: int = int(os.getenv("SPEECH_PHRASE_TIME_LIMIT", "10"))
    
    # Agent Configuration
    AGENT_TEMPERATURE: float = float(os.getenv("AGENT_TEMPERATURE", "0.1"))
    MAX_RESPONSE_TOKENS: int = int(os.getenv("MAX_RESPONSE_TOKENS", "1000"))
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate essential configuration"""
        if not cls.GROQ_API_KEY or cls.GROQ_API_KEY == "your_groq_api_key_here":
            print("⚠️  Warning: GROQ_API_KEY not set properly. Please update .env file.")
            return False
        return True

# Create global config instance
config = Config()