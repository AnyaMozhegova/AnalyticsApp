from errors.not_found import NotFoundError
from mongoengine import DO_NOTHING, ReferenceField

from models.user import User


class Admin(User):
    parent_admin = ReferenceField(User, reverse_delete_rule=DO_NOTHING)

    def to_dict(self):
        user = super(Admin, self)
        if user.is_active:
            admin_dict = user.to_dict()
            admin_dict['parent_admin'] = self.parent_admin.to_dict()
            return admin_dict
        else:
            raise NotFoundError(f"Could not convert admin with id = {self.id} to dict. The entity is not found")
