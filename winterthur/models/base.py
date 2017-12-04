from peewee import Field
from playhouse.signals import Model
from psycopg2.extras import NumericRange

from . import db  # pylint: disable=import-self


# pylint: disable=too-few-public-methods,no-init,old-style-class
class Base(Model):
    class Meta:
        database = db


class NumericRangeField(Field):
    # pylint: disable=no-self-use
    """Range type field definition for numeric value."""

    db_field = 'numrange'

    def get_column_type(self):
        return 'numrange'

    def db_value(self, value):
        if isinstance(value, (list, tuple)) and len(value) == 2:
            return NumericRange(lower=float(value[0]), upper=float(value[1]),
                                bounds='[]', empty=False)
        return value

    def python_value(self, value):
        return value
