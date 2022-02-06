from enum import IntEnum
from typing import Type, TypeVar
import logging


T = TypeVar("T")


class LogLevel(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def get(cls: Type[T], name: str) -> T:
        return getattr(cls, name.upper())


class Logger:
    def __init__(
        self, name: str, level: LogLevel, *, parent: logging.Logger | None = None
    ):
        self._name = name
        self._level = level

        self._parent = parent
        if parent:
            self._logger = self._parent.getChild(self._name)
        else:
            self._logger = logging.getLogger(name)

        self.set_level(self._level)

    def log(self, message: str, level: LogLevel, *args, **kwargs):
        self._logger.log(level, message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs):
        self.log(message, LogLevel.DEBUG, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        self.log(message, LogLevel.INFO, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self.log(message, LogLevel.WARNING, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self.log(message, LogLevel.ERROR, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        self.log(message, LogLevel.CRITICAL, *args, **kwargs)

    def set_level(self, level: LogLevel):
        self._level = level
        self._logger.setLevel(level)

    def create_child_logger(self, name: str, level: LogLevel | None = None):
        return Logger(name, self._level, parent=level or self._logger)

    @staticmethod
    def initialize_loggers(level: LogLevel = LogLevel.ERROR):
        logging.basicConfig(level=level)
