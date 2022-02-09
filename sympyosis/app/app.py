from bevy import AutoInject, Context, detect_dependencies
from sympyosis.app.args import get_arg_parser
from sympyosis.config import Config
from sympyosis.logger import Logger, LogLevel
from sympyosis.options import Options
from sympyosis.services import ServiceManager
from typing import Any
import asyncio


@detect_dependencies
class App(AutoInject):
    config: Config
    log: Logger
    service_manager: ServiceManager

    def run(self):
        try:
            asyncio.run(self.service_manager.start())
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
        finally:
            self.log.debug("Sympyosis has shutdown")

    @classmethod
    def launch(
        cls,
        cli_args: str | None = None,
        *,
        disable_arg_parse: bool = False,
        context: Context | None = None
    ):
        context = context or Context()

        args = {} if disable_arg_parse else cls.get_cli_input(cli_args)
        options = Options(**args) >> context

        logger_name = (options.get(options.logger_name_option_name, "Sympyosis"),)
        logger_level = LogLevel.get(
            options.get(options.logger_level_option_name, "ERROR")
        )
        logger = logger(cls.create_logger(logger_name, logger_level)) >> context

        logger.info("Starting Sympyosis")
        app = cls @ context

        app.run()

    @staticmethod
    def get_cli_input(cli_args: str | None = None) -> dict[str, Any]:
        """Processes CLI input to create a dictionary of options that the app should use."""
        parser = get_arg_parser()
        input_args = cli_args.split() if cli_args else None
        return {
            key: dict(value) if key == "options" else value
            for key, value in parser.parse_args(input_args).__dict__.items()
        }

    @staticmethod
    def create_logger(name: str, level: LogLevel) -> Logger:
        Logger.initialize_loggers()
        logger = Logger(name, level)
