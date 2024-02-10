from models.report_column import ReportColumn
from models.user import User
from mongoengine import BooleanField, CASCADE, DateTimeField, Document, ListField, PULL, ReferenceField, SequenceField, \
    StringField

from errors.not_found import NotFoundError


class Report(Document):
    id = SequenceField(primary_key=True)
    user = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    report_link = StringField(required=True)
    date_uploaded = DateTimeField(required=True)
    columns = ListField(ReferenceField(ReportColumn, reverse_delete_rule=PULL), required=True)
    fits_correlation_analysis = BooleanField(required=True)
    fits_dispersion_analysis = BooleanField(required=True)
    is_active = BooleanField(default=True)

    def to_dict(self):
        if self.is_active:
            return {
                'id': self.id,
                'user': self.user.id,
                'report_link': self.report_link,
                'columns': ['' if not column else column.to_dict() for column in self.columns],
                'date_uploaded': self.date_uploaded.strftime('%Y-%m-%d %H:%M:%S'),
                'fits_correlation_analysis': self.fits_correlation_analysis,
                'fits_dispersion_analysis': self.fits_dispersion_analysis
            }
        else:
            raise NotFoundError(f"Could not convert report with id = {self.id} to dict. The entity is not found")
