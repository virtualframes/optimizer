import yaml
from pydantic import BaseModel, Field
from typing import Optional

class SimulationSettings(BaseModel):
    engine: str = "pybullet"
    gravity: float = -9.8
    time_step: float = 0.01

class APISettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000

class LoggingSettings(BaseModel):
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = "intel_harvester.log"

class Settings(BaseModel):
    simulation: SimulationSettings
    api: APISettings
    logging: LoggingSettings

# A default settings object to be used when no config file is specified.
settings = Settings(
    simulation=SimulationSettings(),
    api=APISettings(),
    logging=LoggingSettings(),
)

def load_config_into_global_settings(path: str):
    """
    Loads configuration from a YAML file and updates the global settings object.
    Raises FileNotFoundError if the file cannot be found.
    """
    global settings
    try:
        with open(path, "r") as f:
            config_data = yaml.safe_load(f)
        settings = Settings(**config_data)
    except FileNotFoundError:
        # Re-raise the exception to be handled by the caller
        raise