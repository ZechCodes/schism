from bevy import AutoInject, detect_dependencies
from bevy.builder import Builder
from sympyosis.config import Config
from sympyosis.logger import Logger
from sympyosis.services import Service


@detect_dependencies
class ServiceManager(AutoInject):
    config: Config
    log: Logger
    service_builder: Builder[Service]

    def start(self):
        self._start_services()

    def _start_services(self):
        for config in self.config.services.values():
            service = self.service_builder(config)
            self.log.info(f"Creating {service.name!r} service")
            service.create_interface()
