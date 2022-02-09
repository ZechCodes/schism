from sympyosis.exceptions import BaseSympyosisException
from typing import Protocol, runtime_checkable


class SympyosisUnableToFindStartCoroutine(BaseSympyosisException):
    """Raised when Sympyosis cannot find the start coroutine on a service's interface."""


@runtime_checkable
class ServiceManager(Protocol):
    async def start(self):
        ...
