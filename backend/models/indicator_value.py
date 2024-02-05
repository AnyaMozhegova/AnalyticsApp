from mongoengine import CASCADE, Document, FloatField, ReferenceField, SequenceField

from models.report_indicator import ReportIndicator


class IndicatorValue(Document):
    id = SequenceField(primary_key=True)
    reportIndicator = ReferenceField(ReportIndicator, reverse_delete_rule=CASCADE)
    value = FloatField(required=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.reportIndicator.name,
            'value': self.value
        }
