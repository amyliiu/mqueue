from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    SMS_RATE_LIMIT: str = "5/minute"
    
    class Config:
        env_file = ".env"

settings = Settings()