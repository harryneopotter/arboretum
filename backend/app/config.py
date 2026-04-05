"""
Configuration for Plant Care FastAPI Backend.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str | None = None
    db_user: str | None = None
    db_pass: str | None = None
    db_name: str | None = None
    db_host: str | None = None

    # Qdrant
    qdrant_url: str = "https://27aff9e6-8dae-4699-8803-9ee4fd06af81.eu-central-1-0.aws.cloud.qdrant.io"
    qdrant_api_key: str = ""

    # Collections
    plants_collection: str = "plants"
    plant_images_collection: str = "plant-images"

    # Vector names
    dense_vector_name: str = "plant-vector-dense"
    sparse_vector_name: str = "plant-vector-sparse"
    image_vector_name: str = "image-vector"

    # Vector dimensions
    dense_dim: int = 1536
    image_dim: int = 512

    # Search limits
    default_search_limit: int = 5
    max_search_limit: int = 20

    # OpenAI
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"

    # Beta telemetry / admin access
    admin_log_token: str | None = None
    beta_telemetry_enabled: bool = True

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
