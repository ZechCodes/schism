from __future__ import annotations
from bevy import AutoInject, detect_dependencies
from sympyosis.config import ServiceConfig
from sympyosis.logger import Logger
from sympyosis.exceptions import BaseSympyosisException
from sympyosis.services.interface_provider import InterfaceProviderProtocol
from importlib import import_module
from typing import Type
from types import ModuleType


class SympyosisUnableToImportService(BaseSympyosisException):
    """This exception is raised when attempting to import a service package."""


class SympyosisUnableToFindServiceInterface(BaseSympyosisException):
    """This exception is raised when attempting to get the service interface from the service package."""


class SympyosisMissingInterfaceConfig(BaseSympyosisException):
    """This exception is raised when no interface config is set for a service."""


@detect_dependencies
class Service(AutoInject):
    log: Logger

    def __init__(self, config: ServiceConfig):
        self._config = config
        self._interface = None

    @property
    def name(self) -> str:
        return self._config["name"]

    @property
    def interface(self) -> Type[InterfaceProviderProtocol]:
        """This will be class that the service wants made public."""
        if not self._interface:
            self._interface = self._get_service_interface()

        return self._interface

    def create_interface(self) -> InterfaceProviderProtocol:
        self.log.debug(f"Creating service interface for {self.name!r}")
        service_context = self.__bevy_context__.branch()
        service_context.add(self._config)
        service_context.add(
            self.log.create_child_logger(self.name, self._config.get("log_level", None))
        )
        interface = service_context.bind(self.interface)()
        self.__bevy_context__.add(interface)
        return interface

    def _import_service_interface_module(self, dot_path: str) -> ModuleType:
        package, *_ = dot_path.rpartition(".")
        try:
            return import_module(dot_path, package)
        except ImportError:
            self.log.error(
                f"Could not import {self.name!r} service's interface. Attempted to import the module {dot_path!r} from "
                f"the {package!r} package."
            )
            raise SympyosisUnableToImportService(
                f"Failed to import the {dot_path} service. Make sure it is on the Python path and that the interface "
                f"import dot path in the Sympyosis config is correct."
            )

    def _get_service_interface(self) -> Type[InterfaceProviderProtocol]:
        try:
            dot_path, interface = self._config["interface"].split(":")
        except KeyError:
            raise SympyosisMissingInterfaceConfig(
                f"No interface was set for the {self._config['name']!r} service in your Sympyosis config file.\n\nYou "
                f"must have an 'interface' entry for every service in the config. The value should be a valid import "
                f'path followed by the class name that should be used as the interface.\n\nExample: "interface": '
                f'"example.package.module:ExampleServiceInterface"'
            )

        module = self._import_service_interface_module(dot_path)
        self.log.debug(
            f"Imported {self.name!r} service's interface module at {dot_path!r}."
        )
        try:
            return getattr(module, interface)
        except AttributeError:
            self.log.error(
                f"Failed to get the {self.name!r} service's interface {interface!r} from {dot_path!r}."
            )
            raise SympyosisUnableToFindServiceInterface(
                f"Failed to get the service interface {interface!r} from {dot_path}. Make sure that the interface "
                f"class name in the Sympyosis config is correct."
            )
