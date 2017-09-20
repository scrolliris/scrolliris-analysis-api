"""Scythia application package
"""
import logging
import sys
from wsgiref.handlers import BaseHandler

from paste.translogger import TransLogger
from pyramid.config import Configurator
from pyramid.threadlocal import get_current_registry

from scythia.env import Env

# -- configurations


# pylint: disable=protected-access
def ignore_broken_pipes(self):
    """Ignores unused error message about broken pipe
    """
    if sys.exc_info()[0] != BrokenPipeError:
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
    """Returns settings from current ini
    """
    return get_current_registry().settings


def resolve_env_vars(settings):
    """Loads environment variables into settings
    """
    env = Env()
    s = settings.copy()
    for k, v in env.settings_mappings.items(): # pylint: disable=no-member
        # ignores missing key or it has a already value in config
        if k not in s or s[k]:
            continue
        new_v = env.get(v, None)
        if not isinstance(new_v, str):
            continue
        # ignores empty string
        if ',' in new_v:
            s[k] = [nv for nv in new_v.split(',') if nv != '']
        elif new_v:
            s[k] = new_v
    return s


def main(_, **settings):
    """The server main function
    """
    from .request import CustomRequest

    config = Configurator(settings=resolve_env_vars(dict(settings)))
    config.set_request_factory(CustomRequest)

    config.scan()
    config.include('.services')
    config.include('.models')
    config.include('.views')

    config.include('.route')

    app = config.make_wsgi_app()
    app = TransLogger(app, setup_console_handler=False)
    return app
