from __future__ import print_function
import os
import sys
from contextlib import contextmanager

from pyramid.paster import get_appsettings, setup_logging
from pyramid.scripts.common import parse_vars

from winterthur import resolve_env_vars
from winterthur.env import load_dotenv_vars
from winterthur.models import ReadingResult
from winterthur.utils import yaml_loader


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <command> <action> [var=value]\n'
          '(example: "%s \'development.ini#\' db seed")' % (cmd, cmd))
    sys.exit(1)


class DbCli(object):
    def __init__(self, settings):
        self.settings = settings

        # for migrate router
        self.migrate_table = 'migrations'
        self.migrate_dir = os.path.join(os.getcwd(), 'db', 'migrations')

    @contextmanager
    def _raw_db(self):
        from copy import copy
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        with self._db() as db:
            datname = copy(db.database)
            db.database = 'template1'
            conn = db.get_conn()
            conn.set_isolation_level(
                ISOLATION_LEVEL_AUTOCOMMIT
            )
            yield (db, datname)

    @contextmanager
    def _db(self):
        from winterthur.models import db, init_db

        init_db(self.settings)

        yield db

    def help(self):  # pylint: disable=no-self-use
        print('usage: db {help|init|seed|drop} [var=value]')
        sys.exit(1)

    def init(self):
        with self._raw_db() as (db, datname):
            q = "SELECT 1 FROM pg_database WHERE datname='{}'".format(datname)
            if db.execute_sql(q).rowcount != 0:
                sys.exit(0)

            q = "CREATE DATABASE {0} ENCODING '{1}' TEMPLATE {2}".format(
                datname,
                'UTF-8',
                'template0'
            )
            db.execute_sql(q)

    def migrate(self):
        from peewee_migrate import Router

        with self._db() as db, db.atomic():
            router = Router(db, migrate_table=self.migrate_table,
                            migrate_dir=self.migrate_dir)
            router.run()

    def rollback(self):
        from peewee_migrate import Router

        with self._db() as db, db.atomic():
            router = Router(db, migrate_table=self.migrate_table,
                            migrate_dir=self.migrate_dir)
            if router.done:
                router.rollback(router.done[-1])

    def seed(self):
        with self._db() as db, db.atomic():
            with yaml_loader(self.settings) as loader:
                # db/seeds/*.yml
                # TODO: import all files in db/seeds/*.yml
                # `order` sensitive
                models = [
                    ReadingResult,
                ]

                for klass in models:
                    # pylint: disable=no-member,protected-access
                    table = klass._meta.db_table
                    seed_yml = os.path.join(os.getcwd(), 'db', 'seeds',
                                            '{}.yml'.format(table))
                    if os.path.isfile(seed_yml):
                        data = loader(seed_yml)
                        for attributes in data[table]:
                            obj = klass(**attributes)
                            obj.save()

    def drop(self):
        with self._raw_db() as (db, datname):
            q = "SELECT 1 FROM pg_database WHERE datname='{}'".format(datname)
            if db.execute_sql(q).rowcount == 0:
                sys.exit(0)

            q = 'DROP DATABASE {0}'.format(datname)
            db.execute_sql(q)


def main():
    argv = sys.argv
    if len(argv) < 4:
        usage(argv)
    config_uri = argv[1]
    command = argv[2]
    action = argv[3]
    options = parse_vars(argv[4:])

    setup_logging(config_uri)
    load_dotenv_vars()

    # TODO: parse command and actions
    if command not in ('db',):
        raise Exception('Run with valid command {db} :\'(')

    shared_actions = ('help', 'init', 'drop')
    err_msg = 'Run with valid action {0!s} :\'('
    if command == 'db':
        db_actions = shared_actions + ('migrate', 'rollback', 'seed')
        if action not in db_actions:
            raise Exception(err_msg.format('|'.join(db_actions)))

    settings = get_appsettings(config_uri, options=options)
    settings = resolve_env_vars(dict(settings))

    cli = '{0}{1}'.format(command.capitalize(), 'Cli')
    c = globals()[cli](settings)
    getattr(c, action.lower())()
