from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class JulesSettings(BaseSettings):
    # one-liner config, v2-style
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
        case_sensitive=False, extra="ignore"
    )

    # Core
    jules_env: str = Field(default="development")
    jules_debug: bool = True
    jules_api_host: str = "0.0.0.0"
    jules_api_port: int = 8080

    # Logging
    jules_log_level: str = Field(default="INFO")
    jules_log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    jules_log_file: Optional[str] = Field(default="optimizer.log")

    # Simulation
    simulation_engine: str = Field(default="pybullet")
    simulation_gravity: float = Field(default=-9.8)
    simulation_time_step: float = Field(default=0.01)

    # Secrets typed as SecretStr
    openai_api_key: Optional[SecretStr] = None
    anthropic_api_key: Optional[SecretStr] = None
    google_api_key: Optional[SecretStr] = None
    github_token: Optional[SecretStr] = None
    neo4j_password: Optional[SecretStr] = None
    vector_db_password: Optional[SecretStr] = None
    redis_password: Optional[SecretStr] = None
    jwt_secret_key: Optional[SecretStr] = None