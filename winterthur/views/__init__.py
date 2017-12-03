def tpl(filename):
    return 'winterthur:templates/{0:s}.mako'.format(filename)


def no_cache(_req, res):
    """Sets no-cache using cache_control."""
    res.pragma = 'no-cache'
    res.expires = '0'
    res.cache_control = 'no-cache,no-store,must-revalidate'


def includeme(config):
    """Initializes the view for winterthur.

    Activate this setup using ``config.include('winterthur.views')``.
    """
    config.include('.result')
