from mongoengine import CASCADE, Document, FloatField, ReferenceField, SequenceField

from models.report_indicator import ReportIndicator


class IndicatorValue(Document):
    id = SequenceField(primary_key=True)
    report_indicator = ReferenceField(ReportIndicator, reverse_delete_rule=CASCADE)
    value = FloatField(required=False, default=None)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.report_indicator.name,
            'value': self.value
        }
