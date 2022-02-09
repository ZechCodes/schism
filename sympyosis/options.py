from typing import Any
import os


class Options:
    """The options object aggregates all options values that the Sympyosis application pulls in from the environment."""

    envvar_prefix = "SYMPYOSIS"
    path_option_name = f"PATH"
    config_file_name_option_name = f"CONFIG_FILE_NAME"
    logger_level_option_name = f"LOGGER_LEVEL"
    logger_name_option_name = f"LOGGER_NAME"

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
            {self.path_option_name: self._get_path()}
            | self._load_env()
            | self._map_options(options)
        )

    def _get_path(self):
        return os.getcwd()

    def _load_env(self) -> dict[str, Any]:
        prefix = f"{self.envvar_prefix}_"
        return {
            key.removeprefix(prefix): value
            for key, value in os.environ.items()
            if key.startswith(prefix)
        }

    def _map_options(self, options: dict[str, Any]) -> dict[str, Any]:
        mapping = {
            "path": self.path_option_name,
            "config": self.config_file_name_option_name,
            "log_level": self.logger_level_option_name,
            "logger_name": self.logger_name_option_name,
        }
        return {
            mapping.get(key, key): value
            for key, value in options.items()
            if value is not None
        }
