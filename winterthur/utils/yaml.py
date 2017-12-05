from __future__ import absolute_import, print_function
import os
from ast import literal_eval
from datetime import datetime, timedelta
from contextlib import contextmanager


def tag_datetime_utcnow_plus_timedelta(_loader, node):
    return datetime.utcnow() + timedelta(seconds=literal_eval(node.value))


@contextmanager
def yaml_loader(settings=None):
    # only for development and testing
    import yaml as orig_yaml

    def load_yaml(yml_file):
        data = {}
        if os.path.isfile(yml_file):
            with open(yml_file, 'r') as f:
                try:
                    data = orig_yaml.load(f)
                except orig_yaml.YAMLError as e:
                    print(e)
        return data

    # simple utility functions for tag in yaml
    if settings and isinstance(settings, dict):
        orig_yaml.add_constructor(
            '!datetime.utcnow+timedelta',
            tag_datetime_utcnow_plus_timedelta)

    yield load_yaml
