import os
import sys

from pyramid.paster import (
    get_app,
    setup_logging
)

from winterthur.env import Env, load_dotenv_vars


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s {staging|production}.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=None):
    import cherrypy

    if not argv:
        argv = sys.argv

    if len(argv) < 2:
        usage(argv)

    load_dotenv_vars()

    config = argv[1]
    wsgi_app = get_app(config)
    setup_logging(config)

    cherrypy.tree.graft(wsgi_app, '/')
    cherrypy.server.unsubscribe()

    env = Env()
    server = cherrypy._cpserver.Server()  # pylint: disable=protected-access
    server.socket_host = env.host
    server.socket_port = env.port
    server.thread_pool = 30
    server.subscribe()

    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    sys.exit(main() or 0)
