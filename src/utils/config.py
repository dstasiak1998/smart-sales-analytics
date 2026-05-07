from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_env: str = "development"
    app_port: int = 8000
    debug: bool = True

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "sales_analytics"
    db_user: str = "postgres"
    db_password: str = "postgres"

    api_key: str = "dev-secret-key"
    streamlit_port: int = 8501

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+psycopg2://"
            f"{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}"
            f"/{self.db_name}"
        )

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()