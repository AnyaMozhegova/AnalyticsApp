from mongoengine import Document, SequenceField, StringField


class ReportIndicator(Document):
    id = SequenceField(primary_key=True)
    name = StringField(unique=True, required=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

