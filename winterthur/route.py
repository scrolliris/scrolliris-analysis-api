from os import path

import pyramid.httpexceptions as exc

from winterthur.env import Env
from winterthur.services import ICollator

STATIC_DIR = path.join(path.dirname(path.abspath(__file__)), '../static')


def session_predicator(inf, req):
    """Validates `project_id` and `api_key` using SesionCollator."""
    from . import logger

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
    """Validates `version_id` parameter."""
    if info['route'].name in ('result_read_event',):
        return info['match']['version_id'] in ('1.0',)


def includeme(config):
    env = Env()
    # routes
    # static files at /*
    filenames = [f for f in ('robots.txt', 'humans.txt')
                 if path.isfile((STATIC_DIR + '/{}').format(f))]
    if filenames:
        cache_max_age = 3600 if env.is_production else 0
        config.add_asset_views(
            STATIC_DIR, filenames=filenames, http_cache=cache_max_age)

    config.add_route(
        'result_read_event',
        '/v{version_id}/projects/{project_id}/results/read',
        custom_predicates=(version_predicator, session_predicator,)
    )
