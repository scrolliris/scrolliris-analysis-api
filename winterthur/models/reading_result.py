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
        # pylint: disable=too-few-public-methods
        db_table = 'reading_results'

    def __repr__(self):
        return '<ReadingResult id:{} element_id:{} code:{} path:{}>'.format(
            self.id, self.element_id, self.code, self.path)

    @classmethod
    def fetch_paragraph_median_by(cls, project_id='', site_id=0):
        """Fetches median values by site."""
        res = cls.select(
            cls.project_id, cls.site_id,
            cls.subject_type, cls.subject_index, cls.median_value
        ).where(
            cls.project_id == project_id,
            cls.site_id == site_id,
            cls.subject_type == 'paragraph',
        ).order_by(
            cls.subject_index.asc()
        )
        data = dict([(str(r.subject_index), r.median_value) for r in res])
        # normalize
        values = data.values()
        min_v = min(values)
        max_v = max(values)
        result = []
        for k in sorted(data.keys()):
            result.append((k, '{0:.2f}'.format(
                (data[k] - min_v) / (max_v - min_v))))

        return [('p', dict(result))]
