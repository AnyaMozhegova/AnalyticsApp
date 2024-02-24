from errors.not_found import NotFoundError
from models.role import Role
from mongoengine import BooleanField, DO_NOTHING, Document, ReferenceField, SequenceField, StringField


class User(Document):
    id = SequenceField(primary_key=True)
    name = StringField(required=True)
    email = StringField(required=True)
    password = StringField(required=True)
    is_active = BooleanField(default=True)
    role = ReferenceField(Role, reverse_delete_rule=DO_NOTHING)

    meta = {'allow_inheritance': True}

    def to_dict(self):
        if self.is_active:
            return {
                'id': self.id,
                'name': self.name,
                'email': self.email,
                'role': self.role.name
            }
        else:
            raise NotFoundError(f"Could not convert user with id = {self.id} to dict. The entity is not found")
