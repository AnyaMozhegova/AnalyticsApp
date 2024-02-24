from models.user import User


class Customer(User):
    def to_dict(self):
        return super(User, self)
