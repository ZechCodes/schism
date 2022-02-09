from bevy import AutoInject, detect_dependencies
from sympyosis.config import Config
from sympyosis.ext.processes.supervisor import SupervisorManager
from sympyosis.ext.processes.database import Database


@detect_dependencies
class SupervisorService(AutoInject):
    config: Config
    db: Database
    manager: SupervisorManager

    def __init__(self):
        self._port = self._find_port()

    @property
    def port(self):
        return self._port

    async def start(self):
        ...

    def _find_port(self):
        if port := self.config.get("supervisor_port", None):
            return port

        lowest, _ = self.manager.port_range
        return lowest
