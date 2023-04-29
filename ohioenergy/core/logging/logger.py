import logging
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Union

from pydantic import BaseModel, BaseSettings, Field, ValidationError, validator

THIS_DIR = Path(__file__).parent

default_log_file = "logs/app.log"
valid_levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]

default_fmt = "[%(levelname)s][%(asctime)s][%(name)s]: %(message)s"
default_extended_fmt = "[%(asctime)s]:[%(levelname)s]:[%(name)s] -> [%(funcName)s()]:[Line-%(lineno)d]> %(message)s"
default_file_fmt = "[%(asctime)s]:[%(levelname)s]:[%(name)s]:Proc:%(process)d]:[Line-%(lineno)d]> %(message)s"
default_date_fmt = "%Y-%m-%d_%H:%M:%S"


def ensure_log_file(log_file: str = default_log_file):
    if not Path(log_file).parent.exists():
        try:
            Path(log_file).parent.mkdir(exist_ok=True, parents=True)

            return True
        except Exception as exc:
            print(
                Exception(
                    f"Unhandled exception staging log file: {log_file}. Exception details: {exc}"
                )
            )
            return False

    else:
        return True


class LoggerConfig(BaseModel):
    format: str = Field(default=default_fmt)
    datefmt: str = Field(default=default_date_fmt)
    level: str = Field(default="INFO")

    @validator("level")
    def valid_level(cls, v) -> str:
        if v.upper() not in valid_levels:
            raise ValidationError(
                f"Invalid logging level: {v}. Must be one of {valid_levels}"
            )

        return v.upper()


default_log_config = LoggerConfig()


class BaseLogger(BaseSettings):
    name: str = __name__
    log_config: LoggerConfig = default_log_config
    formatter: logging.Formatter = Field(
        default=logging.Formatter(fmt=default_fmt, datefmt=default_date_fmt)
    )


default_logger = BaseLogger()


class ConsoleLogger(BaseLogger):
    pass


class FileLogger(BaseLogger):
    log_file: str = Field(default=default_log_file)
    formatter: logging.Formatter = Field(
        default=logging.Formatter(fmt=default_file_fmt, datefmt=default_date_fmt)
    )
    rotate_when: str = Field(default="midnight")
    max_bytes: int = 100 * 1024
    backup_count: int = 3


def get_console_handler():
    console_config = ConsoleLogger()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_config.formatter)

    return console_handler


def get_file_handler():
    file_config = FileLogger(log_file=default_log_file)

    ## If using TimedRotatingFileHandler, replace maxBytes & backupCount with: when=file_config.ROTATE_WHEN,
    file_handler = RotatingFileHandler(
        file_config.log_file,
        maxBytes=file_config.max_bytes,
        backupCount=file_config.backup_count,
    )
    file_handler.setFormatter(file_config.formatter)

    return file_handler


def get_logger(logger_name, level="INFO"):
    ensure_log_file()

    logger = logging.getLogger(logger_name)
    logger.setLevel(level.upper())
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())

    ## Propagate error up to parent
    logger.propagate = False

    return logger
