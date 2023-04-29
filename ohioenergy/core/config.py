from pathlib import Path

from pydantic import BaseModel, BaseSettings, Field

THIS_DIR = Path(__file__).parent


# class LansweeperSettings(BaseSettings):
#     BASE_URL: str = Field(default=None, env="BASE_URL")
#     API_KEY: str = Field(default=None, env="API_KEY")

#     class Config:
#         env_file = f"{THIS_DIR}/env_files/.env"


class LoggingSettings(BaseSettings):
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = f"{THIS_DIR}/env_files/logging.env"


class AppSettings(BaseSettings):
    APP_TITLE: str = Field(default="Default FastAPI App Title", env="APP_TITLE")
    APP_DESCRIPTION: str = Field(
        default="Default FastAPI app description", env="APP_DESCRIPTION"
    )
    APP_VERSION: str = Field(default="0.0.1", env="APP_VERSION")

    class Config:
        env_file = f"{THIS_DIR}/env_files/.env"


logging_settings = LoggingSettings()
app_settings = AppSettings()
