"""View action module for result read event
"""
import json

from pyramid.response import Response
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from scythia.views import no_cache
from scythia.models import ReadingResult
from scythia.services import ICollator
from scythia.env import Env


@view_config(route_name='result_read_event',
             renderer='json',
             request_method='GET')
def result_read_event(req):
    """Returns data for reflector canvas.
    """
    from scythia import logger

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

    collator = req.find_service(iface=ICollator, name='session')
    site_id = collator.site_id
    if not site_id:
        raise exc.HTTPNotFound()

    logger.info('version_id -> %s, project_id -> %s, site_id -> %s, '
                'api_key -> %s, context -> read',
                version_id, project_id, site_id, api_key)

    req.add_response_callback(no_cache)

    result = ReadingResult.fetch_paragraph_median_by(
        project_id=project_id, site_id=site_id)

    prefix = env.get('RESPONSE_PREFIX', '')
    res = Response(prefix + json.dumps(dict(result)), status='200 OK')
    res.content_type = 'application/json'
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['X-Content-Type-Options'] = 'nosniff'
    return res
