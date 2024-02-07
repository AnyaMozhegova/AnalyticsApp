from mongoengine import BooleanField, CASCADE, DateTimeField, Document, ListField, PULL, ReferenceField, SequenceField, \
    StringField

from models.indicator_value import IndicatorValue

from models.user import User

from models.column import Column


class Report(Document):
    id = SequenceField(primary_key=True)
    user = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    report_link = StringField(required=True)
    date_uploaded = DateTimeField(required=True)
    columns = ListField(ReferenceField(Column, reverse_delete_rule=PULL), required=True)
    fits_correlation_analysis = BooleanField(required=True)
    fits_dispersion_analysis = BooleanField(required=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.id,
            'report_link': self.report_link,
            'columns': ['' if not column else column.to_dict() for column in self.columns],
            'date_uploaded': self.date_uploaded.strftime('%Y-%m-%d %H:%M:%S'),
            'fits_correlation_analysis': self.fits_correlation_analysis,
            'fits_dispersion_analysis': self.fits_dispersion_analysis
        }
