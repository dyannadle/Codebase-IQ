from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    QDRANT_URL: str
    QDRANT_API_KEY: str = ""
    
    REDIS_URL: str
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720
    
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    OPENAI_API_KEY: str
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
