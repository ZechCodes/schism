from typing import Any
import os


class Options:
    """The options object aggregates all options values that the Sympyosis application pulls in from the environment."""

    sympyosis_envvar_prefix = "SYMPYOSIS"
    sympyosis_path_envvar = f"{sympyosis_envvar_prefix}_PATH"
    sympyosis_config_file_name_envvar = f"{sympyosis_envvar_prefix}_CONFIG_FILE_NAME"
    sympyosis_logger_level_envvar = f"{sympyosis_envvar_prefix}_LOGGER_LEVEL"
    sympyosis_logger_name_envvar = f"{sympyosis_envvar_prefix}_LOGGER_NAME"

    def __init__(self, **options):
        self._options = self._build_options(options)

    def __getitem__(self, item: str) -> Any:
        return self._options[item]

    def __contains__(self, item: str) -> bool:
        return item in self._options

    def get(self, item: str, default: Any | None = None) -> Any | None:
        return self._options.get(item, default)

    def _build_options(self, options: dict[str, Any]) -> dict[str, Any]:
        return (
            {self.sympyosis_path_envvar: self._get_path()}
            | self._load_env()
            | self._map_options(options)
        )

    def _get_path(self):
        return os.getcwd()

    def _load_env(self) -> dict[str, Any]:
        return {
            key: value
            for key, value in os.environ.items()
            if key.startswith(self.sympyosis_envvar_prefix)
        }

    def _map_options(self, options: dict[str, Any]) -> dict[str, Any]:
        mapping = {
            "path": self.sympyosis_path_envvar,
            "config": self.sympyosis_config_file_name_envvar,
            "log_level": self.sympyosis_logger_level_envvar,
            "logger_name": self.sympyosis_logger_name_envvar,
        }
        return {
            mapping.get(key, key): value
            for key, value in options.items()
            if value is not None
        }
