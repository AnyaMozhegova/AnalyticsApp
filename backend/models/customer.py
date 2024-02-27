from models.user import User


class Customer(User):
    def to_dict(self):
        return super(Customer, self).to_dict()
