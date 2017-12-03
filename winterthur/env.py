import os

from pyramid.decorator import reify


def load_dotenv_vars(dotenv_file=None):
    # loads .env
    if dotenv_file is None:
        dotenv_file = os.path.join(os.getcwd(), '.env')
    if os.path.isfile(dotenv_file):
        print('loading environment variables from .env')
        from dotenv import load_dotenv
        load_dotenv(dotenv_file)

    # update vars using prefix such as {TEST_|DEVELOPMENT_|PRODUCTION_}
    for _, v in Env.settings_mappings().items():
        prefix = '{}_'.format(Env.env_name().upper())
        env_v = os.environ.get(prefix + v, None)
        if env_v is not None:
            os.environ[v] = env_v


class Env():
    VALUES = ('development', 'test', 'production')

    def __init__(self):
        self._value = self.__class__.env_name()

    @classmethod
    def env_name(cls):
        v = str(os.environ.get('ENV', None))
        return v if v in cls.VALUES else 'production'

    @classmethod
    def settings_mappings(cls):
        return {
            # Note: these values are updated if exist but not empty
            'wsgi.url_scheme': 'WSGI_URL_SCHEME',
            'response_prefix': 'RESPONSE_PREFIX',
            'database.url': 'DATABASE_URL',
            'aws.access_key_id': 'AWS_ACCESS_KEY_ID',
            'aws.secret_access_key': 'AWS_SECRET_ACCESS_KEY',
            'dynamodb.endpoint_url': 'DYNAMODB_ENDPOINT_URL',
            'dynamodb.region_name': 'DYNAMODB_REGION_NAME',
            'dynamodb.table_name': 'DYNAMODB_TABLE_NAME',
        }

    def get(self, key, default=None):  # pylint: disable=no-self-use
        return os.environ.get(key, default)

    def set(self, key, value):  # pylint: disable=no-self-use
        os.environ[key] = value

    @reify
    def host(self):
        # TODO
        # get host and port from server section in ini as fallback
        return str(self.get('HOST', '127.0.0.1'))

    @reify
    def port(self):
        return int(self.get('PORT', 5000))

    @reify
    def value(self):
        return self._value

    @reify
    def is_test(self):
        return self._value == 'test'

    @reify
    def is_production(self):
        return self._value == 'production'
