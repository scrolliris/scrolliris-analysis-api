from pyramid.response import Response
from pyramid.view import (
    forbidden_view_config,
    notfound_view_config,
    view_config,
)
import pyramid.httpexceptions as exc

from winterthur.views import tpl


@notfound_view_config(accept='text/html', renderer=tpl('404'),
                      append_slash=exc.HTTPMovedPermanently)
def notfound_html(req):
    req.response.status = 404
    return dict()


@notfound_view_config(accept='application/json', renderer='json',
                      append_slash=exc.HTTPMovedPermanently)
def notfound_json(req):
    req.response.status = 404
    return dict()


@forbidden_view_config(accept='text/html', renderer=tpl('403'))
def forbidden_html(req):
    req.response.status = 403
    return dict()


@forbidden_view_config(accept='application/json', renderer='json')
def forbidden_json(req):
    req.response.status = 403
    return dict()


@view_config(accept='text/html', context=exc.HTTPInternalServerError,
             renderer='string')
def internal_server_error_html(req):
    body = 'Cannot {} {}'.format(req.method, req.path)
    return Response(body, status='500 Internal Server Error')


@view_config(accept='application/json', context=exc.HTTPInternalServerError,
             renderer='json')
def internal_server_error_json(req):
    req.response.status = 500
    return dict()
