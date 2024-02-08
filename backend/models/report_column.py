from typing import Optional

from mongoengine import DecimalField, Document, FloatField, ListField, PULL, ReferenceField, SequenceField, StringField

from models.indicator_value import IndicatorValue

from custom_types.nullable_floatField import NullableFloatField


class ReportColumn(Document):
    id = SequenceField(primary_key=True)
    name = StringField(unique=True, required=True)
    column_data = ListField(NullableFloatField(required=False), required=False)
    indicator_values = ListField(ReferenceField(IndicatorValue, reverse_delete_rule=PULL))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'column_data': ['None' if not column_value else column_value for column_value in self.column_data],
            'indicator_values': ['' if not indicator_value else indicator_value.to_dict() for indicator_value in
                                 self.indicator_values],
        }
