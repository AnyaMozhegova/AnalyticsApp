from mongoengine import DO_NOTHING, Document, ReferenceField, SequenceField, StringField, BooleanField

from models.role import Role


class User(Document):
    id = SequenceField(primary_key=True)
    name = StringField(required=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    is_active = BooleanField(default=True)
    role = ReferenceField(Role, reverse_delete_rule=DO_NOTHING)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'is_active': self.is_active,
            'role': self.role.name
        }
