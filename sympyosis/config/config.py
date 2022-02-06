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

    sympyosis_default_config_file_name = "sympyosis.config.json"
    sympyosis_service_config_section_key = "services"
    sympyosis_service_name_key = "name"

    def __init__(self, config_file_name: str | None = None):
        self._file_name = config_file_name or self.options.get(
            self.options.sympyosis_config_file_name_envvar,
            self.sympyosis_default_config_file_name,
        )
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
                data[self.sympyosis_service_name_key]: ServiceConfig(data)
                for data in self.get(self.sympyosis_service_config_section_key, [])
            }

        return self._service_configs

    def _load_config(self):
        with self._get_config_file() as file:
            return json.load(file)

    @contextmanager
    def _get_config_file(self) -> Generator[None, TextIOBase, None]:
        file_path = (
            Path(self.options[self.options.sympyosis_path_envvar]) / self._file_name
        ).resolve()
        if not file_path.exists():
            self.log.critical(f"Could not find log file: {file_path}")
            raise SympyosisConfigFileNotFound(
                f"Could not find the Sympyosis config file.\n- Checked the {self.options.sympyosis_path_envvar} "
                f"({self.options[self.options.sympyosis_path_envvar]}) for a {self._file_name!r} file.\n\nMake sure "
                f"that the {self.options.sympyosis_path_envvar} and {self.options.sympyosis_config_file_name_envvar} "
                f"environment variables are correct. When not set the path will use the current working directory and "
                f"the filename will default to {self.sympyosis_default_config_file_name!r}."
            )

        self.log.info(f"Opening config file: {file_path}")
        with file_path.open("r") as file:
            yield file
