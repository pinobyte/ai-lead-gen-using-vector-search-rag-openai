from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB_NAME: str
    APIFY_API_KEY: str
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DB: str
    COMPANY_PROFILE_JSON_MAPPING_QUERY: str
    SEARCH_INDEX_NAME: str
    SEARCH_SERVICE_NAME: str
    VECTOR_SEARCH_DIM: int
    SEARCH_API_KEY: str
    SEARCH_ENDPOINT: str
    EMBEDDING_ENDPOINT: str
    EMBEDDING_KEY:str
    AZURE_COMPLETION_ENDPOINT: str
    AZURE_OPENAI_KEY: str
    EMBEDDING_API_VERSION: str
    COMPLETION_API_VERSION: str
    EMBEDDING_MODEL_NAME: str
    GOOGLE_CLIENT_ID: str

    class Config:
        env_file = str(Path(__file__).resolve().parent / ".env")

settings = Settings()