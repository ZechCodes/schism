from bevy import AutoInject, detect_dependencies
from collections.abc import Mapping
from contextlib import contextmanager
from io import TextIOBase
from pathlib import Path
from sympyosis.exceptions import BaseSympyosisException
from sympyosis.options import Options
from typing import Any, Generator, Iterator
import json


class SympyosisConfigFileNotFound(BaseSympyosisException):
    """This exception is raised when the Sympyosis config manager cannot find the config file."""


class ServiceConfig(Mapping):
    def __init__(self, config_data: dict[str, Any]):
        self._config_data = config_data

    def __contains__(self, item: str) -> bool:
        return item in self._config_data

    def __getitem__(self, item: str) -> Any:
        return self._config_data[item]

    def __iter__(self) -> Iterator[Any]:
        return iter(self._config_data)

    def __len__(self) -> int:
        return len(self._config_data)

    def __repr__(self):
        return f"{type(self).__name__}({self._config_data})"


@detect_dependencies
class Config(AutoInject, Mapping):
    options: Options

    sympyosis_path_key = "SYMPYOSIS_PATH"
    sympyosis_config_file_name_key = "SYMPYOSIS_CONFIG_FILE_NAME"
    sympyosis_default_config_file_name = "sympyosis.config.json"
    sympyosis_service_config_section_key = "services"
    sympyosis_service_name_key = "name"

    def __init__(self, config_file_name: str | None = None):
        self._file_name = config_file_name or self.options.get(
            self.sympyosis_config_file_name_key, self.sympyosis_default_config_file_name
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
        file_path = Path(self.options[self.sympyosis_path_key]) / self._file_name
        if not file_path.exists():
            raise SympyosisConfigFileNotFound(
                f"Could not find the Sympyosis config file. Checked the {self.sympyosis_path_key} "
                f"({self.options[self.sympyosis_path_key]}) for {self._file_name!r}. Make sure that the "
                f"{self.sympyosis_path_key} and {self.sympyosis_config_file_name_key} environment variables are "
                f"correct. When not set the path will use the current working directory and the filename will default "
                f"to {self.sympyosis_default_config_file_name!r}."
            )

        with file_path.open("r") as file:
            yield file
