# pylint: disable=inherit-non-class,no-self-argument,no-method-argument
from __future__ import absolute_import
import logging
import sys
from datetime import datetime, timedelta
try:
    from datetime import timezone
except ImportError:
    from time import timezone

import boto3
from boto3.dynamodb.conditions import Key, Attr
from zope.interface import Interface


class ICollator(Interface):
    # pylint: disable=missing-docstring

    def collate():
        pass


class ContextError(Exception):
    """Custom error class for session context."""

    def __init__(self, value):
        if sys.version_info[0] > 3:
            # pylint: disable=missing-super-argument
            super().__init__()
        else:
            super(ContextError, self).__init__()

        self.value = value

    def __str__(self):
        return repr(self.value)


class BaseDynamoDBServiceObject(object):
    # pylint: disable=too-few-public-methods
    def __init__(self, *_, **kwargs):
        session = boto3.session.Session(
            aws_access_key_id=kwargs['aws_access_key_id'],
            aws_secret_access_key=kwargs['aws_secret_access_key']
        )
        options = {
            'use_ssl': True,
            'region_name': kwargs['region_name']
        }
        if 'endpoint_url' in kwargs and kwargs['endpoint_url']:
            options['endpoint_url'] = kwargs['endpoint_url']
        self.db = session.resource('dynamodb', **options)
        self.table = self.db.Table(kwargs['table_name'])


class SessionCollator(BaseDynamoDBServiceObject):
    def __init__(self, *args, **kwargs):
        self.item = None
        if sys.version_info[0] > 3:
            # pylint: disable=missing-super-argument
            super().__init__(*args, **kwargs)
        else:
            super(SessionCollator, self).__init__(*args, **kwargs)

    @classmethod
    def options(cls, settings):
        _options = {
            'aws_access_key_id': settings['aws.access_key_id'],
            'aws_secret_access_key': settings['aws.secret_access_key'],
            'region_name': settings['dynamodb.region_name'],
            'table_name': settings['dynamodb.table_name'],
        }
        if settings['dynamodb.endpoint_url']:
            _options['endpoint_url'] = settings['dynamodb.endpoint_url']
        return _options

    @classmethod
    def generate_timestamp(cls, **kwargs):
        """Generates Unix Timestamp int using timedelta in UTC.

        NOTE:
          `datetime.utcnow().timestamp()` is invalid, because `timestamp()`
          method assumes that time object has local time.
        """
        return int((datetime.now(timezone.utc) -
                    timedelta(**kwargs)).timestamp())

    @property
    def site_id(self):
        """Return site_id after collation."""
        item = self.item
        if not isinstance(item, dict) or 'site_id' not in item:
            logger = logging.getLogger(__name__)
            logger.error('site_id is missing: item: %s', item)
            return None
        return item['site_id']

    def collate(self, project_id='', api_key='', token='', context='read'):
        """Check session using token."""
        if context != 'read':
            raise ContextError('invalid context {0:s}'.format(context))

        try:
            ts = self.__class__.generate_timestamp(minutes=60)
            res = self.table.query(
                KeyConditionExpression=(
                    Key('token').eq(token) & Key('initiated_at').gt(ts)),
                FilterExpression=(
                    Attr('project_id').eq(project_id) &
                    Attr('api_key').eq(api_key) &
                    Attr('context').eq(context)
                )
            )
            items = res['Items']
            if len(items) != 1:
                return False

            # set item after view
            self.item = items[0]
            return True
        except Exception as e:  # pylint: disable=broad-except
            logger = logging.getLogger(__name__)
            logger.error('session provisioning error -> %s', e)
            return None
        return token


def session_collator_factory():
    def _session_collator(_, req):
        options = SessionCollator.options(req.settings)
        return SessionCollator(req, **options)

    return _session_collator


def includeme(config):
    config.register_service_factory(
        session_collator_factory(),
        iface=ICollator,
        name='session')
