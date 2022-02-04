from typing import Any
import os


class Options:
    """The options object aggregates all options values that the Sympyosis application pulls in from the environment."""

    sympyosis_envvar_prefix = "SYMPYOSIS"
    sympyosis_path_envvar = f"{sympyosis_envvar_prefix}_PATH"
    sympyosis_config_file_name_envvar = f"{sympyosis_envvar_prefix}_CONFIG_FILE_NAME"

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
            {self.sympyosis_path_envvar: self._get_path()} | self._load_env() | options
        )

    def _get_path(self):
        return os.getcwd()

    def _load_env(self) -> dict[str, Any]:
        return {
            key: value
            for key, value in os.environ.items()
            if key.startswith(self.sympyosis_envvar_prefix)
        }
