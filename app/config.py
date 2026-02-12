from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Trip API"
    api_version: str = "v1"
    environment: str = "local"

    class Config:
        env_file = ".env"


settings = Settings()
