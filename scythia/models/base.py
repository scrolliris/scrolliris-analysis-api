"""Base model module.
"""
from peewee import Field
from playhouse.signals import Model
from psycopg2.extras import NumericRange

from . import db  # pylint: disable=import-self


class Base(Model):  # pylint: disable=too-few-public-methods
    """Base model class
    """
    class Meta:
        # pylint: disable=too-few-public-methods
        """The meta class
        """
        database = db


class NumericRangeField(Field):
    # pylint: disable=no-self-use
    """Range type field definition for numeric value.
    """
    db_field = 'numrange'

    def get_column_type(self):
        """Returns column type name.
        """
        return 'numrange'

    def db_value(self, value):
        """Returns value for database
        """
        if isinstance(value, (list, tuple)) and len(value) == 2:
            return NumericRange(lower=float(value[0]), upper=float(value[1]),
                                bounds='[]', empty=False)
        return value

    def python_value(self, value):
        """Returns value from database
        """
        return value


