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
    file: Optional[str] = "optimizer.log"

class Settings(BaseModel):
    simulation: SimulationSettings
    api: APISettings
    logging: LoggingSettings

def load_config(path: str = "config.yml") -> Settings:
    """
    Loads configuration from a YAML file.

    If the file is not found, it returns a default Settings object.
    This is useful for environments like testing where a config file may not be present.
    """
    try:
        with open(path, "r") as f:
            config_data = yaml.safe_load(f)
        return Settings(**config_data)
    except FileNotFoundError:
        return Settings(
            simulation=SimulationSettings(),
            api=APISettings(),
            logging=LoggingSettings(),
        )

settings = load_config()