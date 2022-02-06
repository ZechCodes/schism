from bevy import AutoInject, Context, detect_dependencies
from sympyosis.app.args import get_arg_parser
from sympyosis.config import Config
from sympyosis.logger import Logger, LogLevel
from sympyosis.options import Options
from sympyosis.services import ServiceManager
import asyncio


@detect_dependencies
class App(AutoInject):
    config: Config
    service_manager: ServiceManager

    async def run(self):
        self.service_manager.start()

    @classmethod
    def launch(
        cls,
        cli_args: str | None = None,
        *,
        disable_arg_parse: bool = False,
        context: Context | None = None
    ):
        context = context or Context()

        args = {}
        if not disable_arg_parse:
            parser = get_arg_parser()
            args = parser.parse_args(cli_args.split() if cli_args else None).__dict__

        options = Options(**args)
        context.add(options)

        Logger.initialize_loggers()
        log_level = LogLevel.get(options.get("SYMPYOSIS_LOGGER_LEVEL", "ERROR"))
        logger = Logger(options.get("SYMPYOSIS_LOGGER_NAME", "Sympyosis"), log_level)
        context.add(logger)

        logger.info("Starting Sympyosis")
        app = context.bind(cls)()
        asyncio.run(app.run())
