"""
Configuration module for MixtilesImageGenerator API
"""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()


class Settings():
    """Application settings"""

    # OpenAI API Key
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    # Claude API Key
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY")
    # Groq API Key
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    # Gemini API Key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

# Create settings instance
settings = Settings()
