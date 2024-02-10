from errors.not_found import NotFoundError
from models.indicator_value import IndicatorValue
from mongoengine import BooleanField, Document, ListField, PULL, ReferenceField, \
    SequenceField, StringField

from custom_types.nullable_floatField import NullableFloatField


class ReportColumn(Document):
    id = SequenceField(primary_key=True)
    name = StringField(unique=True, required=True)
    column_data = ListField(NullableFloatField(), required=True)
    indicator_values = ListField(ReferenceField(IndicatorValue, reverse_delete_rule=PULL))
    is_active = BooleanField(default=True)

    def to_dict(self):
        if self.is_active:
            return {
                'id': self.id,
                'name': self.name,
                'column_data': ['None' if not column_value else column_value for column_value in self.column_data],
                'indicator_values': ['' if not indicator_value else indicator_value.to_dict() for indicator_value in
                                     self.indicator_values],
            }
        else:
            raise NotFoundError(f"Could not convert report column with id = {self.id} to dict. The entity is not found")
