from mongoengine import BooleanField, CASCADE, DateTimeField, Document, ListField, PULL, ReferenceField, SequenceField, \
    StringField

from models.indicator_value import IndicatorValue

from models.user import User


class Report(Document):
    id = SequenceField(primary_key=True)
    user = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    report_link = StringField(required=True)
    date_uploaded = DateTimeField(required=True)
    indicator_values = ListField(ReferenceField(IndicatorValue, reverse_delete_rule=PULL), required=True)
    fits_correlation_analysis = BooleanField(required=True)
    fits_dispersion_analysis = BooleanField(required=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.id,
            'report_link': self.report_link,
            'date_uploaded': self.date_uploaded.strftime('%Y-%m-%d %H:%M:%S'),
            'indicator_values': ['' if not indicator_value else indicator_value.to_dict() for indicator_value in
                                 self.indicator_values],
            'fits_correlation_analysis': self.fits_correlation_analysis,
            'fits_dispersion_analysis': self.fits_dispersion_analysis
        }
