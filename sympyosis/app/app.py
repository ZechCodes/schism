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
        self.log.info("Sympyosis is starting")
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
        context: Context | None = None,
    ):
        args = {} if disable_arg_parse else cls.get_cli_input(cli_args)
        options = Options(**args)

        context = Context.new(context) << options << cls.create_logger(options)
        (cls @ context).run()

    @staticmethod
    def get_cli_input(cli_args: str | None = None) -> dict[str, Any]:
        """Processes CLI input to create a dictionary of options that the app should use."""
        parser = get_arg_parser()
        input_args = cli_args.split() if cli_args else None
        args = parser.parse_args(input_args).__dict__
        return args | dict(args.pop("option"))

    @staticmethod
    def create_logger(options: Options) -> Logger:
        """Creates an logger logger using the options passed into the application."""
        name = options.get(options.logger_name_option_name, "Sympyosis")
        level = LogLevel.get(options.get(options.logger_level_option_name, "ERROR"))

        Logger.initialize_loggers()
        return Logger(name, level)
