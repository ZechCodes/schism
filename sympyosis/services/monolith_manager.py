from bevy import AutoInject, detect_dependencies
from bevy.builder import Builder
from sympyosis.config import Config
from sympyosis.services.managers import SympyosisUnableToFindStartCoroutine
from sympyosis.logger import Logger
from sympyosis.services import Service
from sympyosis.services.interface_provider import InterfaceProviderProtocol
from typing import Awaitable
import asyncio


@detect_dependencies
class MonolithManager(AutoInject):
    config: Config
    log: Logger
    service_builder: Builder[Service]

    def __init__(self):
        self._services: dict[str, InterfaceProviderProtocol] = {}

    async def start(self):
        self._create_services()
        await self._run_services()

    def _create_services(self):
        for config in self.config.services.values():
            service = self.service_builder(config)
            self.log.info(f"Creating {service.name!r} service")
            self._services[service.name] = service.create_interface()

    async def _run_services(self):
        funcs: list[Awaitable] = []
        for name, service in self._services.items():
            try:
                funcs.append(service.start())
            except AttributeError:
                self.log.error(
                    f"Could not find the start coroutine on the {name!r} service's provider "
                    f"{type(service).__qualname__!r}."
                )
                raise SympyosisUnableToFindStartCoroutine(
                    f"Could not find the start coroutine on the {name!r} service's provider "
                    f"{type(service).__qualname__!r}.\n\nBe sure that the service's interface module and interface "
                    f"class are correct in the Sympyosis config file. The services provider class must adhere to the "
                    f"interface protocol ({InterfaceProviderProtocol.__qualname__})."
                )
        await asyncio.gather(*funcs)
