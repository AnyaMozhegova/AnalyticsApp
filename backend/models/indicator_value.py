from mongoengine import BooleanField, CASCADE, Document, FloatField, ReferenceField, SequenceField

from models.report_indicator import ReportIndicator

from errors.not_found import NotFoundError


class IndicatorValue(Document):
    id = SequenceField(primary_key=True)
    report_indicator = ReferenceField(ReportIndicator, reverse_delete_rule=CASCADE)
    value = FloatField(required=False, default=None)
    is_active = BooleanField(default=True)

    def to_dict(self):
        if self.is_active:
            return {
                'id': self.id,
                'name': self.report_indicator.name,
                'value': self.value
            }
        else:
            raise NotFoundError(
                f"Could not convert indicator value with id = {self.id} to dict. The entity is not found")
