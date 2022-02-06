from typing import Protocol


class InterfaceProviderProtocol(Protocol):
    """Protocol that all interface providers need to implement."""

    async def start(self):
        ...
