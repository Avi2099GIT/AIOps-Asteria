from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "Asteria AIOps"
    api_key: str = "dev-token"
    kafka_bootstrap: str = "localhost:9092"
    events_topic: str = "asteria-events"
    redis_host: str = "localhost"
    redis_port: int = 6380

    # Postgres DB (Phase 5)
    database_host: str = "localhost"
    database_port: int = 5432
    database_user: str = "asteria"
    database_password: str = "asteria_pass"
    database_name: str = "asteria_db"

    class Config:
        env_prefix = ""
        env_file = ".env"

settings = Settings()
