from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "DStarix AI Assistant"
    app_version: str = "1.0.0"
    debug: bool = True

    gemini_api_key: str = ""
    database_url: str = ""

    class Config:
        env_file = ".env"


settings = Settings()