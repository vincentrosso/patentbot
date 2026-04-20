"""
Environment configuration - load API keys and settings from .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(ENV_PATH)

def get_uspto_api_key() -> str:
    """Get USPTO API key"""
    key = os.getenv("USPTO_API_KEY")
    if not key:
        raise ValueError("USPTO_API_KEY not set in .env")
    return key

def get_anthropic_api_key() -> str:
    """Get Anthropic API key"""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not set in .env")
    return key

def get_voyage_api_key() -> str:
    """Get Voyage API key"""
    key = os.getenv("VOYAGE_API_KEY")
    if not key:
        raise ValueError("VOYAGE_API_KEY not set in .env")
    return key

def get_uspto_rate_limit() -> int:
    """Get USPTO requests per minute"""
    return int(os.getenv("USPTO_REQUESTS_PER_MINUTE", "45"))

def get_google_rate_limit() -> float:
    """Get Google requests per second"""
    return float(os.getenv("GOOGLE_REQUESTS_PER_SECOND", "1"))