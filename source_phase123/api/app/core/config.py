from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    project_name: str = "Asteria AIOps"
    api_key: str = "dev-token"
    kafka_bootstrap: str = "localhost:9092"
    events_topic: str = "asteria-events"
    redis_host: str = "localhost"
    redis_port: int = 6380

settings = Settings()
