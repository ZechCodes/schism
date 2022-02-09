from bevy import AutoInject, detect_dependencies
from collections.abc import Mapping
from contextlib import contextmanager
from io import TextIOBase
from pathlib import Path
from sympyosis.config.service import ServiceConfig
from sympyosis.logger import Logger
from sympyosis.exceptions import BaseSympyosisException
from sympyosis.options import Options
from typing import Any, Generator, Iterator
import json


class SympyosisConfigFileNotFound(BaseSympyosisException):
    """This exception is raised when the Sympyosis config manager cannot find the config file."""


@detect_dependencies
class Config(AutoInject, Mapping):
    log: Logger
    options: Options

    default_config_file_name = "sympyosis.config.json"
    service_config_section_key = "services"
    service_name_key = "name"

    def __init__(self, config_file: str | None = None):
        self._file_path = self._create_config_file_path(config_file)
        self._config = self._load_config()
        self._service_configs: dict[str, ServiceConfig] = {}

    def __contains__(self, item: str) -> bool:
        return item in self._config

    def __getitem__(self, item: str) -> Any:
        return self._config[item]

    def __iter__(self) -> Iterator[Any]:
        return iter(self._config)

    def __len__(self) -> int:
        return len(self._config)

    @property
    def services(self) -> dict[str, ServiceConfig]:
        if not self._service_configs:
            self._service_configs = {
                data[self.service_name_key]: ServiceConfig(data)
                for data in self.get(self.service_config_section_key, [])
            }

        return self._service_configs

    def _create_config_file_path(self, config_file: str | None) -> Path:
        if config_file:
            return Path(config_file).resolve()

        if config_file := self.options.get(self.options.config_file_option_name):
            return Path(config_file).resolve()

        path = Path(self.options[self.options.path_option_name])
        return path / self.default_config_file_name

    def _load_config(self):
        with self._get_config_file() as file:
            return json.load(file)

    @contextmanager
    def _get_config_file(self) -> Generator[None, TextIOBase, None]:
        if not self._file_path.exists():
            self.log.critical(f"Could not find log file: {self._file_path}")
            raise SympyosisConfigFileNotFound(
                f"Could not find the Sympyosis config file.\n- Attempted to load {self._file_path!r}.\n\nMake sure "
                f"that the {self.options.path_option_name} and {self.options.config_file_option_name} environment "
                f"variables are correct. When not set the path will use the current working directory and the filename "
                f"will default to {self.default_config_file_name!r}."
            )

        self.log.info(f"Opening config file: {self._file_path}")
        with self._file_path.open("r") as file:
            yield file
