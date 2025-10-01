"""Configuration settings using Pydantic and YAML."""

from typing import Optional, Tuple
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
import yaml


class SimulationConfig(BaseSettings):
    """Simulation-specific configuration."""
    
    time_step: float = Field(default=1.0 / 240.0, description="Physics simulation time step")
    max_steps: int = Field(default=1000, description="Maximum simulation steps")
    gravity: Tuple[float, float, float] = Field(default=(0, 0, -9.81), description="Gravity vector")
    use_gui: bool = Field(default=False, description="Use PyBullet GUI")


class APIConfig(BaseSettings):
    """API server configuration."""
    
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, description="API port")
    reload: bool = Field(default=False, description="Auto-reload on code changes")
    log_level: str = Field(default="info", description="Logging level")


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    
    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="json", description="Log format (json or console)")
    output_file: Optional[str] = Field(default=None, description="Log output file")


class Settings(BaseSettings):
    """Main application settings."""
    
    app_name: str = Field(default="optimizer", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = False


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def load_settings_from_yaml(config_path: Path) -> Settings:
    """
    Load settings from a YAML configuration file.
    
    Args:
        config_path: Path to YAML config file
        
    Returns:
        Settings object
    """
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
    
    return Settings(**config_data)
