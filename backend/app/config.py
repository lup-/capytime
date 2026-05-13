from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    JWT_SECRET_KEY: str = "secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8080/api/oauth/google/callback"

    YANDEX_CLIENT_ID: str = ""
    YANDEX_CLIENT_SECRET: str = ""
    YANDEX_REDIRECT_URI: str = "http://localhost:8080/api/oauth/yandex/callback"

    YANDEX_TELEMOST_LOGIN: str = ""
    YANDEX_TELEMOST_PASSWORD: str = ""
    YANDEX_TELEMOST_COOKIES_PATH: str = "yandex_telemost_cookies.json"

    SENDSAY_LOGIN: str = ""
    SENDSAY_SUBLOGIN: str = ""
    SENDSAY_PASSWORD: str = ""

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_LOGIN: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""

    FRONTEND_URL: str = "https://capytime.ru"

    class Config:
        env_file = ".env"


settings = Settings()
