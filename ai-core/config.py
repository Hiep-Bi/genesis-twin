"""AI Core Configuration"""
import os
from dotenv import load_dotenv

load_dotenv()


class AIConfig:
    """AI Core configuration"""
    
    # Gemini API
    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY",
        "AIzaSyAoAqbfLHYxgGokxM7GFEoEfeXdESREwaQ"
    )
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    GEMINI_MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", "2048"))
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Channels
    CHANNEL_SENSOR_DATA = "genesis:sensor:data"
    CHANNEL_MACHINE_STATE = "genesis:machine:state"
    CHANNEL_AI_PREDICTIONS = "genesis:ai:predictions"
    CHANNEL_ALERTS = "genesis:alerts"
    
    # Prediction thresholds
    DEFECT_CONFIDENCE_THRESHOLD = 0.75
    ENERGY_ANOMALY_THRESHOLD = 0.8
    MAINTENANCE_PREDICTION_DAYS = 7
    
    # Model parameters
    ANOMALY_DETECTION_WINDOW = 100  # Number of data points for anomaly detection
    PREDICTION_INTERVAL_SECONDS = 60  # Run predictions every 60 seconds


config = AIConfig()

