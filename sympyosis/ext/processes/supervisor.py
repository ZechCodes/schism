from bevy import AutoInject, detect_dependencies
from sympyosis.config import Config


@detect_dependencies
class SupervisorManager(AutoInject):
    config: Config

    @property
    def port_range(self) -> tuple[int, int]:
        return self.config.get("service_port_range", (8000, 8999))

    async def start(self):
        ...
