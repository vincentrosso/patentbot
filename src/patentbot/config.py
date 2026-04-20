"""
Configuration module for PatentBot
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    uspto_api_key: str
    anthropic_api_key: str
    voyage_api_key: str
    uspto_rate_limit: int = 45
    google_rate_limit: float = 1.0
    db_path: str = "patents.db"
    max_workers: int = 10
    batch_size: int = 100

def load_config() -> Config:
    """Load configuration from environment"""
    from .env import (
        get_uspto_api_key,
        get_anthropic_api_key,
        get_voyage_api_key,
        get_uspto_rate_limit,
        get_google_rate_limit
    )
    
    return Config(
        uspto_api_key=get_uspto_api_key(),
        anthropic_api_key=get_anthropic_api_key(),
        voyage_api_key=get_voyage_api_key(),
        uspto_rate_limit=get_uspto_rate_limit(),
        google_rate_limit=get_google_rate_limit()
    )