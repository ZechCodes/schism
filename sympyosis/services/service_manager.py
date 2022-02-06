from bevy import AutoInject, detect_dependencies
from bevy.builder import Builder
from sympyosis.config import Config
from sympyosis.logger import Logger
from sympyosis.services import Service
from sympyosis.services.interface_provider import InterfaceProviderProtocol


@detect_dependencies
class ServiceManager(AutoInject):
    config: Config
    log: Logger
    service_builder: Builder[Service]

    def __init__(self):
        self._services: dict[str, InterfaceProviderProtocol] = {}

    async def start(self):
        for config in self.config.services.values():
            service = self.service_builder(config)
            self.log.info(f"Creating {service.name!r} service")
            self._services[service.name] = service.create_interface()
