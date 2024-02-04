from mongoengine import Document, SequenceField, StringField, signals
from mongoengine.errors import OperationError


class Role(Document):
    id = SequenceField(primary_key=True)
    name = StringField(unique=True, required=True)

    # Use a signal to check before deleting a Role
    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        from models.user import User
        if User.objects(roles=document).count() > 0:
            raise OperationError("Cannot delete a role that is assigned to users.")


signals.pre_delete.connect(Role.pre_delete, sender=Role)
