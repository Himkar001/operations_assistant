"""
Configuration loader for the Operations Assistant project.
Loads environment variables and provides typed configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Model configuration
    model_type: str = os.getenv("MODEL_TYPE", "ollama")
    model_name: str = os.getenv("MODEL_NAME", "mistral")
    
    # API Keys (only needed for cloud models)
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    
    # MCP Server settings
    mcp_host: str = os.getenv("MCP_HOST", "localhost")
    mcp_port: int = int(os.getenv("MCP_PORT", "8000"))
    
    # Crew settings
    crew_verbose: bool = os.getenv("CREW_VERBOSE", "true").lower() == "true"
    crew_max_iter: int = int(os.getenv("CREW_MAX_ITER", "10"))
    
    # Paths
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", "./outputs"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

def get_model_config() -> dict:
    """Get model configuration based on settings."""
    settings = get_settings()
    
    if settings.model_type == "ollama":
        return {
            "model": settings.model_name,
            "base_url": "http://localhost:11434",
        }
    elif settings.model_type == "anthropic":
        return {
            "model": "claude-3-5-sonnet-20241022",
            "api_key": settings.anthropic_api_key,
        }
    elif settings.model_type == "openai":
        return {
            "model": settings.openai_api_key or "gpt-4-turbo",
            "api_key": settings.openai_api_key,
        }
    elif settings.model_type == "groq":
        return {
            "model": f"groq/{settings.model_name}" if settings.model_name else "groq/llama-3.3-70b-versatile",
            "api_key": settings.groq_api_key,
        }
    else:
        raise ValueError(f"Unknown model type: {settings.model_type}")

# Create output directories if they don't exist
def ensure_output_dirs():
    """Create necessary output directories."""
    settings = get_settings()
    (settings.output_dir / "reports").mkdir(parents=True, exist_ok=True)
    (settings.output_dir / "traces").mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "documents").mkdir(parents=True, exist_ok=True)
