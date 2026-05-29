import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "DeepFake Shield"
    API_V1_STR: str = "/api/v1"

    # Security & JWT
    # SECRET_KEY MUST be provided via environment for production. No default is set here.
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    ALGORITHM: str = "HS256"

    # Databases & Caching (no hard-coded credentials)
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None

    # S3 Storage Configuration (do not hard-code credentials)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = "http://localhost:9000"
    S3_BUCKET_NAME: str = "uploads"
    S3_REGION_NAME: Optional[str] = "us-east-1"
    
    # gRPC Inference Server
    GRPC_INFERENCE_HOST: str = "localhost"
    GRPC_INFERENCE_PORT: int = 50051

    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
