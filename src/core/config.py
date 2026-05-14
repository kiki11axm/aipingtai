from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    app_name: str = "现代农业与绿色低碳AI平台"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/agri_carbon"
    )
    database_pool_size: int = 20
    database_max_overflow: int = 10

    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_pool_size: int = 50

    influxdb_url: str = os.getenv("INFLUXDB_URL", "http://localhost:8086")
    influxdb_token: str = os.getenv("INFLUXDB_TOKEN", "my-token")
    influxdb_org: str = os.getenv("INFLUXDB_ORG", "agri-carbon")
    influxdb_bucket: str = os.getenv("INFLUXDB_BUCKET", "farm_db")

    minio_endpoint: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    minio_bucket_satellite: str = "farm-imagery-satellite"
    minio_bucket_drone: str = "farm-imagery-drone"
    minio_bucket_documents: str = "farm-documents"
    minio_bucket_qrcode: str = "farm-qrcode"

    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    satellite_api_url: str = os.getenv(
        "SATELLITE_API_URL",
        "https://scihub.copernicus.eu/apihub/"
    )
    satellite_api_key: str = os.getenv("SATELLITE_API_KEY", "")

    weather_api_url: str = os.getenv(
        "WEATHER_API_URL",
        "https://api.weather.gov.cn/"
    )

    kafka_bootstrap_servers: str = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092"
    )

    blockchain_node_url: str = os.getenv(
        "BLOCKCHAIN_NODE_URL",
        "http://localhost:8545"
    )
    blockchain_contract_address: str = os.getenv(
        "BLOCKCHAIN_CONTRACT_ADDRESS",
        "0x0000000000000000000000000000000000000000"
    )

    ai_api_base_url: str = os.getenv("AI_API_BASE_URL", "http://localhost:8084")
    ai_api_timeout: int = 500

    cors_origins: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
