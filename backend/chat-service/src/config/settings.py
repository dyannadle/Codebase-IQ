from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    QDRANT_URL: str
    QDRANT_API_KEY: str = ""
    
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
