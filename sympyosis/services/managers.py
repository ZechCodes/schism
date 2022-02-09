from sympyosis.exceptions import BaseSympyosisException
from typing import Protocol


class SympyosisUnableToFindStartCoroutine(BaseSympyosisException):
    """Raised when Sympyosis cannot find the start coroutine on a service's interface."""


class ServiceManager(Protocol):
    async def start(self):
        ...
