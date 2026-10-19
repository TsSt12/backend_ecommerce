from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "API Stickers"
    DATABASE_URL: str
    CORS_ORIGINS: str = "http://localhost:5173"

    # JWT — se cargan en la Clase 7
    SECRET_KEY: str = "CAMBIAR_EN_ENV"   # sin default real, siempre desde .env
    ALGORITHM: str = "HS256"
    ACCESS_MIN: int = 30
    REFRESH_MIN: int = 10080            # 7 días en minutos

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
