import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "The Fracture Vaults"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "FRACTURE_VAULTS_SECRET_CHANGE_ME")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fracture_vaults.db")
    PAYHIP_IPN_SECRET: str = os.getenv("PAYHIP_IPN_SECRET", "")
    PAYHIP_STORE_URL: str = "https://payhip.com/ForgedInIceVaults"
    ENABLE_SCHEDULER: bool = False
    AI_ENABLED: bool = False
    SIMULATION_ENABLED: bool = True
    EDUCATION_ENABLED: bool = True
    PROGRESSION_ENABLED: bool = True
    REWARDS_ENABLED: bool = True
    ADS_ENABLED: bool = False
    SUBSCRIPTIONS_ENABLED: bool = False
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
