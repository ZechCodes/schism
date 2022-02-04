from bevy import AutoInject, Context, detect_dependencies
from bevy.builder import Builder
from contextlib import contextmanager
from io import StringIO
from sympyosis.app.app import App
from sympyosis.config.config import Config, ServiceConfig
from sympyosis.services.service import Service
from sympyosis.services.service_manager import ServiceManager


class ConfigTester(Config):
    def __init__(self, config=None):
        self.data = (
            config
            or """
            {
                "services": [
                    {"name": "Service A", "interface": "A.service_a:ServiceA"},
                    {"name": "Service B", "interface": "B.service_b:ServiceB"}
                ]
            }
            """
        )
        super().__init__()

    @contextmanager
    def _get_config_file(self):
        yield StringIO(self.data)


class ModuleDummy:
    class ServiceA:
        ran = 0

        def __init__(self):
            self.ran += 1

    @detect_dependencies
    class ServiceB(AutoInject):
        config: ServiceConfig
        ran = 0

        def __init__(self):
            self.ran += 1

    @detect_dependencies
    class ServiceC(AutoInject):
        service_b: "ModuleDummy.ServiceB"
        config: ServiceConfig


@detect_dependencies
class ServiceTester(Service):
    def _import_service_interface_module(self, dot_path: str):
        return ModuleDummy


@detect_dependencies
class ServiceManager(ServiceManager):
    service_builder: Builder[ServiceTester]


def test_config_services():
    context = Context()
    context.add(context.bind(ConfigTester)())
    context.add(context.bind(ServiceManager)())
    App.launch(disable_arg_parse=True, context=context)

    a, b = context.get(ModuleDummy.ServiceA), context.get(ModuleDummy.ServiceB)
    assert a is a
    assert a is not b
    assert a.ran == 1
    assert b.ran == 1


def test_service_interdependency():
    context = Context()
    context.add(
        context.bind(ConfigTester)(
            """
            {
                "services": [
                    {"name": "Service B", "interface": "B.service_b:ServiceB"},
                    {"name": "Service C", "interface": "C.service_c:ServiceC"}
                ]
            }
            """
        )
    )
    context.add(context.bind(ServiceManager)())
    App.launch(disable_arg_parse=True, context=context)

    b, c = context.get(ModuleDummy.ServiceB), context.get(ModuleDummy.ServiceC)
    assert c.service_b is b
    assert c.__bevy_context__ is not context


def test_service_config():
    context = Context()
    context.add(
        context.bind(ConfigTester)(
            """
            {
                "services": [
                    {"name": "Service B", "interface": "B.service_b:ServiceB"},
                    {"name": "Service C", "interface": "C.service_c:ServiceC"}
                ]
            }
            """
        )
    )
    context.add(context.bind(ServiceManager)())
    App.launch(disable_arg_parse=True, context=context)

    b, c = context.get(ModuleDummy.ServiceB), context.get(ModuleDummy.ServiceC)
    assert b.config["name"] == "Service B"
    assert c.config["name"] == "Service C"
