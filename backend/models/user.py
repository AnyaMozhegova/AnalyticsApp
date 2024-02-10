from mongoengine import DO_NOTHING, Document, ReferenceField, SequenceField, StringField, BooleanField

from models.role import Role

from errors.not_found import NotFoundError


class User(Document):
    id = SequenceField(primary_key=True)
    name = StringField(required=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    is_active = BooleanField(default=True)
    role = ReferenceField(Role, reverse_delete_rule=DO_NOTHING)

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