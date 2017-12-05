from __future__ import absolute_import
import logging
import socket
import sys
import types
from wsgiref.handlers import BaseHandler

from pyramid.config import Configurator
from pyramid.threadlocal import get_current_registry

from winterthur.env import Env

# -- configurations


# pylint: disable=protected-access
def ignore_broken_pipes(self):
    """Ignores unused error message about broken pipe."""
    try:
        ex = BrokenPipeError
    except NameError:
        ex = socket.error
    if sys.exc_info()[0] != ex:
        BaseHandler.__handle_error_original_(self)


BaseHandler.__handle_error_original_ = BaseHandler.handle_error
BaseHandler.handle_error = ignore_broken_pipes
# pylint: enable=protected-access

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(sh)
# pylint: enable=invalid-name


def get_settings():
    return get_current_registry().settings


def get_expected_env_value_from(env, key, expected_type):
    """Get value(s) through environment variable."""
    value = env.get(key, None)
    if not isinstance(value, expected_type):
        return None
    # split, but ignore empty string
    if ',' in value:
        value = [v for v in value.split(',') if v != '']
    return value


def resolve_env_vars(settings):
    env = Env()
    s = settings.copy()

    string_type = str
    if sys.version_info[0] < 3:
        try:
            # `types.StringTypes` works also in Python2.7's unicode
            string_type = types.StringTypes
        except AttributeError:
            pass

    for k, k_upper in Env.settings_mappings().items():
        # ignores missing key or it has a already value in config
        if k not in s or s[k]:
            continue
        new_v = get_expected_env_value_from(env, k_upper, string_type)
        if new_v:
            s[k] = new_v
    return s


def main(_, **settings):
    from winterthur.request import CustomRequest

    config = Configurator(settings=resolve_env_vars(dict(settings)))
    config.set_request_factory(CustomRequest)

    config.scan()
    config.include('.services')
    config.include('.models')
    config.include('.views')

    config.include('.route')

    app = config.make_wsgi_app()
    # enable file logger [wsgi/access_log]
    # from paste.translogger import TransLogger
    # app = TransLogger(app, setup_console_handler=False)
    return app
