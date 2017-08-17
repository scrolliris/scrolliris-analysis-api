# pylint: disable=inherit-non-class,no-self-argument,no-method-argument
"""Service package.
"""
import base64
from datetime import datetime, timedelta, timezone
import logging
import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key, Attr
from zope.interface import Interface


class ICollator(Interface):
    """Interface as collator service.
    """
    # pylint: disable=missing-docstring

    def collate():
        pass


class ContextError(Exception):
    """Custom error class for session context.
    """
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class BaseDynamoDBServiceObject(object):
    # pylint: disable=too-few-public-methods
    """Service using AWS DynamoDB.
    """
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
    """SessionInitiator Service.
    """
    @classmethod
    def options(cls, settings):
        """Returns options for this collator.
        """
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

    def collate(self, project_id='', api_key='', token='', context='read'):
        """Check session using token.
        """
        if context != 'read':
            raise ContextError('invalid context {0:s}'.format(context))

        try:
            ts = self.__class__.generate_timestamp(minutes=60)
            res = self.table.query(
                KeyConditionExpression=Key('token').eq(token),
                FilterExpression=Attr('initiated_at').gt(ts) &
                Attr('project_id').eq(project_id) &
                Attr('api_key').eq(api_key) &
                Attr('context').eq(context)
            )
            items = res['Items']
            return len(items) == 1
        except Exception as e:  # pylint: disable=broad-except
            logger = logging.getLogger(__name__)
            logger.error('session provisioning error -> %s', e)
            return None
        return token


def session_collator_factory():
    """The session collator service factory.
    """

    def _session_collator(_, req):
        """Actual collator factory method.
        """
        options = SessionCollator.options(req.settings)
        return SessionCollator(req, **options)

    return _session_collator


def includeme(config):
    """Initializes service objects.
    """
    config.register_service_factory(
        session_collator_factory(),
        iface=ICollator,
        name='session')
