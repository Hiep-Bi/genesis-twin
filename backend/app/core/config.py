"""Application Configuration"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
import secrets


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Genesis Twin"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = secrets.token_urlsafe(32)
    
    # Password requirements
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Database
    DATABASE_URL: str = "postgresql://genesis_user:genesis_pass@localhost:5432/genesis_twin"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # 5 minutes
    
    # WebSocket
    WS_MESSAGE_QUEUE_SIZE: int = 1000
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # AI Core
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 2048
    
    # Simulation
    SIMULATION_INTERVAL_MS: int = 1000
    NUM_SENSORS: int = 1000
    NUM_MACHINES: int = 50
    NUM_ROBOTS: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # IP Whitelist for dashboard access (empty list = allow all)
    ALLOWED_IPS: List[str] = []  # e.g., ["192.168.1.100", "10.0.0.5"]
    ALLOWED_NETWORKS: List[str] = []  # e.g., ["192.168.1.0/24", "10.0.0.0/8"]
    ENABLE_IP_WHITELIST: bool = False  # Set to True to enable IP whitelist
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("ALLOWED_IPS", pre=True)
    def assemble_allowed_ips(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v or []
    
    @validator("ALLOWED_NETWORKS", pre=True)
    def assemble_allowed_networks(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v or []
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

