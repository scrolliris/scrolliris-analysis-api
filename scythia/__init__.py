"""Scythi aApplication.
"""
import json
import logging
from os import path
import sys
from wsgiref.handlers import BaseHandler

from paste.translogger import TransLogger
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.threadlocal import get_current_registry
from pyramid.view import forbidden_view_config, notfound_view_config
import pyramid.httpexceptions as exc

from .services import ICollator
from .env import Env

# -- configurations

STATIC_DIR = path.join(path.dirname(path.abspath(__file__)), '../static')


# pylint: disable=protected-access
def ignore_broken_pipes(self):
    """Ignores unused error message about broken pipe.
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
    """Returns settings from current ini.
    """
    return get_current_registry().settings


def resolve_env_vars(settings):
    """Loads environment variables into settings
    """
    env = Env()
    s = settings.copy()
    for k, v in env.settings_mappings.items():
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


def tpl(filename):
    """HTML Template Utility.
    """
    return './templates/{0:s}.mako'.format(filename)


def no_cache(_request, response):
    """Sets no-cache using cache_control
    """
    response.pragma = 'no-cache'
    response.expires = '0'
    response.cache_control = 'no-cache,no-store,must-revalidate'


# -- views


@notfound_view_config(accept='text/html', renderer=tpl('404'),
                      append_slash=exc.HTTPMovedPermanently)
def notfound_html(req):
    """404 Not Found Error.
    """
    req.response.status = 404
    return dict()


@notfound_view_config(accept='application/json', renderer='json',
                      append_slash=exc.HTTPMovedPermanently)
def notfound_json(req):
    """404 Not Found Error in JSON.
    """
    req.response.status = 404
    return dict()


@forbidden_view_config(accept='text/html', renderer=tpl('403'))
def forbidden_html(req):
    """403 Forbidden Error in HTML.
    """
    req.response.status = 403
    return dict()


@forbidden_view_config(accept='application/json', renderer='json')
def forbidden_json(req):
    """403 Forbidden Error in JSON.
    """
    req.response.status = 403
    return dict()


@view_config(accept='text/html', context=exc.HTTPInternalServerError,
             renderer='string')
def internal_server_error_html(req):
    """Internal Server Error in HTML.
    """
    body = 'Cannot {} {}'.format(req.method, req.path)
    return Response(body, status='500 Internal Server Error')


@view_config(accept='application/json', context=exc.HTTPInternalServerError,
             renderer='json')
def internal_server_error_json(req):
    """Internal Server Error in JSON.
    """
    req.response.status = 500
    return dict()


@view_config(route_name='result_read_event',
             renderer='json',
             request_method='GET')
def result_read_event(req):
    """Returns data for reflector canvas.
    """
    # FIXME: use decorator
    if 'api_key' not in req.params:
        raise exc.HTTPForbidden()

    # FIXME: use decorator
    if str(req.accept).lower() != 'application/json':
        raise exc.HTTPForbidden()

    env = Env()

    version_id = req.matchdict['version_id']
    project_id = req.matchdict['project_id']
    api_key = req.params['api_key']

    req.add_response_callback(no_cache)

    # FIXME: fetch result
    prefix = env.get('RESPONSE_PREFIX', '')
    res = Response(prefix + json.dumps(dict([('p', [])])), status='200 OK')
    res.content_type = 'application/json'
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['X-Content-Type-Options'] = 'nosniff'
    return res


# -- main

def main(_, **settings):
    """The main function.
    """
    from .request import CustomRequest

    env = Env()

    config = Configurator(settings=resolve_env_vars(settings))
    config.set_request_factory(CustomRequest)

    # routes
    # static files at /*
    filenames = [f for f in ('robots.txt', 'humans.txt')
                 if path.isfile((STATIC_DIR + '/{}').format(f))]
    if filenames:
        cache_max_age = 3600 if env.is_production else 0
        config.add_asset_views(
            STATIC_DIR, filenames=filenames, http_cache=cache_max_age)

    def session_predicator(inf, req):
        """Validates `project_id` and `api_key` using SesionCollator.
        """
        route_name = inf['route'].name
        if route_name in ('result_read_event',):
            if 'api_key' not in req.params or \
               'X-CSRF-Token' not in req.headers:
                raise exc.HTTPForbidden()

            project_id = inf['match']['project_id']
            api_key = req.params['api_key']
            token = req.headers['X-CSRF-Token']

            logger.info('project_id -> %s, api_key -> %s, token -> %s, '
                        'context -> read', project_id, api_key, token)

            collator = req.find_service(iface=ICollator, name='session')
            if not collator.collate(project_id=project_id, api_key=api_key,
                                    token=token, context='read'):
                logger.error('invalid session token')
                raise exc.HTTPNotAcceptable()

            return True

        return False

    def version_predicator(info, _req):
        """Validates `version_id` parameter.
        """
        if info['route'].name in ('result_read_event',):
            return info['match']['version_id'] in ('1.0',)

    config.add_route(
        'result_read_event',
        '/v{version_id}/projects/{project_id}/results/read',
        custom_predicates=(version_predicator, session_predicator,)
    )

    config.scan()
    config.include('.services')

    app = config.make_wsgi_app()
    app = TransLogger(app, setup_console_handler=False)
    return app
