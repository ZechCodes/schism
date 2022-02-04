from collections.abc import Mapping
from typing import Any, Iterator


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
