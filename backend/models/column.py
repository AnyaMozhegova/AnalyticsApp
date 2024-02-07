from mongoengine import Document, ListField, PULL, ReferenceField, SequenceField, StringField

from models.indicator_value import IndicatorValue


class Column(Document):
    id = SequenceField(primary_key=True)
    name = StringField(unique=True, required=True)
    indicator_values = ListField(ReferenceField(IndicatorValue, reverse_delete_rule=PULL), required=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'indicator_values': ['' if not indicator_value else indicator_value.to_dict() for indicator_value in
                                 self.indicator_values],
        }
