import pytest

from winterthur.env import Env


@pytest.fixture(autouse=True)
def setup(config):  # pylint: disable=unused-argument
    pass


def test_env_name_test(mocker):
    import os
    mocker.patch.object(os, 'environ')
    os.environ = {'ENV': 'test'}
    assert 'test' == Env.env_name()


def test_env_name_unknown_value(mocker):
    import os
    mocker.patch.object(os, 'environ')
    os.environ = {'ENV': 'unknown'}
    assert 'production' == Env.env_name()


def test_settings_mappings():
    result = Env.settings_mappings()
    assert dict == type(result)
    assert ('wsgi.url_scheme', 'WSGI_URL_SCHEME') in result.items()


def test_env_value_via_is_test():
    env = Env()
    assert env.is_test
    assert not env.is_production


def test_env_value_via_is_production(mocker):
    import os
    mocker.patch.object(os, 'environ')
    os.environ = {'ENV': 'production'}
    env = Env()
    assert not env.is_test
    assert env.is_production
