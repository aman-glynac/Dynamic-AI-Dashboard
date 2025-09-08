"""
Configuration for Input Parser Agent
"""

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()


@dataclass
class GroqConfig:
    """Groq LLM configuration."""
    api_key: str = ""
    model: str = "llama-3.3-70b-versatile"
    max_tokens: int = 1000
    temperature: float = 0.1
    timeout: int = 30


@dataclass
class DatabaseConfig:
    """Database configuration."""
    db_path: str = "test_dashboard.db"
    schema_cache_ttl: int = 3600
    max_connections: int = 5


@dataclass
class AgentConfig:
    """Main agent configuration."""
    groq: GroqConfig
    database: DatabaseConfig
    
    text_cleaning_enabled: bool = True
    validation_threshold: float = 0.3
    confidence_threshold: float = 0.5
    checkpoint_db_path: str = "agent_checkpoints.db"
    enable_checkpoints: bool = True
    
    @classmethod
    def from_env(cls) -> 'AgentConfig':
        """Create configuration from environment variables."""
        groq_config = GroqConfig(
            api_key=os.getenv("GROQ_API_KEY", ""),
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("GROQ_TEMPERATURE", "0.1")),
            timeout=int(os.getenv("GROQ_TIMEOUT", "30"))
        )
        
        db_config = DatabaseConfig(
            db_path=os.getenv("DATABASE_PATH", "test_dashboard.db"),
            schema_cache_ttl=int(os.getenv("SCHEMA_CACHE_TTL", "3600")),
            max_connections=int(os.getenv("DB_MAX_CONNECTIONS", "5"))
        )
        
        return cls(
            groq=groq_config,
            database=db_config,
            text_cleaning_enabled=os.getenv("TEXT_CLEANING_ENABLED", "true").lower() == "true",
            validation_threshold=float(os.getenv("VALIDATION_THRESHOLD", "0.3")),
            confidence_threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.5")),
            checkpoint_db_path=os.getenv("CHECKPOINT_DB_PATH", "agent_checkpoints.db"),
            enable_checkpoints=os.getenv("ENABLE_CHECKPOINTS", "true").lower() == "true"
        )
    
    def validate(self) -> bool:
        """Validate configuration."""
        if not self.groq.api_key:
            print("⚠️  Warning: GROQ_API_KEY not set")
            return False
        
        if not os.path.exists(self.database.db_path):
            print(f"⚠️  Warning: Database file not found at {self.database.db_path}")
            return False
        
        return True


config = AgentConfig.from_env()
