import logging
import os
from enum import StrEnum
from typing import Optional


class LogLevels(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Logger:
    LOG_FORMAT_DEBUG = "[%(asctime)s]: [%(levelname)s] [%(name)s] %(message)s"
    LOG_FORMAT_DEFAULT = "[%(levelname)s]: [%(name)s] %(message)s"

    _instance = None  # Singleton instance

    def __init__(self, log_level: Optional[LogLevels] = None):
        self.log_level = self._get_log_level(log_level)
        self._configure_logging()
        Logger._instance = self

    def _get_log_level(self, log_level: Optional[LogLevels]) -> LogLevels:
        if log_level is None:
            log_level = LogLevels(os.getenv("LOG_LEVEL", "INFO"))

        log_level_str = str(log_level).upper()
        if log_level_str not in LogLevels.__members__:
            return LogLevels.INFO

        return LogLevels(log_level_str)

    def _configure_logging(self):
        log_format = (
            self.LOG_FORMAT_DEBUG
            if self.log_level == LogLevels.DEBUG
            else self.LOG_FORMAT_DEFAULT
        )

        logging.basicConfig(
            level=str(self.log_level),
            format=log_format,
            force=True
        )

    @classmethod
    def configure(cls, log_level: Optional[LogLevels] = None) -> 'Logger':
        return cls(log_level)
