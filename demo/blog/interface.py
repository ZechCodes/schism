from bevy import AutoInject, detect_dependencies
from sympyosis import Logger
from demo.admin.interface import AdminAPI
import asyncio


@detect_dependencies
class BlogAPI(AutoInject):
    admin: AdminAPI
    log: Logger

    async def start(self):
        self.log.info("Blog API has started!")
        while True:
            await asyncio.sleep(5)
            self.log.info(f"Blog still running {self.admin.say_hi()}")
