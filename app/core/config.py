from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Database
    # database_url: str = Field(..., alias="DATABASE_URL")
    postgres_db: str = Field(..., alias="POSTGRES_DB")
    postgres_user: str = Field(..., alias="POSTGRES_USER")
    postgres_password: str = Field(..., alias="POSTGRES_PASSWORD")
    postgres_port: int = Field(..., alias="POSTGRES_PORT")
    postgres_host: str = Field(..., alias="POSTGRES_HOST")

    # Redis
    redis_url: str = Field(..., alias="REDIS_URL")

    # JWT
    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # MailJet
    mailjet_api_key: str = Field(..., alias="MAILJET_API_KEY")
    mailjet_api_secret: str = Field(..., alias="MAILJET_API_SECRET")
    mailjet_from_email: str = Field(..., alias="MAILJET_FROM_EMAIL")
    mailjet_from_name: str = Field(default="Coffee Shop", alias="MAILJET_FROM_NAME")

    # Application
    verification_code_expire_hours: int = Field(
        default=48, alias="VERIFICATION_CODE_EXPIRE_HOURS"
    )
    environment: str = Field(default="development", alias="ENVIRONMENT")

    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        ).unicode_string()

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
