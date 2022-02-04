from io import StringIO
from sympyosis.config.config import Config, ServiceConfig
from contextlib import contextmanager


class ConfigStub(Config):
    @contextmanager
    def _get_config_file(self):
        yield StringIO(
            """
            {
                "services": [
                    {"name": "Service A", "setting": "foobar"},
                    {"name": "Service B", "setting": "arfoo"}
                ]
            }
            """
        )


def test_config_services():
    config = ConfigStub()

    assert tuple(config.services) == ("Service A", "Service B")
    assert isinstance(config.services["Service A"], ServiceConfig)
