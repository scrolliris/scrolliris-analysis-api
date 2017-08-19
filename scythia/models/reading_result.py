"""The result model.
"""
from datetime import datetime

from peewee import (
    CharField,
    DateTimeField,
    FloatField,
    IntegerField,
    PrimaryKeyField,
)

from .base import Base, NumericRangeField


class ReadingResult(Base):  # pylint: disable=too-few-public-methods
    """Result model class.
    """
    # pylint: disable=too-many-ancestors
    id = PrimaryKeyField()
    element_id = CharField(max_length=255, unique=True)
    project_id = CharField(max_length=128)
    site_id = IntegerField()
    code = CharField(max_length=128)
    host = CharField(max_length=64)
    path = CharField(max_length=255)
    subject_type = CharField(max_length=16)
    subject_index = IntegerField()
    last_value = FloatField()
    mean_value = FloatField()
    sd_value = FloatField()
    median_value = FloatField()
    variance_value = FloatField()
    total_count = IntegerField()
    trusted_section = NumericRangeField()

    created_at = DateTimeField(null=False, default=datetime.utcnow)
    updated_at = DateTimeField(null=False, default=datetime.utcnow)

    class Meta:
        """The meta class of site.
        """
        # pylint: disable=too-few-public-methods
        db_table = 'reading_results'

    def __repr__(self):
        return '<ReadingResult id:{} element_id:{} code:{} path:{}>'.format(
            self.id, self.element_id, self.code, self.path)
