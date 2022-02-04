from bevy import AutoInject, Context, detect_dependencies
from sympyosis.app.args import get_arg_parser
from sympyosis.config import Config
from sympyosis.options import Options
import asyncio


@detect_dependencies
class App(AutoInject):
    config: Config
    options: Options

    async def run(self):
        ...

    @classmethod
    def launch(cls, cli_args: str | None = None):
        context = Context()

        args = get_arg_parser().parse_args(cli_args.split() if cli_args else None)
        context.add(Options(**args.__dict__))

        app = context.bind(cls)()
        asyncio.run(app.run())
